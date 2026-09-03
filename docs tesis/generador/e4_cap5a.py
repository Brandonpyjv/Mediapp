# -*- coding: utf-8 -*-
"""
E4 — Capítulo 5, parte A. Diseño de la solución y arquitectura del sistema.

Cubre del 5.1 al 5.7. La parte B (`e4_cap5b.py`, T14) sigue con el diseño de la base de datos,
el modelo entidad-relación, el modelo físico y el diccionario de datos.

**Los casos de uso se leen de `casos_de_uso.py`**, que es la misma fuente de la que salen los
diagramas del anexo E2 y las fichas del E3. La trazabilidad a las once tablas vive en la
estructura de datos, en el campo `tablas` de cada caso, y no en la prosa, de modo que el punto
5.2.2 y el anexo E3 no pueden contradecirse.

Cuatro observaciones del evaluador se resuelven aquí.

**O05 y O11**, que faltaban los actores médico y paciente en los casos de uso y que había que
ordenarlos. Los tres roles aparecen en el diagrama general y en los de módulo, y el catálogo
está ordenado por actor dentro de cada diagrama.

**O12**, que en los casos de uso no debe ir código SQL. La trazabilidad del 5.2.2 nombra
tablas, nunca sentencias, y `verificar.py` lo comprueba sobre el documento ya generado.

**O06 y O15**, que no había mockups y que debían corresponder a las interfaces reales. El 5.6
lleva capturas de la aplicación en funcionamiento con los datos de `Base/seed_demo.py`, tomadas
el 2026-09-03 y guardadas en `insumos/capturas/`. Son las únicas imágenes del trabajo que no
las genera un programa.

**O13**, ajustar el mapa de navegación. El 5.7 lleva el mapa nuevo, dibujado contra las rutas
reales y con los tres roles diferenciados.

El 5.5 retoma **D9** desde el modelo de acceso, después de que el 4.4.5 lo justificara desde la
regla de negocio. Aquí la pregunta no es por qué el paciente agenda, sino cómo se le concede esa
capacidad sin abrirle nada más.
"""
from pathlib import Path

import casos_de_uso
import figuras
from requisitos import USUARIOS

DIAGRAMAS = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"
CAPTURAS = Path(__file__).resolve().parent.parent / "insumos" / "capturas"

# Los tres diagramas de módulo que se llevan al documento. El anexo E2 trae los once. Se
# eligieron por lo que cada uno demuestra y no por tamaño: el de citas porque es donde vive la
# razón de ser del sistema y donde los tres actores concurren, el de historia clínica porque es
# la restricción que define el proyecto, y el de autenticación porque es el único con
# relaciones de inclusión encadenadas.
DIAGRAMAS_EN_EL_DOCUMENTO = [
    ("DCU-05", "DCU-05 Agendamiento de citas.png",
     "Es el único módulo en el que concurren los tres actores, y la razón es la decisión de "
     "que el paciente reserve por sí mismo. El administrador dispone de la agenda completa, el "
     "médico aparece únicamente consultando la suya y el paciente alcanza el calendario, su "
     "propia reserva y su propia cancelación."),
    ("DCU-06", "DCU-06 Historia clínica.png",
     "Muestra la restricción que define el proyecto. La creación, la edición y la eliminación "
     "cuelgan del médico, y del administrador solo cuelga la consulta, que es la única "
     "operación del sistema en la que ese rol queda por debajo de otro."),
    ("DCU-01", "DCU-01 Autenticación y sesión.png",
     "Es el diagrama con las relaciones encadenadas. La redirección al panel se incluye en el "
     "ingreso porque un ingreso que no lleva a ningún tablero no ha terminado, y la "
     "restricción por rol se incluye a su vez en la redirección porque el panel no puede "
     "armarse sin saber qué módulos tiene permitidos quien acaba de entrar."),
]

# El caso que se documenta completo en el 5.2.1, como muestra del formato del anexo E3.
CASO_DE_MUESTRA = "CU-24"

