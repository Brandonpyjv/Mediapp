# -*- coding: utf-8 -*-
"""
E4 — Cierre. Conclusiones, referencias bibliográficas y anexos.

**Las referencias se construyen desde `FUENTES`**, el mismo diccionario del que salen las citas
del capítulo 2. Escribir la lista aparte lleva siempre al mismo defecto, que es una fuente
citada en el cuerpo y ausente de la lista, o una lista con fuentes que nadie citó. Aquí el
generador comprueba las dos cosas al importarse y se detiene si alguna falla.

Las conclusiones se ordenan por los tres objetivos específicos y **declaran el cumplimiento con
la evidencia detrás**, no con una afirmación. Esa es la razón por la que el capítulo 1 se cerró
con objetivos acotados: uno que prometa de más no puede declararse cumplido.
"""
import re
from pathlib import Path

import casos_de_uso
import esquema
import requisitos
from e4_cap2 import FUENTES

GENERADOR = Path(__file__).resolve().parent

ANEXOS = [
    ("Anexo A", "Especificación de requisitos funcionales y no funcionales",
     "Catálogo completo de los requisitos funcionales agrupados en diez módulos y de los no "
     "funcionales en siete categorías, con su priorización por valor y urgencia, la matriz "
     "MoSCoW derivada de esa priorización, las capacidades excluidas del alcance y la "
     "trazabilidad frente a los objetivos específicos.",
     "MediApp - Requisitos Funcionales y No Funcionales"),
    ("Anexo B", "Diagramas de casos de uso",
     "Los once diagramas de casos de uso del sistema, uno general y diez por módulo, con los "
     "tres actores humanos, el actor Sistema y las relaciones de inclusión y de extensión "
     "entre casos.",
     "MediApp - Diagramas de Casos de Uso"),
    ("Anexo C", "Documentación de casos de uso",
     "Fichas de los casos de uso, completas para los críticos y en formato breve para los "
     "restantes, cada una con las tablas del modelo de datos que toca y con la matriz de "
     "trazabilidad en las dos direcciones.",
     "MediApp - Documentacion de Casos de Uso"),
    ("Anexo D", "Diccionario de datos",
     "Descripción de las once tablas del esquema con todas sus columnas, su tipo de dato, su "
     "obligatoriedad, el papel que cumplen como clave y el significado del dato que "
     "almacenan, leída del propio motor de base de datos.",
     "MediApp - Diccionario de Datos"),
]


def escribir(d):
    _conclusiones(d)
    _referencias(d)
    _anexos(d)


# --- Conclusiones --------------------------------------------------------------

def _conclusiones(d):
    r = requisitos.conteo()
    cu = casos_de_uso.conteo()
    bd = esquema.conteo()

    d.titulo("CONCLUSIONES", nivel=1, nueva_pagina=True)
    d.parrafo(
        f"El proyecto desarrolló MediApp, un sistema web de agendamiento de citas médicas y "
        f"gestión del acto clínico con acceso diferenciado para administrador, médico y "
        f"paciente. El sistema comprende {r['modulos']} módulos funcionales que satisfacen "
        f"{r['funcionales']} requisitos funcionales y {r['no_funcionales']} no funcionales, "
        f"opera sobre {bd['tablas']} tablas con {bd['columnas']} columnas y "
        f"{bd['foraneas']} claves foráneas, y sus funcionalidades están descritas en "
        f"{cu['casos']} casos de uso."
    )
    d.parrafo(
        "El primer objetivo específico se cumplió. La programación de la atención dejó de ser "
        "una lista que alguien debe interpretar y pasó a ser un calendario semanal de "
        "disponibilidad calculada, sobre el que agendan tanto el administrador como el propio "
        "paciente. Las dos reglas que impiden una agenda imposible, que son la separación "
        "mínima de treinta minutos entre atenciones del mismo médico y el límite de una cita "
        "por paciente y por día, se comprueban en el servidor y no en la pantalla, y quedaron "
        "cubiertas por las pruebas automatizadas de agenda y de concurrencia."
    )
    d.parrafo(
        "El segundo objetivo específico se cumplió. La historia clínica, el diagnóstico con su "
        "plan de tratamiento y la prescripción son escritura exclusiva del médico tratante, y "
        "el administrador, que en el resto del sistema puede hacerlo todo, aquí solo puede "
        "consultar. La autoría de esos registros se toma de la sesión en curso y nunca del "
        "formulario enviado, de modo que la firma de quien atiende no depende de lo que llegue "
        "en la petición."
    )
    d.parrafo(
        "El tercer objetivo específico se cumplió en los términos en que fue enunciado. La "
        "confidencialidad se garantiza mediante control de acceso basado en roles, que en la "
        "práctica son tres comprobaciones sucesivas, esto es, que exista sesión, que el rol "
        "tenga permitida la operación y que el registro pertenezca a quien lo pide. La tercera "
        "es la que impide que un paciente autenticado alcance la historia clínica de otro "
        "cambiando un número en la dirección, y sin ella el sistema tendría control por rol "
        "pero no confidencialidad entre pacientes."
    )
    d.parrafo(
        "La decisión de que el paciente reserve su propia cita sin aprobación previa se apartó "
        "del planteamiento inicial y demostró ser acertada. Un agendamiento en el que la "
        "solicitud queda esperando la confirmación de un tercero conserva la demora que la "
        "herramienta viene a eliminar, y sustituye una fila en la ventanilla por una fila "
        "electrónica. El control administrativo no desapareció, se trasladó a después de la "
        "reserva, y la delegación quedó acotada por el hecho de que el paciente reserva "
        "únicamente para sí mismo."
    )
    d.parrafo(
        "El desarrollo confirmó que las reglas que sostienen un sistema de este tipo no se "
        "descubren en el enunciado inicial de requisitos, sino cuando alguien intenta usar el "
        "sistema y este se lo permite. Los dos problemas más serios que se encontraron, que "
        "son la doble reserva de un mismo turno y la conexión a la base de datos compartida "
        "entre peticiones simultáneas, tienen en común que ninguno se manifiesta mientras el "
        "sistema se usa de a una persona por vez. Encontrarlos exigió provocarlos, y "
        "corregirlos exigió mover la comprobación al mismo lugar donde ocurre la escritura."
    )
    d.parrafo(
        "De ahí se sigue la conclusión metodológica del trabajo. En un sistema cuyo valor "
        "reside en lo que impide, la verificación manual resulta insuficiente, porque un "
        "control de acceso que deja de aplicarse no produce ningún error visible y "
        "sencillamente permite lo que no debería. Las pruebas automatizadas no se incorporaron "
        "para demostrar que el sistema funciona, sino para advertir cuando algo que funcionaba "
        "deja de hacerlo, y esa es la diferencia entre un sistema que se probó una vez y uno "
        "que puede seguir modificándose sin perder lo que ya garantizaba."
    )
    d.parrafo(
        "El sistema queda además preparado para crecer sin rehacerse. Los roles se conceden a "
        "la función y no a la persona, las tablas de apoyo son catálogos y no listas escritas "
        "en el código, y ningún registro se elimina físicamente, de modo que incorporar un "
        "profesional, una especialidad o un medicamento no exige tocar el programa y dar de "
        "baja a alguien no borra lo que firmó ni lo que recibió."
    )
    d.parrafo(
        "Quedan fuera de esta versión, por decisión expresa de alcance, la notificación "
        "automática de la cita, la teleconsulta, la facturación, la firma digital certificada "
        "de la historia clínica, el cifrado de la información en reposo y en tránsito, el "
        "respaldo automático y la integración con sistemas externos. Ninguna de ellas resultó "
        "necesaria para cumplir los objetivos, y todas fueron evaluadas y descartadas con su "
        "razón escrita, de manera que su ausencia obedece a una decisión y no a un olvido. La "
        "más significativa es el cifrado, porque depende de la infraestructura de despliegue y "
        "no del programa, y es la que explica que el tercer objetivo se enunciara acotado al "
        "control de acceso por roles."
    )


