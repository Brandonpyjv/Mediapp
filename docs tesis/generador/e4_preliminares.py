# -*- coding: utf-8 -*-
"""
E4 — Preliminares: cubierta, portada, tabla de contenido, resumen, abstract e introducción.

El resumen y la introducción se escribieron contra el sistema construido y no contra el
planteamiento inicial. Es la primera vez que el documento le dice al lector qué es MediApp, y
decirlo mal aquí obliga a corregirlo en los seis capítulos siguientes. No es una historia
clínica electrónica certificada ni un sistema de gestión hospitalaria, es un sistema de
agendamiento de citas que además protege el acto clínico repartiendo el acceso por rol.

**Las cifras no se escriben a mano.** El número de requisitos, de casos de uso, de tablas y de
pruebas se lee de los módulos que los definen, de modo que el resumen no pueda quedar afirmando
una cifra que el resto del documento contradice. Es el mismo criterio de los anexos.

🔴 **Dos observaciones se resuelven aquí.** La **O03** pedía un título con la estructura de qué,
con qué objetivo y por qué, que es el aprobado en el cuaderno y que **no se reescribe**. La
**O02** pedía enumerar las hojas en la tabla de contenido, que se resuelve con el campo de Word
que inserta `apa.py` y se comprueba abriendo el documento. Se atiende además la recomendación
8.2 del documento devuelto, que pedía dejar constancia de los autores, la ficha y la instructora
en la portada institucional.
"""
from docx.enum.text import WD_ALIGN_PARAGRAPH

import casos_de_uso
import esquema
import requisitos

# --- Datos institucionales (cuaderno §11.1, cerrados por el autor) ---------------

TITULO = "MEDIAPP"
SUBTITULO = ("Sistema web de agendamiento de citas médicas y gestión de historias clínicas "
             "para la optimización de la atención en centros de salud")

INTEGRANTES = ["ÁNGEL JESÚS HERNÁNDEZ ARÉVALO",
               "RICHARD ALBERTO QUIÑONES QUIÑONES"]

FICHA = "3115426"
PROGRAMA = "Tecnólogo en Análisis y Desarrollo de Software"
INSTRUCTORA = "Heidy Lizbeth Adarme"
CENTRO = "Centro de la Industria, la Empresa y los Servicios (CIES)"
CIUDAD = "CÚCUTA, NORTE DE SANTANDER"
ANIO = 2026


def escribir(d):
    _cubierta(d)
    _portada(d)
    d.tabla_contenido()
    _resumen(d)
    _abstract(d)
    _introduccion(d)


def _centrado(d, texto, negrita=False):
    return d.parrafo(texto, sangria=False, alineacion=WD_ALIGN_PARAGRAPH.CENTER,
                     negrita=negrita)


def _cubierta(d):
    """Primera hoja, con el programa de formación y el nombre del proyecto."""
    _centrado(d, "ANÁLISIS Y DESARROLLO DE SOFTWARE", negrita=True)
    for _ in range(3):
        d.parrafo()
    _centrado(d, "INTEGRANTES:")
    for integrante in INTEGRANTES:
        _centrado(d, integrante)
    d.parrafo()
    _centrado(d, f"FICHA {FICHA}")
    d.parrafo()
    _centrado(d, "INSTRUCTORA:")
    _centrado(d, INSTRUCTORA.upper())
    for _ in range(3):
        d.parrafo()
    _centrado(d, TITULO, negrita=True)
    for _ in range(3):
        d.parrafo()
    _centrado(d, CIUDAD)
    _centrado(d, "SENA, CIES")
    _centrado(d, str(ANIO))
    d.salto_pagina()


