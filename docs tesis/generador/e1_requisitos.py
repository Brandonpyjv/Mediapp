# -*- coding: utf-8 -*-
"""
E1 — Especificación de requisitos funcionales y no funcionales de MediApp.

Documento aparte y **completo**, del que después se extraen para el documento de grado los
requisitos más relevantes (puntos 4.4 y 4.5). Aquí queda el registro entero, incluidos los que
por secundarios no entran al cuerpo del trabajo pero sí forman parte del sistema construido.

**Este módulo no define requisitos, los maqueta.** Los datos viven en `requisitos.py`, que es la
fuente única cerrada en T3, y de ahí los lee también el capítulo 4 del documento de grado y la
diapositiva de requisitos. Si hay que cambiar un requisito, se cambia allá y se vuelve a correr
esto.

Responde a la observación **O04** del evaluador, que decía que el modelo MoSCoW no se observaba
en el documento anterior. Lo que la responde no es la tabla sino el capítulo 5, donde la
clasificación se deriva del mismo puntaje que da la prioridad y queda justificada en lugar de
declarada.

    python e1_requisitos.py
"""
from pathlib import Path

from apa import DocumentoAPA, inicial_minuscula
from requisitos import (ENTORNO, FUERA_DE_ALCANCE, MODULOS, RNF, TRAZABILIDAD, USUARIOS,
                        conteo, moscow, por_moscow, prioridad, puntaje, todos)

SALIDA = Path(__file__).resolve().parent.parent / "entregables"
ARCHIVO = SALIDA / "MediApp - Requisitos Funcionales y No Funcionales.docx"


# --- Armado del documento -------------------------------------------------------

def construir():
    d = DocumentoAPA()

    d.portada(
        titulo="MEDIAPP",
        subtitulo="Especificación de requisitos funcionales y no funcionales",
        integrantes=["ÁNGEL JESÚS HERNÁNDEZ ARÉVALO",
                     "RICHARD ALBERTO QUIÑONES QUIÑONES"],
        grado="Documento de especificación de requisitos del proyecto de grado\n"
              "Tecnólogo en Análisis y Desarrollo de Software\n"
              "Ficha 3115426",
        institucion=["SERVICIO NACIONAL DE APRENDIZAJE (SENA)",
                     "Centro de la Industria, la Empresa y los Servicios (CIES)",
                     "Tecnólogo en Análisis y Desarrollo de Software"],
        ciudad="CÚCUTA, NORTE DE SANTANDER",
        anio=2026,
    )
    d.tabla_contenido()

    _introduccion(d)
    _descripcion_general(d)
    _funcionales(d)
    _no_funcionales(d)
    _priorizacion(d)
    _trazabilidad(d)

    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d


