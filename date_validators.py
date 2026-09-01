# -*- coding: utf-8 -*-
"""
date_validators.py
-------------------
Funciones reutilizables para validar fechas provenientes de formularios
HTML (inputs type="date" y type="datetime-local") en el backend.

Se centraliza aquí la lógica para que "hoy" se calcule SIEMPRE de forma
dinámica (nunca una fecha fija) y usando la zona horaria de Colombia
(America/Bogota), evitando que un servidor configurado en otra zona
horaria (p. ej. UTC) determine incorrectamente el cambio de día.

Reglas de negocio implementadas:
    - CITAS MÉDICAS:       la fecha NO puede ser anterior a hoy (hoy y
                            futuro sí se permiten).
    - FECHA DE NACIMIENTO: la fecha NO puede ser futura (hoy y pasado
                            sí se permiten).
    - HISTORIAS CLÍNICAS:  la fecha debe ser válida y bien formada
                            (no se exige regla de pasado/futuro porque
                            no fue solicitada; solo se evita guardar
                            basura o fechas mal formadas).
"""
from datetime import datetime, timedelta, timezone as dt_timezone

try:
    # Disponible en Python 3.9+. Si el sistema no tiene la base de datos
    # de zonas horarias (tzdata) instalada, caemos al fallback de abajo.
    from zoneinfo import ZoneInfo
    COLOMBIA_TZ = ZoneInfo("America/Bogota")
except Exception:
    # Colombia no tiene horario de verano: siempre es UTC-5.
    COLOMBIA_TZ = dt_timezone(timedelta(hours=-5))


def now_colombia():
    """Fecha y hora actuales en la zona horaria de Colombia."""
    return datetime.now(COLOMBIA_TZ)


def today_colombia():
    """Fecha (sin hora) actual en la zona horaria de Colombia."""
    return now_colombia().date()


def parse_date(value):
    """
    Convierte un valor de <input type="date"> ('YYYY-MM-DD') a `date`.
    Devuelve None si el valor está vacío o mal formado.
    """
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def parse_datetime_local(value):
    """
    Convierte un valor de <input type="datetime-local">
    ('YYYY-MM-DDTHH:MM' o 'YYYY-MM-DDTHH:MM:SS') a `datetime` (naive).
    También acepta 'YYYY-MM-DD HH:MM' por si el separador viene distinto.
    Devuelve None si el valor está vacío o mal formado.
    """
    if not value:
        return None
    normalized = value.strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    return None


def parse_flexible_datetime(value):
    """
    Intenta parsear tanto 'YYYY-MM-DD' (date) como 'YYYY-MM-DDTHH:MM'
    (datetime-local). Útil para historia clínica, cuyo campo 'fecha' se
    edita a veces con un input type="date" (modal rápido) y a veces con
    uno type="datetime-local" (formulario completo).
    Devuelve un `datetime` (con hora 00:00 si solo venía la fecha) o None.
    """
    if not value:
        return None
    dt = parse_datetime_local(value)
    if dt is not None:
        return dt
    d = parse_date(value)
    if d is not None:
        return datetime(d.year, d.month, d.day)
    return None


def validate_appointment_datetime(value):
    """
    Regla de negocio para CITAS MÉDICAS:
    No se permiten fechas anteriores al día de hoy. Hoy o cualquier
    fecha futura sí se permiten.

    Retorna una tupla (es_valida: bool, mensaje_error: str | None).
    """
    parsed = parse_datetime_local(value)
    if parsed is None:
        return False, "Fecha no válida. Ingrese una fecha y hora de cita correctas."
    if parsed.date() < today_colombia():
        return False, ("Fecha no válida. No se pueden registrar citas en "
                        "fechas anteriores a la fecha actual.")
    return True, None


def validate_birthdate(value):
    """
    Regla de negocio para FECHA DE NACIMIENTO (registro de usuarios y
    pacientes): No se permite una fecha futura. Hoy o cualquier fecha
    pasada sí se permiten.

    Retorna una tupla (es_valida: bool, mensaje_error: str | None).
    """
    parsed = parse_date(value)
    if parsed is None:
        return False, "Fecha no válida. Ingrese una fecha de nacimiento correcta."
    if parsed > today_colombia():
        return False, "Fecha no válida. La fecha de nacimiento no puede ser una fecha futura."
    return True, None


def validate_clinical_record_datetime(value):
    """
    Regla de negocio para HISTORIAS CLÍNICAS: la fecha debe ser una
    fecha real y bien formada. No se restringe pasado/futuro porque
    esa regla no fue solicitada para este módulo.

    Retorna una tupla (es_valida: bool, mensaje_error: str | None).
    """
    parsed = parse_flexible_datetime(value)
    if parsed is None:
        return False, "Fecha no válida. Ingrese una fecha correcta para la historia clínica."
    return True, None


def validate_consultation_datetime(value):
    """
    Regla de negocio para CONSULTAS: la fecha y hora deben ser reales y
    estar bien formadas. No se restringe pasado/futuro (mismo criterio
    que historias clínicas) porque una consulta puede registrarse
    después de haber ocurrido.

    Retorna una tupla (es_valida: bool, mensaje_error: str | None).
    """
    parsed = parse_flexible_datetime(value)
    if parsed is None:
        return False, "Fecha no válida. Ingrese una fecha y hora correctas para la consulta."
    return True, None


def validate_lab_request_datetime(value):
    """
    Regla de negocio para SOLICITUDES DE EXAMEN: la fecha de solicitud
    debe ser una fecha real y bien formada. No se restringe pasado/futuro
    por el mismo criterio que historias clínicas y consultas.

    Retorna una tupla (es_valida: bool, mensaje_error: str | None).
    """
    parsed = parse_flexible_datetime(value)
    if parsed is None:
        return False, "Fecha no válida. Ingrese una fecha de solicitud correcta para el examen."
    return True, None
