# -*- coding: utf-8 -*-
"""
E4 — Capítulo 3. Metodología de investigación y desarrollo.

Los diez sprints están alineados con el cronograma del capítulo 4, que es la misma figura
`FIG-cronograma.png` y sitúa la fase de ejecución entre noviembre de 2025 y marzo de 2026, con
diez iteraciones de dos semanas. Si uno de los dos cambia, el otro tiene que cambiar con él,
porque un documento que dice que las prescripciones se hicieron en el sprint 9 y en el
cronograma las pone antes que las consultas se contradice a sí mismo.

Las cifras de la encuesta no se escriben aquí. Salen de `encuesta.py`, que es donde viven los
datos y de donde se dibujan también las dos figuras, de manera que el análisis y las gráficas no
puedan discrepar.

Los módulos y el número de requisitos por módulo se leen de `requisitos.py`, por la misma razón:
el reparto del product backlog en sprints es una vista del catálogo y no una lista aparte.
"""
from pathlib import Path

import encuesta
import requisitos
from e4_cap2 import cita

IMAGENES = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"


def _n(cantidad):
    """«34 (71 %)», el número y su porcentaje, calculados siempre sobre la muestra."""
    return f"{cantidad} ({encuesta.porcentaje(cantidad)} %)"


def _modulo(codigo):
    """El nombre y el número de requisitos de un módulo del catálogo."""
    for clave, nombre, _descripcion, _porque, lista in requisitos.MODULOS:
        if clave == codigo:
            return nombre, len(lista)
    raise KeyError(codigo)


# El orden de los sprints es el de las dependencias técnicas, no el de la prioridad.
# (número, código del módulo, alcance comprometido)
SPRINTS = [
    ("Sprint 1", "RF 1",
     "Ingreso con credenciales, derivación de la contraseña, roles, protección de las rutas "
     "por sesión, redirección automática al panel del rol y registro público del paciente."),
    ("Sprint 2", "RF 2",
     "Alta, edición, baja lógica y reactivación de las cuentas de acceso, con su rol asignado "
     "y el bloqueo del nombre de usuario repetido."),
    ("Sprint 3", "RF 10",
     "Catálogo de especialidades y catálogo de medicamentos, que son los dos que el resto de "
     "los módulos consulta."),
    ("Sprint 4", "RF 3",
     "Ficha profesional del médico, su especialidad, el vínculo con la cuenta con la que "
     "ingresa, su baja lógica y el control independiente de su acceso."),
    ("Sprint 5", "RF 4",
     "Datos personales y de contacto del paciente, su vínculo con la cuenta con la que "
     "consulta lo suyo y el bloqueo del documento repetido."),
    ("Sprint 6", "RF 5",
     "Calendario semanal de disponibilidad, agendamiento por el administrador y por el propio "
     "paciente, separación mínima entre atenciones, una cita por paciente y por día, "
     "reprogramación y cancelación."),
    ("Sprint 7", "RF 6",
     "Registro de la historia clínica bajo la autoría del médico tratante, su edición, su "
     "eliminación y la consulta de solo lectura para el administrador y para el paciente."),
    # 🔴 Decía «su vínculo con la cita y con el paciente atendido», y el esquema no tiene esa
    # columna: `consulta` referencia a `paciente` y a `medico`, no a `cita`.
    ("Sprint 8", "RF 7",
     "Diagnóstico posterior a la atención, plan de tratamiento, autoría del médico tomada de "
     "la sesión y vínculo con el paciente atendido."),
    ("Sprint 9", "RF 8",
     "Prescripción de medicamentos con su dosis y su frecuencia, tomados del catálogo, y su "
     "vínculo con la consulta que la origina."),
    ("Sprint 10", "RF 9",
     "Registro de los exámenes de laboratorio y de sus resultados por parte del "
     "administrador, y su consulta por el paciente y por el médico."),
]

