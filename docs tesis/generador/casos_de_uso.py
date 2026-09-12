# -*- coding: utf-8 -*-
"""
Catálogo de casos de uso de MediApp, **fuente única**.

De aquí salen los diagramas del anexo E2 (T5), las fichas del anexo E3 (T6) y el punto 5.2 del
documento de grado (T13). Tenerlo en un solo lugar no es prolijidad, porque son tres piezas que
hablan de lo mismo, y cuando cada una mantiene su propia lista basta con un caso agregado en
una para que las otras queden describiendo un sistema que ya no existe. Un diagrama con seis
elipses y una documentación con siete fichas es un error que nadie nota hasta la sustentación.

Cada caso se enuncia como un **objetivo del actor** y no como una operación de la base, de
manera que se lee «Cambiar el estado de la cuenta» y no «Actualizar el campo estado de
usuario». Por eso hay 60 casos de uso frente a 87 requisitos funcionales, y la correspondencia
entre unos y otros queda anotada en el campo `rf`.

**El campo `tablas` es lo que pide el evaluador.** La observación de los jurados exige que cada
caso de uso sea trazable a las tablas del modelo de datos que toca, y que en esa trazabilidad
no aparezca código SQL (observación O12). Por eso aquí solo van nombres de tabla, nunca
sentencias, y `verificar.py` comprueba esa regla sobre el documento ya generado.

Un caso sin actores dibujados corresponde al actor Sistema, que es el nombre que este trabajo
le da a las reglas que se ejecutan sin que nadie las solicite.

Este módulo no genera ningún documento, solo datos.
"""

# (código, nombre, [actores], descripción, requisitos que cubre, [tablas que toca])

M1 = [
    ("CU-01", "Iniciar sesión", ["Administrador", "Médico", "Paciente"],
     "Acceder al sistema presentando el nombre de usuario y la contraseña, que se compara "
     "contra el hash almacenado.", "RF 1.1, RF 1.3", ["usuario", "rol"]),
    ("CU-02", "Redirigir al panel según el rol", [],
     "Determinar el rol de quien acaba de autenticarse y llevarlo al tablero que le "
     "corresponde, sin pedirle que elija su perfil.", "RF 1.2", ["usuario", "rol"]),
    ("CU-03", "Registrarse como paciente", ["Paciente"],
     "Crear la propia cuenta indicando los datos personales y las credenciales, con lo que la "
     "persona queda registrada a la vez como usuario y como paciente.", "RF 1.4, RF 1.5",
     ["usuario", "rol", "paciente"]),
    ("CU-04", "Cerrar sesión", ["Administrador", "Médico", "Paciente"],
     "Terminar la sesión en curso, con lo que el sistema queda sin acceso hasta un nuevo "
     "ingreso.", "RF 1.7", ["Ninguna"]),
    ("CU-05", "Restringir la vista y las operaciones según el rol", [],
     "Comprobar en cada petición que existe una sesión válida y que el rol que trae tiene "
     "permitida la operación, y presentar únicamente los módulos que ese rol puede abrir.",
     "RF 1.6, RF 1.8, RF 1.9", ["usuario", "rol"]),
]

M2 = [
    ("CU-06", "Crear la cuenta de usuario", ["Administrador"],
     "Dar de alta una cuenta de acceso indicando su nombre de usuario, su contraseña y el rol "
     "con el que trabajará.", "RF 2.1, RF 2.7", ["usuario", "rol"]),
    ("CU-07", "Consultar las cuentas de usuario", ["Administrador"],
     "Revisar las cuentas del sistema, buscarlas por nombre de usuario y filtrarlas por rol y "
     "por estado.", "RF 2.2, RF 2.8", ["usuario", "rol"]),
    ("CU-08", "Actualizar la cuenta y su rol", ["Administrador"],
     "Modificar el nombre de usuario, el rol asignado o la contraseña de una cuenta ya "
     "existente.", "RF 2.3, RF 2.4, RF 2.7", ["usuario", "rol"]),
    ("CU-09", "Cambiar el estado de la cuenta", ["Administrador"],
     "Desactivar una cuenta para retirarle el acceso, o reactivarla, sin borrarla del "
     "sistema.", "RF 2.5, RF 2.6", ["usuario"]),
]

