# -*- coding: utf-8 -*-
"""
E4 — Capítulo 4. Análisis y especificación de requisitos.

**Nada de lo que este capítulo afirma se escribe aquí.** Los requisitos y sus puntajes se leen
de `requisitos.py`, el cronograma y los riesgos de `figuras.py` y los objetivos de `e4_cap1.py`.
La razón es la de siempre, y es que el mismo dato aparece en el anexo E1, en este capítulo y en
la diapositiva; con tres listas separadas basta cambiar un puntaje en una para que las otras dos
describan un sistema que ya no existe, y nadie lo nota hasta la sustentación.

Tres observaciones del evaluador se resuelven en este capítulo.

**O04, que el modelo MoSCoW no se observaba.** El 4.6 no presenta el reparto sin más, sino la
regla que lo produce, los cortes elegidos y lo que se decidió no construir. El detalle requisito
por requisito queda en E1, que es el anexo que existe para eso.

**O09, que los riesgos eran del software y no del proyecto.** El 4.7 no trae un solo riesgo
técnico de la aplicación. Trae los del trabajo de grado como empresa, que son el equipo, el
tiempo, la evaluación y la infraestructura de la que depende la sustentación.

**O10, que el Gantt del documento y el de la diapositiva eran distintos.** El 4.3 no dibuja ni
tabula un cronograma propio: lee `figuras.FASES`, que es de donde sale también `FIG-cronograma`
y de donde lo tomará la diapositiva. No pueden discrepar porque son el mismo dato.

Aquí queda además la **justificación escrita de D9**, que el paciente agende su propia cita sin
aprobación previa, dentro del 4.4.5. El 5.5 la retomará desde el modelo de permisos.
"""
from pathlib import Path

import figuras
import requisitos
from e4_cap1 import OBJETIVOS_ESPECIFICOS
from requisitos import MODULOS, RNF, FUERA_DE_ALCANCE, prioridad, puntaje, conteo

IMAGENES = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

HISTORIAS = [
    ("HU-01", "Como paciente, quiero crear mi propia cuenta indicando mis datos para poder "
              "solicitar citas sin tener que pedirle a alguien que me registre."),
    ("HU-02", "Como usuario del sistema, quiero que al ingresar se me lleve directamente al "
              "panel que me corresponde para no tener que elegir con qué perfil entro."),
    ("HU-03", "Como paciente, quiero ver en un calendario los horarios libres de cada médico "
              "para escoger el que me convenga sin preguntar por ellos."),
    ("HU-04", "Como paciente, quiero que el horario que elijo quede agendado en el momento "
              "para no tener que esperar a que un tercero me lo confirme."),
    ("HU-05", "Como paciente, quiero cancelar mi propia cita desde el sistema para liberar el "
              "horario sin desplazarme hasta el centro de salud."),
    ("HU-06", "Como administrador, quiero agendar una cita a nombre de cualquier paciente "
              "para poder atender a quien la solicite por teléfono o en ventanilla."),
    ("HU-07", "Como administrador, quiero reprogramar o cancelar cualquier cita ya agendada, "
              "incluidas las que reservó un paciente, para conservar el control de la agenda."),
    ("HU-08", "Como sistema, quiero rechazar toda cita que caiga dentro de la separación "
              "mínima de otra del mismo médico para no programar una atención que no podrá "
              "cumplirse."),
    ("HU-09", "Como sistema, quiero resolver en el servidor dos reservas simultáneas del mismo "
              "horario para que solo una de las dos quede en firme."),
    ("HU-10", "Como médico, quiero consultar mi agenda sin poder modificarla para saber a "
              "quién atiendo sin asumir la responsabilidad de programarla."),
    ("HU-11", "Como médico, quiero registrar la historia clínica del paciente que atiendo para "
              "dejar constancia de su evolución bajo mi propia autoría."),
    # 🔴 Decía «para que queden unidos a la cita que los originó», y el esquema no tiene esa
    # columna: `consulta` referencia a `paciente` y a `medico`, no a `cita`. La cita es el
    # motivo por el que se atiende, no un dato que la consulta guarde.
    ("HU-12", "Como médico, quiero registrar el diagnóstico y el plan de tratamiento de la "
              "atención que acabo de prestar para que queden bajo mi autoría y a nombre del "
              "paciente atendido."),
    ("HU-13", "Como médico, quiero prescribir medicamentos tomados del catálogo, con su dosis "
              "y su frecuencia, para que la fórmula quede legible y sin ambigüedad."),
    ("HU-14", "Como administrador, quiero cargar los exámenes de laboratorio y sus resultados "
              "para que el médico disponga de ellos al elaborar el diagnóstico."),
    ("HU-15", "Como paciente, quiero consultar en línea mis historias, mis diagnósticos, mis "
              "recetas y mis exámenes para tener a la mano lo mío sin solicitarlo."),
    ("HU-16", "Como paciente, quiero que nadie distinto del médico que me atiende pueda "
              "escribir en mi historia clínica para que conserve la reserva que le "
              "corresponde."),
    ("HU-17", "Como administrador, quiero dar de baja a un médico o a un paciente sin que "
              "desaparezcan los registros que firmó o recibió, para no perder el historial "
              "del centro."),
]

