# -*- coding: utf-8 -*-
"""
Figuras del documento de grado de MediApp.

Todas se dibujan con matplotlib y desde los datos reales del proyecto, por la misma razón por
la que se dibujan así los diagramas de casos de uso, y es que van a cambiar cada vez que cambie
el sistema, y rehacerlas a mano termina en figuras que ya no coinciden con el texto que las
acompaña. El modelo entidad-relación y el modelo físico salen del esquema leído con
`esquema.py`, la priorización sale de `requisitos.py` y el mapa de navegación se escribe contra
las rutas reales de la aplicación.

**El color sale de `paleta.py`**, que es el morado de las tarjetas del panel. Aquí sí manda,
porque estas son figuras que presentan datos y el color señala categorías. En los diagramas de
casos de uso, en cambio, el color se limita al óvalo, según la decisión recogida en el cuaderno.

    python figuras.py            # dibuja todas
    python figuras.py mer        # dibuja solo la que se nombre
"""
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle

import esquema
import requisitos
from paleta import (FONDO_SUAVE, GRIS, GRIS_CLARO, MORADO, MORADO_OSCURO, RELLENO, TINTA,
                    serie)

SALIDA = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"

NEGRO = "#000000"
FUENTE = "DejaVu Sans"


def _lienzo(ancho, alto):
    figura, ejes = plt.subplots(figsize=(ancho, alto))
    ejes.set_xlim(0, 100)
    ejes.set_ylim(0, 100)
    ejes.axis("off")
    return figura, ejes


def _guardar(figura, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / nombre
    figura.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return destino


def _caja(ejes, x, y, ancho, alto, texto, relleno=RELLENO, borde=MORADO_OSCURO,
          color_texto=NEGRO, tamano=8.0, negrita=False, ancho_texto=22):
    ejes.add_patch(FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=0,rounding_size=1.2",
                                  facecolor=relleno, edgecolor=borde, linewidth=1.2, zorder=2))
    ejes.text(x + ancho / 2, y + alto / 2, "\n".join(textwrap.wrap(texto, ancho_texto)),
              ha="center", va="center", fontsize=tamano, color=color_texto, zorder=3,
              weight="bold" if negrita else "normal")


# --- 1. Modelo entidad-relación conceptual --------------------------------------

def mer():
    """Las once entidades y sus relaciones, leídas del esquema real."""
    datos = esquema.leer()
    relaciones = esquema.relaciones(datos)

    # Posiciones pensadas para que el paciente y el médico queden en el centro, que es
    # donde el modelo los pone, y las relaciones no se crucen más de lo necesario.
    lugares = {
        "rol":          (3, 87), "usuario":      (26, 87),
        "especialidad": (3, 64), "medico":       (26, 64), "paciente":  (57, 64),
        "historia":     (2, 38), "cita":         (24, 38),
        "examen":       (46, 38), "consulta":    (68, 38),
        "receta":       (68, 12), "medicamento": (85, 12),
    }
    ancho, alto = 14, 8

    figura, ejes = _lienzo(11.5, 8.0)
    centros = {}
    for tabla, (x, y) in lugares.items():
        centros[tabla] = (x + ancho / 2, y + alto / 2)

    for origen, columna, destino, _ in relaciones:
        xo, yo = centros[origen]
        xd, yd = centros[destino]
        ejes.plot([xo, xd], [yo, yd], color=GRIS, lw=1.0, zorder=1)
        # La etiqueta va cerca del extremo de origen y no en el medio. Puestas todas al
        # 50 %, las de `medico` y `paciente` hacia sus cuatro tablas hijas caen casi en el
        # mismo punto y se escriben una encima de otra.
        largo = ((xd - xo) ** 2 + (yd - yo) ** 2) ** 0.5
        t = 0.30 if largo > 30 else 0.5
        ejes.text(xo + (xd - xo) * t, yo + (yd - yo) * t, columna, fontsize=5.4, color=GRIS,
                  ha="center", va="center", zorder=4, style="italic",
                  bbox=dict(facecolor="white", edgecolor="none", pad=0.6))

    for tabla, (x, y) in lugares.items():
        _caja(ejes, x, y, ancho, alto, tabla, tamano=8.4, negrita=True, ancho_texto=14)

    return _guardar(figura, "FIG-mer.png")


# --- 2. Diagrama conceptual -----------------------------------------------------

def conceptual():
    """Qué hace el sistema, en una figura, sin entrar en cómo está construido."""
    figura, ejes = _lienzo(10.5, 6.2)

    ejes.add_patch(Rectangle((24, 8), 52, 84, facecolor=FONDO_SUAVE, edgecolor=MORADO_OSCURO,
                             lw=1.4, zorder=1))
    ejes.text(50, 88, "MEDIAPP", ha="center", va="center", fontsize=12, weight="bold",
              color=NEGRO, zorder=3)
    ejes.text(50, 83, "Agendamiento de citas y gestión del acto clínico", ha="center",
              va="center", fontsize=8, color=NEGRO, zorder=3)

    bloques = [
        (28, 62, "Agenda de citas\ny disponibilidad"),
        (28, 44, "Historia clínica\ny diagnósticos"),
        (28, 26, "Prescripciones\ny laboratorio"),
        (54, 62, "Personas\ny catálogos"),
        (54, 44, "Control de acceso\npor rol"),
        (54, 26, "Cuentas\ny sesión"),
    ]
    for x, y, texto in bloques:
        _caja(ejes, x, y, 18, 14, texto.replace("\n", " "), tamano=7.6, ancho_texto=16)

    actores = [(4, 66, "Administrador"), (4, 40, "Médico"), (4, 14, "Paciente")]
    for x, y, nombre in actores:
        _caja(ejes, x, y, 16, 12, nombre, relleno="white", borde=NEGRO, tamano=8.2,
              negrita=True, ancho_texto=14)
        ejes.annotate("", xy=(24, y + 6), xytext=(20, y + 6),
                      arrowprops=dict(arrowstyle="->", color=NEGRO, lw=1.1))

    _caja(ejes, 82, 40, 15, 12, "Base de datos MySQL", relleno="white", borde=NEGRO,
          tamano=7.6, ancho_texto=12)
    ejes.annotate("", xy=(82, 46), xytext=(76, 46),
                  arrowprops=dict(arrowstyle="<->", color=NEGRO, lw=1.1))

    return _guardar(figura, "FIG-conceptual.png")


