# -*- coding: utf-8 -*-
"""Integridad de los datos: el bug del Ítem 11, las bajas lógicas, los duplicados
y el aislamiento entre pacientes.

El primer bloque es una regresión del fallo que reprobó la sustentación anterior,
así que si alguna de esas cinco vuelve a fallar, vuelve a fallar la sustentación.
"""
from datetime import timedelta

import pytest

import date_validators as dv

INEXISTENTE = 999999


@pytest.fixture
def clinica(app, datos, entrar):
    datos.usuario("ana.admin", "admin")
    id_medico, _ = datos.medico(nombre="Ana Torres", username="ana.torres")
    id_paciente, id_usuario_paciente = datos.paciente(nombre="Luis Pardo", username="luis.pardo")
    otro_paciente, _ = datos.paciente(nombre="Sara Gil", username="sara.gil")
    return {
        "admin": entrar("ana.admin", rol="admin"),
        "medico": entrar("ana.torres", rol="medico"),
        "paciente": entrar("luis.pardo", rol="paciente"),
        "otro_cliente": entrar("sara.gil", rol="paciente"),
        "id_medico": id_medico,
        "id_paciente": id_paciente,
        "otro_paciente": otro_paciente,
        "id_usuario_paciente": id_usuario_paciente,
    }


# --- Ítem 11: un error de base de datos no puede tumbar la pantalla ----------
#
# La causa real no era el esquema. En `addHI`, cuando el INSERT fallaba, el
# `except` avisaba pero no salía de la función, así que la ejecución seguía y
# reutilizaba un cursor ya cerrado: el usuario veía un error 500 con la traza
# completa, y encima de un fallo que no tenía nada que ver con el suyo. El mismo
# código copiado estaba en cuatro rutas más.

def test_crear_una_historia_con_un_paciente_inexistente_no_tumba_la_pantalla(clinica, datos):
    respuesta = clinica["medico"].post("/addHI", data={
        "id_paciente": INEXISTENTE, "fecha": "2026-09-01",
        "descripcion": "prueba", "notas": "",
    }, follow_redirects=True)
    assert respuesta.status_code == 200, "la pantalla respondió con un error del servidor"
    assert datos.contar("historia") == 0


def test_crear_un_examen_con_un_paciente_inexistente_no_tumba_la_pantalla(clinica, datos):
    respuesta = clinica["medico"].post("/addEX", data={
        "id_paciente": INEXISTENTE, "tipo_examen": "Hemograma",
        "fecha_solicitud": "2026-09-01",
    }, follow_redirects=True)
    assert respuesta.status_code == 200
    assert datos.contar("examen") == 0


def test_crear_una_receta_con_un_medicamento_inexistente_no_tumba_la_pantalla(clinica, datos):
    respuesta = clinica["medico"].post("/addRE", data={
        "id_consulta": INEXISTENTE, "id_medicamento": INEXISTENTE,
        "cantidad": 1, "indicaciones": "una al día",
    }, follow_redirects=True)
    assert respuesta.status_code == 200
    assert datos.contar("receta") == 0


def test_editar_un_medico_con_una_especialidad_inexistente_no_tumba_la_pantalla(clinica, datos):
    respuesta = clinica["admin"].post(f"/editMED/{clinica['id_medico']}", data={
        "nombre": "Ana Torres", "numero_identidad": "12345", "telefono": "3000000000",
        "email": "ana@ejemplo.com", "id_especialidad": INEXISTENTE,
    }, follow_redirects=True)
    assert respuesta.status_code == 200


def test_el_camino_feliz_de_la_historia_clinica_sigue_funcionando(clinica, datos):
    """La otra mitad del Ítem 11: que la corrección no rompiera lo que sí servía."""
    clinica["medico"].post("/addHI", data={
        "id_paciente": clinica["id_paciente"], "fecha": "2026-09-01",
        "descripcion": "evolución favorable", "notas": "control en un mes",
    }, follow_redirects=True)
    assert datos.contar("historia") == 1


# --- Bajas lógicas: nunca se borra a nadie -----------------------------------

def test_dar_de_baja_a_un_usuario_no_lo_borra(clinica, datos):
    id_usuario = datos.usuario("temporal", "paciente")
    clinica["admin"].post(f"/deleteUS/{id_usuario}", follow_redirects=True)
    fila = datos.fila("SELECT estado FROM usuario WHERE id_usuario=%s", (id_usuario,))
    assert fila is not None, "el usuario se borró de verdad"
    assert fila["estado"] == "inactivo"


def test_un_usuario_dado_de_baja_se_puede_reactivar(clinica, datos):
    id_usuario = datos.usuario("temporal", "paciente", estado="inactivo")
    clinica["admin"].post(f"/reactivateUS/{id_usuario}", follow_redirects=True)
    assert datos.fila("SELECT estado FROM usuario WHERE id_usuario=%s",
                      (id_usuario,))["estado"] == "activo"


