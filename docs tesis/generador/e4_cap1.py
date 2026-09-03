# -*- coding: utf-8 -*-
"""
E4 — Capítulo 1. Planteamiento del problema y formulación del proyecto.

🔴 **Los objetivos van literal** como quedaron aprobados en el §11.2 del cuaderno de trabajo.
Son lo que el capítulo 6 declara cumplido, así que reescribirlos aquí, aunque fuera para mejorar
la redacción, dejaría al documento prometiendo una cosa y demostrando otra.

Este capítulo responde además a la observación **O08**, que pedía replantear los objetivos
específicos porque los del documento anterior eran del software y no del proyecto. Los de ahora
están redactados como resultados y no como actividades, son tres en lugar de cinco y ninguno
empieza por «Documentar», que es una tarea de la tesis y no del proyecto. El apartado 1.6 lo
deja dicho de forma expresa, para que el jurado no tenga que deducirlo.
"""

# --- Texto aprobado por el autor, que no se reescribe (cuaderno §11.2) -----------

OBJETIVO_GENERAL = (
    "Desarrollar MediApp, un sistema web de agendamiento de citas médicas con acceso "
    "diferenciado para administrador, médico y paciente, que permita gestionar la "
    "disponibilidad de la atención médica y controlar el historial clínico en centros de salud."
)

OBJETIVOS_ESPECIFICOS = [
    "Facilitar la programación de la atención médica mediante un módulo interactivo que "
    "permita al administrador y al paciente agendar citas de forma intuitiva.",

    "Habilitar la gestión del acto clínico como responsabilidad exclusiva del médico tratante "
    "para la creación y actualización de historias clínicas, diagnósticos y prescripciones.",

    "Garantizar la confidencialidad de la información médica mediante un control de acceso "
    "basado en roles que restrinja la visualización y edición según el perfil del usuario.",
]

# --- Condiciones que el proyecto no eligió --------------------------------------

RESTRICCIONES = [
    "El proyecto se desarrolla como trabajo de grado, de modo que su alcance y su plazo son "
    "los del programa de formación y no los de un producto comercial.",

    "El equipo lo componen dos personas que cursan al mismo tiempo el programa, sin dedicación "
    "exclusiva al desarrollo.",

    "La infraestructura disponible es un entorno local de desarrollo, sin servidor contratado "
    "ni dominio propio, por lo que el cifrado del tránsito depende de dónde se despliegue el "
    "sistema y no del programa.",

    "Se emplean únicamente herramientas libres y de uso común, sin componentes de licencia "
    "propietaria, para que la solución pueda instalarse sin costo de licenciamiento.",

    "El sistema no puede presentarse como historia clínica electrónica certificada, porque su "
    "habilitación exige requisitos normativos y de interoperabilidad que exceden el alcance "
    "académico del proyecto.",

    "Los datos con los que se demuestra el funcionamiento son ficticios, ya que operar con "
    "información clínica real exigiría autorización del titular y un tratamiento de datos "
    "personales que el proyecto no está en condiciones de garantizar.",
]

LIMITACIONES = [
    "El sistema no notifica la cita por correo electrónico ni por mensaje de texto, de modo "
    "que el recordatorio sigue dependiendo del paciente.",

    "No incluye teleconsulta ni videollamada, porque pertenecen a la prestación del servicio y "
    "no a su agendamiento, que es lo que el objetivo general delimita.",

    "No factura los servicios prestados ni administra convenios con aseguradoras.",

    "No firma digitalmente la historia clínica, lo que requeriría una autoridad certificadora.",

    "No realiza respaldos automáticos ni aplica una política de retención, pues son funciones "
    "de la administración del servidor de base de datos y no del sistema.",

    "No cuenta con aplicación móvil nativa, aunque la interfaz responde desde el navegador de "
    "un teléfono.",
]


def escribir(d):
    d.titulo("Capítulo 1. Planteamiento del problema y formulación del proyecto",
             nivel=1, nueva_pagina=True)

    _problema(d)
    _justificacion(d)
    _restricciones(d)
    _limitaciones(d)
    _objetivos(d)


def _problema(d):
    d.titulo("1.1 Descripción del problema", nivel=2)
    d.parrafo(
        "La atención ambulatoria de un centro de salud pequeño se organiza alrededor de una "
        "agenda, y de la consistencia de esa agenda depende buena parte de lo que el paciente "
        "percibe como calidad del servicio. Cuando las citas se registran en un cuaderno o en "
        "una hoja de cálculo compartida, el registro anota lo que se le escribe y no comprueba "
        "nada, de manera que la consistencia queda encomendada por completo a la memoria de "
        "quien agenda."
    )
    d.parrafo(
        "El diagnóstico realizado sobre la operación de centros de atención de este tamaño "
        "identificó tres situaciones que se repiten y que tienen la misma causa. La primera es "
        "el choque de horarios, porque nada impide citar a dos pacientes con el mismo médico a "
        "la misma hora ni dejar entre dos citas un margen menor del que dura la consulta. La "
        "segunda es la acumulación, ya que un mismo paciente puede quedar citado varias veces "
        "en el mismo día sin que el registro lo advierta. La tercera es el agendamiento sobre "
        "fechas ya transcurridas, que ocurre al copiar una programación anterior sin revisarla."
    )
    d.parrafo(
        "Las consecuencias de esas tres situaciones no se quedan en el mostrador. Una sala de "
        "espera con dos personas citadas a la misma hora produce un retraso que el médico "
        "arrastra el resto de la jornada, y termina en un paciente que regresa a su casa sin "
        "haber sido atendido. El costo no es solamente de tiempo, porque una cita perdida en "
        "un servicio de salud puede significar un control que no se hizo o un tratamiento que "
        "se demoró."
    )
    d.parrafo(
        "Junto a la agenda aparece una segunda dificultad, de naturaleza distinta y de mayor "
        "consecuencia. La información clínica de un paciente, que es su historia, su "
        "diagnóstico y lo que se le prescribe, tiene un responsable con nombre propio, que es "
        "el médico que lo atendió. Cuando esa información vive en un archivo que todo el "
        "personal puede abrir y modificar, la responsabilidad deja de poder sostenerse, porque "
        "nada distingue lo que escribió el médico de lo que corrigió después alguien más. No "
        "se trata de desconfianza hacia el personal administrativo, sino de que un registro "
        "clínico sin autoría verificable pierde su condición de registro clínico."
    )
    d.parrafo(
        "Las dos dificultades comparten una misma raíz, y es que la herramienta con la que se "
        "trabaja no distingue entre quién hace qué. Un cuaderno no sabe qué es una regla de "
        "agenda y una hoja de cálculo no sabe qué es un rol, de modo que ni la consistencia de "
        "la programación ni la custodia del acto clínico pueden apoyarse en ellas. De ahí que "
        "el problema no se resuelva ordenando mejor el archivo, sino sustituyéndolo por un "
        "sistema que compruebe."
    )


