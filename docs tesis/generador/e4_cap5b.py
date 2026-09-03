# -*- coding: utf-8 -*-
"""
E4 — Capítulo 5, parte B. Diseño de la base de datos, modelo entidad-relación, modelo físico y
diccionario de datos.

Continúa la numeración donde la dejó `e4_cap5a.py`, del 5.8 al 5.11.

**Nada de esto está transcrito a mano.** Las tablas, las columnas, los tipos, los nulos y las
claves foráneas se leen con `esquema.py`, que consulta el propio motor MySQL y cae al respaldo
cuando no está disponible. Lo único escrito a mano son las descripciones de las columnas, que
viven en `esquema.DESCRIPCIONES`, y el generador se niega a producir el documento si alguna
columna se quedó sin la suya. Las zonas del 5.8 se leen de `figuras.ZONAS`, que es de donde las
toma también el dibujo del modelo físico.

**O14** se resuelve en el 5.10, que pedía agregar el modelo relacional generado desde MySQL. La
figura se dibuja leyendo el catálogo interno del motor y va en **página apaisada**, porque
reducida al ancho de una página vertical los nombres de las columnas dejan de leerse y un
diagrama que no se lee no documenta nada.

El diccionario completo de las once tablas es el anexo E5. Aquí van tres tablas, escogidas por
lo que cada una demuestra.
"""
import esquema
import figuras
from pathlib import Path

DIAGRAMAS = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"

# Las tres que llevan diccionario detallado en el documento de grado.
# `cita` porque es donde vive la razón de ser del sistema y donde se aplican sus dos reglas
# propias; `historia` porque es el registro que define el proyecto y el que fallaba en la
# versión anterior; y `usuario` porque es donde se ve que la contraseña no se guarda.
DETALLADAS = ["cita", "historia", "usuario"]

INTRO_TABLA = {
    "cita":
        "Es la tabla sobre la que operan las dos reglas de negocio propias del sistema, que "
        "son la separación mínima entre dos atenciones del mismo médico y el límite de una "
        "cita por paciente y por día. Ninguna de las dos está declarada como restricción del "
        "motor, y la razón es que ninguna puede expresarse como tal, porque no prohíben un "
        "valor repetido sino una distancia entre valores, de modo que se comprueban en el "
        "servidor dentro de la misma transacción que escribe.",
    "historia":
        "Es el registro que da nombre al proyecto y el que concentra su restricción de "
        "acceso. Su columna de médico no guarda a quién se consulta sino quién escribió, y "
        "por eso su valor se toma de la sesión en curso y nunca del formulario enviado. La "
        "fila no lleva ninguna marca de rol, porque el permiso no se guarda en el dato sino "
        "que se comprueba en cada petición.",
    "usuario":
        "Guarda las credenciales de acceso. La columna de contraseña no almacena ninguna "
        "contraseña, sino el resultado de aplicarle la función de derivación de clave "
        "descrita en el marco teórico, y su longitud responde a la del valor que esa función "
        "produce. La columna de estado es la que permite retirar el acceso de una cuenta sin "
        "borrarla, de modo que lo que esa cuenta firmó conserve su autor.",
}

# (tabla, por qué su estado no se borra) para las cuatro que llevan baja lógica.
BAJA_LOGICA = {
    "usuario": "una cuenta borrada dejaría sin autor conocido a las historias y a las recetas "
               "que firmó",
    "medico": "un profesional borrado dejaría sin firma su historia clínica y sin médico sus "
              "citas pasadas",
    "paciente": "un paciente borrado se llevaría consigo su historial completo",
    "medicamento": "un medicamento descontinuado sigue apareciendo en las recetas que ya se "
                   "emitieron",
}


def escribir(d):
    datos = esquema.leer()
    faltan = esquema.sin_descripcion(datos)
    if faltan:
        raise SystemExit(f"Hay {len(faltan)} columnas sin descripción: {', '.join(faltan)}")
    _diseno(d, datos)
    _entidad_relacion(d, datos)
    _fisico(d, datos)
    _diccionario(d, datos)


# --- 5.8 -----------------------------------------------------------------------

