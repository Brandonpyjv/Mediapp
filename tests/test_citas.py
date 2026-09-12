# -*- coding: utf-8 -*-
"""Las reglas de negocio de la agenda.

Son las que el autor fijó en el audio del 2026-08-31 y en las decisiones D4, D8 y
D9, más el apretón de S5. Cada una se comprueba forzando la petición, porque el
calendario ya evita ofrecer un turno imposible y lo que hay que demostrar es que
el servidor tampoco lo acepta cuando alguien se salta el calendario.
"""
from datetime import timedelta

import pytest

import date_validators as dv


def _fecha(dias, hora=9, minuto=0):
    """Una fecha futura con la forma que manda el formulario."""
    momento = (dv.now_colombia_naive() + timedelta(days=dias)).replace(
        hour=hora, minute=minuto, second=0, microsecond=0)
    return momento.strftime("%Y-%m-%dT%H:%M")


@pytest.fixture
def agenda(app, datos, entrar):
    datos.usuario("ana.admin", "admin")
    id_medico, _ = datos.medico(nombre="Ana Torres", username="ana.torres")
    otro_medico, _ = datos.medico(nombre="Beto Ruiz")
    id_paciente, _ = datos.paciente(nombre="Luis Pardo", username="luis.pardo")
    otro_paciente, _ = datos.paciente(nombre="Sara Gil", username="sara.gil")
    return {
        "admin": entrar("ana.admin", rol="admin"),
        "medico": entrar("ana.torres", rol="medico"),
        "paciente": entrar("luis.pardo", rol="paciente"),
        "otro_paciente_cliente": entrar("sara.gil", rol="paciente"),
        "id_medico": id_medico,
        "otro_medico": otro_medico,
        "id_paciente": id_paciente,
        "otro_paciente": otro_paciente,
    }


def _agendar(cliente, id_paciente, id_medico, fecha, **extra):
    datos = {"id_paciente": id_paciente, "id_medico": id_medico,
             "fecha": fecha, "motivo": "control"}
    datos.update(extra)
    return cliente.post("/addCI", data=datos, follow_redirects=True)


# --- Lo que sí se puede -------------------------------------------------------

def test_el_administrador_agenda_una_cita_en_un_turno_libre(agenda, datos):
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10))
    assert datos.contar("cita") == 1


# --- D4: treinta minutos entre citas del mismo médico, estrictos -------------

def test_dos_citas_del_mismo_medico_a_quince_minutos_se_rechazan(agenda, datos):
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10, 9, 0))
    respuesta = _agendar(agenda["admin"], agenda["otro_paciente"], agenda["id_medico"],
                         _fecha(10, 9, 15))
    assert datos.contar("cita") == 1
    assert "dentro de 30 minutos" in respuesta.data.decode("utf-8")


def test_dos_citas_del_mismo_medico_a_veintinueve_minutos_se_rechazan(agenda, datos):
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10, 9, 0))
    _agendar(agenda["admin"], agenda["otro_paciente"], agenda["id_medico"], _fecha(10, 9, 29))
    assert datos.contar("cita") == 1


def test_dos_citas_del_mismo_medico_a_treinta_minutos_exactos_se_permiten(agenda, datos):
    """El límite es estricto: 2:00 bloquea hasta 2:29, y 2:30 ya convive.
    Es el ejemplo que dio el autor."""
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10, 9, 0))
    _agendar(agenda["admin"], agenda["otro_paciente"], agenda["id_medico"], _fecha(10, 9, 30))
    assert datos.contar("cita") == 2


def test_la_separacion_es_por_medico_no_por_clinica(agenda, datos):
    """Dos médicos distintos pueden atender a la misma hora."""
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10, 9, 0))
    _agendar(agenda["admin"], agenda["otro_paciente"], agenda["otro_medico"], _fecha(10, 9, 0))
    assert datos.contar("cita") == 2


# --- Una cita por paciente y por día -----------------------------------------

def test_un_paciente_no_tiene_dos_citas_el_mismo_dia(agenda, datos):
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10, 9, 0))
    respuesta = _agendar(agenda["admin"], agenda["id_paciente"], agenda["otro_medico"],
                         _fecha(10, 15, 0))
    assert datos.contar("cita") == 1
    assert "ya tiene una cita" in respuesta.data.decode("utf-8")


def test_el_mismo_paciente_sí_puede_tener_citas_en_dias_distintos(agenda, datos):
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(10))
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(11))
    assert datos.contar("cita") == 2