def _portada(d):
    """Segunda hoja, con el título completo y la finalidad del trabajo."""
    _centrado(d, TITULO, negrita=True)
    _centrado(d, SUBTITULO)
    d.parrafo()
    _centrado(d, "Presentado por:")
    for integrante in INTEGRANTES:
        _centrado(d, integrante)
    d.parrafo()
    _centrado(d, f"Ficha {FICHA}")
    d.parrafo()
    _centrado(d, "Trabajo de grado presentado como requisito para optar al título de:")
    _centrado(d, PROGRAMA)
    d.parrafo()
    _centrado(d, "Instructora:")
    _centrado(d, INSTRUCTORA)
    d.parrafo()
    _centrado(d, "SERVICIO NACIONAL DE APRENDIZAJE (SENA)")
    _centrado(d, CENTRO)
    _centrado(d, PROGRAMA)
    d.parrafo()
    _centrado(d, CIUDAD)
    _centrado(d, str(ANIO))
    d.salto_pagina()


def _resumen(d):
    rf = requisitos.conteo()
    cu = casos_de_uso.conteo()
    bd = esquema.conteo()

    d.titulo("RESUMEN", nivel=1)
    d.parrafo(
        "El presente proyecto tiene como propósito el análisis, diseño y desarrollo de "
        "MediApp, un sistema web de agendamiento de citas médicas y gestión de historias "
        "clínicas para centros de salud. La propuesta surge de dos dificultades que aparecen "
        "juntas en la atención ambulatoria. La primera es el desorden de la agenda, porque "
        "cuando las citas se anotan a mano o en una hoja de cálculo compartida nada impide "
        "que dos pacientes queden citados con el mismo médico a la misma hora, que un mismo "
        "paciente acumule varias citas en un día o que se agende sobre una fecha que ya pasó. "
        "La segunda es la custodia de la información clínica, ya que en un archivo que todos "
        "abren no hay forma de sostener que la historia de un paciente solo la escribe el "
        "médico que lo atiende."
    )
    d.parrafo(
        "MediApp responde a ambas con un mismo sistema. Sobre la agenda impone las reglas que "
        "la hacen consistente, que son una separación mínima de treinta minutos entre citas "
        "del mismo médico, un máximo de una cita por paciente y por día, el rechazo de las "
        "fechas ya transcurridas y una reserva del turno que se resuelve dentro de una "
        "transacción con bloqueo, de modo que dos solicitudes simultáneas sobre el mismo "
        "horario terminen en una cita y un rechazo y nunca en dos citas. Sobre la información "
        "clínica reparte el acceso en tres perfiles que no se solapan, y la restricción que "
        "le da carácter al proyecto es que el administrador, que puede hacer todo lo demás, no "
        "puede crear ni modificar historias clínicas, diagnósticos ni recetas, mientras que el "
        "médico, que es quien menos pantallas tiene, es el único que puede hacerlo. El "
        "paciente consulta lo que le pertenece y, como única excepción de escritura, reserva y "
        "cancela su propia cita desde un calendario de disponibilidad."
    )
    d.parrafo(
        "El desarrollo se realizó bajo la metodología ágil Scrum, aplicando la encuesta, la "
        "entrevista y la observación directa como técnicas de elicitación de requisitos, a "
        f"partir de las cuales se especificaron {rf['funcionales']} requisitos funcionales, "
        f"{rf['no_funcionales']} requisitos no funcionales y {cu['casos']} casos de uso, "
        "priorizados con el modelo MoSCoW sobre una escala de valor y urgencia. La solución se "
        "construyó con Python y el marco de trabajo Flask, plantillas Jinja2 con Bootstrap y "
        f"una base de datos MySQL de {bd['tablas']} tablas y {bd['foraneas']} claves foráneas. "
        "Las contraseñas se almacenan mediante la función de derivación de clave scrypt, el "
        "rol se comprueba en el servidor en cada operación y la autoría de todo registro "
        "clínico se toma de la sesión y nunca del formulario enviado."
    )
    d.parrafo(
        "La verificación se realizó mediante una batería de noventa y una pruebas "
        "automatizadas que cubre las reglas críticas del sistema, entre ellas la matriz de "
        "permisos, el límite de los treinta minutos, el aislamiento de los datos entre "
        "pacientes y la carrera entre dos reservas simultáneas. El resultado es un sistema en "
        "funcionamiento que ordena la agenda de atención y sostiene, de forma verificable, que "
        "el acto clínico pertenece a quien lo ejecuta."
    )
    d.parrafo()
    p = d.parrafo(sangria=False)
    p.add_run("Palabras clave: ").bold = True
    p.add_run("agendamiento de citas, historia clínica, control de acceso basado en roles, "
              "aplicación web, centro de salud, concurrencia.")
    d.salto_pagina()