# --- 3. Arquitectura por capas --------------------------------------------------

def arquitectura():
    """Las capas reales del sistema, según lo descrito en la guía de arquitectura."""
    figura, ejes = _lienzo(9.5, 6.6)

    capas = [
        (78, "Capa de presentación",
         "Plantillas Jinja2 con Bootstrap 5 y JavaScript sin marco de trabajo"),
        (58, "Capa de control",
         "Rutas Flask de index.py, con los decoradores que comprueban sesión y rol"),
        (38, "Capa de reglas de negocio",
         "Validación de la agenda, reglas de fecha y comprobaciones de propiedad"),
        (18, "Capa de acceso a datos",
         "database.py, con una conexión por petición tomada de un pool"),
    ]
    for y, titulo, detalle in capas:
        ejes.add_patch(FancyBboxPatch((10, y), 80, 16,
                                      boxstyle="round,pad=0,rounding_size=1.5",
                                      facecolor=RELLENO, edgecolor=MORADO_OSCURO, lw=1.3,
                                      zorder=2))
        ejes.text(50, y + 10.5, titulo, ha="center", va="center", fontsize=9.4,
                  weight="bold", color=NEGRO, zorder=3)
        ejes.text(50, y + 5, detalle, ha="center", va="center", fontsize=7.2, color=NEGRO,
                  zorder=3)

    for y in (74, 54, 34):
        ejes.annotate("", xy=(50, y - 4), xytext=(50, y),
                      arrowprops=dict(arrowstyle="<->", color=NEGRO, lw=1.2))

    _caja(ejes, 10, 2, 80, 11, "Base de datos MySQL con las once tablas del esquema",
          relleno="white", borde=NEGRO, tamano=8.6, ancho_texto=60)
    ejes.annotate("", xy=(50, 13), xytext=(50, 18),
                  arrowprops=dict(arrowstyle="<->", color=NEGRO, lw=1.2))
    ejes.text(50, 96, "Navegador del usuario", ha="center", va="center", fontsize=9,
              weight="bold", color=NEGRO)
    ejes.annotate("", xy=(50, 94), xytext=(50, 90),
                  arrowprops=dict(arrowstyle="<->", color=NEGRO, lw=1.2))

    return _guardar(figura, "FIG-arquitectura.png")


# --- 4. Matriz de permisos por rol ----------------------------------------------

# La matriz autoritativa del proyecto. C crear, E editar, B eliminar, L leer, y el guion
# significa que ese rol no alcanza el módulo.
PERMISOS = [
    ("historia",     "L",   "CEB", "L*"),
    ("consulta",     "L",   "CE",  "L*"),
    ("receta",       "L",   "CEB", "L*"),
    ("examen",       "E",   "C",   "L*"),
    ("cita",         "CEB", "L*",  "CE*"),
    ("usuario",      "CEB", "-",   "-"),
    ("medico",       "CEB", "L",   "-"),
    ("paciente",     "CEB", "L",   "L*"),
    ("especialidad", "CEB", "-",   "-"),
    ("medicamento",  "CEB", "-",   "-"),
    ("rol",          "L",   "-",   "-"),
]

_TONO = {"CEB": MORADO_OSCURO, "CE": MORADO, "C": MORADO, "E": MORADO,
         "L": RELLENO, "L*": RELLENO, "CE*": MORADO, "-": "white"}


def permisos():
    """Quién puede hacer qué sobre cada módulo, que es el corazón del proyecto."""
    roles = ["Administrador", "Médico", "Paciente"]
    figura, ejes = plt.subplots(figsize=(8.0, 6.4))
    ejes.set_xlim(0, 3)
    ejes.set_ylim(0, len(PERMISOS))
    ejes.axis("off")

    for fila, (tabla, *celdas) in enumerate(PERMISOS):
        y = len(PERMISOS) - fila - 1
        ejes.text(-0.08, y + 0.5, tabla, ha="right", va="center", fontsize=8.6, color=NEGRO)
        for columna, valor in enumerate(celdas):
            color = _TONO[valor]
            ejes.add_patch(Rectangle((columna, y), 1, 1, facecolor=color,
                                     edgecolor=GRIS_CLARO, lw=0.8))
            claro = valor in ("CEB", "CE", "C", "E", "CE*")
            ejes.text(columna + 0.5, y + 0.5, valor if valor != "-" else "",
                      ha="center", va="center", fontsize=8.2,
                      color="white" if claro else NEGRO,
                      weight="bold" if claro else "normal")

    for columna, rol in enumerate(roles):
        ejes.text(columna + 0.5, len(PERMISOS) + 0.25, rol, ha="center", va="bottom",
                  fontsize=9.2, weight="bold", color=NEGRO)

    leyenda = [
        Line2D([], [], marker="s", linestyle="", markersize=9, markerfacecolor=MORADO_OSCURO,
               markeredgecolor=GRIS_CLARO, label="C crear   E editar   B eliminar"),
        Line2D([], [], marker="s", linestyle="", markersize=9, markerfacecolor=RELLENO,
               markeredgecolor=GRIS_CLARO, label="L solo lectura"),
        Line2D([], [], marker="s", linestyle="", markersize=9, markerfacecolor="white",
               markeredgecolor=GRIS_CLARO, label="Sin acceso al módulo"),
    ]
    ejes.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.02),
                ncol=3, frameon=False, fontsize=7.8)
    ejes.text(1.5, -0.9, "El asterisco indica que el rol alcanza únicamente sus propios "
                          "registros.",
              ha="center", va="center", fontsize=7.4, color=GRIS, style="italic")

    return _guardar(figura, "FIG-permisos.png")


# --- 5. Priorización MoSCoW -----------------------------------------------------
# 🔴 Esta figura responde a **O04**, y el evaluador no escribió que faltara una tabla sino que
# «el modelo MoSCoW no se observa». Por eso no es un gráfico de barras. Una barra dice cuántos
# requisitos cayeron en cada categoría, que es justamente lo que menos importa, y no dice lo
# único que el modelo comunica, que es **qué se compromete el proyecto a entregar y qué no**.
#
# Cada tarjeta lleva el compromiso que representa la categoría, el corte de puntaje del que
# sale y ejemplos reales tomados del catálogo. Los ejemplos **no están escritos a mano**, se
# eligen por puntaje, así que si mañana cambia la calificación de un requisito la figura cambia
# con ella. FactuGest no tiene esta figura porque a FactuGest no se la pidieron.