def _justificacion(d):
    d.titulo("1.2 Justificación", nivel=2)
    d.parrafo(
        "MediApp se justifica porque atiende las dos dificultades anteriores con un mismo "
        "diseño y en el punto exacto donde se originan. Sobre la agenda convierte el registro "
        "pasivo en una comprobación, de modo que ninguna cita llega a guardarse sin que el "
        "sistema haya verificado que el médico dispone del tiempo necesario, que el paciente "
        "no tiene ya otra cita ese día y que la fecha no ha transcurrido. La regla deja de "
        "depender de que alguien la recuerde el día de más trabajo, que es justamente cuando "
        "se olvida."
    )
    d.parrafo(
        "Sobre la información clínica, el sistema reparte el acceso en tres perfiles y "
        "comprueba el perfil en el servidor en cada operación, no ocultando opciones en la "
        "pantalla. La diferencia entre las dos formas de hacerlo es la que separa una "
        "restricción real de una apariencia de restricción, porque una opción oculta vuelve a "
        "mostrarse desde el navegador mientras que una comprobación en el servidor rechaza la "
        "petición aunque llegue por fuera de la interfaz."
    )
    d.parrafo(
        "El reparto de esos perfiles es lo que distingue a este proyecto de un sistema de "
        "gestión corriente. El administrador gestiona la operación completa y su única "
        "restricción es que no puede crear ni modificar historias clínicas, diagnósticos ni "
        "recetas. El médico, que es el perfil con menos pantallas, es el único que puede "
        "hacerlo. Esa inversión no es un detalle de configuración, porque traslada al sistema "
        "una regla del ejercicio profesional, y es que el acto clínico pertenece a quien lo "
        "ejecuta."
    )
    d.parrafo(
        "El beneficio se reparte entre los tres perfiles y es distinto en cada uno. La "
        "administración deja de sostener la agenda con la memoria y gana un registro que "
        "rechaza lo que no puede ser. El médico obtiene la certeza de que lo que firma queda a "
        "su nombre y no se altera después. El paciente deja de depender de una llamada en "
        "horario de oficina para pedir o cancelar su cita, porque lo hace desde un calendario "
        "que le muestra los horarios libres sin revelarle quién ocupa los demás."
    )
    d.parrafo(
        "Desde el punto de vista técnico, el proyecto se justifica además como ejercicio de "
        "formación sobre un problema que no admite soluciones aparentes. Una agenda compartida "
        "obliga a resolver la concurrencia, porque dos personas pueden pedir el mismo horario "
        "en el mismo instante, y un sistema descuidado se lo concede a las dos. Un reparto de "
        "acceso por roles obliga a distinguir entre esconder y prohibir. Ambas cuestiones se "
        "resuelven en este trabajo y se verifican con pruebas automatizadas, que es lo que "
        "permite afirmar que están resueltas en lugar de suponerlo."
    )


def _restricciones(d):
    d.titulo("1.3 Restricciones", nivel=2)
    d.parrafo(
        "Las restricciones son condiciones impuestas al proyecto desde fuera, que delimitan lo "
        "que puede construirse y bajo qué condiciones."
    )
    d.vinetas(RESTRICCIONES)


def _limitaciones(d):
    d.titulo("1.4 Limitaciones", nivel=2)
    d.parrafo(
        "Las limitaciones son alcances que la solución no cubre. Se declaran de forma expresa "
        "porque un sistema que custodia información clínica de personas identificadas no "
        "admite ambigüedad sobre lo que hace y lo que no, y porque un documento que solo "
        "describe lo que el sistema tiene deja al lector suponiendo el resto."
    )
    d.vinetas(LIMITACIONES)
    d.parrafo(
        "Ninguna de estas limitaciones es un olvido. Todas corresponden a capacidades que se "
        "evaluaron durante el análisis y se descartaron para esta versión, y aparecen en el "
        "anexo de especificación de requisitos como la categoría de aquello que de forma "
        "expresa no se construirá."
    )


def _objetivos(d):
    d.titulo("1.5 Objetivo general", nivel=2)
    d.parrafo(OBJETIVO_GENERAL)

    d.titulo("1.6 Objetivos específicos", nivel=2)
    d.numerada(OBJETIVOS_ESPECIFICOS)


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
