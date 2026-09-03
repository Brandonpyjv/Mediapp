# -*- coding: utf-8 -*-
"""
E4 — Capítulo 6, parte A. Desarrollo, estructura, módulos y seguridad.

Cubre del 6.1 al 6.5. La parte B (`e4_cap6b.py`, T16) sigue con la integración, las pruebas, la
evidencia, los resultados y las tecnologías.

Las **diez capturas de los módulos** se tomaron el 2026-09-03 con la aplicación corriendo sobre
los datos de `Base/seed_demo.py`, con el procedimiento del §18.3 del cuaderno, y viven en
`insumos/capturas/`. Junto con las del 5.6 son las únicas imágenes del trabajo que no genera un
programa, y responden a **O15**, que pedía que los mockups correspondieran a las interfaces
reales del software.

El **6.5 es nuevo respecto de FactuGest** y aquí queda la decisión **D2**, scrypt frente a
bcrypt, descrita desde la implementación. El marco teórico del 2.1 ya argumentó por qué se
eligió; este apartado dice cómo quedó aplicada y qué más sostiene la seguridad del sistema.

Los conteos que el capítulo cita se leen de los catálogos y no se escriben: los módulos y sus
requisitos de `requisitos.py`, las tablas y las columnas de `esquema.py`.
"""
from pathlib import Path

import esquema
import requisitos
from requisitos import ENTORNO

CAPTURAS = Path(__file__).resolve().parent.parent / "insumos" / "capturas"

REQUERIMIENTOS = [
    ("Servidor de aplicación", "Procesador de dos núcleos, 4 GB de memoria",
     "Procesador de cuatro núcleos, 8 GB de memoria"),
    ("Almacenamiento", "20 GB disponibles",
     "50 GB en disco de estado sólido, con respaldo programado"),
    ("Sistema operativo del servidor", "Windows 10 o distribución Linux con soporte vigente",
     "Distribución Linux con soporte extendido"),
    ("Entorno de ejecución", "Python 3.11 o superior", "Python 3.13"),
    ("Gestor de base de datos", "MySQL 8.0 o MariaDB equivalente",
     "MySQL 8.0 con respaldo automático diario"),
    ("Servidor web", "El servidor de desarrollo del marco de trabajo",
     "Servidor de aplicación con varios procesos, detrás de un proxy inverso con HTTPS"),
    ("Equipo del usuario", "Cualquier equipo o teléfono con navegador vigente",
     "Pantalla de 1366 por 768 o superior"),
    ("Navegador", "Chrome, Firefox o Edge en versión vigente", "Chrome o Edge actualizado"),
    ("Conexión a internet", "2 Mbps", "10 Mbps con respaldo"),
]

ESTRUCTURA = [
    ("index.py", "El punto de entrada y las rutas de la aplicación. Cada ruta recibe la "
                 "petición, comprueba la sesión y el rol mediante su decorador, aplica las "
                 "reglas de negocio y responde."),
    ("database.py", "El acceso a datos. Entrega a cada petición una conexión tomada de un "
                    "conjunto reutilizable y la devuelve al terminar, deshaciendo lo que haya "
                    "quedado sin confirmar."),
    ("date_validators.py", "Las reglas de fecha y hora, entre ellas la que decide si una cita "
                           "ya pasó, que es la misma para agendar, editar y cancelar."),
    ("validators.py", "Las validaciones reutilizables de los formularios."),
    ("templates/", "Las plantillas de la interfaz, con una carpeta por módulo, una plantilla "
                   "base de la que heredan todas y el menú lateral que cambia con el rol."),
    ("templates/static/", "Las hojas de estilo, los guiones de navegador y las imágenes."),
    ("Base/", "El esquema de la base de datos, las migraciones numeradas y el sembrado de "
              "datos de demostración."),
    ("tests/", "Las pruebas automatizadas y su configuración."),
]