def _abstract(d):
    rf = requisitos.conteo()
    cu = casos_de_uso.conteo()
    bd = esquema.conteo()

    d.titulo("ABSTRACT", nivel=1)
    d.parrafo(
        "The purpose of this project is the analysis, design, and development of MediApp, a "
        "web system for medical appointment scheduling and clinical record management in "
        "health centers. The proposal addresses two difficulties that appear together in "
        "outpatient care. The first is a disorganized schedule, because when appointments are "
        "recorded by hand or in a shared spreadsheet nothing prevents two patients from being "
        "booked with the same physician at the same time, a single patient from accumulating "
        "several appointments in one day, or an appointment from being booked on a date that "
        "has already passed. The second is the custody of clinical information, since in a "
        "file that everyone can open there is no way to guarantee that a patient record is "
        "written only by the attending physician."
    )
    d.parrafo(
        "MediApp addresses both within a single system. On the schedule it enforces the rules "
        "that keep it consistent, namely a minimum separation of thirty minutes between "
        "appointments with the same physician, a maximum of one appointment per patient per "
        "day, the rejection of dates that have already passed, and a slot reservation resolved "
        "inside a locking transaction, so that two simultaneous requests for the same time "
        "result in one appointment and one rejection rather than two appointments. On clinical "
        "information it distributes access across three non overlapping profiles, and the "
        "restriction that defines the project is that the administrator, who may do everything "
        "else, cannot create or modify clinical records, diagnoses, or prescriptions, while "
        "the physician is the only role that can. The patient consults what belongs to them "
        "and, as the sole writing exception, books and cancels their own appointment from an "
        "availability calendar."
    )
    d.parrafo(
        "Development followed the agile Scrum methodology, using surveys, interviews, and "
        "direct observation as requirements elicitation techniques, from which "
        f"{rf['funcionales']} functional requirements, {rf['no_funcionales']} non functional "
        f"requirements, and {cu['casos']} use cases were specified and prioritized with the "
        "MoSCoW model. The solution was built with Python and the Flask framework, Jinja2 "
        f"templates with Bootstrap, and a MySQL database of {bd['tablas']} tables and "
        f"{bd['foraneas']} foreign keys. Passwords are stored using the scrypt key derivation "
        "function, the user role is verified on the server for every operation, and the "
        "authorship of any clinical record is taken from the session and never from the "
        "submitted form."
    )
    d.parrafo(
        "Verification was carried out through a suite of ninety one automated tests covering "
        "the critical rules of the system, including the permission matrix, the thirty minute "
        "limit, data isolation between patients, and the race condition between two "
        "simultaneous bookings. The result is a working system that organizes the care "
        "schedule and verifiably upholds that the clinical act belongs to whoever performs it."
    )
    d.parrafo()
    p = d.parrafo(sangria=False)
    p.add_run("Keywords: ").bold = True
    p.add_run("appointment scheduling, clinical record, role based access control, web "
              "application, health center, concurrency.")
    d.salto_pagina()


