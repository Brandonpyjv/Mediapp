# -*- coding: utf-8 -*-
"""Autenticación, redirección por rol y tratamiento de contraseñas.

Cubre el flujo que la videollamada del 2026-08-31 pidió explícitamente (entrar y
caer en el tablero del rol, sin elegirlo a mano) y la decisión **D2**, que hay que
poder sostener por escrito ante el evaluador: las contraseñas se guardan con
`scrypt` a través de `werkzeug.security`, nunca en texto plano.
"""


def test_entrar_con_credenciales_correctas(app, datos):
    datos.usuario("ana.admin", "admin")
    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": "ana.admin", "password": "Admin123"},
                             follow_redirects=True)
    assert respuesta.status_code == 200
    assert b"incorrectos" not in respuesta.data


def test_una_contrasena_equivocada_no_deja_entrar(app, datos):
    datos.usuario("ana.admin", "admin")
    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": "ana.admin", "password": "otra"},
                             follow_redirects=True)
    assert "Usuario o contraseña incorrectos" in respuesta.data.decode("utf-8")


def test_un_usuario_inexistente_recibe_el_mismo_mensaje(app):
    """No se distingue "no existe" de "clave mala": decirlo revelaría qué
    usuarios existen a quien pruebe nombres al azar."""
    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": "nadie", "password": "x"},
                             follow_redirects=True)
    assert "Usuario o contraseña incorrectos" in respuesta.data.decode("utf-8")


def test_una_cuenta_desactivada_no_puede_entrar(app, datos):
    datos.usuario("de.baja", "paciente", estado="inactivo")
    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": "de.baja", "password": "Paciente123"},
                             follow_redirects=True)
    assert "desactivada" in respuesta.data.decode("utf-8")


def test_desactivar_a_alguien_le_cierra_la_sesion_abierta(app, datos, bd):
    """No basta con bloquear el login: una cuenta desactivada mientras navega
    no puede seguir operando hasta que se le ocurra salir."""
    id_usuario = datos.usuario("ana.admin", "admin")
    cliente = app.test_client()
    cliente.post("/login", data={"username": "ana.admin", "password": "Admin123"},
                 follow_redirects=True)
    assert cliente.get("/paMC").status_code == 200

    cur = bd.cursor()
    cur.execute("UPDATE usuario SET estado='inactivo' WHERE id_usuario=%s", (id_usuario,))
    cur.close()

    respuesta = cliente.get("/paMC", follow_redirects=True)
    assert "desactivada" in respuesta.data.decode("utf-8")


def test_sin_sesion_ninguna_pantalla_entrega_contenido(anonimo):
    """Un anónimo nunca ve datos: siempre acaba en el formulario de entrada.

    No se exige que el primer salto sea `/login`. Las rutas de administrador
    rebotan antes al tablero, porque `admin_required` manda ahí a quien no tiene
    permiso, y es el tablero el que exige sesión. Lo que importa es dónde termina.
    """
    for ruta in ("/", "/ciMC", "/paMC", "/hiMC", "/usMC", "/coMC", "/reMC",
                 "/exMC", "/esMC", "/meMC", "/medMC", "/disponibilidad"):
        assert anonimo.get(ruta).status_code == 302, f"{ruta} respondió sin sesión"
        final = anonimo.get(ruta, follow_redirects=True).data.decode("utf-8")
        assert 'name="username"' in final and 'name="password"' in final,             f"{ruta} no terminó en el formulario de entrada"


def test_salir_cierra_la_sesion(app, datos):
    datos.usuario("ana.admin", "admin")
    cliente = app.test_client()
    cliente.post("/login", data={"username": "ana.admin", "password": "Admin123"},
                 follow_redirects=True)
    cliente.get("/logout")
    respuesta = cliente.get("/paMC")
    assert respuesta.status_code == 302 and "/login" in respuesta.headers["Location"]


# --- D2: contraseñas ---------------------------------------------------------

def test_el_registro_guarda_la_contrasena_hasheada_con_scrypt(app, datos, bd):
    """D2, la observación del evaluador. La contraseña no se guarda nunca tal
    cual, y el algoritmo es scrypt, un KDF con endurecimiento de memoria."""
    cliente = app.test_client()
    cliente.post("/register", data={
        "nombre": "Marta Gil", "tipo_documento": "CC", "numero_documento": "1088123456",
        "fecha_nacimiento": "1995-04-12", "telefono": "3001234567",
        "direccion": "Calle 1", "email": "marta@ejemplo.com",
        "username": "marta.gil", "password": "Paciente123",
    }, follow_redirects=True)

    fila = datos.fila("SELECT password FROM usuario WHERE username=%s", ("marta.gil",))
    assert fila is not None, "el registro no creó la cuenta"
    assert fila["password"] != "Paciente123"
    assert fila["password"].startswith("scrypt:"), fila["password"][:20]


def test_una_contrasena_en_texto_plano_no_sirve_para_entrar(app, bd):
    """Se quitó el respaldo que comparaba en texto plano cuando el hash fallaba.
    Una fila así (residuo de una base vieja) no puede iniciar sesión."""
    cur = bd.cursor()
    cur.execute("SELECT id_rol FROM rol WHERE nombre_rol='admin'")
    id_rol = cur.fetchone()[0]
    cur.execute("INSERT INTO usuario (username, password, id_rol, estado) "
                "VALUES ('viejo', '12345', %s, 'activo')", (id_rol,))
    cur.close()

    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": "viejo", "password": "12345"},
                             follow_redirects=True)
    assert "Usuario o contraseña incorrectos" in respuesta.data.decode("utf-8")


def test_dos_cuentas_con_la_misma_contrasena_no_comparten_hash(app, datos):
    """La sal es por cuenta. Si dos hashes iguales delataran claves iguales,
    filtrar la tabla revelaría de una vez quiénes usan la misma."""
    datos.usuario("uno", "paciente", clave="Paciente123")
    datos.usuario("dos", "paciente", clave="Paciente123")
    a = datos.fila("SELECT password FROM usuario WHERE username='uno'")["password"]
    b = datos.fila("SELECT password FROM usuario WHERE username='dos'")["password"]
    assert a != b