PREGUNTAS = [
    ("1", "¿De qué manera solicita usted una cita médica actualmente?",
     "Presencialmente en el centro / Por teléfono / Por mensajería instantánea / Por una "
     "página web o aplicación"),
    ("2", "Desde que la solicita, ¿cuánto tiempo le toma que le asignen la cita?",
     "Menos de 10 minutos / De 10 a 30 minutos / De 30 minutos a una hora / Más de una hora"),
    ("3", "¿En qué momento puede solicitar su cita?",
     "Solo en el horario de atención del centro / A cualquier hora"),
    ("4", "¿Le ha ocurrido que la cita asignada se cruce con la de otro paciente o que el "
          "médico no esté disponible a esa hora?",
     "Nunca / Una vez / Varias veces"),
    ("5", "¿Ha tenido que desplazarse hasta el centro de salud únicamente para solicitar o "
          "cancelar una cita?", "Sí / No"),
    ("6", "Cuando ha necesitado cancelar una cita, ¿pudo hacerlo sin ir al centro?",
     "Sí / No, tuve que ir / No he necesitado cancelar"),
    ("7", "¿Le gustaría consultar los horarios libres de cada médico y elegir usted mismo el "
          "que le convenga?", "Sí / No / Tal vez"),
    ("8", "Al solicitar una cita, ¿preferiría que quedara agendada de inmediato o pendiente "
          "de aprobación?",
     "Agendada de inmediato / Pendiente de aprobación / Me es indiferente"),
    ("9", "¿Le gustaría consultar en línea su historial de consultas y sus fórmulas médicas?",
     "Sí / No / Tal vez"),
    ("10", "¿Qué importancia le da a que únicamente el médico que lo atiende pueda escribir "
           "en su historia clínica?", "Escala de 1 a 5"),
    ("11", "¿Le preocupa que personal no médico pueda leer o modificar su historia clínica?",
     "Sí / No / No lo había pensado"),
    ("12", "¿Dispone de un teléfono o de un computador con acceso a internet?", "Sí / No"),
]

EQUIPO = [
    ("Ángel Jesús Hernández Arévalo", "Product Owner y desarrollador",
     "Definió y priorizó el product backlog, condujo la elicitación de requisitos y el "
     "modelado de los casos de uso, y decidió el alcance comprometido en cada sprint."),
    ("Richard Alberto Quiñones Quiñones", "Scrum Master y desarrollador",
     "Facilitó la planificación de las iteraciones y el seguimiento de los impedimentos, y "
     "coordinó la integración de los módulos y la ejecución de las pruebas."),
]

INTERESADOS = [
    ("Pacientes de los centros de salud",
     "Usuarios finales del agendamiento. De que consigan una cita sin desplazarse y sin "
     "intermediarios depende que la solución resuelva el problema planteado."),
    ("Médicos y profesionales de la salud",
     "Titulares del acto clínico. Necesitan ver su agenda y ser los únicos que puedan escribir "
     "en la historia, en el diagnóstico y en la prescripción."),
    ("Personal administrativo del centro",
     "Opera el sistema todos los días, ya que gestiona las personas, los catálogos, el "
     "laboratorio y la agenda completa. Es quien más pantallas utiliza."),
    ("Dirección del centro de salud",
     "Responde por el cumplimiento de la reserva de la historia clínica y decide la adopción "
     "de la herramienta."),
    ("Experto del dominio clínico",
     "Aportó las reglas de la atención que el sistema debía respetar y validó que lo "
     "construido correspondiera con la práctica real."),
    ("Equipo de desarrollo",
     "Responsable del análisis, la construcción y las pruebas de la solución."),
    ("Centro de formación, instructora y evaluadores",
     "Orientan el desarrollo del proyecto y evalúan su cumplimiento como trabajo de grado."),
]


def escribir(d):
    d.titulo("Capítulo 3. Metodología de investigación y desarrollo", nivel=1,
             nueva_pagina=True)
    _scrum(d)
    _backlog(d)
    _elicitacion(d)
    _tecnicas(d)
    _analisis(d)
    _equipo(d)


# --- 3.1 -----------------------------------------------------------------------

