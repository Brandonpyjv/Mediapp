# -*- coding: utf-8 -*-
"""
Andamiaje de las pruebas automatizadas de MediApp (S6).

**Ninguna prueba toca la base de desarrollo.** Se trabaja siempre contra
`mediapp_test`, que se construye desde cero al empezar la sesión de pruebas y se
vacía antes de cada prueba. La variable de entorno `MEDIAPP_DB` se fija aquí,
antes de importar la aplicación, porque `database.py` arma su pool al importarse:
si se pusiera después, el pool ya estaría apuntando a la base equivocada.

**El esquema se clona del de desarrollo, no de un `.sql` guardado.** Se copia con
`SHOW CREATE TABLE` de la base real, lo que garantiza que las pruebas corran
contra exactamente el mismo esquema que la aplicación, con sus siete migraciones
aplicadas y sus claves foráneas. Un volcado aparte envejecería: la migración
número ocho dejaría las pruebas comprobando un esquema que ya no existe.

Cómo se corren:

    python -m pytest tests -v
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

BASE_REAL = os.environ.get("MEDIAPP_DB_ORIGEN", "mediapp")
BASE_PRUEBAS = os.environ.get("MEDIAPP_DB_PRUEBAS", "mediapp_test")

# Antes de cualquier `import index`, que arrastra `database` y su pool.
os.environ["MEDIAPP_DB"] = BASE_PRUEBAS

import mysql.connector                                        # noqa: E402
from werkzeug.security import generate_password_hash          # noqa: E402

CONEXION = {
    "host": os.environ.get("MEDIAPP_DB_HOST", "localhost"),
    "user": os.environ.get("MEDIAPP_DB_USER", "root"),
    "passwd": os.environ.get("MEDIAPP_DB_PASSWORD", ""),
}

# Orden de borrado: de las hijas a las madres, para no chocar con las claves
# foráneas. `rol` no se borra nunca porque es catálogo, no dato de prueba.
ORDEN_BORRADO = ["receta", "consulta", "historia", "examen", "cita",
                 "medicamento", "medico", "paciente", "especialidad", "usuario"]

CLAVES = {"admin": "Admin123", "medico": "Medico123", "paciente": "Paciente123"}


def _sin_base(**extra):
    return mysql.connector.connect(**CONEXION, **extra)


def _clonar_esquema():
    """Rehace `mediapp_test` con el mismo esquema que la base de desarrollo."""
    origen = _sin_base(database=BASE_REAL)
    cur = origen.cursor()
    cur.execute("SHOW TABLES")
    tablas = [f[0] for f in cur.fetchall()]
    definiciones = []
    for tabla in tablas:
        cur.execute(f"SHOW CREATE TABLE `{tabla}`")
        definiciones.append(cur.fetchone()[1])
    cur.execute("SELECT id_rol, nombre_rol FROM rol")
    roles = cur.fetchall()
    cur.close()
    origen.close()

    servidor = _sin_base()
    cur = servidor.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS `{BASE_PRUEBAS}`")
    cur.execute(f"CREATE DATABASE `{BASE_PRUEBAS}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
    cur.execute(f"USE `{BASE_PRUEBAS}`")
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")   # el orden de creación deja de importar
    for definicion in definiciones:
        cur.execute(definicion)
    cur.executemany("INSERT INTO rol (id_rol, nombre_rol) VALUES (%s, %s)", roles)
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    servidor.commit()
    cur.close()
    servidor.close()
    return {nombre: id_rol for id_rol, nombre in roles}


# La base se construye **al cargar este archivo**, no en una fixture. Un módulo de
# prueba puede hacer `import database` en su primera línea, y eso arma el pool: si
# la base no existiera todavía, pytest fallaría al recolectar, antes de que
# ninguna fixture haya tenido ocasión de crearla.
try:
    ROLES = _clonar_esquema()
except mysql.connector.Error as error:
    raise RuntimeError(
        f"No se pudo preparar la base de pruebas «{BASE_PRUEBAS}» a partir de "
        f"«{BASE_REAL}». ¿Está MySQL arriba (XAMPP) y existe la base de "
        f"desarrollo? Error de MySQL: {error}"
    ) from error

_FALTAN = {"admin", "medico", "paciente"} - set(ROLES)
if _FALTAN:
    raise RuntimeError(f"La base {BASE_REAL} no tiene los roles {_FALTAN}")


@pytest.fixture(scope="session")
def roles():
    return ROLES


@pytest.fixture(scope="session")
def app(roles):
    import index
    index.app.config["TESTING"] = True
    return index.app


@pytest.fixture
def bd(app):
    """Conexión directa a la base de pruebas, para montar y comprobar datos.

    Es una conexión aparte de la de la aplicación a propósito: comprobar el
    resultado con la misma conexión que lo escribió no probaría que quedó
    confirmado en la base.
    """
    conexion = _sin_base(database=BASE_PRUEBAS)
    conexion.autocommit = True
    yield conexion
    conexion.close()


@pytest.fixture(autouse=True)
def base_limpia(bd):
    """Deja la base sin datos antes de cada prueba. Se aplica sola."""
    cur = bd.cursor()
    for tabla in ORDEN_BORRADO:
        cur.execute(f"DELETE FROM `{tabla}`")
    cur.close()
    yield


# Las cuentas de las fixtures se hashean con un KDF barato, no con el de la
# aplicación. `scrypt` es lento **a propósito**, que es justo su virtud, pero cada
# prueba crea tres cuentas y entra tres veces, y eso convertía la suite en cuarenta
# segundos de espera. Con esto baja a unos pocos.
#
# No debilita nada, porque no es la aplicación la que se está configurando: quien
# guarda contraseñas de verdad es el registro, y hay una prueba dedicada
# (`test_el_registro_guarda_la_contrasena_hasheada_con_scrypt`) que pasa por esa
# ruta real y comprueba que el hash guardado empieza por «scrypt:». `werkzeug`
# reconoce el algoritmo desde el propio hash, así que el inicio de sesión de las
# pruebas recorre exactamente el mismo código que en producción.
KDF_DE_PRUEBAS = "pbkdf2:sha256:1"


class Ayudante:
    """Crea los datos que una prueba necesita, con la forma que usa la aplicación.

    Las contraseñas se hashean igual que lo hace el registro real (salvo el coste,
    ver arriba), porque una fila insertada con la contraseña en texto plano no
    podría iniciar sesión y la prueba fallaría por el andamiaje y no por el sistema.
    """

    def __init__(self, conexion, roles):
        self.bd = conexion
        self.roles = roles
        self._siguiente = 1000

    def _insertar(self, sql, valores):
        cur = self.bd.cursor()
        cur.execute(sql, valores)
        nuevo = cur.lastrowid
        cur.close()
        return nuevo

    def usuario(self, username, rol, estado="activo", clave=None):
        return self._insertar(
            "INSERT INTO usuario (username, password, id_rol, estado) VALUES (%s, %s, %s, %s)",
            (username, generate_password_hash(clave or CLAVES[rol], method=KDF_DE_PRUEBAS),
             self.roles[rol], estado))

    def especialidad(self, nombre="Medicina General"):
        """La crea, o devuelve la que ya existe con ese nombre.

        `especialidad.nombre` es único, y dos médicos de prueba pedían la misma
        por defecto. Reutilizarla es además lo realista: en una clínica los
        médicos comparten especialidad.
        """
        existente = self.fila("SELECT id_especialidad FROM especialidad WHERE nombre=%s",
                              (nombre,))
        if existente:
            return existente["id_especialidad"]
        return self._insertar("INSERT INTO especialidad (nombre) VALUES (%s)", (nombre,))

    def _documento(self):
        """Un número de documento distinto en cada llamada.

        `medico.numero_identidad` y `paciente.numero_documento` son únicos, así
        que dos personas de prueba con el valor por defecto chocaban entre sí.
        """
        self._siguiente += 1
        return self._siguiente

    def medico(self, nombre="Ana Torres", username=None, estado="activo", id_especialidad=None):
        """Devuelve `(id_medico, id_usuario)`. Sin `username`, queda sin cuenta."""
        id_usuario = self.usuario(username, "medico") if username else None
        documento = self._documento()
        return self._insertar(
            "INSERT INTO medico (nombre, numero_identidad, telefono, email, "
            "id_especialidad, id_usuario, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nombre, documento, "3000000000", f"medico{documento}@ejemplo.com",
             id_especialidad or self.especialidad(), id_usuario, estado)), id_usuario

    def paciente(self, nombre="Luis Pardo", username=None, estado="activo"):
        """Devuelve `(id_paciente, id_usuario)`. Sin `username`, queda sin cuenta."""
        id_usuario = self.usuario(username, "paciente") if username else None
        documento = self._documento()
        return self._insertar(
            "INSERT INTO paciente (nombre, tipo_documento, numero_documento, "
            "fecha_nacimiento, telefono, direccion, email, id_usuario, estado) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (nombre, "CC", str(documento), "1990-01-01", "3000000000", "Calle 1",
             f"paciente{documento}@ejemplo.com", id_usuario, estado)), id_usuario

    def cita(self, id_paciente, id_medico, fecha, motivo="control", estado="agendada"):
        return self._insertar(
            "INSERT INTO cita (id_paciente, id_medico, fecha, motivo, estado) VALUES (%s, %s, %s, %s, %s)",
            (id_paciente, id_medico, fecha, motivo, estado))

    def historia(self, id_paciente, id_medico, fecha, descripcion="nota clínica"):
        return self._insertar(
            "INSERT INTO historia (id_paciente, id_medico, fecha, descripcion) VALUES (%s, %s, %s, %s)",
            (id_paciente, id_medico, fecha, descripcion))

    def contar(self, tabla, donde="1", valores=()):
        cur = self.bd.cursor()
        cur.execute(f"SELECT COUNT(*) FROM `{tabla}` WHERE {donde}", valores)
        total = cur.fetchone()[0]
        cur.close()
        return total

    def fila(self, sql, valores=()):
        cur = self.bd.cursor(dictionary=True)
        cur.execute(sql, valores)
        fila = cur.fetchone()
        cur.close()
        return fila


@pytest.fixture
def datos(bd, roles):
    return Ayudante(bd, roles)


def _entrar(app, username, clave):
    cliente = app.test_client()
    respuesta = cliente.post("/login", data={"username": username, "password": clave},
                             follow_redirects=True)
    assert b"incorrectos" not in respuesta.data, f"No se pudo entrar como {username}"
    return cliente


@pytest.fixture
def anonimo(app):
    return app.test_client()


@pytest.fixture
def entrar(app):
    """Devuelve una función para iniciar sesión con cualquier cuenta."""
    def hacerlo(username, clave=None, rol="admin"):
        return _entrar(app, username, clave or CLAVES[rol])
    return hacerlo


@pytest.fixture
def admin(app, datos):
    datos.usuario("admin_pruebas", "admin")
    return _entrar(app, "admin_pruebas", CLAVES["admin"])