CAPTURAS_DEL_DOCUMENTO = [
    ("Pantalla de inicio de sesión", "IU-01 inicio de sesion.jpg",
     "Es el único punto de entrada al sistema. No se pide elegir el perfil, porque el rol se "
     "determina al validar las credenciales y de él depende el panel al que se llega."),
    ("Panel del administrador", "IU-02 panel del administrador.jpg",
     "Reúne las ocho acciones más frecuentes de la operación y el menú lateral completo, con "
     "los grupos de administración, atención médica y recursos."),
    ("Panel del médico", "IU-03 panel del medico.jpg",
     "Separa las acciones clínicas, que son las que este rol crea, de lo que solo consulta. El "
     "rótulo de la segunda zona declara que la agenda es de lectura, que es la restricción de "
     "este rol."),
    ("Panel del paciente", "IU-04 panel del paciente.jpg",
     "Presenta el acceso de lectura a sus propios registros y, como única acción de escritura "
     "ofrecida desde el panel, la de agendar su cita."),
    ("Calendario semanal de disponibilidad", "IU-05 calendario de disponibilidad.jpg",
     "Es la pantalla sobre la que el paciente reserva. Muestra el número de turnos libres por "
     "franja de treinta minutos, advierte de la separación mínima entre atenciones del mismo "
     "médico y marca el día en el que quien consulta ya tiene una cita."),
]

# (capa, qué contiene, dónde vive)
ARQUITECTURA = [
    ("Presentación", "Las pantallas que ve el usuario y la validación inmediata del "
     "formulario, que acompaña a la del servidor sin sustituirla.",
     "Plantillas Jinja2 con Bootstrap 5 y JavaScript sin marco de trabajo"),
    ("Control", "El enrutamiento de cada petición, la comprobación de que existe sesión y de "
     "que el rol tiene permitida la operación, y la respuesta que se devuelve.",
     "Las rutas de Flask, con sus decoradores de sesión y de rol"),
    ("Reglas de negocio", "Las comprobaciones que deciden si una operación es admisible, entre "
     "ellas los conflictos de agenda, la separación mínima entre atenciones, la validez de la "
     "fecha y la propiedad del registro que se consulta.",
     "Funciones de validación y los módulos de reglas de fecha"),
    ("Acceso a datos", "La obtención de una conexión para cada petición, la ejecución de las "
     "consultas con parámetros y la confirmación o el deshacer de la transacción.",
     "El módulo de base de datos, con un conjunto reutilizable de conexiones"),
]

LEYENDA_PERMISOS = [
    ("C", "crear registros del módulo"),
    ("E", "editar registros del módulo"),
    ("B", "eliminar registros del módulo"),
    ("L", "consultar sin poder modificar"),
    ("Asterisco", "el rol alcanza únicamente sus propios registros"),
    ("Guion", "el rol no tiene acceso al módulo"),
]

_NOMBRE_PERMISO = {
    "CEB": "Crear, editar y eliminar", "CE": "Crear y editar", "CE*": "Crear y editar la suya",
    "C": "Crear", "E": "Cargar resultados", "L": "Solo lectura",
    "L*": "Solo lectura de lo suyo", "-": "Sin acceso",
}


_LETRAS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
           "diez", "once", "doce"]


def _letras(numero):
    """Los números pequeños en palabras.

    El conteo sale de los datos, pero escrito como cifra queda «En 6 de los once módulos», que
    mezcla dígito y palabra en la misma frase.
    """
    return _LETRAS[numero] if numero < len(_LETRAS) else str(numero)


def escribir(d):
    d.titulo("Capítulo 5. Diseño de la solución y arquitectura del sistema", nivel=1,
             nueva_pagina=True)
    _actores(d)
    _casos_de_uso(d)
    _conceptual(d)
    _arquitectura(d)
    _permisos(d)
    _interfaces(d)
    _navegacion(d)


# --- 5.1 -----------------------------------------------------------------------

