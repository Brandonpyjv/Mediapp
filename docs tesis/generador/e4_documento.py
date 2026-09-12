# -*- coding: utf-8 -*-
"""
E4 — Documento de grado de MediApp. Ensamblador.

Cada capítulo vive en su propio módulo y expone una función `escribir(d)` que recibe el
documento y le agrega su parte. Aquí solo se declara el orden.

**Por qué así.** El documento se escribe en sesiones distintas, una por capítulo. Con todo en un
archivo, cada sesión tendría que releer y reescribir el conjunto, y el riesgo no es el trabajo
perdido sino el capítulo que queda a medias. Separado, una sesión toca un archivo y el ensamble
es esta lista. Los contadores de tablas y de figuras corren solos de un capítulo al siguiente
porque el documento es uno solo.

**El ensamblador funciona desde el primer capítulo.** `CAPITULOS` declara el orden completo del
documento, incluidos los módulos que todavía no existen, y el ensamble salta los que faltan
avisando cuáles son. Así se puede generar y revisar el documento en cada sesión en vez de tener
que esperar a que estén los diez, que es cuando un error de formato costaría diez correcciones
en lugar de una.

    python e4_documento.py
"""
import importlib
from pathlib import Path

from apa import DocumentoAPA

SALIDA = Path(__file__).resolve().parent.parent / "entregables"
ARCHIVO = SALIDA / "MediApp - Documento de Grado.docx"

# El orden de esta lista es el orden del documento. (módulo, qué trae, tarea que lo escribe)
CAPITULOS = [
    ("e4_preliminares", "Cubierta, portada, tabla de contenido, resumen, abstract e "
                        "introducción", "T8"),
    ("e4_cap1", "Planteamiento del problema y formulación del proyecto", "T9"),
    ("e4_cap2", "Marco referencial del proyecto", "T10"),
    ("e4_cap3", "Metodología de investigación y desarrollo", "T11"),
    ("e4_cap4", "Análisis y especificación de requisitos", "T12"),
    ("e4_cap5a", "Diseño de la solución, actores y casos de uso", "T13"),
    ("e4_cap5b", "Diseño de la base de datos y modelo físico", "T14"),
    ("e4_cap6a", "Desarrollo, estructura y módulos del sistema", "T15"),
    ("e4_cap6b", "Integración, pruebas y resultados", "T16"),
    ("e4_cierre", "Conclusiones, referencias y anexos", "T17"),
]

# Mientras un módulo siga siendo la copia de FactuGest, escribiría un capítulo de facturación
# electrónica dentro del documento de MediApp. Por eso no basta con que el archivo exista, y
# cada capítulo tiene que declararse listo poniendo esta marca a `True` en su propio módulo.
MARCA = "ADAPTADO_A_MEDIAPP"


def _disponibles():
    """Los capítulos ya escritos contra MediApp, y los que todavía no."""
    listos, pendientes = [], []
    for nombre, descripcion, tarea in CAPITULOS:
        try:
            modulo = importlib.import_module(nombre)
        except ModuleNotFoundError:
            pendientes.append((nombre, descripcion, tarea, "no existe"))
            continue
        except Exception as error:
            # Una copia de FactuGest sin adaptar puede ni siquiera importarse, porque busca
            # cosas que aquí se llaman de otra forma. Eso también es estar pendiente, y no
            # tiene por qué impedir generar el documento con los capítulos que sí están.
            pendientes.append((nombre, descripcion, tarea,
                               f"no importa todavía, {type(error).__name__}"))
            continue
        if not getattr(modulo, MARCA, False):
            pendientes.append((nombre, descripcion, tarea, "todavía es la copia de FactuGest"))
            continue
        listos.append((nombre, modulo))
    return listos, pendientes


def construir():
    listos, pendientes = _disponibles()
    d = DocumentoAPA()
    for _nombre, modulo in listos:
        modulo.escribir(d)
    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d, listos, pendientes


if __name__ == "__main__":
    documento, listos, pendientes = construir()
    print(f"Generado: {ARCHIVO}")
    print(f"Capitulos escritos: {len(listos)} de {len(CAPITULOS)}")
    for nombre, _modulo in listos:
        print(f"   [x] {nombre}")
    for nombre, descripcion, tarea, motivo in pendientes:
        print(f"   [ ] {nombre:18} {tarea:4} {descripcion} ({motivo})")
    print(f"Tablas: {documento.n_tabla}  Figuras: {documento.n_figura}")
