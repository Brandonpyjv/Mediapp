# -*- coding: utf-8 -*-
"""
Lector del esquema de la base de datos de MediApp.

El diccionario de datos y el modelo físico se arman **leyendo el esquema real**, no
transcribiendo las tablas a mano. Un diccionario copiado a mano empieza a envejecer el día que
se escribe, y la forma en que se descubre es siempre la misma, cuando alguien busca en el
sistema una columna que el documento describe y que ya no existe.

🔴 **Esto responde a la observación O14**, que pedía agregar el modelo relacional generado desde
MySQL. La fuente preferida es el propio motor, consultado a través de su catálogo interno, de
modo que lo que el documento describe es literalmente lo que la base tiene. Si el motor no está
disponible, se cae al respaldo `Base/mediapp.sql`, que también lo produjo MySQL, y la función
`fuente()` dice cuál de los dos se usó.

**Las descripciones son lo único escrito a mano, y no por gusto.** FactuGest las sacaba del
`COMMENT` de cada columna, pero el esquema de MediApp no lleva comentarios, así que viven en
`DESCRIPCIONES`. Toda columna que no tenga la suya se reporta al correr el módulo, de manera que
una columna nueva no pueda pasar al documento sin explicación.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RESPALDO = RAIZ / "Base" / "mediapp.sql"

BASE_DE_DATOS = "mediapp"

# Las once tablas, en el orden en que las nombra la documentación.
TABLAS = ["cita", "consulta", "especialidad", "examen", "historia", "medicamento",
          "medico", "paciente", "receta", "rol", "usuario"]

TIPOS = {
    "int": "Entero", "bigint": "Entero grande", "tinyint": "Entero pequeño",
    "smallint": "Entero pequeño", "varchar": "Texto", "text": "Texto largo",
    "longtext": "Texto largo", "mediumtext": "Texto largo", "tinytext": "Texto",
    "decimal": "Decimal", "double": "Decimal", "float": "Decimal",
    "date": "Fecha", "datetime": "Fecha y hora", "timestamp": "Fecha y hora",
    "time": "Hora", "enum": "Enumerado", "char": "Texto",
    "blob": "Binario", "longblob": "Binario", "mediumblob": "Binario",
}

# Qué guarda y para qué sirve cada tabla.
PROPOSITO = {
    "cita": "Agenda de atención. Guarda cada cita con su fecha y hora, el motivo por el que se "
            "solicita y su estado, que distingue las vigentes de las canceladas.",
    "consulta": "Diagnóstico y plan de tratamiento que el médico registra tras atender a un "
                "paciente. De ella cuelgan las prescripciones.",
    "especialidad": "Catálogo de especialidades médicas al que se adscribe cada profesional.",
    "examen": "Exámenes de laboratorio. Reúne en una misma fila la solicitud que hace el "
              "médico y el resultado que carga después el laboratorio.",
    "historia": "Historia clínica del paciente. Guarda la evolución registrada por el médico "
                "tratante a lo largo del tiempo.",
    "medicamento": "Catálogo de medicamentos disponibles para prescribir, con su estado, que "
                   "distingue los vigentes de los descontinuados.",
    "medico": "Ficha profesional del médico, con su especialidad, sus datos de contacto y el "
              "vínculo con la cuenta con la que ingresa al sistema.",
    "paciente": "Datos personales y de contacto de las personas que reciben atención, con el "
                "vínculo a la cuenta con la que consultan lo suyo.",
    "receta": "Prescripción emitida sobre una consulta, con el medicamento, la cantidad y las "
              "indicaciones del tratamiento.",
    "rol": "Catálogo de los tres perfiles de acceso del sistema, que son administrador, médico "
           "y paciente.",
    "usuario": "Cuentas de acceso, con su nombre de usuario, la contraseña guardada como hash, "
               "el rol asignado y su estado.",
}

# (tabla, columna): descripción. Escritas a mano porque el esquema no lleva comentarios.
DESCRIPCIONES = {
    ("cita", "id_cita"): "Identificador único de la cita.",
    ("cita", "fecha"): "Fecha y hora en que se atenderá la cita.",
    ("cita", "motivo"): "Motivo por el que se solicita la consulta.",
    ("cita", "estado"): "Estado de la cita. Las canceladas se ignoran al validar la agenda, de "
                        "modo que su horario vuelve a quedar libre.",
    ("cita", "id_paciente"): "Paciente que recibirá la atención.",
    ("cita", "id_medico"): "Médico que atenderá la cita.",

    ("consulta", "id_consulta"): "Identificador único de la consulta.",
    ("consulta", "fecha"): "Fecha y hora en que se registró el diagnóstico.",
    ("consulta", "diagnostico"): "Diagnóstico emitido por el médico tratante.",
    ("consulta", "tratamiento"): "Plan de tratamiento indicado al paciente.",
    ("consulta", "id_paciente"): "Paciente al que corresponde el diagnóstico.",
    ("consulta", "id_medico"): "Médico que registró la consulta, tomado de la sesión y nunca "
                               "del formulario.",

    ("especialidad", "id_especialidad"): "Identificador único de la especialidad.",
    ("especialidad", "nombre"): "Nombre de la especialidad. No puede repetirse.",
    ("especialidad", "descripcion"): "Descripción del ámbito de la especialidad.",

    ("examen", "id_examen"): "Identificador único del examen.",
    ("examen", "id_paciente"): "Paciente al que se le practica el examen.",
    ("examen", "id_medico"): "Médico que solicitó el examen.",
    ("examen", "tipo_examen"): "Tipo de examen solicitado.",
    ("examen", "fecha_solicitud"): "Fecha y hora en que el médico solicitó el examen.",
    ("examen", "fecha_resultado"): "Fecha y hora en que el laboratorio cargó el resultado. "
                                   "Queda vacía mientras el examen esté pendiente.",
    ("examen", "resultado"): "Resultado del examen, que carga el administrador. Es la parte de "
                             "la fila que el médico no puede escribir.",

    ("historia", "id_historia"): "Identificador único del registro clínico.",
    ("historia", "id_paciente"): "Paciente al que pertenece la historia clínica.",
    ("historia", "id_medico"): "Médico que firmó el registro, tomado de la sesión y nunca del "
                               "formulario.",
    ("historia", "fecha"): "Fecha y hora de la evolución registrada.",
    ("historia", "descripcion"): "Descripción de la evolución del paciente.",
    ("historia", "notas"): "Observaciones adicionales del médico tratante.",

    ("medicamento", "id_medicamento"): "Identificador único del medicamento.",
    ("medicamento", "nombre"): "Nombre del medicamento. No puede repetirse.",
    ("medicamento", "descripcion"): "Descripción del medicamento.",
    ("medicamento", "dosis"): "Presentación o dosis de referencia del medicamento.",
    ("medicamento", "estado"): "Estado del medicamento. Los descontinuados dejan de ofrecerse "
                               "al recetar, pero las recetas que ya los usaron los conservan.",

    ("medico", "id_medico"): "Identificador único del médico.",
    ("medico", "nombre"): "Nombre completo del profesional.",
    ("medico", "numero_identidad"): "Número de documento del médico. No puede repetirse.",
    ("medico", "telefono"): "Teléfono de contacto.",
    ("medico", "email"): "Correo electrónico de contacto.",
    ("medico", "id_especialidad"): "Especialidad a la que pertenece el médico.",
    ("medico", "id_usuario"): "Cuenta con la que el médico ingresa al sistema. Queda vacía "
                              "mientras la ficha no se haya vinculado a una cuenta, y en ese "
                              "caso el profesional no puede firmar registros clínicos.",
    ("medico", "estado"): "Estado de la ficha. Un médico inactivo deja de ofrecerse al agendar "
                          "y conserva todo lo que firmó.",

    ("paciente", "id_paciente"): "Identificador único del paciente.",
    ("paciente", "nombre"): "Nombre completo del paciente.",
    ("paciente", "tipo_documento"): "Tipo de documento de identidad.",
    ("paciente", "numero_documento"): "Número de documento. No puede repetirse.",
    ("paciente", "fecha_nacimiento"): "Fecha de nacimiento. No puede ser posterior al día de "
                                      "hoy.",
    ("paciente", "telefono"): "Teléfono de contacto.",
    ("paciente", "direccion"): "Dirección de residencia.",
    ("paciente", "email"): "Correo electrónico de contacto.",
    ("paciente", "id_usuario"): "Cuenta con la que el paciente consulta lo suyo. Queda vacía "
                                "cuando lo registró el administrador y todavía no tiene cuenta.",
    ("paciente", "estado"): "Estado del paciente. Uno inactivo conserva su historial y sus "
                            "citas.",

    ("receta", "id_receta"): "Identificador único de la receta.",
    ("receta", "id_consulta"): "Consulta sobre la que se emite la prescripción.",
    ("receta", "id_medicamento"): "Medicamento prescrito, tomado del catálogo.",
    ("receta", "cantidad"): "Cantidad prescrita. Debe ser mayor que cero.",
    ("receta", "indicaciones"): "Indicaciones de administración del tratamiento.",

    ("rol", "id_rol"): "Identificador único del rol.",
    ("rol", "nombre_rol"): "Nombre del perfil de acceso.",

    ("usuario", "id_usuario"): "Identificador único de la cuenta.",
    ("usuario", "username"): "Nombre de usuario con el que se ingresa. No puede repetirse.",
    ("usuario", "password"): "Contraseña guardada como hash con el algoritmo scrypt. En ningún "
                             "caso se almacena la contraseña legible.",
    ("usuario", "id_rol"): "Rol asignado a la cuenta, del que dependen todos los permisos.",
    ("usuario", "estado"): "Estado de la cuenta. Una cuenta inactiva no puede iniciar sesión y "
                           "conserva lo que firmó.",
}

_FUENTE = None


def _legible(tipo_sql):
    """«varchar(150)» se lee mejor como «Texto (150)» en un documento."""
    tipo_sql = tipo_sql.strip()
    base = re.match(r"([a-z]+)(\((.*)\))?", tipo_sql, re.I)
    if not base:
        return tipo_sql
    nombre = TIPOS.get(base.group(1).lower(), base.group(1))
    detalle = base.group(3)
    if not detalle:
        return nombre
    if base.group(1).lower() == "enum":
        valores = ", ".join(v.strip().strip("'\"") for v in detalle.split(","))
        return f"{nombre} ({valores})"
    return f"{nombre} ({detalle})"


# --- Lectura desde el motor -----------------------------------------------------

def _desde_mysql():
    import mysql.connector

    conexion = mysql.connector.connect(host="localhost", user="root", password="",
                                       database=BASE_DE_DATOS, connection_timeout=5)
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA "
        "FROM information_schema.columns WHERE TABLE_SCHEMA = %s "
        "ORDER BY TABLE_NAME, ORDINAL_POSITION", (BASE_DE_DATOS,))
    columnas = {}
    for fila in cursor.fetchall():
        columnas.setdefault(fila["TABLE_NAME"], []).append(
            (fila["COLUMN_NAME"], fila["COLUMN_TYPE"], fila["IS_NULLABLE"] == "YES",
             fila["COLUMN_KEY"], fila["EXTRA"] or ""))

    cursor.execute(
        "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
        "FROM information_schema.key_column_usage "
        "WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL "
        "ORDER BY TABLE_NAME, COLUMN_NAME", (BASE_DE_DATOS,))
    foraneas = [(f["TABLE_NAME"], f["COLUMN_NAME"], f["REFERENCED_TABLE_NAME"],
                 f["REFERENCED_COLUMN_NAME"]) for f in cursor.fetchall()]

    cursor.close()
    conexion.close()
    return columnas, foraneas


# --- Lectura desde el respaldo --------------------------------------------------

def _cuerpo(tabla, sql):
    patron = rf"CREATE TABLE (?:IF NOT EXISTS )?`?{tabla}`?\s*\((.*?)\n\)\s*ENGINE"
    encontrado = re.search(patron, sql, re.S | re.I)
    if not encontrado:
        raise KeyError(f"No se encontró la tabla «{tabla}» en {RESPALDO.name}")
    return encontrado.group(1)


def _desde_respaldo():
    sql = RESPALDO.read_text(encoding="utf-8", errors="replace")
    columnas, foraneas = {}, []
    for tabla in TABLAS:
        cuerpo = _cuerpo(tabla, sql)
        propias = []
        claves_unicas, primaria = set(), set()
        for linea in cuerpo.splitlines():
            linea = linea.strip().rstrip(",")
            if m := re.match(r"PRIMARY KEY \((.+)\)", linea, re.I):
                primaria |= {c.strip().strip("`") for c in m.group(1).split(",")}
            elif m := re.match(r"UNIQUE KEY `[^`]+` \((.+)\)", linea, re.I):
                claves_unicas |= {c.strip().strip("`") for c in m.group(1).split(",")}
            elif m := re.match(
                    r"CONSTRAINT `[^`]+` FOREIGN KEY \(`([^`]+)`\) "
                    r"REFERENCES `([^`]+)` \(`([^`]+)`\)", linea, re.I):
                foraneas.append((tabla, m.group(1), m.group(2), m.group(3)))
            elif m := re.match(r"`([^`]+)` +([a-z]+(?:\([^)]*\))?)(.*)", linea, re.I):
                propias.append([m.group(1), m.group(2), "NOT NULL" not in m.group(3).upper(),
                                "", "auto_increment" if "AUTO_INCREMENT" in m.group(3).upper()
                                else ""])
        for columna in propias:
            if columna[0] in primaria:
                columna[3] = "PRI"
            elif columna[0] in claves_unicas:
                columna[3] = "UNI"
        columnas[tabla] = [tuple(c) for c in propias]

    for tabla, columna, _destino, _ in foraneas:
        for i, c in enumerate(columnas[tabla]):
            if c[0] == columna and not c[3]:
                columnas[tabla][i] = (c[0], c[1], c[2], "MUL", c[4])
    return columnas, foraneas


def leer():
    """Devuelve (columnas por tabla, claves foráneas) y recuerda de dónde salió."""
    global _FUENTE
    try:
        datos = _desde_mysql()
        _FUENTE = "el motor MySQL, consultado a través de su catálogo interno"
    except Exception:
        datos = _desde_respaldo()
        _FUENTE = f"el respaldo {RESPALDO.name}, generado por MySQL"
    return datos


def fuente():
    if _FUENTE is None:
        leer()
    return _FUENTE


# --- Lo que consumen el diccionario y las figuras -------------------------------

def columnas(tabla, datos=None):
    """(nombre, tipo legible, admite nulo, clave, descripción) por columna."""
    crudas, _ = datos if datos else leer()
    salida = []
    for nombre, tipo, admite_nulo, clave, extra in crudas[tabla]:
        # Se deja en «Primaria» a secas y no en «Primaria, autonumérica». Las once claves
        # primarias lo son, así que repetirlo en cada fila no informa y además parte la
        # palabra en la columna estrecha del diccionario. El dato se declara una vez, en el
        # apartado de convenciones del documento.
        etiqueta = {"PRI": "Primaria", "UNI": "Única", "MUL": "Foránea"}.get(clave, "")
        salida.append((nombre, _legible(tipo), "Sí" if admite_nulo else "No",
                       etiqueta or "Ninguna",
                       DESCRIPCIONES.get((tabla, nombre), "")))
    return salida


def relaciones(datos=None):
    """(tabla origen, columna, tabla destino, columna) por clave foránea."""
    _, foraneas = datos if datos else leer()
    return foraneas


def sin_descripcion(datos=None):
    """Columnas que todavía no tienen descripción escrita."""
    datos = datos or leer()
    faltan = []
    for tabla in TABLAS:
        for nombre, *_ in datos[0][tabla]:
            if not DESCRIPCIONES.get((tabla, nombre)):
                faltan.append(f"{tabla}.{nombre}")
    return faltan


def conteo(datos=None):
    datos = datos or leer()
    return {
        "tablas": len(TABLAS),
        "columnas": sum(len(datos[0][t]) for t in TABLAS),
        "foraneas": len(datos[1]),
    }


if __name__ == "__main__":
    datos = leer()
    c = conteo(datos)
    print(f"Fuente: {fuente()}")
    print(f"Tablas: {c['tablas']}  Columnas: {c['columnas']}  Claves foraneas: {c['foraneas']}")
    for tabla in TABLAS:
        print(f"\n== {tabla} ==")
        for nombre, tipo, nulo, clave, _desc in columnas(tabla, datos):
            print(f"   {nombre:20} {tipo:34} nulo={nulo:3} {clave}")
    faltan = sin_descripcion(datos)
    if faltan:
        print(f"\nAVISO sin descripcion ({len(faltan)}): {', '.join(faltan)}")
        raise SystemExit(1)
    print("\nTodas las columnas tienen descripcion.")
