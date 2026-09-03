# -*- coding: utf-8 -*-
"""Comprueba el andamiaje antes que nada.

Si estas cuatro fallan, ninguna de las demás significa nada: estarían probando
la base equivocada, o una base sin esquema, o con datos colgando de la prueba
anterior.
"""
import database as db

from conftest import BASE_PRUEBAS


def test_la_aplicacion_apunta_a_la_base_de_pruebas(app):
    assert db.CONFIG["database"] == BASE_PRUEBAS
    assert BASE_PRUEBAS != "mediapp", "las pruebas no pueden correr sobre la base real"


def test_la_base_de_pruebas_tiene_las_once_tablas(bd):
    cur = bd.cursor()
    cur.execute("SHOW TABLES")
    tablas = {f[0] for f in cur.fetchall()}
    cur.close()
    assert tablas == {"cita", "consulta", "especialidad", "examen", "historia",
                      "medicamento", "medico", "paciente", "receta", "rol", "usuario"}


def test_cada_prueba_empieza_con_la_base_vacia(datos):
    assert datos.contar("cita") == 0
    assert datos.contar("usuario") == 0
    datos.usuario("residuo", "admin")
    assert datos.contar("usuario") == 1      # la siguiente prueba no debe verlo


def test_la_prueba_anterior_no_dejo_residuos(datos):
    assert datos.contar("usuario") == 0