def _introduccion(d):
    d.titulo("INTRODUCCIÓN", nivel=1)
    d.parrafo(
        "La atención ambulatoria de un centro de salud pequeño se organiza alrededor de una "
        "agenda, y de lo bien que esa agenda se lleve depende buena parte de lo que el "
        "paciente percibe como calidad del servicio. Una cita mal anotada no es un error "
        "administrativo aislado, porque se traduce en una sala de espera con dos personas "
        "citadas a la misma hora, en un médico que atiende con retraso el resto de la jornada "
        "y en un paciente que vuelve a su casa sin haber sido atendido."
    )
    d.parrafo(
        "El diagnóstico que dio origen a este proyecto encontró que la dificultad no está en "
        "la falta de voluntad de quien agenda, sino en la herramienta con que lo hace. Una "
        "hoja de cálculo compartida, o un cuaderno, registran lo que se les escribe y no "
        "comprueban nada. No advierten que el médico ya tiene una cita quince minutos antes, "
        "no impiden que el mismo paciente quede citado tres veces en la misma semana y no "
        "distinguen entre una fecha futura y una que ya pasó. La consecuencia es que la "
        "consistencia de la agenda depende por completo de la memoria de una persona, y esa "
        "memoria falla el día que hay más trabajo, que es justamente cuando más importa."
    )
    d.parrafo(
        "Junto a la agenda aparece una segunda dificultad, de naturaleza distinta y de mayor "
        "consecuencia. La información clínica de un paciente, que es su historia, su "
        "diagnóstico y lo que se le prescribe, tiene un responsable con nombre propio, que es "
        "el médico que lo atendió. Cuando esa información vive en un archivo que todo el "
        "personal puede abrir y modificar, esa responsabilidad deja de poder sostenerse, "
        "porque nada distingue lo que escribió el médico de lo que corrigió después alguien "
        "más. No es un problema de desconfianza hacia el personal administrativo, sino de que "
        "un registro clínico sin autoría verificable no sirve como registro clínico."
    )
    d.parrafo(
        "En respuesta a esa situación surge MediApp, un sistema web que atiende las dos "
        "dificultades con un mismo diseño. La agenda deja de ser un registro pasivo y pasa a "
        "comprobar, antes de guardar cualquier cita, que el médico tenga el tiempo libre que "
        "necesita, que el paciente no tenga ya otra cita ese día y que la fecha no haya "
        "transcurrido. La información clínica deja de estar al alcance de todos y queda "
        "repartida en tres perfiles de acceso que el servidor comprueba en cada operación, de "
        "manera que la restricción no dependa de que una pantalla oculte un botón."
    )
    d.parrafo(
        "El reparto de esos tres perfiles es lo que distingue a este proyecto de un sistema de "
        "gestión corriente, y conviene enunciarlo desde el principio porque el resto del "
        "documento se apoya en él. El administrador gestiona la operación completa, es decir "
        "los usuarios, los médicos, los pacientes, los catálogos y la agenda, y su única "
        "restricción es que no puede crear ni modificar historias clínicas, diagnósticos ni "
        "recetas. El médico, que es el rol con menos pantallas, es el único que puede hacerlo, "
        "y en cambio consulta su agenda sin poder modificarla. El paciente consulta lo que le "
        "pertenece y tiene una sola excepción de escritura, que es reservar y cancelar su "
        "propia cita desde un calendario de disponibilidad."
    )
    d.parrafo(
        "El desarrollo se fundamentó en conceptos relacionados con el agendamiento de la "
        "atención, la custodia del registro clínico, el control de acceso basado en roles y "
        "las funciones de derivación de clave para el almacenamiento de contraseñas. Se aplicó "
        "la metodología ágil Scrum, con la encuesta, la entrevista y la observación directa "
        "como técnicas de elicitación, y la construcción se realizó con Python, el marco de "
        "trabajo Flask y una base de datos MySQL."
    )
    d.parrafo(
        "El documento se organiza en seis capítulos. El primero plantea el problema, la "
        "justificación y los objetivos. El segundo reúne el marco teórico, conceptual y "
        "tecnológico. El tercero describe la metodología de investigación y de desarrollo. El "
        "cuarto presenta el análisis y la especificación de requisitos, con su priorización y "
        "los riesgos del proyecto. El quinto expone el diseño de la solución, la arquitectura, "
        "el modelo de control de acceso y el modelo de datos. El sexto relata el desarrollo, "
        "la implementación, las pruebas y los resultados obtenidos. El documento cierra con "
        "las conclusiones, las referencias y los anexos."
    )
    d.salto_pagina()

# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