def _diseno(d, datos):
    c = esquema.conteo(datos)

    d.titulo("5.8 Diseño de la base de datos", nivel=2, nueva_pagina=True)
    d.parrafo(
        f"La base de datos se diseñó sobre el modelo relacional, con la integridad garantizada "
        f"por claves primarias, claves foráneas y restricciones de unicidad. Comprende "
        f"{c['tablas']} tablas, {c['columnas']} columnas y {c['foraneas']} claves foráneas. El "
        "acceso se realiza mediante consultas escritas de forma explícita y sin mapeador "
        "objeto-relacional, decisión que responde a la naturaleza del sistema, porque al "
        "reservar una cita importa exactamente qué se ejecuta, en qué orden y qué queda "
        "bloqueado mientras tanto."
    )
    d.parrafo(
        "El diseño se organiza en cuatro zonas que agrupan las tablas según el papel que "
        "cumplen. La separación no es una preferencia de orden, sino la que deja ver que el "
        "acceso al sistema y el acto clínico son dos asuntos distintos y que solo se tocan por "
        "el vínculo entre una persona y la cuenta con la que entra."
    )
    d.tabla(
        "Organización de las tablas por zona",
        ["Zona", "Qué agrupa", "Tablas"],
        [[rotulo.split("·")[0].strip().capitalize(), rotulo.split("·")[1].strip(),
          ", ".join(t for grupo in columnas for t in grupo)]
         for _clave, rotulo, _x, _ancho, _fondo, columnas in figuras.ZONAS],
        nota="Elaboración propia. Es el mismo reparto que emplea el modelo físico del "
             "apartado 5.10.",
        anchos=[2.4, 5.4, 8.5],
    )
    d.parrafo(
        "Ese vínculo entre la persona y su cuenta es la única costura entre las dos mitades, y "
        "es deliberadamente opcional. Tanto el médico como el paciente pueden existir sin "
        "cuenta de acceso, lo que permite registrar a un paciente que nunca va a entrar al "
        "sistema y suspender el ingreso de un profesional sin sacarlo de la agenda ni romper "
        "las citas que ya tenía. Es también la razón por la cual el rol no se guarda en la "
        "ficha de la persona sino en la cuenta, que es donde el control de acceso lo busca."
    )
    d.tabla(
        "Propósito de cada tabla",
        ["Tabla", "Qué guarda", "Columnas"],
        [[tabla, esquema.PROPOSITO[tabla], str(len(esquema.columnas(tabla, datos)))]
         for tabla in esquema.TABLAS],
        nota="Elaboración propia a partir del esquema real de la base de datos.",
        anchos=[2.6, 11.2, 2.5],
    )

    d.titulo("5.8.1 La baja lógica y por qué no se borra", nivel=3)
    d.parrafo(
        f"Cuatro tablas llevan una columna de estado que permite retirar una fila de la "
        f"operación sin eliminarla, que son {', '.join(list(BAJA_LOGICA)[:-1])} y "
        f"{list(BAJA_LOGICA)[-1]}. La decisión no es de comodidad, y en cada caso obedece a "
        "una razón concreta."
    )
    d.vinetas([(tabla.capitalize(), f"porque {porque}.")
               for tabla, porque in BAJA_LOGICA.items()])
    d.parrafo(
        "El caso de la cita es distinto, porque su estado no distingue lo activo de lo "
        "retirado sino lo vigente de lo cancelado. Una cita cancelada no es una fila oculta, "
        "es un hecho del que hay que dejar constancia, ya que libera un turno que vuelve a "
        "ofrecerse y explica por qué una atención prevista no ocurrió."
    )


# --- 5.9 -----------------------------------------------------------------------

def _entidad_relacion(d, datos):
    d.titulo("5.9 Modelo entidad-relación conceptual", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El modelo conceptual presenta las entidades del dominio y las relaciones entre ellas, "
        "sin descender al detalle de los atributos ni a la forma en que se almacenan. Cada "
        "enlace lleva el nombre de la columna que lo establece, de modo que el modelo pueda "
        "compararse con el esquema sin necesidad de una equivalencia aparte."
    )
    d.figura(
        "Modelo entidad-relación conceptual",
        DIAGRAMAS / "FIG-mer.png",
        nota="Elaboración propia a partir de las claves foráneas declaradas en la base de "
             "datos.",
    )
    d.parrafo(
        "El modelo no tiene forma de árbol sino de dos centros. Las entidades de médico y de "
        "paciente ocupan el medio y de ellas cuelgan "
        "las cuatro entidades de la atención, que son la cita, la historia clínica, la "
        "consulta y el examen. Las cuatro repiten el mismo par de referencias, y esa "
        "repetición es la que sostiene todo el control de acceso, ya que preguntar si un "
        "registro le pertenece a quien lo pide siempre se resuelve del mismo modo."
    )
    d.parrafo(
        "La referencia al médico significa cosas distintas según la entidad. En la cita indica "
        "a quién se va a "
        "atender, es decir, de quién es la agenda que se ocupa. En la historia clínica y en la "
        "consulta indica quién escribió, esto es, quién firma el registro y responde por él. "
        "Son dos sentidos que la misma columna no distingue, y por eso el sistema los "
        "distingue en el momento de escribir, tomando la autoría de la sesión."
    )
    d.parrafo(
        "La receta no cuelga del paciente sino de la consulta, y de ahí "
        "toma a quién se le prescribe. La razón es que una prescripción sin diagnóstico que la "
        "sustente no tendría sentido clínico, de manera que el modelo impide que exista."
    )
    d.parrafo(
        "La consulta no referencia a la cita. El diagnóstico se registra "
        "después de haber atendido, pero lo que queda guardado es a quién se atendió y quién "
        "lo atendió, no el turno en el que ocurrió. La cita es el motivo por el que las dos "
        "personas se encontraron y no un dato del hallazgo clínico, que conserva su valor "
        "aunque el turno se reprograme o se cancele después."
    )