def _actores(d):
    d.titulo("5.1 Actores del sistema", nivel=2)
    d.parrafo(
        "Un actor es un papel que alguien desempeña frente al sistema, y no una persona. La "
        "distinción importa porque los permisos se conceden al papel, de modo que dos personas "
        "con el mismo rol pueden hacer exactamente lo mismo y una misma persona cambia de "
        "capacidades al cambiar de rol."
    )
    d.parrafo(
        "El sistema reconoce tres roles humanos, que son los que la base de datos almacena, y "
        "un cuarto actor no humano al que este trabajo atribuye las reglas que se ejecutan sin "
        "que nadie las solicite. Nombrarlo es lo que permite que los diagramas de casos de uso "
        "muestren esas reglas en lugar de dejarlas implícitas, porque una comprobación de "
        "conflicto que no aparece en ningún diagrama parece no existir hasta que rechaza una "
        "cita."
    )
    d.tabla(
        "Actores del sistema y alcance de cada uno",
        ["Actor", "Alcance"],
        [[nombre, descripcion] for nombre, descripcion in USUARIOS],
        nota="Elaboración propia. Los tres primeros corresponden a los roles almacenados en el "
             "sistema; el cuarto agrupa las reglas que se ejecutan por sí solas.",
        anchos=[3.4, 12.9],
    )
    d.parrafo(
        "Los tres roles no siguen la jerarquía habitual en la que cada nivel puede todo lo del "
        "anterior y algo más. El "
        "administrador puede prácticamente todo, salvo escribir en la historia clínica, en el "
        "diagnóstico y en la prescripción, que son justamente los registros que definen la "
        "atención. El médico no administra nada de la operación y en cambio es el único que "
        "puede producir esos tres registros. Los dos roles se cruzan en lugar de contenerse, y "
        "esa forma es la consecuencia directa de que la responsabilidad sobre el acto clínico "
        "no sea delegable."
    )


# --- 5.2 -----------------------------------------------------------------------

def _casos_de_uso(d):
    c = casos_de_uso.conteo()

    d.titulo("5.2 Diagrama de casos de uso", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Los casos de uso describen lo que cada actor consigue del sistema, enunciado como un "
        "objetivo suyo y no como una operación sobre la base de datos. La diferencia no es de "
        "estilo, porque un caso llamado «Reservar la cita propia» puede discutirse con quien "
        "va a usarlo, mientras que uno llamado «Insertar una fila en la tabla de citas» solo "
        "puede discutirse con quien va a programarlo."
    )
    d.parrafo(
        f"El análisis identificó {c['casos']} casos de uso, organizados en {c['modulos']} "
        f"diagramas de módulo, con {c['inclusiones']} relaciones de inclusión y "
        f"{c['extensiones']} de extensión. Los tres actores humanos aparecen en el diagrama "
        "general y cada diagrama de módulo muestra a los que intervienen en él."
    )
    d.figura(
        "Diagrama general de casos de uso",
        DIAGRAMAS / "DCU-00 general.png",
        nota="Elaboración propia. Los casos se agrupan por actor para evitar el cruce de "
             "líneas que produce una lista alternada.",
    )
    d.parrafo(
        "El diagrama general reúne los objetivos de más alto nivel y deja ver de un vistazo el "
        "reparto de responsabilidades. Del administrador cuelga la operación, esto es, las "
        "personas, los catálogos, la agenda y la carga de resultados de laboratorio. Del "
        "médico cuelga el acto clínico completo más la consulta de su propia agenda. Y del "
        "paciente cuelgan dos objetivos, uno de lectura sobre lo suyo y otro de escritura, que "
        "es reservar y cancelar su cita."
    )
    d.parrafo(
        f"Los {c['modulos']} diagramas de módulo constan íntegros en el anexo de diagramas de "
        "casos de uso. Se reproducen aquí tres de ellos, escogidos por lo que cada uno "
        "demuestra y no por su tamaño."
    )
    for codigo, archivo, comentario in DIAGRAMAS_EN_EL_DOCUMENTO:
        nombre = next(m[1] for m in casos_de_uso.MODULOS if m[0] == codigo)
        d.figura(
            f"Casos de uso del módulo de {nombre.lower()}",
            DIAGRAMAS / archivo,
            nota="Elaboración propia.",
        )
        d.parrafo(comentario)

    _ficha(d)
    _trazabilidad(d)