def _scrum(d):
    d.titulo("3.1 Metodología de desarrollo Scrum", nivel=2)
    d.parrafo(
        "Scrum es un marco de trabajo ágil para el desarrollo de productos complejos, basado "
        "en iteraciones cortas de duración fija llamadas sprints, al término de cada una de "
        f"las cuales se entrega un incremento utilizable del producto ({cita('scrum')}). Su "
        "estructura se apoya en tres artefactos, que son el product backlog, el sprint backlog "
        "y el incremento, y en eventos de planificación, seguimiento diario, revisión y "
        "retrospectiva."
    )
    d.parrafo(
        "La elección de Scrum para este proyecto no respondió únicamente a su difusión, sino a "
        "una condición del problema, y es que la regla que gobierna una atención médica no se "
        "conoce entera antes de construirla. Cuestiones como cuánto tiempo debe mediar entre "
        "dos atenciones del mismo profesional, si un paciente puede tener dos citas el mismo "
        "día o quién puede corregir una cita ya programada no aparecen en un enunciado inicial "
        "de requisitos, aparecen cuando alguien intenta agendar y el sistema se lo permite. Un "
        "marco de trabajo que exigiera fijar la totalidad de las reglas antes de escribir la "
        "primera línea habría obligado a comprometerse con supuestos que la práctica desmiente."
    )
    d.parrafo(
        "El proyecto lo confirmó con la regla que hoy más lo define. El agendamiento se "
        "concibió como una responsabilidad exclusiva del personal administrativo, y así se "
        "construyó el sprint correspondiente. Al contrastarlo con lo que la elicitación había "
        "mostrado, quedó claro que obligar al paciente a tramitar su cita con un tercero "
        "reproducía dentro del sistema la misma demora que el sistema venía a eliminar, y la "
        "regla cambió para que el paciente reserve directamente sobre el calendario de "
        "disponibilidad. El cambio se incorporó reordenando el product backlog, porque lo "
        "construido siguió siendo válido, ya que las comprobaciones de conflicto, el "
        "calendario y la reserva son las mismas venga la petición de donde venga, y lo que "
        "cambió fue quién está autorizado a hacerla. Con un enfoque secuencial, el mismo "
        "hallazgo aparecido a mitad de la construcción habría obligado a rehacer el análisis "
        "completo."
    )
    d.figura(
        "Ciclo de Scrum aplicado al desarrollo de MediApp",
        IMAGENES / "FIG-scrum.png",
        nota="Elaboración propia con base en Schwaber y Sutherland (2020). Los sprints "
             "tuvieron una duración de dos semanas y cada uno cerró con un módulo utilizable.",
    )
    d.parrafo(
        "Se definieron diez sprints de dos semanas durante la fase de ejecución, comprendida "
        "entre noviembre de 2025 y marzo de 2026 según el cronograma que se detalla en el "
        "capítulo siguiente. Cada uno se orientó a dejar un módulo en funcionamiento y no una "
        "porción de varios, ya que un módulo terminado puede mostrarse, probarse y corregirse, "
        "mientras que tres módulos a medias solo pueden describirse."
    )


# --- 3.2 -----------------------------------------------------------------------