# Los no funcionales que se llevan al documento de grado, por su código. Se eligieron para que
# las siete categorías queden representadas; el catálogo completo va en el anexo E1.
RNF_SELECCIONADOS = ["RNF 01", "RNF 03", "RNF 04", "RNF 05", "RNF 08", "RNF 10", "RNF 11",
                     "RNF 12", "RNF 13", "RNF 14", "RNF 16", "RNF 18", "RNF 19", "RNF 22",
                     "RNF 24"]

# Lo que hay que decir de un módulo además de lo que ya dice su ficha del catálogo. Se guarda
# aparte porque `requisitos.py` describe el módulo y aquí se argumenta una decisión de diseño.
COMENTARIOS = {
    "RF 5": "_agendamiento",
    "RF 6": "_acto_clinico",
    "RF 10": "_catalogos",
}


def _criticos(lista):
    return [(c, n, desc, actor) for c, n, desc, actor, v, u in lista
            if prioridad(v, u) == "Crítica"]


def _mes(indice):
    """El mes número `indice` del cronograma, contado desde su primer mes."""
    absoluto = figuras.MES_CERO + indice
    return MESES[absoluto % 12], 2025 + absoluto // 12


def _periodo(inicio, duracion):
    """«Noviembre de 2025 a marzo de 2026», «Marzo a mayo de 2025» o «Marzo de 2025».

    El año se escribe una sola vez cuando el periodo no cambia de año, porque «marzo de 2025 a
    mayo de 2025» repite el dato que la propia frase ya dio.
    """
    mes_inicial, anio_inicial = _mes(inicio)
    mes_final, anio_final = _mes(inicio + duracion - 1)
    if duracion == 1:
        return f"{mes_inicial.capitalize()} de {anio_inicial}"
    if anio_inicial == anio_final:
        return f"{mes_inicial.capitalize()} a {mes_final} de {anio_final}"
    return f"{mes_inicial.capitalize()} de {anio_inicial} a {mes_final} de {anio_final}"


def escribir(d):
    d.titulo("Capítulo 4. Análisis y especificación de requisitos", nivel=1, nueva_pagina=True)
    _stakeholders(d)
    _historias(d)
    _cronograma(d)
    _funcionales(d)
    _no_funcionales(d)
    _priorizacion(d)
    _riesgos(d)


# --- 4.1 -----------------------------------------------------------------------

def _stakeholders(d):
    d.titulo("4.1 Matriz de stakeholders", nivel=2)
    d.parrafo(
        "La matriz de stakeholders se empleó para identificar y clasificar a los actores "
        "involucrados en el proyecto según dos criterios."
    )
    d.vinetas([
        ("Influencia", "capacidad que tiene un actor para afectar las decisiones o el "
                       "desarrollo del proyecto."),
        ("Interés", "nivel de preocupación o participación que tiene respecto de los "
                    "resultados del proyecto."),
    ])
    d.parrafo(
        "El cruce de ambos criterios define cuatro cuadrantes, y cada uno determina una "
        "estrategia distinta de comunicación y de gestión."
    )
    d.figura(
        "Matriz de influencia e interés de las partes interesadas",
        IMAGENES / "FIG-stakeholders.png",
        nota="Elaboración propia. Cada cuadrante determina la estrategia de gestión de los "
             "actores que contiene.",
    )
    d.parrafo(
        "Los médicos y los pacientes quedaron en el cuadrante de alto interés y baja influencia. "
        "Son quienes más se juegan en el resultado, porque el sistema decide si el paciente "
        "consigue su cita y si el profesional conserva la autoría de lo que firma, y sin "
        "embargo ninguno de los dos decide su adopción ni participa en su construcción. La "
        "estrategia frente a ellos no es de negociación sino de satisfacción, y consiste en que "
        "el sistema resuelva lo que cada uno necesita aunque no estén en la mesa donde se "
        "decide."
    )
    d.parrafo(
        "La segunda es que la instructora y los evaluadores del centro de formación quedaron "
        "en el cuadrante de alta influencia y alto interés, junto al equipo de desarrollo y a "
        "la dirección del centro de salud. Su influencia sobre este proyecto es determinante, "
        "ya que las quince observaciones que originaron esta versión del trabajo provienen de "
        "esa evaluación, y por eso la estrategia frente a ellos es de participación, que en "
        "la práctica significa que cada observación quedó cruzada con la tarea que la resuelve "
        "y ninguna se dio por cerrada por su cuenta."
    )


