# -*- coding: utf-8 -*-
"""
E6 — Guion de la sustentación de MediApp.

Lo que dice cada expositor en cada una de las 38 diapositivas.

No es un documento académico sino material de trabajo, así que va con interlineado
sencillo para que quepa en pocas hojas y pueda tenerse a mano mientras se ensaya.

**El guion sigue a las diapositivas, no al revés.** Las 38 entradas de abajo están
numeradas contra el archivo que produce `../generar_mediapp_ppt.py`, que a su vez
copia la presentación de FactuGest y escribe encima. Si esa presentación cambia de
orden, este guion queda desalineado, así que `_comprobar_contra_las_diapositivas()`
lo verifica al construir y falla antes de escribir nada.

El reparto sigue los roles declarados en el capítulo 3 del documento de grado
(`e4_cap3.EQUIPO`). Que cada uno hable de lo que le tocó hacer no es solo comodidad,
porque si el jurado pregunta, responde quien lo construyó.

    python e6_guion.py
"""
from pathlib import Path

from docx.shared import Pt

from apa import DocumentoAPA

SALIDA = Path(__file__).resolve().parent.parent / "entregables"
ARCHIVO = SALIDA / "MediApp - Guion de la Sustentacion.docx"
PRESENTACION = Path(__file__).resolve().parent.parent / "exposicion" / "MediApp - Sustentación.pptx"

ANGEL = "Ángel Jesús Hernández Arévalo"
RICHARD = "Richard Alberto Quiñones Quiñones"

REPARTO = [
    (ANGEL, "Product Owner", "1 a 19",
     "Formulación del proyecto y análisis de requisitos", "14 minutos"),
    (RICHARD, "Scrum Master", "20 a 38",
     "Diseño, desarrollo, pruebas y cierre", "16 minutos"),
]

