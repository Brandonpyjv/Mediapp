# -*- coding: utf-8 -*-
"""
Encuesta de elicitación de MediApp: instrumento, datos y figuras.

Los datos viven aquí y en ningún otro lugar. El capítulo 3 toma de este módulo tanto las
gráficas como las cifras que menciona en el texto, de modo que el tamaño de la muestra y los
porcentajes no puedan discrepar entre una sección y otra, porque una cifra que cambia entre el
análisis y la gráfica es lo primero que delata un dato mal llevado.

**A quién se preguntó y por qué.** FactuGest encuestó empresas obligadas a facturar, porque su
problema era por qué no lo hacían. El de MediApp es otro y por eso el instrumento también lo es.
Aquí se pregunta a personas que solicitan atención en centros de salud cómo consiguen hoy una
cita, cuánto les cuesta conseguirla y qué esperarían de un sistema que las atienda, que es lo
que decide si el proyecto tiene que ordenar una agenda o construir otra cosa.

**Sobre el color.** Cada gráfica presenta una sola distribución, así que el color no codifica
identidad. Hay un tono de acento para la barra que sostiene el hallazgo y uno recesivo para el
resto, los dos tomados de `paleta.py`, que es la definición única del morado de la aplicación.
La identidad de cada barra la lleva su rótulo, no su color.

    python encuesta.py
"""
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from paleta import MORADO, MORADO_OSCURO, TINTA, GRIS, GRIS_CLARO

SALIDA = Path(__file__).resolve().parent.parent / "entregables" / "diagramas"

ACENTO = MORADO
RECESIVO = "#D2B4DE"        # el morado muy aclarado de la serie, para lo que no destaca
SECUNDARIA = GRIS
LINEA = GRIS_CLARO

MUESTRA = 48          # personas encuestadas. Cámbiese aquí y en ningún otro sitio.

# (pregunta abreviada, [(opción, respuestas)], índice de la barra destacada)
RESULTADOS = [
    ("¿De qué manera solicita hoy una cita médica?",
     [("Presencialmente en el centro", 26), ("Por teléfono", 14),
      ("Por mensajería instantánea", 6), ("Por una página o aplicación", 2)], 0),

    ("¿Cuánto tiempo le toma que le asignen la cita?",
     [("Menos de 10 minutos", 5), ("De 10 a 30 minutos", 12),
      ("De 30 minutos a una hora", 16), ("Más de una hora", 15)], 2),

    ("¿Le han asignado una cita cruzada con otro paciente?",
     [("Nunca", 19), ("Una vez", 16), ("Varias veces", 13)], 2),

    ("¿Se ha desplazado solo para pedir o cancelar una cita?",
     [("Sí", 34), ("No", 14)], 0),

    ("¿Le gustaría elegir usted mismo el horario libre?",
     [("Sí", 41), ("Tal vez", 5), ("No", 2)], 0),

    ("¿Prefiere que la cita quede agendada de inmediato?",
     [("Agendada de inmediato", 39), ("Pendiente de aprobación", 5),
      ("Me es indiferente", 4)], 0),
]

# Preguntas que no van a la gráfica pero sí se citan en el análisis.
MOMENTO = [("Solo en el horario de atención del centro", 38), ("A cualquier hora", 10)]
CANCELACION = [("Sí, sin ir al centro", 9), ("No, tuve que ir", 22),
               ("No he necesitado cancelar", 17)]
HISTORIAL = [("Sí", 40), ("Tal vez", 6), ("No", 2)]
PREOCUPACION = [("Sí", 29), ("No lo había pensado", 12), ("No", 7)]

SOLO_EN_HORARIO = 38        # solo pueden solicitar dentro del horario de atención
TUVO_QUE_IR = 22            # tuvieron que desplazarse para cancelar
HISTORIAL_SI = 40           # consultarían en línea su historial y sus fórmulas
CONFIDENCIALIDAD_ALTA = 43  # calificaron con 4 o 5 que solo el médico escriba
PREOCUPA_NO_MEDICO = 29     # les preocupa que personal no médico acceda a la historia
CON_DISPOSITIVO = 45        # disponen de teléfono o computador con internet


def porcentaje(cantidad):
    return round(cantidad * 100 / MUESTRA)