def _ficha(d):
    codigo, nombre, modulo, actores, descripcion, rf, tablas = casos_de_uso.caso(CASO_DE_MUESTRA)

    d.titulo("5.2.1 Documentación de un caso de uso", nivel=3, nueva_pagina=True)
    d.parrafo(
        "Cada caso de uso está documentado en una ficha que indica quién lo ejecuta, qué debe "
        "cumplirse antes, qué ocurre paso a paso, en qué estado queda el sistema al terminar y "
        "qué sucede cuando el curso normal se interrumpe. Se reproduce a continuación una de "
        "ellas a modo de muestra del formato; el conjunto completo consta en el anexo de "
        "documentación de casos de uso."
    )
    d.parrafo(
        "La ficha escogida es la de la reserva de la cita por parte del paciente, porque es "
        "donde se concentran las reglas propias del sistema y donde el curso alterno tiene más "
        "peso que el normal, ya que casi todo lo que este caso hace consiste en decidir si la "
        "reserva puede aceptarse."
    )
    d.tabla(
        f"Ficha del caso de uso {codigo}",
        ["Campo", "Contenido"],
        [
            ["Código", codigo],
            ["Nombre", nombre],
            ["Módulo", modulo],
            ["Actor principal", ", ".join(actores) if actores else "Sistema"],
            ["Descripción", descripcion],
            ["Precondiciones",
             "El paciente tiene una sesión iniciada con su rol, existe al menos un médico "
             "activo y el turno elegido pertenece a una fecha que todavía no ha pasado."],
            ["Curso normal",
             "1. El paciente abre el calendario semanal de disponibilidad. "
             "2. El sistema calcula los turnos libres de cada médico para la semana y los "
             "presenta. "
             "3. El paciente elige un médico, un día y una franja de treinta minutos. "
             "4. El sistema toma la identidad del paciente de la sesión, bloquea la agenda de "
             "ese médico y vuelve a comprobar las reglas de conflicto. "
             "5. El sistema registra la cita en estado agendado y confirma la reserva."],
            ["Postcondiciones",
             "La cita queda registrada a nombre de quien la solicitó y el turno deja de "
             "ofrecerse como libre, tanto a ese paciente como a cualquier otro."],
            ["Curso alterno",
             "- Si el paciente ya tiene una cita ese mismo día, la reserva se rechaza y el "
             "calendario marca el día como ocupado. "
             "- Si el médico tiene otra atención dentro de la separación mínima, el turno se "
             "presenta sin cupo y la reserva se rechaza. "
             "- Si otra petición reservó el mismo turno mientras esta se resolvía, la segunda "
             "se rechaza al liberarse el bloqueo, con lo que solo una de las dos queda en "
             "firme. "
             "- Si la fecha y la hora elegidas ya pasaron, la reserva se rechaza."],
            ["Requisitos que cubre", rf],
            ["Tablas que toca", ", ".join(tablas)],
        ],
        nota="Elaboración propia. El formato es el mismo del anexo de documentación de casos "
             "de uso.",
        anchos=[3.6, 12.7],
    )


def _trazabilidad(d):
    por_tabla = casos_de_uso.por_tabla()
    c = casos_de_uso.conteo()

    d.titulo("5.2.2 Trazabilidad de los casos de uso con el modelo de datos", nivel=3,
             nueva_pagina=True)
    d.parrafo(
        "Cada caso de uso indica sobre qué tablas del modelo de datos opera. La relación se "
        "presenta en las dos direcciones, porque cada una responde una pregunta distinta. De "
        "caso hacia tabla se responde qué toca una funcionalidad, que es lo que hace falta para "
        "saber qué se rompe al cambiarla. De tabla hacia casos se responde qué funcionalidades "
        "dependen de una tabla, que es lo que hace falta para saber a qué afecta un cambio del "
        "modelo y para comprobar que ninguna tabla del esquema sobra."
    )
    d.parrafo(
        f"La correspondencia cubre las {c['tablas']} tablas del esquema y no deja ninguna sin "
        "al menos un caso de uso que la alcance. En esta trazabilidad se nombran tablas y "
        "nunca sentencias de consulta, de manera que la documentación de casos de uso se "
        "mantenga en el plano del análisis y no en el de la implementación."
    )
    d.tabla(
        "Trazabilidad de las tablas del modelo hacia los casos de uso",
        ["Tabla", "Casos de uso que la alcanzan", "Cantidad"],
        [[tabla, ", ".join(lista), str(len(lista))]
         for tabla, lista in por_tabla.items()],
        nota="Elaboración propia. La relación de cada caso hacia las tablas que toca consta en "
             "el anexo de documentación de casos de uso.",
        anchos=[2.6, 11.2, 2.5],
    )
    ordenadas = sorted(por_tabla.items(), key=lambda par: len(par[1]), reverse=True)
    (primera, casos_primera), (segunda, casos_segunda) = ordenadas[0], ordenadas[1]
    d.parrafo(
        f"La distribución señala dónde está el centro del modelo, y son las dos tablas que "
        f"guardan a las personas. La de {primera} interviene en {len(casos_primera)} casos de "
        f"uso y la de {segunda} en {len(casos_segunda)}, muy por encima de cualquier otra, y "
        "no por su tamaño sino por su posición, ya que toda cita relaciona a una con la otra y "
        "todo registro clínico nombra al profesional que lo firma y al paciente al que "
        "corresponde. Es también la razón por la cual dar de baja a una persona no puede "
        "borrarla, porque su desaparición dejaría sin autor o sin sujeto a todo lo que ya está "
        "registrado."
    )