def _backlog(d):
    conteo = requisitos.conteo()
    d.titulo("3.2 Product backlog", nivel=2)
    d.parrafo(
        f"El product backlog se conformó con las funcionalidades identificadas durante la "
        f"elicitación, organizadas en los {conteo['modulos']} módulos funcionales del sistema y "
        f"priorizadas según su valor para la atención y su urgencia, criterio que se detalla en "
        f"el capítulo siguiente. La lista completa comprende {conteo['funcionales']} requisitos "
        f"funcionales."
    )
    d.parrafo(
        "El orden de los sprints no siguió la prioridad de los requisitos sino sus "
        "dependencias técnicas, que son dos cosas distintas. El agendamiento "
        "es el módulo de mayor prioridad del proyecto, porque es su razón de ser, y aun así se "
        "construyó en sexto lugar, ya que una cita relaciona a un médico con un paciente y "
        "ninguno de los dos existe mientras no estén sus módulos. Por la misma razón los "
        "catálogos de especialidades y de medicamentos, que son los requisitos de menor "
        "prioridad del conjunto, se adelantaron al tercer sprint, pues sin especialidad no se "
        "puede registrar un médico y sin catálogo de medicamentos no se puede prescribir. Los "
        "tres módulos del acto clínico se dejaron para el final en el orden en que la atención "
        "los produce, esto es, la historia clínica del paciente, el diagnóstico de la consulta "
        "y la prescripción que se deriva de ese diagnóstico."
    )
    filas = []
    for numero, codigo, alcance in SPRINTS:
        nombre, cantidad = _modulo(codigo)
        filas.append([numero, nombre, alcance, f"{codigo} ({cantidad})"])
    d.tabla(
        "Organización del product backlog en sprints",
        ["Sprint", "Módulo", "Alcance comprometido", "Requisitos"],
        filas,
        nota="Elaboración propia. La columna «Requisitos» remite al módulo del catálogo "
             "especificado en el capítulo 4 e indica entre paréntesis cuántos requisitos "
             "funcionales comprende.",
        anchos=[1.9, 3.3, 8.9, 2.2],
    )


# --- 3.3 -----------------------------------------------------------------------

def _elicitacion(d):
    # Sin salto de página a propósito. La tabla de los sprints termina a media página 28 y un
    # salto aquí dejaría dos tercios de esa página en blanco; 3.4 sí abre página, que es donde
    # de verdad empieza el material de la elicitación.
    d.titulo("3.3 Elicitación de requisitos", nivel=2)
    d.parrafo(
        "La elicitación de requisitos es la etapa en la que se identifican, comprenden y "
        "documentan las necesidades de los usuarios y las expectativas de los interesados. De "
        "su calidad depende que el sistema resuelva un problema real y no uno supuesto, ya que "
        "un error introducido aquí se propaga al diseño, a la construcción y a las pruebas, y "
        f"resulta más costoso de corregir en cada etapa que atraviesa ({cita('sommerville')})."
    )
    d.parrafo(
        "En este proyecto la elicitación debía responder dos preguntas que no se dejan "
        "contestar por la misma persona. La primera es por qué conseguir una cita cuesta lo "
        "que cuesta, y solo puede responderla quien la pide. La segunda es qué reglas debe "
        "respetar una agenda clínica para que la atención sea posible, y solo puede "
        "responderla quien atiende. Preguntar únicamente a los pacientes habría producido una "
        "aplicación cómoda que programa atenciones imposibles de cumplir, y preguntar "
        "únicamente al personal clínico habría producido un registro correcto que nadie usa."
    )
    d.parrafo(
        "Se emplearon en consecuencia tres técnicas complementarias. La encuesta sirvió para "
        "conocer la situación de un conjunto amplio de usuarios, la entrevista al experto del "
        "dominio para incorporar las reglas de la práctica clínica y la observación directa "
        "para ver cómo se administra hoy una agenda. La primera indica qué tan extendido está "
        "un problema, la segunda qué condiciones no pueden negociarse y la tercera por qué el "
        "problema ocurre."
    )


# --- 3.4 -----------------------------------------------------------------------

