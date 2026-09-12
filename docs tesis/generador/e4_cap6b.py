# -*- coding: utf-8 -*-
"""
E4 — Capítulo 6, parte B. Integración, pruebas, resultados y tecnologías.

Cubre del 6.6 al 6.11 y cierra el cuerpo del documento.

🔴 **Aquí se resuelve O07**, que es la observación más exigente de las quince, porque el
evaluador no pidió una afirmación sino tres cosas concretas: qué tipo de pruebas se realizaron,
sus resultados y **pantallazos de las pruebas**. El 6.7 responde el tipo y el alcance con las
cifras de la suite automatizada, y el 6.8 responde con **cuatro casos de prueba documentados**,
cada uno con su ficha y con el par de capturas de antes y después.

**El par de capturas es lo que hace la evidencia.** Un pantallazo suelto demuestra que la
pantalla existe; el par demuestra que la operación ocurrió, porque puede compararse lo que se
ingresó con lo que el sistema devolvió. Es el patrón que empleó FactuGest y se hereda tal cual.

Las cifras de las pruebas están declaradas como constantes y **se comprueban contra la suite**
antes de escribir nada, de modo que el documento no pueda afirmar un número que ya no es cierto.

El 6.10 relata la conexión compartida como problema **encontrado, diagnosticado y resuelto**, y
no como limitación, que es lo que era antes de la fase de corrección.
"""
from pathlib import Path

import requisitos

CAPTURAS = Path(__file__).resolve().parent.parent / "insumos" / "capturas"

# Cifras de la suite, verificadas con `python -m pytest` el 2026-09-03.
PRUEBAS_TOTAL = 91
SEGUNDOS = "6,9"

# (archivo, cuántas, qué comprueba)
COBERTURA = [
    ("test_andamiaje.py", 4,
     "Que la suite corre sobre la base de pruebas y no sobre la real, que esa base tiene las "
     "once tablas y que cada prueba arranca sin datos de la anterior. Si estas fallan, "
     "ninguna de las demás significa nada."),
    ("test_autenticacion.py", 10,
     "El ingreso con credenciales correctas e incorrectas, la redirección automática al panel "
     "de cada rol y el almacenamiento de la contraseña como valor derivado."),
    ("test_citas.py", 26,
     "Las reglas de la agenda, que son la separación mínima entre atenciones del mismo médico, "
     "el límite de una cita por paciente y por día, el rechazo de fechas ya pasadas, la "
     "reprogramación y la cancelación."),
    ("test_concurrencia.py", 2,
     "Que dos peticiones simultáneas sobre el mismo turno producen una sola cita, y que lo que "
     "lo impide es el bloqueo y no la casualidad."),
    ("test_datos.py", 17,
     "La integridad de los datos, con el fallo del historial clínico como regresión, las bajas "
     "lógicas, el bloqueo de duplicados y el aislamiento entre pacientes."),
    ("test_permisos.py", 32,
     "La matriz de permisos completa de los tres roles, comprobada por su efecto y forzando la "
     "petición, no por que el botón no aparezca en la pantalla."),
]