def _barras(ejes, titulo, opciones, destacada):
    etiquetas = [o for o, _ in opciones]
    valores = [v for _, v in opciones]
    posiciones = range(len(valores))

    for posicion, valor in zip(posiciones, valores):
        color = ACENTO if posicion == destacada else RECESIVO
        # Extremo redondeado y anclado en el cero, como marca la guía de marcas.
        ejes.add_patch(FancyBboxPatch(
            (0, posicion - 0.28), max(valor, 0.35), 0.56,
            boxstyle="round,pad=0,rounding_size=0.55",
            facecolor=color, edgecolor="white", linewidth=1.2, zorder=2,
            mutation_aspect=0.12))
        ejes.text(valor + max(valores) * 0.035, posicion,
                  f"{valor}  ({porcentaje(valor)} %)", va="center", ha="left",
                  fontsize=7.6, color=TINTA, zorder=3)

    ejes.set_yticks(list(posiciones))
    ejes.set_yticklabels(["\n".join(textwrap.wrap(e, 18)) for e in etiquetas], fontsize=7.6,
                         color=TINTA)
    # Aire arriba para que el título no quede pegado a la primera barra.
    ejes.set_ylim(len(valores) - 0.5, -0.95)
    ejes.set_xlim(0, max(valores) * 1.34)
    ejes.set_xticks([])
    for lado in ("top", "right", "bottom"):
        ejes.spines[lado].set_visible(False)
    ejes.spines["left"].set_color(LINEA)
    ejes.tick_params(axis="y", length=0)
    ejes.set_title("\n".join(textwrap.wrap(titulo, 44)), fontsize=8.6, color=TINTA,
                   loc="left", pad=8, weight="bold")


def grafica_resultados(destino=None):
    """Las seis distribuciones que sostienen el diagnóstico, en un solo panel."""
    destino = destino or SALIDA / "FIG-encuesta-resultados.png"
    # Cada fila se alta en proporción a cuántas opciones tiene, porque con altura igual los
    # paneles de dos o tres respuestas quedan con la mitad del cuadro en blanco y sus barras se
    # leen como si midieran más que las de al lado.
    alturas = [max(len(RESULTADOS[fila * 2][1]), len(RESULTADOS[fila * 2 + 1][1]))
               for fila in range(3)]
    figura, ejes = plt.subplots(3, 2, figsize=(11, 8.6),
                                gridspec_kw={"height_ratios": alturas})
    for cuadro, (titulo, opciones, destacada) in zip(ejes.flat, RESULTADOS):
        _barras(cuadro, titulo, opciones, destacada)
    figura.suptitle(f"Resultados de la encuesta aplicada a {MUESTRA} personas",
                    fontsize=11, color=TINTA, weight="bold", y=0.985)
    figura.tight_layout(rect=(0, 0, 1, 0.965), h_pad=3.2, w_pad=4.0)

    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return destino


PREGUNTAS_FORMULARIO = [
    ("1. ¿De qué manera solicita usted una cita médica actualmente?",
     ["Presencialmente en el centro", "Por teléfono", "Por mensajería instantánea",
      "Por una página web o aplicación"], 0),
    ("2. Desde que la solicita, ¿cuánto tiempo le toma que le asignen la cita?",
     ["Menos de 10 minutos", "De 10 a 30 minutos", "De 30 minutos a una hora",
      "Más de una hora"], 2),
    ("4. ¿Le ha ocurrido que la cita asignada se cruce con la de otro paciente?",
     ["Nunca", "Una vez", "Varias veces"], 2),
    ("5. ¿Ha tenido que desplazarse al centro solo para pedir o cancelar una cita?",
     ["Sí", "No"], 0),
    ("7. ¿Le gustaría ver los horarios libres del médico y elegir usted mismo?",
     ["Sí", "No", "Tal vez"], 0),
    ("8. ¿Preferiría que la cita quedara agendada de inmediato o pendiente de aprobación?",
     ["Agendada de inmediato", "Pendiente de aprobación", "Me es indiferente"], 0),
]

ANCHO_ENUNCIADO = 62
ALTO_LINEA = 0.40
AIRE_ENUNCIADO = 0.14   # entre el enunciado y su primera opción
ALTO_OPCION = 0.42
ALTO_SEPARADOR = 0.52


def _alto_formulario():
    """Cuánto mide el formulario, en unidades del lienzo.

    Se calcula en vez de fijarse, porque con un alto fijo agregar una pregunta o alargar un
    enunciado empuja las últimas preguntas fuera del lienzo, y lo que se recorta no avisa, ya
    que queda un formulario en el que las dos últimas preguntas aparecen sin sus opciones.
    """
    alto = 1.9                              # encabezado
    for enunciado, opciones, _ in PREGUNTAS_FORMULARIO:
        alto += ALTO_LINEA * len(textwrap.wrap(enunciado, ANCHO_ENUNCIADO)) + AIRE_ENUNCIADO
        alto += ALTO_OPCION * len(opciones) + ALTO_SEPARADOR
    return alto + 0.9                       # pie


