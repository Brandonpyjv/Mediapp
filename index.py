from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import date_validators as dv
import validators as vd
from functools import wraps
import math

app = Flask(__name__, template_folder="templates")
app.secret_key = "mediapp_secret_key"
app.static_folder = 'templates/static'
# Por defecto Flask ordena alfabéticamente las claves de cualquier jsonify()
# (incluida la respuesta de api/view que arma el modal de detalle), así que
# los campos no aparecían en el orden lógico del formulario sino en A-Z.
# Desactivado para respetar el orden de inserción de cada dict `fields`.
app.json.sort_keys = False

@app.before_request
def ensure_db_connection():
    try:
        db.conexion.ping(reconnect=True, attempts=3, delay=2)
    except Exception as e:
        pass

    # Si al usuario lo desactivaron mientras tenía la sesión abierta,
    # se le cierra la sesión en la siguiente petición (no basta con
    # bloquear el login: una cuenta desactivada no debe seguir operando).
    if request.endpoint != 'static' and 'usuario' in session:
        try:
            cursor = db.conexion.cursor()
            cursor.execute("SELECT estado FROM usuario WHERE id_usuario = %s", (session.get('id_usuario'),))
            row = cursor.fetchone()
            cursor.close()
            if not row or row[0] != 'activo':
                session.clear()
                flash("Su cuenta ha sido desactivada. Por favor, contacte al administrador.", "danger")
        except Exception:
            pass

# T6.10: los listados con datos reales (citas, consultas, historias, exámenes,
# recetas) crecen sin límite con el uso del sistema. Sin paginar, `ciMC` llegó a
# renderizar 1343 filas de una sola vez (2,2 MB de HTML, 1,7 s hasta el DOM
# listo). `FILAS_POR_PAGINA` fija cuántas filas trae cada página.
FILAS_POR_PAGINA = 50

def _paginar(cursor, sql, params=()):
    """Pagina una consulta ya armada con su WHERE de permisos por rol.

    El llamador decide primero **qué** filas puede ver el rol (el patrón de
    3 vías admin/médico/paciente que ya usan estos módulos); esta función
    solo decide **cuántas** de esas filas se muestran a la vez, leyendo la
    página del query param `page` de la URL actual. La paginación se aplica
    siempre después del filtro de permisos, nunca antes — nunca decide ella
    misma qué es visible.

    Ejecuta el conteo total en un cursor aparte (nunca en el del llamador)
    para no interferir con si viene con `dictionary=True` o no: cada módulo
    sigue post-procesando `cursor.fetchall()` exactamente igual que antes.
    Devuelve `(pagina_actual, total_paginas)`."""
    try:
        pagina = max(1, int(request.args.get('page', 1)))
    except (TypeError, ValueError):
        pagina = 1

    conteo_cursor = db.conexion.cursor()
    conteo_cursor.execute(f"SELECT COUNT(*) FROM ({sql}) AS _conteo", params)
    total_filas = conteo_cursor.fetchone()[0]
    conteo_cursor.close()

    total_paginas = max(1, math.ceil(total_filas / FILAS_POR_PAGINA))
    pagina = min(pagina, total_paginas)
    offset = (pagina - 1) * FILAS_POR_PAGINA

    cursor.execute(sql + " LIMIT %s OFFSET %s", tuple(params) + (FILAS_POR_PAGINA, offset))
    return pagina, total_paginas

# Helper: check if id_usuario column exists in paciente table
def _has_user_filter():
    try:
        cursor = db.conexion.cursor()
        cursor.execute("SHOW COLUMNS FROM paciente LIKE 'id_usuario'")
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except:
        return False

def _current_medico_id():
    """Devuelve el id_medico enlazado al usuario en sesión, o None si la
    sesión actual no corresponde a ningún médico (o el vínculo se perdió)."""
    cursor = db.conexion.cursor()
    cursor.execute("SELECT id_medico FROM medico WHERE id_usuario = %s", (session.get('id_usuario'),))
    row = cursor.fetchone()
    cursor.close()
    return row[0] if row else None

# -------------------------
# DECORADORES DE SEGURIDAD
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'admin':
            flash("Acceso restringido solo para administradores.", "danger")
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorated_function

def medico_required(f):
    """Restringe una ruta al rol Médico. Usado para el historial clínico
    (creación, edición y eliminación), permiso exclusivo del médico
    (CLAUDE.md §2 / decisión D1) — el Administrador queda bloqueado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'medico':
            flash("Acceso restringido solo para médicos.", "danger")
            return redirect(url_for('menu'))
        # Una cuenta con rol médico pero sin ficha en `medico` no puede
        # firmar nada: el `id_medico` que se toma de la sesión sería NULL.
        # Existen dos cuentas así (`john.hernandez`, `brandon`), residuo de
        # cuando eliminar un médico lo borraba de verdad — lo que esta misma
        # tarea (D11-a) acaba de impedir para el futuro. Sin este aviso, la
        # pantalla fallaba con un error de base de datos incomprensible.
        if _current_medico_id() is None:
            flash("Su cuenta tiene el rol de médico pero no está vinculada a una ficha "
                  "de médico. Pida al administrador que la vincule antes de continuar.", "danger")
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# LOGIN / LOGOUT
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'usuario' in session:
        return redirect(url_for('menu'))

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        cursor = db.conexion.cursor(dictionary=True)
        # Only search by username to verify hash later
        cursor.execute("""
            SELECT u.*, r.nombre_rol AS rol_nombre
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.username = %s
        """, (username,))
        usuario = cursor.fetchone()
        cursor.close()

        # Verificamos la contraseña SIEMPRE contra el hash (scrypt). No existe
        # fallback en texto plano: toda cuenta debe tener su password hasheado
        # (ver migración de datos en TASKS.md / commit de esta tarea).
        if usuario and check_password_hash(usuario['password'], password):
            if usuario.get('estado') != 'activo':
                return render_template("login.html", error="Esta cuenta ha sido desactivada. Contacte al administrador.")

            session['usuario'] = usuario['username']
            session['rol'] = usuario['rol_nombre']
            session['id_usuario'] = usuario['id_usuario']

            return redirect(url_for('menu'))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'usuario' in session:
        return redirect(url_for('menu'))

    if request.method == "POST":
        # Captura de datos del paciente
        nombre = request.form.get('nombre', '').strip()
        tipo_doc = request.form.get('tipo_documento', '')
        num_doc = request.form.get('numero_documento', '').strip()
        fecha_nac = request.form.get('fecha_nacimiento', '')
        tel = request.form.get('telefono', '').strip()
        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()
        
        # Captura de datos de usuario
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validaciones de que todo sea obligatorio
        if not all([nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, username, password]):
            return render_template("register.html", error="Todos los campos son obligatorios")

        if len(username) < 3 or len(password) < 4:
            return render_template("register.html", error="Usuario (mín. 3) o contraseña (mín. 4) demasiado cortos",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

        # Validación de formato de correo electrónico (T5.8)
        email_valido, email_error = vd.validate_email(email)
        if not email_valido:
            return render_template("register.html", error=email_error,
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

        # Validación de fecha de nacimiento (no puede ser una fecha futura)
        fecha_valida, fecha_error = dv.validate_birthdate(fecha_nac)
        if not fecha_valida:
            return render_template("register.html", error=fecha_error,
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

        cursor = db.conexion.cursor()
        try:
            # 1. Validar si usuario ya existe
            cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone():
                return render_template("register.html", error="El usuario ya está en uso",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

            # 2. Validar si el paciente ya existe (por numero_documento)
            cursor.execute("SELECT id_paciente FROM paciente WHERE numero_documento = %s", (num_doc,))
            if cursor.fetchone():
                return render_template("register.html", error="El número de documento ya está registrado",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

            # 3. Crear usuario (rol 2 por defecto = user)
            hashed_pw = generate_password_hash(password)
            cursor.execute("INSERT INTO usuario (username, password, id_rol) VALUES (%s, %s, %s)", (username, hashed_pw, 2))
            id_usuario = cursor.lastrowid

            # 4. Crear paciente entrelazado con el usuario
            sql_paciente = """
                INSERT INTO paciente 
                (nombre, tipo_documento, numero_documento, fecha_nacimiento, telefono, direccion, email, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_paciente, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario))

            db.conexion.commit()
            flash("Registro exitoso. Ya puede iniciar sesión.", "success")
            return redirect(url_for('login'))
            
        except IntegrityError as e:
            db.conexion.rollback()
            return render_template("register.html", error="Ocurrió un error de base de datos. Verifique que sus datos sean correctos.",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)
        except Exception as e:
            db.conexion.rollback()
            return render_template("register.html", error=f"Error inesperado: {e}",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)
        finally:
            cursor.close()

    return render_template("register.html")

# -------------------------
# PANELES PRINCIPALES
# -------------------------

@app.route("/")
@login_required
def menu():
    return render_template("menu.html", rol=session['rol'])

# -------------------------
# MÓDULO: USUARIOS
# -------------------------
@app.route("/usMC")
@admin_required
def usMC():
    data = []
    if db.conexion.is_connected():
        cursor = db.conexion.cursor(dictionary=True)
        # La identificación no vive en `usuario`: está en la ficha de paciente o
        # de médico que apunta a esa cuenta. Se resuelve con subconsultas y no
        # con LEFT JOIN porque `paciente.id_usuario` y `medico.id_usuario` solo
        # tienen índice, no UNIQUE: un JOIN duplicaría la fila del usuario si
        # alguna vez quedaran dos fichas apuntando a la misma cuenta.
        # El administrador no tiene ficha, así que queda en NULL (D13: se
        # muestra un guion).
        cursor.execute("""
            SELECT u.id_usuario, u.username, u.estado, r.nombre_rol,
                   COALESCE(
                       (SELECT p.numero_documento FROM paciente p
                         WHERE p.id_usuario = u.id_usuario LIMIT 1),
                       (SELECT m.numero_identidad FROM medico m
                         WHERE m.id_usuario = u.id_usuario LIMIT 1)
                   ) AS identificacion
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
        """)
        data = cursor.fetchall()
        cursor.close()
    return render_template("usuarios/usMC.html", data=data, rol=session['rol'])

@app.route("/addUS", methods=["GET", "POST"])
@admin_required
def addUS():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if len(username) < 3 or len(password) < 4:
            return render_template("usuarios/addUS.html", error="Los datos son demasiado cortos")

        hashed_pw = generate_password_hash(password)

        try:
            cursor = db.conexion.cursor()
            # Esta pantalla crea administradores y solo administradores. Antes
            # tomaba el rol de un campo `id_rol` del formulario que nunca existió,
            # así que caía siempre en el 2 (paciente) y creaba cuentas de paciente
            # huérfanas: sin ficha en `paciente`, el usuario entraba al sistema
            # pero no tenía citas, recetas ni historia que consultar.
            # Las cuentas de paciente se crean desde `addPA` y las de médico desde
            # `addMED`, que sí crean la ficha correspondiente.
            cursor.execute("SELECT id_rol FROM rol WHERE nombre_rol = 'admin'")
            fila_rol = cursor.fetchone()
            if not fila_rol:
                cursor.close()
                return render_template("usuarios/addUS.html",
                                       error="No existe el rol 'admin' en la base de datos.")
            id_rol = fila_rol[0]

            cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                return render_template("usuarios/addUS.html", error=f"El usuario '{username}' ya existe.")
            cursor.execute(
                "INSERT INTO usuario (username, password, id_rol) VALUES (%s, %s, %s)",
                (username, hashed_pw, id_rol)
            )
            db.conexion.commit()
            cursor.close()
            flash("Administrador creado exitosamente", "success")
            return redirect(url_for('usMC'))
        except Exception as e:
            return render_template("usuarios/addUS.html", error=f"Error: {e}")

    return render_template("usuarios/addUS.html")

def _usuario_para_formulario(cursor, id_usuario):
    """Trae el usuario con su rol y su identificación, tal como los muestra
    `editUS.html`. La identificación vive en la ficha de paciente o de médico
    (ver la nota en `usMC` sobre por qué son subconsultas y no JOINs).
    Se listan las columnas una por una a propósito: con `u.*` el hash de la
    contraseña llegaba hasta la plantilla, que es justo lo que se está quitando."""
    cursor.execute("""
        SELECT u.id_usuario, u.username, u.estado, u.id_rol, r.nombre_rol,
               COALESCE(
                   (SELECT p.numero_documento FROM paciente p
                     WHERE p.id_usuario = u.id_usuario LIMIT 1),
                   (SELECT m.numero_identidad FROM medico m
                     WHERE m.id_usuario = u.id_usuario LIMIT 1)
               ) AS identificacion
        FROM usuario u
        INNER JOIN rol r ON u.id_rol = r.id_rol
        WHERE u.id_usuario = %s
    """, (id_usuario,))
    return cursor.fetchone()


