# -*- coding: utf-8 -*-
"""Dos personas pidiendo el mismo turno a la vez (S2).

La regla de los treinta minutos estaba bien escrita desde antes, pero no se
aplicaba sola: entre el `SELECT` que comprobaba si el hueco estaba libre y el
`INSERT` que lo ocupaba había un instante en el que otra petición podía
comprobar lo mismo, no ver nada y agendar encima.

Aquí se prueban las dos cosas: que el sistema ya no deja pasar la doble reserva,
y que lo que la impide es el candado y no la suerte.
"""
import threading
from datetime import timedelta

import mysql.connector
import pytest

import date_validators as dv
from conftest import BASE_PRUEBAS, CONEXION

REPETICIONES = 6


@pytest.fixture
def dos_pacientes(app, datos, entrar):
    datos.usuario("ana.admin", "admin")
    id_medico, _ = datos.medico(nombre="Ana Torres")
    uno, _ = datos.paciente(nombre="Luis Pardo")
    otro, _ = datos.paciente(nombre="Sara Gil")
    return {"clientes": [entrar("ana.admin", rol="admin") for _ in range(2)],
            "id_medico": id_medico, "pacientes": [uno, otro]}


def _turno(dias, hora=9):
    return (dv.now_colombia_naive() + timedelta(days=dias)).replace(
        hour=hora, minute=0, second=0, microsecond=0)


def test_dos_peticiones_simultaneas_no_agendan_el_mismo_turno(dos_pacientes, datos):
    """La prueba de la carrera, tal como la vive el sistema.

    Las dos peticiones se sueltan a la vez con una barrera, para que ninguna
    empiece antes que la otra. Se repite varias veces porque una carrera que se
    corre una sola vez puede salir bien por casualidad.
    """
    for vuelta in range(REPETICIONES):
        momento = _turno(20 + vuelta)
        fecha = momento.strftime("%Y-%m-%dT%H:%M")
        salida = threading.Barrier(2)

        def pedir(k):
            salida.wait()
            dos_pacientes["clientes"][k].post("/addCI", data={
                "id_paciente": dos_pacientes["pacientes"][k],
                "id_medico": dos_pacientes["id_medico"],
                "fecha": fecha, "motivo": "carrera"}, follow_redirects=True)

        hilos = [threading.Thread(target=pedir, args=(k,)) for k in (0, 1)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        creadas = datos.contar("cita", "DATE(fecha)=%s", (momento.date(),))
        assert creadas == 1, (f"vuelta {vuelta + 1}: se agendaron {creadas} citas "
                              "para el mismo médico a la misma hora")


def test_el_candado_es_lo_que_evita_la_doble_reserva(datos):
    """La demostración del mecanismo, sin la aplicación de por medio.

    Dos conexiones hacen lo que hace la ruta, comprobar y después insertar, pero
    se les obliga a comprobar las dos **antes** de que ninguna inserte, que es
    justo el instante donde vivía el problema. Con la consulta a secas las dos
    ven el hueco libre y agendan; con `FOR UPDATE` la segunda espera, vuelve a
    mirar y encuentra la cita de la primera.

    Si esta prueba deja de distinguir los dos casos, el candado dejó de servir
    aunque la prueba de arriba siga pasando por lo rápido que corre.
    """
    id_medico, _ = datos.medico(nombre="Ana Torres")
    pacientes = [datos.paciente(nombre="Luis Pardo")[0], datos.paciente(nombre="Sara Gil")[0]]

    consulta = ("SELECT id_cita FROM cita WHERE id_medico=%s AND estado<>'cancelada' "
                "AND ABS(TIMESTAMPDIFF(MINUTE, fecha, %s))<30")

    def carrera(con_candado, momento):
        comprobado = threading.Barrier(2)
        candado = " FOR UPDATE" if con_candado else ""

        def reservar(k):
            conexion = mysql.connector.connect(**CONEXION, database=BASE_PRUEBAS)
            cursor = conexion.cursor()
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 10")
            try:
                cursor.execute(consulta + candado, (id_medico, momento))
                libre = cursor.fetchone() is None
                if not con_candado:
                    # Sin candado hay que forzar el solapamiento a mano; con él,
                    # la segunda ya se queda esperando aquí sola.
                    comprobado.wait()
                if libre:
                    cursor.execute("INSERT INTO cita (id_paciente, id_medico, fecha, motivo) "
                                   "VALUES (%s, %s, %s, 'demo')",
                                   (pacientes[k], id_medico, momento))
                    conexion.commit()
                else:
                    conexion.rollback()
            except mysql.connector.Error:
                conexion.rollback()          # interbloqueo: esa reserva no ocurre
            finally:
                cursor.close()
                conexion.close()

        hilos = [threading.Thread(target=reservar, args=(k,)) for k in (0, 1)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()
        return datos.contar("cita", "DATE(fecha)=%s", (momento.date(),))

    sin_candado = carrera(False, _turno(40))
    con_candado = carrera(True, _turno(41))

    assert sin_candado == 2, ("sin el candado deberían colarse las dos reservas; "
                              "si no ocurre, la prueba dejó de reproducir la carrera")
    assert con_candado == 1, "con el candado solo puede quedar una cita"