_MOSCOW = [
    ("MUST HAVE", "must", MORADO_OSCURO, "#DED6F2", "Puntaje 4,6 o más",
     "Sin esto el sistema no cumple su propósito. Su ausencia invalida la entrega."),
    ("SHOULD HAVE", "should", MORADO, "#E7D5EF", "Puntaje de 4,0 a 4,5",
     "El sistema funciona sin esto, pero obliga a resolver a mano lo que debería resolver el "
     "programa."),
    ("COULD HAVE", "could", "#B98BD0", "#EFE3F5", "Puntaje menor que 4,0",
     "Aporta comodidad y puede aplazarse a una versión posterior sin afectar la operación."),
    ("WON'T HAVE", "wont", GRIS, "#F2F2F2", "No se deriva del puntaje",
     "Se evaluó y se decidió no construirlo en esta versión. Delimita hasta dónde llega el "
     "compromiso."),
]


def moscow():
    """El modelo MoSCoW con ejemplos reales dentro de cada categoría."""
    grupos = requisitos.por_moscow()
    conteo = requisitos.conteo()
    total = conteo["funcionales"]

    # Los ejemplos se eligen solos, por puntaje descendente, para que la figura no pueda
    # quedar citando un requisito que ya cambió de categoría.
    def ejemplos(clave, cuantos=3):
        if clave == "wont":
            return [q for q, _por_que in requisitos.FUERA_DE_ALCANCE[:cuantos]]
        etiqueta = {"must": "Must have", "should": "Should have", "could": "Could have"}[clave]
        ordenados = sorted(grupos[etiqueta],
                           key=lambda f: -requisitos.puntaje(f[5], f[6]))
        return [f"{fila[0]} {fila[1]}" for fila in ordenados[:cuantos]]

    figura, ejes = _lienzo(14.0, 7.0)
    ancho, hueco = 23.0, 1.7
    inicio = (100 - (4 * ancho + 3 * hueco)) / 2

    for indice, (titulo, clave, color, fondo, corte, compromiso) in enumerate(_MOSCOW):
        x = inicio + indice * (ancho + hueco)
        cantidad = conteo["fuera_de_alcance"] if clave == "wont" else conteo[clave]

        ejes.add_patch(FancyBboxPatch((x, 6), ancho, 82,
                                      boxstyle="round,pad=0,rounding_size=1.2",
                                      facecolor=fondo, edgecolor=color, lw=1.5, zorder=2))
        # Franja superior con el nombre de la categoría y su cuenta.
        ejes.add_patch(FancyBboxPatch((x, 70), ancho, 18,
                                      boxstyle="round,pad=0,rounding_size=1.2",
                                      facecolor=color, edgecolor=color, lw=1.5, zorder=3))
        ejes.text(x + ancho / 2, 82, titulo, ha="center", va="center", fontsize=11.5,
                  weight="bold", color="white", zorder=4)
        # En «Won't have» no se cuentan requisitos sino capacidades descartadas, y llamarlas
        # requisitos daría a entender que el sistema las tiene sin implementar.
        etiqueta = "capacidades excluidas" if clave == "wont" else (
            "requisito" if cantidad == 1 else "requisitos")
        ejes.text(x + ancho / 2, 74.5, f"{cantidad} {etiqueta}", ha="center", va="center",
                  fontsize=9.0 if clave == "wont" else 9.6, color="white", zorder=4)

        ejes.text(x + ancho / 2, 66, corte, ha="center", va="center", fontsize=7.6,
                  color=GRIS, style="italic", zorder=4)
        ejes.text(x + ancho / 2, 57,
                  "\n".join(textwrap.wrap(compromiso, 34)), ha="center", va="center",
                  fontsize=7.8, color=NEGRO, zorder=4)

        ejes.plot([x + 2.5, x + ancho - 2.5], [46, 46], color=color, lw=0.9, zorder=4)
        rotulo = "Se decidió no construir" if clave == "wont" else "Por ejemplo"
        ejes.text(x + 2.5, 42.5, rotulo, ha="left", va="center", fontsize=7.4,
                  weight="bold", color=color, zorder=4)

        renglon = 38.0
        for texto in ejemplos(clave):
            partido = textwrap.wrap(texto, 30)
            ejes.text(x + 2.5, renglon, "- " + partido[0], ha="left", va="top", fontsize=7.2,
                      color=NEGRO, zorder=4)
            for extra in partido[1:3]:
                renglon -= 3.0
                ejes.text(x + 4.2, renglon, extra, ha="left", va="top", fontsize=7.2,
                          color=NEGRO, zorder=4)
            renglon -= 8.0

    ejes.text(50, 1.5,
              f"Los {total} requisitos funcionales del sistema se reparten en las tres primeras "
              f"categorías según su puntaje. La cuarta no sale de un puntaje bajo, porque un "
              f"requisito implementado nunca es algo que no se hará.",
              ha="center", va="center", fontsize=8.0, color=GRIS, style="italic")

    return _guardar(figura, "FIG-moscow.png")


# --- 6. Ciclo Scrum adaptado ----------------------------------------------------