# (número de diapositiva, título, qué se ve, qué decir)
PARTE_ANGEL = [
    (1, "Portada", "El logo de MediApp y los nombres del equipo.",
     "Buenos días. Somos Ángel Hernández y Richard Quiñones, de la ficha 3115426. "
     "Presentamos MediApp, nuestro proyecto de grado. Yo abro con la formulación y el "
     "análisis, y Richard continúa con el diseño, el desarrollo y las pruebas."),

    (2, "MediApp", "El nombre del proyecto y la línea que lo define.",
     "MediApp es un sistema web para agendar citas médicas y manejar historias clínicas. "
     "La diferencia que le da sentido a todo el proyecto es que el paciente elige él mismo "
     "el horario libre y su cita queda en firme en ese momento, sin pasar por la ventanilla "
     "y sin esperar a que un tercero se la confirme."),

    (3, "I. Formulación del proyecto", "Diapositiva divisoria.",
     "Empiezo por el problema que encontramos."),

    (4, "Planteamiento del Problema", "La frase del problema y tres párrafos con cifras.",
     "Conseguir una cita médica hoy depende de dos cosas, de presentarse en el centro de "
     "salud y de la memoria de quien asigna los turnos. De las 48 personas que encuestamos, "
     "26 piden su cita presentándose y 34 se han desplazado solo para pedirla o para "
     "cancelarla. 31 tardan más de media hora en que se la asignen y 29 han recibido al "
     "menos una vez una cita cruzada con la de otro paciente. El problema no es que falte "
     "demanda, es que no hay un canal propio, y como la disponibilidad se recuerda en vez "
     "de consultarse, la ventanilla y el teléfono llegan a ofrecer el mismo turno."),

    (5, "Justificación del Proyecto", "Tres cifras de la encuesta y la frase de cierre.",
     "Estas tres cifras son las que justifican el proyecto. El 71 % se ha desplazado "
     "únicamente para pedir o cancelar una cita, o sea que el viaje no fue para atenderse. "
     "El 65 % espera más de media hora a que se la asignen. Y el 60 % ha sufrido un cruce "
     "de horario, que es un error que no comete el paciente sino el procedimiento manual. "
     "MediApp ataca las tres con una sola solución, que es dejar que el paciente vea la "
     "agenda y reserve en ella."),

    (6, "Objetivo General", "El objetivo completo, centrado.",
     "Nuestro objetivo general es desarrollar MediApp, un sistema web de agendamiento de "
     "citas médicas con acceso diferenciado para administrador, médico y paciente, que "
     "permita gestionar la disponibilidad de la atención médica y controlar el historial "
     "clínico en centros de salud. Los tres roles no son un adorno del enunciado, son la "
     "estructura del sistema."),

    (7, "Objetivos Específicos", "Los tres objetivos numerados.",
     "De ahí salen tres específicos, y son tres y no cinco a propósito. El primero es la "
     "programación de la atención, que es el módulo de agendamiento con su calendario. El "
     "segundo es que el acto clínico sea responsabilidad exclusiva del médico tratante, o "
     "sea la historia clínica, el diagnóstico y la receta. Y el tercero es la "
     "confidencialidad mediante un control de acceso basado en roles. Fíjense en que el "
     "tercero dice «mediante un control de acceso basado en roles» y no dice cifrado, "
     "porque el sistema no cifra, y un objetivo que promete de más no se puede declarar "
     "cumplido."),

    (8, "Alcance", "Dos columnas, lo que hace y lo que queda fuera.",
     "A la izquierda está lo que el sistema hace hoy y funcionando, y a la derecha lo que "
     "dejamos fuera. Lo importante de la columna derecha es que cada exclusión tiene una "
     "razón. La notificación por correo necesita un servicio de envío contratado, el "
     "cifrado depende de dónde se despliegue y no del programa, y la aplicación móvil "
     "sobraría porque la interfaz ya responde en el navegador del teléfono."),

    (9, "Riesgos y Restricciones", "Dos bloques de tres puntos cada uno.",
     "Los riesgos que identificamos son del proyecto y no del software. Que la "
     "documentación se nos acumulara para el final, que quedara alguna observación sin "
     "atender y que el entorno fallara justo hoy. Los tres los atendimos, y el último "
     "ensayando el arranque desde cero y trayendo el volcado de la base. Las restricciones "
     "son las condiciones con las que hay que contar, y la principal es que esto corre "
     "sobre un entorno local con XAMPP y no sobre infraestructura de producción."),

    (10, "Cronograma de Actividades", "El diagrama de Gantt del proyecto.",
     "Este es el cronograma real del proyecto, en cinco fases entre marzo de 2025 y "
     "septiembre de 2026. Es exactamente el mismo diagrama que está en el punto 4.3 del "
     "documento, porque los dos salen del mismo archivo y no pueden discrepar."),

    (11, "II. Análisis", "Diapositiva divisoria.",
     "Paso ahora a cómo levantamos los requisitos."),

    (12, "Herramientas para la Captura de Requisitos",
     "La encuesta y las dos preguntas que decidieron el proyecto.",
     "Usamos tres instrumentos, una encuesta a 48 usuarios de centros de salud de Cúcuta, "
     "una entrevista a un experto del dominio y observación directa en la ventanilla. Lo "
     "que ven proyectado son las dos preguntas que decidieron el proyecto. El 85 % quiere "
     "elegir él mismo el horario libre, y el 81 % quiere que la cita quede agendada de "
     "inmediato. Esas dos preguntas separan querer ver la agenda de querer reservar en "
     "ella, y son cosas distintas."),

    (13, "Historias de Usuario", "Tres historias derivadas de la encuesta.",
     "De la encuesta salieron diecisiete historias de usuario y traje tres. Las dos "
     "primeras son del paciente y recogen justo el hallazgo, ver el calendario y que el "
     "horario elegido quede agendado en el momento. La tercera es del médico y es la "
     "contraparte, porque quien registra la historia clínica deja constancia bajo su propia "
     "autoría."),

    (14, "Requisitos Funcionales Relacionados", "Tabla con cuatro requisitos.",
     "Estos son los cuatro requisitos que salen directamente de esas historias. El "
     "calendario, la reserva por parte del paciente, la separación mínima entre citas y la "
     "exclusividad del médico sobre la historia. Los dos del medio son los que sostienen el "
     "proyecto, y los dos son reglas que se comprueban en el servidor."),

    (15, "Matriz de Stakeholders", "Los cuatro cuadrantes de poder e interés.",
     "Identificamos ocho partes interesadas y las ubicamos por su poder y su interés. En el "
     "cuadrante de involucrar están los pacientes y los médicos, que son quienes usan el "
     "sistema todos los días. El administrador queda ahí también, porque pierde el control "
     "exclusivo de la agenda y hay que explicarle qué gana a cambio."),

    (16, "Técnica de Priorización de Requisitos", "La escala de puntaje de uno a cinco.",
     "Para priorizar puntuamos cada requisito de uno a cinco en dos ejes, el valor para la "
     "atención y la urgencia. El valor pesa 60 % y la urgencia 40 %, o sea que lo importante "
     "manda sobre lo afanado. No es una opinión requisito por requisito, es una regla que se "
     "aplica igual a los 87."),

    (17, "Conclusión General de la Priorización", "Los diez módulos ordenados por puntaje.",
     "Aplicada esa regla, el módulo que encabeza es agendamiento de citas con 4,6, que es "
     "exactamente el problema que el proyecto viene a resolver. Le sigue autenticación y "
     "sesión con 4,5, porque sin los tres roles no hay nada que proteger. Y cierra catálogos "
     "con 3,6, que son las especialidades y los medicamentos, parámetros que se ajustan de "
     "vez en cuando. Que el orden que salió de la fórmula coincida con el orden del problema "
     "es la mejor señal de que la regla estaba bien planteada."),

    (18, "Requisitos Funcionales", "Los diez módulos con sus cifras y el total.",
     "En total son 87 requisitos funcionales repartidos en diez módulos, de los cuales 42 "
     "son críticos. Agendamiento de citas se lleva 14, y once de esos catorce son críticos, "
     "que es la proporción más alta de la tabla. En el reparto MoSCoW son 42 Must, 25 "
     "Should, 20 Could y 8 Won't, y los ocho del final son los que ya vieron en el alcance."),

    (19, "Requisitos No Funcionales", "Las siete categorías con un ejemplo cada una.",
     "Los no funcionales son 24 en siete categorías, y cada uno trae cómo se verifica, que "
     "es lo que evita que sean buenas intenciones. Seguridad es la categoría más poblada con "
     "siete, y el primero de ellos dice que la autoría de un registro clínico se toma de la "
     "sesión y nunca del formulario. Con eso le dejo a Richard el diseño."),
]

