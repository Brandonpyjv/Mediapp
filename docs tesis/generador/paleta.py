# -*- coding: utf-8 -*-
"""
Paleta de color de los gráficos de MediApp, **definición única**.

Decisión del autor del 2026-09-02. Donde los generadores de FactuGest usan azul, MediApp usa el
**morado de las tarjetas de acciones rápidas del panel**, que es `#9B59B6`, con `#8E44AD` para
los tonos oscuros. Sale de `templates/static/css/main.css` (la clase `.quick-purple`), de manera
que el documento y la aplicación se vean del mismo proyecto y no de dos.

De aquí lo leen `uml.py` (T5), `figuras.py` (T7) y `ppt.py` (P0). **Ningún generador vuelve a
escribir un color a mano**, porque el día que el autor cambie el morado habría que ir a
buscarlo a catorce archivos y siempre quedaría uno sin cambiar.

El cuaderno anunciaba esta constante dentro de `figuras.py`, pero `uml.py` la necesita en T5 y
`figuras.py` no existe hasta T7, así que vive en su propio módulo y los tres la importan. Es la
misma decisión, en un archivo que no obliga a T5 a depender de T7.
"""

# --- Los dos colores de la aplicación -------------------------------------------

MORADO = "#9B59B6"          # `.quick-purple i`, el color de la tarjeta
MORADO_OSCURO = "#8E44AD"   # el extremo oscuro de su degradado

# --- Tonos derivados, para rellenos y fondos ------------------------------------
# El morado puro sirve para una barra, pero detrás de un texto de 8 puntos le quita
# contraste. Para rellenar se aclara mucho, conservando el mismo tono.

RELLENO = "#EFE3F5"         # relleno de los óvalos de los casos de uso y de las cajas
FONDO_SUAVE = "#F7F1FA"     # fondos de zona en las figuras de T7
TINTA = "#4A235A"           # morado oscurecido, para texto sobre relleno claro

# 🔴 **Dónde NO va el morado.** En los diagramas de casos de uso el color se limita al óvalo.
# La frontera del sistema, los actores, los rótulos y las flechas van en negro, porque en un
# diagrama UML el trazo es notación y no decoración, y teñirlo entero hace que el color deje
# de señalar nada (decisión del autor, 2026-09-03). `uml.py` define su propio negro y solo
# toma de aquí el borde y el relleno del óvalo. El morado manda, en cambio, en las figuras que
# presentan datos, que son el cronograma, el mapa de navegación, la matriz de permisos, la
# priorización MoSCoW y cualquier gráfico de barras.

# --- Serie para las figuras con varias categorías (T7 y las diapositivas) -------
# Ordenada de más a menos saturada, de modo que la primera categoría de cualquier
# gráfico sea siempre la morada de la aplicación.

SERIE = [MORADO, MORADO_OSCURO, "#B98BD0", "#6C3483", "#D2B4DE", "#7D3C98"]

# Grises de apoyo, para lo que no debe competir con el morado.
GRIS = "#7F8C8D"
GRIS_CLARO = "#D5D8DC"


def serie(n):
    """Los primeros `n` colores de la serie, repitiéndola si hiciera falta."""
    return [SERIE[i % len(SERIE)] for i in range(n)]