def scrum():
    """El ciclo, espejando la figura de FactuGest.

    La primera versión ponía las cinco etapas en fila, lo que dice el orden pero no dice lo
    único que distingue a Scrum de una cascada, y es que hay un ciclo que se repite y que
    dentro del sprint ocurre su propio ritmo diario. Esta reproduce la forma de FactuGest, con
    el sprint recuadrado aparte y el aprendizaje volviendo al backlog.
    """
    figura, ejes = _lienzo(11.5, 6.0)

    _caja(ejes, 3, 44, 22, 15, "Product backlog, 87 requisitos priorizados",
          relleno="white", borde=NEGRO, tamano=9.4, negrita=True, ancho_texto=18)
    _caja(ejes, 30, 74, 22, 14, "Planificación del sprint", tamano=9.0, ancho_texto=22)
    _caja(ejes, 30, 44, 22, 15, "Sprint backlog, lo comprometido para dos semanas",
          tamano=9.0, ancho_texto=24)
    _caja(ejes, 30, 8, 22, 14, "Revisión y retrospectiva", tamano=9.0, ancho_texto=22)

    # El recuadro del sprint, con su ritmo interno.
    ejes.add_patch(FancyBboxPatch((58, 12), 39, 74,
                                  boxstyle="round,pad=0,rounding_size=1.6",
                                  facecolor=FONDO_SUAVE, edgecolor=MORADO_OSCURO, lw=1.5,
                                  zorder=1))
    ejes.text(77.5, 80, "SPRINT DE 2 SEMANAS", ha="center", va="center", fontsize=10.6,
              weight="bold", color=MORADO_OSCURO, zorder=3)

    interno = [
        (62, "Reunión diaria de seguimiento", "white", GRIS_CLARO, False),
        (44, "Desarrollo, revisión y pruebas", "white", GRIS_CLARO, False),
        (20, "Incremento. Un módulo funcionando", RELLENO, MORADO_OSCURO, True),
    ]
    for y, texto, relleno, borde, resaltado in interno:
        _caja(ejes, 61, y, 33, 13, texto, relleno=relleno, borde=borde, tamano=8.8,
              negrita=resaltado, ancho_texto=30)
    for y in (62, 44):
        ejes.annotate("", xy=(77.5, y - 5), xytext=(77.5, y),
                      arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.2))

    flechas = [
        ((25, 55), (30, 76)),        # backlog -> planificación
        ((41, 74), (41, 59)),        # planificación -> sprint backlog
        ((52, 51), (61, 48)),        # sprint backlog -> sprint
        ((61, 22), (52, 18)),        # incremento -> revisión
        ((30, 16), (14, 44)),        # revisión -> backlog
    ]
    for desde, hasta in flechas:
        ejes.annotate("", xy=hasta, xytext=desde,
                      arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.3,
                                      connectionstyle="arc3,rad=0.12"))
    ejes.text(14, 24, "lo aprendido vuelve al backlog", ha="center", va="center",
              fontsize=8.2, color=GRIS, style="italic")
    ejes.text(50, 2, "Cada sprint terminó con un módulo utilizable y no con una parte de "
                     "varios, de modo que el avance se pudo mostrar y corregir.",
              ha="center", va="center", fontsize=8.4, color=GRIS, style="italic")

    return _guardar(figura, "FIG-scrum.png")


# --- 7. Modelo físico de la base ------------------------------------------------
# Se espeja el modelo físico de FactuGest, que es el listón de calidad de esta figura. De él se
# hereda lo que la hace legible: las tablas agrupadas en **zonas rotuladas** con su propio
# fondo, cada columna con su **tipo de dato** a la derecha, las claves marcadas con un símbolo
# en lugar de una sigla, el **ruteo ortogonal** por pasillos entre zonas para que ninguna línea
# cruce por encima de una tabla, y un recuadro de «cómo se lee».
#
# El reparto por zonas no es decoración. Dice de un vistazo que el acceso y el acto clínico son
# dos mundos distintos y que solo se tocan por el vínculo opcional de las personas con su
# cuenta, que es la idea central del proyecto.

# (clave, rótulo, x, ancho, color de fondo, [columnas de tablas, de arriba abajo])
# La zona de atención va en **dos columnas** porque sus cinco tablas suman treinta filas y en
# una sola se salen de la hoja. FactuGest hace lo mismo con su zona comercial.
ZONAS = [
    ("acceso", "ACCESO · quién entra", 1.0, 18.0, "#F2F7F4",
     [["rol", "usuario"]]),
    ("catalogos", "CATÁLOGOS · no cambian con la operación", 21.0, 18.5, "#FBF6EE",
     [["especialidad", "medicamento"]]),
    ("personas", "PERSONAS · de quién se habla", 41.5, 18.5, "#F7F1FA",
     [["medico", "paciente"]]),
    ("atencion", "ATENCIÓN · agenda y acto clínico", 62.0, 37.0, "#F4F1FA",
     [["cita", "historia", "consulta"], ["receta", "examen"]]),
]

_ENCABEZADO = {"acceso": "#DCEAE2", "catalogos": "#F3E6D2", "personas": "#E7D5EF",
               "atencion": "#DED6F2"}

_ALTO_FILA = 1.55
_ALTO_TITULO = 2.5
_HUECO_TABLA = 2.0


def _tipo_motor(nombre_columna, tabla, datos):
    """El tipo tal como lo declara el motor, en mayúsculas, igual que en FactuGest."""
    crudas, _ = datos
    for nombre, tipo, *_ in crudas[tabla]:
        if nombre != nombre_columna:
            continue
        base = tipo.split("(")[0].upper()
        if base == "ENUM":
            return "ENUM"
        if base == "VARCHAR" and "(" in tipo:
            return f"VARCHAR({tipo[tipo.index('(') + 1:tipo.index(')')]})"
        return base
    return ""