# --- 4.2 -----------------------------------------------------------------------

def _historias(d):
    d.titulo("4.2 Historias de usuario", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Las historias de usuario expresan las necesidades identificadas desde la perspectiva "
        "de quien las tiene, indicando el actor, lo que necesita y para qué lo necesita. Esta "
        "última parte es la que orienta el diseño, porque dos soluciones pueden satisfacer la "
        "misma petición y solo una atender el propósito que hay detrás."
    )
    d.tabla(
        "Historias de usuario del sistema",
        ["ID", "Historia de usuario"],
        [[i, h] for i, h in HISTORIAS],
        nota="Elaboración propia. Las historias se redactaron a partir de los hallazgos de la "
             "encuesta, de la entrevista y de la observación directa descritos en el capítulo "
             "anterior.",
        anchos=[1.7, 14.6],
    )
    d.parrafo(
        "Tres de estas historias no provienen de una petición sino de un hallazgo. La HU-08 y "
        "la HU-09 están enunciadas desde el sistema y no desde una persona, porque describen "
        "reglas que se ejecutan sin que nadie las solicite, y son justamente las que la "
        "observación directa mostró que hoy no se cumplen, ya que la separación entre "
        "atenciones depende de la memoria de quien asigna y dos solicitudes atendidas a la vez "
        "pueden ocupar la misma franja. La HU-16, sobre que nadie distinto del médico escriba "
        "en la historia clínica, corresponde a una expectativa que el paciente no habría "
        "formulado como funcionalidad, y que la encuesta reveló al preguntarla de forma "
        "directa."
    )
    d.parrafo(
        "A partir de estas historias se construyó el product backlog descrito en el capítulo "
        "anterior y se derivaron los requisitos funcionales que conforman cada uno de los "
        "módulos del sistema."
    )


# --- 4.3 -----------------------------------------------------------------------

def _cronograma(d):
    d.titulo("4.3 Cronograma de actividades", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Con el fin de organizar la ejecución del proyecto se estableció un cronograma que "
        "abarca desde el levantamiento de requisitos hasta la sustentación del trabajo final. "
        "La planificación se estructuró en cinco fases, que son análisis, planeación, "
        "ejecución, evaluación y corrección, cada una con actividades y entregables definidos, "
        "lo que permitió hacer seguimiento al avance y controlar los tiempos de desarrollo."
    )
    d.figura(
        "Cronograma de actividades del proyecto",
        IMAGENES / "FIG-cronograma.png",
        nota="Elaboración propia. Cada barra abarca los meses que la actividad ocupó, y el "
             "trazo vertical grueso marca el cambio de año.",
    )
    filas = []
    for nombre, _color, actividades in figuras.FASES:
        for posicion, (actividad, inicio, duracion) in enumerate(actividades):
            filas.append([nombre if posicion == 0 else "", _periodo(inicio, duracion),
                          actividad])
    # El nombre no repite el de la figura anterior. Con los dos llamados «Cronograma de
    # actividades del proyecto», una remisión del texto no dice a cuál de los dos manda.
    d.tabla(
        "Actividades del proyecto por fase y periodo",
        ["Fase", "Periodo", "Actividad"],
        filas,
        # 🔴 §17. La nota explicaba que la tabla y la figura salen del mismo dato y que por eso
        # no pueden diferir de la diapositiva. Es cierto y es la razón por la que O10 queda
        # cerrada, pero le habla al evaluador sobre el documento en vez de hablarle al lector
        # sobre el proyecto. Va por consola, no aquí (el autor lo mandó quitar el 2026-09-03).
        nota="Elaboración propia.",
        anchos=[2.8, 5.2, 8.3],
    )
    d.parrafo(
        "La fase de análisis ocupó cuatro meses, una proporción alta frente al total del "
        "proyecto, y la razón se expuso en el capítulo anterior, porque la elicitación no "
        "buscaba una lista de funcionalidades sino establecer por qué conseguir una cita cuesta "
        "lo que cuesta y qué reglas debe respetar una agenda clínica. Establecer que el "
        "problema estaba en el acceso a la agenda, y no en la falta de un registro, es lo que "
        "condujo al sistema que se construyó después."
    )
    d.parrafo(
        "La quinta fase no estaba prevista en la planificación inicial. El proyecto fue "
        "sustentado al término de la fase de evaluación y el resultado "
        "obligó a abrir un periodo adicional de corrección, durante el cual se atendieron las "
        # §17. Terminaba diciendo que el cronograma incorpora esta fase «en lugar de omitirla
        # porque es el periodo del que este documento da cuenta», que es hablar del documento
        # y no del proyecto. El hecho se enuncia y basta.
        "observaciones recibidas, se saldó la deuda técnica acumulada, se construyó la suite de "
        "pruebas automatizadas y se elaboró de nuevo el trabajo escrito."
    )


