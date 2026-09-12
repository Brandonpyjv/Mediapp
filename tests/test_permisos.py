# -*- coding: utf-8 -*-
"""La matriz de permisos de los tres roles (`CLAUDE.md` §2).

Es la parte del sistema donde un error no se ve, porque la pantalla sigue
funcionando: simplemente alguien puede hacer algo que no le corresponde. Por eso
cada regla se comprueba **por su efecto**, forzando la petición, y no por que el
botón no aparezca en el HTML.

Las tres reglas que el evaluador y el autor pusieron por encima de las demás:

- El **Administrador** puede hacer todo salvo **crear o modificar historias
  clínicas**. Es su única restricción.
- El **Médico** es dueño exclusivo del acto clínico (historia, consulta y
  receta) y su agenda es **de solo lectura**: nunca agenda ni cambia sus citas.
- El **Paciente** consulta lo suyo, con dos únicas excepciones de escritura:
  agendar su cita (D9) y cancelarla (D8). No puede ni eliminar su propio perfil.
"""
import pytest

# (ruta, quién puede entrar). Levantado de los decoradores reales de `index.py`.
PANTALLAS = [
    ("/usMC", {"admin"}),
    ("/medMC", {"admin"}),
    ("/esMC", {"admin"}),
    ("/meMC", {"admin"}),
    ("/addPA", {"admin"}),
    ("/addUS", {"admin"}),
    ("/addMED", {"admin"}),
    ("/addES", {"admin"}),
    ("/addME", {"admin"}),
    ("/addHI", {"medico"}),
    ("/addCO", {"medico"}),
    ("/addRE", {"medico"}),
    ("/addEX", {"medico"}),
    ("/", {"admin", "medico", "paciente"}),
    ("/ciMC", {"admin", "medico", "paciente"}),
    ("/hiMC", {"admin", "medico", "paciente"}),
    ("/coMC", {"admin", "medico", "paciente"}),
    ("/reMC", {"admin", "medico", "paciente"}),
    ("/exMC", {"admin", "medico", "paciente"}),
    ("/paMC", {"admin", "medico", "paciente"}),
    ("/disponibilidad", {"admin", "medico", "paciente"}),
]


@pytest.fixture
def tres_roles(app, datos, entrar):
    """Un administrador, un médico con ficha y un paciente con ficha, dentro."""
    datos.usuario("ana.admin", "admin")
    id_medico, _ = datos.medico(nombre="Ana Torres", username="ana.torres")
    id_paciente, id_usuario_paciente = datos.paciente(nombre="Luis Pardo", username="luis.pardo")
    return {
        "clientes": {
            "admin": entrar("ana.admin", rol="admin"),
            "medico": entrar("ana.torres", rol="medico"),
            "paciente": entrar("luis.pardo", rol="paciente"),
        },
        "id_medico": id_medico,
        "id_paciente": id_paciente,
        "id_usuario_paciente": id_usuario_paciente,
    }


@pytest.mark.parametrize("ruta,permitidos", PANTALLAS)
def test_quien_entra_a_cada_pantalla(tres_roles, ruta, permitidos):
    for rol, cliente in tres_roles["clientes"].items():
        respuesta = cliente.get(ruta)
        if rol in permitidos:
            assert respuesta.status_code == 200, f"{rol} debería entrar a {ruta}"
        else:
            assert respuesta.status_code == 302, f"{rol} NO debería entrar a {ruta}"


# --- Historia clínica: la única cosa que el administrador no puede hacer ------

def test_el_administrador_no_puede_crear_una_historia_clinica(tres_roles, datos):
    respuesta = tres_roles["clientes"]["admin"].post("/addHI", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "descripcion": "intento del administrador", "notas": "",
    }, follow_redirects=True)
    assert datos.contar("historia") == 0, "el administrador creó una historia clínica"
    assert "solo para médicos" in respuesta.data.decode("utf-8")


def test_el_administrador_no_puede_editar_una_historia_clinica(tres_roles, datos):
    id_historia = datos.historia(tres_roles["id_paciente"], tres_roles["id_medico"],
                                 "2026-09-01", "original")
    tres_roles["clientes"]["admin"].post(f"/editHI/{id_historia}", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "descripcion": "reescrita por el administrador", "notas": "",
    }, follow_redirects=True)
    fila = datos.fila("SELECT descripcion FROM historia WHERE id_historia=%s", (id_historia,))
    assert fila["descripcion"] == "original"