# --- S5: no se agenda en el pasado, ni por fecha ni por hora -----------------

def test_no_se_agenda_en_una_fecha_pasada(agenda, datos):
    ayer = (dv.now_colombia_naive() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    respuesta = _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], ayer)
    assert datos.contar("cita") == 0
    assert "ya pasaron" in respuesta.data.decode("utf-8")


def test_no_se_agenda_hoy_a_una_hora_que_ya_paso(agenda, datos):
    """S5. Antes solo se comparaba la fecha, así que el servidor aceptaba una
    cita hoy a las 08:00 siendo las 15:00, aunque el calendario ya no la ofrecía."""
    hace_dos_horas = (dv.now_colombia_naive() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
    respuesta = _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"],
                         hace_dos_horas)
    assert datos.contar("cita") == 0
    assert "ya pasaron" in respuesta.data.decode("utf-8")


# --- D9: el paciente agenda su propia cita -----------------------------------

def test_el_paciente_agenda_su_cita_desde_el_calendario(agenda, datos):
    _agendar(agenda["paciente"], agenda["id_paciente"], agenda["id_medico"],
             _fecha(12), origen="calendario")
    assert datos.contar("cita") == 1


def test_el_paciente_no_puede_agendarle_una_cita_a_otro(agenda, datos):
    """El `id_paciente` sale SIEMPRE de la sesión. Si se tomara del formulario,
    un paciente podría agendarle una cita a otro manipulando la petición."""
    _agendar(agenda["paciente"], agenda["otro_paciente"], agenda["id_medico"],
             _fecha(12), origen="calendario")
    fila = datos.fila("SELECT id_paciente FROM cita")
    assert fila is not None, "la cita no se creó"
    assert fila["id_paciente"] == agenda["id_paciente"], \
        "la cita quedó a nombre del paciente enviado en el formulario, no del de la sesión"


def test_el_paciente_no_agenda_por_el_formulario_completo(agenda, datos):
    """El formulario completo permite elegir a qué paciente se agenda, y esa
    elección no es suya: se le devuelve al calendario."""
    respuesta = _agendar(agenda["paciente"], agenda["id_paciente"], agenda["id_medico"],
                         _fecha(12))
    assert datos.contar("cita") == 0
    assert "calendario de disponibilidad" in respuesta.data.decode("utf-8")


# --- La agenda del médico es de solo lectura ---------------------------------

def test_el_medico_no_agenda_citas(agenda, datos):
    respuesta = _agendar(agenda["medico"], agenda["id_paciente"], agenda["id_medico"],
                         _fecha(12))
    assert datos.contar("cita") == 0
    assert "restringido" in respuesta.data.decode("utf-8").lower()


def test_el_medico_no_agenda_ni_pasando_por_el_calendario(agenda, datos):
    _agendar(agenda["medico"], agenda["id_paciente"], agenda["id_medico"],
             _fecha(12), origen="calendario")
    assert datos.contar("cita") == 0


def test_el_medico_no_puede_editar_una_cita(agenda, datos):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"],
                         _fecha(12).replace("T", " "), motivo="original")
    agenda["medico"].post(f"/editCI/{id_cita}", data={
        "id_paciente": agenda["id_paciente"], "id_medico": agenda["id_medico"],
        "fecha": _fecha(13), "motivo": "cambiado por el médico"}, follow_redirects=True)
    assert datos.fila("SELECT motivo FROM cita WHERE id_cita=%s", (id_cita,))["motivo"] == "original"


def test_el_medico_no_puede_eliminar_una_cita(agenda, datos):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    agenda["medico"].post(f"/deleteCI/{id_cita}", follow_redirects=True)
    assert datos.contar("cita") == 1


# --- D8: el paciente cancela la suya, y solo la suya -------------------------

def test_el_paciente_cancela_su_propia_cita(agenda, datos):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    agenda["paciente"].post(f"/cancelCI/{id_cita}", follow_redirects=True)
    assert datos.fila("SELECT estado FROM cita WHERE id_cita=%s", (id_cita,))["estado"] == "cancelada"


def test_cancelar_no_borra_la_cita(agenda, datos):
    """Nunca se pierde el registro: la fila sigue ahí, marcada."""
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    agenda["paciente"].post(f"/cancelCI/{id_cita}", follow_redirects=True)
    assert datos.contar("cita", "id_cita=%s", (id_cita,)) == 1


