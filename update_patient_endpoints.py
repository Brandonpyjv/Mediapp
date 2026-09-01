import re

with open('index.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace Spanish flash/error messages and add id_usuario logic

code = code.replace('El nombre es demasiado corto.', 'Name is too short.')

# Update addPA
old_addPA = '''
@app.route("/addPA", methods=["GET", "POST"])
@admin_required
def addPA():
    """Registra un nuevo paciente con validaciones de formato."""
    if request.method == "POST":
'''
new_addPA = '''
@app.route("/addPA", methods=["GET", "POST"])
@admin_required
def addPA():
    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, username FROM usuario")
    usuarios = cursor.fetchall()

    if request.method == "POST":
'''
code = code.replace(old_addPA.strip(), new_addPA.strip())

old_addPA_vars = '''        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()

        # --- VALIDACIONES ---'''
new_addPA_vars = '''        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()
        id_usuario = request.form.get('id_usuario', '')
        if not id_usuario: id_usuario = None

        # --- VALIDACIONES ---'''
code = code.replace(old_addPA_vars, new_addPA_vars)

old_addPA_render = '''        if error:
            # Retornamos los valores ingresados (v_...) para no vaciar el formulario
            return render_template("pacientes/addPA.html", 
                                error=error,
                                v_nombre=nombre, v_tipo_doc=tipo_doc,
                                v_num_doc=num_doc, v_fecha_nac=fecha_nac,
                                v_tel=tel, v_dir=dir, v_email=email)'''
new_addPA_render = '''        if error:
            return render_template("pacientes/addPA.html", 
                                error=error, usuarios=usuarios,
                                v_nombre=nombre, v_tipo_doc=tipo_doc,
                                v_num_doc=num_doc, v_fecha_nac=fecha_nac,
                                v_tel=tel, v_dir=dir, v_email=email, v_id_usuario=id_usuario)'''
code = code.replace(old_addPA_render, new_addPA_render)

old_addPA_insert = '''            sql = """
                INSERT INTO paciente 
                (nombre, tipo_documento, numero_documento, fecha_nacimiento, telefono, direccion, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email))'''
new_addPA_insert = '''            sql = """
                INSERT INTO paciente 
                (nombre, tipo_documento, numero_documento, fecha_nacimiento, telefono, direccion, email, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario))'''
code = code.replace(old_addPA_insert, new_addPA_insert)

old_addPA_return = '''    return render_template("pacientes/addPA.html")'''
new_addPA_return = '''    return render_template("pacientes/addPA.html", usuarios=usuarios)'''
code = code.replace(old_addPA_return, new_addPA_return)

# Update editPA
old_editPA = '''
@app.route("/editPA/<string:id>", methods=["GET", "POST"])
@admin_required
def editPA(id):
    """Actualiza la información de un paciente existente."""
    cursor = db.conexion.cursor(dictionary=True)

    if request.method == "POST":'''
new_editPA = '''
@app.route("/editPA/<string:id>", methods=["GET", "POST"])
@admin_required
def editPA(id):
    cursor = db.conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, username FROM usuario")
    usuarios = cursor.fetchall()

    if request.method == "POST":'''
code = code.replace(old_editPA.strip(), new_editPA.strip())

old_editPA_vars = '''        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()

        # Validations'''
new_editPA_vars = '''        dir = request.form.get('direccion', '').strip()
        email = request.form.get('email', '').strip()
        id_usuario = request.form.get('id_usuario', '')
        if not id_usuario: id_usuario = None

        # Validations'''
code = code.replace(old_editPA_vars, new_editPA_vars)

old_editPA_render = '''        if error:
            # En edición, pasamos los datos dentro de un objeto 'user' para el HTML
            return render_template("pacientes/editPA.html",
                                error=error,
                                user={
                                    "id_paciente": id, "nombre": nombre,
                                    "tipo_documento": tipo_doc, "numero_documento": num_doc,
                                    "fecha_nacimiento": fecha_nac, "telefono": tel,
                                    "direccion": dir, "email": email
                                })'''
new_editPA_render = '''        if error:
            return render_template("pacientes/editPA.html",
                                error=error, usuarios=usuarios,
                                user={
                                    "id_paciente": id, "nombre": nombre,
                                    "tipo_documento": tipo_doc, "numero_documento": num_doc,
                                    "fecha_nacimiento": fecha_nac, "telefono": tel,
                                    "direccion": dir, "email": email, "id_usuario": id_usuario
                                })'''
code = code.replace(old_editPA_render, new_editPA_render)

old_editPA_update = '''            sql = """
                UPDATE paciente 
                SET nombre=%s, tipo_documento=%s, numero_documento=%s, 
                    fecha_nacimiento=%s, telefono=%s, direccion=%s, email=%s
                WHERE id_paciente=%s
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id))'''
new_editPA_update = '''            sql = """
                UPDATE paciente 
                SET nombre=%s, tipo_documento=%s, numero_documento=%s, 
                    fecha_nacimiento=%s, telefono=%s, direccion=%s, email=%s, id_usuario=%s
                WHERE id_paciente=%s
            """
            cursor.execute(sql, (nombre, tipo_doc, num_doc, fecha_nac, tel, dir, email, id_usuario, id))'''
code = code.replace(old_editPA_update, new_editPA_update)

old_editPA_return = '''    return render_template("pacientes/editPA.html", user=paciente)'''
new_editPA_return = '''    return render_template("pacientes/editPA.html", user=paciente, usuarios=usuarios)'''
code = code.replace(old_editPA_return, new_editPA_return)

with open('index.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('Success')