# --- 4.4 -----------------------------------------------------------------------

def _funcionales(d):
    c = conteo()
    criticos = {codigo: _criticos(lista) for codigo, _, _, _, lista in MODULOS}
    total_criticos = sum(len(v) for v in criticos.values())

    d.titulo("4.4 Requisitos funcionales", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Los requisitos funcionales describen las funcionalidades que el sistema debe "
        "proporcionar para satisfacer las necesidades identificadas durante el levantamiento. "
        f"Se agruparon en {c['modulos']} módulos funcionales que corresponden a los conjuntos "
        "de trabajo reales de la aplicación, y que son los mismos que organizan los diagramas "
        "de casos de uso y la descripción del sistema."
    )
    d.parrafo(
        "La agrupación separa de forma deliberada tres módulos que un sistema clínico "
        "convencional trataría como uno solo. La historia clínica, la consulta con su "
        "diagnóstico y la prescripción se registran en el mismo acto de atención, pero "
        "responden a preguntas distintas, porque la primera relata la evolución del paciente, "
        "la segunda concluye qué tiene y qué se le indica, y la tercera ordena lo que debe "
        "tomar. Mantenerlos separados es lo que permite que cada uno conserve su propia "
        "autoría y su propio vínculo con la cita que lo originó."
    )
    d.parrafo(
        f"El levantamiento produjo {c['funcionales']} requisitos funcionales. En este capítulo "
        f"se presentan los {total_criticos} de prioridad crítica, que son aquellos sin los "
        "cuales el sistema no cumple su propósito; el catálogo completo se encuentra en el "
        "anexo de especificación de requisitos."
    )
    d.tabla(
        "Módulos funcionales y distribución de los requisitos",
        ["Código", "Módulo", "Requisitos", "De prioridad crítica"],
        [[codigo, nombre, str(len(lista)), str(len(criticos[codigo]))]
         for codigo, nombre, _, _, lista in MODULOS]
        + [["", "Total", str(c["funcionales"]), str(total_criticos)]],
        nota="Elaboración propia.",
        anchos=[2.0, 7.6, 3.2, 3.5],
    )
    d.parrafo(
        "La distribución dice por sí sola dónde está el peso del proyecto. El módulo de "
        "agendamiento reúne más requisitos críticos que ningún otro, porque es donde viven las "
        "reglas que impiden programar una atención imposible, y el de catálogos no aporta "
        "ninguno, ya que mantiene listas de apoyo que el resto de los módulos consulta."
    )

    for indice, (codigo, nombre, intro, _porque, lista) in enumerate(MODULOS, start=1):
        d.titulo(f"4.4.{indice} {nombre}", nivel=3)
        d.parrafo(intro)
        if criticos[codigo]:
            d.tabla(
                f"Requisitos funcionales críticos del módulo {codigo}",
                ["Código", "Requisito", "Descripción", "Actor"],
                [[c_rf, n, desc, actor] for c_rf, n, desc, actor in criticos[codigo]],
                nota="Elaboración propia. Se relacionan únicamente los requisitos de prioridad "
                     "crítica; los de prioridad alta, media y baja constan en el anexo de "
                     "especificación.",
                anchos=[1.7, 3.6, 8.0, 3.0],
            )
        else:
            d.parrafo(
                f"Ninguno de los {len(lista)} requisitos de este módulo alcanzó la prioridad "
                "crítica, y esa ausencia es en sí misma un resultado de la valoración. Los "
                "catálogos no atienden a un paciente ni producen un registro clínico, sino que "
                "sostienen a los módulos que sí lo hacen, de modo que su ausencia limita el "
                "sistema pero no lo invalida. El detalle de todos ellos consta en el anexo de "
                "especificación."
            )
        if codigo in COMENTARIOS:
            globals()[COMENTARIOS[codigo]](d)