def _introduccion(d):
    d.titulo("1. Introducción", nivel=1)

    d.titulo("1.1 Propósito", nivel=2)
    d.parrafo(
        "Este documento especifica la totalidad de los requisitos funcionales y no funcionales "
        "de MediApp, sistema web de agendamiento de citas médicas y gestión de historias "
        "clínicas desarrollado como proyecto de grado del programa Tecnólogo en Análisis y "
        "Desarrollo de Software. Su finalidad es servir de referencia única sobre lo que el "
        "sistema debe hacer y bajo qué condiciones de calidad debe hacerlo, de modo que el "
        "desarrollo, las pruebas y la verificación del cumplimiento de los objetivos se "
        "contrasten contra un mismo enunciado."
    )
    d.parrafo(
        "Del catálogo aquí especificado se extraen, para el documento de grado, los requisitos "
        "de mayor relevancia. Este documento conserva el registro completo, incluidos aquellos "
        "que por su carácter secundario no se incorporan al cuerpo del trabajo pero sí forman "
        "parte del sistema construido."
    )

    d.titulo("1.2 Alcance del producto", nivel=2)
    d.parrafo(
        "MediApp administra la agenda de un centro de salud y protege el acto clínico que se "
        "deriva de esa agenda. Registra a los médicos con su especialidad y a los pacientes que "
        "reciben atención, presenta la disponibilidad de cada médico por semana y permite "
        "reservar una cita sobre un horario libre, reprogramarla y cancelarla. Sobre la "
        "atención prestada, el médico registra la evolución del paciente en su historia "
        "clínica, el diagnóstico y el plan de tratamiento que resultan de la cita, la "
        "prescripción de los medicamentos y la solicitud de los exámenes de laboratorio cuyo "
        "resultado carga después el personal administrativo."
    )
    d.parrafo(
        "El sistema opera con tres perfiles de acceso que no se solapan. El administrador "
        "gestiona la operación completa y la agenda, el médico es el único que puede escribir "
        "sobre la historia clínica, el diagnóstico y la receta, y el paciente consulta lo que "
        "le pertenece con dos capacidades de escritura sobre su propia cita, que son reservarla "
        "y cancelarla. Esa separación no es un detalle de la interfaz, porque se comprueba en "
        "el servidor en cada operación y es lo que sostiene el tercer objetivo específico del "
        "proyecto."
    )
    d.parrafo(
        "Quedan fuera del alcance la facturación de los servicios prestados, la teleconsulta, "
        "la notificación automática de las citas, la firma digital certificada de la historia "
        "clínica y la integración con sistemas externos. El apartado 5.4 recoge estas "
        "exclusiones con la razón de cada una, porque un documento de requisitos que solo "
        "enumera lo que el sistema hace deja al lector suponiendo el resto."
    )

    d.titulo("1.3 Definiciones y abreviaturas", nivel=2)
    d.vinetas([
        ("RF", "requisito funcional, que describe una capacidad que el sistema debe ofrecer."),
        ("RNF", "requisito no funcional, que describe una condición de calidad bajo la cual "
                "esa capacidad debe prestarse."),
        ("MoSCoW", "técnica de priorización que reparte los requisitos en cuatro categorías, "
                   "que son las de obligatorio cumplimiento, las deseables, las opcionales y "
                   "las excluidas del alcance."),
        ("Acto clínico", "conjunto de registros que el médico produce sobre un paciente, que "
                         "son la historia clínica, el diagnóstico con su tratamiento y la "
                         "prescripción."),
        ("Baja lógica", "retiro de un registro de la operación cambiando su estado en lugar de "
                        "borrarlo, de manera que lo que lo referencia siga siendo consultable."),
        ("Control de acceso basado en roles", "modelo de autorización en el que los permisos se "
                                              "conceden a un rol y las personas los reciben por "
                                              "pertenecer a él."),
        ("KDF", "función de derivación de clave, que transforma una contraseña en un valor "
                "almacenable del que no puede recuperarse la original."),
    ])

    d.titulo("1.4 Referencias del proyecto", nivel=2)
    d.parrafo(
        "Los requisitos de este documento se levantaron contra el sistema construido y no "
        "contra una intención de construirlo. Las fuentes son el código de la aplicación, con "
        "sus cincuenta y tres rutas, el esquema relacional con sus once tablas, la matriz de "
        "permisos por rol acordada con el autor del proyecto y la batería de noventa y una "
        "pruebas automatizadas que verifica las reglas críticas. No hay en este catálogo ningún "
        "requisito que no corresponda a algo que el sistema haga hoy, salvo los del apartado "
        "5.4, que se enuncian precisamente como no construidos."
    )