def fisico():
    """Las once tablas con todas sus columnas, para la página apaisada (O14)."""
    datos = esquema.leer()
    relaciones = esquema.relaciones(datos)

    figura, ejes = plt.subplots(figsize=(16.0, 9.0))
    ejes.set_xlim(0, 100)
    ejes.set_ylim(0, 57)
    ejes.axis("off")

    # -- se sitúa cada tabla dentro de su zona, columna por columna y de arriba abajo --
    cajas, marcos = {}, []
    for clave, rotulo, x, ancho, fondo, columnas in ZONAS:
        ancho_col = (ancho - 2.0 - 1.0 * (len(columnas) - 1)) / len(columnas)
        piso = 44.0
        for indice, grupo in enumerate(columnas):
            cima = 44.0
            x_col = x + 1.0 + indice * (ancho_col + 1.0)
            for tabla in grupo:
                alto = _ALTO_TITULO + len(esquema.columnas(tabla, datos)) * _ALTO_FILA
                cajas[tabla] = (x_col, cima - alto, ancho_col, alto, clave)
                cima -= alto + _HUECO_TABLA
            piso = min(piso, cima + _HUECO_TABLA)
        marcos.append((rotulo, x, piso - 1.2, ancho, 44.0 - piso + 4.4, fondo))

    # -- el marco de cada zona, por debajo de las tablas --
    for rotulo, x, y, ancho, alto, fondo in marcos:
        ejes.add_patch(FancyBboxPatch((x, y), ancho, alto,
                                      boxstyle="round,pad=0,rounding_size=0.8",
                                      facecolor=fondo, edgecolor=GRIS_CLARO, lw=1.0,
                                      linestyle=(0, (4, 3)), zorder=1))
        ejes.text(x + 1.0, y + alto - 1.5, rotulo, ha="left", va="center", fontsize=7.2,
                  color=GRIS, weight="bold", zorder=4)

    # -- las tablas --
    for tabla, (x, y, ancho, alto, zona) in cajas.items():
        ejes.add_patch(FancyBboxPatch((x, y), ancho, alto,
                                      boxstyle="round,pad=0,rounding_size=0.4",
                                      facecolor="white", edgecolor=GRIS_CLARO, lw=0.9,
                                      zorder=2))
        ejes.add_patch(Rectangle((x, y + alto - _ALTO_TITULO), ancho, _ALTO_TITULO,
                                 facecolor=_ENCABEZADO[zona], edgecolor="none", zorder=3))
        ejes.text(x + 0.8, y + alto - _ALTO_TITULO / 2, tabla, ha="left", va="center",
                  fontsize=7.6, weight="bold", color=NEGRO, zorder=4)

        for fila, (nombre, _t, _n, clave, _d) in enumerate(esquema.columnas(tabla, datos)):
            cy = y + alto - _ALTO_TITULO - (fila + 0.5) * _ALTO_FILA
            if clave == "Primaria":
                ejes.plot(x + 1.0, cy, marker="o", markersize=2.6, color="#C87A2B", zorder=5)
            elif clave == "Foránea":
                ejes.plot(x + 1.0, cy, marker="D", markersize=2.3, color=MORADO_OSCURO,
                          zorder=5)
            ejes.text(x + 1.9, cy, nombre, ha="left", va="center", fontsize=5.5, color=NEGRO,
                      zorder=5, weight="bold" if clave == "Primaria" else "normal")
            ejes.text(x + ancho - 0.7, cy, _tipo_motor(nombre, tabla, datos), ha="right",
                      va="center", fontsize=4.7, color=GRIS, zorder=5)

    # -- ruteo ortogonal por los pasillos entre zonas --
    # Cada línea sale por el lado izquierdo de su tabla, recorre un pasillo vertical y entra al
    # destino por su lado derecho. Los pasillos son los huecos entre zonas, y cada relación
    # toma un carril propio dentro del pasillo para que dos líneas no se monten.
    pasillos = {"acceso": 20.0, "catalogos": 40.4, "personas": 60.9}
    carril = {}
    for origen, columna, destino, _ in relaciones:
        xo, yo, ao, ho, zona_o = cajas[origen]
        xd, yd, ad, hd, zona_d = cajas[destino]
        nombres = [c[0] for c in esquema.columnas(origen, datos)]
        y_salida = yo + ho - _ALTO_TITULO - (nombres.index(columna) + 0.5) * _ALTO_FILA
        y_llegada = yd + hd - _ALTO_TITULO - 0.5 * _ALTO_FILA

        if zona_o == zona_d:
            x_pasillo = xo - 1.0
        else:
            indice = carril.get(zona_d, 0)
            carril[zona_d] = indice + 1
            x_pasillo = pasillos[zona_d] - indice * 0.5

        puntos = [(xo, y_salida), (x_pasillo, y_salida), (x_pasillo, y_llegada),
                  (xd + ad + 1.1, y_llegada)]
        for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
            ejes.plot([x1, x2], [y1, y2], color=GRIS, lw=0.7, zorder=1,
                      solid_capstyle="round")
        ejes.annotate("", xy=(xd + ad, y_llegada), xytext=(xd + ad + 1.1, y_llegada),
                      arrowprops=dict(arrowstyle="-|>", color=GRIS, lw=0.7, shrinkA=0,
                                      shrinkB=0), zorder=5)

    # -- recuadro de cómo se lee --
    ejes.add_patch(FancyBboxPatch((1.5, 48.5), 97.0, 6.5,
                                  boxstyle="round,pad=0,rounding_size=0.6",
                                  facecolor="white", edgecolor=GRIS_CLARO, lw=1.0,
                                  linestyle=(0, (4, 3)), zorder=2))
    ejes.text(2.8, 53.3, "CÓMO SE LEE", ha="left", va="center", fontsize=7.6, weight="bold",
              color=GRIS, zorder=4)
    ejes.plot(3.4, 51.0, marker="o", markersize=2.6, color="#C87A2B", zorder=4)
    ejes.text(4.4, 51.0, "clave primaria", ha="left", va="center", fontsize=6.6, color=NEGRO,
              zorder=4)
    ejes.plot(19.0, 51.0, marker="D", markersize=2.3, color=MORADO_OSCURO, zorder=4)
    ejes.text(20.0, 51.0, "clave foránea declarada en la base", ha="left", va="center",
              fontsize=6.6, color=NEGRO, zorder=4)
    ejes.text(50.0, 52.0, "La flecha apunta de la clave foránea a la clave primaria que "
                          "referencia.", ha="left", va="center", fontsize=6.6, color=GRIS,
              zorder=4)
    ejes.text(50.0, 50.0, "Ninguna línea pasa por encima de una tabla, todas recorren los "
                          "pasillos entre zonas.", ha="left", va="center", fontsize=6.6,
              color=GRIS, zorder=4)

    return _guardar(figura, "FIG-fisico.png")


# --- 8. Mapa de navegación (O13) ------------------------------------------------

# Los grupos del menú, con el rol que los ve. Levantados de las rutas reales.
NAVEGACION = [
    ("Gestión de personas", "Administrador",
     ["Usuarios", "Médicos", "Pacientes"]),
    ("Agenda", "Administrador, Médico y Paciente",
     ["Citas", "Agendar cita", "Disponibilidad"]),
    ("Acto clínico", "Médico escribe, los demás consultan",
     ["Historia clínica", "Consultas", "Recetas"]),
    ("Laboratorio", "Médico solicita, Administrador resuelve",
     ["Exámenes"]),
    ("Catálogos", "Administrador",
     ["Especialidades", "Medicamentos"]),
]