M3 = [
    ("CU-10", "Registrar el médico", ["Administrador"],
     "Dar de alta la ficha profesional de un médico con su especialidad y vincularla a la "
     "cuenta con la que ingresará al sistema.", "RF 3.1, RF 3.7",
     ["medico", "usuario", "especialidad"]),
    ("CU-11", "Consultar los médicos", ["Administrador"],
     "Revisar los médicos registrados, buscarlos por nombre o documento y filtrarlos por "
     "especialidad y por estado.", "RF 3.2, RF 3.8", ["medico", "especialidad"]),
    ("CU-12", "Actualizar la ficha del médico", ["Administrador"],
     "Modificar los datos de contacto del médico o la especialidad a la que pertenece.",
     "RF 3.3", ["medico", "especialidad"]),
    ("CU-13", "Cambiar el estado del médico", ["Administrador"],
     "Dar de baja a un médico para que deje de ofrecerse al agendar, o reactivarlo, sin que "
     "desaparezca nada de lo que firmó.", "RF 3.4, RF 3.5", ["medico"]),
    ("CU-14", "Controlar el acceso del médico", ["Administrador"],
     "Habilitar o suspender el ingreso de la cuenta de un médico sin dar de baja su ficha ni "
     "alterar su agenda.", "RF 3.6", ["medico", "usuario"]),
]

M4 = [
    ("CU-15", "Registrar el paciente", ["Administrador"],
     "Dar de alta a una persona que recibirá atención, con sus datos personales y de "
     "contacto.", "RF 4.1, RF 4.7, RF 4.8", ["paciente", "usuario"]),
    ("CU-16", "Consultar los pacientes", ["Administrador", "Médico"],
     "Revisar el directorio de pacientes registrados y buscar a uno por nombre o documento, "
     "con el médico limitado a consultarlo.", "RF 4.2, RF 4.3", ["paciente"]),
    ("CU-17", "Actualizar los datos del paciente", ["Administrador"],
     "Modificar los datos personales y de contacto de un paciente ya registrado.", "RF 4.4",
     ["paciente"]),
    ("CU-18", "Cambiar el estado del paciente", ["Administrador"],
     "Dar de baja a un paciente, o reactivarlo, conservando su historial clínico y sus citas.",
     "RF 4.5, RF 4.6", ["paciente"]),
    ("CU-19", "Consultar el perfil propio", ["Paciente"],
     "Revisar los datos personales propios, sin posibilidad de eliminar el perfil.", "RF 4.9",
     ["paciente", "usuario"]),
]