def _tecnicas(d):
    d.titulo("3.4 Técnicas de elicitación utilizadas", nivel=2, nueva_pagina=True)

    d.titulo("3.4.1 Encuesta", nivel=3)
    d.parrafo(
        "Se diseñó un cuestionario dirigido a personas que solicitan atención en centros de "
        "salud, con el propósito de establecer de qué manera consiguen hoy una cita, qué les "
        "cuesta conseguirla, qué inconvenientes han tenido con la programación y qué "
        "esperarían de una herramienta que las atendiera."
    )
    d.parrafo(
        "El instrumento consta de doce preguntas de respuesta cerrada, agrupadas en cuatro "
        "bloques, que son la forma actual de solicitar la cita, los inconvenientes sufridos "
        "con la programación, la disposición frente a un agendamiento en línea y la "
        "expectativa sobre la reserva de la información clínica. Las preguntas 7 y 8 son "
        "deliberadamente complementarias, porque la primera indaga si el usuario querría "
        "elegir por sí mismo el horario y la segunda si querría que esa elección quedara en "
        "firme de inmediato o sujeta a la aprobación de un tercero. Contrastar ambas "
        "respuestas es lo que permite distinguir la comodidad de consultar la agenda de la "
        "autonomía para reservar en ella, que son cosas distintas y conducen a soluciones "
        "distintas."
    )
    d.tabla(
        "Instrumento de encuesta aplicado",
        ["N.º", "Pregunta", "Opciones de respuesta"],
        [[n, p, o] for n, p, o in PREGUNTAS],
        nota="Elaboración propia. Cuestionario de respuesta cerrada, diligenciado en "
             "formulario digital.",
        anchos=[1.2, 8.4, 6.7],
    )
    d.parrafo(
        f"El instrumento se aplicó a {encuesta.MUESTRA} personas residentes en Cúcuta que "
        "habían solicitado al menos una cita médica durante el año anterior, seleccionadas por "
        "conveniencia a la salida de centros de atención ambulatoria. El cuestionario se "
        "diligenció en formulario digital y las respuestas se recogieron durante la fase de "
        "análisis del proyecto."
    )
    d.figura(
        "Formulario digital empleado para la aplicación de la encuesta",
        IMAGENES / "FIG-encuesta-formulario.png",
        nota="Elaboración propia. Se muestran las preguntas 1, 2, 4, 5, 7 y 8; las restantes "
             "continúan en la segunda página del formulario.",
    )
    d.figura(
        "Resultados de la encuesta aplicada",
        IMAGENES / "FIG-encuesta-resultados.png",
        nota=f"Elaboración propia. Distribución de respuestas sobre {encuesta.MUESTRA} "
             "personas encuestadas. En cada gráfica se destaca la opción más relevante para "
             "el diagnóstico.",
    )

    d.titulo("3.4.2 Entrevista al experto del dominio", nivel=3)
    d.parrafo(
        "Se realizó una entrevista semiestructurada a un profesional con experiencia en "
        "consulta externa, orientada a establecer qué condiciones debe cumplir una agenda "
        "clínica para que la atención pueda prestarse y quién puede intervenir cada registro "
        "que la atención produce. La técnica se eligió porque estas reglas no se observan "
        "desde el mostrador ni se deducen de una encuesta, ya que son criterios profesionales "
        "y en parte obligaciones normativas."
    )
    d.parrafo(
        "La entrevista dejó cuatro condiciones que el sistema tenía que respetar. La primera "
        "es que una consulta ambulatoria ocupa alrededor de media hora entre la atención y el "
        "registro de lo atendido, de modo que una agenda que admita dos citas del mismo "
        "profesional dentro de esa franja está programando una atención que no se va a "
        "cumplir, y el retraso se acumula sobre los pacientes siguientes. La segunda es que el "
        "profesional no arma su propia agenda ni la corrige, sino que la recibe, y lo que "
        "necesita del sistema es verla con antelación. La tercera es que la historia clínica "
        "es un documento sometido a reserva cuyo diligenciamiento corresponde a quien "
        f"interviene directamente en la atención ({cita('res1995')}), de manera que un "
        "registro clínico modificado por personal administrativo compromete al profesional que "
        "lo firma. La cuarta es que el resultado de un examen de laboratorio no es un registro "
        "clínico del mismo tipo, porque lo produce el laboratorio y lo carga el personal "
        "administrativo, y quien lo interpreta es el médico al elaborar el diagnóstico."
    )
    d.parrafo(
        "De estas condiciones se derivaron decisiones directas del diseño. La separación "
        "mínima de treinta minutos entre dos citas del mismo médico responde a la primera. Que "
        "el médico vea su agenda sin poder modificarla responde a la segunda. Que la historia "
        "clínica, el diagnóstico y la prescripción sean escritura exclusiva del médico "
        "tratante, y que el administrador solo pueda consultarlos, responde a la tercera. Y "
        "que el registro de exámenes sea la única función clínica que el administrador sí "
        "puede escribir responde a la cuarta."
    )

    d.titulo("3.4.3 Observación directa", nivel=3)
    d.parrafo(
        "La observación directa se realizó sobre la ventanilla de asignación de citas de un "
        "centro de atención ambulatoria. La técnica consistió en presenciar la asignación "
        "durante la jornada, sin intervenir en el proceso, y en revisar con la persona "
        "encargada el recorrido completo de una solicitud desde que el paciente la formula "
        "hasta que queda anotada."
    )
    d.parrafo(
        "La observación estableció cuatro hechos que la encuesta no habría revelado. El "
        "primero es que la disponibilidad no se consulta, se recuerda, porque quien asigna "
        "sostiene mentalmente qué franjas están ocupadas y solo verifica en la agenda cuando "
        "duda, de modo que la calidad de la programación depende de la memoria de una persona. "
        "El segundo es que la ventanilla y el teléfono se atienden a la vez, y en dos ocasiones "
        "se ofreció la misma franja por los dos canales antes de que ninguna de las dos "
        "quedara anotada, lo que muestra que el conflicto no aparece por descuido sino porque "
        "dos solicitudes simultáneas consultan el mismo estado antes de que cualquiera escriba. "
        "El tercero es que quien llega a cancelar hace la misma fila que quien llega a "
        "solicitar, de manera que liberar un horario cuesta tanto como ocuparlo y por eso "
        "muchos horarios no se liberan. El cuarto es que la anotación no registra quién la "
        "hizo, así que cuando una cita aparece cambiada no hay forma de saber quién la cambió."
    )
    d.parrafo(
        "De estos hallazgos se derivaron también decisiones concretas. Que la disponibilidad "
        "se presente como un calendario semanal calculado por el sistema, y no como una lista "
        "que alguien deba interpretar, responde al primero. Que la comprobación de conflictos "
        "y la reserva ocurran dentro de una misma transacción que bloquea la agenda del médico "
        "hasta confirmar responde al segundo. Que el paciente pueda cancelar su propia cita "
        "desde su panel responde al tercero. Y que cada registro guarde el autor tomado de la "
        "sesión, y no de lo que venga en el formulario, responde al cuarto."
    )


