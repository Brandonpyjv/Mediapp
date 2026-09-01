from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from mysql.connector import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import date_validators as dv
from functools import wraps

app = Flask(__name__, template_folder="templates")
app.secret_key = "mediapp_secret_key"
app.static_folder = 'templates/static'

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
                flash("Your account has been deactivated. Please contact the administrator.", "danger")
        except Exception:
            pass

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
            flash("Access restricted to administrators only.", "danger")
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
            flash("Access restricted to doctors only.", "danger")
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
                return render_template("login.html", error="This account has been deactivated. Contact the administrator.")

            session['usuario'] = usuario['username']
            session['rol'] = usuario['rol_nombre']
            session['id_usuario'] = usuario['id_usuario']

            return redirect(url_for('menu'))
        else:
            return render_template("login.html", error="Invalid username or password")

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
            return render_template("register.html", error="All fields are required")

        if len(username) < 3 or len(password) < 4:
            return render_template("register.html", error="Username (min 3) or password (min 4) too short",
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
                return render_template("register.html", error="Username is already taken",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)

            # 2. Validar si el paciente ya existe (por numero_documento)
            cursor.execute("SELECT id_paciente FROM paciente WHERE numero_documento = %s", (num_doc,))
            if cursor.fetchone():
                return render_template("register.html", error="Document number is already registered",
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
            flash("Registration successful. You can now sign in.", "success")
            return redirect(url_for('login'))
            
        except IntegrityError as e:
            db.conexion.rollback()
            return render_template("register.html", error="A database error occurred. Ensure your data is correct.",
                                   v_nombre=nombre, v_tipo_doc=tipo_doc, v_num_doc=num_doc,
                                   v_fecha_nac=fecha_nac, v_tel=tel, v_dir=dir, v_email=email, v_user=username)
        except Exception as e:
            db.conexion.rollback()
            return render_template("register.html", error=f"Unexpected error: {e}",
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
        cursor.execute("""
            SELECT u.id_usuario, u.username, u.estado, r.nombre_rol
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
        id_rol = request.form.get('id_rol', 2) # Por defecto 2 (asumiendo 'user')

        if len(username) < 3 or len(password) < 4:
            return render_template("usuarios/addUS.html", error="Data is too short")

        hashed_pw = generate_password_hash(password)
        
        try:
            cursor = db.conexion.cursor()
            cursor.execute(
                "INSERT INTO usuario (username, password, id_rol) VALUES (%s, %s, %s)",
                (username, hashed_pw, id_rol)
            )
            db.conexion.commit()
            cursor.close()
            flash("User created successfully", "success")
            return redirect(url_for('usMC'))
        except Exception as e:
            return render_template("usuarios/addUS.html", error=f"Error: {e}")

    return render_template("usuarios/addUS.html")

@app.route("/editUS/<string:id>", methods=["GET", "POST"])
@admin_required
def editUS(id):
    cursor = db.conexion.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form['username']
        new_password = request.form['password']
        
        # If password is empty, don't update it
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            sql = "UPDATE usuario SET username=%s, password=%s WHERE id_usuario=%s"
            data = (username, hashed_pw, id)
        else:
            sql = "UPDATE usuario SET username=%s WHERE id_usuario=%s"
            data = (username, id)

        cursor.execute(sql, data)
        db.conexion.commit()
        cursor.close()
        flash("User updated successfully", "success")
        return redirect(url_for('usMC'))

    cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        flash("User not found", "danger")
        return redirect(url_for('usMC'))
        
    return render_template("usuarios/editUS.html", user=user)

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
        flash("User deactivated.", "success")
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
        flash("User reactivated.", "success")
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
        error = None
        if any(char.isdigit() for char in nombre):
            error = "Name cannot contain numbers."
        elif not num_id.isdigit() or len(num_id) < 5:
            error = "Invalid ID (numbers only, minimum 5 digits)."
        elif "@" not in email:
            error = "Invalid email format."
        elif not id_esp:
            error = "You must select a specialty."
        elif len(tel) != 10 or not tel.isdigit():
            error = "Phone number must be exactly 10 digits."
        elif len(username) < 3:
            error = "Username must be at least 3 characters long."
        elif len(password) < 4:
            error = "Password must be at least 4 characters long."

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
                                    error="Username is already taken.",
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
            flash("Doctor added successfully.", "success")
            return redirect(url_for('medMC'))
        except Exception as e:
            db.conexion.rollback()
            error = f"Database error: {e}"
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

        # Averiguamos si este médico ya tiene cuenta de acceso
        cursor.execute("SELECT id_usuario FROM medico WHERE id_medico = %s", (id,))
        current = cursor.fetchone()
        current_id_usuario = current['id_usuario'] if current else None

        # Validations
        error = None
        if any(char.isdigit() for char in nombre):
            error = "Name cannot contain numbers."
        elif len(tel) != 10:
            error = "Invalid phone number."
        elif current_id_usuario is None and not username:
            error = "This doctor has no login account yet. Provide a username and password to create one."
        elif current_id_usuario is None and len(password) < 4:
            error = "Password must be at least 4 characters long."
        elif username and len(username) < 3:
            error = "Username must be at least 3 characters long."
        elif password and len(password) < 4:
            error = "Password must be at least 4 characters long."

        user_ctx = {"id_medico": id, "nombre": nombre, "numero_identidad": num_id,
                    "telefono": tel, "email": email, "id_especialidad": id_esp,
                    "id_usuario": current_id_usuario, "username": username}

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
                                        error="Username is already taken.", user=user_ctx)
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
                                            error="Username is already taken.", user=user_ctx)
                    cursor.execute("UPDATE usuario SET username=%s WHERE id_usuario=%s",
                                (username, current_id_usuario))
                if password:
                    hashed_pw = generate_password_hash(password)
                    cursor.execute("UPDATE usuario SET password=%s WHERE id_usuario=%s",
                                (hashed_pw, current_id_usuario))

            sql = """UPDATE medico
                    SET nombre=%s, numero_identidad=%s, telefono=%s, email=%s, id_especialidad=%s, id_usuario=%s
                    WHERE id_medico=%s"""
            cursor.execute(sql, (nombre, num_id, tel, email, id_esp, id_usuario_final, id))
            db.conexion.commit()
            flash("Doctor updated successfully.", "success")
            return redirect(url_for('medMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Update error: {e}", "danger")
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
        flash("Doctor not found.", "warning")
        return redirect(url_for('medMC'))

    return render_template("medicos/editMED.html", user=medico, especialidades=especialidades)


@app.route("/deleteMED/<string:id>", methods=["POST"])
@admin_required
def deleteMED(id):
    """Deletes a doctor if there are no blocking records. Also
    deactivates the doctor's login account, if any: a 'usuario' row is
    never hard-deleted, and an orphaned active account with no matching
    doctor would still be able to sign in but couldn't access any
    doctor-only feature."""
    cursor = db.conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_usuario FROM medico WHERE id_medico = %s", (id,))
        row = cursor.fetchone()
        id_usuario = row['id_usuario'] if row else None

        cursor.execute("DELETE FROM medico WHERE id_medico = %s", (id,))
        if id_usuario:
            cursor.execute("UPDATE usuario SET estado='inactivo' WHERE id_usuario = %s", (id_usuario,))
        db.conexion.commit()
        flash("Doctor deleted successfully.", "success")
    except IntegrityError:
        db.conexion.rollback()
        flash("Cannot delete: The doctor has appointments or associated records.", "danger")
    finally:
        cursor.close()
    return redirect(url_for('medMC'))

# ===========================================================================
# MÓDULO: PACIENTES (CRUD COMPLETO)
# ===========================================================================

@app.route("/paMC")
@login_required
def paMC():
    """Lista todos los pacientes registrados o el paciente del usuario actual."""
    cursor = db.conexion.cursor(dictionary=True)
    if session.get('rol') == 'admin' or not _has_user_filter():
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
        error = None
        if len(nombre) < 3:
            error = "Name is too short."
        elif any(char.isdigit() for char in nombre):
            error = "Name cannot contain numbers."
        elif not tipo_doc:
            error = "You must select a document type."
        elif len(num_doc) < 5 or not num_doc.isdigit():
            error = "Invalid document number (minimum 5 digits)."
        elif len(tel) != 10 or not tel.isdigit():
            error = "Phone number must be exactly 10 digits."
        elif "@" not in email or "." not in email:
            error = "Invalid email format."
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
            sql = """
                INSERT INTO paciente 
                (nombre, tipo_documento, numero_documento, fecha_nacimiento, telefono, direccion, email, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario))
            db.conexion.commit()
            cursor.close()
            flash("Patient registered successfully.", "success")
            return redirect(url_for('paMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("pacientes/addPA.html", error=f"Database error: {e}")

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
        error = None
        if len(nombre) < 3: error = "Name is too short."
        elif len(tel) != 10: error = "Phone must be 10 digits."
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
            flash("Patient data updated.", "success")
            return redirect(url_for('paMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Update error: {e}", "danger")
            return redirect(url_for('paMC'))

    # GET: Obtener datos actuales del paciente
    cursor.execute("SELECT * FROM paciente WHERE id_paciente = %s", (id,))
    paciente = cursor.fetchone()
    cursor.close()

    if not paciente:
        flash("Patient not found.", "warning")
        return redirect(url_for('paMC'))

    return render_template("pacientes/editPA.html", user=paciente, usuarios=usuarios)


@app.route("/deletePA/<string:id>", methods=["POST"])
@admin_required
def deletePA(id):
    """Elimina un paciente, verificando que no tenga historial clínico previo."""
    cursor = db.conexion.cursor()
    try:
        cursor.execute("DELETE FROM paciente WHERE id_paciente = %s", (id,))
        db.conexion.commit()
        flash("Patient deleted successfully.", "success")
    except IntegrityError:
        # Triggered if patient is referenced in other tables
        flash("Cannot delete: The patient has associated medical records.", "danger")
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
            error = "Specialty name must be at least 4 characters long."
        elif any(char.isdigit() for char in nombre):
            error = "Specialty name cannot contain numbers."
        
        if error:
            return render_template("especialidad/addES.html", 
                                error=error, 
                                v_nombre=nombre, 
                                v_descripcion=descripcion)

        # --- INSERCIÓN EN BD ---
        try:
            cursor = db.conexion.cursor()
            sql = "INSERT INTO especialidad (nombre, descripcion) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, descripcion))
            db.conexion.commit()
            cursor.close()
            flash("Specialty created successfully.", "success")
            return redirect(url_for('esMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("especialidad/addES.html", error=f"Database error: {e}")

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
            error = "Name is too short."
        elif any(char.isdigit() for char in nombre):
            error = "Name cannot contain numbers."

        if error:
            return render_template("especialidad/editES.html", 
                                error=error, 
                                item={"id_especialidad": id, "nombre": nombre, "descripcion": descripcion})

        try:
            sql = "UPDATE especialidad SET nombre=%s, descripcion=%s WHERE id_especialidad=%s"
            cursor.execute(sql, (nombre, descripcion, id))
            db.conexion.commit()
            cursor.close()
            flash("Specialty updated successfully.", "success")
            return redirect(url_for('esMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Update error: {e}", "danger")
            return redirect(url_for('esMC'))

    # GET: Cargar datos de la especialidad
    cursor.execute("SELECT * FROM especialidad WHERE id_especialidad = %s", (id,))
    especialidad = cursor.fetchone()
    cursor.close()

    if not especialidad:
        flash("Specialty not found.", "warning")
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
        flash("Specialty deleted.", "success")
    except IntegrityError:
        # Occurs if doctors are linked to this specialty
        flash("Cannot delete: There are doctors registered under this specialty.", "danger")
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
        sql = """
            SELECT r.*, co.id_medico AS id_medico_consulta, m.nombre AS nombre_medicamento
            FROM receta r
            INNER JOIN medicamento m ON r.id_medicamento = m.id_medicamento
            INNER JOIN consulta co ON r.id_consulta = co.id_consulta
            ORDER BY r.id_receta DESC
        """
        cursor.execute(sql)
    else:
        sql = """
            SELECT r.*, co.id_medico AS id_medico_consulta, m.nombre AS nombre_medicamento
            FROM receta r
            INNER JOIN medicamento m ON r.id_medicamento = m.id_medicamento
            INNER JOIN consulta co ON r.id_consulta = co.id_consulta
            INNER JOIN paciente p ON co.id_paciente = p.id_paciente
            WHERE p.id_usuario = %s
            ORDER BY r.id_receta DESC
        """
        cursor.execute(sql, (session.get('id_usuario'),))
    data = cursor.fetchall()
    cursor.close()
    return render_template("recetas/reMC.html", data=data, current_medico_id=current_medico_id)


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
    cursor.execute("SELECT id_medicamento, nombre FROM medicamento")
    medicamentos = cursor.fetchall()

    if request.method == "POST":
        id_consulta = request.form.get('id_consulta')
        id_medicamento = request.form.get('id_medicamento')
        cantidad = request.form.get('cantidad')
        indicaciones = request.form.get('indicaciones', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_consulta or not id_medicamento:
            error = "You must select a consultation and a medication."
        elif not cantidad or int(cantidad) < 1:
            error = "You must enter a valid quantity."
        elif not any(str(c['id_consulta']) == str(id_consulta) for c in consultas):
            # Defensa extra: el id_consulta debe ser una de sus propias consultas.
            error = "You can only prescribe on your own consultations."

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
            flash("Prescription created successfully.", "success")
            return redirect(url_for('reMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Save error: {e}", "danger")
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
        SELECT r.*, co.id_medico AS id_medico_consulta
        FROM receta r INNER JOIN consulta co ON r.id_consulta = co.id_consulta
        WHERE r.id_receta = %s
    """, (id,))
    receta = cursor.fetchone()

    if not receta:
        cursor.close()
        flash("Prescription not found.", "warning")
        return redirect(url_for('reMC'))

    if receta['id_medico_consulta'] != id_medico:
        cursor.close()
        flash("You can only edit prescriptions you created yourself.", "danger")
        return redirect(url_for('reMC'))

    cursor.execute("""
        SELECT co.id_consulta, co.fecha, p.nombre AS nombre_paciente
        FROM consulta co INNER JOIN paciente p ON co.id_paciente = p.id_paciente
        WHERE co.id_medico = %s ORDER BY co.fecha DESC
    """, (id_medico,))
    consultas = cursor.fetchall()
    cursor.execute("SELECT id_medicamento, nombre FROM medicamento")
    medicamentos = cursor.fetchall()

    if request.method == "POST":
        id_consulta = request.form.get('id_consulta')
        id_medicamento = request.form.get('id_medicamento')
        cantidad = request.form.get('cantidad')
        indicaciones = request.form.get('indicaciones', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_consulta or not id_medicamento:
            error = "You must select a consultation and a medication."
        elif not cantidad or int(cantidad) < 1:
            error = "You must enter a valid quantity."
        elif not any(str(c['id_consulta']) == str(id_consulta) for c in consultas):
            error = "You can only prescribe on your own consultations."

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
            flash("Prescription updated successfully.", "success")
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
        flash("Prescription not found.", "warning")
        return redirect(url_for('reMC'))
    if row[0] != id_medico:
        cursor.close()
        flash("You can only delete prescriptions you created yourself.", "danger")
        return redirect(url_for('reMC'))
    try:
        cursor.execute("DELETE FROM receta WHERE id_receta = %s", (id,))
        db.conexion.commit()
        flash("Prescription deleted.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Could not delete: {e}", "danger")
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
            error = "Medication name is too short."
        elif not dosis:
            error = "Dosage details are required."

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
                                    error=f"Medication '{nombre}' already exists.", 
                                    v_nombre=nombre, v_desc=descripcion, v_dosis=dosis)
            
            sql = "INSERT INTO medicamento (nombre, descripcion, dosis) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, descripcion, dosis))
            db.conexion.commit()
            cursor.close()
            return redirect(url_for('meMC'))
            
        except Exception as e:
            db.conexion.rollback()
            return render_template("medicamentos/addME.html", error=f"Database error: {e}")

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
            error = "Invalid name."
        elif not dosis:
            error = "Dosage is required."

        if error:
            return render_template("medicamentos/editME.html", 
                                medicamento=medicamento,
                                error=error)

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
                                error=f"Database error: {e}")

    cursor.close()
    return render_template("medicamentos/editME.html", medicamento=medicamento)

@app.route("/deleteME/<string:id>", methods=["POST"])
@admin_required
def deleteME(id):
    cursor = db.conexion.cursor()
    try:
        sql = "DELETE FROM medicamento WHERE id_medicamento = %s"
        cursor.execute(sql, (id,))
        db.conexion.commit()
    except Exception as e:
        db.conexion.rollback()
        # Puedes añadir un mensaje flash aquí si falla por integridad
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
        return (f"The doctor already has an appointment within {MINUTOS_ENTRE_CITAS} minutes "
                "of that time. Please choose a different time.")

    return None

# Permisos: el Administrador gestiona todas las citas (CRUD completo,
# ver addCI/editCI/deleteCI). El Médico solo lee su propia agenda — no
# puede modificarla (audio del autor, 2026-08-31). El Paciente solo ve
# las suyas.
@app.route("/ciMC", methods=["GET"])
@login_required
def ciMC():
    insertObject = []
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
            cursor.execute(base_sql + " ORDER BY c.fecha DESC")
        elif rol == 'medico':
            cursor.execute(base_sql + " WHERE c.id_medico = %s ORDER BY c.fecha DESC",
                        (_current_medico_id(),))
        else:
            cursor.execute(base_sql + " WHERE p.id_usuario = %s ORDER BY c.fecha DESC",
                        (session.get('id_usuario'),))
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("citas/ciMC.html", data=insertObject)

@app.route("/addCI", methods=["GET", "POST"])
@admin_required
def addCI():
    cursor = db.conexion.cursor(dictionary=True)
    
    # Cargamos las listas para los Selects del formulario
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT id_medico, nombre FROM medico")
    medicos = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        id_med = request.form.get('id_medico')
        fecha = request.form.get('fecha')
        motivo = request.form.get('motivo', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac or not id_med:
            error = "Please select a patient and a doctor."
        elif not fecha:
            error = "Appointment date and time are required."
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
            flash("Appointment scheduled successfully.", "success")
            return redirect(url_for('ciMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("citas/addCI.html", 
                                pacientes=pacientes, medicos=medicos,
                                error=f"Database error: {e}")
        finally:
            cursor.close()

    return render_template("citas/addCI.html", pacientes=pacientes, medicos=medicos)

@app.route("/editCI/<string:id>", methods=["GET", "POST"])
@admin_required
def editCI(id):
    cursor = db.conexion.cursor(dictionary=True)

    # Cargamos pacientes y médicos para que el usuario pueda reasignar la cita
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT id_medico, nombre FROM medico")
    medicos = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        id_med = request.form.get('id_medico')
        fecha = request.form.get('fecha')
        motivo = request.form.get('motivo', '').strip()

        error = None
        if not id_pac or not id_med:
            error = "You must select a patient and a doctor."
        elif not fecha:
            error = "Date is required."
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
                                    "motivo": motivo
                                })

        try:
            sql = """
                UPDATE cita 
                SET id_paciente=%s, id_medico=%s, fecha=%s, motivo=%s
                WHERE id_cita=%s
            """
            cursor.execute(sql, (id_pac, id_med, fecha, motivo, id))
            db.conexion.commit()
            flash("Appointment updated successfully.", "success")
            return redirect(url_for('ciMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template("citas/editCI.html",
                                pacientes=pacientes, medicos=medicos,
                                error=f"Update error: {e}")
        finally:
            cursor.close()

    # GET: Obtener los datos actuales de la cita
    cursor.execute("SELECT * FROM cita WHERE id_cita = %s", (id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("Appointment does not exist.", "warning")
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
        flash("Appointment deleted successfully.", "success")
    except IntegrityError:
        db.conexion.rollback()
        flash("Cannot delete: This appointment already has an associated clinical consultation.", "danger")
    except Exception as e:
        db.conexion.rollback()
        flash(f"An unexpected error occurred: {e}", "danger")
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
        flash("Only patients can cancel their own appointments.", "danger")
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
            flash("Appointment not found.", "warning")
        elif cita['estado'] == 'cancelada':
            flash("This appointment is already cancelled.", "warning")
        elif cita['fecha'].date() < dv.today_colombia():
            flash("Past appointments can't be cancelled.", "danger")
        else:
            cursor.execute("UPDATE cita SET estado='cancelada' WHERE id_cita = %s", (id,))
            db.conexion.commit()
            flash("Appointment cancelled successfully.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error cancelling appointment: {e}", "danger")
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
    cursor.execute("SELECT id_medico, nombre FROM medico")
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
            cursor.execute(sql)
        else:
            sql = """
                SELECT co.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
                FROM consulta co
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                WHERE p.id_usuario = %s
                ORDER BY co.fecha DESC
            """
            cursor.execute(sql, (session.get('id_usuario'),))
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("consultas/coMC.html", data=insertObject, current_medico_id=current_medico_id)

@app.route("/addCO", methods=["GET", "POST"])
@medico_required
def addconsultas():
    """Registra una consulta (diagnóstico y tratamiento). Permiso
    exclusivo del Médico (CLAUDE.md §2 / D6): el médico autor se toma
    siempre de la sesión, nunca del formulario."""
    cursor = db.conexion.cursor(dictionary=True)
    id_medico = _current_medico_id()

    # Cargar la lista de pacientes para el selector del formulario
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        tratamiento = request.form.get('tratamiento', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac:
            error = "Please select a patient."
        elif not fecha:
            error = "Consultation date and time are required."
        elif not tratamiento:
            error = "Treatment cannot be empty."
        elif not diagnostico:
            error = "Diagnosis cannot be empty."

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
            flash("Consultation registered successfully.", "success")
            return redirect(url_for('coMC'))
        except Exception as e:
            db.conexion.rollback()
            return render_template(
                "consultas/addCO.html",
                pacientes=pacientes,
                error=f"Database error: {e}"
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

    cursor.execute("SELECT * FROM consulta WHERE id_consulta = %s", (id,))
    consulta = cursor.fetchone()

    if not consulta:
        cursor.close()
        flash("Consultation record not found.", "warning")
        return redirect(url_for('coMC'))

    if consulta['id_medico'] != current_medico_id:
        cursor.close()
        flash("You can only edit consultations you created yourself.", "danger")
        return redirect(url_for('coMC'))

    cursor.execute("SELECT id_paciente, nombre FROM paciente")
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_pac = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        tratamiento = request.form.get('tratamiento', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_pac:
            error = "You must select a patient."
        elif not fecha:
            error = "Date is required."
        elif not tratamiento:
            error = "Treatment is required."
        elif not diagnostico:
            error = "Diagnosis is required."

        if error:
            cursor.close()
            return render_template("consultas/editCO.html",
                                pacientes=pacientes,
                                error=error,
                                user={
                                    "id_consulta": id,
                                    "id_paciente": id_pac,
                                    "id_medico": current_medico_id,
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
            flash("Consultation updated successfully.", "success")
            return redirect(url_for('coMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Update error: {e}", "danger")
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
        flash("Consultation record not found.", "warning")
        return redirect(url_for('coMC'))
    if row[0] != current_medico_id:
        cursor.close()
        flash("You can only delete consultations you created yourself.", "danger")
        return redirect(url_for('coMC'))
    try:
        sql = "DELETE FROM consulta WHERE id_consulta = %s"
        cursor.execute(sql, (id,))
        db.conexion.commit()
        flash("Consultation record deleted.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Could not delete record: {e}", "danger")
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
            cursor.execute(sql)
        else:
            sql = """
                SELECT h.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM historia h
                INNER JOIN paciente p ON h.id_paciente = p.id_paciente
                INNER JOIN medico m ON h.id_medico = m.id_medico
                WHERE p.id_usuario = %s
                ORDER BY h.fecha DESC
            """
            cursor.execute(sql, (session.get('id_usuario'),))
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("historias/hiMC.html", data=insertObject, current_medico_id=current_medico_id)

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
            error = "Please select a patient."
        elif not fecha:
            error = "Date is required."
        elif not descripcion:
            error = "Description cannot be empty."
        else:
            fecha_valida, fecha_error = dv.validate_clinical_record_datetime(fecha)
            if not fecha_valida:
                error = fecha_error

        if error:
            # Recargamos la lista para el selector en caso de error
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
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
            flash("Medical history record added.", "success")
            return redirect(url_for('hiMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Save error: {e}", "danger")
            return redirect(url_for('hiMC'))
        finally:
            cursor.close()

    # GET: cargamos pacientes para el selector (el médico ya es el de sesión)
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
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

    cursor.execute("SELECT * FROM historia WHERE id_historia = %s", (id,))
    historia = cursor.fetchone()

    if not historia:
        cursor.close()
        flash("Record not found.", "warning")
        return redirect(url_for('hiMC'))

    if historia['id_medico'] != current_medico_id:
        cursor.close()
        flash("You can only edit clinical records you created yourself.", "danger")
        return redirect(url_for('hiMC'))

    # Cargamos el catálogo de pacientes para el select
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
    pacientes = cursor.fetchall()

    if request.method == "POST":
        id_paciente = request.form.get('id_paciente')
        fecha = request.form.get('fecha')
        descripcion = request.form.get('descripcion', '').strip()
        notas = request.form.get('notas', '').strip()

        # --- VALIDATIONS ---
        error = None
        if not id_paciente:
            error = "You must select a patient."
        elif not fecha:
            error = "Date is required."
        elif not descripcion:
            error = "Description cannot be empty."
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
            flash("Medical history updated successfully.", "success")
            return redirect(url_for('hiMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Database error: {e}", "danger")
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
            flash("Record not found.", "warning")
        elif row[0] != current_medico_id:
            flash("You can only delete clinical records you created yourself.", "danger")
        else:
            cursor.execute("DELETE FROM historia WHERE id_historia = %s", (id,))
            db.conexion.commit()
            flash("Medical history deleted successfully.", "success")
    except IntegrityError:
        db.conexion.rollback()
        flash("Cannot delete: This history record is linked to other clinical data.", "danger")
    except Exception as e:
        db.conexion.rollback()
        flash(f"An unexpected error occurred: {e}", "danger")
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
            cursor.execute(sql)
        else:
            sql = """
                SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM examen e
                INNER JOIN paciente p ON e.id_paciente = p.id_paciente
                INNER JOIN medico m ON e.id_medico = m.id_medico
                WHERE p.id_usuario = %s
                ORDER BY e.fecha_solicitud DESC
            """
            cursor.execute(sql, (session.get('id_usuario'),))
        myresult = cursor.fetchall()
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
    return render_template("examenes/exMC.html", data=insertObject, current_medico_id=current_medico_id)

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
            error = "Please select a patient."
        elif not tipo_examen:
            error = "Test type is required."
        elif not fecha_solicitud:
            error = "Request date is required."

        if error:
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
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
            flash("Lab test requested successfully.", "success")
            return redirect(url_for('exMC'))
        except Exception as e:
            db.conexion.rollback()
            flash(f"Error registering lab test: {e}", "danger")
            return redirect(url_for('exMC'))
        finally:
            cursor.close()

    # GET: cargamos pacientes para el selector (el médico ya es el de sesión)
    cursor.execute("SELECT id_paciente, nombre FROM paciente")
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
        flash("Access restricted to doctors and administrators.", "danger")
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
        flash("Lab test not found.", "warning")
        return redirect(url_for('exMC'))

    es_medico = (rol == 'medico')
    if es_medico and examen['id_medico'] != _current_medico_id():
        cursor.close()
        flash("You can only edit lab tests you requested yourself.", "danger")
        return redirect(url_for('exMC'))

    pacientes = []
    if es_medico:
        cursor.execute("SELECT id_paciente, nombre FROM paciente")
        pacientes = cursor.fetchall()

    if request.method == "POST":
        if es_medico:
            id_paciente = request.form.get('id_paciente')
            tipo_examen = request.form.get('tipo_examen', '').strip()
            fecha_solicitud = request.form.get('fecha_solicitud')

            error = None
            if not id_paciente:
                error = "You must select a patient."
            elif not tipo_examen:
                error = "Test type is required."
            elif not fecha_solicitud:
                error = "Request date is required."

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
                flash("Lab test request updated successfully.", "success")
                return redirect(url_for('exMC'))
            except Exception as e:
                db.conexion.rollback()
                flash(f"Database error: {e}", "danger")
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
                flash("Lab result saved successfully.", "success")
                return redirect(url_for('exMC'))
            except Exception as e:
                db.conexion.rollback()
                flash(f"Database error: {e}", "danger")
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
        flash("Lab test deleted successfully.", "success")
    except Exception as e:
        db.conexion.rollback()
        flash(f"Error deleting lab test: {e}", "danger")
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
                SELECT c.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
                FROM cita c
                INNER JOIN medico m ON c.id_medico = m.id_medico
                INNER JOIN paciente p ON c.id_paciente = p.id_paciente
                WHERE c.id_cita = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
            pacs = cursor.fetchall()
            cursor.execute("SELECT id_medico, nombre FROM medico")
            meds = cursor.fetchall()
            fields = {
                'id_paciente': {'label': 'Patient', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': True, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Doctor', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': True, 'type': 'select',
                    'options': [{'value': m['id_medico'], 'label': m['nombre']} for m in meds]},
                'fecha': {'label': 'Date & Time', 'value': str(row['fecha']), 'editable': True, 'type': 'datetime-local'},
                'motivo': {'label': 'Reason', 'value': row.get('motivo', ''), 'editable': True, 'type': 'textarea'},
                'estado': {'label': 'Status', 'value': row.get('estado', ''), 'display': row.get('estado', '').capitalize(), 'editable': False},
            }
        elif module == 'consulta':
            cursor.execute("""
                SELECT co.*, m.nombre AS nombre_medico, p.nombre AS nombre_paciente
                FROM consulta co
                INNER JOIN medico m ON co.id_medico = m.id_medico
                INNER JOIN paciente p ON co.id_paciente = p.id_paciente
                WHERE co.id_consulta = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
            pacs = cursor.fetchall()
            # Solo el médico autor puede editar su propia consulta (D6, mismo
            # criterio que historia). El administrador tiene solo lectura.
            puede_editar = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            fields = {
                'id_paciente': {'label': 'Patient', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Doctor', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'fecha': {'label': 'Date', 'value': str(row['fecha']), 'editable': puede_editar, 'type': 'datetime-local'},
                'diagnostico': {'label': 'Diagnosis', 'value': row.get('diagnostico', ''), 'editable': puede_editar, 'type': 'textarea'},
                'tratamiento': {'label': 'Treatment', 'value': row.get('tratamiento', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'historia':
            cursor.execute("""
                SELECT h.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM historia h
                INNER JOIN paciente p ON h.id_paciente = p.id_paciente
                INNER JOIN medico m ON h.id_medico = m.id_medico
                WHERE h.id_historia = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
            pacs = cursor.fetchall()
            # Solo el médico autor puede editar su propia historia clínica
            # (ni otro médico ni el administrador). El campo 'id_medico'
            # nunca es editable: la autoría no se reasigna.
            puede_editar = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            fields = {
                'id_paciente': {'label': 'Patient', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Doctor', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'fecha': {'label': 'Date', 'value': str(row['fecha']), 'editable': puede_editar, 'type': 'date'},
                'descripcion': {'label': 'Description', 'value': row.get('descripcion', ''), 'editable': puede_editar, 'type': 'textarea'},
                'notas': {'label': 'Notes', 'value': row.get('notas', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'examen':
            cursor.execute("""
                SELECT e.*, p.nombre AS nombre_paciente, m.nombre AS nombre_medico
                FROM examen e
                INNER JOIN paciente p ON e.id_paciente = p.id_paciente
                INNER JOIN medico m ON e.id_medico = m.id_medico
                WHERE e.id_examen = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT id_paciente, nombre FROM paciente")
            pacs = cursor.fetchall()
            # Permisos divididos por campo (D7): el médico solicitante
            # edita la solicitud; el administrador carga el resultado.
            es_medico_propio = (session.get('rol') == 'medico' and row['id_medico'] == _current_medico_id())
            es_admin = session.get('rol') == 'admin'
            fields = {
                'id_paciente': {'label': 'Patient', 'value': row['id_paciente'], 'display': row['nombre_paciente'], 'editable': es_medico_propio, 'type': 'select',
                    'options': [{'value': p['id_paciente'], 'label': p['nombre']} for p in pacs]},
                'id_medico': {'label': 'Doctor', 'value': row['id_medico'], 'display': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'tipo_examen': {'label': 'Test Type', 'value': row.get('tipo_examen', ''), 'editable': es_medico_propio, 'type': 'text'},
                'fecha_solicitud': {'label': 'Request Date', 'value': str(row.get('fecha_solicitud', '')), 'editable': es_medico_propio, 'type': 'date'},
                'fecha_resultado': {'label': 'Result Date', 'value': str(row.get('fecha_resultado', '') or ''), 'editable': es_admin, 'type': 'date'},
                'resultado': {'label': 'Result', 'value': row.get('resultado', ''), 'editable': es_admin, 'type': 'textarea'},
            }
        elif module == 'receta':
            cursor.execute("""
                SELECT r.*, co.id_medico AS id_medico_consulta,
                       p.nombre AS nombre_paciente, m.nombre AS nombre_medico, med.nombre AS nombre_medicamento
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
            cursor.execute("SELECT id_medicamento, nombre FROM medicamento")
            meds = cursor.fetchall()
            fields = {
                'id_consulta': {'label': 'Consultation', 'value': row['id_consulta'],
                    'display': f"#{row['id_consulta']} — {row['nombre_paciente']}", 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': c['id_consulta'], 'label': f"#{c['id_consulta']} — {c['nombre_paciente']} — {c['fecha']}"} for c in cons]},
                'id_medicamento': {'label': 'Medication', 'value': row['id_medicamento'], 'display': row['nombre_medicamento'], 'editable': puede_editar, 'type': 'select',
                    'options': [{'value': m['id_medicamento'], 'label': m['nombre']} for m in meds]},
                'patient': {'label': 'Patient', 'value': row['nombre_paciente'], 'editable': False},
                'doctor': {'label': 'Doctor', 'value': 'Dr. ' + row['nombre_medico'], 'editable': False},
                'cantidad': {'label': 'Quantity', 'value': row.get('cantidad', ''), 'editable': puede_editar, 'type': 'number'},
                'indicaciones': {'label': 'Instructions', 'value': row.get('indicaciones', ''), 'editable': puede_editar, 'type': 'textarea'},
            }
        elif module == 'medico':
            cursor.execute("""
                SELECT medico.*, especialidad.nombre AS nombre_es
                FROM medico
                INNER JOIN especialidad ON medico.id_especialidad = especialidad.id_especialidad
                WHERE id_medico = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT * FROM especialidad")
            esps = cursor.fetchall()
            fields = {
                'nombre': {'label': 'Full Name', 'value': row['nombre'], 'editable': True, 'type': 'text'},
                'numero_identidad': {'label': 'Identity Number', 'value': row['numero_identidad'], 'editable': True, 'type': 'text'},
                'telefono': {'label': 'Phone', 'value': row['telefono'], 'editable': True, 'type': 'text'},
                'email': {'label': 'Email', 'value': row['email'], 'editable': True, 'type': 'email'},
                'id_especialidad': {'label': 'Specialty', 'value': row['id_especialidad'], 'display': row['nombre_es'], 'editable': True, 'type': 'select',
                    'options': [{'value': e['id_especialidad'], 'label': e['nombre']} for e in esps]},
            }
        elif module == 'paciente':
            cursor.execute("SELECT p.*, u.username FROM paciente p LEFT JOIN usuario u ON p.id_usuario = u.id_usuario WHERE p.id_paciente = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT id_usuario, username FROM usuario")
            users = cursor.fetchall()
            user_options = [{'value': '', 'label': '-- No User Linked --'}] + [{'value': u['id_usuario'], 'label': u['username']} for u in users]
            fields = {
                'nombre': {'label': 'Full Name', 'value': row['nombre'], 'editable': True, 'type': 'text'},
                'tipo_documento': {'label': 'Document Type', 'value': row.get('tipo_documento', ''), 'editable': True, 'type': 'text'},
                'numero_documento': {'label': 'Document Number', 'value': row.get('numero_documento', ''), 'editable': True, 'type': 'text'},
                'fecha_nacimiento': {'label': 'Birth Date', 'value': str(row.get('fecha_nacimiento', '')), 'editable': True, 'type': 'date'},
                'telefono': {'label': 'Phone', 'value': row.get('telefono', ''), 'editable': True, 'type': 'text'},
                'direccion': {'label': 'Address', 'value': row.get('direccion', ''), 'editable': True, 'type': 'text'},
                'email': {'label': 'Email', 'value': row.get('email', ''), 'editable': True, 'type': 'email'},
                'id_usuario': {'label': 'Linked User', 'value': row.get('id_usuario', ''), 'display': row.get('username') or 'None', 'editable': True, 'type': 'select', 'options': user_options},
            }
        elif module == 'especialidad':
            cursor.execute("SELECT * FROM especialidad WHERE id_especialidad = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            fields = {
                'nombre': {'label': 'Specialty Name', 'value': row['nombre'], 'editable': True, 'type': 'text'},
                'descripcion': {'label': 'Description', 'value': row.get('descripcion', ''), 'editable': True, 'type': 'textarea'},
            }
        elif module == 'medicamento':
            cursor.execute("SELECT * FROM medicamento WHERE id_medicamento = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            fields = {
                'nombre': {'label': 'Medication Name', 'value': row['nombre'], 'editable': True, 'type': 'text'},
                'descripcion': {'label': 'Description', 'value': row.get('descripcion', ''), 'editable': True, 'type': 'textarea'},
                'dosis': {'label': 'Dosage', 'value': row.get('dosis', ''), 'editable': True, 'type': 'text'},
            }
        elif module == 'usuario':
            cursor.execute("""
                SELECT u.*, r.nombre_rol FROM usuario u
                INNER JOIN rol r ON u.id_rol = r.id_rol
                WHERE u.id_usuario = %s
            """, (id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Not found'}), 404
            cursor.execute("SELECT * FROM rol")
            roles = cursor.fetchall()
            fields = {
                'username': {'label': 'Username', 'value': row['username'], 'editable': True, 'type': 'text'},
                'id_rol': {'label': 'Role', 'value': row['id_rol'], 'display': row['nombre_rol'], 'editable': True, 'type': 'select',
                    'options': [{'value': r['id_rol'], 'label': r['nombre_rol']} for r in roles]},
            }
        else:
            return jsonify({'error': 'Unknown module'}), 400
    finally:
        cursor.close()
    return jsonify({'fields': fields})


# ===========================================================================
# API: SAVE (Admin inline edit from modal)
# ===========================================================================
@app.route("/api/save/<module>/<string:id>", methods=["POST"])
@login_required
def api_save(module, id):
    # La mayoría de los módulos de este endpoint son de uso exclusivo del
    # Administrador. 'historia' es exclusiva del Médico (y solo sus propios
    # registros). 'examen' es compartida: el Médico corrige la solicitud
    # (y solo la suya), el Administrador carga el resultado. 'historia',
    # 'consulta' y 'receta' son exclusivas del Médico (y solo sus propios
    # registros) — el Administrador tiene acceso de solo lectura a las tres.
    # La comprobación de autoría/campo se hace más abajo, en cada rama.
    if module in ('historia', 'consulta', 'receta'):
        if session.get('rol') != 'medico':
            return jsonify({'success': False, 'error': 'Access restricted to doctors only.'})
    elif module == 'examen':
        if session.get('rol') not in ('medico', 'admin'):
            return jsonify({'success': False, 'error': 'Access restricted to doctors and administrators.'})
    elif session.get('rol') != 'admin':
        return jsonify({'success': False, 'error': 'Access restricted to administrators only.'})

    cursor = db.conexion.cursor()
    try:
        if module == 'cita':
            fecha_valida, fecha_error = dv.validate_appointment_datetime(request.form.get('fecha'))
            if not fecha_valida:
                return jsonify({'success': False, 'error': fecha_error})
            conflict_error = _check_appointment_conflicts(
                cursor, request.form['id_paciente'], request.form['id_medico'],
                request.form['fecha'], exclude_id=id
            )
            if conflict_error:
                return jsonify({'success': False, 'error': conflict_error})
            sql = "UPDATE cita SET id_paciente=%s, id_medico=%s, fecha=%s, motivo=%s WHERE id_cita=%s"
            cursor.execute(sql, (request.form['id_paciente'], request.form['id_medico'], request.form['fecha'], request.form['motivo'], id))
        elif module == 'consulta':
            current_medico_id = _current_medico_id()
            cursor.execute("SELECT id_medico FROM consulta WHERE id_consulta = %s", (id,))
            owner = cursor.fetchone()
            if not owner or owner[0] != current_medico_id:
                return jsonify({'success': False, 'error': 'You can only edit consultations you created yourself.'})
            # id_medico nunca se toma del formulario: la autoría no se reasigna.
            sql = "UPDATE consulta SET id_paciente=%s, fecha=%s, diagnostico=%s, tratamiento=%s WHERE id_consulta=%s AND id_medico=%s"
            cursor.execute(sql, (request.form['id_paciente'], request.form['fecha'], request.form['diagnostico'], request.form['tratamiento'], id, current_medico_id))
        elif module == 'historia':
            current_medico_id = _current_medico_id()
            cursor.execute("SELECT id_medico FROM historia WHERE id_historia = %s", (id,))
            owner = cursor.fetchone()
            if not owner or owner[0] != current_medico_id:
                return jsonify({'success': False, 'error': 'You can only edit clinical records you created yourself.'})
            fecha_valida, fecha_error = dv.validate_clinical_record_datetime(request.form.get('fecha'))
            if not fecha_valida:
                return jsonify({'success': False, 'error': fecha_error})
            # id_medico nunca se toma del formulario: la autoría no se reasigna.
            sql = "UPDATE historia SET id_paciente=%s, fecha=%s, descripcion=%s, notas=%s WHERE id_historia=%s AND id_medico=%s"
            cursor.execute(sql, (request.form['id_paciente'], request.form['fecha'], request.form['descripcion'], request.form['notas'], id, current_medico_id))
        elif module == 'examen':
            # Permisos divididos por campo (D7): el Médico solicitante
            # corrige la solicitud; el Administrador (laboratorio) carga
            # el resultado. Ninguno puede tocar el campo del otro.
            if session.get('rol') == 'medico':
                current_medico_id = _current_medico_id()
                cursor.execute("SELECT id_medico FROM examen WHERE id_examen = %s", (id,))
                owner = cursor.fetchone()
                if not owner or owner[0] != current_medico_id:
                    return jsonify({'success': False, 'error': 'You can only edit lab tests you requested yourself.'})
                sql = "UPDATE examen SET id_paciente=%s, tipo_examen=%s, fecha_solicitud=%s WHERE id_examen=%s AND id_medico=%s"
                cursor.execute(sql, (request.form['id_paciente'], request.form['tipo_examen'], request.form['fecha_solicitud'], id, current_medico_id))
            else:
                sql = "UPDATE examen SET fecha_resultado=%s, resultado=%s WHERE id_examen=%s"
                cursor.execute(sql, (request.form.get('fecha_resultado') or None, request.form.get('resultado', ''), id))
        elif module == 'receta':
            # La receta no tiene id_medico propio: su dueño es el médico de
            # la consulta a la que pertenece.
            current_medico_id = _current_medico_id()
            cursor.execute("""
                SELECT co.id_medico FROM receta r
                INNER JOIN consulta co ON r.id_consulta = co.id_consulta
                WHERE r.id_receta = %s
            """, (id,))
            owner = cursor.fetchone()
            if not owner or owner[0] != current_medico_id:
                return jsonify({'success': False, 'error': 'You can only edit prescriptions you created yourself.'})
            # Si se reasigna a otra consulta, esa consulta también debe ser suya.
            cursor.execute("SELECT id_medico FROM consulta WHERE id_consulta = %s", (request.form.get('id_consulta'),))
            nueva = cursor.fetchone()
            if not nueva or nueva[0] != current_medico_id:
                return jsonify({'success': False, 'error': 'You can only attach prescriptions to your own consultations.'})
            if not request.form.get('cantidad') or int(request.form['cantidad']) < 1:
                return jsonify({'success': False, 'error': 'Quantity must be at least 1.'})
            sql = "UPDATE receta SET id_consulta=%s, id_medicamento=%s, cantidad=%s, indicaciones=%s WHERE id_receta=%s"
            cursor.execute(sql, (request.form['id_consulta'], request.form['id_medicamento'], request.form['cantidad'], request.form['indicaciones'], id))
        elif module == 'medico':
            sql = "UPDATE medico SET nombre=%s, numero_identidad=%s, telefono=%s, email=%s, id_especialidad=%s WHERE id_medico=%s"
            cursor.execute(sql, (request.form['nombre'], request.form['numero_identidad'], request.form['telefono'], request.form['email'], request.form['id_especialidad'], id))
        elif module == 'paciente':
            id_usuario_val = request.form.get('id_usuario')
            if not id_usuario_val:
                id_usuario_val = None
            fecha_nac_val = request.form.get('fecha_nacimiento')
            if fecha_nac_val:
                # Solo se valida si se envió una fecha (consistente con editPA)
                fecha_valida, fecha_error = dv.validate_birthdate(fecha_nac_val)
                if not fecha_valida:
                    return jsonify({'success': False, 'error': fecha_error})
            sql = "UPDATE paciente SET nombre=%s, tipo_documento=%s, numero_documento=%s, fecha_nacimiento=%s, telefono=%s, direccion=%s, email=%s, id_usuario=%s WHERE id_paciente=%s"
            cursor.execute(sql, (request.form['nombre'], request.form['tipo_documento'], request.form['numero_documento'], request.form['fecha_nacimiento'], request.form['telefono'], request.form['direccion'], request.form['email'], id_usuario_val, id))
        elif module == 'especialidad':
            sql = "UPDATE especialidad SET nombre=%s, descripcion=%s WHERE id_especialidad=%s"
            cursor.execute(sql, (request.form['nombre'], request.form['descripcion'], id))
        elif module == 'medicamento':
            sql = "UPDATE medicamento SET nombre=%s, descripcion=%s, dosis=%s WHERE id_medicamento=%s"
            cursor.execute(sql, (request.form['nombre'], request.form['descripcion'], request.form['dosis'], id))
        elif module == 'usuario':
            sql = "UPDATE usuario SET username=%s, id_rol=%s WHERE id_usuario=%s"
            cursor.execute(sql, (request.form['username'], request.form['id_rol'], id))
        else:
            return jsonify({'success': False, 'error': 'Unknown module'})
        db.conexion.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.conexion.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

#MAIN
if __name__ == "__main__":
    app.run(debug=True)