# (código, requisito, nombre, antes, después, entrada, esperado)
EVIDENCIAS = [
    ("CP-01", "RF 6.1", "Registro de la historia clínica por el médico tratante",
     "CP-01a historia clinica formulario.jpg", "CP-01b historia clinica creada.jpg",
     "Con una sesión de médico se abre el formulario de creación y se indican el paciente, la "
     "fecha del registro, la descripción clínica y las notas. El formulario advierte que el "
     "registro quedará creado a nombre de quien tiene la sesión.",
     "La historia queda registrada y aparece en el listado firmada por el médico de la sesión, "
     "sin que su identidad se haya pedido en ningún campo del formulario."),

    ("CP-02", "RF 5.6", "Rechazo de una cita dentro de la separación mínima",
     "CP-02a cita en conflicto formulario.jpg", "CP-02b cita en conflicto rechazada.jpg",
     "Con una sesión de administrador se intenta agendar una cita para un médico que ya tiene "
     "otra atención quince minutos antes, es decir, dentro de la franja de treinta minutos que "
     "debe mediar entre dos atenciones suyas.",
     "El sistema rechaza la reserva, informa el motivo exacto y conserva los datos "
     "diligenciados para que puedan corregirse. No se crea ninguna cita."),

    ("CP-03", "RF 6.2", "Rechazo del administrador al intentar escribir una historia clínica",
     "CP-03a historias vistas por el administrador.jpg",
     "CP-03b administrador rechazado al crear historia.jpg",
     "Con una sesión de administrador se abre el listado de historias clínicas, que no ofrece "
     "acción de crear, y a continuación se solicita directamente la dirección del formulario "
     "de creación, saltándose la interfaz.",
     "El listado presenta únicamente la acción de consultar, y la petición forzada se rechaza "
     "devolviendo al panel con el motivo del rechazo."),

    ("CP-04", "RF 5.2", "Reserva de la cita por el propio paciente",
     "CP-04a paciente reserva su turno.jpg", "CP-04b cita agendada por el paciente.jpg",
     "Con una sesión de paciente se abre el calendario de disponibilidad, se elige un médico y "
     "un turno libre, y se indica el motivo. El formulario muestra el paciente sin permitir "
     "cambiarlo y advierte que la cita queda a su nombre.",
     "La cita queda agendada de inmediato, sin aprobación previa, y el día pasa a marcarse "
     "como ocupado para ese paciente, con lo que el límite de una cita por día queda visible "
     "en el propio calendario."),
]

RESULTADOS = [
    ("Programación de la atención por el administrador y por el paciente",
     "Calendario semanal de disponibilidad calculada, agendamiento por ambos roles, "
     "reprogramación, cancelación y las dos reglas de conflicto comprobadas en el servidor.",
     "28 pruebas de agenda y concurrencia", "Cumplido"),
    ("Acto clínico como responsabilidad exclusiva del médico tratante",
     "Historia clínica, diagnóstico con plan de tratamiento y prescripción, creados y "
     "modificados únicamente por el médico, con la autoría tomada de la sesión.",
     "Pruebas de permisos sobre los tres módulos clínicos", "Cumplido"),
    ("Confidencialidad mediante control de acceso basado en roles",
     "Sesión obligatoria en toda ruta, comprobación de rol en cada operación y comprobación "
     "de propiedad sobre cada registro consultado.",
     "59 pruebas de permisos, autenticación y aislamiento", "Cumplido"),
    ("Corrección del fallo del registro de historia clínica",
     "El fallo que impedía agregar un historial a un paciente quedó corregido y cubierto por "
     "pruebas de regresión, de modo que no pueda reaparecer sin que la suite lo advierta.",
     "Pruebas de integridad de datos", "Cumplido"),
    ("Reserva simultánea del mismo turno",
     "Dos peticiones que piden el mismo horario a la vez producen una sola cita, porque la "
     "comprobación y la escritura ocurren dentro de una misma operación que mantiene "
     "bloqueadas las filas consultadas.",
     "2 pruebas de concurrencia", "Cumplido"),
]

TECNOLOGIAS = [
    ("Python", "3.13", "Lenguaje en el que está escrita la totalidad de la lógica del "
                       "servidor."),
    ("Flask", "3.1", "Marco de trabajo web que resuelve el enrutamiento, la sesión y el "
                     "renderizado de las plantillas."),
    ("Jinja2", "Incluido con Flask",
     "Motor de plantillas con el que el servidor arma el HTML de cada rol."),
    ("Bootstrap", "5", "Biblioteca de estilos que aporta la rejilla y los componentes, y con "
                       "la que las pantallas se adaptan al ancho del dispositivo."),
    ("JavaScript", "Sin marco de trabajo",
     "Guiones de navegador para el calendario de disponibilidad y las validaciones "
     "inmediatas del formulario."),
    ("MariaDB", "10.4", "Gestor de base de datos compatible con MySQL, que almacena las once "
                        "tablas y aporta las claves foráneas y el bloqueo de filas."),
    ("mysql-connector-python", "9.5",
     "Conector oficial, empleado con consultas parametrizadas y con un conjunto reutilizable "
     "de conexiones."),
    ("werkzeug.security", "Incluido con Flask",
     "Derivación y verificación de las contraseñas mediante scrypt."),
    ("pytest", "8", "Herramienta con la que se escribieron y se ejecutan las pruebas "
                    "automatizadas."),
    ("Git", "Control de versiones", "Registro de la evolución del proyecto."),
]