# Los casos van agrupados por actor y no por orden de aparición en la aplicación. El motivo es
# el dibujo: el diagrama sitúa a cada actor a la altura media de sus casos, así que una lista
# que alterna administrador, paciente y médico produce un diagrama donde todas las líneas se
# cruzan en el centro. Agrupados, cada actor queda frente a los suyos.
M5 = [
    ("CU-20", "Agendar la cita para un paciente", ["Administrador"],
     "Registrar una cita eligiendo el paciente, el médico, la fecha, la hora y el motivo de la "
     "consulta.", "RF 5.1", ["cita", "paciente", "medico"]),
    ("CU-21", "Reprogramar la cita", ["Administrador"],
     "Cambiar la fecha, la hora, el médico o el motivo de una cita ya agendada, incluidas las "
     "que reservó un paciente.", "RF 5.11", ["cita", "paciente", "medico"]),
    ("CU-22", "Eliminar la cita", ["Administrador"],
     "Retirar del sistema una cita cuando corresponda hacerlo.", "RF 5.13", ["cita"]),
    ("CU-23", "Consultar el listado de citas", ["Administrador"],
     "Revisar todas las citas del sistema, buscarlas por paciente o por médico y filtrarlas "
     "por estado y por fecha.", "RF 5.14", ["cita", "paciente", "medico"]),
    ("CU-24", "Reservar la cita propia", ["Paciente"],
     "Tomar un horario libre del calendario y quedar con la cita agendada de inmediato, sin "
     "aprobación previa y siempre a nombre de quien tiene la sesión.", "RF 5.2, RF 5.3",
     ["cita", "paciente", "medico"]),
    ("CU-25", "Consultar las citas propias", ["Paciente"],
     "Revisar únicamente las citas propias, con su estado y el médico que atenderá.",
     "RF 5.10", ["cita", "medico"]),
    ("CU-26", "Consultar la agenda propia", ["Médico"],
     "Revisar las citas asignadas, en modo de solo lectura y sin poder modificarlas.",
     "RF 5.9", ["cita", "paciente", "medico"]),
    ("CU-27", "Consultar la disponibilidad del médico", ["Paciente", "Administrador"],
     "Revisar por semana qué horarios de un médico están libres y cuáles están ocupados, sin "
     "que se revele qué paciente los ocupa.", "RF 5.8", ["cita", "medico"]),
    ("CU-28", "Validar las reglas de la agenda", [],
     "Comprobar antes de guardar que el paciente no tenga otra cita ese día, que el médico "
     "tenga al menos treinta minutos libres alrededor de la hora pedida y que la fecha no haya "
     "pasado.", "RF 5.4, RF 5.5, RF 5.7", ["cita"]),
    ("CU-29", "Reservar el turno de forma atómica", [],
     "Comprobar la disponibilidad y guardar la cita dentro de una misma transacción con "
     "bloqueo, de modo que dos solicitudes simultáneas sobre el mismo horario terminen en una "
     "cita y un rechazo.", "RF 5.6", ["cita"]),
    ("CU-30", "Cancelar la cita propia", ["Paciente"],
     "Anular una cita propia, con lo que el horario vuelve a quedar disponible sin que la cita "
     "se borre de la base.", "RF 5.12", ["cita"]),
]

M6 = [
    ("CU-31", "Registrar la evolución del paciente", ["Médico"],
     "Escribir un registro de historia clínica con su fecha, su descripción y las "
     "observaciones, que queda firmado por el médico de la sesión.",
     "RF 6.1, RF 6.3, RF 6.8", ["historia", "paciente", "medico"]),
    ("CU-32", "Corregir el registro clínico", ["Médico"],
     "Modificar un registro de historia clínica propio.", "RF 6.4", ["historia", "medico"]),
    ("CU-33", "Eliminar el registro clínico", ["Médico"],
     "Retirar un registro de historia clínica propio.", "RF 6.5", ["historia", "medico"]),
    ("CU-34", "Restringir la escritura clínica al médico", [],
     "Rechazar todo intento del administrador o del paciente de crear, modificar o eliminar un "
     "registro de historia clínica, aunque la petición se envíe directamente.", "RF 6.2",
     ["historia", "usuario", "rol"]),
    ("CU-35", "Consultar la historia clínica propia", ["Paciente"],
     "Revisar únicamente la propia historia clínica, sin poder modificarla.", "RF 6.6",
     ["historia", "medico"]),
    ("CU-36", "Consultar la historia clínica como apoyo a la operación", ["Administrador"],
     "Revisar las historias clínicas en modo de solo lectura.", "RF 6.7",
     ["historia", "paciente", "medico"]),
]

