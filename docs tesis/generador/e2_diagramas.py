# -*- coding: utf-8 -*-
"""
E2 — Diagramas de casos de uso de MediApp.

Los diagramas se dibujan a partir de `casos_de_uso.py`, que es la misma lista de la que salen
las fichas de E3 y el punto 5.2 del documento de grado. Las relaciones de inclusión y de
extensión se declaran por código de caso y aquí se traducen a nombres, que es lo que el
dibujante rotula.

Responde a dos observaciones del evaluador. La **O05** pedía ordenar los casos de uso y agregar
los actores médico y paciente, y la **O11** decía directamente que faltaban los casos de uso de
los pacientes y los médicos. Por eso los tres actores aparecen en el diagrama general y cada
diagrama de módulo declara a los suyos, incluidos los que solo leen.

    python e2_diagramas.py
"""
from pathlib import Path

import casos_de_uso as catalogo
from apa import DocumentoAPA, inicial_minuscula
from uml import Diagrama

BASE = Path(__file__).resolve().parent.parent
SALIDA = BASE / "entregables"
IMAGENES = SALIDA / "diagramas"
ARCHIVO = SALIDA / "MediApp - Diagramas de Casos de Uso.docx"

SISTEMA = "MEDIAPP"

ACTORES = [
    ("Administrador", "Persona que gestiona la operación del centro de salud. Administra los "
     "usuarios, los médicos, los pacientes y los catálogos, controla la agenda completa y "
     "carga los resultados de los exámenes de laboratorio. Su única restricción es que no "
     "crea ni modifica historias clínicas, consultas ni recetas, aunque sí puede "
     "consultarlas."),
    ("Médico", "Profesional que presta la atención. Es el único actor que puede escribir sobre "
     "el acto clínico, esto es, la historia clínica, el diagnóstico con su tratamiento y la "
     "prescripción, y además solicita los exámenes de laboratorio. Consulta su agenda pero no "
     "la modifica, porque quien agenda es el administrador o el propio paciente."),
    ("Paciente", "Persona que recibe la atención. Consulta lo que le pertenece, que son sus "
     "citas, su historia clínica, sus diagnósticos, sus recetas y sus exámenes. Tiene dos "
     "capacidades de escritura, ambas sobre su propia cita, que son reservarla desde el "
     "calendario de disponibilidad y cancelarla."),
    ("Sistema", "Actor no humano al que se atribuyen las reglas que se ejecutan sin que nadie "
     "las solicite, como la validación de los conflictos de la agenda, la reserva del turno y "
     "la comprobación del rol en cada operación. No se dibuja como figura porque no inicia "
     "ningún caso, y sus casos aparecen sin línea de asociación."),
]


def _dibujar_general():
    diagrama = Diagrama(
        sistema=SISTEMA,
        actores_izq=["Administrador"],
        actores_der=["Médico", "Paciente"],
        casos=catalogo.GENERAL,
    )
    return diagrama.dibujar(IMAGENES / "DCU-00 general.png")


def _dibujar_modulo(modulo):
    codigo, nombre, izq, der, casos, inclusiones, extensiones, _ = modulo
    nombres = {c[0]: c[1] for c in casos}
    diagrama = Diagrama(
        sistema=SISTEMA,
        modulo=nombre,
        actores_izq=izq,
        actores_der=der,
        casos=catalogo.por_nombre(casos),
        inclusiones=[(nombres[a], nombres[b]) for a, b in inclusiones],
        extensiones=[(nombres[a], nombres[b]) for a, b in extensiones],
    )
    return diagrama.dibujar(IMAGENES / f"{codigo} {nombre}.png")