def _descripcion_general(d):
    d.titulo("2. Descripción general", nivel=1, nueva_pagina=True)

    d.titulo("2.1 Perspectiva del producto", nivel=2)
    d.parrafo(
        "MediApp se construyó como una aplicación web monolítica en la que el servidor arma las "
        "páginas y las entrega listas al navegador. No hay una interfaz de programación "
        "separada ni un cliente desacoplado, y la única excepción es un servicio de solo "
        "lectura que alimenta el calendario de disponibilidad. Esa decisión mantiene una sola "
        "capa donde se comprueban los permisos, porque un sistema en el que la regla de acceso "
        "se escribe dos veces termina teniendo dos reglas distintas."
    )
    d.parrafo(
        "La información se organiza en once tablas que giran alrededor del paciente, de las "
        "cuales tres guardan el acto clínico, que son la historia, la consulta y la receta, dos "
        "guardan a las personas que intervienen, que son el médico y el paciente, una guarda la "
        "agenda, otra los exámenes de laboratorio, dos son catálogos y las dos restantes "
        "sostienen el acceso al sistema. Ninguna baja de una persona borra su fila, de manera "
        "que un médico retirado del servicio conserva la autoría de todo lo que firmó."
    )

    d.titulo("2.2 Funciones principales del sistema", nivel=2)
    d.parrafo(
        "Las capacidades del sistema se agruparon en diez módulos que corresponden a los "
        "conjuntos de trabajo reales de la aplicación. La agrupación no es una comodidad de "
        "redacción, porque es la misma que organiza los diagramas de casos de uso, la "
        "descripción del sistema en el documento de grado y el reparto de las pruebas "
        "automatizadas."
    )
    d.tabla(
        "Módulos funcionales y alcance de cada uno",
        ["Código", "Módulo", "Alcance"],
        [[c, n, alcance] for c, n, alcance, _, _ in MODULOS],
        nota="Elaboración propia.",
        anchos=[1.7, 4.0, 10.8],
    )

    d.titulo("2.3 Características de los usuarios", nivel=2)
    d.parrafo(
        "El sistema reconoce tres perfiles humanos y atribuye a un cuarto actor, denominado "
        "Sistema, las reglas que se ejecutan sin que nadie las solicite. Nombrar ese cuarto "
        "actor evita que las validaciones de la agenda y las comprobaciones de permiso queden "
        "escritas como si fueran decisiones de una persona."
    )
    d.tabla(
        "Actores del sistema y alcance de su acceso",
        ["Actor", "Alcance"],
        [[a, desc] for a, desc in USUARIOS],
        nota="Elaboración propia, a partir de la matriz de permisos acordada con el autor del "
             "proyecto.",
        anchos=[3.0, 13.5],
    )

    d.titulo("2.4 Entorno operativo", nivel=2)
    d.tabla(
        "Entorno tecnológico de operación",
        ["Componente", "Tecnología"],
        [[c, t] for c, t in ENTORNO],
        nota="Elaboración propia.",
        anchos=[5.0, 11.5],
    )

    d.titulo("2.5 Restricciones y supuestos", nivel=2)
    d.parrafo(
        "La especificación se formula bajo las siguientes condiciones, cuyo incumplimiento "
        "afectaría la validez de alguno de los requisitos enunciados."
    )
    d.vinetas([
        "El sistema opera sobre una pila de servidor libre, con Python y MySQL, sin componentes "
        "de licencia propietaria.",
        "El acceso se realiza desde un navegador web vigente, sin instalación en el equipo del "
        "usuario.",
        "El cifrado del tránsito y del almacenamiento depende de la infraestructura donde se "
        "despliegue el sistema y no del programa, razón por la cual el tercer objetivo "
        "específico se acotó al control de acceso por roles.",
        "El respaldo de la información es responsabilidad de la administración del servidor de "
        "base de datos.",
        "Cada médico tiene una cuenta de acceso propia y no comparte credenciales, supuesto sin "
        "el cual la autoría de los registros clínicos dejaría de ser confiable.",
        "Las fechas y las horas se manejan en el huso horario de Colombia, que es donde opera "
        "el centro de salud.",
    ])


def _funcionales(d):
    c = conteo()
    d.titulo("3. Requisitos funcionales", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Los requisitos funcionales describen las capacidades que el sistema debe proporcionar. "
        f"Se especificaron {c['funcionales']} requisitos repartidos en los "
        f"{c['modulos']} módulos descritos en el apartado 2.2, con el fin de facilitar su "
        "organización, su desarrollo, su validación y su mantenimiento."
    )
    d.parrafo(
        "La agrupación se aparta deliberadamente de la de un sistema de gestión hospitalaria "
        "completo. MediApp no factura servicios, no administra camas ni inventario de insumos y "
        "no certifica la historia clínica ante ninguna autoridad, sino que administra la agenda "
        "de atención y protege el acto clínico que se deriva de ella. Por esa razón, donde un "
        "sistema hospitalario tendría facturación y gestión de suministros, aquí hay "
        "agendamiento de citas y control de acceso por rol."
    )
    d.parrafo(
        "Tres de los diez módulos merecen una advertencia de lectura. En historia clínica, en "
        "consultas y en prescripciones aparece un requisito que no describe una capacidad sino "
        "una prohibición, y es el que impide al administrador y al paciente escribir sobre esos "
        "registros. Se enuncia como requisito funcional y no como condición de calidad porque "
        "es una regla de negocio del centro de salud, comprobable operación por operación, y "
        "no una aspiración general de seguridad."
    )

    d.tabla(
        "Distribución de los requisitos funcionales por módulo",
        ["Código", "Módulo", "Cantidad de RF"],
        [[c_mod, n, str(len(rf))] for c_mod, n, _, _, rf in MODULOS]
        + [["", "Total", str(c["funcionales"])]],
        nota="Elaboración propia.",
        anchos=[2.2, 10.6, 3.5],
    )

    for indice, (codigo, nombre, _alcance, cierre, requisitos) in enumerate(MODULOS, start=1):
        d.titulo(f"3.{indice} {codigo}. {nombre}", nivel=2, nueva_pagina=True)
        d.parrafo(cierre)
        d.tabla(
            f"Requisitos funcionales del módulo de {inicial_minuscula(nombre)}",
            ["Código", "Requisito", "Descripción", "Actor", "Prioridad"],
            [[c_rf, n, desc, actor, prioridad(v, u)]
             for c_rf, n, desc, actor, v, u in requisitos],
            nota="Elaboración propia. La prioridad se deriva del valor de negocio y de la "
                 "urgencia asignados en el capítulo 5.",
            anchos=[1.6, 3.3, 6.8, 2.6, 2.0],
        )