M7 = [
    ("CU-37", "Registrar el diagnóstico de la atención", ["Médico"],
     "Escribir el diagnóstico y el plan de tratamiento que resultan de haber atendido a un "
     "paciente, firmados por el médico de la sesión.", "RF 7.1, RF 7.6, RF 7.7",
     ["consulta", "paciente", "medico"]),
    ("CU-38", "Corregir el diagnóstico", ["Médico"],
     "Modificar el diagnóstico o el tratamiento de una consulta propia.", "RF 7.3",
     ["consulta", "medico"]),
    ("CU-39", "Eliminar la consulta", ["Médico"],
     "Retirar del sistema una consulta propia.", "RF 7.4", ["consulta", "medico"]),
    ("CU-40", "Restringir la escritura del diagnóstico al médico", [],
     "Rechazar todo intento del administrador o del paciente de crear, modificar o eliminar "
     "una consulta con su diagnóstico.", "RF 7.2", ["consulta", "usuario", "rol"]),
    ("CU-41", "Consultar los diagnósticos propios", ["Paciente"],
     "Revisar únicamente los diagnósticos propios y su plan de tratamiento.", "RF 7.5",
     ["consulta", "medico"]),
    ("CU-42", "Consultar los diagnósticos como apoyo a la operación", ["Administrador"],
     "Revisar las consultas registradas en modo de solo lectura.", "RF 7.8",
     ["consulta", "paciente", "medico"]),
]

M8 = [
    ("CU-43", "Emitir la receta", ["Médico"],
     "Prescribir un medicamento indicando la dosis, la frecuencia y la duración del "
     "tratamiento, sobre una consulta propia.", "RF 8.1, RF 8.7",
     ["receta", "consulta", "medicamento", "paciente"]),
    ("CU-44", "Seleccionar el medicamento del catálogo", [],
     "Ofrecer al médico los medicamentos vigentes en el momento de recetar, dejando fuera los "
     "descontinuados.", "RF 8.3", ["medicamento"]),
    ("CU-45", "Corregir la receta", ["Médico"],
     "Modificar una receta emitida sobre una consulta propia.", "RF 8.4",
     ["receta", "medicamento"]),
    ("CU-46", "Eliminar la receta", ["Médico"],
     "Retirar del sistema una receta emitida sobre una consulta propia.", "RF 8.5",
     ["receta", "consulta"]),
    ("CU-47", "Restringir la prescripción al médico", [],
     "Rechazar todo intento del administrador o del paciente de emitir, modificar o eliminar "
     "una receta.", "RF 8.2", ["receta", "usuario", "rol"]),
    ("CU-48", "Consultar las recetas propias", ["Paciente"],
     "Revisar únicamente las recetas emitidas al propio paciente, con su medicamento y su "
     "posología.", "RF 8.6", ["receta", "medicamento", "consulta"]),
    ("CU-49", "Consultar las recetas como apoyo a la operación", ["Administrador"],
     "Revisar las recetas emitidas en modo de solo lectura.", "RF 8.8",
     ["receta", "medicamento", "paciente"]),
]

M9 = [
    ("CU-50", "Solicitar el examen de laboratorio", ["Médico"],
     "Pedir un examen para un paciente indicando el tipo y la fecha, sin tocar los campos del "
     "resultado.", "RF 9.1, RF 9.7", ["examen", "paciente", "medico"]),
    ("CU-51", "Cargar el resultado del examen", ["Administrador"],
     "Registrar el resultado de un examen ya solicitado, que es el trabajo del laboratorio.",
     "RF 9.2", ["examen"]),
    ("CU-52", "Separar los campos del examen según el rol", [],
     "Exponer al médico los campos de la solicitud y al administrador los del resultado, y "
     "rechazar en el servidor el intento de cruzar ese límite.", "RF 9.3",
     ["examen", "usuario", "rol"]),
    ("CU-53", "Consultar los exámenes propios", ["Paciente"],
     "Revisar únicamente los exámenes propios, con su resultado cuando ya esté cargado.",
     "RF 9.4", ["examen", "medico"]),
    ("CU-54", "Consultar los exámenes solicitados", ["Médico"],
     "Revisar los exámenes solicitados por el propio médico y su resultado.", "RF 9.5",
     ["examen", "paciente"]),
    ("CU-55", "Eliminar el examen", ["Administrador"],
     "Retirar del sistema un examen.", "RF 9.6", ["examen"]),
]