def formulario(destino=None):
    """Representación del formulario digital con el que se aplicó el instrumento."""
    destino = destino or SALIDA / "FIG-encuesta-formulario.png"
    alto = _alto_formulario()
    figura, ejes = plt.subplots(figsize=(7.6, 7.6 * alto / 10.0))
    ejes.set_xlim(0, 10)
    ejes.set_ylim(0, alto)
    ejes.axis("off")

    ejes.add_patch(FancyBboxPatch((0.3, alto - 1.55), 9.4, 1.3,
                                  boxstyle="round,pad=0.02,rounding_size=0.1",
                                  facecolor=MORADO_OSCURO, edgecolor="none"))
    ejes.text(0.75, alto - 0.68, "MediApp. Diagnóstico de la solicitud de citas médicas",
              fontsize=11, color="white", weight="bold", va="center")
    ejes.text(0.75, alto - 1.18,
              "Encuesta dirigida a usuarios de centros de salud. Cúcuta, 2025",
              fontsize=8.2, color="#E8D9F0", va="center")

    y = alto - 2.0
    for enunciado, opciones, marcada in PREGUNTAS_FORMULARIO:
        lineas = textwrap.wrap(enunciado, ANCHO_ENUNCIADO)
        ejes.text(0.55, y, "\n".join(lineas), fontsize=8.6, color=TINTA, va="top",
                  weight="bold")
        y -= ALTO_LINEA * len(lineas) + AIRE_ENUNCIADO
        for indice, opcion in enumerate(opciones):
            elegido = indice == marcada
            ejes.add_patch(plt.Circle((0.85, y + 0.06), 0.11, facecolor="white",
                                      edgecolor=ACENTO if elegido else "#C9B6D6",
                                      linewidth=1.4, zorder=2))
            if elegido:
                ejes.add_patch(plt.Circle((0.85, y + 0.06), 0.055, facecolor=ACENTO,
                                          edgecolor="none", zorder=3))
            ejes.text(1.15, y + 0.06, opcion, fontsize=8.2, va="center",
                      color=TINTA if elegido else SECUNDARIA)
            y -= ALTO_OPCION
        y -= ALTO_SEPARADOR - 0.16
        ejes.plot([0.55, 9.45], [y, y], color=LINEA, linewidth=0.9)
        y -= 0.16

    ejes.text(0.55, 0.35,
              f"Respuestas recibidas: {MUESTRA}.    Preguntas 3, 6 y 9 a 12 en la página "
              "siguiente del formulario",
              fontsize=7.8, color=SECUNDARIA, style="italic")

    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return destino


def grafica_contraste(destino=None):
    """Las preguntas 7 y 8, una al lado de la otra.

    Es el hallazgo que sostiene la decisión de que el paciente agende su propia cita y de que
    quede agendada de inmediato, y en la sustentación se muestra solo, sin las otras cuatro
    gráficas. El panel completo del documento tiene seis distribuciones y proyectado no se
    distingue cuál es la que importa.
    """
    destino = destino or SALIDA / "FIG-encuesta-contraste.png"
    # Muy apaisada a propósito, para que en la diapositiva pueda ocupar todo el ancho
    # disponible sin que el alto la obligue a encogerse.
    figura, ejes = plt.subplots(1, 2, figsize=(12, 2.95))
    for cuadro, (titulo, opciones, destacada) in zip(ejes, RESULTADOS[4:6]):
        _barras(cuadro, titulo, opciones, destacada)
        cuadro.title.set_fontsize(11)
        for etiqueta in cuadro.get_yticklabels():
            etiqueta.set_fontsize(9.5)
    figura.tight_layout(w_pad=5.0)
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return destino


def comprobar():
    """Que ninguna distribución sume distinto de la muestra.

    Es la comprobación que de verdad hace falta aquí, porque un dato de más en una opción no se
    ve en la gráfica sino en el análisis, y para entonces ya está escrito en el texto.
    """
    faltas = []
    distribuciones = [(t, o) for t, o, _ in RESULTADOS]
    distribuciones += [("Momento de la solicitud", MOMENTO),
                       ("Cancelación", CANCELACION),
                       ("Consulta del historial", HISTORIAL),
                       ("Preocupación por el acceso", PREOCUPACION)]
    for titulo, opciones in distribuciones:
        total = sum(v for _, v in opciones)
        if total != MUESTRA:
            faltas.append(f"«{titulo}» suma {total} y la muestra es {MUESTRA}")
    for nombre, valor in [("SOLO_EN_HORARIO", SOLO_EN_HORARIO),
                          ("TUVO_QUE_IR", TUVO_QUE_IR),
                          ("HISTORIAL_SI", HISTORIAL_SI),
                          ("CONFIDENCIALIDAD_ALTA", CONFIDENCIALIDAD_ALTA),
                          ("PREOCUPA_NO_MEDICO", PREOCUPA_NO_MEDICO),
                          ("CON_DISPOSITIVO", CON_DISPOSITIVO)]:
        if not 0 <= valor <= MUESTRA:
            faltas.append(f"{nombre} vale {valor} y la muestra es {MUESTRA}")
    return faltas


if __name__ == "__main__":
    problemas = comprobar()
    for problema in problemas:
        print(f"   FALTA {problema}")
    print(f"Comprobacion de los datos: {len(problemas)} faltas")
    for ruta in (formulario(), grafica_resultados(), grafica_contraste()):
        print(f"Generado: {ruta}")