PARTE_RICHARD = [
    (20, "III. Diseño", "Diapositiva divisoria.",
     "Gracias. Yo sigo con el diseño de la solución."),

    (21, "Panel del Administrador", "La pantalla real del panel del administrador.",
     "Esta es la pantalla real del sistema, no un boceto. El administrador ve la operación "
     "completa, o sea usuarios, médicos, pacientes, citas, catálogos y laboratorio. Lo que "
     "quiero que noten es lo que no está, y es que en historias clínicas solo tiene el botón "
     "de consultar. No hay crear ni editar, y no es que se los escondamos, es que el "
     "servidor los rechaza."),

    (22, "Calendario de Disponibilidad", "La pantalla que resuelve el problema.",
     "Esta es la pantalla que resuelve el problema. El paciente elige médico y semana y ve "
     "los turnos libres de treinta minutos. Arriba, el aviso explica la regla de la "
     "separación mínima. Y el martes dice que ya tiene cita, que es la segunda regla, la de "
     "una cita por paciente al día. Las dos reglas se ven en una sola imagen, pero las dos "
     "se comprueban en el servidor y no aquí."),

    (23, "Modelo Físico de la Base de Datos", "El esquema leído del motor.",
     "Este modelo no lo dibujamos, lo generamos desde el propio motor MySQL consultando su "
     "catálogo interno, así que es el esquema que está corriendo y no el que quisimos que "
     "hubiera."),

    (24, "Modelo Entidad-Relación", "Las once tablas y sus relaciones.",
     "Son once tablas con 63 columnas y catorce claves foráneas. Tiene dos centros, que son "
     "médico y paciente, y casi todo lo demás cuelga de ellos. Fíjense en que historia, "
     "consulta y receta referencian al médico, y esa columna es la que sostiene la autoría "
     "de la que hablaba Ángel."),

    (25, "Diccionario de Datos", "Las columnas de la tabla paciente.",
     "Este es el diccionario de la tabla paciente. Señalo dos campos. El número de documento "
     "es único, y eso es lo que impide registrar dos veces a la misma persona. Y el estado es "
     "activo o inactivo, porque en este sistema nada se borra, se da de baja lógica. Un "
     "paciente eliminado se llevaría por delante sus historias y sus citas."),

    (26, "Casos de Uso", "El diagrama general con los cuatro actores.",
     "El análisis identificó 60 casos de uso en los diez módulos, con cuatro actores. Uno de "
     "ellos no es una persona, es el propio sistema, y aparece porque las dos reglas de la "
     "agenda se aplican solas, sin que nadie las pida. Entre los casos hay 24 relaciones de "
     "inclusión y dos de extensión."),

    (27, "Documentación de Casos de Uso", "La ficha de reservar una cita.",
     "Esta es la ficha del caso central, reservar una cita desde el calendario. Miren el "
     "paso donde dice que el servidor toma la identidad de la sesión. Eso significa que si "
     "alguien manipula la petición para agendarle una cita a otro paciente, la cita queda "
     "igual a nombre de quien la pidió. Lo probamos enviando el identificador de otra "
     "persona."),

    (28, "Metodología de Desarrollo", "El ciclo de Scrum y los sprints.",
     "Trabajamos con Scrum, en diez sprints de dos semanas, aproximadamente uno por cada "
     "módulo del sistema. Cada sprint cerró con un módulo utilizable y no con un pedazo de "
     "varios, y eso es lo que nos permitió probar de verdad al final de cada iteración."),

    (29, "IV. Desarrollo", "Diapositiva divisoria.",
     "Paso a con qué lo construimos."),

    (30, "Herramientas de Backend, Base de Datos y Web",
     "Tabla con el lenguaje, la base, la web y el entorno.",
     "Del lado del servidor usamos Python con Flask. Elegimos Flask porque no impone una "
     "estructura, y en un sistema cuyo valor está en las reglas de permiso queríamos que "
     "esas reglas estuvieran escritas y a la vista, no escondidas dentro de un framework. La "
     "base es MariaDB, compatible con MySQL, con acceso mediante consultas SQL explícitas. Y "
     "la interfaz son plantillas Jinja2 con Bootstrap 5."),

    (31, "Herramientas de Apoyo, Pruebas y Control de Versiones",
     "Claude, Git y GitHub, y pytest.",
     "Como apoyo usamos Claude para revisar código y contrastar decisiones de diseño, Git y "
     "GitHub para el trabajo en equipo, y pytest para las pruebas automatizadas, que corren "
     "en menos de siete segundos y por eso las corríamos todo el tiempo."),

    (32, "V. Implementación", "Diapositiva divisoria.",
     "Y termino con las pruebas y los resultados."),

    (33, "Pruebas del Sistema", "Qué se comprueba y qué quedó fuera.",
     "Tenemos 91 pruebas automatizadas que corren en 6,9 segundos, repartidas en seis "
     "archivos. Fíjense en qué se comprueba, porque los cuatro puntos son rechazos y no "
     "altas. Que la separación mínima se aplique en el servidor y no solo en el calendario, "
     "que de dos reservas simultáneas del mismo turno quede una sola, que la autoría salga de "
     "la sesión, y que cada rol no pueda hacer lo que no le corresponde. En un sistema cuyo "
     "valor está en lo que impide, probar que algo se guarda es lo fácil."),

    (34, "Evidencia de Pruebas, historia clínica", "Formulario y resultado del registro.",
     "A la izquierda el médico diligencia la historia clínica, y arriba se lee que el "
     "registro quedará creado a su nombre como médico tratante. A la derecha ya está "
     "guardada, y en la columna del médico aparece él. Esa misma pantalla, vista con sesión "
     "de administrador, no tiene el botón de agregar."),

    (35, "Evidencia de Pruebas, separación mínima", "Formulario y el rechazo del servidor.",
     "Esta es la prueba central. A la izquierda intentamos agendar una cita a quince minutos "
     "de otra del mismo médico. A la derecha el servidor la rechaza. Y quiero ser preciso con "
     "algo. Esta regla no se puede poner como restricción de la base de datos, porque una "
     "restricción única prohíbe un valor repetido y esto no es un valor repetido, es una "
     "distancia entre dos valores. Por eso se comprueba en el servidor, dentro de la misma "
     "operación que escribe."),

    (36, "Resultado Obtenido de la Reserva", "Tabla con los cinco puntos comprobados.",
     "La prueba de la reserva fue satisfactoria en los cinco puntos. Quiero detenerme en el "
     "de concurrencia. Si dos pacientes piden el mismo turno al mismo tiempo, el navegador no "
     "puede resolverlo, porque los dos vieron el turno libre. Se resuelve en el servidor con "
     "una reserva atómica, y de las dos peticiones solo una queda en firme. Es la única forma "
     "de sostener el criterio de que gana quien llega primero."),

    (37, "Resultados Obtenidos", "Tabla de cumplimiento de los objetivos.",
     "Los tres objetivos específicos se cumplieron y cada uno tiene detrás la evidencia que "
     "lo sostiene. La última fila es la que dejamos declarada como fuera de alcance, que es "
     "el cifrado de la información en reposo, y es la razón por la que el tercer objetivo se "
     "acotó desde el principio al control de acceso por roles."),

    (38, "Cierre", "La diapositiva de agradecimiento.",
     "Con eso terminamos. La conclusión que nos llevamos es que en un sistema cuyo valor está "
     "en lo que impide, la verificación manual no alcanza, porque un control que deja de "
     "aplicarse no produce ningún error visible. Muchas gracias por su atención y quedamos "
     "atentos a sus preguntas."),
]