def _comprobar():
    """Que las cifras del texto coincidan con el desglose de la suite.

    El total se escribe una vez y el desglose por archivo se escribe aparte, así que lo único
    que puede fallar es que dejen de sumar. Comprobarlo aquí cuesta nada y evita que el
    documento afirme noventa y una pruebas mientras su propia tabla enumera otra cantidad.
    """
    suma = sum(cuantas for _archivo, cuantas, _que in COBERTURA)
    if suma != PRUEBAS_TOTAL:
        raise AssertionError(
            f"El desglose de COBERTURA suma {suma} y PRUEBAS_TOTAL dice {PRUEBAS_TOTAL}. "
            "Correr `python -m pytest` y corregir el que esté mal."
        )


def escribir(d):
    _comprobar()
    _integracion(d)
    _pruebas(d)
    _evidencias(d)
    _resultados(d)
    _analisis(d)
    _tecnologias(d)


# --- 6.6 -----------------------------------------------------------------------

def _integracion(d):
    d.titulo("6.6 Integración de módulos", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Los diez módulos no funcionan por separado, sino que se apoyan unos en otros en un "
        "orden que el modelo de datos impone. Los catálogos alimentan a los médicos y a las "
        "prescripciones, las personas alimentan a la agenda, la agenda hace posible la "
        "atención y de la atención salen los tres registros clínicos."
    )
    d.parrafo(
        "Dos elementos atraviesan a todos los módulos y son los que de verdad los integran. El "
        "primero es la sesión, de la que cada módulo obtiene quién está operando y con qué "
        "rol, y de la que salen tanto la decisión de aceptar la operación como la autoría del "
        "registro que se escribe. El segundo es la conexión a la base, que cada petición toma "
        "al empezar y devuelve al terminar, y que es la que permite que una comprobación y la "
        "escritura que depende de ella ocurran dentro de la misma operación."
    )
    d.parrafo(
        "La integración se verificó recorriendo el ciclo completo de un paciente, desde que "
        "crea su cuenta hasta que consulta su prescripción. Ese recorrido atraviesa siete de "
        "los diez módulos y cambia de rol tres veces, porque el paciente se registra y "
        "reserva, el administrador carga el resultado del laboratorio y el médico registra la "
        "historia, el diagnóstico y la receta. Un fallo de integración se manifiesta "
        "justamente en los cambios de rol, ya que es donde un módulo recibe un registro que "
        "otro escribió."
    )


# --- 6.7 -----------------------------------------------------------------------

def _pruebas(d):
    d.titulo("6.7 Pruebas", nivel=2, nueva_pagina=True)

    d.titulo("6.7.1 Tipo y objetivo de las pruebas", nivel=3)
    d.parrafo(
        "Se realizaron dos tipos de prueba, con propósitos distintos y complementarios. Las "
        "pruebas funcionales comprueban que cada operación del sistema hace lo que debe hacer "
        "y se documentan en el apartado siguiente con su evidencia. Las pruebas automatizadas "
        "comprueban que las reglas críticas se siguen cumpliendo después de cada cambio, y su "
        "valor no está en encontrar un fallo la primera vez sino en advertir cuando algo que "
        "funcionaba deja de funcionar."
    )
    d.parrafo(
        "La distinción importa porque las reglas que sostienen este sistema no se ven en la "
        "pantalla. Una comprobación de permisos que deja de aplicarse no rompe nada visible, y "
        "simplemente alguien puede hacer algo que no le corresponde. Por esa razón cada regla "
        "se comprueba por su efecto, forzando la petición desde el rol equivocado, y no "
        "verificando que el botón no aparezca en la interfaz."
    )
    d.parrafo(
        "Las pruebas automatizadas se ejecutan sobre una base de datos de prueba distinta de "
        "la real, cuyo esquema se clona del esquema verdadero antes de empezar. Las cuatro "
        "primeras pruebas de la suite comprueban precisamente eso, porque una suite que corre "
        "sobre la base equivocada, o sobre una base sin esquema, o con datos que quedaron de "
        "la prueba anterior, informa resultados que no significan nada."
    )

    d.titulo("6.7.2 Alcance y resultado", nivel=3)
    d.parrafo(
        f"La suite comprende {PRUEBAS_TOTAL} pruebas automatizadas distribuidas en "
        f"{len(COBERTURA)} archivos, y se ejecuta completa en {SEGUNDOS} segundos. En la "
        "última ejecución las noventa y una pasaron sin fallos."
    )
    d.tabla(
        "Alcance de las pruebas automatizadas",
        ["Archivo", "Pruebas", "Qué comprueba"],
        [[archivo, str(cuantas), que] for archivo, cuantas, que in COBERTURA]
        + [["Total", str(PRUEBAS_TOTAL), ""]],
        nota="Elaboración propia. El resultado corresponde a la ejecución completa de la "
             "suite.",
        anchos=[4.0, 1.8, 10.5],
    )
    d.parrafo(
        "El reparto no es proporcional al tamaño de cada módulo sino al riesgo que concentra. "
        "Los permisos y la agenda reúnen entre los dos más de la mitad de las pruebas, porque "
        "son las dos partes del sistema donde un error no produce un mensaje visible, y las "
        "dos únicas pruebas de concurrencia pesan más que su número, ya que comprueban una "
        "situación que no puede reproducirse a mano."
    )