# --- 5.10 ----------------------------------------------------------------------

def _fisico(d, datos):
    c = esquema.conteo(datos)

    d.titulo("5.10 Modelo físico de la base de datos", nivel=2, nueva_pagina=True)
    d.parrafo(
        "El modelo físico corresponde a la implementación del modelo conceptual sobre el "
        "gestor de base de datos, con los tipos de dato concretos, las claves y las relaciones "
        f"tal como quedan declaradas. Comprende las {c['tablas']} tablas con sus "
        f"{c['columnas']} columnas y las {c['foraneas']} claves foráneas que las relacionan."
    )
    d.parrafo(
        f"El diagrama no está dibujado a mano. Se genera leyendo {esquema.fuente()}, de manera "
        "que lo que muestra es literalmente lo que la base tiene, con los tipos y las claves "
        "que el gestor declara. Se presenta en orientación horizontal porque a lo ancho de una "
        "página vertical los nombres de las columnas dejan de leerse."
    )
    ancho = d.seccion_horizontal()
    d.figura(
        "Modelo físico de la base de datos",
        DIAGRAMAS / "FIG-fisico.png",
        nota="Elaboración propia, generada desde el esquema real. Las agrupaciones "
             "corresponden a las zonas del apartado 5.8 y la flecha apunta de la clave "
             "foránea a la clave primaria que referencia.",
        ancho=ancho,
    )
    d.seccion_vertical()
    d.parrafo(
        "Las once tablas emplean el motor transaccional del gestor, condición necesaria para "
        "que la reserva de una cita pueda comprobarse y escribirse dentro de una misma "
        "operación que se confirma entera o no se confirma. Las claves primarias son "
        "autonuméricas en todas ellas, de modo que el sistema no depende de que un dato del "
        "dominio sea único y estable en el tiempo."
    )
    d.parrafo(
        "Las claves foráneas se concentran en la zona de atención. Las tablas de acceso y de "
        "catálogos no referencian a ninguna otra, porque no dependen de nada, y son en cambio "
        "las referenciadas. Esa dirección es la que permite que el "
        "sistema arranque con los catálogos vacíos y se vaya poblando sin dejar filas "
        "apuntando a lo que todavía no existe."
    )


# --- 5.11 ----------------------------------------------------------------------

def _diccionario(d, datos):
    # Sin salto: `seccion_vertical()` ya abrió página al cerrar la apaisada, y un salto más
    # dejaba una página con dos párrafos y el resto en blanco.
    d.titulo("5.11 Diccionario de datos", nivel=2)
    d.parrafo(
        "El diccionario de datos describe cada columna indicando su tipo, si admite ausencia "
        "de valor, el papel que cumple como clave y el significado del dato que almacena. Se "
        "presentan aquí tres tablas, escogidas por lo que cada una demuestra, y el diccionario "
        "completo de las once consta en el anexo correspondiente."
    )
    d.parrafo(
        "Las columnas, los tipos, los nulos y las claves se leen del propio esquema y no están "
        "transcritos, de manera que lo que se describe es lo que la base tiene. Las "
        "descripciones sí están escritas, porque el esquema no lleva comentarios incorporados, "
        "y el generador comprueba que ninguna columna se quede sin la suya."
    )
    for indice, tabla in enumerate(DETALLADAS, start=1):
        # Sin salto por tabla. FactuGest lo pone porque sus tres tablas tienen veinte
        # columnas cada una; estas tienen seis, seis y cinco, y una página por tabla
        # dejaría dos tercios en blanco tres veces seguidas.
        d.titulo(f"5.11.{indice} Tabla {tabla}", nivel=3)
        d.parrafo(INTRO_TABLA[tabla])
        d.tabla(
            f"Diccionario de datos de la tabla {tabla}",
            ["Columna", "Tipo", "Nulo", "Clave", "Descripción"],
            [[nombre, tipo, nulo, clave, descripcion]
             for nombre, tipo, nulo, clave, descripcion in esquema.columnas(tabla, datos)],
            nota="Elaboración propia a partir del esquema real de la base de datos.",
            anchos=[3.2, 3.0, 1.3, 2.0, 6.8],
        )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