# --- 3.5 -----------------------------------------------------------------------

def _analisis(d):
    d.titulo("3.5 Análisis de resultados de la elicitación", nivel=2, nueva_pagina=True)

    presencial = 26
    mas_de_media_hora = 16 + 15
    al_menos_una_vez = 16 + 13

    d.parrafo(
        f"De las {encuesta.MUESTRA} personas encuestadas, {_n(presencial)} solicitan hoy su "
        f"cita presentándose en el centro de salud y {_n(14)} lo hacen por teléfono, de manera "
        f"que ocho de cada diez dependen de que haya alguien del otro lado en ese momento. "
        f"Solo {_n(2)} disponen de una página o una aplicación para hacerlo. El canal, por "
        f"tanto, no es una preferencia de los usuarios, es lo único que tienen."
    )
    d.parrafo(
        f"El costo de ese canal aparece en la segunda pregunta. A {_n(mas_de_media_hora)} la "
        f"asignación les toma más de media hora desde que la solicitan, y a {_n(15)} de ellas "
        f"más de una hora. A esa espera se suma el desplazamiento, ya que {_n(34)} han tenido "
        f"que ir al centro de salud únicamente para solicitar o cancelar una cita, y "
        f"{_n(encuesta.SOLO_EN_HORARIO)} solo pueden hacer la solicitud dentro del horario de "
        f"atención, que es el mismo horario en el que trabajan o estudian."
    )
    d.parrafo(
        f"La programación tampoco resulta confiable. {_n(al_menos_una_vez)} han recibido al "
        f"menos una vez una cita que se cruzó con la de otro paciente o para la que el médico "
        f"no estaba disponible, y {_n(13)} lo han vivido varias veces. Contrastado con lo "
        f"observado en la ventanilla, el dato deja de parecer un descuido, porque el cruce se "
        f"produce cuando dos solicitudes se atienden a la vez sobre una disponibilidad que "
        f"nadie ha escrito todavía, y eso ocurre por la forma en que se lleva la agenda y no "
        f"por la falta de cuidado de quien la lleva."
    )
    d.parrafo(
        "El contraste entre las preguntas 7 y 8 constituye el hallazgo central de la "
        f"elicitación. Ante la pregunta de si les gustaría ver los horarios libres del médico "
        f"y elegir por sí mismos, {_n(41)} respondieron afirmativamente. Y ante la pregunta de "
        f"si preferirían que esa elección quedara agendada de inmediato o pendiente de "
        f"aprobación, {_n(39)} escogieron que quedara en firme y apenas {_n(5)} prefirieron la "
        f"aprobación previa. Las dos respuestas juntas dicen algo más preciso que cada una por "
        f"separado, y es que lo que se pide no es consultar la agenda sino reservar en ella."
    )
    d.parrafo(
        "Esa distinción es la que sostiene la regla de negocio que más se aparta del "
        "planteamiento inicial del proyecto. Un agendamiento en el que el paciente elige el "
        "horario pero su solicitud queda esperando la confirmación de un administrativo "
        "conserva la demora que la herramienta venía a eliminar, y sustituye una fila física "
        "por una fila electrónica. Por eso la cita nace agendada y no pendiente, y el orden lo "
        "resuelve quien llegue primero. El control no desaparece, se traslada a después de la "
        "reserva, ya que el administrador puede cancelar o reprogramar cualquier cita, "
        "incluidas las que agendó un paciente."
    )
    d.parrafo(
        "Las preguntas restantes aportaron información que se tradujo igualmente en decisiones "
        "concretas del diseño."
    )
    d.tabla(
        "Hallazgos complementarios de la encuesta y su efecto sobre el diseño",
        ["Pregunta", "Resultado", "Efecto sobre la solución"],
        [
            ["Momento en que puede solicitarse la cita",
             f"{_n(encuesta.SOLO_EN_HORARIO)} solo pueden solicitarla dentro del horario de "
             f"atención del centro",
             "Sostuvo que el agendamiento fuera una aplicación web disponible a cualquier "
             "hora y no un canal atendido por una persona."],
            ["Cancelación de una cita",
             f"{_n(encuesta.TUVO_QUE_IR)} tuvieron que desplazarse para cancelar y solo "
             f"{_n(9)} pudieron hacerlo sin ir",
             "Justificó que el paciente cancele su propia cita desde su panel, que es la "
             "segunda excepción de escritura que se le concede."],
            ["Consulta en línea del historial y de las fórmulas",
             f"{_n(encuesta.HISTORIAL_SI)} manifestaron interés",
             "Determinó que el paciente tuviera acceso de lectura a sus historias, sus "
             "consultas, sus recetas y sus exámenes, y no solo a sus citas."],
            ["Importancia de que solo el médico escriba la historia clínica",
             f"{_n(encuesta.CONFIDENCIALIDAD_ALTA)} la calificaron con 4 o 5 sobre 5",
             "Confirmó desde la expectativa del paciente lo que la entrevista había planteado "
             "como obligación profesional, y sustentó que el acto clínico fuera escritura "
             "exclusiva del médico tratante."],
            ["Preocupación por el acceso de personal no médico",
             f"{_n(encuesta.PREOCUPA_NO_MEDICO)} manifestaron preocupación",
             "Motivó que el administrador conserve lectura sobre la historia clínica pero "
             "no pueda crearla ni modificarla, que es su única restricción en el sistema."],
            ["Disponibilidad de un dispositivo con internet",
             f"{_n(encuesta.CON_DISPOSITIVO)} disponen de teléfono o computador con acceso",
             "Descartó la necesidad de una aplicación instalable y fijó como condición que "
             "las pantallas se adapten al ancho de un teléfono."],
        ],
        nota="Elaboración propia con base en los resultados de la encuesta.",
        anchos=[3.6, 5.2, 7.5],
    )
    d.parrafo(
        "Las tres técnicas convergieron en el mismo punto por caminos distintos, y esa "
        "convergencia es lo que permitió adoptar el diagnóstico como premisa del proyecto y no "
        "como una hipótesis por verificar. La encuesta mostró la magnitud del problema, esto "
        "es, cuántas personas dependen de un canal presencial, cuánto tiempo pierden y cuántas "
        "han sufrido un cruce. La observación mostró el mecanismo que lo produce, que es una "
        "agenda sostenida en la memoria de quien la administra y expuesta a que dos "
        "solicitudes simultáneas ocupen la misma franja. Y la entrevista fijó los límites que "
        "la solución no podía cruzar, que son la duración real de una consulta y la reserva "
        "del acto clínico."
    )
    d.parrafo(
        f"El resultado de la elicitación se consolidó en {requisitos.conteo()['funcionales']} "
        f"requisitos funcionales y {requisitos.conteo()['no_funcionales']} no funcionales, "
        f"organizados en {requisitos.conteo()['modulos']} módulos, que se especifican en el "
        f"capítulo siguiente. La trazabilidad entre lo observado y lo especificado se mantiene "
        f"en ambas direcciones, porque cada requisito responde a una necesidad identificada y "
        f"cada hallazgo relevante tiene al menos un requisito que lo atiende."
    )
    d.parrafo(
        "Conviene señalar una limitación del ejercicio. La muestra se seleccionó por "
        "conveniencia y se concentra en un ámbito geográfico determinado, de modo que sus "
        "resultados describen la situación de las personas consultadas y no deben leerse como "
        "una estimación estadística de la población. Del mismo modo, la entrevista recoge el "
        "criterio de un profesional y la observación corresponde a un solo centro de atención. "
        "El propósito del ejercicio fue orientar el diseño de la solución, y para ese propósito "
        "la coincidencia entre las tres técnicas resultó suficiente."
    )