def _svg_mapa():
    """El mapa se escribe como SVG a mano, igual que en FactuGest.

    Es la única figura que no se dibuja con matplotlib, porque es un organigrama de cajas y
    líneas rectas donde la posición de cada caja se decide a ojo, y en un lenguaje de dibujo
    eso se escribe más corto y se corrige más rápido que empujando coordenadas en Python.
    """
    ancho_caja, alto_caja, hueco = 150, 40, 14
    columnas = len(NAVEGACION)
    ancho = columnas * ancho_caja + (columnas + 1) * hueco
    hojas_max = max(len(g[2]) for g in NAVEGACION)
    alto = 132 + alto_caja + hojas_max * (alto_caja + hueco) + 60

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}" font-family="DejaVu Sans, Arial, sans-serif">',
        f'<rect width="{ancho}" height="{alto}" fill="white"/>',
    ]

    def caja(x, y, w, h, texto, subtitulo=None, relleno=RELLENO, borde=MORADO_OSCURO,
             tamano=13, peso="normal"):
        # El subtítulo se parte en renglones porque hay grupos cuyo texto no cabe de una
        # línea, como el del laboratorio, que se salía por el borde derecho de la caja.
        renglones = textwrap.wrap(subtitulo, 26) if subtitulo else []
        partes.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{relleno}" '
            f'stroke="{borde}" stroke-width="1.6"/>')
        centro = y + h / 2 + (5 - 6 * len(renglones))
        partes.append(
            f'<text x="{x + w / 2}" y="{centro}" text-anchor="middle" font-size="{tamano}" '
            f'font-weight="{peso}" fill="{NEGRO}">{texto}</text>')
        for indice, renglon in enumerate(renglones):
            partes.append(
                f'<text x="{x + w / 2}" y="{centro + 13 + indice * 11}" text-anchor="middle" '
                f'font-size="9.5" fill="{GRIS}">{renglon}</text>')

    def linea(x1, y1, x2, y2):
        partes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{NEGRO}" '
                      f'stroke-width="1.2"/>')

    # N0, el ingreso
    x_centro = ancho / 2
    caja(x_centro - 90, 16, 180, alto_caja, "Ingreso al sistema",
         "login y registro público", relleno="white", borde=NEGRO, tamano=14, peso="bold")

    # N1, el tablero
    y_tablero = 16 + alto_caja + 30
    caja(x_centro - 110, y_tablero, 220, alto_caja, "Tablero según el rol",
         "el menú cambia con el perfil", tamano=14, peso="bold")
    linea(x_centro, 16 + alto_caja, x_centro, y_tablero)

    # N2, los grupos del menú y sus pantallas
    y_grupo = y_tablero + alto_caja + 34
    y_barra = y_grupo - 17
    alto_grupo = alto_caja + 12
    linea(x_centro, y_tablero + alto_caja, x_centro, y_barra)

    centros = []
    for indice, (grupo, quien, hojas) in enumerate(NAVEGACION):
        x = hueco + indice * (ancho_caja + hueco)
        centro = x + ancho_caja / 2
        centros.append(centro)
        linea(centro, y_barra, centro, y_grupo)
        caja(x, y_grupo, ancho_caja, alto_grupo, grupo, quien, tamano=12, peso="bold")

        y_hoja = y_grupo + alto_grupo + hueco
        for hoja in hojas:
            linea(centro, y_hoja - hueco, centro, y_hoja)
            caja(x + 12, y_hoja, ancho_caja - 24, alto_caja - 10, hoja,
                 relleno="white", borde=GRIS, tamano=11)
            y_hoja += alto_caja - 10 + hueco

    linea(min(centros), y_barra, max(centros), y_barra)

    partes.append(
        f'<text x="{x_centro}" y="{alto - 22}" text-anchor="middle" font-size="10.5" '
        f'fill="{GRIS}" font-style="italic">Toda pantalla exige sesión iniciada, y el rol se '
        f'comprueba en el servidor y no solo ocultando la entrada del menú.</text>')
    partes.append("</svg>")
    return "\n".join(partes)


def mapa_navegacion():
    """Escribe el SVG y lo rasteriza, porque python-docx no inserta SVG.

    Se rasteriza con pymupdf, que ya estaba en el proyecto para revisar los documentos, así
    que el mapa no obliga a instalar nada nuevo.
    """
    import pymupdf

    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_svg = SALIDA / "FIG-mapa-navegacion.svg"
    ruta_svg.write_text(_svg_mapa(), encoding="utf-8")

    documento = pymupdf.open(str(ruta_svg))
    imagen = documento[0].get_pixmap(matrix=pymupdf.Matrix(2.4, 2.4))
    ruta_png = SALIDA / "FIG-mapa-navegacion.png"
    imagen.save(str(ruta_png))
    documento.close()
    return ruta_png


# --- 9. Cronograma de actividades (O10) -----------------------------------------
# El rango arranca donde arrancó el de FactuGest, en marzo de 2025, por decisión del autor. La
# cola se estira dos meses porque MediApp tiene una fase que FactuGest no tuvo, la de corrección
# posterior a la primera sustentación, que es la que este trabajo documenta y que ocurrió de
# verdad entre agosto y septiembre de 2026. Un cronograma que la omitiera dejaría fuera
# justamente el periodo del que hay evidencia en el repositorio.

MES_CERO = 2          # marzo, contando enero como 0
MESES_TOTAL = 19      # de marzo de 2025 a septiembre de 2026
ABREVIATURAS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# (fase, color, [(actividad, mes de inicio, duración en meses)])
FASES = [
    ("Análisis", "#D2B4DE", [
        ("Levantamiento de requisitos", 0, 3),
        ("Identificación de actores y roles", 1, 2),
        ("Análisis del problema", 2, 2)]),
    ("Planeación", "#B98BD0", [
        ("Diseño de la solución y arquitectura", 4, 2),
        ("Modelado de datos y casos de uso", 5, 2),
        ("Conformación del product backlog", 6, 2)]),
    ("Ejecución", MORADO, [
        ("Diez sprints de dos semanas", 8, 5),
        ("Integración de los módulos", 12, 2),
        ("Pruebas técnicas", 13, 2)]),
    ("Evaluación", MORADO_OSCURO, [
        ("Pruebas finales y ajustes", 15, 1),
        ("Primera sustentación", 16, 1)]),
    ("Corrección", "#5B2C6F", [
        ("Corrección de hallazgos y deuda técnica", 17, 1),
        ("Pruebas automatizadas", 17, 1),
        ("Elaboración del trabajo escrito", 17, 2),
        ("Sustentación final", 18, 1)]),
]