def construir():
    IMAGENES.mkdir(parents=True, exist_ok=True)
    general = _dibujar_general()
    dibujos = {m[0]: _dibujar_modulo(m) for m in catalogo.MODULOS}

    d = DocumentoAPA()
    d.portada(
        titulo="MEDIAPP",
        subtitulo="Diagramas de casos de uso",
        integrantes=["ÁNGEL JESÚS HERNÁNDEZ ARÉVALO",
                     "RICHARD ALBERTO QUIÑONES QUIÑONES"],
        grado="Ficha 3115426\nTecnólogo en Análisis y Desarrollo de Software",
        institucion=["SERVICIO NACIONAL DE APRENDIZAJE (SENA)",
                     "Centro de la Industria, la Empresa y los Servicios (CIES)",
                     "Tecnólogo en Análisis y Desarrollo de Software"],
        ciudad="CÚCUTA, NORTE DE SANTANDER",
        anio=2026,
    )
    d.tabla_contenido()

    _introduccion(d)
    _actores(d)
    _general(d, general)
    _modulos(d, dibujos)
    _matriz(d)

    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d


def _introduccion(d):
    total = len(catalogo.todos())
    c = catalogo.conteo()

    d.titulo("1. Introducción", nivel=1)
    d.parrafo(
        "Este documento reúne los diagramas de casos de uso de MediApp. Un caso de uso "
        "describe un objetivo que un actor persigue en el sistema y no una operación sobre la "
        "base de datos, de manera que el catálogo se lee como aquello que el sistema permite "
        f"hacer y no como la lista de sus pantallas. Por esa razón hay {total} casos de uso "
        "frente a los ochenta y siete requisitos funcionales especificados, ya que un mismo "
        "objetivo suele apoyarse en varios requisitos."
    )
    d.parrafo(
        f"Los casos se organizan en {c['modulos']} diagramas de módulo, más un diagrama "
        "general que resume el sistema completo. La organización coincide con la del documento "
        "de requisitos, y esa coincidencia es intencional, porque cada caso declara los "
        "requisitos que realiza y permite comprobar que ningún requisito quedó sin caso y que "
        "ningún caso describe algo que no fue especificado."
    )
    d.parrafo(
        "Los tres actores humanos del sistema aparecen en el diagrama general y en los "
        "diagramas de los módulos en que intervienen, incluidos aquellos en los que solo "
        "consultan. Representar también al lector es necesario en un sistema cuyo propósito es "
        "repartir el acceso, porque un diagrama en el que únicamente aparece quien escribe "
        "deja sin mostrar la mitad de las reglas."
    )

    d.titulo("1.1 Notación empleada", nivel=2)
    d.parrafo(
        "Los diagramas siguen la notación del Lenguaje Unificado de Modelado. Los elementos "
        "utilizados son los siguientes."
    )
    d.vinetas([
        ("Actor", "figura de palotes situada fuera de la frontera del sistema. Representa un "
                  "rol y no a una persona concreta, de modo que una misma persona podría "
                  "actuar como dos actores distintos si tuviera dos cuentas."),
        ("Caso de uso", "elipse situada dentro de la frontera, rotulada con el objetivo que "
                        "persigue el actor."),
        ("Frontera del sistema", "rectángulo que separa lo que el sistema hace de quienes se "
                                 "lo piden."),
        ("Asociación", "línea continua entre un actor y un caso de uso, que indica que ese "
                       "actor participa en él."),
        ("Inclusión", "flecha discontinua rotulada «include», dirigida del caso base al caso "
                      "incluido. Significa que el caso base no puede completarse sin el "
                      "incluido, y se usa para no repetir en varios casos un comportamiento "
                      "que es obligatorio en todos ellos."),
        ("Extensión", "flecha discontinua rotulada «extend», dirigida del caso que extiende "
                      "hacia el caso base. Significa que el primero ocurre a veces sobre el "
                      "segundo, sin que su ausencia impida que el segundo termine."),
    ])
    d.parrafo(
        "Los casos que no tienen ningún actor asociado corresponden al actor Sistema, y son "
        "reglas que se ejecutan como parte de otro caso sin que nadie las solicite. Se "
        "representan como elipses sin línea de asociación, y en todos los diagramas aparecen "
        "como destino de una relación de inclusión, que es exactamente lo que son."
    )
    d.parrafo(
        "La distinción entre inclusión y extensión merece una aclaración, porque es la que más "
        "se confunde. La validación de las reglas de la agenda se modela como inclusión y no "
        "como extensión, ya que una cita que no pasa por ella no llega a existir. La "
        "cancelación de una cita, en cambio, se modela como extensión de la consulta de las "
        "citas propias, porque el paciente entra a mirar lo que tiene y puede salir sin "
        "cancelar nada."
    )