# (nombre del módulo, archivo de la captura, qué es, qué muestra la pantalla, la decisión)
MODULOS = [
    ("Autenticación y sesión", "MOD-01 autenticacion y sesion.jpg",
     "Controla quién entra al sistema y a qué panel llega. Comprende el ingreso con "
     "credenciales, el cierre de sesión y el registro público con el que una persona crea su "
     "propia cuenta de paciente.",
     "La captura corresponde al registro público, que pide en un solo formulario los datos "
     "personales del paciente y las credenciales de la cuenta, porque de ese envío salen dos "
     "filas, una en la tabla de cuentas y otra en la de pacientes.",
     "El sistema no pide elegir el perfil al entrar. El rol se determina al validar las "
     "credenciales y de él depende el panel al que se llega, ya que pedirle al usuario que "
     "escoja su perfil sería dejar que un paciente entre como médico."),

    ("Gestión de usuarios", "MOD-02 gestion de usuarios.jpg",
     "Administra las cuentas de acceso con su rol asignado y su estado. Es donde se decide de "
     "qué es capaz cada persona, porque el rol que aquí se concede es el que después leen "
     "todos los controles de acceso.",
     "El listado presenta el nombre de usuario, el documento de la persona asociada, el rol y "
     "el estado. La columna de contraseña muestra una máscara fija y no el valor almacenado, "
     "que además no es una contraseña sino su hash.",
     "Las cuentas se dan de baja y no se borran. Una cuenta eliminada dejaría sin autor "
     "conocido a las historias clínicas y a las recetas que firmó, de modo que la baja cambia "
     "el estado y el ingreso queda rechazado desde ese momento."),

    ("Gestión de médicos", "MOD-03 gestion de medicos.jpg",
     "Mantiene la ficha profesional de cada médico, su especialidad, sus datos de contacto y "
     "el vínculo con la cuenta con la que ingresa.",
     "El listado presenta dos columnas de estado que responden preguntas distintas. La de "
     "estado indica si el profesional sigue recibiendo pacientes, y la de acceso, si su cuenta "
     "puede iniciar sesión.",
     "Separar las dos condiciones permite lo que un solo interruptor no permitiría, porque un "
     "médico en licencia queda activo y sin acceso, y uno que ya no atiende puede conservar el "
     "acceso para consultar lo que firmó."),

    ("Gestión de pacientes", "MOD-04 gestion de pacientes.jpg",
     "Mantiene los datos personales y de contacto de las personas que reciben atención, con el "
     "vínculo opcional a la cuenta con la que consultan lo suyo.",
     "El listado presenta el tipo y el número de documento, la fecha de nacimiento y los datos "
     "de contacto. El vínculo con la cuenta es opcional, de manera que puede registrarse a un "
     "paciente que nunca va a entrar al sistema.",
     "El número de documento no puede repetirse, y esa restricción vive en la base de datos y "
     "no solamente en el formulario, porque un duplicado partiría el historial de una misma "
     "persona en dos fichas."),

    ("Agendamiento de citas", "MOD-05 agendamiento de citas.jpg",
     "Es el módulo que da razón de ser al sistema. Comprende el calendario semanal de "
     "disponibilidad, el agendamiento por parte del administrador y del propio paciente, la "
     "reprogramación y la cancelación.",
     "El listado presenta cada cita con su médico, su paciente, su fecha con hora y su estado. "
     "Las canceladas se muestran atenuadas y no desaparecen, porque su horario vuelve a "
     "quedar disponible y conviene que quede constancia de por qué la atención no ocurrió.",
     "Dos reglas gobiernan este módulo y ninguna puede declararse como restricción de la base "
     "de datos, porque no prohíben un valor repetido sino una distancia entre valores. La "
     "primera exige treinta minutos de separación entre dos atenciones del mismo médico y la "
     "segunda limita a una las citas de un paciente en un mismo día. Las dos se comprueban en "
     "el servidor dentro de la misma operación que escribe."),

    ("Historia clínica", "MOD-06 historia clinica.jpg",
     "Guarda la evolución del paciente registrada por el médico tratante. Es el registro que "
     "concentra la restricción de acceso más estricta del sistema.",
     "La captura está tomada con una sesión de administrador, y por eso la columna de acciones "
     "ofrece únicamente consultar. No hay botón de crear, ni de editar, ni de eliminar, "
     "porque ese rol no puede escribir aquí.",
     "La autoría del registro se toma de la sesión en curso y nunca del formulario enviado. La "
     "columna de médico no indica a quién se consulta sino quién escribió, y de esa firma "
     "depende la responsabilidad profesional sobre lo registrado."),

    ("Consultas y diagnósticos", "MOD-07 consultas y diagnosticos.jpg",
     "Registra el diagnóstico y el plan de tratamiento que resultan de una atención. De la "
     "consulta cuelgan después las prescripciones.",
     "El listado presenta la fecha, el diagnóstico con su tratamiento, el paciente atendido y "
     "el médico que lo registró. Como en la historia clínica, el administrador solo dispone de "
     "la acción de consultar.",
     "La consulta no puede fecharse en el futuro, porque un diagnóstico es el resultado de "
     "haber atendido y no una previsión de lo que se va a encontrar."),

    ("Prescripciones", "MOD-08 prescripciones.jpg",
     "Emite las órdenes de medicamentos derivadas de una consulta, con su cantidad y sus "
     "indicaciones.",
     "El listado presenta la cédula del paciente, la consulta que origina la receta con su "
     "fecha, el medicamento tomado del catálogo, la cantidad y las indicaciones. Sobre él hay "
     "un buscador por número de documento.",
     "El medicamento se elige de un catálogo y no se escribe libremente, lo que evita que el "
     "mismo principio activo quede registrado con tres grafías distintas y hace que la "
     "prescripción pueda leerse sin ambigüedad."),

    ("Exámenes de laboratorio", "MOD-09 examenes de laboratorio.jpg",
     "Reúne en una misma fila la solicitud del examen y el resultado que se carga después.",
     "El listado presenta el paciente, el médico solicitante, el tipo de examen, las dos "
     "fechas y el resultado. Las filas sin resultado corresponden a exámenes solicitados y "
     "todavía no procesados.",
     "Es la única función clínica que el administrador sí puede escribir, y la diferencia está "
     "en la naturaleza del registro, porque el resultado lo produce el laboratorio y no el "
     "criterio del profesional. Lo que sigue siendo del médico es solicitarlo e interpretarlo "
     "al elaborar el diagnóstico."),

    ("Catálogos", "MOD-10 catalogos.jpg",
     "Mantiene las dos listas de apoyo que el resto de los módulos consulta, que son las "
     "especialidades médicas y los medicamentos disponibles para prescribir.",
     "La captura corresponde al catálogo de medicamentos, con su descripción, su dosis de "
     "referencia y su estado.",
     "El estado de un medicamento no distingue lo activo de lo inactivo sino lo vigente de lo "
     "descontinuado, y la palabra importa. Un medicamento descontinuado deja de ofrecerse al "
     "prescribir pero sigue apareciendo en las recetas ya emitidas, de modo que llamarlo "
     "inactivo sugeriría que desapareció de un historial en el que sigue estando."),
]