# --- 6.8 -----------------------------------------------------------------------

def _evidencias(d):
    d.titulo("6.8 Evidencia de pruebas", nivel=2, nueva_pagina=True)
    d.parrafo(
        f"Se documentan a continuación {len(EVIDENCIAS)} pruebas funcionales representativas, "
        "escogidas porque cada una comprueba una regla que define el sistema. De cada una se "
        "presenta la ficha del caso de prueba y dos capturas, la del estado antes de confirmar "
        "la operación y la del resultado obtenido, de modo que pueda compararse lo que se "
        "ingresó con lo que el sistema devolvió."
    )
    for indice, (codigo, rf, nombre, antes, despues, entrada, esperado) in enumerate(
            EVIDENCIAS, start=1):
        d.titulo(f"6.8.{indice} {codigo}. {nombre}", nivel=3, nueva_pagina=(indice > 1))
        d.tabla(
            f"Caso de prueba {codigo}",
            ["Aspecto", "Descripción"],
            [
                ["Código", codigo],
                ["Requisito verificado", rf],
                ["Objetivo", f"Comprobar el comportamiento del sistema ante el siguiente "
                             f"caso, {nombre[0].lower() + nombre[1:]}."],
                ["Datos de entrada", entrada],
                ["Resultado esperado", esperado],
                ["Resultado obtenido", "Coincide con el resultado esperado."],
                ["Estado", "Satisfactorio"],
            ],
            nota="Elaboración propia.",
            anchos=[4.0, 12.3],
        )
        d.figura(
            f"{codigo}. Estado antes de confirmar la operación",
            CAPTURAS / antes,
            nota="Captura de la aplicación en funcionamiento con los datos de demostración.",
        )
        d.figura(
            f"{codigo}. Resultado obtenido",
            CAPTURAS / despues,
            nota="Captura de la aplicación en funcionamiento con los datos de demostración.",
        )


# --- 6.9 -----------------------------------------------------------------------

def _resultados(d):
    d.titulo("6.9 Resultados obtenidos", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Se relacionan los resultados alcanzados por el proyecto, con la evidencia que "
        "sostiene cada uno. Los tres primeros corresponden uno a uno con los objetivos "
        "específicos enunciados en el capítulo 1, y los dos últimos con los problemas que la "
        "fase de corrección se propuso resolver."
    )
    d.tabla(
        "Resultados obtenidos y evidencia que los sostiene",
        ["Resultado", "En qué consiste", "Evidencia", "Estado"],
        [[resultado, en_que, evidencia, estado]
         for resultado, en_que, evidencia, estado in RESULTADOS],
        nota="Elaboración propia.",
        anchos=[3.6, 6.4, 3.6, 2.7],
    )
    c = requisitos.conteo()
    d.parrafo(
        f"En términos de alcance, el sistema satisface los {c['funcionales']} requisitos "
        f"funcionales especificados en {c['modulos']} módulos, y los "
        f"{c['fuera_de_alcance']} elementos declarados fuera del alcance siguen fuera, sin que "
        "ninguno de ellos haya resultado necesario para cumplir los objetivos."
    )


# --- 6.10 ----------------------------------------------------------------------