M10 = [
    ("CU-56", "Gestionar las especialidades", ["Administrador"],
     "Mantener el catálogo de especialidades médicas, con su nombre y su descripción.",
     "RF 10.1, RF 10.2", ["especialidad"]),
    ("CU-57", "Impedir la eliminación de una especialidad con médicos", [],
     "Rechazar el borrado de una especialidad que tenga médicos asociados, para no dejar "
     "fichas sin especialidad.", "RF 10.3", ["especialidad", "medico"]),
    ("CU-58", "Gestionar los medicamentos", ["Administrador"],
     "Mantener el catálogo de medicamentos, con su nombre, su presentación y su descripción.",
     "RF 10.4, RF 10.5", ["medicamento"]),
    ("CU-59", "Descontinuar y reactivar el medicamento", ["Administrador"],
     "Retirar un medicamento de la oferta o devolverlo a ella, sin que las recetas que ya lo "
     "usaron dejen de mostrarlo.", "RF 10.6, RF 10.7", ["medicamento", "receta"]),
    ("CU-60", "Reservar los catálogos al administrador", [],
     "Rechazar el acceso del médico y del paciente a las pantallas de catálogo y a la consulta "
     "de su contenido.", "RF 10.8", ["especialidad", "medicamento", "usuario", "rol"]),
]

# (código del diagrama, nombre, actores a la izquierda, actores a la derecha, casos,
#  inclusiones, extensiones, descripción del diagrama)