SEGURIDAD = [
    ("Almacenamiento de la contraseña",
     "Se deriva con scrypt a través de la biblioteca que acompaña al marco de trabajo. En la "
     "base no existe ninguna contraseña legible y la comprobación consiste en volver a derivar "
     "la que se escribe y comparar los dos resultados."),
    ("Firma de la sesión",
     "La llave con la que se firma la cookie de sesión se lee de una variable de entorno o, en "
     "su defecto, de un archivo local excluido del control de versiones que se genera solo en "
     "el primer arranque. No está escrita en el código."),
    ("Sesión obligatoria",
     "Toda ruta del sistema, salvo el ingreso y el registro público, exige una sesión "
     "iniciada, y la comprobación se aplica antes de atender la petición y no ruta por ruta."),
    ("Comprobación del rol",
     "Cada operación verifica en el servidor que el rol de la sesión la tenga permitida. "
     "Ocultar la opción en la interfaz acompaña a esta comprobación pero no la sustituye."),
    ("Comprobación de propiedad",
     "Cuando la operación recae sobre un registro concreto se verifica además que ese registro "
     "pertenezca a quien lo pide, de modo que cambiar un número en la dirección no da acceso a "
     "lo de otra persona."),
    ("Autoría tomada de la sesión",
     "El autor de un registro clínico y el paciente de una reserva se toman de la sesión en "
     "curso y nunca de los datos enviados por el formulario."),
    ("Consultas parametrizadas",
     "Toda consulta a la base se envía con parámetros y jamás componiendo la sentencia con los "
     "valores recibidos, con lo que un dato del formulario no puede interpretarse como "
     "instrucción."),
    ("Cierre de la cuenta desactivada",
     "Una cuenta dada de baja no solo deja de poder iniciar sesión, sino que ve cerrada la "
     "sesión que tuviera abierta en su siguiente petición."),
]