# --- 5.3 -----------------------------------------------------------------------

def _conceptual(d):
    # Sin salto: el 5.2.2 termina con un párrafo corto en lo alto de la página y un salto aquí
    # la dejaría casi entera en blanco.
    d.titulo("5.3 Diagrama conceptual", nivel=2)
    d.parrafo(
        "El diagrama conceptual presenta qué hace el sistema y con quién se relaciona, sin "
        "entrar en cómo está construido. Sirve para fijar el alcance antes de discutir la "
        "solución técnica, y responde a la pregunta de qué queda dentro y qué queda fuera."
    )
    d.figura(
        "Diagrama conceptual del sistema",
        DIAGRAMAS / "FIG-conceptual.png",
        nota="Elaboración propia. Los bloques del interior son las capacidades del sistema y "
             "lo del exterior son los actores que las utilizan.",
    )
    d.parrafo(
        "Lo que el diagrama deja fuera es tan significativo como lo que encierra. No aparecen "
        "la facturación, la teleconsulta, la firma digital certificada ni la integración con "
        "sistemas externos, que son las capacidades descartadas de forma expresa en el "
        "apartado de requisitos excluidos del alcance. Un diagrama conceptual que las "
        "dibujara comprometería al proyecto con un sistema distinto del que se formuló."
    )


# --- 5.4 -----------------------------------------------------------------------

def _arquitectura(d):
    d.titulo("5.4 Arquitectura del sistema", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El sistema se organiza en cuatro capas, de manera que cada una dependa únicamente de "
        "la que tiene debajo y ninguna necesite conocer los detalles de las demás. La ventaja "
        "de esa separación no es teórica, y consiste en que una regla de negocio se corrige en "
        "un solo lugar y queda corregida para todas las pantallas que la usan."
    )
    d.figura(
        "Arquitectura del sistema por capas",
        DIAGRAMAS / "FIG-arquitectura.png",
        nota="Elaboración propia. Cada capa se apoya en la inmediatamente inferior.",
    )
    d.tabla(
        "Responsabilidad de cada capa",
        ["Capa", "De qué responde", "Con qué está construida"],
        [[capa, responsabilidad, con_que] for capa, responsabilidad, con_que in ARQUITECTURA],
        nota="Elaboración propia.",
        anchos=[3.0, 8.0, 5.3],
    )
    # 🔴 §17, ampliado por el autor el 2026-09-03. Aquí iban dos párrafos, uno sobre la
    # diferencia entre ocultar una opción y prohibirla, y otro sobre la conexión por petición
    # y las consultas con parámetros. Los dos hablan del sistema y no del documento, así que
    # la regla anterior los admitía, pero el autor los mandó quitar igual: el documento
    # **enuncia** lo que el sistema es y no le razona al lector cada matiz. La tabla de arriba
    # ya dice de qué responde cada capa, y lo que aquí se argumentaba se retoma donde
    # corresponde, que es el 5.5 para el control de acceso y el 6.5 para la seguridad.


# --- 5.5 -----------------------------------------------------------------------