def _no_funcionales(d):
    d.titulo("4. Requisitos no funcionales", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Los requisitos no funcionales establecen las condiciones de calidad que el sistema "
        "debe satisfacer. No describen capacidades, sino restricciones sobre la manera en que "
        "estas se prestan, esto es, con qué garantías de seguridad, con qué fiabilidad frente a "
        "usos simultáneos, con qué facilidad de uso y con qué posibilidad de mantenerse en el "
        "tiempo."
    )
    d.parrafo(
        "Cada requisito se acompaña de la forma en que se comprueba. Un requisito no funcional "
        "que no indica cómo verificarse es una aspiración y no un requisito, porque al momento "
        "de evaluar el sistema no habría manera de afirmar si se cumplió. Buena parte de estas "
        "verificaciones están automatizadas en la batería de pruebas del proyecto, de modo que "
        "no dependen de que alguien recuerde ejecutarlas a mano."
    )

    categorias = []
    for _, categoria, _, _ in RNF:
        if categoria not in categorias:
            categorias.append(categoria)

    d.tabla(
        "Distribución de los requisitos no funcionales por categoría",
        ["Categoría", "Cantidad"],
        [[cat, str(sum(1 for r in RNF if r[1] == cat))] for cat in categorias]
        + [["Total", str(len(RNF))]],
        nota="Elaboración propia.",
        anchos=[10.5, 6.0],
    )

    d.tabla(
        "Requisitos no funcionales del sistema",
        ["Código", "Categoría", "Requisito", "Verificación"],
        [[c, cat, r, v] for c, cat, r, v in RNF],
        nota="Elaboración propia. Las categorías responden a los atributos de calidad "
             "relevantes para un sistema que custodia información clínica de personas "
             "identificadas.",
        anchos=[1.7, 2.6, 6.9, 5.1],
    )

    d.parrafo(
        "Dos de estas categorías merecen una observación. La de seguridad no es aquí una "
        "exigencia genérica, porque el sistema custodia el historial médico de personas "
        "identificadas y una lectura indebida no degrada el servicio sino que vulnera al "
        "paciente, de ahí que siete de los veinticuatro requisitos pertenezcan a ella. La de "
        "fiabilidad recoge una condición que suele pasarse por alto en un sistema de agenda, y "
        "es que dos personas pueden pedir el mismo horario en el mismo instante, situación que "
        "un sistema descuidado resuelve otorgando la cita a las dos."
    )