def _actores(d):
    d.titulo("2. Actores del sistema", nivel=1, nueva_pagina=True)
    d.parrafo(
        "El sistema reconoce tres actores humanos, que corresponden a los tres roles de "
        "acceso, y un cuarto actor no humano al que se atribuyen las reglas automáticas. La "
        "separación entre los tres primeros no es una organización del menú, porque se "
        "comprueba en el servidor en cada operación y es lo que sostiene el tercer objetivo "
        "específico del proyecto."
    )
    d.tabla(
        "Actores del sistema y alcance de su participación",
        ["Actor", "Descripción"],
        [[a, desc] for a, desc in ACTORES],
        nota="Elaboración propia, a partir de la matriz de permisos acordada con el autor del "
             "proyecto.",
        anchos=[3.0, 13.5],
    )
    d.parrafo(
        "Conviene señalar lo que el reparto tiene de particular, porque no es el de un sistema "
        "de gestión corriente. El administrador puede hacer prácticamente todo salvo escribir "
        "en la historia clínica, y el médico, que es quien menos pantallas tiene, es el único "
        "que puede hacerlo. Esa inversión responde a que el acto clínico pertenece a quien "
        "presta la atención y no a quien administra el centro de salud."
    )


def _general(d, imagen):
    total = len(catalogo.todos())
    d.titulo("3. Diagrama general de casos de uso", nivel=1, nueva_pagina=True)
    d.parrafo(
        "El diagrama general presenta el sistema completo agrupando los casos por el propósito "
        "que atienden, y cada uno de esos grupos se detalla después en su propio diagrama. Se "
        f"presenta de esta forma porque un diagrama con los {total} casos y todas sus "
        "asociaciones resultaría ilegible, y un diagrama que no se lee no cumple la función de "
        "comunicar el alcance del sistema."
    )
    d.figura(
        "Diagrama general de casos de uso de MediApp",
        imagen,
        nota="Elaboración propia. Cada elipse agrupa los casos de uso de uno o varios módulos, "
             "detallados en el capítulo 4.",
    )
    d.parrafo(
        "Tres observaciones sobre lo que el diagrama muestra. La primera es que el paciente no "
        "aparece únicamente como destinatario de la atención, sino iniciando la reserva y la "
        "cancelación de su propia cita, que es una decisión de diseño del proyecto y se "
        "justifica en el capítulo de análisis del documento de grado. La segunda es que el "
        "médico aparece consultando su agenda pero no gestionándola, lo que corresponde a su "
        "situación real, ya que nunca agenda ni modifica sus propias citas."
    )
    d.parrafo(
        "La tercera es la que más dice del sistema. El registro de la historia clínica, del "
        "diagnóstico y de la prescripción se conecta con un solo actor, y el administrador, "
        "que en todos los demás grupos aparece como el actor principal, no tiene línea hacia "
        "ninguno de ellos. Esa ausencia no es un olvido del diagrama sino la restricción "
        "central del proyecto dibujada."
    )


