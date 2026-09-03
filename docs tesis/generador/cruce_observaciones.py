# -*- coding: utf-8 -*-
"""
Cruza las 15 observaciones del evaluador contra los entregables ya generados.

    python cruce_observaciones.py        # 0 si pasan todas

Es el criterio de aceptación del §4 del cuaderno, ejecutable. No comprueba que un
apartado esté «bien redactado», sino que **exista de verdad en el archivo
producido** lo que el cuaderno declara como responsable de esa observación.

**Por qué existe.** La tabla del §4 se llevaba a mano, y una casilla marcada no
demuestra nada después de regenerar los documentos: basta con que un capítulo
cambie de sitio un apartado para que una observación quede sin atender sin que
nadie lo note hasta la sustentación. Aquí cada fila es una comprobación sobre el
`.docx`, así que volver a correrlo tras cualquier cambio dice si alguna se rompió.

**Lo que no puede comprobar.** O02, la paginación del índice, no se ve desde
python-docx porque el campo TOC está vacío hasta que Word abre el archivo; aquí
solo se comprueba que el índice exista, y la paginación se mira en el PDF que
produce `revisar.a_pdf()`.
"""
import re
import sys
from pathlib import Path

from docx import Document

BASE = Path(r"D:\01. Proyectos\Mediapp\docs tesis\entregables")
E1 = BASE / "MediApp - Requisitos Funcionales y No Funcionales.docx"
E2 = BASE / "MediApp - Diagramas de Casos de Uso.docx"
E3 = BASE / "MediApp - Documentacion de Casos de Uso.docx"
E4 = BASE / "MediApp - Documento de Grado.docx"
E5 = BASE / "MediApp - Diccionario de Datos.docx"


def texto(ruta):
    d = Document(str(ruta))
    partes = [p.text for p in d.paragraphs]
    for t in d.tables:
        for fila in t.rows:
            for celda in fila.cells:
                partes.append(celda.text)
    return "\n".join(partes)


def imagenes(ruta):
    d = Document(str(ruta))
    return [r.target_part.partname for r in d.part.rels.values()
            if "image" in r.reltype]


CACHE = {}
def T(ruta):
    if ruta not in CACHE:
        CACHE[ruta] = texto(ruta)
    return CACHE[ruta]


def tiene(ruta, *patrones):
    t = T(ruta)
    return all(re.search(p, t, re.I | re.S) for p in patrones)


PRUEBAS = [
    ("O01", "Sin texto amarillo de observaciones",
     lambda: "quitar este texto" not in T(E4).lower(), "E4 generado desde cero"),

    ("O02", "Tabla de contenido con paginación",
     lambda: tiene(E4, r"Tabla de contenido|Contenido"), "E4, campo TOC de Word"),

    ("O03", "Título con la estructura de tres partes",
     lambda: tiene(E4, r"MediApp.{0,80}agendamiento de citas m[eé]dicas.{0,200}"
                       r"optimizaci[oó]n de la atenci[oó]n"), "E4, cubierta y portada"),

    ("O04", "El modelo MoSCoW aparece",
     lambda: tiene(E4, r"MoSCoW") and tiene(E1, r"MoSCoW", r"Must", r"Should",
                                            r"Could", r"Won.t"), "E4 4.6 y E1"),

    ("O05", "Casos de uso ordenados, con médico y paciente",
     lambda: tiene(E2, r"M[eé]dico", r"Paciente", r"Administrador"), "E2 y E3"),

    ("O06", "Hay mockups (capturas reales)",
     lambda: tiene(E4, r"interfaz|interfaces|pantalla") and len(imagenes(E4)) >= 30,
     "E4 5.6, capturas de la aplicación"),

    ("O07", "Pruebas, su tipo y sus pantallazos",
     lambda: tiene(E4, r"pytest", r"91\s*pruebas|91 pruebas"), "E4 6.7 y 6.8"),

    ("O08", "Objetivos específicos del software",
     lambda: tiene(E4, r"Objetivos espec[ií]ficos",
                   r"Facilitar la programaci[oó]n de la atenci[oó]n m[eé]dica",
                   r"Habilitar la gesti[oó]n del acto cl[ií]nico",
                   r"Garantizar la confidencialidad"), "E4 1.6"),

    ("O09", "Riesgos del proyecto, no del software",
     lambda: tiene(E4, r"Gesti[oó]n de riesgos del proyecto",
                   r"No se incluyen aqu[ií] los riesgos t[eé]cnicos del sistema"),
     "E4 4.7"),

    ("O10", "El Gantt del documento es el de la diapositiva",
     lambda: (BASE / "diagramas" / "FIG-cronograma.png").exists()
             and tiene(E4, r"Cronograma"), "E4 4.3 y la diapositiva, misma figura"),

    ("O11", "Casos de uso de pacientes y médicos",
     lambda: tiene(E3, r"M[eé]dico") and tiene(E3, r"Paciente"), "E3 y E2"),

    ("O12", "Sin código SQL en los casos de uso",
     lambda: not re.search(r"\b(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|"
                           r"CREATE\s+TABLE|ALTER\s+TABLE|JOIN|WHERE)\b",
                           T(E3) + T(E2), re.I), "E3 y E2, comprobado por verificar.py"),

    ("O13", "Mapa de navegación ajustado",
     lambda: (BASE / "diagramas" / "FIG-mapa-navegacion.png").exists()
             and tiene(E4, r"[Mm]apa de navegaci[oó]n"), "E4, FIG-mapa-navegacion"),

    ("O14", "Modelo relacional generado desde MySQL",
     lambda: (BASE / "diagramas" / "FIG-fisico.png").exists()
             and tiene(E4, r"[Mm]odelo f[ií]sico"), "E4 5.10"),

    ("O15", "Mockups ajustados a las interfaces reales",
     lambda: tiene(E4, r"MediApp") and len(imagenes(E4)) >= 30,
     "E4 5.6, capturas con datos del sembrado"),

    ("--", "Autores, ficha e instructora en la portada",
     lambda: tiene(E4, r"HERN[AÁ]NDEZ AR[EÉ]VALO", r"QUI[NÑ]ONES",
                   r"3115426", r"Adarme"), "E4, cubierta y portada"),

    ("--", "Trazabilidad caso de uso -> las 11 tablas",
     lambda: tiene(E3, r"Tablas que toca") and tiene(E5, r"11|once"),
     "E4 5.2.2 y E3"),

    ("--", "Fallo del historial clínico corregido, con evidencia",
     lambda: tiene(E4, r"historia cl[ií]nica") and tiene(E4, r"pytest"),
     "E4 6.8"),
]


def main():
    ancho = max(len(d) for _, d, _, _ in PRUEBAS)
    fallos = 0
    for codigo, descripcion, prueba, donde in PRUEBAS:
        try:
            ok = bool(prueba())
        except Exception as e:
            ok = False
            donde += f"  <error: {type(e).__name__}>"
        marca = "OK  " if ok else "FALLA"
        if not ok:
            fallos += 1
        print(f"{codigo:4} {marca}  {descripcion:<{ancho}}  {donde}")
    print(f"\n{len(PRUEBAS) - fallos} de {len(PRUEBAS)} resueltas")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