def test_un_paciente_no_puede_cancelar_la_cita_de_otro(agenda, datos):
    id_cita = datos.cita(agenda["otro_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    agenda["paciente"].post(f"/cancelCI/{id_cita}", follow_redirects=True)
    assert datos.fila("SELECT estado FROM cita WHERE id_cita=%s", (id_cita,))["estado"] == "agendada"


def test_el_medico_no_cancela_citas(agenda, datos):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    agenda["medico"].post(f"/cancelCI/{id_cita}", follow_redirects=True)
    assert datos.fila("SELECT estado FROM cita WHERE id_cita=%s", (id_cita,))["estado"] == "agendada"


def test_un_turno_cancelado_vuelve_a_estar_libre(agenda, datos):
    """D8. Si el horario siguiera bloqueado, cancelar perjudicaría a los demás."""
    _agendar(agenda["admin"], agenda["id_paciente"], agenda["id_medico"], _fecha(14, 9, 0))
    id_cita = datos.fila("SELECT id_cita FROM cita")["id_cita"]
    agenda["paciente"].post(f"/cancelCI/{id_cita}", follow_redirects=True)

    _agendar(agenda["admin"], agenda["otro_paciente"], agenda["id_medico"], _fecha(14, 9, 0))
    assert datos.contar("cita", "estado='agendada'") == 1


# --- T6.9: no se reescribe el histórico --------------------------------------

def test_no_se_edita_una_cita_que_ya_paso(agenda, datos):
    ayer = (dv.now_colombia_naive() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], ayer)
    respuesta = agenda["admin"].get(f"/editCI/{id_cita}", follow_redirects=True)
    assert "ya pasó" in respuesta.data.decode("utf-8")


def test_no_se_edita_una_cita_cancelada(agenda, datos):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"],
                         _fecha(12).replace("T", " "), estado="cancelada")
    respuesta = agenda["admin"].get(f"/editCI/{id_cita}", follow_redirects=True)
    assert "cancelada" in respuesta.data.decode("utf-8")


def test_no_se_cancela_una_cita_que_ya_paso(agenda, datos):
    """S5 alineó esta regla con la de agendar: antes comparaba solo la fecha, así
    que una cita de hoy a las 08:00 se podía cancelar a las 15:00."""
    hace_dos_horas = (dv.now_colombia_naive() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], hace_dos_horas)
    respuesta = agenda["paciente"].post(f"/cancelCI/{id_cita}", follow_redirects=True)
    assert "ya pasaron" in respuesta.data.decode("utf-8")
    assert datos.fila("SELECT estado FROM cita WHERE id_cita=%s", (id_cita,))["estado"] == "agendada"


# --- S4: reprogramar tampoco puede asignar a alguien dado de baja ------------

def test_no_se_reasigna_una_cita_a_un_medico_dado_de_baja(agenda, datos, bd):
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"], _fecha(12).replace("T", " "))
    cur = bd.cursor()
    cur.execute("UPDATE medico SET estado='inactivo' WHERE id_medico=%s", (agenda["otro_medico"],))
    cur.close()

    agenda["admin"].post(f"/editCI/{id_cita}", data={
        "id_paciente": agenda["id_paciente"], "id_medico": agenda["otro_medico"],
        "fecha": _fecha(12), "motivo": "control"}, follow_redirects=True)
    fila = datos.fila("SELECT id_medico FROM cita WHERE id_cita=%s", (id_cita,))
    assert fila["id_medico"] == agenda["id_medico"]


def test_se_puede_guardar_una_cita_cuyo_medico_esta_de_baja_sin_cambiarlo(agenda, datos, bd):
    """El otro lado de S4: si se prohibiera sin más, guardar cualquier cambio en
    una cita vieja expulsaría de ella al médico que la atendió."""
    id_cita = datos.cita(agenda["id_paciente"], agenda["id_medico"],
                         _fecha(12).replace("T", " "), motivo="original")
    cur = bd.cursor()
    cur.execute("UPDATE medico SET estado='inactivo' WHERE id_medico=%s", (agenda["id_medico"],))
    cur.close()

    agenda["admin"].post(f"/editCI/{id_cita}", data={
        "id_paciente": agenda["id_paciente"], "id_medico": agenda["id_medico"],
        "fecha": _fecha(12), "motivo": "motivo corregido"}, follow_redirects=True)
    assert datos.fila("SELECT motivo FROM cita WHERE id_cita=%s",
                      (id_cita,))["motivo"] == "motivo corregido"