def cronograma():
    """Diagrama de Gantt de las cinco fases, mes a mes."""
    filas = sum(len(a) for _, _, a in FASES)
    figura, ejes = plt.subplots(figsize=(13.0, 6.2))
    ejes.set_xlim(-0.02, MESES_TOTAL + 1.6)
    ejes.set_ylim(-1.3, filas - 0.25)
    ejes.invert_yaxis()
    ejes.axis("off")

    # Rejilla de meses por debajo de las barras. Sin ella no se puede leer dónde empieza una
    # actividad sin seguir la línea con el dedo hasta el eje.
    cambio_de_anio = 12 - MES_CERO
    for mes in range(MESES_TOTAL + 1):
        grueso = mes == cambio_de_anio
        ejes.plot([mes, mes], [-0.75, filas - 0.35], color=NEGRO if grueso else GRIS_CLARO,
                  linewidth=1.1 if grueso else 0.7, zorder=0)

    for mes in range(MESES_TOTAL):
        ejes.text(mes + 0.5, -0.55, ABREVIATURAS[(MES_CERO + mes) % 12], ha="center",
                  va="center", fontsize=8.4, color=GRIS)
    ejes.text(cambio_de_anio / 2, -1.0, "2025", ha="center", va="center", fontsize=9.4,
              color=NEGRO, weight="bold")
    ejes.text((cambio_de_anio + MESES_TOTAL) / 2, -1.0, "2026", ha="center", va="center",
              fontsize=9.4, color=NEGRO, weight="bold")

    fila = 0
    for nombre, color, actividades in FASES:
        primera, ultima = fila, fila + len(actividades) - 1
        ejes.add_patch(FancyBboxPatch(
            (-6.6, primera - 0.36), 0.16, (ultima - primera) + 0.72,
            boxstyle="round,pad=0.01,rounding_size=0.05",
            facecolor=color, edgecolor="none", clip_on=False, zorder=3))
        ejes.text(-6.8, (primera + ultima) / 2, nombre, ha="right", va="center",
                  fontsize=10.0, color=NEGRO, weight="bold", clip_on=False)

        for actividad, inicio, duracion in actividades:
            ejes.text(-6.35, fila, actividad, ha="left", va="center", fontsize=8.6,
                      color=NEGRO, clip_on=False)
            ejes.add_patch(FancyBboxPatch(
                (inicio + 0.06, fila - 0.24), duracion - 0.12, 0.48,
                boxstyle="round,pad=0.01,rounding_size=0.06",
                facecolor=color, edgecolor=MORADO_OSCURO, linewidth=0.8, zorder=2))
            meses = f"{duracion} mes" + ("es" if duracion > 1 else "")
            ejes.text(inicio + duracion + 0.16, fila, meses, ha="left", va="center",
                      fontsize=7.6, color=GRIS)
            fila += 1

    figura.subplots_adjust(left=0.36, right=0.985, top=0.98, bottom=0.02)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "FIG-cronograma.png"
    figura.savefig(destino, dpi=200, facecolor="white")
    plt.close(figura)
    return destino


# --- 10. Riesgos del proyecto (O09), que NO son una figura ----------------------
# 🔴 El evaluador marcó que los riesgos del documento anterior eran del software y pidió que
# fueran **del proyecto**. Por eso aquí no hay ni un solo riesgo técnico de la aplicación, y sí
# los del trabajo de grado como empresa, que son el equipo, el tiempo, la evaluación y la
# infraestructura de la que depende la sustentación.
#
# 📌 **Esto son datos, no una figura, y es deliberado.** Hubo una versión dibujada como rejilla
# de probabilidad por impacto, con los riesgos puestos como códigos R1 a R8 dentro de las
# celdas. El autor la rechazó con razón el 2026-09-03, porque un código dentro de una celda no
# dice qué riesgo es y obliga a buscar la equivalencia en otra parte, de modo que la figura no
# se explicaba sola. Se comprobó además que **FactuGest no tiene ninguna figura de riesgos**,
# sino que los enuncia en prosa. Aquí los riesgos van en una **tabla** del capítulo 4, con su
# probabilidad, su impacto y su respuesta en la misma fila, que es donde el lector los necesita.

# (código, riesgo, probabilidad 1-3, impacto 1-3, respuesta)
RIESGOS = [
    ("R1", "Reprobar de nuevo la sustentación por dejar alguna observación sin atender", 2, 3,
     "Cruzar las quince observaciones contra las tareas y no dar por cerrado el trabajo hasta "
     "que todas queden resueltas."),
    ("R2", "Baja o retiro de uno de los dos integrantes del equipo", 2, 3,
     "Mantener todo en un repositorio compartido y documentado, de modo que cualquiera de los "
     "dos pueda retomar lo del otro."),
    ("R3", "Acumular la documentación para el final y llegar sin tiempo", 3, 3,
     "Generar los entregables desde el principio y por tareas, con un cuaderno de trabajo que "
     "impide arrancar una tarea sin cerrar la anterior."),
    ("R4", "Pérdida del trabajo por no tener respaldo fuera del equipo", 1, 3,
     "Versionar el proyecto y publicarlo en un repositorio remoto."),
    ("R5", "Fallo del entorno local el día de la sustentación", 2, 3,
     "Ensayar el arranque completo desde cero y llevar preparados el volcado de la base y los "
     "datos de demostración."),
    ("R6", "No conseguir un experto del dominio clínico que valide las reglas", 2, 2,
     "Sustituirlo por la entrevista y la observación directa ya realizadas, y dejar declarado "
     "el alcance de esa limitación."),
    ("R7", "Subestimar el esfuerzo del trabajo escrito frente al del software", 3, 2,
     "Automatizar la generación de los documentos, de modo que un cambio en el sistema no "
     "obligue a reescribirlos a mano."),
    ("R8", "Cambio de criterio entre una evaluación y la siguiente", 1, 2,
     "Justificar por escrito cada decisión que se aparta de lo previsto, para poder sostenerla "
     "ante cualquier evaluador."),
]