def _modulos(d, dibujos):
    c = catalogo.conteo()
    d.titulo("4. Diagramas por módulo", nivel=1, nueva_pagina=True)
    d.parrafo(
        f"Los {c['modulos']} diagramas siguientes corresponden a los diez módulos funcionales "
        "especificados en el documento de requisitos. Cada uno se acompaña de la tabla de sus "
        "casos, en la que se indican los actores que participan, los requisitos que el caso "
        "realiza y las tablas del modelo de datos sobre las que opera."
    )
    d.parrafo(
        "La columna de tablas responde a una exigencia expresa de los evaluadores del "
        "proyecto, que pidieron que los casos de uso fueran trazables al modelo de datos. Se "
        "presenta con los nombres de las tablas y sin sentencias de consulta, porque los "
        "propios evaluadores observaron que en los casos de uso no debe ir código."
    )

    for indice, modulo in enumerate(catalogo.MODULOS, start=1):
        codigo, nombre, _izq, _der, casos, _inc, _ext, explicacion = modulo
        numero_rf = codigo.replace("DCU-", "").lstrip("0") or "10"
        d.titulo(f"4.{indice} {codigo}. {nombre}", nivel=2, nueva_pagina=True)
        d.parrafo(explicacion)
        d.figura(
            f"Diagrama de casos de uso del módulo de {inicial_minuscula(nombre)}",
            dibujos[codigo],
            nota=f"Elaboración propia. Corresponde al módulo RF {numero_rf} del documento de "
                 "requisitos.",
        )
        d.tabla(
            f"Casos de uso del módulo {codigo}",
            ["Código", "Caso de uso", "Actores", "Requisitos", "Tablas que toca"],
            [[c_cu, n, ", ".join(a) if a else "Sistema", rf, ", ".join(tablas)]
             for c_cu, n, a, _desc, rf, tablas in casos],
            nota="Elaboración propia. Los casos atribuidos al Sistema son casos incluidos, que "
                 "se ejecutan como parte de otro y que nadie inicia por separado.",
            anchos=[1.6, 4.0, 3.2, 3.2, 4.5],
        )


def _matriz(d):
    d.titulo("5. Matriz de casos de uso por actor", nivel=1, nueva_pagina=True)
    d.parrafo(
        "La matriz resume en qué casos participa cada actor. Sirve para comprobar dos cosas, "
        "que ningún actor quedó sin casos, lo que indicaría un rol declarado pero no "
        "utilizado, y que ningún caso quedó sin actor salvo los incluidos, que por definición "
        "los ejecuta el sistema."
    )

    humanos = ["Administrador", "Médico", "Paciente"]
    filas = []
    for codigo, nombre, _modulo, suyos, _desc, _rf, _tablas in catalogo.todos():
        marcas = ["X" if a in suyos else "" for a in humanos]
        filas.append([codigo, nombre] + marcas + ["X" if not suyos else ""])

    d.tabla(
        "Matriz de participación de los actores en los casos de uso",
        ["Código", "Caso de uso", "Administrador", "Médico", "Paciente", "Sistema"],
        filas,
        nota="Elaboración propia. La columna Sistema marca los casos sin actor humano, que se "
             "ejecutan como parte de otro caso.",
        anchos=[1.6, 6.0, 3.0, 2.0, 2.0, 1.9],
    )

    todos = catalogo.todos()
    sin_actor = [c for c, _, _, actores, _, _, _ in todos if not actores]
    conteo_actor = {a: sum(1 for caso in todos if a in caso[3]) for a in humanos}
    d.parrafo(
        f"De los {len(todos)} casos de uso, {len(sin_actor)} se atribuyen al actor Sistema y "
        "el resto tiene al menos un actor humano. El administrador participa en "
        f"{conteo_actor['Administrador']} casos, el médico en {conteo_actor['Médico']} y el "
        f"paciente en {conteo_actor['Paciente']}, de modo que los tres roles declarados "
        "intervienen en el sistema y ninguno quedó como un perfil escrito en la documentación "
        "pero sin uso."
    )
    d.parrafo(
        "El reparto de la matriz confirma lo que el diagrama general mostraba. El "
        "administrador encabeza el conteo porque gestiona la operación completa, pero no "
        "aparece marcado en ninguno de los casos de escritura sobre la historia clínica, la "
        "consulta ni la receta, y el médico, que participa en menos casos, es el único marcado "
        "en todos ellos."
    )


if __name__ == "__main__":
    documento = construir()
    print(f"Generado: {ARCHIVO}")
    print(f"Casos de uso: {len(catalogo.todos())}  Diagramas: {len(catalogo.MODULOS) + 1}")
    print(f"Tablas: {documento.n_tabla}  Figuras: {documento.n_figura}")