def _priorizacion(d):
    d.titulo("5. Priorización de los requisitos funcionales", nivel=1, nueva_pagina=True)
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
            ["1", "Impacto muy bajo sobre la atención",
             "No es urgente, puede esperar"],
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
        "El puntaje individual de cada requisito resulta de ponderar el valor para la operación "
        "en un sesenta por ciento y la urgencia en un cuarenta por ciento. La ponderación no es "
        "neutra y responde a una decisión explícita, y es que lo importante debe pesar más que "
        "lo afanado, porque un requisito urgente pero de bajo valor desplaza recursos de otro "
        "que sostiene la atención. El puntaje global del módulo es el promedio de los puntajes "
        "de sus requisitos."
    )

    d.titulo("5.1 Puntaje de cada requisito", nivel=2, nueva_pagina=True)
    filas = []
    for _codigo, nombre, _alcance, _cierre, requisitos in MODULOS:
        global_modulo = round(sum(puntaje(v, u) for *_, v, u in requisitos) / len(requisitos), 1)
        for posicion, (c_rf, n, _, _, v, u) in enumerate(requisitos):
            filas.append([
                nombre if posicion == 0 else "",
                f"{c_rf} {n}",
                str(v), str(u),
                str(puntaje(v, u)),
                str(global_modulo) if posicion == 0 else "",
            ])

    d.tabla(
        "Priorización de los requisitos funcionales",
        ["Módulo", "Requisito", "Valor", "Urgencia", "Puntaje individual",
         "Puntaje global del módulo"],
        filas,
        nota="Elaboración propia. El puntaje individual pondera el valor para la operación al "
             "60 % y la urgencia al 40 %; el global es el promedio del módulo.",
        anchos=[3.2, 5.6, 1.3, 1.8, 2.2, 2.2],
    )

    orden = sorted(
        ((n, round(sum(puntaje(v, u) for *_, v, u in rf) / len(rf), 1))
         for _, n, _, _, rf in MODULOS),
        key=lambda x: x[1], reverse=True,
    )
    d.parrafo(
        "El orden resultante confirma la naturaleza del proyecto. Encabezan la lista los "
        "módulos de los que depende que una cita quede bien agendada y que el acto clínico "
        "quede en manos de quien corresponde, y quedan al final los que mantienen catálogos que "
        "se ajustan de vez en cuando. "
        f"El módulo mejor puntuado es el de {inicial_minuscula(orden[0][0])}, con "
        f"{orden[0][1]} puntos, y el de menor puntaje es el de "
        f"{inicial_minuscula(orden[-1][0])}, con {orden[-1][1]}."
    )

    _moscow(d)


def _moscow(d):
    """El apartado que responde a la observación O04.

    Lo que el evaluador marcó en el documento anterior no fue que faltara una tabla, sino que
    el modelo no se observaba. Por eso aquí no se presenta el reparto sin más, sino la regla
    que lo produce, los cortes elegidos y lo que se decidió no construir.
    """
    c = conteo()
    grupos = por_moscow()

    d.titulo("5.2 Modelo de priorización MoSCoW", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Sobre los puntajes del apartado anterior se aplicó el modelo MoSCoW, técnica de "
        "priorización que reparte los requisitos en cuatro categorías según el compromiso que "
        "el equipo adquiere con cada uno. Las categorías son Must have, para lo que el sistema "
        "no puede dejar de hacer, Should have, para lo que debería hacer y se implementa "
        "siempre que no comprometa a lo anterior, Could have, para lo deseable que puede "
        "aplazarse sin consecuencias, y Won't have, para lo que se decide de forma expresa no "
        "construir en esta versión."
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
             "entrega.",
             str(c["must"])],
            ["Should have", "Entre 4,0 y 4,5",
             "El sistema funciona sin él, pero su ausencia obliga a resolver a mano lo que "
             "debería resolver el programa.",
             str(c["should"])],
            ["Could have", "Menor que 4,0",
             "Aporta comodidad o completitud y puede aplazarse a una versión posterior sin "
             "afectar la operación.",
             str(c["could"])],
            ["Won't have", "No se deriva del puntaje",
             "Se decidió de forma expresa no construirlo, según el apartado 5.4.",
             str(c["fuera_de_alcance"])],
        ],
        nota="Elaboración propia. Los cortes se fijaron sobre la escala ponderada del apartado "
             "5.1, cuyo valor máximo es 5,0.",
        anchos=[2.6, 3.0, 8.4, 2.5],
    )
    d.parrafo(
        "La cuarta categoría exige una precisión que suele omitirse. Won't have no es el fondo "
        "de la escala, porque un requisito con puntaje bajo sigue estando implementado y no "
        "puede declararse como algo que no se hará. Won't have recoge decisiones de alcance, "
        "esto es, capacidades que se evaluaron y se descartaron para esta versión, y por eso se "
        "enumera aparte en el apartado 5.4 en lugar de salir de un corte del puntaje."
    )

    d.titulo("5.3 Reparto resultante", nivel=2)
    d.parrafo(
        f"De los {c['funcionales']} requisitos funcionales especificados, {c['must']} quedaron "
        f"clasificados como Must have, {c['should']} como Should have y {c['could']} como "
        f"Could have. Que casi la mitad del catálogo sea de obligatorio cumplimiento no indica "
        "una valoración generosa, sino la naturaleza del sistema, porque en un sistema que "
        "custodia historias clínicas las reglas de acceso no admiten grados y una cita mal "
        "validada es una cita perdida."
    )

    for categoria in ("Must have", "Should have", "Could have"):
        d.tabla(
            f"Requisitos clasificados como {categoria}",
            ["Código", "Requisito", "Módulo", "Puntaje"],
            [[c_rf, n, mod, str(puntaje(v, u))]
             for c_rf, n, mod, _desc, _actor, v, u in grupos[categoria]],
            nota="Elaboración propia. La categoría se deriva del puntaje según los cortes del "
                 "apartado 5.2.",
            anchos=[1.7, 6.3, 5.5, 3.0],
        )

    d.titulo("5.4 Requisitos excluidos del alcance", nivel=2, nueva_pagina=True)
    d.parrafo(
        "La categoría Won't have recoge las capacidades que se evaluaron durante el análisis y "
        "se descartaron para esta versión del sistema. Dejarlas escritas cumple dos funciones, "
        "porque delimita hasta dónde llega el compromiso del proyecto y deja constancia de que "
        "la ausencia de cada una obedece a una decisión y no a un olvido."
    )
    d.tabla(
        "Capacidades excluidas del alcance y razón de la exclusión",
        ["Capacidad", "Razón de la exclusión"],
        [[q, por_que] for q, por_que in FUERA_DE_ALCANCE],
        nota="Elaboración propia.",
        anchos=[5.5, 11.0],
    )
    d.parrafo(
        "La exclusión del cifrado de la información merece una nota, porque es la que sostiene "
        "la redacción del tercer objetivo específico del proyecto. Ese objetivo garantiza la "
        "confidencialidad de la información médica mediante un control de acceso basado en "
        "roles, y la acotación que introduce la palabra mediante no es un adorno de estilo, ya "
        "que un enunciado sin ella prometería también cifrado en tránsito y en reposo, que "
        "depende de la infraestructura de despliegue y no del programa. Un objetivo que promete "
        "más de lo que el sistema entrega es un objetivo que no puede declararse cumplido."
    )


