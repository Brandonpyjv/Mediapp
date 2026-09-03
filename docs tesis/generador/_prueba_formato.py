"""
Prueba del motor APA (T2): genera un documento corto con **todos** los elementos
que la norma regula, para abrirlo en Word y verificar el formato antes de escribir
cien páginas encima.

No hace parte de los entregables. El nombre empieza por guion bajo para que se vea
que es andamiaje y no un capítulo.

    python "docs tesis/generador/_prueba_formato.py"

Después conviene mirarlo de verdad, no como uno cree que quedó:

    python "docs tesis/generador/revisar.py" "docs tesis/entregables/_prueba_formato_apa.docx"
"""
from pathlib import Path

from apa import DocumentoAPA

BASE = Path(__file__).resolve().parent.parent
PROYECTO = BASE.parent
SALIDA = BASE / "entregables" / "_prueba_formato_apa.docx"

TITULO = ("MediApp: Sistema web de agendamiento de citas médicas y gestión de historias "
          "clínicas para la optimización de la atención en centros de salud")

d = DocumentoAPA()

d.portada(
    titulo="MEDIAPP",
    subtitulo=("Sistema web de agendamiento de citas médicas y gestión de historias "
               "clínicas para la optimización de la atención en centros de salud"),
    integrantes=["ÁNGEL JESÚS HERNÁNDEZ ARÉVALO",
                 "RICHARD ALBERTO QUIÑONES QUIÑONES"],
    grado=("Trabajo de grado presentado como requisito para optar al título de:\n"
           "Tecnólogo en Análisis y Desarrollo de Software"),
    institucion=["SERVICIO NACIONAL DE APRENDIZAJE (SENA)",
                 "Centro de la Industria, la Empresa y los Servicios (CIES)",
                 "Tecnólogo en Análisis y Desarrollo de Software"],
    ciudad="CÚCUTA, NORTE DE SANTANDER",
    anio=2026,
)

d.tabla_contenido()

d.titulo("Prueba de formato", nivel=1)
d.parrafo(
    "Este documento no hace parte de los entregables. Existe para verificar en Word que "
    "el motor de formato aplica lo que la norma exige, es decir, márgenes de 2,54 cm en "
    "los cuatro lados, Times New Roman de 12 puntos, interlineado doble, sangría de "
    "primera línea de 1,27 cm y numeración de páginas en la esquina superior derecha "
    "desde la portada."
)
d.parrafo(
    "Este segundo párrafo permite comprobar dos cosas a la vez, porque la sangría de "
    "primera línea tiene que repetirse y entre párrafos no debe agregarse espacio "
    "adicional, ya que en un texto a doble espacio ese espacio extra sobra."
)

d.titulo("1.1 Un título de nivel 2", nivel=2)
d.parrafo(
    "Los títulos no se escriben con mayúscula sostenida y conservan el tamaño del cuerpo "
    "del texto. Se distinguen por su peso y su posición, no por ser más grandes."
)

d.titulo("1.1.1 Un título de nivel 3", nivel=3)
d.parrafo(
    "El de nivel 3 va en negrita cursiva y termina en punto. El motor le agrega el punto "
    "si quien escribe lo olvida, y aquí se omitió a propósito para comprobarlo"
)

d.parrafo("Los tres perfiles del sistema, con viñetas y término en negrita:", sangria=False)
d.vinetas([
    ("Administrador", "gestiona la operación del centro, las personas, los catálogos y la "
                      "agenda completa."),
    ("Médico", "es dueño exclusivo del acto clínico, es decir, de la historia, el "
               "diagnóstico y la prescripción."),
    ("Paciente", "consulta lo suyo, agenda su propia cita y puede cancelarla."),
])

d.parrafo("Los objetivos específicos, en lista numerada:", sangria=False)
d.numerada([
    "Facilitar la programación de la atención médica mediante un módulo interactivo que "
    "permita al administrador y al paciente agendar citas de forma intuitiva.",
    "Habilitar la gestión del acto clínico como responsabilidad exclusiva del médico "
    "tratante para la creación y actualización de historias clínicas, diagnósticos y "
    "prescripciones.",
    "Garantizar la confidencialidad de la información médica mediante un control de "
    "acceso basado en roles que restrinja la visualización y edición según el perfil "
    "del usuario.",
])