PREGUNTAS = [
    ("¿Por qué el paciente puede agendar sin que nadie le apruebe la cita?",
     "Porque el 81 % de los encuestados lo pidió así, y porque una solicitud que espera "
     "confirmación conserva la demora que la herramienta viene a quitar. El control no "
     "desaparece, se traslada, ya que el administrador puede cancelar o reprogramar "
     "cualquier cita. Y la delegación tiene un límite, porque el paciente solo reserva para "
     "sí mismo, dado que su identidad sale de la sesión.", "Ángel"),

    ("¿Por qué usaron scrypt y no bcrypt?",
     "Las dos están admitidas por las recomendaciones vigentes de seguridad en aplicaciones "
     "web. La diferencia es que scrypt exige además una cantidad configurable de memoria "
     "durante el cálculo, y la memoria es cara de multiplicar en el hardware especializado "
     "con el que se prueban contraseñas en paralelo. No es que una sea más sólida que la "
     "otra, es que tienen propiedades distintas frente a ese atacante.", "Richard"),

    ("¿Por qué la separación de treinta minutos no es una restricción de la base de datos?",
     "Porque una restricción única prohíbe un valor repetido, y esto no es un valor repetido "
     "sino una distancia entre dos valores. La base no puede expresar que no haya otra cita a "
     "menos de treinta minutos, así que se comprueba en el servidor dentro de la misma "
     "operación que escribe.", "Richard"),

    ("¿Qué pasa si dos pacientes piden el mismo turno al mismo tiempo?",
     "Se resuelve en el servidor con una reserva atómica. Los dos ven el turno libre en el "
     "navegador, pero solo una de las dos peticiones queda en firme. Hay una prueba "
     "automatizada dedicada a ese caso.", "Richard"),

    ("¿El administrador puede escribir en una historia clínica?",
     "No, y no es que le escondamos el botón. Si envía la petición directamente, el servidor "
     "la rechaza. Es la única restricción que tiene el administrador en todo el sistema, y "
     "está probada.", "Ángel"),

    ("¿Por qué el médico no puede agendar sus propias citas?",
     "Porque en el centro de salud el médico recibe su agenda ya construida, no la arma él. "
     "Nos lo dijo el experto del dominio en la entrevista y lo respetamos en el modelo de "
     "permisos, así que su agenda es de solo lectura.", "Ángel"),

    ("¿Por qué son tres objetivos específicos y no cinco?",
     "Porque están redactados como resultados y no como actividades. Cada uno se puede "
     "declarar cumplido o no cumplido con una evidencia detrás, y eso es justamente lo que "
     "muestra la penúltima diapositiva.", "Ángel"),

    ("¿Por qué el tercer objetivo no habla de cifrado?",
     "Porque el sistema no cifra. El cifrado depende de la infraestructura de despliegue y no "
     "del programa, así que lo declaramos fuera de alcance desde el principio. Un objetivo "
     "que promete de más no se puede declarar cumplido.", "Richard"),

    ("¿Qué tipo de pruebas hicieron?",
     "91 pruebas automatizadas con pytest en seis archivos, que cubren autenticación, "
     "permisos, agenda, concurrencia y datos, más pruebas funcionales sobre la interfaz, de "
     "las que tenemos las capturas de antes y después.", "Richard"),

    ("¿Por qué nada se borra del sistema?",
     "Porque un registro borrado se lleva por delante lo que cuelga de él. Un paciente "
     "eliminado se llevaría sus historias y sus citas, que son el historial del centro. Por "
     "eso la baja es lógica, con un campo de estado que permite además reactivarlo.", "Ángel"),
]