def test_dar_de_baja_a_un_medico_no_lo_borra(clinica, datos):
    clinica["admin"].post(f"/deleteMED/{clinica['id_medico']}", follow_redirects=True)
    fila = datos.fila("SELECT estado FROM medico WHERE id_medico=%s", (clinica["id_medico"],))
    assert fila is not None and fila["estado"] == "inactivo"


def test_dar_de_baja_a_un_paciente_no_lo_borra(clinica, datos):
    clinica["admin"].post(f"/deletePA/{clinica['id_paciente']}", follow_redirects=True)
    fila = datos.fila("SELECT estado FROM paciente WHERE id_paciente=%s",
                      (clinica["id_paciente"],))
    assert fila is not None and fila["estado"] == "inactivo"


def test_un_paciente_dado_de_baja_conserva_su_historial(clinica, datos):
    """Es la razón de ser de la baja lógica: el historial clínico no se pierde
    porque alguien deje de atenderse."""
    datos.historia(clinica["id_paciente"], clinica["id_medico"], "2026-09-01", "nota previa")
    clinica["admin"].post(f"/deletePA/{clinica['id_paciente']}", follow_redirects=True)
    assert datos.contar("historia") == 1


def test_un_medico_dado_de_baja_no_recibe_citas_nuevas(clinica, datos):
    clinica["admin"].post(f"/deleteMED/{clinica['id_medico']}", follow_redirects=True)
    fecha = (dv.now_colombia_naive() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M")
    respuesta = clinica["admin"].post("/addCI", data={
        "id_paciente": clinica["id_paciente"], "id_medico": clinica["id_medico"],
        "fecha": fecha, "motivo": "control"}, follow_redirects=True)
    assert datos.contar("cita") == 0
    assert "ya no recibe citas nuevas" in respuesta.data.decode("utf-8")


# --- Duplicados ---------------------------------------------------------------

def test_no_se_crean_dos_especialidades_con_el_mismo_nombre(clinica, datos):
    for _ in range(2):
        clinica["admin"].post("/addES", data={"nombre": "Cardiología",
                                              "descripcion": "corazón"},
                              follow_redirects=True)
    assert datos.contar("especialidad", "nombre='Cardiología'") == 1


def test_no_se_crean_dos_medicamentos_con_el_mismo_nombre(clinica, datos):
    for _ in range(2):
        clinica["admin"].post("/addME", data={"nombre": "Ibuprofeno",
                                              "descripcion": "analgésico",
                                              "dosis": "400 mg"},
                              follow_redirects=True)
    assert datos.contar("medicamento", "nombre='Ibuprofeno'") == 1


# --- Aislamiento entre pacientes ---------------------------------------------

def test_un_paciente_no_ve_la_historia_de_otro_por_la_api(clinica, datos):
    """La fuga que se encontró y se cerró: `api/view` devolvía el registro sin
    comprobar de quién era."""
    id_historia = datos.historia(clinica["otro_paciente"], clinica["id_medico"],
                                 "2026-09-01", "dato ajeno")
    respuesta = clinica["paciente"].get(f"/api/view/historia/{id_historia}")
    assert respuesta.status_code == 403
    assert b"dato ajeno" not in respuesta.data


def test_un_paciente_si_ve_la_suya_por_la_api(clinica, datos):
    id_historia = datos.historia(clinica["id_paciente"], clinica["id_medico"],
                                 "2026-09-01", "dato propio")
    respuesta = clinica["paciente"].get(f"/api/view/historia/{id_historia}")
    assert respuesta.status_code == 200
    assert "dato propio" in respuesta.data.decode("utf-8")


def test_el_listado_de_historias_de_un_paciente_solo_trae_las_suyas(clinica, datos):
    datos.historia(clinica["id_paciente"], clinica["id_medico"], "2026-09-01", "mi evolución")
    datos.historia(clinica["otro_paciente"], clinica["id_medico"], "2026-09-01", "evolución ajena")
    contenido = clinica["paciente"].get("/hiMC").data.decode("utf-8")
    assert "mi evolución" in contenido
    assert "evolución ajena" not in contenido


def test_el_listado_de_citas_de_un_paciente_solo_trae_las_suyas(clinica, datos):
    futuro = (dv.now_colombia_naive() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    otro_dia = (dv.now_colombia_naive() + timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S")
    datos.cita(clinica["id_paciente"], clinica["id_medico"], futuro, motivo="mi control")
    datos.cita(clinica["otro_paciente"], clinica["id_medico"], otro_dia, motivo="control ajeno")
    contenido = clinica["paciente"].get("/ciMC").data.decode("utf-8")
    assert "mi control" in contenido
    assert "control ajeno" not in contenido