def escribir(d):
    d.titulo("Capítulo 6. Desarrollo, implementación, pruebas y resultados", nivel=1,
             nueva_pagina=True)
    _requerimientos(d)
    _descripcion(d)
    _estructura(d)
    _modulos(d)
    _seguridad(d)


# --- 6.1 -----------------------------------------------------------------------

def _requerimientos(d):
    d.titulo("6.1 Requerimientos técnicos de implementación", nivel=2)
    d.parrafo(
        "Se relacionan las condiciones de infraestructura necesarias para poner el sistema en "
        "funcionamiento. La columna de mínimo corresponde a lo que permite operar, y la de "
        "recomendado a lo que conviene para un centro de salud con varios puestos de atención "
        "trabajando a la vez."
    )
    d.tabla(
        "Requerimientos técnicos de implementación",
        ["Componente", "Mínimo", "Recomendado"],
        [[componente, minimo, recomendado]
         for componente, minimo, recomendado in REQUERIMIENTOS],
        nota="Elaboración propia.",
        anchos=[4.6, 6.0, 5.7],
    )
    d.parrafo(
        "El proxy inverso con conexión cifrada aparece en la columna de recomendado y no en la "
        "de mínimo porque no lo provee el programa sino la infraestructura sobre la que se "
        "despliega. Es la razón por la cual el tercer objetivo específico del proyecto se "
        "acotó al control de acceso por roles, según se explicó en el apartado de requisitos "
        "excluidos del alcance."
    )
    d.tabla(
        "Componentes del entorno de ejecución",
        ["Componente", "Con qué está resuelto"],
        [[componente, con_que] for componente, con_que in ENTORNO],
        nota="Elaboración propia.",
        anchos=[5.0, 11.3],
    )


# --- 6.2 -----------------------------------------------------------------------