@app.route("/editUS/<string:id>", methods=["GET", "POST"])
@admin_required
def editUS(id):
    cursor = db.conexion.cursor(dictionary=True)

    def _volver_con_error(mensaje):
        """Repinta el formulario con el error, sin perder los datos mostrados."""
        user = _usuario_para_formulario(cursor, id)
        cursor.close()
        return render_template("usuarios/editUS.html", error=mensaje, user=user,
                               identificacion=user.get('identificacion') if user else None)

    if request.method == "POST":
        username = request.form['username']
        # Vacío = conservar la contraseña actual. El formulario ya no precarga
        # nada en este campo (antes traía el hash y era obligatorio, así que
        # guardar sin tocarlo volvía a hashear el hash y dejaba al usuario sin
        # poder entrar con su contraseña real).
        new_password = request.form.get('password', '').strip()

        cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s AND id_usuario != %s", (username, id))
        if cursor.fetchone():
            return _volver_con_error(f"El usuario '{username}' ya existe.")

        if len(username) < 3:
            return _volver_con_error("El usuario debe tener al menos 3 caracteres.")

        # Mismo mínimo que al crear (`addUS`), que aquí no se validaba.
        if new_password and len(new_password) < 4:
            return _volver_con_error("La contraseña debe tener al menos 4 caracteres.")

        if new_password:
            hashed_pw = generate_password_hash(new_password)
            sql = "UPDATE usuario SET username=%s, password=%s WHERE id_usuario=%s"
            data = (username, hashed_pw, id)
        else:
            sql = "UPDATE usuario SET username=%s WHERE id_usuario=%s"
            data = (username, id)

        try:
            cursor.execute(sql, data)
            db.conexion.commit()
            cursor.close()
            flash("Usuario actualizado exitosamente", "success")
            return redirect(url_for('usMC'))
        except Exception as e:
            db.conexion.rollback()
            return _volver_con_error(f"Error al actualizar: {e}")

    user = _usuario_para_formulario(cursor, id)
    cursor.close()

    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('usMC'))

    return render_template("usuarios/editUS.html", user=user,
                           identificacion=user.get('identificacion'))