def test_el_administrador_no_puede_eliminar_una_historia_clinica(tres_roles, datos):
    id_historia = datos.historia(tres_roles["id_paciente"], tres_roles["id_medico"],
                                 "2026-09-01")
    tres_roles["clientes"]["admin"].post(f"/deleteHI/{id_historia}", follow_redirects=True)
    assert datos.contar("historia") == 1


def test_el_administrador_si_puede_leer_las_historias(tres_roles, datos):
    """D5: leer sí, escribir no. El administrador necesita ver el historial para
    operar la clínica, pero el acto clínico no es suyo."""
    datos.historia(tres_roles["id_paciente"], tres_roles["id_medico"], "2026-09-01",
                   "una nota que el administrador debe poder leer")
    respuesta = tres_roles["clientes"]["admin"].get("/hiMC")
    assert respuesta.status_code == 200
    assert "una nota que el administrador debe poder leer" in respuesta.data.decode("utf-8")


def test_el_medico_si_puede_crear_una_historia_clinica(tres_roles, datos):
    """El otro lado de la regla: si esto falla, el permiso exclusivo no sirve
    de nada. Es además el fallo del Ítem 11 que reprobó la sustentación."""
    tres_roles["clientes"]["medico"].post("/addHI", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "descripcion": "evolución del paciente", "notas": "sin novedad",
    }, follow_redirects=True)
    assert datos.contar("historia") == 1
    fila = datos.fila("SELECT id_medico, descripcion FROM historia")
    assert fila["descripcion"] == "evolución del paciente"
    assert fila["id_medico"] == tres_roles["id_medico"], \
        "la autoría debe salir de la sesión del médico"


def test_el_paciente_no_puede_crear_una_historia_clinica(tres_roles, datos):
    tres_roles["clientes"]["paciente"].post("/addHI", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "descripcion": "intento del paciente", "notas": "",
    }, follow_redirects=True)
    assert datos.contar("historia") == 0


# --- Consulta y receta: también exclusivas del médico ------------------------

def test_el_administrador_no_puede_crear_una_consulta(tres_roles, datos):
    tres_roles["clientes"]["admin"].post("/addCO", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "diagnostico": "intento", "tratamiento": "intento",
    }, follow_redirects=True)
    assert datos.contar("consulta") == 0


def test_el_paciente_no_puede_crear_una_consulta(tres_roles, datos):
    tres_roles["clientes"]["paciente"].post("/addCO", data={
        "id_paciente": tres_roles["id_paciente"], "fecha": "2026-09-01",
        "diagnostico": "intento", "tratamiento": "intento",
    }, follow_redirects=True)
    assert datos.contar("consulta") == 0


# --- El perfil del paciente ---------------------------------------------------

def test_el_paciente_no_puede_eliminar_su_propio_perfil(tres_roles, datos):
    tres_roles["clientes"]["paciente"].post(f"/deletePA/{tres_roles['id_paciente']}",
                                            follow_redirects=True)
    assert datos.contar("paciente", "id_paciente=%s", (tres_roles["id_paciente"],)) == 1


def test_el_medico_no_puede_eliminar_a_un_paciente(tres_roles, datos):
    tres_roles["clientes"]["medico"].post(f"/deletePA/{tres_roles['id_paciente']}",
                                          follow_redirects=True)
    assert datos.contar("paciente", "id_paciente=%s", (tres_roles["id_paciente"],)) == 1


# --- Los catálogos son del administrador (nota de la FASE 8) -----------------

def test_los_catalogos_no_se_leen_por_la_api_sin_ser_administrador(tres_roles, datos):
    """T8.1: `api/view` no comprobaba el rol en estos dos módulos, así que el
    catálogo se podía leer con cualquier sesión iniciada."""
    id_especialidad = datos.especialidad("Dermatología")
    id_medicamento = datos.fila(
        "SELECT id_medicamento FROM medicamento LIMIT 1") or {"id_medicamento": None}

    for rol in ("medico", "paciente"):
        respuesta = tres_roles["clientes"][rol].get(f"/api/view/especialidad/{id_especialidad}")
        assert respuesta.status_code == 403, f"{rol} pudo leer el catálogo de especialidades"

    respuesta = tres_roles["clientes"]["admin"].get(f"/api/view/especialidad/{id_especialidad}")
    assert respuesta.status_code == 200