MODULOS = [
    ("DCU-01", "Autenticación y sesión",
     ["Administrador", "Médico"], ["Paciente"], M1,
     [("CU-01", "CU-02"), ("CU-02", "CU-05")], [],
     "Recoge la entrada al sistema y el reparto de lo que cada quien ve. La redirección al "
     "panel se modela como caso incluido porque no es una decisión aparte, ya que un ingreso "
     "que no lleva a ningún tablero no ha terminado, y la restricción por rol se incluye a su "
     "vez porque el panel no puede armarse sin saber qué módulos tiene permitidos quien "
     "acaba de entrar. Esa misma restricción la incluye toda operación de los demás "
     "diagramas, y se omite de ellos para no volverlos ilegibles."),

    ("DCU-02", "Gestión de usuarios",
     ["Administrador"], [], M2, [], [],
     "Reúne la administración de las cuentas de acceso. Todos sus casos corresponden a un "
     "mismo actor porque decidir de qué es capaz cada persona es una atribución exclusiva del "
     "administrador, y por eso no hay aquí relaciones de inclusión ni de extensión."),

    ("DCU-03", "Gestión de médicos",
     ["Administrador"], ["Médico"], M3, [], [("CU-14", "CU-13")],
     "Cubre la ficha profesional del médico y su vínculo con la cuenta con la que ingresa, que "
     "se administra en el diagrama anterior. El control del acceso extiende el cambio de "
     "estado, porque suspender el ingreso de un médico y darlo de baja de la agenda son dos "
     "decisiones distintas que no siempre se toman juntas, ya que un profesional puede seguir "
     "recibiendo citas mientras se le retira temporalmente el acceso al sistema."),

    ("DCU-04", "Gestión de pacientes",
     ["Administrador"], ["Médico", "Paciente"], M4, [], [],
     "Cubre el registro y el mantenimiento de las personas que reciben atención. Aparecen los "
     "tres actores con alcances distintos, ya que el administrador gestiona, el médico "
     "únicamente consulta el directorio para ubicar a quien atiende y el paciente solo ve su "
     "propio perfil."),

    ("DCU-05", "Agendamiento de citas",
     ["Administrador", "Paciente"], ["Médico"], M5,
     [("CU-20", "CU-28"), ("CU-20", "CU-29"), ("CU-21", "CU-28"), ("CU-24", "CU-27"),
      ("CU-24", "CU-28"), ("CU-24", "CU-29")],
     [("CU-30", "CU-25")],
     "Es el núcleo del sistema. Los tres casos que escriben en la agenda comparten las "
     "condiciones que hacen válida a una cita, que son la validación de las reglas y la "
     "reserva del turno, y por eso se modelan como casos incluidos en lugar de repetirse en "
     "cada uno. La reserva de la cita propia incluye además la consulta de disponibilidad, "
     "porque el paciente no dispone de un formulario donde elegir la hora y solo puede tomar "
     "un horario del calendario, que es lo que impide que agende sobre un turno ocupado. La "
     "cancelación, en cambio, extiende la consulta de las citas propias, ya que el paciente "
     "entra a mirar lo que tiene y puede salir sin cancelar nada."),

    ("DCU-06", "Historia clínica",
     ["Médico"], ["Paciente", "Administrador"], M6,
     [("CU-31", "CU-34"), ("CU-32", "CU-34"), ("CU-33", "CU-34")], [],
     "Es el diagrama donde se ve la restricción que le da carácter al proyecto. Los tres casos "
     "de escritura incluyen la comprobación del rol, que no es una acción que alguien decida "
     "ejecutar sino una condición obligatoria de haber intentado escribir, y los dos actores "
     "de la derecha aparecen únicamente como lectores."),

    ("DCU-07", "Consultas y diagnósticos",
     ["Médico"], ["Paciente", "Administrador"], M7,
     [("CU-37", "CU-40"), ("CU-38", "CU-40"), ("CU-39", "CU-40")], [],
     "Repite la estructura del diagrama anterior porque la regla es la misma, y de la consulta "
     "cuelgan después las prescripciones. El administrador y el paciente aparecen a la derecha "
     "porque leen el resultado del acto clínico sin participar en él."),

    ("DCU-08", "Prescripciones",
     ["Médico"], ["Paciente", "Administrador"], M8,
     [("CU-43", "CU-44"), ("CU-43", "CU-47"), ("CU-45", "CU-47"), ("CU-46", "CU-47")], [],
     "Cierra el acto clínico. La selección del medicamento se modela como caso incluido porque "
     "el medicamento no se escribe libremente sino que se toma del catálogo vigente, de modo "
     "que una receta siempre apunte a un producto que existe."),

    ("DCU-09", "Exámenes de laboratorio",
     ["Médico", "Administrador"], ["Paciente"], M9,
     [("CU-50", "CU-52"), ("CU-51", "CU-52")], [],
     "Es el único diagrama con dos actores escribiendo sobre la misma fila, porque solicitar el "
     "examen y resolverlo son dos actos de dos personas distintas. La separación de los campos "
     "se incluye en ambos casos, ya que es lo que impide que el médico escriba un resultado o "
     "que el administrador modifique la solicitud."),

    ("DCU-10", "Catálogos",
     ["Administrador"], ["Médico"], M10,
     [("CU-56", "CU-57"), ("CU-56", "CU-60"), ("CU-58", "CU-60"), ("CU-59", "CU-60")], [],
     "Reúne los datos que se ajustan de vez en cuando y que después alimentan los formularios "
     "de todos los días. El médico aparece a la derecha sin pantalla propia de catálogo, "
     "porque el único lugar donde necesita ver los medicamentos es el selector del formulario "
     "de recetas, que pertenece al diagrama de prescripciones."),
]

# Casos del diagrama general, que resume el sistema en una sola figura.
# (nombre, [actores])

GENERAL = [
    ("Administrar usuarios y accesos", ["Administrador"]),
    ("Administrar médicos y pacientes", ["Administrador"]),
    ("Mantener los catálogos del sistema", ["Administrador"]),
    ("Gestionar la agenda de citas", ["Administrador"]),
    ("Cargar el resultado del examen", ["Administrador"]),
    ("Acceder al sistema según el rol", ["Administrador", "Médico", "Paciente"]),
    ("Consultar la agenda propia", ["Médico"]),
    ("Registrar la historia clínica", ["Médico"]),
    ("Registrar el diagnóstico y la prescripción", ["Médico"]),
    ("Solicitar el examen de laboratorio", ["Médico"]),
    ("Reservar y cancelar la cita propia", ["Paciente"]),
    ("Consultar la información clínica propia", ["Paciente"]),
]