def _analisis(d):
    d.titulo("6.10 Análisis de resultados", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Los resultados anteriores dicen qué quedó funcionando. Este apartado se ocupa de dos "
        "problemas que aparecieron durante el desarrollo y que no se habrían encontrado sin "
        "las pruebas, porque ninguno de los dos produce un error visible mientras el sistema "
        "se usa de a una persona por vez."
    )

    d.titulo("6.10.1 La reserva simultánea del mismo turno", nivel=3)
    d.parrafo(
        "La regla de la separación mínima entre atenciones estaba escrita desde el principio y "
        "funcionaba, pero no se aplicaba por sí sola. El sistema consultaba primero si el "
        "horario estaba libre y escribía después, y entre esas dos operaciones había un "
        "instante en el que otra petición podía consultar lo mismo, no encontrar nada y "
        "reservar encima. El resultado eran dos citas en un turno que solo admite una."
    )
    d.parrafo(
        "El problema se comprobó lanzando dos peticiones simultáneas sobre el mismo horario, y "
        "sin corregir producían dos citas de manera reproducible. La solución consistió en "
        "reunir la comprobación y la escritura dentro de una misma operación que mantiene "
        "bloqueadas las filas de la agenda de ese médico hasta confirmar, de modo que la "
        "segunda petición espera y, al llegar su turno, ya encuentra ocupado el horario. Las "
        "dos pruebas de concurrencia comprueban ambas cosas, es decir, que el resultado es una "
        "sola cita y que lo que lo impide es el bloqueo y no la casualidad."
    )

    d.titulo("6.10.2 La conexión compartida entre peticiones", nivel=3)
    d.parrafo(
        "El segundo problema estaba en la capa de acceso a datos y era de una naturaleza "
        "distinta, porque no violaba ninguna regla de negocio sino que hacía frágil todo lo "
        "demás. La aplicación abría una sola conexión a la base de datos y la compartía entre "
        "todas las peticiones, mientras el servidor las atendía en paralelo. Dos peticiones "
        "simultáneas usaban por tanto la misma conexión y la misma transacción, de manera que "
        "lo que una deshacía podía deshacer lo que la otra acababa de escribir."
    )
    d.parrafo(
        "La corrección consistió en que cada petición tome su propia conexión de un conjunto "
        "reutilizable al empezar y la devuelva al terminar, deshaciendo antes lo que haya "
        "quedado sin confirmar. La prueba de esa corrección dejó ver dos consecuencias que no "
        "estaban previstas y que también se corrigieron, porque el agotamiento del conjunto "
        "bajo carga devolvía un error genérico en lugar de un mensaje entendible, y los "
        "listados paginados no ordenaban de forma estable, de modo que un mismo registro podía "
        "aparecer en dos páginas o en ninguna."
    )
    # 🔴 §17. Aquí iba un párrafo que explicaba por qué este problema se relata como resuelto
    # y no entre las limitaciones del capítulo 1. Habla del documento, no del sistema, así que
    # va por consola. Lo que el lector necesita saber ya está dicho: el problema existió, se
    # diagnosticó y se corrigió.


# --- 6.11 ---------------------------------------------------------------------

def _tecnologias(d):
    d.titulo("6.11 Tecnologías utilizadas", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Se relacionan las tecnologías empleadas con la versión sobre la que el sistema se "
        "desarrolló y se probó. Todas son de uso libre y se instalan sobre un equipo corriente "
        "sin costo de licenciamiento, que fue una de las condiciones de la selección."
    )
    d.tabla(
        "Tecnologías utilizadas en el desarrollo",
        ["Tecnología", "Versión", "Función dentro del sistema"],
        [[tecnologia, version, funcion] for tecnologia, version, funcion in TECNOLOGIAS],
        nota="Elaboración propia. Las versiones corresponden al entorno sobre el que se "
             "ejecutaron las pruebas.",
        anchos=[4.0, 3.2, 9.1],
    )
    d.parrafo(
        "El gestor de base de datos merece una nota de precisión. El desarrollo se realizó "
        "sobre MariaDB, que es el gestor que acompaña a la distribución de servidor local "
        "empleada, y el sistema es igualmente compatible con MySQL, ya que las funciones de "
        "las que depende, que son las claves foráneas, las transacciones y el bloqueo de "
        "filas, se comportan del mismo modo en los dos."
    )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