def _descripcion(d):
    c = requisitos.conteo()
    tablas = esquema.conteo()

    d.titulo("6.2 Descripción general del sistema", nivel=2, nueva_pagina=True)
    d.parrafo(
        f"MediApp es una aplicación web que presenta tres vistas sobre una misma lógica de "
        f"negocio, una por cada rol. Comprende {c['modulos']} módulos funcionales que "
        f"satisfacen {c['funcionales']} requisitos, y opera sobre {tablas['tablas']} tablas. "
        "Lo que distingue a cada vista no es la apariencia sino el conjunto de operaciones que "
        "el servidor le acepta."
    )
    d.parrafo(
        "El recorrido de una reserva ilustra cómo trabaja el sistema. El paciente abre el "
        "calendario semanal, que no es una lista de citas sino la disponibilidad ya calculada, "
        "y elige un médico, un día y una franja de treinta minutos. El servidor toma la "
        "identidad del paciente de la sesión, abre una transacción, bloquea la agenda de ese "
        "médico, vuelve a comprobar las dos reglas de conflicto sobre los datos ya "
        "bloqueados, registra la cita y confirma."
    )
    d.parrafo(
        "El orden de esos pasos no es accidental. La identidad se toma antes que nada y del "
        "lado del servidor, porque de ella depende a nombre de quién queda la cita. El bloqueo "
        "va antes de la comprobación y no después, ya que comprobar sobre datos que otra "
        "petición todavía puede cambiar equivale a no comprobar. Y la comprobación se repite "
        "dentro de la transacción aunque el calendario ya la hubiera hecho, porque entre "
        "consultar el calendario y pulsar el botón cabe otra reserva."
    )
    d.parrafo(
        "El recorrido de una atención es el que sostiene la otra mitad del sistema. El médico "
        "abre su agenda, que puede ver pero no modificar, atiende al paciente y registra lo "
        "que corresponda, esto es, la evolución en la historia clínica, el diagnóstico con su "
        "plan de tratamiento en la consulta y la prescripción sobre esa consulta. Los tres "
        "registros quedan firmados con la identidad de la sesión, y ni el administrador ni el "
        "paciente pueden crearlos ni modificarlos."
    )


# --- 6.3 -----------------------------------------------------------------------

def _estructura(d):
    d.titulo("6.3 Estructura del proyecto", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El proyecto se organiza en archivos y carpetas que corresponden a las capas descritas "
        "en la arquitectura del capítulo anterior. Esa correspondencia es deliberada, porque "
        "una organización que no refleja la arquitectura obliga a explicar dos veces lo mismo "
        "y termina divergiendo."
    )
    d.tabla(
        "Organización del proyecto",
        ["Archivo o carpeta", "Qué contiene"],
        [[donde, que] for donde, que in ESTRUCTURA],
        nota="Elaboración propia.",
        anchos=[4.2, 12.1],
    )
    d.parrafo(
        "Las migraciones merecen mención propia. El esquema de la base no se modifica a mano "
        "en cada instalación, sino que cada cambio queda escrito en un archivo numerado que se "
        "aplica en orden. De ese modo una instalación nueva y una que ya estaba en uso llegan "
        "al mismo esquema por el mismo camino, y el historial de esos archivos explica cuándo "
        "y por qué apareció cada columna."
    )


# --- 6.4 -----------------------------------------------------------------------

def _modulos(d):
    d.titulo("6.4 Módulos del sistema", nivel=2, nueva_pagina=True)
    d.parrafo(
        f"Se describen a continuación los {len(MODULOS)} módulos del sistema, con una captura "
        "de cada uno tomada de la aplicación en funcionamiento sobre los datos de "
        "demostración. Las capturas están tomadas con una sesión de administrador, salvo la "
        "del primer módulo, que corresponde al registro público y por definición ocurre antes "
        "de que exista sesión alguna."
    )
    for indice, (nombre, imagen, que_es, que_muestra, decision) in enumerate(MODULOS, start=1):
        d.titulo(f"6.4.{indice} Módulo de {nombre[0].lower() + nombre[1:]}", nivel=3,
                 nueva_pagina=(indice > 1))
        d.parrafo(que_es)
        d.figura(
            f"Módulo de {nombre[0].lower() + nombre[1:]}",
            CAPTURAS / imagen,
            nota="Captura de la aplicación en funcionamiento con los datos de demostración.",
        )
        d.parrafo(que_muestra)
        d.parrafo(decision)


# --- 6.5 -----------------------------------------------------------------------