# Las 11 tablas del esquema, en el orden en que las nombra la documentación. Sirve para
# comprobar que ningún caso de uso apunte a una tabla que no existe y que ninguna tabla se
# quede sin caso de uso que la toque, que es la trazabilidad que exigen los jurados.
TABLAS = [
    "cita", "consulta", "especialidad", "examen", "historia", "medicamento",
    "medico", "paciente", "receta", "rol", "usuario",
]


# --- Utilidades para quien consume el catálogo ----------------------------------

def todos():
    """Los 60 casos, en orden, con el módulo al que pertenecen."""
    salida = []
    for _, nombre_modulo, _, _, casos, *_ in MODULOS:
        for codigo, nombre, actores, descripcion, rf, tablas in casos:
            salida.append((codigo, nombre, nombre_modulo, actores, descripcion, rf, tablas))
    return salida


def por_nombre(casos):
    """Convierte la lista del catálogo al formato que espera el dibujante de diagramas."""
    return [(nombre, actores) for _, nombre, actores, _, _, _ in casos]


def codigo_de(nombre):
    for codigo, otro, *_ in todos():
        if otro == nombre:
            return codigo
    raise KeyError(nombre)


def caso(codigo):
    for fila in todos():
        if fila[0] == codigo:
            return fila
    raise KeyError(codigo)


def por_tabla():
    """Qué casos de uso toca cada tabla, que es la trazabilidad al revés."""
    mapa = {t: [] for t in TABLAS}
    for codigo, _, _, _, _, _, tablas in todos():
        for t in tablas:
            if t in mapa:
                mapa[t].append(codigo)
    return mapa


def _requisitos_citados():
    citados = set()
    for _, _, _, _, _, rf, _ in todos():
        for c in rf.split(","):
            c = c.strip()
            if c:
                citados.add(c)
    return citados


def comprobar():
    """Cruza el catálogo con el de requisitos y devuelve la lista de problemas.

    Es la comprobación que evita el error del que habla el encabezado, y son cuatro cosas.
    Que no haya un requisito funcional sin caso de uso que lo realice, que no haya un caso
    citando un requisito inexistente, que ningún caso apunte a una tabla que no está en el
    esquema y que ninguna de las 11 tablas se quede sin caso de uso que la toque.
    """
    import requisitos

    problemas = []
    existentes = {fila[0] for fila in requisitos.todos()}
    citados = _requisitos_citados()

    for codigo in sorted(existentes - citados):
        problemas.append(f"El requisito {codigo} no lo realiza ningun caso de uso.")
    for codigo in sorted(citados - existentes):
        problemas.append(f"Un caso de uso cita el requisito {codigo}, que no existe.")

    validas = set(TABLAS) | {"Ninguna"}
    for codigo, _, _, _, _, _, tablas in todos():
        for t in tablas:
            if t not in validas:
                problemas.append(f"{codigo} apunta a la tabla '{t}', que no esta en el esquema.")

    for tabla, casos in por_tabla().items():
        if not casos:
            problemas.append(f"La tabla '{tabla}' no la toca ningun caso de uso.")

    return problemas


def conteo():
    return {
        "casos": len(todos()),
        "modulos": len(MODULOS),
        "generales": len(GENERAL),
        "tablas": len(TABLAS),
        "inclusiones": sum(len(m[5]) for m in MODULOS),
        "extensiones": sum(len(m[6]) for m in MODULOS),
    }


if __name__ == "__main__":
    c = conteo()
    print(f"Casos de uso: {c['casos']} en {c['modulos']} diagramas de modulo")
    print(f"Relaciones: {c['inclusiones']} inclusiones y {c['extensiones']} extensiones")
    print(f"Diagrama general: {c['generales']} casos")
    print()
    for tabla, casos in por_tabla().items():
        print(f"  {tabla:14} {len(casos):>2} casos  {', '.join(casos)}")
    print()
    fallos = comprobar()
    if fallos:
        print(f"PROBLEMAS ({len(fallos)}):")
        for f in fallos:
            print(f"  - {f}")
        raise SystemExit(1)
    print("Sin problemas: todos los requisitos tienen caso de uso y las 11 tablas estan "
          "cubiertas.")