def _comprobar_contra_las_diapositivas():
    """El guion tiene que cubrir las 38 diapositivas, una por una y sin huecos.

    Se comprueba contra el `.pptx` si está a mano, porque un guion numerado que no
    corresponde con la presentación es peor que no tenerlo: el expositor lee la
    entrada equivocada delante del jurado.
    """
    numeros = [n for n, *_ in PARTE_ANGEL + PARTE_RICHARD]
    if numeros != list(range(1, len(numeros) + 1)):
        raise AssertionError(f"El guion salta o repite diapositivas: {numeros}")

    if PRESENTACION.exists():
        from pptx import Presentation
        total = len(Presentation(str(PRESENTACION)).slides)
        if total != len(numeros):
            raise AssertionError(
                f"El guion cubre {len(numeros)} diapositivas y la presentación tiene "
                f"{total}. Corregir el guion o revisar generar_mediapp_ppt.py.")
    return len(numeros)


def construir():
    total = _comprobar_contra_las_diapositivas()

    d = DocumentoAPA()
    for nombre in ("Normal", "Heading 1", "Heading 2", "Heading 3"):
        d.doc.styles[nombre].paragraph_format.line_spacing = 1.15
    # Con interlineado sencillo los títulos quedan pegados al párrafo anterior y la
    # hoja se lee como un bloque único.
    for nombre in ("Heading 1", "Heading 2", "Heading 3"):
        d.doc.styles[nombre].paragraph_format.space_before = Pt(14)
        d.doc.styles[nombre].paragraph_format.space_after = Pt(4)

    d.portada(
        titulo="MEDIAPP",
        subtitulo="Guion de la sustentación",
        integrantes=[ANGEL, RICHARD],
        grado="Ficha 3115426\nTecnólogo en Análisis y Desarrollo de Software",
        institucion=["SERVICIO NACIONAL DE APRENDIZAJE (SENA)",
                     "Centro de la Industria, la Empresa y los Servicios (CIES)"],
        ciudad="CÚCUTA, NORTE DE SANTANDER",
        anio=2026,
    )

    _como_usarla(d)
    _reparto(d, total)
    _antes(d)
    _guion(d, ANGEL, "Formulación del proyecto y análisis de requisitos", PARTE_ANGEL)
    _guion(d, RICHARD, "Diseño, desarrollo, pruebas y cierre", PARTE_RICHARD)
    _preguntas(d)
    _ensayo(d)
    _compactar(d)

    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d, total