def _agendamiento(d):
    """La justificación escrita de D9, que es donde el proyecto se aparta de lo planteado."""
    d.parrafo(
        "Este módulo contiene la decisión de diseño que más se aparta del planteamiento "
        "inicial del proyecto, y por eso se justifica por escrito. El planteamiento original "
        "asignaba el agendamiento como responsabilidad exclusiva del personal administrativo, "
        "de manera que el paciente formulaba la solicitud y un tercero la convertía en cita. "
        "El sistema construido permite que el paciente reserve directamente sobre el "
        "calendario de disponibilidad y que la cita quede agendada en el momento, sin un "
        "estado intermedio de aprobación."
    )
    d.parrafo(
        "La justificación es la que arroja la elicitación. Un agendamiento en el que el "
        "paciente elige el horario pero la solicitud queda esperando confirmación conserva la "
        "demora que la herramienta viene a eliminar, y sustituye una fila en la ventanilla por "
        "una fila electrónica. Las respuestas del capítulo anterior lo muestran con claridad, "
        "porque la gran mayoría de los encuestados prefirió que la cita quedara en firme de "
        "inmediato antes que sujeta a la aprobación de un tercero. El criterio adoptado es que "
        "el turno lo obtiene quien lo solicita primero."
    )
    d.parrafo(
        "La decisión no elimina el control administrativo, lo traslada. El administrador "
        "conserva la facultad de cancelar y de reprogramar cualquier cita ya agendada, "
        "incluidas las que reservó un paciente, de modo que el control deja de ejercerse antes "
        "de la reserva y pasa a ejercerse sobre ella. Se conservan además, sin excepción, las "
        "dos reglas que impiden una agenda imposible, que son la separación mínima entre dos "
        "atenciones del mismo médico y el límite de una cita por paciente y por día, y ambas "
        "se comprueban en el servidor, no en el calendario del navegador."
    )
    d.parrafo(
        "La delegación tiene un límite que conviene enunciar, porque de él depende que la "
        "decisión sea segura. El paciente puede reservar únicamente para sí mismo, y la "
        "identidad con la que la cita queda registrada se toma de la sesión y nunca del "
        "formulario enviado. De tomarse del formulario, cualquiera podría agendarle una cita a "
        "otra persona alterando la petición, y la autonomía concedida al paciente se "
        "convertiría en una vía para suplantarlo."
    )


def _acto_clinico(d):
    d.parrafo(
        "Los tres módulos que siguen a este comparten una restricción que ningún otro tiene, y "
        "es que su escritura corresponde de forma exclusiva al médico tratante. El "
        "administrador, que en el resto del sistema puede hacerlo todo, aquí solo puede "
        "consultar. La restricción no es una preferencia de diseño sino una consecuencia de la "
        "naturaleza del registro clínico, cuyo diligenciamiento corresponde a quien interviene "
        "directamente en la atención, y de la responsabilidad profesional que acompaña a la "
        "firma de quien lo suscribe."
    )


def _catalogos(d):
    d.parrafo(
        "Los catálogos son el único módulo del sistema al que el médico no tiene acceso "
        "propio, y la razón es que no lo necesita, ya que lo que requiere de ellos lo obtiene "
        "donde de verdad lo usa, que es el selector de medicamentos del formulario de "
        "prescripción. Una pantalla de catálogo aparte le daría una capacidad que no ejerce y "
        "ampliaría sin motivo la superficie de acceso del sistema."
    )


# --- 4.5 -----------------------------------------------------------------------

def _no_funcionales(d):
    d.titulo("4.5 Requisitos no funcionales", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Los requisitos no funcionales establecen las condiciones de calidad que el sistema "
        "debe satisfacer. No describen funcionalidades, sino restricciones sobre la manera en "
        "que estas se prestan, esto es, con qué garantías de seguridad, con qué fiabilidad "
        "frente a operaciones simultáneas, con qué facilidad de uso y con qué posibilidad de "
        "mantenerse en el tiempo."
    )
    d.parrafo(
        "Cada requisito se acompaña de la forma en que se comprueba. Un requisito no funcional "
        "que no indica cómo verificarse es una aspiración y no un requisito, porque al evaluar "
        "el sistema no habría manera de afirmar si se cumplió o no. La mayoría de estas "
        "verificaciones están hoy automatizadas, y el capítulo 6 informa su resultado."
    )
    seleccion = [r for r in RNF if r[0] in RNF_SELECCIONADOS]
    d.tabla(
        "Requisitos no funcionales del sistema",
        ["Código", "Categoría", "Requisito", "Verificación"],
        [[c, cat, req, ver] for c, cat, req, ver in seleccion],
        nota=f"Elaboración propia. Se presentan {len(seleccion)} de los {len(RNF)} requisitos "
             "no funcionales especificados, con las siete categorías representadas; los "
             "restantes constan en el anexo de especificación.",
        anchos=[1.7, 2.6, 6.9, 5.1],
    )
    d.parrafo(
        "En este sistema, dos de estas categorías no son exigencias genéricas de calidad. "
        "La de seguridad recoge condiciones cuyo "
        "incumplimiento no degrada el servicio sino que lo invalida, ya que un sistema que "
        "custodia historias clínicas y permite que cualquiera las lea deja de cumplir su "
        "propósito por completo. La de fiabilidad no habla de disponibilidad ni de tiempos de "
        "respuesta, sino de que dos peticiones simultáneas sobre el mismo horario no puedan "
        "producir dos citas, que es el modo concreto en que este sistema puede fallar."
    )