# --- Referencias ---------------------------------------------------------------

def _referencias(d):
    d.titulo("REFERENCIAS BIBLIOGRÁFICAS", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Las referencias se presentan en orden alfabético, según el estilo APA en su séptima "
        "edición.", sangria=False
    )
    d.parrafo()
    for _, referencia in sorted(FUENTES.values(), key=lambda fuente: fuente[1].lower()):
        # Sangría francesa: la primera línea al margen y las siguientes desplazadas, que es
        # como APA presenta cada entrada de la lista.
        p = d.parrafo(referencia, sangria=False)
        p.paragraph_format.left_indent = SANGRIA_FRANCESA
        p.paragraph_format.first_line_indent = -SANGRIA_FRANCESA


# --- Anexos --------------------------------------------------------------------

def _anexos(d):
    d.titulo("ANEXOS", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Se relacionan los documentos que acompañan a este trabajo y que contienen el detalle "
        "completo de los artefactos de análisis y diseño. Al cuerpo del documento se llevó una "
        "selección de cada uno, escogida por lo que demuestra, y aquí consta la referencia al "
        "material íntegro."
    )
    d.tabla(
        "Anexos del documento",
        ["Anexo", "Documento", "Contenido"],
        [[codigo, titulo, contenido] for codigo, titulo, contenido, _archivo in ANEXOS],
        nota="Elaboración propia. Los cuatro anexos se entregan como documentos "
             "independientes.",
        anchos=[1.9, 4.6, 9.8],
    )
    # 🔴 §17. Aquí iba un párrafo que explicaba que los anexos y el documento salen de las
    # mismas fuentes de datos y por eso no pueden contradecirse. Es cierto y es lo que sostiene
    # la coherencia del conjunto, pero habla de cómo se produjo el documento y no del sistema.
    # Va por consola.


SANGRIA_FRANCESA = None    # se resuelve al importar, con el valor del motor de formato


def _preparar():
    from apa import SANGRIA
    global SANGRIA_FRANCESA
    SANGRIA_FRANCESA = SANGRIA


def _comprobar_citas():
    """Ninguna fuente puede quedar sin citar, ni citarse una que no esté declarada."""
    texto = "".join(ruta.read_text(encoding="utf-8")
                    for ruta in GENERADOR.glob("e4_*.py"))
    citadas = set(re.findall(r"cita\('([a-z0-9]+)'\)", texto))
    declaradas = set(FUENTES)
    sin_citar = declaradas - citadas
    sin_declarar = citadas - declaradas
    if sin_citar or sin_declarar:
        raise SystemExit(
            f"Referencias sin citar en el texto: {sorted(sin_citar)} · "
            f"Citas sin referencia declarada: {sorted(sin_declarar)}")
    return len(declaradas)


_preparar()
_comprobar_citas()


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
