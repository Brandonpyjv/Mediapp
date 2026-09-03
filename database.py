"""
Conexión a MySQL. **Una por petición**, tomada de un pool.

Antes había una sola conexión global abierta al importar el módulo, y todas las
rutas la compartían. Funcionaba mientras las peticiones llegaran de a una, pero
Flask sirve con hilos (`app.run` fuerza `threaded=True` en Flask 3.1) y las
conexiones de `mysql-connector` no son seguras entre hilos: dos peticiones
simultáneas se intercalaban sobre el mismo socket y podían cruzar resultados en
cualquier consulta, no solo en las citas.

Ese mismo diseño causaba el hallazgo H6, el de "los cambios hechos por fuera no
se ven hasta reiniciar Flask". La causa no era ningún caché sino la transacción:
`mysql-connector` no confirma sola, así que el primer `SELECT` abría una
transacción que jamás se cerraba, y la conexión seguía leyendo el mismo
instante de la base durante días. Aquí cada petición devuelve su conexión al
pool con un `rollback()`, que es lo que cierra esa transacción, de modo que la
siguiente empieza viendo la base como está.

**Cómo se usa desde las rutas: igual que antes.** `db.conexion` sigue
existiendo y sigue significando "la conexión con la que trabajo ahora", solo que
ahora resuelve a la de la petición en curso. No hubo que tocar las 142 veces que
aparece en `index.py` porque el módulo la resuelve al momento de leerla, con el
`__getattr__` de módulo de PEP 562. Por eso este archivo **no debe declarar una
variable global llamada `conexion`**: si existiera, Python la devolvería sin
llamar nunca a `__getattr__` y volveríamos a la conexión compartida.

Fuera de una petición (un script, una consola) no hay dónde guardar la conexión
de nadie, así que se usa una suelta, abierta aparte del pool para no consumir
sus plazas.
"""
import time

import mysql.connector
from mysql.connector import pooling

CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "",
    "database": "mediapp",
}

# El servidor de desarrollo atiende una pestaña, no una sala llena. Diez plazas
# dejan margen para las peticiones que el navegador lanza en paralelo (la página
# y sus llamadas al calendario) sin abrirle a MySQL conexiones que nadie usa.
TAMANO_POOL = 10

# Cuánto espera una petición por una plaza libre antes de abrirse una conexión
# aparte. Tres segundos es mucho más de lo que dura cualquier pantalla del
# sistema, así que si se agota es porque de verdad hay una avalancha.
ESPERA_POOL = 3.0

_ATRIBUTO = "_conexion_mediapp"      # dónde vive la conexión dentro de `g`

_pool = pooling.MySQLConnectionPool(
    pool_name="mediapp",
    pool_size=TAMANO_POOL,
    # El reseteo automático se deja apagado y la transacción se cierra a mano en
    # `_devolver()`. MariaDB responde al reseteo de sesión de forma distinta a
    # MySQL, y un fallo ahí ocurriría al devolver la conexión, es decir, después
    # de que la petición ya respondió: un error imposible de rastrear desde la
    # pantalla que lo provocó.
    pool_reset_session=False,
    **CONFIG,
)

_suelta = None                       # la de los scripts, fuera de Flask


def _sacar_del_pool():
    """Pide una plaza al pool, esperando si están todas ocupadas.

    `get_connection()` no espera: si las diez plazas están tomadas lanza
    `PoolError` de inmediato y la petición muere con un error 500. Eso se vio en
    la prueba de carga de S1, con cien peticiones a la vez. Como una plaza se
    libera al terminar cualquier petición, casi siempre basta con esperar unos
    milisegundos, así que aquí se reintenta durante `ESPERA_POOL` segundos antes
    de darse por vencido.
    """
    limite = time.monotonic() + ESPERA_POOL
    while True:
        try:
            return _pool.get_connection()
        except mysql.connector.errors.PoolError:
            if time.monotonic() >= limite:
                raise
            time.sleep(0.02)


def _abrir_del_pool():
    """La conexión de la petición, viva y comprobada.

    Una conexión que estuvo guardada mientras MySQL cerraba la suya por
    inactividad vuelve del pool muerta, y el error aparecería en medio de la
    consulta de una ruta. El `ping` con reconexión lo resuelve antes.

    Si el pool sigue lleno después de la espera, se abre una conexión fuera de
    él en vez de responder con un error. Es una válvula de escape: prefiere una
    conexión de más a una pantalla caída, y se cierra igual al terminar la
    petición porque `close()` sobre una conexión no agrupada la cierra de verdad.
    """
    try:
        conexion = _sacar_del_pool()
    except mysql.connector.errors.PoolError:
        return _abrir_suelta()
    try:
        conexion.ping(reconnect=True, attempts=3, delay=1)
    except mysql.connector.Error:
        conexion.close()
        conexion = _sacar_del_pool()
    return conexion


def _abrir_suelta():
    return mysql.connector.connect(**CONFIG)


def obtener():
    """La conexión de esta petición, o una suelta si no hay petición."""
    from flask import g, has_app_context

    if has_app_context():
        conexion = getattr(g, _ATRIBUTO, None)
        if conexion is None:
            conexion = _abrir_del_pool()
            setattr(g, _ATRIBUTO, conexion)
        return conexion

    global _suelta
    if _suelta is None or not _suelta.is_connected():
        _suelta = _abrir_suelta()
    return _suelta


def _devolver(_error=None):
    """Cierra la transacción de la petición y devuelve la conexión al pool.

    El `rollback()` no descarta trabajo confirmado, porque las rutas confirman
    con `commit()` en cuanto terminan de escribir. Lo que descarta es la
    transacción de lectura que abre cualquier `SELECT`, y es justo lo que hay que
    cerrar para que la conexión no se quede mirando una foto vieja de la base.
    """
    from flask import g

    conexion = g.pop(_ATRIBUTO, None)
    if conexion is None:
        return
    try:
        conexion.rollback()
    except mysql.connector.Error:
        pass
    try:
        conexion.close()             # en una conexión del pool, esto la devuelve
    except mysql.connector.Error:
        pass


def registrar(app):
    """Engancha la devolución de la conexión al final de cada petición."""
    app.teardown_appcontext(_devolver)
    return app


def __getattr__(nombre):
    """`db.conexion` resuelve a la conexión de quien la pide (PEP 562)."""
    if nombre == "conexion":
        return obtener()
    raise AttributeError(f"module {__name__!r} no tiene el atributo {nombre!r}")
