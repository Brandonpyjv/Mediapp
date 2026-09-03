"""
Dibujante de diagramas de casos de uso.

Se dibujan con matplotlib y no con una herramienta de modelado por una razón
práctica: son once diagramas que van a cambiar cada vez que cambie la lista de
casos de uso, y rehacerlos a mano en cada ajuste termina en diagramas que ya no
coinciden con la documentación que los acompaña. Aquí el diagrama y la ficha salen
de la misma lista.

El trazo sigue la notación UML: los actores como figuras de palotes fuera de la
frontera, los casos de uso como elipses dentro, la frontera como un rectángulo con
el nombre del sistema, la asociación como línea continua y las relaciones de
inclusión y extensión como flechas discontinuas con su estereotipo.
"""
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrow, Rectangle

from paleta import MORADO_OSCURO, RELLENO

# Decisión del autor del 2026-09-03: en los diagramas de casos de uso **el color va solo en los
# óvalos**. La frontera del sistema, los actores, los rótulos y las flechas van en negro, que es
# como se lee un diagrama UML, y el morado se reserva para lo que de verdad distingue, que son
# los casos de uso. El morado de la aplicación sigue mandando en las figuras de datos, como el
# cronograma, el mapa de navegación y los gráficos de barras, que es donde el color informa en
# vez de decorar.
NEGRO = "#000000"

TINTA = NEGRO               # frontera, actores, rótulos del sistema
LINEA = NEGRO               # líneas de asociación
PUNTEADO = NEGRO            # flechas de inclusión y extensión, y sus estereotipos
BORDE_CASO = MORADO_OSCURO  # el borde del óvalo, único trazo en color
TEXTO_CASO = NEGRO          # el nombre del caso, dentro del óvalo

ANCHO_CASO = 2.9
ALTO_CASO = 0.88           # antes 0,78
SEPARACION = 1.10          # entre centros de elipses consecutivas; antes 1,02
ANCHO_TEXTO = 24           # caracteres por renglón dentro del óvalo; antes 20

# Los tres suben juntos y por el mismo motivo. Un caso como «Consultar la historia clínica como
# apoyo a la operación» partía en cuatro renglones a veinte caracteres, y cuatro renglones no
# caben en una elipse de 0,78 de alto: el primero y el último se salían por encima y por debajo
# del borde. Con el trazo azulado de FactuGest apenas se notaba, pero con el óvalo morado sobre
# borde negro queda a la vista. Se ensancha el renglón para que el texto parta en menos líneas
# y se sube el alto de la elipse para que quepan, y la separación acompaña para que dos casos
# seguidos no se toquen. Los valores están ajustados al peor caso real, que a veinticuatro
# caracteres son tres renglones y no cuatro; subirlos más solo alarga el diagrama, y un
# diagrama más alto no cabe junto a su párrafo y se va a la página siguiente dejando media
# página en blanco.

# Altura mínima a la que puede bajar una elipse. La frontera del sistema arranca en 0,45 y la
# elipse mide 0,78 de alto, así que por debajo de este suelo el caso queda medio afuera del
# rectángulo. Se subió de 0,75 a 0,95 al dibujar el diagrama de citas, que es el que más casos
# secundarios tiene y el primero que llegó tan abajo.
SUELO = 0.95


def _texto_caso(texto):
    return "\n".join(textwrap.wrap(texto, ANCHO_TEXTO))