# --- 4.6 -----------------------------------------------------------------------

def _priorizacion(d):
    """Responde a O04, «El modelo moscow no se observa en este documento».

    Lo que el evaluador marcó no fue que faltara una tabla, sino que el modelo no se veía. Por
    eso este apartado presenta la regla que produce el reparto y no solamente su resultado.
    """
    c = conteo()

    # Sin dos puntos en el título. El índice del cuaderno lo anunciaba como «Priorización de
    # requisitos: matriz MoSCoW y su justificación», que es justo el patrón «afirmación:
    # explicación» que el §1.1 prohíbe y que `verificar.py` señala.
    d.titulo("4.6 Priorización de requisitos mediante la matriz MoSCoW", nivel=2,
             nueva_pagina=True)
    d.parrafo(
        "Con el fin de establecer el orden de implementación de las funcionalidades, se "
        "priorizaron los requisitos funcionales considerando su valor para la operación del "
        "centro de salud y la urgencia asociada a cada uno. La evaluación empleó una escala de "
        "1 a 5 en ambos criterios, donde los valores más altos representan un mayor impacto "
        "sobre la atención de los pacientes y una necesidad más inmediata de implementación."
    )
    d.tabla(
        "Escala de valoración empleada",
        ["#", "Valor para la operación", "Urgencia"],
        [
            ["1", "Impacto muy bajo sobre la atención", "No es urgente, puede esperar"],
            ["2", "Impacto bajo, aporta poca funcionalidad",
             "Poco urgente, puede desarrollarse después"],
            ["3", "Impacto medio, mejora procesos importantes",
             "Urgencia moderada, conviene implementarlo pronto"],
            ["4", "Impacto alto, necesario para operar con eficiencia",
             "Muy urgente, afecta procesos importantes"],
            ["5", "Impacto crítico, indispensable para el sistema",
             "Urgencia crítica, debe implementarse de inmediato"],
        ],
        nota="Elaboración propia, adaptada de la técnica de priorización por valor y urgencia.",
        anchos=[1.0, 7.6, 7.7],
    )
    d.parrafo(
        "El puntaje individual de cada requisito resulta de ponderar el valor para la "
        "operación en un sesenta por ciento y la urgencia en un cuarenta por ciento. La "
        "ponderación no es neutra y responde a una decisión explícita, y es que lo importante "
        "debe pesar más que lo afanado, porque un requisito urgente pero de bajo valor "
        "desplaza recursos de otro que sostiene la atención. El puntaje global del módulo es "
        "el promedio de los puntajes de sus requisitos."
    )
    d.parrafo(
        "Sobre esos puntajes se aplicó el modelo MoSCoW, técnica de priorización que reparte "
        "los requisitos en cuatro categorías según el compromiso que el equipo adquiere con "
        "cada uno. Las categorías son Must have, para lo que el sistema no puede dejar de "
        "hacer, Should have, para lo que debería hacer y se implementa siempre que no "
        "comprometa a lo anterior, Could have, para lo deseable que puede aplazarse sin "
        "consecuencias, y Won't have, para lo que se decide de forma expresa no construir en "
        "esta versión."
    )
    d.parrafo(
        "La clasificación no se asignó requisito por requisito según el criterio del equipo, "
        "sino que se derivó del puntaje ya calculado. Esta decisión es deliberada, porque una "
        "priorización asignada a mano permite que dos requisitos con la misma valoración "
        "terminen en categorías distintas, y entonces la matriz deja de explicar nada y pasa a "
        "registrar una preferencia. Al derivarla del puntaje, cada requisito puede rastrearse "
        "hasta el valor y la urgencia con que se le evaluó."
    )
    d.tabla(
        "Correspondencia entre el puntaje y la categoría MoSCoW",
        ["Categoría", "Corte del puntaje", "Compromiso que representa", "Cantidad"],
        [
            ["Must have", "Igual o mayor que 4,6",
             "El sistema no cumple su propósito sin este requisito. Su ausencia invalida la "
             "entrega.", str(c["must"])],
            ["Should have", "Entre 4,0 y 4,5",
             "El sistema funciona sin él, pero su ausencia obliga a resolver a mano lo que "
             "debería resolver el programa.", str(c["should"])],
            ["Could have", "Menor que 4,0",
             "Aporta comodidad o completitud y puede aplazarse a una versión posterior sin "
             "afectar la operación.", str(c["could"])],
            ["Won't have", "No se deriva del puntaje",
             "Se decidió de forma expresa no construirlo en esta versión.",
             str(c["fuera_de_alcance"])],
        ],
        nota="Elaboración propia. Los cortes se fijaron sobre la escala ponderada descrita "
             "arriba, cuyo valor máximo es 5,0.",
        anchos=[2.6, 3.0, 8.4, 2.5],
    )
    d.figura(
        "Priorización de los requisitos funcionales según el modelo MoSCoW",
        IMAGENES / "FIG-moscow.png",
        nota="Elaboración propia. Cada categoría muestra su corte, el compromiso que "
             "representa y ejemplos de los requisitos que contiene.",
    )
    d.parrafo(
        f"De los {c['funcionales']} requisitos funcionales especificados, {c['must']} quedaron "
        f"clasificados como Must have, {c['should']} como Should have y {c['could']} como "
        "Could have. Que casi la mitad del catálogo sea de obligatorio cumplimiento no indica "
        "una valoración generosa, sino la naturaleza del sistema, porque en un sistema que "
        "custodia historias clínicas las reglas de acceso no admiten grados y una cita mal "
        "validada es una cita perdida."
    )

    orden = sorted(
        ((nombre, round(sum(puntaje(v, u) for *_, v, u in lista) / len(lista), 1), lista)
         for _codigo, nombre, _i, _p, lista in MODULOS),
        key=lambda fila: fila[1], reverse=True,
    )
    d.tabla(
        "Priorización de los módulos funcionales",
        ["Módulo", "Requisitos", "Críticos", "Puntaje global"],
        [[nombre, str(len(lista)), str(len(_criticos(lista))), str(global_modulo)]
         for nombre, global_modulo, lista in orden],
        nota="Elaboración propia. Ordenados de mayor a menor puntaje global. El detalle "
             "requisito por requisito consta en el anexo de especificación.",
        anchos=[7.4, 3.0, 2.6, 3.3],
    )
    d.parrafo(
        f"El orden resultante confirma la naturaleza del proyecto. Encabeza la lista el módulo "
        f"de {orden[0][0].lower()}, con {orden[0][1]} puntos, y cierra el de "
        f"{orden[-1][0].lower()}, con {orden[-1][1]}. Entre uno y otro se ordenan los módulos "
        "que hacen posible que una cita quede bien agendada y que el acto clínico quede en "
        "manos de quien corresponde."
    )
    d.parrafo(
        "Esta priorización no coincide con el orden en que los módulos se construyeron, que el "
        "capítulo anterior detalla. La prioridad indica qué es más importante y las "
        "dependencias técnicas indican qué puede hacerse antes, y no siempre coinciden, como "
        "lo muestra que el módulo de catálogos sea el de menor puntaje y aun así se haya "
        "construido en tercer lugar."
    )

    d.titulo("4.6.1 Requisitos excluidos del alcance", nivel=3, nueva_pagina=True)
    d.parrafo(
        "Won't have no es el fondo "
        "de la escala, porque un requisito con puntaje bajo sigue estando implementado y no "
        "puede declararse como algo que no se hará. Won't have recoge decisiones de alcance, "
        "esto es, capacidades que se evaluaron durante el análisis y se descartaron para esta "
        "versión, razón por la cual se enumeran aparte en lugar de salir de un corte del "
        "puntaje. Dejarlas escritas delimita hasta dónde llega el compromiso del proyecto y "
        "deja constancia de que la ausencia de cada una obedece a una decisión y no a un "
        "olvido."
    )
    d.tabla(
        "Capacidades excluidas del alcance y razón de la exclusión",
        ["Capacidad", "Razón de la exclusión"],
        [[que, por_que] for que, por_que in FUERA_DE_ALCANCE],
        nota="Elaboración propia.",
        anchos=[5.5, 11.0],
    )
    d.parrafo(
        "La exclusión del cifrado de la información es la que sostiene la redacción del tercer "
        "objetivo específico del proyecto. Ese objetivo garantiza la "
        "confidencialidad de la información médica mediante un control de acceso basado en "
        "roles, y la acotación que introduce la palabra mediante no es un adorno de estilo, ya "
        "que un enunciado sin ella prometería también cifrado en tránsito y en reposo, que "
        "depende de la infraestructura de despliegue y no del programa. Un objetivo que "
        "promete más de lo que el sistema entrega es un objetivo que no puede declararse "
        "cumplido."
    )
    d.parrafo(
        "La priorización mantiene correspondencia con los objetivos específicos enunciados en "
        f"el capítulo 1. Los {len(OBJETIVOS_ESPECIFICOS)} objetivos se sostienen sobre los "
        "módulos mejor puntuados, de modo que el orden de implementación adoptado condujo a "
        "que lo primero en quedar terminado fuera justamente lo que el proyecto se comprometió "
        "a demostrar. El anexo de especificación relaciona cada objetivo con los requisitos y "
        "las pantallas que lo cumplen."
    )