def _compactar(d):
    """Interlineado sencillo en todo el documento.

    `vinetas()` y `numerada()` fijan el interlineado doble del instructivo, que aquí
    estorba, porque esto se lee de reojo mientras se habla y no se entrega al jurado.
    """
    for parrafo in d.doc.paragraphs:
        parrafo.paragraph_format.line_spacing = 1.15


def _como_usarla(d):
    d.titulo("Cómo usar esta guía", nivel=1)
    d.parrafo(
        "Cada diapositiva trae dos cosas, lo que el jurado ve en pantalla y lo que conviene "
        "decir mientras la ve. El texto de «qué decir» está escrito para hablarse, no para "
        "leerse en voz alta. Léanlo varias veces hasta que sea suyo y después díganlo con "
        "sus palabras.", interlineado=1.15)
    d.parrafo(
        "Las diapositivas no se leen. Todo lo que está proyectado el jurado ya lo puede leer "
        "solo, así que quien expone aporta lo que no está escrito, que es el porqué de cada "
        "decisión.", interlineado=1.15)
    d.parrafo(
        "Al final hay diez preguntas probables con su respuesta y con el nombre de quién "
        "debería contestarlas. Conviene que las dos personas las conozcan, porque el jurado "
        "pregunta a quien quiera.", interlineado=1.15)


def _reparto(d, total):
    d.titulo("Reparto de la exposición", nivel=1)
    d.tabla(
        "Quién expone cada parte",
        ["Expositor", "Rol en el proyecto", "Diapositivas", "Contenido", "Tiempo"],
        [[nombre, rol, diapositivas, contenido, tiempo]
         for nombre, rol, diapositivas, contenido, tiempo in REPARTO],
        nota="El reparto sigue los roles declarados en el capítulo 3 del documento. Cada uno "
             "expone lo que le tocó construir, de modo que si el jurado pregunta, responde "
             "quien lo hizo.",
        anchos=[4.1, 2.2, 2.4, 5.2, 2.1],
    )
    d.parrafo(
        f"El total son treinta minutos de exposición para las {total} diapositivas. Si les "
        "dan menos tiempo, lo primero que se recorta son la 13, la 15 y la 16, que son las "
        "historias de usuario, los interesados y la escala de priorización, y cada bloque se "
        "puede resumir en una frase. Lo que no se puede recortar es la 12, que es donde está "
        "el hallazgo de la encuesta, ni la 35, que es la evidencia de que la regla de negocio "
        "se aplica de verdad.", interlineado=1.15)


