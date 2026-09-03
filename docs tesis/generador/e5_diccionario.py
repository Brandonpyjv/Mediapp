# -*- coding: utf-8 -*-
"""
E5 — Diccionario de datos de MediApp.

Se arma leyendo el esquema real con `esquema.py`, que prefiere el propio motor MySQL y cae al
respaldo cuando no está disponible. Ninguna tabla ni ninguna columna de este documento está
transcrita a mano, y el documento declara de dónde salió.

Responde a la observación **O14**, que pedía agregar el modelo relacional generado desde MySQL.
Lo único escrito a mano son las descripciones, porque el esquema no lleva comentarios de columna,
y el generador se niega a producir el documento si alguna columna se quedó sin la suya.

    python e5_diccionario.py
"""
from pathlib import Path

import casos_de_uso as catalogo
import esquema
from apa import DocumentoAPA

SALIDA = Path(__file__).resolve().parent.parent / "entregables"
ARCHIVO = SALIDA / "MediApp - Diccionario de Datos.docx"


def construir():
    datos = esquema.leer()
    faltan = esquema.sin_descripcion(datos)
    if faltan:
        raise SystemExit(f"Hay {len(faltan)} columnas sin descripción: {', '.join(faltan)}")

    d = DocumentoAPA()
    d.portada(
        titulo="MEDIAPP",
        subtitulo="Diccionario de datos",
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

    _introduccion(d, datos)
    _tablas(d, datos)
    _relaciones(d, datos)

    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d


def _introduccion(d, datos):
    c = esquema.conteo(datos)
    d.titulo("1. Introducción", nivel=1)
    d.parrafo(
        f"Este documento describe la estructura de la base de datos de MediApp, que está "
        f"formada por {c['tablas']} tablas, {c['columnas']} columnas y {c['foraneas']} claves "
        "foráneas. Para cada tabla se indica qué guarda y para qué sirve, y para cada columna "
        "su tipo de dato, si admite ausencia de valor, el papel que cumple como clave y el "
        "significado del dato que almacena."
    )
    d.parrafo(
        f"El contenido no está transcrito a mano. Se genera leyendo {esquema.fuente()}, de modo "
        "que lo que aquí se describe es literalmente lo que la base tiene en el momento de "
        "producir el documento. La decisión responde a una forma de envejecer que tienen los "
        "diccionarios de datos escritos a mano, porque empiezan a separarse del sistema el "
        "mismo día en que se escriben y nadie lo advierte hasta que alguien busca una columna "
        "que el documento describe y que ya no existe."
    )
    d.parrafo(
        "Lo único escrito a mano son las descripciones de las columnas, porque el esquema no "
        "lleva comentarios incorporados. El generador comprueba que ninguna columna se quede "
        "sin descripción y se niega a producir el documento si encuentra alguna, de manera que "
        "una columna agregada más adelante no pueda llegar al documento sin explicación."
    )

    d.titulo("1.1 Convenciones", nivel=2)
    d.vinetas([
        ("Tipo de dato", "tipo del motor, presentado en español. Entre paréntesis va la "
                         "longitud, o los valores admitidos cuando la columna es enumerada."),
        ("Admite nulo", "indica si la columna puede quedarse sin valor. Un «No» significa que "
                        "el dato es obligatorio."),
        ("Clave", "papel de la columna, que puede ser primaria, única o foránea. Una columna "
                  "única no identifica la fila pero no puede repetirse entre filas."),
    ])
    d.parrafo(
        "Las claves primarias son autonuméricas en las once tablas, así que el sistema no "
        "reutiliza identificadores y una fila conserva el suyo durante toda su vida."
    )

    d.titulo("1.2 Las tablas del esquema", nivel=2)
    por_tabla = catalogo.por_tabla()
    d.tabla(
        "Tablas de la base de datos y propósito de cada una",
        ["Tabla", "Columnas", "Casos de uso", "Propósito"],
        [[t, str(len(esquema.columnas(t, datos))), str(len(por_tabla.get(t, []))),
          esquema.PROPOSITO[t]] for t in esquema.TABLAS],
        nota="Elaboración propia. La columna de casos de uso indica cuántos operan sobre la "
             "tabla, según la matriz de trazabilidad del anexo de documentación de casos de "
             "uso.",
        anchos=[2.4, 1.9, 2.0, 10.2],
    )
    d.parrafo(
        "Ninguna tabla queda sin casos de uso que la justifiquen, lo que indica que el esquema "
        "no arrastra estructuras heredadas de un diseño anterior. La comprobación se hace en "
        "sentido inverso, esto es, partiendo de los casos y llegando a las tablas, y está "
        "automatizada en el catálogo de casos de uso."
    )


def _tablas(d, datos):
    d.titulo("2. Descripción de las tablas", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Cada tabla se presenta con su propósito y el detalle de sus columnas. Las tablas "
        "aparecen en orden alfabético, que es el orden en que se busca en un diccionario."
    )

    for indice, tabla in enumerate(esquema.TABLAS, start=1):
        # La primera sigue al párrafo de apertura del capítulo. Saltando también con ella, el
        # capítulo se abre con una página que solo lleva dos renglones.
        d.titulo(f"2.{indice} Tabla {tabla}", nivel=2, nueva_pagina=indice > 1)
        d.parrafo(esquema.PROPOSITO[tabla])
        d.tabla(
            f"Estructura de la tabla {tabla}",
            ["Columna", "Tipo de dato", "Admite nulo", "Clave", "Descripción"],
            [[nombre, tipo, nulo, clave, desc]
             for nombre, tipo, nulo, clave, desc in esquema.columnas(tabla, datos)],
            nota=f"Elaboración propia, generada leyendo {esquema.fuente()}.",
            anchos=[3.0, 3.4, 1.7, 2.0, 6.4],
        )

        salientes = [(c, dt, dc) for o, c, dt, dc in esquema.relaciones(datos) if o == tabla]
        entrantes = [(o, c) for o, c, dt, _ in esquema.relaciones(datos) if dt == tabla]
        if salientes or entrantes:
            frases = []
            if salientes:
                frases.append("Referencia a " + ", ".join(
                    f"{destino} mediante {columna}" for columna, destino, _ in salientes) + ".")
            if entrantes:
                frases.append("Es referenciada por " + ", ".join(
                    f"{origen} mediante {columna}" for origen, columna in entrantes) + ".")
            d.parrafo(" ".join(frases))


def _relaciones(d, datos):
    foraneas = esquema.relaciones(datos)
    d.titulo("3. Relaciones entre las tablas", nivel=1, nueva_pagina=True)
    d.parrafo(
        f"Las {len(foraneas)} claves foráneas del esquema son las que sostienen la integridad "
        "de la información. Impiden que una cita apunte a un paciente que no existe, que una "
        "receta prescriba un medicamento que no está en el catálogo o que un registro clínico "
        "quede sin médico que lo firme."
    )
    d.tabla(
        "Claves foráneas del esquema",
        ["Tabla", "Columna", "Referencia a", "Columna referenciada"],
        [[o, c, dt, dc] for o, c, dt, dc in foraneas],
        nota=f"Elaboración propia, generada leyendo {esquema.fuente()}.",
        anchos=[3.4, 4.1, 3.4, 5.6],
    )

    d.titulo("3.1 Cómo se lee el modelo", nivel=2)
    d.parrafo(
        "El esquema gira alrededor del paciente, que es la entidad que más referencias recibe, "
        "porque de él cuelgan las citas, las historias clínicas, las consultas y los exámenes. "
        "El médico ocupa el segundo lugar por la misma razón, ya que firma todo lo que atiende. "
        "Las dos tablas de acceso, que son usuario y rol, quedan al margen del dominio clínico "
        "y se conectan con él únicamente a través del vínculo opcional que llevan el médico y "
        "el paciente hacia su cuenta."
    )
    d.parrafo(
        "Ese vínculo es opcional a propósito, porque un paciente puede estar registrado por el "
        "administrador sin tener todavía cuenta con la que consultar lo suyo. En el médico, en "
        "cambio, la ausencia del vínculo tiene una consecuencia inmediata, y es que la ficha "
        "existe pero el profesional no puede firmar ningún registro clínico, dado que la "
        "autoría se toma de la sesión y no habría sesión que la aportara."
    )
    d.parrafo(
        "La única cadena de tres niveles del esquema es la de la prescripción, porque la receta "
        "cuelga de la consulta y la consulta del paciente y del médico. Es lo que permite que "
        "una receta se lea completa sin repetir en ella los datos del paciente, que ya están en "
        "la consulta de la que salió."
    )

    d.titulo("3.2 Una relación que el esquema no tiene", nivel=2)
    d.parrafo(
        "Conviene señalar una ausencia, porque es la clase de cosa que un lector atento busca y "
        "no encuentra. La tabla de consultas no referencia a la tabla de citas, de modo que un "
        "diagnóstico registra a qué paciente atendió qué médico y en qué fecha, pero no apunta "
        "a la cita concreta de la que salió. En la práctica la correspondencia se deduce por el "
        "paciente, el médico y la fecha, y no por una clave."
    )
    d.parrafo(
        "Se deja escrito por dos motivos. El primero es que un documento que solo describe lo "
        "que el sistema tiene deja al lector suponiendo el resto, y esta es una relación que "
        "cualquiera esperaría encontrar. El segundo es que señala con precisión la mejora que "
        "el esquema admitiría, que es agregar esa referencia para poder recorrer la atención "
        "completa desde la cita hasta la receta sin depender de una coincidencia de fechas."
    )


if __name__ == "__main__":
    documento = construir()
    c = esquema.conteo()
    print(f"Generado: {ARCHIVO}")
    print(f"Fuente: {esquema.fuente()}")
    print(f"Tablas: {c['tablas']}  Columnas: {c['columnas']}  Foraneas: {c['foraneas']}")
    print(f"Tablas del documento: {documento.n_tabla}")