# --- 4.7 -----------------------------------------------------------------------

def _riesgos(d):
    """Responde a O09, «Revisar el punto de RIESGOS, asociarlo al proyecto NO al software».

    Por eso no hay aquí un solo riesgo técnico de la aplicación. Los riesgos técnicos existen,
    se identificaron y se corrigieron, y de ellos da cuenta el capítulo 6; lo que este apartado
    enumera son los riesgos del trabajo de grado como empresa.
    """
    # El texto de abajo afirma que hay exactamente dos riesgos de probabilidad alta. Se
    # comprueba antes de escribir nada, porque un dato que el texto contradice es peor que un
    # documento que no se genera.
    altos = [riesgo for riesgo in figuras.RIESGOS if riesgo[2] == 3]
    if len(altos) != 2:
        raise AssertionError(
            "El apartado 4.7 afirma que hay dos riesgos de probabilidad alta y en "
            f"figuras.RIESGOS hay {len(altos)}. Corregir el texto o los datos."
        )

    d.titulo("4.7 Gestión de riesgos del proyecto", nivel=2, nueva_pagina=True)
    d.parrafo(
        "La gestión de riesgos identifica los sucesos que podrían impedir que el proyecto "
        "alcance sus objetivos, estima qué tan probables son y qué tanto afectarían, y define "
        "de antemano la respuesta que se dará si ocurren. Anticiparla es lo que distingue una "
        "respuesta de una reacción, porque un riesgo previsto se atiende con una medida "
        "preparada y uno no previsto se atiende con lo que haya a la mano."
    )
    d.parrafo(
        "Los riesgos que se relacionan a continuación son los del proyecto entendido como el "
        "trabajo de grado en su conjunto, esto es, el equipo que lo desarrolla, el tiempo de "
        "que dispone, la evaluación a la que se somete y la infraestructura de la que depende "
        "su sustentación. No se incluyen aquí los riesgos técnicos del sistema, que son de "
        "otra naturaleza, ya que no amenazan la realización del proyecto sino la corrección "
        "del programa, y de ellos da cuenta el capítulo 6 al describir los problemas "
        "encontrados durante las pruebas y la forma en que se resolvieron."
    )
    d.parrafo(
        "La probabilidad y el impacto se valoraron en tres niveles. La probabilidad es baja "
        "cuando el suceso exige una circunstancia excepcional, media cuando ha ocurrido en "
        "proyectos comparables y alta cuando ya se manifestó durante este. El impacto es bajo "
        "cuando obliga a rehacer una parte del trabajo, medio cuando compromete un entregable "
        "completo y alto cuando pone en riesgo la aprobación del proyecto."
    )
    d.tabla(
        "Riesgos del proyecto, valoración y respuesta prevista",
        ["Cód.", "Riesgo", "Prob.", "Impacto", "Respuesta prevista"],
        figuras.riesgos_en_tabla(),
        nota="Elaboración propia. La probabilidad y el impacto se valoraron en tres niveles "
             "sobre el proyecto, no sobre el software.",
        # «Impacto» necesita 1,9 cm; con 1,6 el encabezado partía como «Impact / o».
        anchos=[1.3, 5.1, 1.7, 1.9, 6.3],
    )
    # 🔴 §17. Aquí iban dos párrafos que comentaban los dos riesgos de probabilidad alta y la
    # respuesta al de reprobar la sustentación. Los dos hablaban de cómo se elaboró este
    # documento y de la evaluación anterior, no del proyecto, y el autor los mandó quitar el
    # 2026-09-03. La tabla ya trae la respuesta de cada riesgo en su propia fila, que es donde
    # el lector la necesita.


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