def _antes(d):
    d.titulo("Antes de empezar", nivel=1)
    d.vinetas([
        "Abran la presentación desde el archivo y no desde el PDF, para que la numeración y "
        "las transiciones funcionen.",
        "Tengan el documento de grado impreso o abierto a mano. Si preguntan por un dato, es "
        "más sólido mostrarlo que recordarlo.",
        "Si van a mostrar el sistema en vivo, déjenlo arrancado antes de entrar y tengan a "
        "mano las capturas por si el entorno falla.",
        "Repártanse quién maneja el computador. Quien expone no debería estar pasando "
        "diapositivas.",
        "Hablen de «nosotros» cuando se refieran al proyecto y de «yo» cuando se refieran a "
        "lo que cada uno hizo.",
    ])


def _guion(d, expositor, parte, diapositivas):
    partes = expositor.split()
    d.titulo(f"Guion de {partes[0]} {partes[2]}", nivel=1, nueva_pagina=True)
    d.parrafo(f"{parte}. Diapositivas {diapositivas[0][0]} a {diapositivas[-1][0]}.",
              sangria=False, cursiva=True, interlineado=1.15)
    d.parrafo()
    for numero, titulo, pantalla, texto in diapositivas:
        d.titulo(f"Diapositiva {numero}. {titulo}", nivel=3)
        p = d.parrafo(sangria=False, interlineado=1.15)
        p.add_run("En pantalla. ").bold = True
        p.add_run(pantalla)
        p = d.parrafo(sangria=False, interlineado=1.15)
        p.add_run("Qué decir. ").bold = True
        p.add_run(texto)
        d.parrafo()


def _preguntas(d):
    d.titulo("Preguntas probables del jurado", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Estas son las preguntas que más probablemente van a hacer, con una respuesta "
        "preparada. La columna de la derecha sugiere quién debería responder, pero si "
        "preguntan al otro, que responda igual y luego el responsable complementa.",
        interlineado=1.15)
    d.tabla(
        "Preguntas frecuentes y respuestas preparadas",
        ["Pregunta", "Respuesta", "Responde"],
        [[pregunta, respuesta, quien] for pregunta, respuesta, quien in PREGUNTAS],
        nota="Elaboración propia.",
        anchos=[4.2, 9.9, 1.9],
    )
    d.parrafo(
        "Si preguntan algo que no saben, la respuesta es decirlo. «No lo verificamos» o «eso "
        "quedó fuera del alcance y está declarado en el documento» son respuestas válidas y "
        "mucho mejores que inventar una cifra.", interlineado=1.15)


def _ensayo(d):
    d.titulo("Lista de verificación para el ensayo", nivel=1, nueva_pagina=True)
    d.numerada([
        "Cronometrar cada bloque por separado. Si alguno se pasa de su tiempo, recortar del "
        "guion, no hablar más rápido.",
        "Ensayar el empalme, que es la diapositiva 19. Con dos expositores hay un solo "
        "cambio, y por eso tiene que salir limpio.",
        "Repasar en voz alta las cifras que se dicen, o sea 48 encuestados, 85 %, 81 %, 87 "
        "requisitos, 42 críticos, 60 casos de uso, 11 tablas y 91 pruebas. Son las que el "
        "jurado puede contrastar con el documento.",
        "Comprobar que los dos puedan explicar por qué la separación de treinta minutos se "
        "resuelve en el servidor y no con una restricción de la base. Es la pregunta técnica "
        "más probable.",
        "Tener lista la demostración del calendario, con el volcado de la base cargado y un "
        "paciente que ya tenga cita, porque es lo que hace visible la segunda regla.",
        "Revisar que el computador proyecte en 16:9 y que el verde institucional de las "
        "divisorias no queme en el proyector.",
    ])


if __name__ == "__main__":
    documento, total = construir()
    print(f"Generado: {ARCHIVO}")
    print(f"Diapositivas cubiertas: {total}")
    print(f"Expositores: {len(REPARTO)}  Preguntas preparadas: {len(PREGUNTAS)}")
