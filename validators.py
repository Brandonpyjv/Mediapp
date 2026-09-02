# -*- coding: utf-8 -*-
"""
validators.py
--------------
Funciones reutilizables de validación de formularios que no son fechas
(esas viven en date_validators.py). Por ahora solo correo electrónico.
"""
import re

# Regex pragmática de industria: usuario@dominio.tld, exige un TLD de al
# menos 2 letras. Deliberadamente NO se limita a una lista de dominios
# (gmail.com, hotmail.com...) porque eso dejaría fuera correos
# institucionales legítimos como "@sena.edu.co" o "@hospital.gov.co", que
# en este proyecto son justamente los que importan (decisión T5.8).
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email(value):
    """
    Valida el formato de un correo electrónico con una regex pragmática
    (usuario@dominio.tld). Hoy solo se exigía un '@' y un '.', lo que
    dejaba pasar valores como "brandon@gmail".

    Retorna una tupla (es_valido: bool, mensaje_error: str | None).
    """
    value = (value or "").strip()
    if not value or not _EMAIL_RE.match(value):
        return False, "Formato de correo electrónico no válido."
    return True, None