def _seguridad(d):
    d.titulo("6.5 Seguridad implementada", nivel=2, nueva_pagina=True)
    d.parrafo(
        "La seguridad del sistema descansa en ocho medidas que operan en momentos distintos "
        "del recorrido de una petición. Ninguna de ellas basta por sí sola, y el orden en que "
        "se aplican importa tanto como su existencia."
    )
    d.tabla(
        "Medidas de seguridad implementadas",
        ["Medida", "En qué consiste"],
        [[medida, en_que] for medida, en_que in SEGURIDAD],
        nota="Elaboración propia.",
        anchos=[4.4, 11.9],
    )

    d.titulo("6.5.1 La derivación de la contraseña", nivel=3)
    d.parrafo(
        "El sistema deriva las contraseñas con scrypt, mediante la biblioteca de seguridad que "
        "acompaña al marco de trabajo. La elección se argumentó en el marco teórico, y su "
        "resumen es que scrypt exige una cantidad configurable de memoria durante el cálculo, "
        "y la memoria es un recurso caro de multiplicar en el hardware especializado con el "
        "que se prueban contraseñas en paralelo."
    )
    d.parrafo(
        "En la implementación esa decisión se traduce en dos hechos comprobables. El primero "
        "es que en la tabla de cuentas no hay ninguna contraseña legible, sino cadenas que "
        "declaran el algoritmo empleado y sus parámetros. El segundo es que la validación del "
        "ingreso compara siempre contra el resultado derivado, sin ningún camino alterno que "
        "compare la contraseña recibida con un valor almacenado en texto claro. Una cuenta "
        "cuya contraseña se insertara sin derivar sencillamente no podría iniciar sesión, que "
        "es el comportamiento correcto."
    )
    # §17. Decía «La observación recibida sobre este punto proponía emplear otra función de
    # derivación», que le habla al evaluador sobre la evaluación. La justificación técnica se
    # queda; la referencia a quién la pidió, no.
    d.parrafo(
        "Las dos funciones de derivación más difundidas para esta tarea son admitidas por las "
        "recomendaciones vigentes de seguridad en aplicaciones web, de modo que la diferencia "
        "entre ellas es de propiedades frente a un atacante con hardware especializado y no de "
        "solidez, según se detalla en el apartado 2.1."
    )

    d.titulo("6.5.2 La llave con la que se firma la sesión", nivel=3)
    d.parrafo(
        "El sistema recuerda quién está autenticado mediante una cookie firmada, y esa firma "
        "depende de una llave secreta. Mientras la llave estuvo escrita en el código, "
        "cualquiera con acceso al repositorio podía fabricar una cookie válida y presentarse "
        "como administrador sin conocer contraseña alguna, con lo que quedaban sin efecto de "
        "un golpe la comprobación de rol, el filtrado de los listados y la comprobación de "
        "propiedad."
    )
    d.parrafo(
        "La llave se resuelve ahora leyéndola de una variable de entorno, que es como se "
        "define en una instalación real, y en su defecto de un archivo local excluido del "
        "control de versiones que se genera solo en el primer arranque. El archivo existe por "
        "una razón práctica, y es que generar una llave nueva en cada arranque cerraría la "
        "sesión cada vez que el servidor se reinicia. Dos instalaciones distintas nunca "
        "comparten llave."
    )

    d.titulo("6.5.3 Los tres momentos de la comprobación", nivel=3)
    d.parrafo(
        "Una petición atraviesa tres comprobaciones antes de que el sistema acepte lo que "
        "pide, y cada una responde una pregunta distinta. La primera pregunta si hay sesión "
        "iniciada, y se aplica a todas las rutas salvo el ingreso y el registro público. La "
        "segunda pregunta si el rol de esa sesión tiene permitida la operación. La tercera "
        "pregunta si el registro sobre el que se opera pertenece a quien lo pide."
    )
    d.parrafo(
        "Las dos primeras impiden que un paciente abra el módulo de usuarios o que un "
        "administrador escriba una historia clínica. La tercera impide algo distinto y menos "
        "evidente, y es que un paciente autenticado y con permiso para consultar historias "
        "clínicas alcance la de otra persona cambiando un número en la dirección. Sin ella el "
        "sistema tendría control de acceso por rol pero no confidencialidad entre pacientes, "
        "que es justamente lo que el tercer objetivo específico se comprometió a garantizar."
    )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