def _permisos(d):
    d.titulo("5.5 Modelo de control de acceso y matriz de permisos", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El control de acceso del sistema sigue el modelo basado en roles descrito en el marco "
        "teórico. Los permisos se conceden al rol y las personas los reciben por pertenecer a "
        "él, de modo que incorporar a un profesional consiste en asignarle un rol y no en "
        "revisar una lista de autorizaciones."
    )
    d.parrafo(
        "La comprobación ocurre en tres momentos, y los tres son necesarios. Al llegar la "
        "petición se verifica que exista una sesión iniciada. Enseguida se verifica que el rol "
        "de esa sesión tenga permitida la operación solicitada. Y cuando la operación recae "
        "sobre un registro concreto se verifica además que ese registro pertenezca a quien lo "
        "pide, que es lo que impide que un paciente autenticado consulte la historia clínica "
        "de otro cambiando un número en la dirección."
    )
    d.figura(
        "Matriz de permisos por rol y por módulo",
        DIAGRAMAS / "FIG-permisos.png",
        nota="Elaboración propia. El asterisco indica que el rol alcanza únicamente sus "
             "propios registros.",
    )
    d.tabla(
        "Convenciones empleadas en la matriz de permisos",
        ["Símbolo", "Significado"],
        [[simbolo, significado] for simbolo, significado in LEYENDA_PERMISOS],
        nota="Elaboración propia.",
        anchos=[3.0, 13.3],
    )
    d.tabla(
        "Permisos concedidos a cada rol sobre cada módulo",
        ["Módulo", "Administrador", "Médico", "Paciente"],
        [[tabla, _NOMBRE_PERMISO[admin], _NOMBRE_PERMISO[medico], _NOMBRE_PERMISO[paciente]]
         for tabla, admin, medico, paciente in figuras.PERMISOS],
        nota="Elaboración propia. Es la misma información de la figura anterior, escrita en "
             "palabras.",
        anchos=[3.1, 4.6, 4.3, 4.3],
    )
    d.parrafo(
        "Tres rasgos de la matriz distinguen a este sistema de una jerarquía de permisos "
        "corriente."
    )
    # Los conteos se sacan de la propia matriz. Escritos a mano decían «en diez de los once
    # módulos», que con tres de solo lectura no cuadraba, y ese es justamente el tipo de dato
    # que nadie recalcula al releer.
    plenos = [t for t, admin, *_ in figuras.PERMISOS if admin == "CEB"]
    clinicos = [t for t, admin, *_ in figuras.PERMISOS
                if admin == "L" and t in ("historia", "consulta", "receta")]
    d.parrafo(
        f"La primera es la restricción del administrador. En {_letras(len(plenos))} de los "
        f"once módulos puede crear, editar y eliminar, y en {_letras(len(clinicos))} de ellos, "
        "que son la historia clínica, la consulta y la prescripción, solo puede consultar. "
        "No es una limitación de "
        "comodidad, sino la traducción al sistema de que el diligenciamiento del registro "
        "clínico corresponde a quien interviene en la atención y de que la responsabilidad "
        "acompaña a la firma."
    )
    d.parrafo(
        "El módulo de roles aparece también como de solo lectura para el administrador, pero "
        "por una razón distinta y sin relación con el acto clínico. Los tres roles del sistema "
        "no son un catálogo que se administre desde una pantalla, sino la base sobre la que "
        "está escrito todo el control de acceso, de modo que agregar uno nuevo no consistiría "
        "en crear una fila sino en decidir qué puede hacer, que es una decisión de diseño y no "
        "de operación."
    )
    d.parrafo(
        "La segunda es que el examen de laboratorio no sigue esa regla, y el administrador sí "
        "puede cargarlo. La diferencia está en la naturaleza del registro, porque el resultado "
        "de un examen lo produce el laboratorio y no el criterio del profesional, de manera "
        "que cargarlo es una tarea administrativa. Lo que sigue siendo del médico es "
        "interpretarlo al elaborar el diagnóstico."
    )
    d.parrafo(
        "La tercera es la fila de las citas, y es la que corresponde a la decisión justificada "
        "en el apartado 4.4.5. El paciente, que en todo lo demás solo lee, aquí crea y edita, "
        "aunque acotado a lo suyo. Visto desde el modelo de acceso, la pregunta ya no es por "
        "qué se le concede esa capacidad sino cómo se le concede sin abrirle nada más, y la "
        "respuesta está en el tercer momento de comprobación descrito arriba. La identidad del "
        "paciente se toma de la sesión y no del formulario, así que la cita queda a nombre de "
        "quien la pidió aunque la petición diga otra cosa, y la vía por la que puede reservar "
        "es únicamente el calendario de disponibilidad, no el formulario completo de "
        "agendamiento, que permite elegir a qué paciente se agenda y sigue siendo del "
        "administrador."
    )
    d.parrafo(
        "El médico, en cambio, no reserva citas por ninguna vía. Su fila en la columna de "
        "citas es de solo lectura sobre las suyas, que es la traducción de que la agenda se le "
        "entrega y no la construye él."
    )