class Diagrama:
    """Un diagrama de casos de uso.

    `casos` es una lista de (nombre, [actores]). Los actores se declaran aparte con
    el lado en que se dibujan, de modo que las líneas no crucen la frontera de un
    lado a otro más de lo necesario.
    """

    def __init__(self, sistema, actores_izq, actores_der, casos, inclusiones=(),
                 extensiones=(), nota=None, modulo=None):
        self.sistema = sistema
        self.modulo = modulo        # segundo renglón del rótulo, con letra menor
        self.actores_izq = actores_izq
        self.actores_der = actores_der
        self.casos = casos
        self.inclusiones = inclusiones      # (caso base, caso incluido)
        self.extensiones = extensiones      # (caso extensión, caso base)
        self.nota = nota

    # -- geometría --

    def _secundarios(self):
        """Casos que existen en función de otro: los incluidos y los que extienden.

        Se dibujan en una segunda columna. Puestos todos en una sola, las flechas de
        inclusión tienen que atravesar las elipses que quedan en medio y el
        estereotipo termina escrito encima del nombre de otro caso.
        """
        return ({incluido for _, incluido in self.inclusiones} |
                {extension for extension, _ in self.extensiones})

    def _posiciones(self):
        """Ubica cada elemento. Devuelve el alto, el ancho y la posición de todo."""
        secundarios = self._secundarios()
        primarios = [n for n, _ in self.casos if n not in secundarios]
        segundos = [n for n, _ in self.casos if n in secundarios]

        dos_columnas = bool(segundos)
        ancho = 14.0 if dos_columnas else 12.0
        col_a, col_b = (5.0, 9.0) if dos_columnas else (6.0, None)
        x_izq, x_der = (1.2, ancho - 1.2)

        # El rótulo ocupa uno o dos renglones, y los casos tienen que arrancar debajo.
        cabecera = 2.45 if self.modulo else 2.0
        alto = max(len(primarios) * SEPARACION + cabecera,
                   len(segundos) * SEPARACION + cabecera,
                   max(len(self.actores_izq), len(self.actores_der), 1) * 1.9 + 1.4)

        casos = {}
        arriba = alto - (2.05 if self.modulo else 1.6)
        for indice, nombre in enumerate(primarios):
            casos[nombre] = (col_a, arriba - indice * SEPARACION)

        # Cada secundario se sitúa frente al caso base con el que se relaciona.
        vinculo = {incluido: base for base, incluido in self.inclusiones}
        vinculo.update({extension: base for extension, base in self.extensiones})
        alturas = [casos.get(vinculo.get(n), (0, alto / 2))[1] for n in segundos]
        for nombre, altura in zip(segundos, self._separar(segundos, alturas, alto)):
            casos[nombre] = (col_b, altura)

        return (alto, ancho, casos,
                self._columna(self.actores_izq, x_izq, casos, alto),
                self._columna(self.actores_der, x_der, casos, alto))

    @staticmethod
    def _separar(elementos, alturas, alto, minima=SEPARACION):
        """Empuja hacia abajo lo que quedó demasiado junto, sin sacarlo de la hoja."""
        alturas = list(alturas)
        orden = sorted(range(len(elementos)), key=lambda i: -alturas[i])
        for posicion in range(1, len(orden)):
            anterior, actual = orden[posicion - 1], orden[posicion]
            if alturas[anterior] - alturas[actual] < minima:
                alturas[actual] = alturas[anterior] - minima
        desborde = SUELO - min(alturas, default=0)
        return [a + desborde for a in alturas] if desborde > 0 else alturas

    def _columna(self, actores, x, casos, alto):
        """Pone a cada actor a la altura de los casos con los que se conecta.

        Repartirlos por igual a lo largo del margen produce diagonales que cruzan
        medio diagrama para llegar a un caso que estaba al frente. Ubicado en el
        centro de sus casos, cada actor queda con líneas cortas y el diagrama se lee
        de un vistazo.
        """
        if not actores:
            return {}

        alturas = []
        for actor in actores:
            suyos = [casos[n][1] for n, conectados in self.casos if actor in conectados]
            alturas.append((sum(suyos) / len(suyos)) if suyos else alto / 2)

        alturas = self._separar(actores, alturas, alto, minima=1.75)
        return {actor: (x, altura) for actor, altura in zip(actores, alturas)}

    # -- piezas --

    @staticmethod
    def _actor(ejes, x, y, nombre):
        """Figura de palotes con el nombre debajo."""
        escala = 0.19
        ejes.add_patch(plt.Circle((x, y + escala * 2.1), escala * 0.72,
                                  fill=False, ec=TINTA, lw=1.4, zorder=3))
        ejes.plot([x, x], [y + escala * 1.35, y - escala * 0.6], color=TINTA, lw=1.4, zorder=3)
        ejes.plot([x - escala, x + escala], [y + escala * 0.85, y + escala * 0.85],
                  color=TINTA, lw=1.4, zorder=3)
        ejes.plot([x - escala * 0.85, x, x + escala * 0.85],
                  [y - escala * 1.9, y - escala * 0.6, y - escala * 1.9],
                  color=TINTA, lw=1.4, zorder=3)
        ejes.text(x, y - escala * 2.7, "\n".join(textwrap.wrap(nombre, 14)),
                  ha="center", va="top", fontsize=8.5, color=TINTA, weight="bold")

    @staticmethod
    def _caso(ejes, x, y, nombre):
        ejes.add_patch(Ellipse((x, y), ANCHO_CASO, ALTO_CASO, facecolor=RELLENO,
                               edgecolor=BORDE_CASO, lw=1.4, zorder=2))
        ejes.text(x, y, _texto_caso(nombre), ha="center", va="center",
                  fontsize=7.4, color=TEXTO_CASO, zorder=4)

    @staticmethod
    def _borde_elipse(centro, hacia):
        """Punto donde la recta hacia `hacia` corta el borde de la elipse.

        Sin esto, las flechas de inclusión salen del centro de una elipse y llegan al
        centro de la otra: el trazo queda tapado por el relleno y el estereotipo se
        lee encima del texto del caso.
        """
        dx, dy = hacia[0] - centro[0], hacia[1] - centro[1]
        if dx == 0 and dy == 0:
            return centro
        a, b = ANCHO_CASO / 2, ALTO_CASO / 2
        factor = 1.0 / ((dx / a) ** 2 + (dy / b) ** 2) ** 0.5
        return centro[0] + dx * factor, centro[1] + dy * factor

    @staticmethod
    def _asociacion(ejes, origen, destino):
        ejes.plot([origen[0], destino[0]], [origen[1], destino[1]],
                  color=LINEA, lw=0.9, zorder=1)

    @staticmethod
    def _estereotipo(ejes, desde, hasta, etiqueta):
        # Se dibuja como línea discontinua con punta abierta, que es la notación de la
        # dependencia en UML. Antes era un `FancyArrow`, que es un polígono relleno con el
        # trazo discontinuo solo en el borde: en el azul claro de FactuGest el relleno apenas
        # se veía y la flecha parecía punteada, pero en negro el relleno manda y varias
        # flechas salían continuas. `annotate` traza la línea de verdad, así que la
        # discontinuidad no depende de que el relleno no se note.
        ejes.annotate("", xy=hasta, xytext=desde, zorder=1,
                      arrowprops=dict(arrowstyle="->", color=PUNTEADO, lw=0.9,
                                      linestyle="--", shrinkA=0, shrinkB=0,
                                      mutation_scale=11))
        # Sobre fondo blanco: entre dos elipses seguidas el hueco es de milímetros y
        # el estereotipo quedaría escrito encima del borde de una de las dos.
        ejes.text((desde[0] + hasta[0]) / 2, (desde[1] + hasta[1]) / 2,
                  etiqueta, ha="center", va="center", fontsize=6.6,
                  color=PUNTEADO, style="italic", zorder=5,
                  bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    # -- dibujo --

    def dibujar(self, destino, ancho_pulgadas=8.6):
        # 8,6 y no las 11 pulgadas de FactuGest. El tamaño del lienzo no cambia el trazo,
        # porque la geometría va en coordenadas de datos, pero sí el tamaño relativo de la
        # letra, que se declara en puntos. Insertada en la página, la figura se reduce a las
        # 6,5 pulgadas útiles, de modo que un rótulo de 7,4 puntos dibujado sobre un lienzo de
        # 11 pulgadas se imprime a 4,4 y deja de leerse. Sobre 8,6 llega a 5,6, que es tamaño
        # de rótulo de figura. Se mantiene el margen de sobra para que el texto siga cabiendo
        # dentro de la elipse.
        alto, ancho, casos, izq, der = self._posiciones()
        figura, ejes = plt.subplots(figsize=(ancho_pulgadas, ancho_pulgadas * alto / ancho))
        ejes.set_xlim(0, ancho)
        ejes.set_ylim(0, alto)
        ejes.axis("off")

        # frontera del sistema
        margen_frontera = 2.6 if ancho > 12 else 3.0
        ejes.add_patch(Rectangle((margen_frontera, 0.45), ancho - 2 * margen_frontera,
                                 alto - 1.05, fill=False, edgecolor=TINTA, lw=1.3, zorder=1))
        ejes.text(ancho / 2, alto - 0.95, self.sistema, ha="center", va="center",
                  fontsize=10.5, color=TINTA, weight="bold")
        if self.modulo:
            ejes.text(ancho / 2, alto - 1.32, self.modulo, ha="center", va="center",
                      fontsize=8.6, color=TINTA)

        posicion_actor = {**izq, **der}
        for nombre, (x, y) in posicion_actor.items():
            self._actor(ejes, x, y, nombre)

        for nombre, _ in self.casos:
            x, y = casos[nombre]
            self._caso(ejes, x, y, nombre)

        for nombre, actores in self.casos:
            elipse = casos[nombre]
            for actor in actores:
                if actor not in posicion_actor:
                    raise ValueError(f"El actor «{actor}» no está declarado en el diagrama")
                origen = posicion_actor[actor]
                lado = -1 if origen[0] < elipse[0] else 1
                arranque = (origen[0] + (-lado) * 0.28, origen[1])
                self._asociacion(ejes, arranque, self._borde_elipse(elipse, arranque))

        for base, incluido in self.inclusiones:
            self._estereotipo(ejes,
                              self._borde_elipse(casos[base], casos[incluido]),
                              self._borde_elipse(casos[incluido], casos[base]),
                              "«include»")
        for extension, base in self.extensiones:
            self._estereotipo(ejes,
                              self._borde_elipse(casos[extension], casos[base]),
                              self._borde_elipse(casos[base], casos[extension]),
                              "«extend»")

        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        figura.savefig(destino, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(figura)
        return destino