def _trazabilidad(d):
    d.titulo("6. Trazabilidad con los objetivos del proyecto", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Cada objetivo específico del proyecto se sostiene en un conjunto determinado de "
        "requisitos funcionales y se evidencia en módulos concretos del sistema. La siguiente "
        "matriz establece esa correspondencia, de modo que la verificación del cumplimiento de "
        "un objetivo pueda hacerse sobre requisitos comprobables y no sobre una apreciación "
        "general."
    )
    d.tabla(
        "Matriz de trazabilidad entre objetivos, requisitos y módulos",
        ["Objetivo", "Enunciado", "Requisitos", "Pantallas del sistema"],
        [[o, e, r, m] for o, e, r, m in TRAZABILIDAD],
        nota="Elaboración propia. Los enunciados completos de los objetivos se encuentran en el "
             "capítulo 1 del documento de grado.",
        anchos=[1.8, 5.2, 4.2, 5.3],
    )
    d.parrafo(
        "La matriz cumple además una función de control sobre la propia especificación, porque "
        "un requisito que no puede asociarse a ningún objetivo indica alcance no previsto, y un "
        "objetivo sin requisitos asociados indica una promesa que el sistema no está en "
        "condiciones de cumplir. En la especificación resultante no se presenta ninguno de los "
        "dos casos."
    )
    d.parrafo(
        "El control se extiende un paso más allá en el anexo de documentación de casos de uso, "
        "donde cada caso declara además las tablas del modelo de datos que toca. Con las dos "
        "matrices juntas puede recorrerse el camino completo que va del objetivo al requisito, "
        "de este al caso de uso que lo realiza y de allí a los datos sobre los que opera, que "
        "es la trazabilidad que solicitaron los evaluadores del proyecto."
    )


if __name__ == "__main__":
    documento = construir()
    c = conteo()
    print(f"Generado: {ARCHIVO}")
    print(f"RF: {c['funcionales']} en {c['modulos']} modulos  RNF: {c['no_funcionales']}")
    print(f"MoSCoW: Must {c['must']}  Should {c['should']}  Could {c['could']}  "
          f"Wont {c['fuera_de_alcance']}")
    print(f"Tablas: {documento.n_tabla}  Figuras: {documento.n_figura}")