# --- 3.6 -----------------------------------------------------------------------

def _equipo(d):
    d.titulo("3.6 Equipo de proyecto y partes interesadas", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El equipo de trabajo se conformó con dos integrantes, quienes asumieron los roles "
        "previstos por Scrum sin dejar de participar en el desarrollo. En un equipo de este "
        "tamaño la separación estricta de roles resulta impracticable, y lo que se mantuvo fue "
        "la responsabilidad sobre cada función, no la exclusividad en ella, de manera que "
        "ambos integrantes intervinieron en la construcción de los diez módulos."
    )
    d.tabla(
        "Equipo de proyecto y responsabilidades",
        ["Integrante", "Rol", "Responsabilidades"],
        [[i, r, resp] for i, r, resp in EQUIPO],
        nota="Elaboración propia.",
        anchos=[4.4, 3.6, 8.3],
    )
    d.parrafo(
        "Las partes interesadas comprenden a quienes se ven afectados por el proyecto o "
        "influyen en él, participen o no en su construcción. Su identificación temprana "
        "permite anticipar qué se espera de la solución desde cada posición, que no siempre "
        "coincide, y en este proyecto la diferencia es especialmente marcada, ya que el "
        "paciente quiere reservar sin intermediarios, el médico quiere que nadie escriba en su "
        "lugar y el personal administrativo necesita conservar el control de una agenda que ya "
        "no depende solo de él."
    )
    d.tabla(
        "Partes interesadas del proyecto",
        ["Parte interesada", "Relación con el proyecto"],
        [[p, r] for p, r in INTERESADOS],
        nota="Elaboración propia. La matriz de stakeholders del capítulo 4 detalla su nivel "
             "de interés y de influencia.",
        anchos=[5.0, 11.3],
    )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