@app.route("/deleteUS/<string:id>", methods=["POST"])
@admin_required
def deleteUS(id):
    """Deactivates a user account. A 'usuario' row is never hard-deleted:
    it's set to 'inactivo' so the record and its history are preserved
    and the account can be reactivated later if needed."""
    cursor = db.conexion.cursor()
    try:
        cursor.execute("UPDATE usuario SET estado='inactivo' WHERE id_usuario = %s", (id,))
        db.conexion.commit()
        flash("Usuario desactivado.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('usMC'))

@app.route("/reactivateUS/<string:id>", methods=["POST"])
@admin_required
def reactivateUS(id):
    """Reactivates a previously deactivated user account."""
    cursor = db.conexion.cursor()
    try:
        cursor.execute("UPDATE usuario SET estado='activo' WHERE id_usuario = %s", (id,))
        db.conexion.commit()
        flash("Usuario reactivado.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('usMC'))

# ===========================================================================
# MÓDULO: MÉDICOS (CRUD COMPLETO)
# ===========================================================================

@app.route("/medMC")
@admin_required
def medMC():
    """Lista todos los médicos con el nombre de su especialidad y el
    estado de su cuenta de acceso (puede tener id_usuario asignado pero
    haber sido desactivada desde el módulo de Usuarios)."""
    cursor = db.conexion.cursor(dictionary=True)
    sql = """
        SELECT medico.*, especialidad.nombre AS nombre_es, usuario.estado AS estado_cuenta
        FROM medico
        INNER JOIN especialidad ON medico.id_especialidad = especialidad.id_especialidad
        LEFT JOIN usuario ON medico.id_usuario = usuario.id_usuario
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template("medicos/medMC.html", data=data)


@app.route("/addMED", methods=["GET", "POST"])
@admin_required
def addMED():
    """Adds a new doctor to the system, together with the login account
    that lets them sign in with the Doctor role. Only the Administrator
    can create or modify doctors (CLAUDE.md §2 / decision D1)."""
    cursor = db.conexion.cursor(dictionary=True)

    # Siempre cargamos especialidades para el dropdown del formulario
    cursor.execute("SELECT * FROM especialidad")
    especialidades = cursor.fetchall()

    if request.method == "POST":
        # Captura de datos del médico
        nombre = request.form.get('nombre', '')
        num_id = request.form.get('numero_identidad', '')
        tel = request.form.get('telefono', '')
        email = request.form.get('email', '')
        id_esp = request.form.get('id_especialidad', '')

        # Captura de datos de la cuenta de acceso (rol Médico, id_rol=3)
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # --- VALIDATIONS ---
        email_valido, email_mensaje = vd.validate_email(email)
        error = None
        if any(char.isdigit() for char in nombre):
            error = "El nombre no puede contener números."
        elif not num_id.isdigit() or len(num_id) < 5:
            error = "Documento no válido (solo números, mínimo 5 dígitos)."
        elif not email_valido:
            error = email_mensaje
        elif not id_esp:
            error = "Debe seleccionar una especialidad."
        elif len(tel) != 10 or not tel.isdigit():
            error = "El número de teléfono debe tener exactamente 10 dígitos."
        elif len(username) < 3:
            error = "El usuario debe tener al menos 3 caracteres."
        elif len(password) < 4:
            error = "La contraseña debe tener al menos 4 caracteres."

        if error:
            return render_template("medicos/addMED.html",
                                especialidades=especialidades,
                                error=error,
                                v_nombre=nombre, v_num_id=num_id,
                                v_tel=tel, v_email=email, v_id_esp=id_esp,
                                v_username=username)

        # --- INSERCIÓN (cuenta de usuario + médico, en una sola transacción) ---
        try:
            cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone():
                return render_template("medicos/addMED.html", especialidades=especialidades,
                                    error="El usuario ya está en uso.",
                                    v_nombre=nombre, v_num_id=num_id, v_tel=tel,
                                    v_email=email, v_id_esp=id_esp, v_username=username)

            cursor.execute("SELECT id_medico FROM medico WHERE numero_identidad = %s", (num_id,))
            if cursor.fetchone():
                return render_template("medicos/addMED.html", especialidades=especialidades,
                                    error=f"Ya existe un médico con el documento '{num_id}'.",
                                    v_nombre=nombre, v_num_id=num_id, v_tel=tel,
                                    v_email=email, v_id_esp=id_esp, v_username=username)

            # 1. Crear la cuenta de acceso con rol Médico (id_rol=3)
            hashed_pw = generate_password_hash(password)
            cursor.execute("INSERT INTO usuario (username, password, id_rol) VALUES (%s, %s, %s)",
                        (username, hashed_pw, 3))
            id_usuario = cursor.lastrowid

            # 2. Crear el médico enlazado a esa cuenta
            sql = """INSERT INTO medico (nombre, numero_identidad, telefono, email, id_especialidad, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, num_id, tel, email, id_esp, id_usuario))
            db.conexion.commit()
            flash("Médico agregado exitosamente.", "success")
            return redirect(url_for('medMC'))
        except Exception as e:
            db.conexion.rollback()
            error = f"Error de base de datos: {e}"
            return render_template("medicos/addMED.html", especialidades=especialidades, error=error,
                                v_nombre=nombre, v_num_id=num_id, v_tel=tel,
                                v_email=email, v_id_esp=id_esp, v_username=username)
        finally:
            cursor.close()

    return render_template("medicos/addMED.html", especialidades=especialidades)


@app.route("/editMED/<string:id>", methods=["GET", "POST"])
@admin_required
def editMED(id):
    """Edita los datos de un médico existente y, opcionalmente, crea o
    actualiza su cuenta de acceso. Solo el Administrador puede hacerlo."""
    cursor = db.conexion.cursor(dictionary=True)

    # Cargamos especialidades para el select
    cursor.execute("SELECT * FROM especialidad")
    especialidades = cursor.fetchall()

    if request.method == "POST":
        nombre = request.form.get('nombre', '')
        num_id = request.form.get('numero_identidad', '')
        tel = request.form.get('telefono', '')
        email = request.form.get('email', '')
        id_esp = request.form.get('id_especialidad', '')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Averiguamos si este médico ya tiene cuenta de acceso. El estado se
        # trae solo para poder mostrarlo si hay que re-renderizar por un
        # error: no se edita en este formulario (D11-a).
        cursor.execute("SELECT id_usuario, estado FROM medico WHERE id_medico = %s", (id,))
        current = cursor.fetchone()
        current_id_usuario = current['id_usuario'] if current else None
        estado_actual = current['estado'] if current else 'activo'

        # Validations
        email_valido, email_mensaje = vd.validate_email(email)
        error = None
        if any(char.isdigit() for char in nombre):
            error = "El nombre no puede contener números."
        elif len(tel) != 10:
            error = "Número de teléfono no válido."
        elif not email_valido:
            error = email_mensaje
        elif current_id_usuario is None and not username:
            error = "Este médico todavía no tiene cuenta de acceso. Ingrese un usuario y contraseña para crear una."
        elif current_id_usuario is None and len(password) < 4:
            error = "La contraseña debe tener al menos 4 caracteres."
        elif username and len(username) < 3:
            error = "El usuario debe tener al menos 3 caracteres."
        elif password and len(password) < 4:
            error = "La contraseña debe tener al menos 4 caracteres."

        user_ctx = {"id_medico": id, "nombre": nombre, "numero_identidad": num_id,
                    "telefono": tel, "email": email, "id_especialidad": id_esp,
                    "id_usuario": current_id_usuario, "username": username,
                    "estado": estado_actual}

        if error:
            return render_template("medicos/editMED.html",
                                especialidades=especialidades, error=error, user=user_ctx)

        try:
            id_usuario_final = current_id_usuario

            if current_id_usuario is None:
                # El médico no tenía cuenta de acceso: la creamos ahora.
                cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s", (username,))
                if cursor.fetchone():
                    return render_template("medicos/editMED.html", especialidades=especialidades,
                                        error="El usuario ya está en uso.", user=user_ctx)
                hashed_pw = generate_password_hash(password)
                cursor.execute("INSERT INTO usuario (username, password, id_rol) VALUES (%s, %s, %s)",
                            (username, hashed_pw, 3))
                id_usuario_final = cursor.lastrowid
            else:
                # Ya tenía cuenta: solo se actualiza lo que se haya enviado.
                if username:
                    cursor.execute(
                        "SELECT id_usuario FROM usuario WHERE username = %s AND id_usuario != %s",
                        (username, current_id_usuario))
                    if cursor.fetchone():
                        return render_template("medicos/editMED.html", especialidades=especialidades,
                                            error="El usuario ya está en uso.", user=user_ctx)
                    cursor.execute("UPDATE usuario SET username=%s WHERE id_usuario=%s",
                                (username, current_id_usuario))
                if password:
                    hashed_pw = generate_password_hash(password)
                    cursor.execute("UPDATE usuario SET password=%s WHERE id_usuario=%s",
                                (hashed_pw, current_id_usuario))

            cursor.execute("SELECT id_medico FROM medico WHERE numero_identidad = %s AND id_medico != %s", (num_id, id))
            if cursor.fetchone():
                return render_template("medicos/editMED.html", especialidades=especialidades,
                                    error=f"Ya existe un médico con el documento '{num_id}'.", user=user_ctx)

            sql = """UPDATE medico
                    SET nombre=%s, numero_identidad=%s, telefono=%s, email=%s, id_especialidad=%s, id_usuario=%s
                    WHERE id_medico=%s"""
            cursor.execute(sql, (nombre, num_id, tel, email, id_esp, id_usuario_final, id))
            db.conexion.commit()
            flash("Médico actualizado exitosamente.", "success")
            return redirect(url_for('medMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al actualizar: {e}", "danger")
            return redirect(url_for('medMC'))
        finally:
            cursor.close()

    # GET: Cargar datos actuales del médico junto con su username (si tiene cuenta)
    cursor.execute("""
        SELECT medico.*, usuario.username AS username
        FROM medico
        LEFT JOIN usuario ON medico.id_usuario = usuario.id_usuario
        WHERE medico.id_medico = %s
    """, (id,))
    medico = cursor.fetchone()
    cursor.close()

    if not medico:
        flash("Médico no encontrado.", "warning")
        return redirect(url_for('medMC'))

    return render_template("medicos/editMED.html", user=medico, especialidades=especialidades)


@app.route("/deleteMED/<string:id>", methods=["POST"])
@admin_required
def deleteMED(id):
    """Da de baja a un médico (decisión D11-a): **nunca lo borra**.

    Antes esta ruta hacía `DELETE FROM medico` de verdad, y con ello se
    perdía la ficha de quien firmó historias clínicas, consultas y
    recetas — además de dejar su cuenta huérfana (rol médico sin ficha).
    Ahora solo cambia el estado: el médico deja de aparecer para agendar
    citas nuevas, pero conserva todo lo que ya firmó.

    El nombre de la ruta se mantiene por coherencia con `deleteUS`, que
    hace exactamente lo mismo con las cuentas desde la migración 002.

    La cuenta de acceso **no se toca aquí**: son dos cosas distintas y
    tienen su propia acción (`toggleAccesoMED`). Un médico de licencia
    puede seguir activo en el sistema sin poder entrar, y uno dado de
    baja puede conservar el acceso para consultar lo suyo."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM medico WHERE id_medico = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El médico no existe.", "warning")
            return redirect(url_for('medMC'))

        cursor.execute("UPDATE medico SET estado='inactivo' WHERE id_medico = %s", (id,))
        db.conexion.commit()
        flash(f"Dr. {row['nombre']} fue desactivado. Ya no aparecerá al agendar citas nuevas, "
              f"pero conserva sus registros clínicos.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al desactivar el médico: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('medMC'))


@app.route("/reactivateMED/<string:id>", methods=["POST"])
@admin_required
def reactivateMED(id):
    """Revierte la baja lógica de un médico (D11-a). Vuelve a estar
    disponible para agendarle citas nuevas."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM medico WHERE id_medico = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El médico no existe.", "warning")
            return redirect(url_for('medMC'))

        cursor.execute("UPDATE medico SET estado='activo' WHERE id_medico = %s", (id,))
        db.conexion.commit()
        flash(f"Dr. {row['nombre']} fue reactivado y vuelve a estar disponible para agendar.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al reactivar el médico: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('medMC'))


@app.route("/toggleAccesoMED/<string:id>", methods=["POST"])
@admin_required
def toggleAccesoMED(id):
    """Da o quita el acceso al sistema de un médico (D11-a).

    Actúa **solo sobre la cuenta** (`usuario.estado`), no sobre la ficha
    del médico: son los dos conceptos que antes se confundían en la
    columna "Acceso", que informaba pero no se podía cambiar desde aquí.
    Sirve, por ejemplo, para una licencia temporal sin dar de baja al
    profesional."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.nombre, m.id_usuario, u.estado AS estado_cuenta
            FROM medico m LEFT JOIN usuario u ON m.id_usuario = u.id_usuario
            WHERE m.id_medico = %s
        """, (id,))
        row = cursor.fetchone()
        if not row:
            flash("El médico no existe.", "warning")
            return redirect(url_for('medMC'))
        if not row['id_usuario']:
            flash(f"Dr. {row['nombre']} todavía no tiene cuenta de acceso. "
                  f"Créele una desde el botón de editar.", "warning")
            return redirect(url_for('medMC'))

        nuevo = 'inactivo' if row['estado_cuenta'] == 'activo' else 'activo'
        cursor.execute("UPDATE usuario SET estado=%s WHERE id_usuario = %s", (nuevo, row['id_usuario']))
        db.conexion.commit()
        if nuevo == 'inactivo':
            flash(f"Se le quitó el acceso al sistema a Dr. {row['nombre']}. Sigue siendo médico "
                  f"del sistema, pero no podrá iniciar sesión.", "success")
        else:
            flash(f"Dr. {row['nombre']} vuelve a tener acceso al sistema.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al cambiar el acceso: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('medMC'))

# ===========================================================================
# MÓDULO: PACIENTES (CRUD COMPLETO)
# ===========================================================================

@app.route("/paMC")
@login_required
def paMC():
    """Lista todos los pacientes (admin y médico) o el paciente del usuario actual."""
    cursor = db.conexion.cursor(dictionary=True)
    if session.get('rol') in ('admin', 'medico') or not _has_user_filter():
        cursor.execute("SELECT * FROM paciente")
    else:
        cursor.execute("SELECT * FROM paciente WHERE id_usuario = %s", (session.get('id_usuario'),))
    data = cursor.fetchall()
    cursor.close()
    return render_template("pacientes/paMC.html", data=data)


@app.route("/addPA", methods=["GET", "POST"])
@admin_required
def addPA():
    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, username FROM usuario")
    usuarios = cursor.fetchall()

    if request.method == "POST":
        # Captura de datos desde el formulario
        nombre = request.form.get('nombre', '').strip()
        tipo_doc = request.form.get('tipo_documento', '')
        num_doc = request.form.get('numero_documento', '').strip()
        fecha_nac = request.form.get('fecha_nacimiento', '')
        tel = request.form.get('telefono', '').strip()
        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()
        id_usuario = request.form.get('id_usuario', '')
        if not id_usuario: id_usuario = None

        # --- VALIDACIONES ---
        email_valido, email_mensaje = vd.validate_email(email)
        error = None
        if len(nombre) < 3:
            error = "El nombre es demasiado corto."
        elif any(char.isdigit() for char in nombre):
            error = "El nombre no puede contener números."
        elif not tipo_doc:
            error = "Debe seleccionar un tipo de documento."
        elif len(num_doc) < 5 or not num_doc.isdigit():
            error = "Número de documento no válido (mínimo 5 dígitos)."
        elif len(tel) != 10 or not tel.isdigit():
            error = "El número de teléfono debe tener exactamente 10 dígitos."
        elif not email_valido:
            error = email_mensaje
        else:
            fecha_valida, fecha_error = dv.validate_birthdate(fecha_nac)
            if not fecha_valida:
                error = fecha_error

        if error:
            return render_template("pacientes/addPA.html", 
                                error=error, usuarios=usuarios,
                                v_nombre=nombre, v_tipo_doc=tipo_doc,
                                v_num_doc=num_doc, v_fecha_nac=fecha_nac,
                                v_tel=tel, v_dir=dir, v_email=email, v_id_usuario=id_usuario)

        # --- INSERCIÓN EN BD ---
        try:
            cursor = db.conexion.cursor()
            cursor.execute("SELECT id_paciente FROM paciente WHERE numero_documento = %s", (num_doc,))
            if cursor.fetchone():
                cursor.close()
                return render_template("pacientes/addPA.html",
                                    error=f"Ya existe un paciente con el documento '{num_doc}'.", usuarios=usuarios,
                                    v_nombre=nombre, v_tipo_doc=tipo_doc,
                                    v_num_doc=num_doc, v_fecha_nac=fecha_nac,
                                    v_tel=tel, v_dir=dir, v_email=email, v_id_usuario=id_usuario)
            sql = """
                INSERT INTO paciente
                (nombre, tipo_documento, numero_documento, fecha_nacimiento, telefono, direccion, email, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario))
            db.conexion.commit()
            cursor.close()
            flash("Paciente registrado exitosamente.", "success")
            return redirect(url_for('paMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("pacientes/addPA.html", error=f"Error de base de datos: {e}")

    return render_template("pacientes/addPA.html", usuarios=usuarios)


@app.route("/editPA/<string:id>", methods=["GET", "POST"])
@admin_required
def editPA(id):
    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, username FROM usuario")
    usuarios = cursor.fetchall()

    if request.method == "POST":
        nombre = request.form.get('nombre', '').strip()
        tipo_doc = request.form.get('tipo_documento', '')
        num_doc = request.form.get('numero_documento', '').strip()
        fecha_nac = request.form.get('fecha_nacimiento', '')
        tel = request.form.get('telefono', '').strip()
        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()
        id_usuario = request.form.get('id_usuario', '')
        if not id_usuario: id_usuario = None

        # Validations
        email_valido, email_mensaje = vd.validate_email(email)
        error = None
        if len(nombre) < 3: error = "El nombre es demasiado corto."
        elif len(tel) != 10: error = "El teléfono debe tener 10 dígitos."
        elif not email_valido: error = email_mensaje
        elif fecha_nac:
            # Solo se valida si se envió una fecha (el campo no es obligatorio aquí)
            fecha_valida, fecha_error = dv.validate_birthdate(fecha_nac)
            if not fecha_valida:
                error = fecha_error

        if error:
            return render_template("pacientes/editPA.html",
                                error=error, usuarios=usuarios,
                                user={
                                    "id_paciente": id, "nombre": nombre,
                                    "tipo_documento": tipo_doc, "numero_documento": num_doc,
                                    "fecha_nacimiento": fecha_nac, "telefono": tel,
                                    "direccion": dir, "email": email, "id_usuario": id_usuario
                                })

        cursor.execute("SELECT id_paciente FROM paciente WHERE numero_documento = %s AND id_paciente != %s", (num_doc, id))
        if cursor.fetchone():
            return render_template("pacientes/editPA.html",
                                error=f"Ya existe un paciente con el documento '{num_doc}'.", usuarios=usuarios,
                                user={
                                    "id_paciente": id, "nombre": nombre,
                                    "tipo_documento": tipo_doc, "numero_documento": num_doc,
                                    "fecha_nacimiento": fecha_nac, "telefono": tel,
                                    "direccion": dir, "email": email, "id_usuario": id_usuario
                                })

        try:
            sql = """
                UPDATE paciente
                SET nombre=%s, tipo_documento=%s, numero_documento=%s,
                    fecha_nacimiento=%s, telefono=%s, direccion=%s, email=%s, id_usuario=%s
                WHERE id_paciente=%s
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario, id))
            db.conexion.commit()
            cursor.close()
            flash("Datos del paciente actualizados.", "success")
            return redirect(url_for('paMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al actualizar: {e}", "danger")
            return redirect(url_for('paMC'))

    # GET: Obtener datos actuales del paciente
    cursor.execute("SELECT * FROM paciente WHERE id_paciente = %s", (id,))
    paciente = cursor.fetchone()
    cursor.close()

    if not paciente:
        flash("Paciente no encontrado.", "warning")
        return redirect(url_for('paMC'))

    return render_template("pacientes/editPA.html", user=paciente, usuarios=usuarios)


@app.route("/deletePA/<string:id>", methods=["POST"])
@admin_required
def deletePA(id):
    """Da de baja a un paciente (decisión D11-a): **nunca lo borra**.

    Antes esta ruta hacía `DELETE FROM paciente` de verdad, y en la
    práctica solo servía si el paciente no tenía ningún registro
    asociado (la FK rechazaba el borrado en cualquier otro caso, sin
    que eso fuera una protección real). Ahora solo cambia el estado: el
    paciente deja de ofrecerse al agendar citas nuevas o registrar
    historias/consultas/exámenes, pero conserva todo su historial.

    El nombre de la ruta se mantiene por coherencia con `deleteMED` y
    `deleteUS`, que hacen exactamente lo mismo."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM paciente WHERE id_paciente = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El paciente no existe.", "warning")
            return redirect(url_for('paMC'))

        cursor.execute("UPDATE paciente SET estado='inactivo' WHERE id_paciente = %s", (id,))
        db.conexion.commit()
        flash(f"{row['nombre']} fue dado de baja. Ya no se ofrecerá al agendar citas nuevas "
              f"ni registrar historias, consultas o exámenes, pero conserva su historial.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al dar de baja al paciente: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('paMC'))


@app.route("/reactivatePA/<string:id>", methods=["POST"])
@admin_required
def reactivatePA(id):
    """Revierte la baja lógica de un paciente (D11-a). Vuelve a estar
    disponible para agendarle citas y registrarle historias, consultas
    o exámenes nuevos."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM paciente WHERE id_paciente = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El paciente no existe.", "warning")
            return redirect(url_for('paMC'))

        cursor.execute("UPDATE paciente SET estado='activo' WHERE id_paciente = %s", (id,))
        db.conexion.commit()
        flash(f"{row['nombre']} fue reactivado y vuelve a estar disponible.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al reactivar al paciente: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('paMC'))

# ===========================================================================
# MÓDULO: ESPECIALIDADES (CRUD COMPLETO)
# ===========================================================================

@app.route("/esMC")
@admin_required
def esMC():
    """Lista todas las especialidades médicas registradas."""
    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM especialidad")
    data = cursor.fetchall()
    cursor.close()
    return render_template("especialidad/esMC.html", data=data)


@app.route("/addES", methods=["GET", "POST"])
@admin_required
def addES():
    """Registra una nueva especialidad médica."""
    if request.method == "POST":
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        # --- VALIDACIONES ---
        error = None
        if len(nombre) < 4:
            error = "El nombre de la especialidad debe tener al menos 4 caracteres."
        elif any(char.isdigit() for char in nombre):
            error = "El nombre de la especialidad no puede contener números."
        
        if error:
            return render_template("especialidad/addES.html", 
                                error=error, 
                                v_nombre=nombre, 
                                v_descripcion=descripcion)

        # --- INSERCIÓN EN BD ---
        try:
            cursor = db.conexion.cursor()
            cursor.execute("SELECT id_especialidad FROM especialidad WHERE nombre = %s", (nombre,))
            if cursor.fetchone():
                cursor.close()
                return render_template("especialidad/addES.html",
                                    error=f"La especialidad '{nombre}' ya existe.",
                                    v_nombre=nombre, v_descripcion=descripcion)
            sql = "INSERT INTO especialidad (nombre, descripcion) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, descripcion))
            db.conexion.commit()
            cursor.close()
            flash("Especialidad creada exitosamente.", "success")
            return redirect(url_for('esMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("especialidad/addES.html", error=f"Error de base de datos: {e}")

    return render_template("especialidad/addES.html")


@app.route("/editES/<string:id>", methods=["GET", "POST"])
@admin_required
def editES(id):
    """Actualiza una especialidad existente."""
    cursor = db.conexion.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        # Validations
        error = None
        if len(nombre) < 4:
            error = "El nombre es demasiado corto."
        elif any(char.isdigit() for char in nombre):
            error = "El nombre no puede contener números."

        if error:
            return render_template("especialidad/editES.html",
                                error=error,
                                item={"id_especialidad": id, "nombre": nombre, "descripcion": descripcion})

        cursor.execute("SELECT id_especialidad FROM especialidad WHERE nombre = %s AND id_especialidad != %s", (nombre, id))
        if cursor.fetchone():
            return render_template("especialidad/editES.html",
                                error=f"La especialidad '{nombre}' ya existe.",
                                item={"id_especialidad": id, "nombre": nombre, "descripcion": descripcion})

        try:
            sql = "UPDATE especialidad SET nombre=%s, descripcion=%s WHERE id_especialidad=%s"
            cursor.execute(sql, (nombre, descripcion, id))
            db.conexion.commit()
            cursor.close()
            flash("Especialidad actualizada exitosamente.", "success")
            return redirect(url_for('esMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al actualizar: {e}", "danger")
            return redirect(url_for('esMC'))

    # GET: Cargar datos de la especialidad
    cursor.execute("SELECT * FROM especialidad WHERE id_especialidad = %s", (id,))
    especialidad = cursor.fetchone()
    cursor.close()

    if not especialidad:
        flash("Especialidad no encontrada.", "warning")
        return redirect(url_for('esMC'))

    return render_template("especialidad/editES.html", item=especialidad)


@app.route("/deleteES/<string:id>", methods=["POST"])
@admin_required
def deleteES(id):
    """Elimina una especialidad, verificando que no tenga médicos asociados."""
    cursor = db.conexion.cursor()
    try:
        cursor.execute("DELETE FROM especialidad WHERE id_especialidad = %s", (id,))
        db.conexion.commit()
        flash("Especialidad eliminada.", "success")
    except IntegrityError:
        # Occurs if doctors are linked to this specialty
        flash("No se puede eliminar: hay médicos registrados bajo esta especialidad.", "danger")
    finally:
        cursor.close()
    return redirect(url_for('esMC'))

# ===========================================================================
# MÓDULO: RECETAS MÉDICAS (CRUD COMPLETO)
# ===========================================================================

# Permisos (D6): la receta no tiene id_medico propio — su dueño es el
# médico de la consulta a la que pertenece. Mismo criterio que consulta:
# el Médico crea/edita/borra solo sus propias recetas; Admin y Médico
# ven todas para lectura; Paciente ve las suyas.
@app.route("/reMC")
@login_required
def reMC():
    """Lista todas las recetas con información de pacientes y médicos."""
    cursor = db.conexion.cursor(dictionary=True)
    current_medico_id = _current_medico_id() if session.get('rol') == 'medico' else None
    if session.get('rol') in ('admin', 'medico') or not _has_user_filter():
        # Se traen paciente y fecha de la consulta porque la tabla ya no muestra
        # el id_consulta crudo, sino a qué consulta pertenece la receta en texto.
        sql = """
            SELECT r.*, co.id_medico AS id_medico_consulta, co.fecha AS fecha_consulta,
                   p.nombre AS nombre_paciente, m.nombre AS nombre_medicamento
            FROM receta r
            INNER JOIN medicamento m ON r.id_medicamento = m.id_medicamento
            INNER JOIN consulta co ON r.id_consulta = co.id_consulta
            INNER JOIN paciente p ON co.id_paciente = p.id_paciente
            ORDER BY r.id_receta DESC
        """
        params = ()
    else:
        sql = """
            SELECT r.*, co.id_medico AS id_medico_consulta, co.fecha AS fecha_consulta,
                   p.nombre AS nombre_paciente, m.nombre AS nombre_medicamento
            FROM receta r
            INNER JOIN medicamento m ON r.id_medicamento = m.id_medicamento
            INNER JOIN consulta co ON r.id_consulta = co.id_consulta
            INNER JOIN paciente p ON co.id_paciente = p.id_paciente
            WHERE p.id_usuario = %s
            ORDER BY r.id_receta DESC
        """
        params = (session.get('id_usuario'),)
    pagina, total_paginas = _paginar(cursor, sql, params)
    data = cursor.fetchall()
    cursor.close()
    return render_template("recetas/reMC.html", data=data, current_medico_id=current_medico_id,
                        pagina=pagina, total_paginas=total_paginas)


@app.route("/addRE", methods=["GET", "POST"])
@medico_required
def addRE():
    """Crea una nueva receta médica. Permiso exclusivo del Médico (D6),
    y solo puede recetar sobre sus propias consultas."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    # Solo se ofrecen para elegir las consultas del propio médico.
    cursor.execute("""
        SELECT co.id_consulta, co.fecha, p.nombre AS nombre_paciente
        FROM consulta co INNER JOIN paciente p ON co.id_paciente = p.id_paciente
        WHERE co.id_medico = %s ORDER BY co.fecha DESC
    """, (id_medico,))
    consultas = cursor.fetchall()
    # Solo medicamentos activos (D12-a): uno descontinuado no debe poder
    # recetarse de nuevo, aunque las recetas viejas lo sigan mostrando.
    cursor.execute("SELECT id_medicamento, nombre FROM medicamento WHERE estado = 'activo' ORDER BY nombre")
    medicamentos = cursor.fetchall()

    if request.method == "POST":
        id_consulta = request.form.get('id_consulta')
        id_medicamento = request.form.get('id_medicamento')
        cantidad = request.form.get('cantidad')
        indicaciones = request.form.get('indicaciones', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_consulta or not id_medicamento:
            error = "Debe seleccionar una consulta y un medicamento."
        elif not cantidad or int(cantidad) < 1:
            error = "Debe ingresar una cantidad válida."
        elif not any(str(c['id_consulta']) == str(id_consulta) for c in consultas):
            # Defensa extra: el id_consulta debe ser una de sus propias consultas.
            error = "Solo puede recetar sobre sus propias consultas."

        if error:
            return render_template("recetas/addRE.html",
                                error=error, consultas=consultas, medicamentos=medicamentos,
                                v_id_con=id_consulta, v_id_med=id_medicamento, v_cant=cantidad, v_ind=indicaciones)

        # --- INSERCIÓN ---
        try:
            sql = """INSERT INTO receta (id_consulta, id_medicamento, cantidad, indicaciones)
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (id_consulta, id_medicamento, cantidad, indicaciones))
            db.conexion.commit()
            flash("Receta creada exitosamente.", "success")
            return redirect(url_for('reMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al guardar: {e}", "danger")
            return redirect(url_for('reMC'))
        finally:
            cursor.close()

    cursor.close()
    return render_template("recetas/addRE.html", consultas=consultas, medicamentos=medicamentos)


@app.route("/editRE/<string:id>", methods=["GET", "POST"])
@medico_required
def editRE(id):
    """Edita una receta existente. Solo el médico dueño de la consulta
    asociada puede editarla."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    cursor.execute("""
        SELECT r.*, co.id_medico AS id_medico_consulta,
               p.nombre AS nombre_paciente, m.nombre AS nombre_medico
        FROM receta r
        INNER JOIN consulta co ON r.id_consulta = co.id_consulta
        INNER JOIN paciente p ON co.id_paciente = p.id_paciente
        INNER JOIN medico m ON co.id_medico = m.id_medico
        WHERE r.id_receta = %s
    """, (id,))
    receta = cursor.fetchone()

    if not receta:
        cursor.close()
        flash("Receta no encontrada.", "warning")
        return redirect(url_for('reMC'))

    if receta['id_medico_consulta'] != id_medico:
        cursor.close()
        flash("Solo puede editar las recetas que usted mismo creó.", "danger")
        return redirect(url_for('reMC'))

    cursor.execute("""
        SELECT co.id_consulta, co.fecha, p.nombre AS nombre_paciente
        FROM consulta co INNER JOIN paciente p ON co.id_paciente = p.id_paciente
        WHERE co.id_medico = %s ORDER BY co.fecha DESC
    """, (id_medico,))
    consultas = cursor.fetchall()
    # Solo medicamentos activos (D12-a), más el que ya tiene la receta
    # aunque esté descontinuado: mismo criterio que `editCI` con los
    # médicos.
    cursor.execute("""
        SELECT id_medicamento, nombre FROM medicamento
        WHERE estado = 'activo' OR id_medicamento = %s
        ORDER BY nombre
    """, (receta['id_medicamento'],))
    medicamentos = cursor.fetchall()

    if request.method == "POST":
        id_consulta = request.form.get('id_consulta')
        id_medicamento = request.form.get('id_medicamento')
        cantidad = request.form.get('cantidad')
        indicaciones = request.form.get('indicaciones', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_consulta or not id_medicamento:
            error = "Debe seleccionar una consulta y un medicamento."
        elif not cantidad or int(cantidad) < 1:
            error = "Debe ingresar una cantidad válida."
        elif not any(str(c['id_consulta']) == str(id_consulta) for c in consultas):
            error = "Solo puede recetar sobre sus propias consultas."

        if error:
            cursor.close()
            return render_template("recetas/editRE.html", item=receta,
                                consultas=consultas, medicamentos=medicamentos, error=error)

        try:
            sql = """UPDATE receta
                    SET id_consulta=%s, id_medicamento=%s, cantidad=%s, indicaciones=%s
                    WHERE id_receta=%s"""
            cursor.execute(sql, (id_consulta, id_medicamento, cantidad, indicaciones, id))
            db.conexion.commit()
            flash("Receta actualizada exitosamente.", "success")
            return redirect(url_for('reMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error: {e}", "danger")
            return redirect(url_for('reMC'))
        finally:
            cursor.close()

    cursor.close()
    return render_template("recetas/editRE.html", item=receta, consultas=consultas, medicamentos=medicamentos)


@app.route("/deleteRE/<string:id>", methods=["POST"])
@medico_required
def deleteRE(id):
    """Elimina una receta. Solo el médico dueño de la consulta asociada
    puede eliminarla."""
    cursor = db.conexion.cursor()
    id_medico = _current_medico_id()
    cursor.execute("""
        SELECT co.id_medico FROM receta r
        INNER JOIN consulta co ON r.id_consulta = co.id_consulta
        WHERE r.id_receta = %s
    """, (id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        flash("Receta no encontrada.", "warning")
        return redirect(url_for('reMC'))
    if row[0] != id_medico:
        cursor.close()
        flash("Solo puede eliminar las recetas que usted mismo creó.", "danger")
        return redirect(url_for('reMC'))
    try:
        cursor.execute("DELETE FROM receta WHERE id_receta = %s", (id,))
        db.conexion.commit()
        flash("Receta eliminada.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"No se pudo eliminar: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('reMC'))

# ===========================================================================
# MÓDULO: MEDICAMENTOS (CON DECORADOR @ADMIN_REQUIRED)
# ===========================================================================

@app.route("/meMC", methods=["GET"])
@admin_required
def meMC():
    insertObject = []
    if db.conexion.is_connected():
        cursor = db.conexion.cursor()
        cursor.execute("SELECT * FROM medicamento")
        myresult = cursor.fetchall()
        
        # Mapeo manual a diccionario para compatibilidad total con el HTML
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        
    return render_template("medicamentos/meMC.html", data=insertObject)

@app.route("/addME", methods=["GET", "POST"])
@admin_required
def addME():
    if request.method == "POST":
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        dosis = request.form.get('dosis', '').strip()

        # --- VALIDATIONS ---
        error = None
        if len(nombre) < 2:
            error = "El nombre del medicamento es demasiado corto."
        elif not dosis:
            error = "Los detalles de la dosis son obligatorios."

        if error:
            return render_template("medicamentos/addME.html", 
                                 error=error, v_nombre=nombre, 
                                 v_desc=descripcion, v_dosis=dosis)

        try:
            cursor = db.conexion.cursor()
            # Validar si ya existe
            cursor.execute("SELECT id_medicamento FROM medicamento WHERE nombre = %s", (nombre,))
            if cursor.fetchone():
                cursor.close()
                return render_template("medicamentos/addME.html", 
                                    error=f"El medicamento '{nombre}' ya existe.", 
                                    v_nombre=nombre, v_desc=descripcion, v_dosis=dosis)
            
            sql = "INSERT INTO medicamento (nombre, descripcion, dosis) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, descripcion, dosis))
            db.conexion.commit()
            cursor.close()
            return redirect(url_for('meMC'))
            
        except Exception as e:
            db.conexion.rollback()
            return render_template("medicamentos/addME.html", error=f"Error de base de datos: {e}")

    return render_template("medicamentos/addME.html")

@app.route("/editME/<string:id>", methods=["GET", "POST"])
@admin_required
def editME(id):
    cursor = db.conexion.cursor(dictionary=True)

    # Buscar datos actuales
    cursor.execute("SELECT * FROM medicamento WHERE id_medicamento = %s", (id,))
    medicamento = cursor.fetchone()

    if not medicamento:
        cursor.close()
        return redirect(url_for('meMC'))

    if request.method == "POST":
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        dosis = request.form.get('dosis', '').strip()

        # Validations
        error = None
        if len(nombre) < 2:
            error = "Nombre no válido."
        elif not dosis:
            error = "La dosis es obligatoria."

        if error:
            return render_template("medicamentos/editME.html",
                                medicamento=medicamento,
                                error=error)

        cursor.execute("SELECT id_medicamento FROM medicamento WHERE nombre = %s AND id_medicamento != %s", (nombre, id))
        if cursor.fetchone():
            return render_template("medicamentos/editME.html",
                                medicamento=medicamento,
                                error=f"El medicamento '{nombre}' ya existe.")

        try:
            sql = """UPDATE medicamento
                    SET nombre=%s, descripcion=%s, dosis=%s
                    WHERE id_medicamento=%s"""
            cursor.execute(sql, (nombre, descripcion, dosis, id))
            db.conexion.commit()
            cursor.close()
            return redirect(url_for('meMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("medicamentos/editME.html",
                                medicamento=medicamento,
                                error=f"Error de base de datos: {e}")

    cursor.close()
    return render_template("medicamentos/editME.html", medicamento=medicamento)

@app.route("/deleteME/<string:id>", methods=["POST"])
@admin_required
def deleteME(id):
    """Descontinúa un medicamento (decisión D12-a): **nunca lo borra**.

    Antes esta ruta hacía `DELETE FROM medicamento` de verdad, y solo
    funcionaba si ninguna receta lo había usado nunca — la FK rechazaba
    el borrado en cualquier otro caso. Ahora solo cambia el estado: el
    medicamento deja de ofrecerse al recetar, pero las recetas
    históricas que ya lo usaron lo siguen mostrando con normalidad."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM medicamento WHERE id_medicamento = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El medicamento no existe.", "warning")
            return redirect(url_for('meMC'))

        cursor.execute("UPDATE medicamento SET estado='descontinuado' WHERE id_medicamento = %s", (id,))
        db.conexion.commit()
        flash(f"{row['nombre']} fue descontinuado. Ya no se ofrecerá al recetar, pero las recetas "
              f"que ya lo usaron lo siguen mostrando.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al descontinuar el medicamento: {e}", "danger")
    finally:
        cursor.close()

    return redirect(url_for('meMC'))


@app.route("/reactivateME/<string:id>", methods=["POST"])
@admin_required
def reactivateME(id):
    """Revierte la baja lógica de un medicamento (D12-a). Vuelve a
    estar disponible para recetar."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT nombre FROM medicamento WHERE id_medicamento = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("El medicamento no existe.", "warning")
            return redirect(url_for('meMC'))

        cursor.execute("UPDATE medicamento SET estado='activo' WHERE id_medicamento = %s", (id,))
        db.conexion.commit()
        flash(f"{row['nombre']} vuelve a estar disponible para recetar.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al reactivar el medicamento: {e}", "danger")
    finally:
        cursor.close()

    return redirect(url_for('meMC'))

# ===========================================================================
# MÓDULO: CITAS MÉDICAS (CORREGIDO)
# ===========================================================================

# Separación mínima, en minutos, entre dos citas agendadas del mismo
# médico (decisión D4, 2026-08-31): estricta, es decir, una cita a las
# 2:00 bloquea de 2:01 a 2:29; las 2:30 sí quedan disponibles.
MINUTOS_ENTRE_CITAS = 30

def _check_appointment_conflicts(cursor, id_paciente, id_medico, fecha, exclude_id=None):
    """
    Valida las reglas de negocio de citas ANTES de insertar/actualizar:

    1) El PACIENTE no puede tener más de una cita agendada el mismo día
       (se compara solo la parte de fecha, sin importar la hora).
    2) El MÉDICO necesita al menos MINUTOS_ENTRE_CITAS minutos de
       separación entre dos citas suyas (decisión D4).

    Las citas con estado 'cancelada' se ignoran en ambas reglas: un
    horario cancelado vuelve a estar disponible (decisión D8). Por eso
    ya no puede haber un UNIQUE de base de datos para esto — ver
    BASE_DE_DATOS.md, migración 001.

    `cursor` puede ser un cursor normal o dictionary=True, no importa,
    aquí solo nos interesa saber si existe (o no) una fila en conflicto.

    Retorna un mensaje de error (str) si hay conflicto, o None si se
    puede guardar la cita sin problema.
    """
    fecha_dt = dv.parse_datetime_local(fecha)
    if fecha_dt is None:
        return "Fecha no válida."
    solo_fecha = fecha_dt.date()

    # 1) Paciente: máximo una cita agendada por día
    sql_paciente = """
        SELECT id_cita FROM cita
        WHERE id_paciente = %s AND DATE(fecha) = %s AND estado <> 'cancelada'
    """
    params_paciente = [id_paciente, solo_fecha]
    if exclude_id:
        sql_paciente += " AND id_cita != %s"
        params_paciente.append(exclude_id)
    cursor.execute(sql_paciente, tuple(params_paciente))
    if cursor.fetchone():
        return "Ya tienes una cita registrada para este día."

    # 2) Médico: separación mínima de MINUTOS_ENTRE_CITAS minutos
    sql_medico = """
        SELECT id_cita FROM cita
        WHERE id_medico = %s AND estado <> 'cancelada'
          AND ABS(TIMESTAMPDIFF(MINUTE, fecha, %s)) < %s
    """
    params_medico = [id_medico, fecha_dt, MINUTOS_ENTRE_CITAS]
    if exclude_id:
        sql_medico += " AND id_cita != %s"
        params_medico.append(exclude_id)
    cursor.execute(sql_medico, tuple(params_medico))
    if cursor.fetchone():
        return (f"El médico ya tiene una cita dentro de {MINUTOS_ENTRE_CITAS} minutos "
                "de esa hora. Por favor elija otro horario.")

    return None

# Permisos: el Administrador gestiona todas las citas (CRUD completo,
# ver addCI/editCI/deleteCI). El Médico solo lee su propia agenda — no
# puede modificarla (audio del autor, 2026-08-31). El Paciente solo ve
# las suyas.
@app.route("/ciMC", methods=["GET"])
@login_required
def ciMC():
    insertObject = []
    pagina, total_paginas = 1, 1
    if db.conexion.is_connected():
        cursor = db.conexion.cursor()
        base_sql = """
            SELECT c.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
            FROM cita c
            INNER JOIN medico m ON c.id_medico = m.id_medico
            INNER JOIN paciente p ON c.id_paciente = p.id_paciente
        """
        rol = session.get('rol')
        if rol == 'admin' or not _has_user_filter():
            sql, params = base_sql + " ORDER BY c.fecha DESC", ()
        elif rol == 'medico':
            sql, params = base_sql + " WHERE c.id_medico = %s ORDER BY c.fecha DESC", (_current_medico_id(),)
        else:
            sql, params = base_sql + " WHERE p.id_usuario = %s ORDER BY c.fecha DESC", (session.get('id_usuario'),)
        pagina, total_paginas = _paginar(cursor, sql, params)
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("citas/ciMC.html", data=insertObject, pagina=pagina, total_paginas=total_paginas)

@app.route("/addCI", methods=["GET", "POST"])
@admin_required
def addCI():
    cursor = db.conexion.cursor(dictionary=True)
    
    # Cargamos las listas para los Selects del formulario. Solo se ofrecen
    # pacientes y médicos activos (D11-a): uno dado de baja conserva sus
    # registros pero no debe recibir citas nuevas.
    cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT id_medico, nombre FROM medico WHERE estado = 'activo' ORDER BY nombre")
    medicos = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        id_med = request.form.get('id_medico')
        fecha = request.form.get('fecha')
        motivo = request.form.get('motivo', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac or not id_med:
            error = "Seleccione un paciente y un médico."
        elif not fecha:
            error = "La fecha y hora de la cita son obligatorias."
        else:
            fecha_valida, fecha_error = dv.validate_appointment_datetime(fecha)
            if not fecha_valida:
                error = fecha_error
            else:
                error = _check_appointment_conflicts(cursor, id_pac, id_med, fecha)

        if error:
            return render_template("citas/addCI.html", 
                                pacientes=pacientes, medicos=medicos,
                                error=error, v_id_pac=id_pac, 
                                v_id_med=id_med, v_fecha=fecha, v_motivo=motivo)
        try:
            sql = "INSERT INTO cita (id_paciente, id_medico, fecha, motivo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (id_pac, id_med, fecha, motivo))
            db.conexion.commit()
            flash("Cita agendada exitosamente.", "success")
            return redirect(url_for('ciMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("citas/addCI.html", 
                                pacientes=pacientes, medicos=medicos,
                                error=f"Error de base de datos: {e}")
        finally:
            cursor.close()

    return render_template("citas/addCI.html", pacientes=pacientes, medicos=medicos)

@app.route("/editCI/<string:id>", methods=["GET", "POST"])
@admin_required
def editCI(id):
    cursor = db.conexion.cursor(dictionary=True)

    # Se necesita el estado actual de entrada (no viene del formulario: se
    # cambia únicamente por la acción "Cancelar") para poder mostrarlo tanto
    # en el GET como si la validación falla y hay que re-renderizar.
    cursor.execute("SELECT estado FROM cita WHERE id_cita = %s", (id,))
    cita_actual = cursor.fetchone()
    if not cita_actual:
        cursor.close()
        flash("La cita no existe.", "warning")
        return redirect(url_for('ciMC'))
    estado_actual = cita_actual['estado']

    # Cargamos pacientes y médicos para que el usuario pueda reasignar la cita.
    # Solo activos (D11-a), **más el que ya tiene asignado la cita** aunque
    # esté dado de baja: si no, editar cualquier otro campo de una cita vieja
    # lo borraría del desplegable y la reasignaría sin querer.
    cursor.execute("""
        SELECT id_paciente, nombre FROM paciente
        WHERE estado = 'activo' OR id_paciente = (SELECT id_paciente FROM cita WHERE id_cita = %s)
        ORDER BY nombre
    """, (id,))
    pacientes = cursor.fetchall()
    cursor.execute("""
        SELECT id_medico, nombre FROM medico
        WHERE estado = 'activo' OR id_medico = (SELECT id_medico FROM cita WHERE id_cita = %s)
        ORDER BY nombre
    """, (id,))
    medicos = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        id_med = request.form.get('id_medico')
        fecha = request.form.get('fecha')
        motivo = request.form.get('motivo', '').strip()

        error = None
        if not id_pac or not id_med:
            error = "Debe seleccionar un paciente y un médico."
        elif not fecha:
            error = "La fecha es obligatoria."
        else:
            fecha_valida, fecha_error = dv.validate_appointment_datetime(fecha)
            if not fecha_valida:
                error = fecha_error
            else:
                error = _check_appointment_conflicts(cursor, id_pac, id_med, fecha, exclude_id=id)

        if error:
            return render_template("citas/editCI.html",
                                pacientes=pacientes, medicos=medicos,
                                error=error,
                                user={
                                    "id_cita": id,
                                    "id_paciente": id_pac,
                                    "id_medico": id_med,
                                    "fecha": fecha,
                                    "motivo": motivo,
                                    "estado": estado_actual
                                })

        try:
            sql = """
                UPDATE cita 
                SET id_paciente=%s, id_medico=%s, fecha=%s, motivo=%s
                WHERE id_cita=%s
            """
            cursor.execute(sql, (id_pac, id_med, fecha, motivo, id))
            db.conexion.commit()
            flash("Cita actualizada exitosamente.", "success")
            return redirect(url_for('ciMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("citas/editCI.html",
                                pacientes=pacientes, medicos=medicos,
                                error=f"Error al actualizar: {e}")
        finally:
            cursor.close()

    # GET: Obtener los datos actuales de la cita
    cursor.execute("SELECT * FROM cita WHERE id_cita = %s", (id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("La cita no existe.", "warning")
        return redirect(url_for('ciMC'))

    return render_template("citas/editCI.html", user=user, pacientes=pacientes, medicos=medicos)

@app.route("/deleteCI/<string:id>", methods=["POST"])
@admin_required
def deleteCI(id):
    cursor = db.conexion.cursor()
    try:
        sql = "DELETE FROM cita WHERE id_cita = %s"
        cursor.execute(sql, (id,))
        db.conexion.commit()
        flash("Cita eliminada exitosamente.", "success")
    except IntegrityError:
        db.conexion.rollback()
        flash("No se puede eliminar: esta cita ya tiene una consulta clínica asociada.", "danger")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Ocurrió un error inesperado: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('ciMC'))

@app.route("/cancelCI/<string:id>", methods=["POST"])
@login_required
def cancelCI(id):
    """El Paciente cancela su propia cita (decisión D8). Nunca se borra
    la fila: se marca 'cancelada', lo que además libera el horario para
    que otra persona pueda tomarlo (ver _check_appointment_conflicts,
    que ya ignora las citas canceladas)."""
    if session.get('rol') != 'paciente':
        flash("Solo los pacientes pueden cancelar sus propias citas.", "danger")
        return redirect(url_for('ciMC'))

    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.id_cita, c.fecha, c.estado, p.id_usuario
            FROM cita c
            INNER JOIN paciente p ON c.id_paciente = p.id_paciente
            WHERE c.id_cita = %s
        """, (id,))
        cita = cursor.fetchone()

        if not cita or cita['id_usuario'] != session.get('id_usuario'):
            flash("Cita no encontrada.", "warning")
        elif cita['estado'] == 'cancelada':
            flash("Esta cita ya está cancelada.", "warning")
        elif cita['fecha'].date() < dv.today_colombia():
            flash("No se pueden cancelar citas que ya pasaron.", "danger")
        else:
            cursor.execute("UPDATE cita SET estado='cancelada' WHERE id_cita = %s", (id,))
            db.conexion.commit()
            flash("Cita cancelada exitosamente.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al cancelar la cita: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('ciMC'))

@app.route("/disponibilidad")
@login_required
def disponibilidadCI():
    """Vista de disponibilidad (decisión D8): permite consultar los
    horarios ya ocupados de un médico en una fecha, antes de agendar o
    pedir una cita. No calcula huecos libres: informa qué horas evitar,
    dado el margen de MINUTOS_ENTRE_CITAS."""
    cursor = db.conexion.cursor(dictionary=True)
    # Solo médicos activos: consultar la disponibilidad de uno dado de baja
    # no tiene sentido, porque ya no recibe citas nuevas (D11-a).
    cursor.execute("SELECT id_medico, nombre FROM medico WHERE estado = 'activo' ORDER BY nombre")
    medicos = cursor.fetchall()
    cursor.close()
    return render_template("citas/disponibilidad.html", medicos=medicos, minutos=MINUTOS_ENTRE_CITAS)

@app.route("/api/disponibilidad/<string:id_medico>")
@login_required
def api_disponibilidad(id_medico):
    """Devuelve, en JSON, los horarios ya ocupados (no cancelados) de un
    médico en una fecha dada. No se exponen datos del paciente de cada
    cita: cualquier rol autenticado puede consultar disponibilidad."""
    fecha = dv.parse_date(request.args.get('fecha', ''))
    if not fecha:
        return jsonify({'error': 'Fecha no válida. Use el formato YYYY-MM-DD.'}), 400

    cursor = db.conexion.cursor()
    cursor.execute("""
        SELECT fecha FROM cita
        WHERE id_medico = %s AND DATE(fecha) = %s AND estado <> 'cancelada'
        ORDER BY fecha
    """, (id_medico, fecha))
    ocupados = [row[0].strftime('%H:%M') for row in cursor.fetchall()]
    cursor.close()
    return jsonify({
        'id_medico': id_medico,
        'fecha': fecha.isoformat(),
        'minutos_entre_citas': MINUTOS_ENTRE_CITAS,
        'ocupados': ocupados
    })

# ===========================================================================
# MÓDULO: CONSULTAS CLÍNICAS (CORREGIDO)
# ===========================================================================

# Permisos (D6): Médico crea/edita/borra sus propias consultas (permiso
# exclusivo, igual que historia clínica). Admin y Médico ven todas las
# consultas para lectura; Admin queda en solo lectura. Paciente ve las suyas.
@app.route("/coMC", methods=["GET"])
@login_required
def coMC():
    insertObject = []
    pagina, total_paginas = 1, 1
    current_medico_id = _current_medico_id() if session.get('rol') == 'medico' else None
    if db.conexion.is_connected():
        cursor = db.conexion.cursor()
        if session.get('rol') in ('admin', 'medico') or not _has_user_filter():
            sql = """
                SELECT co.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
                FROM consulta co
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                ORDER BY co.fecha DESC
            """
            params = ()
        else:
            sql = """
                SELECT co.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
                FROM consulta co
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                WHERE p.id_usuario = %s
                ORDER BY co.fecha DESC
            """
            params = (session.get('id_usuario'),)
        pagina, total_paginas = _paginar(cursor, sql, params)
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("consultas/coMC.html", data=insertObject, current_medico_id=current_medico_id,
                        pagina=pagina, total_paginas=total_paginas)

@app.route("/addCO", methods=["GET", "POST"])
@medico_required
def addconsultas():
    """Registra una consulta (diagnóstico y tratamiento). Permiso
    exclusivo del Médico (CLAUDE.md §2 / D6): el médico autor se toma
    siempre de la sesión, nunca del formulario."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    # Cargar la lista de pacientes para el selector del formulario. Solo
    # activos (D11-a): uno dado de baja no debe recibir registros nuevos.
    cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        tratamiento = request.form.get('tratamiento', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac:
            error = "Seleccione un paciente."
        elif not fecha:
            error = "La fecha y hora de la consulta son obligatorias."
        elif not tratamiento:
            error = "El tratamiento no puede estar vacío."
        elif not diagnostico:
            error = "El diagnóstico no puede estar vacío."
        else:
            fecha_valida, fecha_error = dv.validate_consultation_datetime(fecha)
            if not fecha_valida:
                error = fecha_error

        if error:
            return render_template(
                "consultas/addCO.html",
                pacientes=pacientes,
                error=error,
                v_id_pac=id_pac,
                v_fecha=fecha,
                v_tratamiento=tratamiento,
                v_diagnostico=diagnostico
            )

        try:
            sql = """
            INSERT INTO consulta
            (id_paciente, id_medico, fecha, tratamiento, diagnostico)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (id_pac, id_medico, fecha, tratamiento, diagnostico))
            db.conexion.commit()
            flash("Consulta registrada exitosamente.", "success")
            return redirect(url_for('coMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template(
                "consultas/addCO.html",
                pacientes=pacientes,
                error=f"Error de base de datos: {e}"
            )
        finally:
            cursor.close()

    cursor.close()
    return render_template("consultas/addCO.html", pacientes=pacientes)

@app.route("/editCO/<string:id>", methods=["GET", "POST"])
@medico_required
def editCO(id):
    """Edita una consulta. Solo el médico que la creó puede editarla."""
    cursor = db.conexion.cursor(dictionary=True)
    current_medico_id = _current_medico_id()

    cursor.execute("""
        SELECT co.*, m.nombre AS nombre_medico
        FROM consulta co INNER JOIN medico m ON co.id_medico = m.id_medico
        WHERE co.id_consulta = %s
    """, (id,))
    consulta = cursor.fetchone()

    if not consulta:
        cursor.close()
        flash("Consulta no encontrada.", "warning")
        return redirect(url_for('coMC'))

    if consulta['id_medico'] != current_medico_id:
        cursor.close()
        flash("Solo puede editar las consultas que usted mismo creó.", "danger")
        return redirect(url_for('coMC'))

    # Solo pacientes activos (D11-a), más el que ya tiene la consulta aunque
    # esté dado de baja: mismo criterio que `editCI` con los médicos.
    cursor.execute("""
        SELECT id_paciente, nombre FROM paciente
        WHERE estado = 'activo' OR id_paciente = %s
        ORDER BY nombre
    """, (consulta['id_paciente'],))
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        tratamiento = request.form.get('tratamiento', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac:
            error = "Debe seleccionar un paciente."
        elif not fecha:
            error = "La fecha es obligatoria."
        elif not tratamiento:
            error = "El tratamiento es obligatorio."
        elif not diagnostico:
            error = "El diagnóstico es obligatorio."
        else:
            fecha_valida, fecha_error = dv.validate_consultation_datetime(fecha)
            if not fecha_valida:
                error = fecha_error

        if error:
            cursor.close()
            return render_template("consultas/editCO.html",
                                pacientes=pacientes,
                                error=error,
                                user={
                                    "id_consulta": id,
                                    "id_paciente": id_pac,
                                    "id_medico": current_medico_id,
                                    "nombre_medico": consulta['nombre_medico'],
                                    "fecha": fecha,
                                    "tratamiento": tratamiento,
                                    "diagnostico": diagnostico
                                })

        try:
            # id_medico nunca se toma del formulario: la autoría no se
            # reasigna. El WHERE lo incluye como cinturón de seguridad extra.
            sql = """
                UPDATE consulta
                SET id_paciente=%s, fecha=%s, tratamiento=%s, diagnostico=%s
                WHERE id_consulta=%s AND id_medico=%s
            """
            cursor.execute(sql, (id_pac, fecha, tratamiento, diagnostico, id, current_medico_id))
            db.conexion.commit()
            flash("Consulta actualizada exitosamente.", "success")
            return redirect(url_for('coMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al actualizar: {e}", "danger")
            return redirect(url_for('coMC'))
        finally:
            cursor.close()

    cursor.close()
    return render_template("consultas/editCO.html", user=consulta, pacientes=pacientes)

@app.route("/deleteCO/<string:id>", methods=["POST"])
@medico_required
def deleteCO(id):
    """Elimina una consulta. Solo el médico que la creó puede eliminarla."""
    cursor = db.conexion.cursor()
    current_medico_id = _current_medico_id()
    cursor.execute("SELECT id_medico FROM consulta WHERE id_consulta = %s", (id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        flash("Consulta no encontrada.", "warning")
        return redirect(url_for('coMC'))
    if row[0] != current_medico_id:
        cursor.close()
        flash("Solo puede eliminar las consultas que usted mismo creó.", "danger")
        return redirect(url_for('coMC'))
    try:
        sql = "DELETE FROM consulta WHERE id_consulta = %s"
        cursor.execute(sql, (id,))
        db.conexion.commit()
        flash("Consulta eliminada.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"No se pudo eliminar el registro: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('coMC'))

# ===========================================================================
# MÓDULO: HISTORIAS CLÍNICAS (CORREGIDO)
# ===========================================================================

# Permisos: Admin y Médico ven todas las historias (D5: el admin tiene
# lectura general). El Paciente solo ve las suyas. Crear/editar/borrar
# es exclusivo del Médico (ver medico_required más abajo).
@app.route("/hiMC", methods=["GET"])
@login_required
def hiMC():
    insertObject = []
    pagina, total_paginas = 1, 1
    current_medico_id = _current_medico_id() if session.get('rol') == 'medico' else None
    if db.conexion.is_connected():
        cursor = db.conexion.cursor()
        if session.get('rol') in ('admin', 'medico') or not _has_user_filter():
            sql = """
                SELECT h.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM historia h
                INNER JOIN paciente p ON h.id_paciente = p.id_paciente
                INNER JOIN medico m ON h.id_medico = m.id_medico
                ORDER BY h.fecha DESC
            """
            params = ()
        else:
            sql = """
                SELECT h.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM historia h
                INNER JOIN paciente p ON h.id_paciente = p.id_paciente
                INNER JOIN medico m ON h.id_medico = m.id_medico
                WHERE p.id_usuario = %s
                ORDER BY h.fecha DESC
            """
            params = (session.get('id_usuario'),)
        pagina, total_paginas = _paginar(cursor, sql, params)
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("historias/hiMC.html", data=insertObject, current_medico_id=current_medico_id,
                        pagina=pagina, total_paginas=total_paginas)

@app.route("/addHI", methods=["GET", "POST"])
@medico_required
def addHI():
    """Crea un registro de historia clínica. Permiso exclusivo del
    Médico (CLAUDE.md §2). El médico autor se toma siempre de la
    sesión, nunca del formulario, para que nadie pueda atribuirle la
    nota a otro doctor manipulando el POST."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    if request.method == "POST":
        id_paciente = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        descripcion = request.form.get('descripcion', '').strip()
        notas = request.form.get('notas', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_paciente:
            error = "Seleccione un paciente."
        elif not fecha:
            error = "La fecha es obligatoria."
        elif not descripcion:
            error = "La descripción no puede estar vacía."
        else:
            fecha_valida, fecha_error = dv.validate_clinical_record_datetime(fecha)
            if not fecha_valida:
                error = fecha_error

        if error:
            # Recargamos la lista para el selector en caso de error
            cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
            pacientes = cursor.fetchall()
            cursor.close()
            return render_template("historias/addHI.html",
                                pacientes=pacientes, error=error,
                                v_id_pac=id_paciente,
                                v_fecha=fecha, v_desc=descripcion, v_notas=notas)

        try:
            sql = "INSERT INTO historia (id_paciente, id_medico, fecha, descripcion, notas) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (id_paciente, id_medico, fecha, descripcion, notas))
            db.conexion.commit()
            flash("Historia clínica agregada.", "success")
            return redirect(url_for('hiMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al guardar: {e}", "danger")
            return redirect(url_for('hiMC'))
        finally:
            cursor.close()

    # GET: cargamos pacientes para el selector (el médico ya es el de sesión)
    cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
    pacientes = cursor.fetchall()
    cursor.close()
    return render_template("historias/addHI.html", pacientes=pacientes)

@app.route("/editHI/<string:id>", methods=["GET", "POST"])
@medico_required
def editHI(id):
    """Edita un registro de historia clínica. Solo el médico que la
    creó puede editarla — ni otro médico ni el administrador."""
    cursor = db.conexion.cursor(dictionary=True)
    current_medico_id = _current_medico_id()

    cursor.execute("""
        SELECT h.*, m.nombre AS nombre_medico
        FROM historia h INNER JOIN medico m ON h.id_medico = m.id_medico
        WHERE h.id_historia = %s
    """, (id,))
    historia = cursor.fetchone()

    if not historia:
        cursor.close()
        flash("Registro no encontrado.", "warning")
        return redirect(url_for('hiMC'))

    if historia['id_medico'] != current_medico_id:
        cursor.close()
        flash("Solo puede editar las historias clínicas que usted mismo creó.", "danger")
        return redirect(url_for('hiMC'))

    # Cargamos el catálogo de pacientes para el select. Solo activos
    # (D11-a), más el que ya tiene el registro aunque esté dado de baja.
    cursor.execute("""
        SELECT id_paciente, nombre FROM paciente
        WHERE estado = 'activo' OR id_paciente = %s
        ORDER BY nombre
    """, (historia['id_paciente'],))
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_paciente = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        descripcion = request.form.get('descripcion', '').strip()
        notas = request.form.get('notas', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_paciente:
            error = "Debe seleccionar un paciente."
        elif not fecha:
            error = "La fecha es obligatoria."
        elif not descripcion:
            error = "La descripción no puede estar vacía."
        else:
            fecha_valida, fecha_error = dv.validate_clinical_record_datetime(fecha)
            if not fecha_valida:
                error = fecha_error

        if error:
            cursor.close()
            return render_template("historias/editHI.html",
                                pacientes=pacientes, error=error,
                                user={
                                    "id_historia": id,
                                    "id_paciente": id_paciente,
                                    "id_medico": current_medico_id,
                                    "nombre_medico": historia['nombre_medico'],
                                    "fecha": fecha,
                                    "descripcion": descripcion,
                                    "notas": notas
                                })

        try:
            # El WHERE incluye id_medico como cinturón de seguridad extra,
            # aunque ya se validó la autoría arriba.
            sql = """
                UPDATE historia
                SET id_paciente=%s, fecha=%s, descripcion=%s, notas=%s
                WHERE id_historia=%s AND id_medico=%s
            """
            cursor.execute(sql, (id_paciente, fecha, descripcion, notas, id, current_medico_id))
            db.conexion.commit()
            flash("Historia clínica actualizada exitosamente.", "success")
            return redirect(url_for('hiMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error de base de datos: {e}", "danger")
            return redirect(url_for('hiMC'))
        finally:
            cursor.close()

    cursor.close()
    return render_template("historias/editHI.html", user=historia, pacientes=pacientes)

@app.route("/deleteHI/<string:id>", methods=["POST"])
@medico_required
def deleteHI(id):
    """Elimina un registro de historia clínica. Solo el médico que la
    creó puede eliminarla."""
    cursor = db.conexion.cursor()
    current_medico_id = _current_medico_id()
    try:
        cursor.execute("SELECT id_medico FROM historia WHERE id_historia = %s", (id,))
        row = cursor.fetchone()
        if not row:
            flash("Registro no encontrado.", "warning")
        elif row[0] != current_medico_id:
            flash("Solo puede eliminar las historias clínicas que usted mismo creó.", "danger")
        else:
            cursor.execute("DELETE FROM historia WHERE id_historia = %s", (id,))
            db.conexion.commit()
            flash("Historia clínica eliminada exitosamente.", "success")
    except IntegrityError:
        db.conexion.rollback()
        flash("No se puede eliminar: esta historia clínica está vinculada a otros datos clínicos.", "danger")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Ocurrió un error inesperado: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('hiMC'))

# ===========================================================================
# MÓDULO: EXÁMENES DE LABORATORIO (CORREGIDO)
# ===========================================================================

# Permisos: Admin y Médico ven todos los exámenes (lectura amplia, igual
# que historia). El Paciente solo ve los suyos. Escritura dividida por
# campo (D7): el Médico solicita, el Administrador carga el resultado.
@app.route("/exMC", methods=["GET"])
@login_required
def exMC():
    insertObject = []
    pagina, total_paginas = 1, 1
    current_medico_id = _current_medico_id() if session.get('rol') == 'medico' else None
    if db.conexion.is_connected():
        cursor = db.conexion.cursor()
        if session.get('rol') in ('admin', 'medico') or not _has_user_filter():
            sql = """
                SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM examen e
                INNER JOIN paciente p ON e.id_paciente = p.id_paciente
                INNER JOIN medico m ON e.id_medico = m.id_medico
                ORDER BY e.fecha_solicitud DESC
            """
            params = ()
        else:
            sql = """
                SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM examen e
                INNER JOIN paciente p ON e.id_paciente = p.id_paciente
                INNER JOIN medico m ON e.id_medico = m.id_medico
                WHERE p.id_usuario = %s
                ORDER BY e.fecha_solicitud DESC
            """
            params = (session.get('id_usuario'),)
        pagina, total_paginas = _paginar(cursor, sql, params)
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("examenes/exMC.html", data=insertObject, current_medico_id=current_medico_id,
                        pagina=pagina, total_paginas=total_paginas)

@app.route("/addEX", methods=["GET", "POST"])
@medico_required
def addEX():
    """Solicita un examen de laboratorio. Permiso exclusivo del Médico
    (decisión D7): el médico solicitante se toma siempre de la sesión.
    El resultado lo carga después el Administrador (laboratorio) desde
    editEX — al crear la solicitud todavía no existe."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    if request.method == "POST":
        id_paciente = request.form.get('id_paciente')
        tipo_examen = request.form.get('tipo_examen', '').strip()
        fecha_solicitud = request.form.get('fecha_solicitud')

        # --- VALIDATIONS ---
        error = None
        if not id_paciente:
            error = "Seleccione un paciente."
        elif not tipo_examen:
            error = "El tipo de examen es obligatorio."
        elif not fecha_solicitud:
            error = "La fecha de solicitud es obligatoria."
        else:
            fecha_valida, fecha_error = dv.validate_lab_request_datetime(fecha_solicitud)
            if not fecha_valida:
                error = fecha_error

        if error:
            cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
            pacientes = cursor.fetchall()
            cursor.close()
            return render_template("examenes/addEX.html",
                                pacientes=pacientes, error=error,
                                v_id_pac=id_paciente,
                                v_tipo=tipo_examen, v_fecha_s=fecha_solicitud)

        try:
            sql = """
                INSERT INTO examen (id_paciente, id_medico, tipo_examen, fecha_solicitud)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (id_paciente, id_medico, tipo_examen, fecha_solicitud))
            db.conexion.commit()
            flash("Examen solicitado exitosamente.", "success")
            return redirect(url_for('exMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error al registrar el examen: {e}", "danger")
            return redirect(url_for('exMC'))
        finally:
            cursor.close()

    # GET: cargamos pacientes para el selector (el médico ya es el de sesión)
    cursor.execute("SELECT id_paciente, nombre FROM paciente WHERE estado = 'activo' ORDER BY nombre")
    pacientes = cursor.fetchall()
    cursor.close()
    return render_template("examenes/addEX.html", pacientes=pacientes)

@app.route("/editEX/<string:id>", methods=["GET", "POST"])
@login_required
def editEX(id):
    """Edita un examen de laboratorio con permisos divididos por campo
    (decisión D7):
      - Médico (solo el que lo solicitó): corrige la solicitud
        (paciente, tipo de examen, fecha de solicitud).
      - Administrador: carga el resultado (fecha de resultado y
        hallazgos) — no puede tocar la solicitud.
    Ningún otro rol puede entrar."""
    rol = session.get('rol')
    if rol not in ('medico', 'admin'):
        flash("Acceso restringido a médicos y administradores.", "danger")
        return redirect(url_for('menu'))

    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
        FROM examen e
        INNER JOIN paciente p ON e.id_paciente = p.id_paciente
        INNER JOIN medico m ON e.id_medico = m.id_medico
        WHERE e.id_examen = %s
    """, (id,))
    examen = cursor.fetchone()

    if not examen:
        cursor.close()
        flash("Examen no encontrado.", "warning")
        return redirect(url_for('exMC'))

    es_medico = (rol == 'medico')
    if es_medico and examen['id_medico'] != _current_medico_id():
        cursor.close()
        flash("Solo puede editar los exámenes que usted mismo solicitó.", "danger")
        return redirect(url_for('exMC'))

    pacientes = []
    if es_medico:
        # Solo activos (D11-a), más el que ya tiene el examen aunque esté
        # dado de baja.
        cursor.execute("""
            SELECT id_paciente, nombre FROM paciente
            WHERE estado = 'activo' OR id_paciente = %s
            ORDER BY nombre
        """, (examen['id_paciente'],))
        pacientes = cursor.fetchall()

    if request.method == "POST":
        if es_medico:
            id_paciente = request.form.get('id_paciente')
            tipo_examen = request.form.get('tipo_examen', '').strip()
            fecha_solicitud = request.form.get('fecha_solicitud')

            error = None
            if not id_paciente:
                error = "Debe seleccionar un paciente."
            elif not tipo_examen:
                error = "El tipo de examen es obligatorio."
            elif not fecha_solicitud:
                error = "La fecha de solicitud es obligatoria."
            else:
                fecha_valida, fecha_error = dv.validate_lab_request_datetime(fecha_solicitud)
                if not fecha_valida:
                    error = fecha_error

            if error:
                cursor.close()
                return render_template("examenes/editEX.html", examen=examen,
                                    pacientes=pacientes, error=error, es_medico=True)

            try:
                sql = """
                    UPDATE examen
                    SET id_paciente=%s, tipo_examen=%s, fecha_solicitud=%s
                    WHERE id_examen=%s AND id_medico=%s
                """
                cursor.execute(sql, (id_paciente, tipo_examen, fecha_solicitud, id, _current_medico_id()))
                db.conexion.commit()
                flash("Solicitud de examen actualizada exitosamente.", "success")
                return redirect(url_for('exMC'))
            except Exception as e:
                db.conexion.rollback()
                flash(f"Error de base de datos: {e}", "danger")
                return redirect(url_for('exMC'))
            finally:
                cursor.close()
        else:
            # Administrador: solo puede cargar el resultado, nunca la solicitud.
            fecha_resultado = request.form.get('fecha_resultado')
            resultado = request.form.get('resultado', '').strip()
            try:
                sql = "UPDATE examen SET fecha_resultado=%s, resultado=%s WHERE id_examen=%s"
                cursor.execute(sql, (fecha_resultado or None, resultado, id))
                db.conexion.commit()
                flash("Resultado de laboratorio guardado exitosamente.", "success")
                return redirect(url_for('exMC'))
            except Exception as e:
                db.conexion.rollback()
                flash(f"Error de base de datos: {e}", "danger")
                return redirect(url_for('exMC'))
            finally:
                cursor.close()

    cursor.close()
    return render_template("examenes/editEX.html", examen=examen,
                        pacientes=pacientes, es_medico=es_medico)

@app.route("/deleteEX/<string:id>", methods=["POST"])
@admin_required
def deleteEX(id):
    cursor = db.conexion.cursor()
    try:
        sql = "DELETE FROM examen WHERE id_examen = %s"
        cursor.execute(sql, (id,))
        db.conexion.commit()
        flash("Examen eliminado exitosamente.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error al eliminar el examen: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('exMC'))

# ===========================================================================
# API: DETAIL VIEW (JSON for modal)
# ===========================================================================
@app.route("/api/view/<module>/<string:id>")
@login_required
def api_view(module, id):
    cursor = db.conexion.cursor(dictionary=True)
    fields = {}
    try:
        if module == 'cita':
            cursor.execute("""
                SELECT c.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente,
                       p.id_usuario AS paciente_id_usuario
                FROM cita c
                INNER JOIN medico m ON c.id_medico = m.id_medico
                INNER JOIN paciente p ON c.id_paciente = p.id_paciente
                WHERE c.id_cita = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Ver una cita ajena por este endpoint no debe ser posible solo por
            # estar logueado: el médico ve la suya, el paciente la suya, el
            # resto se rechaza — mismo criterio de tres vías que usa `ciMC`.
            rol = session.get('rol')
            if rol == 'admin':
                puede_ver = True
            elif rol == 'medico':
                puede_ver = row['id_medico'] == _current_medico_id()
            else:
                puede_ver = row['paciente_id_usuario'] == session.get('id_usuario')
            if not puede_ver:
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            # Mismo criterio que `editCI`: activos más el que ya tiene la cita.
            cursor.execute("""
                SELECT id_paciente, nombre FROM paciente
                WHERE estado = 'activo' OR id_paciente = %s ORDER BY nombre
            """, (row['id_paciente'],))
            pacs = cursor.fetchall()
            cursor.execute("""
                SELECT id_medico, nombre FROM medico
                WHERE estado = 'activo' OR id_medico = %s ORDER BY nombre
            """, (row['id_medico'],))
            meds = cursor.fetchall()
            # Solo el administrador puede editar citas (CRUD completo); el
            # resto de roles ven este módulo en modo lectura, igual que en
            # la página completa (ciMC/addCI/editCI son @admin_required).
            es_admin = session.get('rol') == 'admin'
            fields = {
                'id_paciente': {'label': 'Paciente', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': es_admin, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Médico', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': es_admin, 'type': 'select',
                    'options': [{'value': m['id_medico'], 'label': m['nombre']} for m in meds]},
                'fecha': {'label': 'Fecha y Hora', 'value': str(row['fecha']), 'editable': es_admin, 'type': 'datetime-local'},
                'motivo': {'label': 'Motivo', 'value': row.get('motivo', ''), 'editable': es_admin, 'type': 'textarea'},
                'estado': {'label': 'Estado', 'value': row.get('estado', ''), 'display': row.get('estado', '').capitalize(), 'editable': False},
            }
        elif module == 'consulta':
            cursor.execute("""
                SELECT co.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente,
                       p.id_usuario AS paciente_id_usuario
                FROM consulta co
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                WHERE co.id_consulta = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Admin y médico ven cualquier consulta (lectura amplia, mismo
            # criterio que `coMC`); el paciente solo puede ver las suyas.
            if session.get('rol') not in ('admin', 'medico') and row['paciente_id_usuario'] != session.get('id_usuario'):
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            # Activos más el que ya tiene el registro (D11-a), mismo
            # criterio que `editCI` con los médicos.
            cursor.execute("""
                SELECT id_paciente, nombre FROM paciente
                WHERE estado = 'activo' OR id_paciente = %s ORDER BY nombre
            """, (row['id_paciente'],))
            pacs = cursor.fetchall()
            # Solo el médico autor puede editar su propia consulta (D6, mismo
            # criterio que historia). El administrador tiene solo lectura.
            puede_editar = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            fields = {
                'id_paciente': {'label': 'Paciente', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Médico', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'fecha': {'label': 'Fecha', 'value': str(row['fecha']), 'editable': puede_editar, 'type': 'datetime-local'},
                'diagnostico': {'label': 'Diagnóstico', 'value': row.get('diagnostico', ''), 'editable': puede_editar, 'type': 'textarea'},
                'tratamiento': {'label': 'Tratamiento', 'value': row.get('tratamiento', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'historia':
            cursor.execute("""
                SELECT h.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico,
                       p.id_usuario AS paciente_id_usuario
                FROM historia h
                INNER JOIN paciente p ON h.id_paciente = p.id_paciente
                INNER JOIN medico m ON h.id_medico = m.id_medico
                WHERE h.id_historia = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Admin y médico ven cualquier historia (lectura amplia, mismo
            # criterio que `hiMC`); el paciente solo puede ver las suyas.
            if session.get('rol') not in ('admin', 'medico') and row['paciente_id_usuario'] != session.get('id_usuario'):
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            # Activos más el que ya tiene el registro (D11-a), mismo
            # criterio que `editCI` con los médicos.
            cursor.execute("""
                SELECT id_paciente, nombre FROM paciente
                WHERE estado = 'activo' OR id_paciente = %s ORDER BY nombre
            """, (row['id_paciente'],))
            pacs = cursor.fetchall()
            # Solo el médico autor puede editar su propia historia clínica
            # (ni otro médico ni el administrador). El campo 'id_medico'
            # nunca es editable: la autoría no se reasigna.
            puede_editar = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            fields = {
                'id_paciente': {'label': 'Paciente', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Médico', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'fecha': {'label': 'Fecha', 'value': str(row['fecha']), 'editable': puede_editar, 'type': 'date'},
                'descripcion': {'label': 'Descripción', 'value': row.get('descripcion', ''), 'editable': puede_editar, 'type': 'textarea'},
                'notas': {'label': 'Notas', 'value': row.get('notas', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'examen':
            cursor.execute("""
                SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico,
                       p.id_usuario AS paciente_id_usuario
                FROM examen e
                INNER JOIN paciente p ON e.id_paciente = p.id_paciente
                INNER JOIN medico m ON e.id_medico = m.id_medico
                WHERE e.id_examen = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Admin y médico ven cualquier examen (lectura amplia, mismo
            # criterio que `exMC`); el paciente solo puede ver los suyos.
            if session.get('rol') not in ('admin', 'medico') and row['paciente_id_usuario'] != session.get('id_usuario'):
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            # Activos más el que ya tiene el registro (D11-a), mismo
            # criterio que `editCI` con los médicos.
            cursor.execute("""
                SELECT id_paciente, nombre FROM paciente
                WHERE estado = 'activo' OR id_paciente = %s ORDER BY nombre
            """, (row['id_paciente'],))
            pacs = cursor.fetchall()
            # Permisos divididos por campo (D7): el médico solicitante
            # edita la solicitud; el administrador carga el resultado.
            es_medico_propio = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            es_admin = session.get('rol') == 'admin'
            fields = {
                'id_paciente': {'label': 'Paciente', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': es_medico_propio, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Médico', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'tipo_examen': {'label': 'Tipo de Examen', 'value': row.get('tipo_examen', ''), 'editable': es_medico_propio, 'type': 'text'},
                'fecha_solicitud': {'label': 'Fecha de Solicitud', 'value': str(row.get('fecha_solicitud', '')), 'editable': es_medico_propio, 'type': 'date'},
                'fecha_resultado': {'label': 'Fecha de Resultado', 'value': str(row.get('fecha_resultado', '') or ''), 'editable': es_admin, 'type': 'date'},
                'resultado': {'label': 'Resultado', 'value': row.get('resultado', ''), 'editable': es_admin, 'type': 'textarea'},
            }
        elif module == 'receta':
            cursor.execute("""
                SELECT r.*, co.id_medico AS id_medico_consulta,
                       p.nombre AS nombre_paciente, m.nombre AS nombre_medico, med.nombre AS nombre_medicamento,
                       p.id_usuario AS paciente_id_usuario
                FROM receta r
                INNER JOIN consulta co ON r.id_consulta = co.id_consulta
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN medicamento med ON r.id_medicamento = med.id_medicamento
                WHERE r.id_receta = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Admin y médico ven cualquier receta (lectura amplia, mismo
            # criterio que `reMC`); el paciente solo puede ver las suyas.
            if session.get('rol') not in ('admin', 'medico') and row['paciente_id_usuario'] != session.get('id_usuario'):
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            # La receta no tiene id_medico propio: su dueño es el médico de
            # la consulta a la que pertenece (D6).
            current_medico_id = _current_medico_id()
            puede_editar = (session.get('rol') == 'medico' and row['id_medico_consulta'] == current_medico_id)
            cons = []
            if puede_editar:
                cursor.execute("""
                    SELECT co.id_consulta, co.fecha, p.nombre AS nombre_paciente
                    FROM consulta co INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                    WHERE co.id_medico = %s ORDER BY co.fecha DESC
                """, (current_medico_id,))
                cons = cursor.fetchall()
            # Activos más el que ya tiene la receta (D12-a), mismo criterio
            # que `editCI` con los médicos.
            cursor.execute("""
                SELECT id_medicamento, nombre FROM medicamento
                WHERE estado = 'activo' OR id_medicamento = %s ORDER BY nombre
            """, (row['id_medicamento'],))
            meds = cursor.fetchall()
            fields = {
                'patient': {'label': 'Paciente', 'value': row['nombre_paciente'], 'editable': False},
                'doctor': {'label': 'Médico', 'value': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'id_consulta': {'label': 'Consulta', 'value': row['id_consulta'],
                    'display': f"#{row['id_consulta']} — {row['nombre_paciente']}", 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': c['id_consulta'], 'label': f"#{c['id_consulta']} — {c['nombre_paciente']} — {c['fecha']}"} for c in cons]},
                'id_medicamento': {'label': 'Medicamento', 'value': row['id_medicamento'], 'display': row['nombre_medicamento'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': m['id_medicamento'], 'label': m['nombre']} for m in meds]},
                'cantidad': {'label': 'Cantidad', 'value': row.get('cantidad', ''), 'editable': puede_editar, 'type': 'number'},
                'indicaciones': {'label': 'Indicaciones', 'value': row.get('indicaciones', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'medico':
            # Ver el detalle de un médico (datos de contacto, identidad) es
            # exclusivo del administrador, igual que el módulo completo
            # (medMC es @admin_required) — médico y paciente no deben poder
            # consultarlo por este endpoint aunque estén logueados.
            if session.get('rol') != 'admin':
                return jsonify({'error': 'Acceso restringido solo para administradores.'}), 403
            cursor.execute("""
                SELECT medico.*, especialidad.nombre AS nombre_es,
                       usuario.username, usuario.estado AS estado_cuenta
                FROM medico
                INNER JOIN especialidad ON medico.id_especialidad = especialidad.id_especialidad
                LEFT JOIN usuario ON medico.id_usuario = usuario.id_usuario
                WHERE id_medico = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT * FROM especialidad")
            esps = cursor.fetchall()
            # Solo el administrador gestiona médicos (CRUD completo).
            es_admin = session.get('rol') == 'admin'
            # Paridad con editMED.html (T5.10): esa vista también gestiona la
            # cuenta de acceso del médico (usuario + contraseña), así que el
            # modal debe mostrar que existe — nunca la contraseña, mismo
            # criterio ya usado en el módulo 'usuario'. No es editable aquí:
            # cambiar usuario/contraseña se hace en la vista de edición, que
            # es la única que ya valida duplicados y longitud mínima.
            if row['id_usuario'] and row['estado_cuenta'] == 'activo':
                acceso_display = f"{row['username']} (Activo)"
            elif row['id_usuario']:
                acceso_display = f"{row['username']} (Desactivado)"
            else:
                acceso_display = 'Sin cuenta de acceso'
            fields = {
                'nombre': {'label': 'Nombre Completo', 'value': row['nombre'], 'editable': es_admin, 'type': 'text'},
                'numero_identidad': {'label': 'Número de Identidad', 'value': row['numero_identidad'], 'editable': es_admin, 'type': 'text'},
                'id_especialidad': {'label': 'Especialidad', 'value': row['id_especialidad'], 'display': row['nombre_es'], 'editable': es_admin, 'type': 'select',
                    'options': [{'value': e['id_especialidad'], 'label': e['nombre']} for e in esps]},
                'telefono': {'label': 'Teléfono', 'value': row['telefono'], 'editable': es_admin, 'type': 'text'},
                'email': {'label': 'Correo Electrónico', 'value': row['email'], 'editable': es_admin, 'type': 'email'},
                'username': {'label': 'Usuario del Sistema', 'value': row.get('username') or '',
                    'display': acceso_display, 'editable': False},
                # El estado no se edita por formulario: se cambia con las
                # acciones Desactivar/Reactivar, que tienen su propia regla
                # (D11-a) — mismo criterio que `cita.estado`.
                'estado': {'label': 'Estado', 'value': row.get('estado', ''),
                    'display': (row.get('estado') or '').capitalize(), 'editable': False},
            }
        elif module == 'paciente':
            cursor.execute("SELECT p.*, u.username FROM paciente p LEFT JOIN usuario u ON p.id_usuario = u.id_usuario WHERE p.id_paciente = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Admin y médico ven cualquier paciente (lectura amplia, mismo
            # criterio que `paMC`); el paciente solo puede ver su propio
            # perfil — sin esto, cualquier paciente podía leer los datos
            # personales (documento, teléfono, dirección) de otro cambiando
            # el id en la URL de este endpoint.
            if session.get('rol') not in ('admin', 'medico') and row.get('id_usuario') != session.get('id_usuario'):
                return jsonify({'error': 'No autorizado para ver este registro.'}), 403
            cursor.execute("SELECT id_usuario, username FROM usuario")
            users = cursor.fetchall()
            user_options = [{'value': '', 'label': '-- Sin usuario vinculado --'}] + [{'value': u['id_usuario'], 'label': u['username']} for u in users]
            # Solo el administrador edita pacientes (CRUD completo); médico y
            # paciente ven este módulo en modo lectura.
            es_admin = session.get('rol') == 'admin'
            fields = {
                'nombre': {'label': 'Nombre Completo', 'value': row['nombre'], 'editable': es_admin, 'type': 'text'},
                'tipo_documento': {'label': 'Tipo de Documento', 'value': row.get('tipo_documento', ''), 'editable': es_admin, 'type': 'text'},
                'numero_documento': {'label': 'Número de Documento', 'value': row.get('numero_documento', ''), 'editable': es_admin, 'type': 'text'},
                'fecha_nacimiento': {'label': 'Fecha de Nacimiento', 'value': str(row.get('fecha_nacimiento', '')), 'editable': es_admin, 'type': 'date'},
                'telefono': {'label': 'Teléfono', 'value': row.get('telefono', ''), 'editable': es_admin, 'type': 'text'},
                'email': {'label': 'Correo Electrónico', 'value': row.get('email', ''), 'editable': es_admin, 'type': 'email'},
                'direccion': {'label': 'Dirección', 'value': row.get('direccion', ''), 'editable': es_admin, 'type': 'text'},
                'id_usuario': {'label': 'Usuario Vinculado', 'value': row.get('id_usuario', ''), 'display': row.get('username') or 'Ninguno', 'editable': es_admin, 'type': 'select', 'options': user_options},
                # El estado no se edita por formulario: se cambia con las
                # acciones Desactivar/Reactivar del listado (D11-a), mismo
                # criterio que `medico.estado`.
                'estado': {'label': 'Estado', 'value': row.get('estado', ''),
                    'display': (row.get('estado') or '').capitalize(), 'editable': False},
            }
        elif module == 'especialidad':
            cursor.execute("SELECT * FROM especialidad WHERE id_especialidad = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Solo el administrador gestiona especialidades (CRUD completo).
            es_admin = session.get('rol') == 'admin'
            fields = {
                'nombre': {'label': 'Nombre de la Especialidad', 'value': row['nombre'], 'editable': es_admin, 'type': 'text'},
                'descripcion': {'label': 'Descripción', 'value': row.get('descripcion', ''), 'editable': es_admin, 'type': 'textarea'},
            }
        elif module == 'medicamento':
            cursor.execute("SELECT * FROM medicamento WHERE id_medicamento = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Solo el administrador gestiona el catálogo de medicamentos.
            es_admin = session.get('rol') == 'admin'
            fields = {
                'nombre': {'label': 'Nombre del Medicamento', 'value': row['nombre'], 'editable': es_admin, 'type': 'text'},
                'dosis': {'label': 'Dosis', 'value': row.get('dosis', ''), 'editable': es_admin, 'type': 'text'},
                'descripcion': {'label': 'Descripción', 'value': row.get('descripcion', ''), 'editable': es_admin, 'type': 'textarea'},
                # El estado no se edita por formulario: se cambia con las
                # acciones Descontinuar/Reactivar del listado (D12-a), mismo
                # criterio que `medico.estado` y `paciente.estado`.
                'estado': {'label': 'Estado', 'value': row.get('estado', ''),
                    'display': (row.get('estado') or '').capitalize(), 'editable': False},
            }
        elif module == 'usuario':
            # Exclusivo del administrador — sin esto, cualquier usuario
            # logueado podía enumerar username + rol de cualquier cuenta
            # del sistema cambiando el id en la URL de este endpoint.
            if session.get('rol') != 'admin':
                return jsonify({'error': 'Acceso restringido solo para administradores.'}), 403
            cursor.execute("""
                SELECT u.*, r.nombre_rol,
                       COALESCE(
                           (SELECT p.numero_documento FROM paciente p
                             WHERE p.id_usuario = u.id_usuario LIMIT 1),
                           (SELECT m.numero_identidad FROM medico m
                             WHERE m.id_usuario = u.id_usuario LIMIT 1)
                       ) AS identificacion
                FROM usuario u
                INNER JOIN rol r ON u.id_rol = r.id_rol
                WHERE u.id_usuario = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            # Solo el administrador gestiona usuarios (CRUD, con baja lógica).
            es_admin = session.get('rol') == 'admin'
            # Mismos campos y en el mismo orden que la tabla de `usMC`.
            # El rol ya NO es editable: cambiarlo desde aquí dejaba la cuenta
            # incoherente con sus datos (p. ej. un paciente con ficha en
            # `paciente` pasaba a rol médico sin ficha en `medico`, o al revés).
            # El rol se define al crear la cuenta desde la pantalla que
            # corresponde: `addUS` (admin), `addPA` (paciente) o `addMED` (médico).
            fields = {
                'username': {'label': 'Usuario', 'value': row['username'], 'editable': es_admin, 'type': 'text'},
                'identificacion': {'label': 'Identificación', 'value': row.get('identificacion') or '',
                    'display': row.get('identificacion') or '—', 'editable': False},
                'password': {'label': 'Contraseña', 'value': '', 'display': '********', 'editable': False},
                'id_rol': {'label': 'Rol', 'value': row['id_rol'], 'display': row['nombre_rol'], 'editable': False},
                'estado': {'label': 'Estado', 'value': row.get('estado', ''),
                    'display': (row.get('estado') or '').capitalize(), 'editable': False},
            }
        else:
            return jsonify({'error': 'Módulo desconocido'}), 400
    finally:
        cursor.close()
    return jsonify({'fields': fields})


#MAIN
if __name__ == "__main__":
    app.run(debug=True)