# --- 5.6 -----------------------------------------------------------------------

def _interfaces(d):
    d.titulo("5.6 Interfaces del sistema", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Se presentan a continuación las pantallas principales del sistema. No son bocetos "
        "previos al desarrollo sino capturas de la aplicación en funcionamiento, tomadas sobre "
        "la base de datos de demostración, de modo que lo que muestran es lo que el sistema "
        "hace hoy."
    )
    d.parrafo(
        "El diseño obedece a una regla que atraviesa las tres vistas, y es que cada rol "
        "encuentra en su panel únicamente lo que puede hacer. No hay una pantalla común con "
        "opciones deshabilitadas, porque una opción visible pero inactiva invita a preguntar "
        "por qué no funciona, mientras que un panel que solo ofrece lo permitido se explica "
        "solo. La comprobación del servidor no depende de esta decisión y se aplica igual."
    )
    for titulo, archivo, comentario in CAPTURAS_DEL_DOCUMENTO:
        d.figura(
            titulo,
            CAPTURAS / archivo,
            nota="Captura de la aplicación en funcionamiento con los datos de demostración.",
        )
        d.parrafo(comentario)
    d.parrafo(
        "Los tres paneles puestos uno junto a otro dejan ver la matriz de permisos convertida "
        "en interfaz. El del administrador ofrece ocho acciones y el menú lateral completo. El "
        "del médico ofrece cuatro acciones clínicas y separa lo que crea de lo que solo "
        "consulta. El del paciente ofrece cinco accesos de lectura y una sola acción de "
        "escritura. Ninguno de los tres muestra una opción que su rol no pueda ejecutar."
    )
    d.parrafo(
        "El calendario es la pantalla que resuelve el problema del que partió el proyecto. "
        "Presenta la disponibilidad ya calculada, en "
        "franjas de treinta minutos y con el número de turnos libres en cada una, de modo que "
        "quien reserva no tiene que interpretar una lista de citas para deducir qué queda "
        "libre. Advierte además de la separación mínima entre atenciones del mismo médico, que "
        "es la razón por la cual una franja puede aparecer sin cupo aunque a esa hora exacta "
        "no haya ninguna cita, y marca el día en el que quien consulta ya tiene una cita, con "
        "lo que la regla de una cita por paciente y por día se ve antes de intentar romperla."
    )


# --- 5.7 -----------------------------------------------------------------------

def _navegacion(d):
    # Sin salto: el 5.6 cierra con un párrafo corto en lo alto de la página.
    d.titulo("5.7 Mapa de navegación", nivel=2)
    d.parrafo(
        "El mapa de navegación relaciona todas las pantallas del sistema y muestra desde cuál "
        "se llega a cuál. Se organiza en tres niveles, que son la entrada, los paneles de cada "
        "rol y las pantallas de cada módulo, y distingue por color qué rol alcanza cada grupo."
    )
    d.figura(
        "Mapa de navegación del sistema",
        DIAGRAMAS / "FIG-mapa-navegacion.png",
        nota="Elaboración propia. Los grupos se colorean según el rol que puede abrirlos.",
    )
    d.parrafo(
        "El mapa hace visible una propiedad del sistema que las pantallas por separado no "
        "dejan ver, y es que no existe ningún camino que lleve de una vista de un rol a una "
        "pantalla de otro. Los tres recorridos parten del mismo punto de entrada y se separan "
        "en el momento en que se determina el rol, sin volver a cruzarse. Las pantallas "
        "compartidas, como el calendario de disponibilidad, no son una excepción, porque lo "
        "que se comparte es la dirección y no lo que se puede hacer allí, ya que el "
        "administrador reserva para cualquier paciente y el paciente únicamente para sí mismo."
    )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