d.parrafo("Una cita de más de cuarenta palabras, en bloque y sin comillas:", sangria=False)
d.cita_larga(
    "La ausencia de herramientas digitales adecuadas obliga al personal de los servicios "
    "de atención de escala reducida a llevar registros en archivos físicos, agendas o "
    "-en el mejor de los casos- hojas de cálculo no estructuradas, lo que genera "
    "consecuencias directas sobre la trazabilidad y la continuidad de la atención, y "
    "aumenta el riesgo de pérdida de información y de errores de identificación del "
    "paciente.",
    fuente="Autor, 2026, p. 12",
)

d.tabla(
    "Matriz de permisos de MediApp por módulo y por rol",
    ["Módulo", "Administrador", "Médico", "Paciente"],
    [
        ["Historia clínica", "Solo lectura", "Crear, editar y eliminar", "Solo la suya"],
        ["Consulta y diagnóstico", "Solo lectura", "Crear y editar", "Solo las suyas"],
        ["Prescripción", "Solo lectura", "Crear y gestionar", "Solo las suyas"],
        ["Cita", "CRUD completo", "Solo ver las suyas", "Agendar y cancelar la suya"],
        ["Usuario, médico y paciente", "CRUD completo", "Ninguno", "Su perfil, sin eliminarlo"],
    ],
    nota="Elaboración propia a partir de los decoradores de permiso de cada ruta. La "
         "columna del Médico recoge su permiso exclusivo sobre el acto clínico.",
    anchos=[4.0, 3.6, 4.5, 4.4],
)

d.figura(
    "Identificador visual de MediApp",
    PROYECTO / "templates" / "static" / "img" / "logo.png",
    nota="Se usa aquí únicamente para comprobar que la figura se centra, se ajusta a los "
         "márgenes y recibe su rótulo y su nota. Elaboración propia.",
)

d.titulo("1.2 Una tabla en página apaisada", nivel=2)
d.parrafo(
    "El modelo físico de la base no cabe en una página vertical, así que el motor abre "
    "una sección horizontal y vuelve a la vertical al terminar. La numeración de páginas "
    "sigue corrida porque el encabezado se hereda."
)
ancho = d.seccion_horizontal()
d.tabla(
    "Las once tablas del esquema relacional",
    ["Tabla", "Qué guarda", "Se relaciona con"],
    [
        ["rol", "Los tres perfiles del sistema", "usuario"],
        ["usuario", "Las credenciales y el perfil de acceso", "rol, medico, paciente"],
        ["paciente", "Los datos demográficos de quien se atiende", "usuario, cita, historia"],
        ["medico", "El profesional y su especialidad", "usuario, especialidad, cita"],
        ["especialidad", "El catálogo de especialidades", "medico"],
        ["cita", "La programación de la atención", "paciente, medico, consulta"],
        ["consulta", "El diagnóstico y el tratamiento posteriores a la cita", "cita, receta"],
        ["historia", "La evolución clínica del paciente", "paciente, medico"],
        ["examen", "La solicitud de laboratorio y su resultado", "paciente, medico"],
        ["medicamento", "El catálogo de medicamentos", "receta"],
        ["receta", "La prescripción emitida en una consulta", "consulta, medicamento"],
    ],
    nota="Elaboración propia a partir del esquema real de la base de datos.",
)
d.seccion_vertical()
d.parrafo(
    "Y aquí el documento continúa en vertical, para comprobar que la sección se cierra "
    "y que el número de página no se duplicó ni se reinició."
)

SALIDA.parent.mkdir(parents=True, exist_ok=True)
d.guardar(SALIDA)
print(f"Generado: {SALIDA}")
print(f"Tablas: {d.n_tabla} · Figuras: {d.n_figura}")