NIVELES_PROBABILIDAD = {1: "Baja", 2: "Media", 3: "Alta"}
NIVELES_IMPACTO = {1: "Bajo", 2: "Medio", 3: "Alto"}


def riesgos_en_tabla():
    """Los riesgos listos para volcarse en una tabla, con sus niveles ya en palabras."""
    return [[codigo, texto_riesgo, NIVELES_PROBABILIDAD[prob], NIVELES_IMPACTO[imp], respuesta]
            for codigo, texto_riesgo, prob, imp, respuesta in RIESGOS]


# --- 11. Matriz de interesados --------------------------------------------------
# Se espeja la figura de FactuGest, que reparte a los interesados **dentro** de cuatro tarjetas
# rotuladas con la acción que corresponde a cada cuadrante. La primera versión los ponía como
# puntos sueltos sobre una rejilla, y así hay que ir del punto al eje y del eje a la etiqueta
# para saber qué significa cada uno. Con la lista dentro de la tarjeta, el cuadrante ya dice
# qué hacer con quien esté ahí.
# (cuadrante, [interesados])

INTERESADOS = {
    "involucrar": ["Instructora y evaluadores del SENA",
                   "Equipo de desarrollo",
                   "Dirección del centro de salud"],
    "satisfacer": ["Médicos",
                   "Pacientes",
                   "Personal administrativo"],
    "comunicar": ["SENA como institución"],
    "monitorear": ["Experto del dominio clínico",
                   "Proveedor del alojamiento"],
}


def stakeholders():
    """Los interesados repartidos en los cuatro cuadrantes de interés por influencia."""
    figura, ejes = _lienzo(11.0, 7.2)

    tarjetas = [
        (10, 52, "SATISFACER", "Alto interés · Baja influencia", "satisfacer", "#EFE3F5"),
        (54, 52, "INVOLUCRAR", "Alto interés · Alta influencia", "involucrar", "#DFC7EA"),
        (10, 10, "MONITOREAR", "Bajo interés · Baja influencia", "monitorear", "#F7F1FA"),
        (54, 10, "COMUNICAR", "Bajo interés · Alta influencia", "comunicar", "#EFE3F5"),
    ]
    ancho, alto = 38, 38
    for x, y, titulo, subtitulo, clave, color in tarjetas:
        ejes.add_patch(FancyBboxPatch((x, y), ancho, alto,
                                      boxstyle="round,pad=0,rounding_size=1.4",
                                      facecolor=color, edgecolor=MORADO_OSCURO, lw=1.4,
                                      zorder=2))
        ejes.text(x + 3, y + alto - 5, titulo, ha="left", va="center", fontsize=12.5,
                  weight="bold", color=MORADO_OSCURO, zorder=3)
        ejes.text(x + 3, y + alto - 11, subtitulo, ha="left", va="center", fontsize=8.4,
                  color=GRIS, style="italic", zorder=3)
        renglon = y + alto - 18
        for nombre in INTERESADOS[clave]:
            # A 34 caracteres los nombres largos caben de un renglón. A 30 partían en dos y la
            # tercera viñeta de «Involucrar» se salía por debajo de la tarjeta.
            partido = textwrap.wrap(nombre, 34)
            ejes.text(x + 3, renglon, "-  " + partido[0], ha="left", va="top", fontsize=9.4,
                      color=NEGRO, zorder=3)
            for extra in partido[1:]:
                renglon -= 3.4
                ejes.text(x + 5, renglon, extra, ha="left", va="top", fontsize=9.4,
                          color=NEGRO, zorder=3)
            renglon -= 7.0

    ejes.annotate("", xy=(4, 92), xytext=(4, 8),
                  arrowprops=dict(arrowstyle="->", color=NEGRO, lw=1.4))
    ejes.text(1.4, 50, "INTERÉS", rotation=90, ha="center", va="center", fontsize=11,
              weight="bold", color=NEGRO)
    ejes.text(4, 94, "alto", ha="center", va="bottom", fontsize=8.4, color=GRIS)
    ejes.text(4, 6, "bajo", ha="center", va="top", fontsize=8.4, color=GRIS)

    ejes.annotate("", xy=(94, 4), xytext=(10, 4),
                  arrowprops=dict(arrowstyle="->", color=NEGRO, lw=1.4))
    ejes.text(52, 0.5, "INFLUENCIA", ha="center", va="center", fontsize=11, weight="bold",
              color=NEGRO)
    ejes.text(10, 1.4, "baja", ha="left", va="center", fontsize=8.4, color=GRIS)
    ejes.text(94, 1.4, "alta", ha="right", va="center", fontsize=8.4, color=GRIS)

    return _guardar(figura, "FIG-stakeholders.png")


# --- Registro -------------------------------------------------------------------

FIGURAS = {
    "mer": mer,
    "conceptual": conceptual,
    "arquitectura": arquitectura,
    "permisos": permisos,
    "moscow": moscow,
    "scrum": scrum,
    "fisico": fisico,
    "mapa": mapa_navegacion,
    "cronograma": cronograma,
    "stakeholders": stakeholders,
}

# El cronograma, los riesgos y los interesados no salen del repositorio, porque ahí no están.
# Son una **propuesta redactada para que el autor la corrija**, autorizada por él el 2026-09-03,
# y quedan declarados como tales igual que la encuesta de elicitación. El rango de meses del
# cronograma es el mismo con que arrancó FactuGest, por decisión suya.
PROPUESTOS = ["cronograma", "stakeholders"]

# Los riesgos también son propuesta a validar, aunque no sean figura.
DATOS_PROPUESTOS = ["riesgos"]


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(FIGURAS)
    for nombre in pedidas:
        if nombre not in FIGURAS:
            print(f"No existe la figura «{nombre}». Disponibles: {', '.join(FIGURAS)}")
            raise SystemExit(1)
        print(f"  {FIGURAS[nombre]().name}")
    print(f"\n{len(pedidas)} figuras generadas en {SALIDA}")
    print(f"A validar por el autor: {', '.join(PROPUESTOS)} "
          f"y los datos de {', '.join(DATOS_PROPUESTOS)}")
