# -*- coding: utf-8 -*-
"""
Catálogo de requisitos de MediApp, **fuente única**.

De aquí salen el anexo E1 (T4), el punto 4.4 y el 4.5 del documento de grado (T12) y la
diapositiva de requisitos (P2). Tenerlo en un solo módulo no es prolijidad, porque son tres
piezas que hablan de lo mismo y, cuando cada una mantiene su propia lista, basta con un
requisito agregado en una para que las otras dos queden describiendo un sistema que ya no
existe.

**Los puntajes son la única fuente de la prioridad.** Cada requisito trae su valor de negocio y
su urgencia, y de ahí salen tanto la columna «Prioridad» como la clasificación MoSCoW que pide
la observación O04. Si estuvieran escritas por separado, el día que una cambie el documento se
contradiría a sí mismo.

Nada de lo que está aquí es una intención. Se levantó recorriendo las 53 rutas de `index.py`,
las 11 tablas de `BASE_DE_DATOS.md` y la matriz de permisos de `CLAUDE.md`, y no hay requisito
que no corresponda a algo que el sistema haga hoy. Lo que se decidió dejar fuera está en
`FUERA_DE_ALCANCE`, que es la columna «Won't have» de la matriz.

Este módulo no genera ningún documento, solo datos.
"""

# --- Cómo se calcula la prioridad ----------------------------------------------

def puntaje(valor, urgencia):
    """El valor de negocio pesa más que la urgencia, y lo importante manda sobre lo afanado."""
    return round(valor * 0.6 + urgencia * 0.4, 1)


def prioridad(valor, urgencia):
    p = puntaje(valor, urgencia)
    if p >= 4.6:
        return "Crítica"
    if p >= 4.0:
        return "Alta"
    if p >= 3.0:
        return "Media"
    return "Baja"


def moscow(valor, urgencia):
    """Traduce el puntaje a la categoría MoSCoW (O04).

    La correspondencia es directa y por eso la matriz queda justificada en lugar de
    declarada, ya que ningún requisito cayó en su categoría por gusto del equipo sino por el
    puntaje que se le asignó al valorarlo. La cuarta categoría, «Won't have», no se deriva de
    ningún puntaje porque agrupa lo que se decidió no construir, y vive en
    `FUERA_DE_ALCANCE`.
    """
    p = puntaje(valor, urgencia)
    if p >= 4.6:
        return "Must have"
    if p >= 4.0:
        return "Should have"
    return "Could have"


# --- Los requisitos funcionales -------------------------------------------------
# (código, requisito, descripción, actor, valor de negocio, urgencia)

RF1 = [
    ("RF 1.1", "Autenticación por credenciales",
     "Permitir el ingreso al sistema presentando un nombre de usuario y una contraseña, y "
     "rechazar el acceso cuando alguno de los dos no corresponda.", "Usuario del sistema", 5, 5),
    ("RF 1.2", "Redirección automática según el rol",
     "Determinar el rol del usuario en el momento de validar sus credenciales y llevarlo "
     "directamente al panel que le corresponde, sin pedirle que elija su perfil.",
     "Sistema", 5, 5),
    ("RF 1.3", "Almacenamiento de la contraseña mediante hash",
     "Guardar la contraseña únicamente como hash producido por una función de derivación de "
     "clave, de modo que en la base no exista ninguna contraseña legible.", "Sistema", 5, 5),
    ("RF 1.4", "Registro público del paciente",
     "Permitir que una persona cree su propia cuenta indicando sus datos personales y sus "
     "credenciales, quedando registrada a la vez como usuario y como paciente.",
     "Paciente", 4, 4),
    ("RF 1.5", "Bloqueo del registro duplicado",
     "Rechazar el registro cuando el nombre de usuario ya esté en uso o cuando el número de "
     "documento ya pertenezca a un paciente registrado.", "Sistema", 5, 4),
    ("RF 1.6", "Protección de las rutas por sesión",
     "Exigir una sesión iniciada en toda pantalla del sistema salvo el ingreso y el registro "
     "público, redirigiendo al ingreso a quien no la tenga.", "Sistema", 5, 5),
    ("RF 1.7", "Cierre de sesión",
     "Terminar la sesión por decisión del usuario, dejando la aplicación sin acceso hasta un "
     "nuevo ingreso.", "Usuario del sistema", 4, 3),
    ("RF 1.8", "Menú diferenciado por rol",
     "Presentar en el panel principal únicamente los módulos que el rol del usuario tiene "
     "permitido, de modo que nadie vea la entrada a una pantalla que no puede abrir.",
     "Sistema", 4, 4),
    ("RF 1.9", "Llave de firma de la sesión fuera del código",
     "Leer la llave con que se firma la cookie de sesión desde el entorno o desde un archivo "
     "local generado automáticamente, nunca desde el código fuente.", "Sistema", 5, 4),
]

RF2 = [
    ("RF 2.1", "Registro de usuario",
     "Crear una cuenta indicando nombre de usuario, contraseña y rol asignado entre "
     "administrador, médico y paciente.", "Administrador", 5, 5),
    ("RF 2.2", "Listado de usuarios",
     "Consultar las cuentas del sistema con búsqueda por nombre de usuario y filtro por rol y "
     "por estado, en un listado paginado.", "Administrador", 4, 4),
    ("RF 2.3", "Edición del usuario",
     "Modificar el nombre de usuario y el rol asignado a una cuenta existente.",
     "Administrador", 4, 4),
    ("RF 2.4", "Cambio de contraseña",
     "Reemplazar la contraseña de una cuenta, guardando siempre el nuevo valor como hash y "
     "conservando la anterior si el campo se deja vacío.", "Administrador", 4, 4),
    ("RF 2.5", "Desactivación del usuario",
     "Dar de baja una cuenta cambiando su estado a inactivo, sin borrar la fila, de modo que "
     "los registros que la referencian conserven su trazabilidad.", "Administrador", 5, 4),
    ("RF 2.6", "Reactivación del usuario",
     "Devolver al estado activo una cuenta previamente desactivada.", "Administrador", 4, 3),
    ("RF 2.7", "Unicidad del nombre de usuario",
     "Impedir que dos cuentas compartan el mismo nombre de usuario, tanto al crearlas como al "
     "editarlas.", "Sistema", 5, 4),
    ("RF 2.8", "Consulta del detalle de un usuario",
     "Consultar los datos de una cuenta en una ventana de detalle sin salir del listado.",
     "Administrador", 3, 3),
]

RF3 = [
    ("RF 3.1", "Registro del médico",
     "Dar de alta un médico con su nombre, documento, especialidad, teléfono y correo, "
     "vinculado a la cuenta de usuario con la que ingresará al sistema.", "Administrador", 5, 5),
    ("RF 3.2", "Listado de médicos",
     "Consultar los médicos registrados con búsqueda por nombre o documento y filtro por "
     "especialidad y por estado.", "Administrador", 4, 4),
    ("RF 3.3", "Edición del médico",
     "Modificar los datos del médico y la especialidad a la que pertenece.",
     "Administrador", 4, 4),
    ("RF 3.4", "Desactivación del médico",
     "Dar de baja un médico cambiando su estado a inactivo, de modo que deje de ofrecerse al "
     "agendar sin que desaparezcan las citas ni las historias que ya firmó.",
     "Administrador", 5, 5),
    ("RF 3.5", "Reactivación del médico",
     "Devolver al estado activo un médico previamente desactivado, con lo que vuelve a "
     "ofrecerse al agendar.", "Administrador", 4, 3),
    ("RF 3.6", "Control del acceso del médico",
     "Habilitar o suspender el ingreso al sistema de la cuenta de un médico sin desactivar su "
     "ficha ni afectar su agenda.", "Administrador", 4, 3),
    ("RF 3.7", "Unicidad del documento del médico",
     "Impedir que dos médicos se registren con el mismo número de documento.",
     "Sistema", 5, 4),
    ("RF 3.8", "Consulta del detalle de un médico",
     "Consultar la ficha de un médico con su especialidad y su estado en una ventana de "
     "detalle.", "Administrador", 3, 3),
]

RF4 = [
    ("RF 4.1", "Registro del paciente",
     "Dar de alta un paciente con su nombre, tipo y número de documento, fecha de nacimiento, "
     "teléfono, dirección y correo.", "Administrador", 5, 5),
    ("RF 4.2", "Listado de pacientes",
     "Consultar los pacientes registrados con búsqueda por nombre o documento y filtro por "
     "estado, en un listado paginado.", "Administrador", 4, 4),
    ("RF 4.3", "Consulta del directorio de pacientes por el médico",
     "Permitir al médico consultar los pacientes registrados para ubicar a quien atiende, sin "
     "poder crearlos, modificarlos ni darlos de baja.", "Médico", 4, 4),
    ("RF 4.4", "Edición del paciente",
     "Modificar los datos personales y de contacto de un paciente registrado.",
     "Administrador", 4, 4),
    ("RF 4.5", "Desactivación del paciente",
     "Dar de baja un paciente cambiando su estado a inactivo, conservando la fila para que su "
     "historial clínico y sus citas sigan siendo consultables.", "Administrador", 5, 4),
    ("RF 4.6", "Reactivación del paciente",
     "Devolver al estado activo un paciente previamente desactivado.", "Administrador", 4, 3),
    ("RF 4.7", "Validación de la fecha de nacimiento",
     "Rechazar una fecha de nacimiento posterior al día de hoy, tanto en el registro público "
     "como en el que hace el administrador.", "Sistema", 4, 4),
    ("RF 4.8", "Unicidad del documento del paciente",
     "Impedir que dos pacientes se registren con el mismo número de documento.",
     "Sistema", 5, 5),
    ("RF 4.9", "Consulta del perfil propio",
     "Permitir al paciente consultar sus propios datos personales sin poder eliminar su "
     "perfil.", "Paciente", 3, 3),
]

RF5 = [
    ("RF 5.1", "Agendamiento de la cita por el administrador",
     "Registrar una cita indicando el paciente, el médico, la fecha y la hora, y el motivo de "
     "la consulta.", "Administrador", 5, 5),
    ("RF 5.2", "Agendamiento de la cita por el propio paciente",
     "Permitir al paciente reservar su cita desde el calendario de disponibilidad, quedando la "
     "cita agendada de inmediato y sin aprobación previa.", "Paciente", 5, 5),
    ("RF 5.3", "Identidad del solicitante tomada de la sesión",
     "Determinar el paciente de una cita reservada desde el calendario a partir de la sesión "
     "en curso y nunca del formulario enviado, de modo que nadie pueda agendar a nombre de "
     "otro.", "Sistema", 5, 5),
    ("RF 5.4", "Separación mínima entre citas del mismo médico",
     "Rechazar una cita que quede a menos de treinta minutos de otra cita vigente del mismo "
     "médico.", "Sistema", 5, 5),
    ("RF 5.5", "Máximo de una cita por paciente y por día",
     "Rechazar una cita cuando el paciente ya tenga otra cita vigente para ese mismo día.",
     "Sistema", 5, 5),
    ("RF 5.6", "Reserva atómica del turno",
     "Comprobar la disponibilidad y registrar la cita dentro de una misma transacción con "
     "bloqueo, de modo que dos solicitudes simultáneas sobre el mismo horario no puedan "
     "obtener ambas la cita.", "Sistema", 5, 5),
    ("RF 5.7", "Rechazo de las citas en el pasado",
     "Rechazar el agendamiento y la edición de una cita cuya fecha y hora ya transcurrieron, "
     "comparando la hora y no solamente el día.", "Sistema", 5, 4),
    ("RF 5.8", "Calendario semanal de disponibilidad",
     "Presentar la disponibilidad de un médico por semana, marcando los horarios ocupados sin "
     "revelar qué paciente los ocupa.", "Paciente", 5, 5),
    ("RF 5.9", "Consulta de la agenda propia por el médico",
     "Permitir al médico consultar las citas que le fueron asignadas, en modo de solo lectura "
     "y sin poder crearlas, modificarlas ni eliminarlas.", "Médico", 5, 5),
    ("RF 5.10", "Consulta de las citas propias por el paciente",
     "Permitir al paciente consultar únicamente sus propias citas, con su estado y el médico "
     "que lo atenderá.", "Paciente", 4, 4),
    ("RF 5.11", "Reprogramación de la cita",
     "Modificar la fecha, la hora, el médico o el motivo de una cita ya agendada, incluidas "
     "las que reservó un paciente, revalidando las reglas de conflicto.", "Administrador", 5, 4),
    ("RF 5.12", "Cancelación de la cita propia por el paciente",
     "Permitir al paciente cancelar su propia cita, con lo que el horario vuelve a quedar "
     "disponible, sin que la cita se borre de la base.", "Paciente", 5, 4),
    ("RF 5.13", "Eliminación de la cita",
     "Eliminar una cita del sistema cuando corresponda hacerlo, operación reservada al "
     "administrador.", "Administrador", 3, 3),
    ("RF 5.14", "Listado de citas con filtros",
     "Consultar las citas con búsqueda por paciente o médico y filtro por estado y por fecha, "
     "en un listado paginado.", "Administrador", 4, 4),
]

RF6 = [
    ("RF 6.1", "Creación del registro de historia clínica",
     "Registrar la evolución del paciente con su fecha, su descripción y las observaciones del "
     "médico tratante.", "Médico", 5, 5),
    ("RF 6.2", "Exclusividad del médico sobre la historia clínica",
     "Impedir que el administrador y el paciente creen, modifiquen o eliminen un registro de "
     "historia clínica, aunque envíen la petición directamente.", "Sistema", 5, 5),
    ("RF 6.3", "Autoría tomada de la sesión",
     "Determinar el médico autor de un registro clínico a partir de la sesión en curso y nunca "
     "del formulario enviado.", "Sistema", 5, 5),
    ("RF 6.4", "Edición del registro de historia clínica",
     "Modificar un registro de historia clínica, operación permitida únicamente al médico que "
     "lo creó.", "Médico", 5, 4),
    ("RF 6.5", "Eliminación del registro de historia clínica",
     "Eliminar un registro de historia clínica, operación permitida únicamente al médico que "
     "lo creó.", "Médico", 4, 3),
    ("RF 6.6", "Consulta de la historia clínica por el paciente",
     "Permitir al paciente consultar únicamente su propia historia clínica, sin poder "
     "modificarla.", "Paciente", 5, 4),
    ("RF 6.7", "Consulta de la historia clínica por el administrador",
     "Permitir al administrador consultar las historias clínicas en modo de solo lectura, como "
     "apoyo a la operación.", "Administrador", 3, 3),
    ("RF 6.8", "Validación de la fecha del registro clínico",
     "Rechazar un registro de historia clínica fechado en el futuro.", "Sistema", 4, 4),
]

RF7 = [
    ("RF 7.1", "Registro del diagnóstico posterior a la cita",
     "Registrar el diagnóstico y el plan de tratamiento derivados de una cita atendida.",
     "Médico", 5, 5),
    ("RF 7.2", "Exclusividad del médico sobre el diagnóstico",
     "Impedir que el administrador y el paciente creen o modifiquen una consulta con su "
     "diagnóstico.", "Sistema", 5, 5),
    ("RF 7.3", "Edición de la consulta",
     "Modificar el diagnóstico o el tratamiento de una consulta, operación permitida "
     "únicamente al médico que la registró.", "Médico", 5, 4),
    ("RF 7.4", "Eliminación de la consulta",
     "Eliminar una consulta, operación permitida únicamente al médico que la registró.",
     "Médico", 4, 3),
    ("RF 7.5", "Consulta de los diagnósticos propios por el paciente",
     "Permitir al paciente consultar únicamente los diagnósticos que le corresponden.",
     "Paciente", 5, 4),
    ("RF 7.6", "Autoría del diagnóstico tomada de la sesión",
     "Determinar el médico que registra una consulta a partir de la sesión en curso y nunca "
     "del formulario enviado.", "Sistema", 5, 4),
    ("RF 7.7", "Validación de la fecha de la consulta",
     "Rechazar una consulta fechada en el futuro.", "Sistema", 4, 4),
    ("RF 7.8", "Consulta de los diagnósticos por el administrador",
     "Permitir al administrador consultar las consultas y sus diagnósticos en modo de solo "
     "lectura, como apoyo a la operación.", "Administrador", 3, 3),
]

RF8 = [
    ("RF 8.1", "Emisión de la prescripción",
     "Registrar una receta indicando el medicamento, la dosis, la frecuencia y la duración del "
     "tratamiento.", "Médico", 5, 5),
    ("RF 8.2", "Exclusividad del médico sobre la prescripción",
     "Impedir que el administrador y el paciente emitan, modifiquen o eliminen una receta.",
     "Sistema", 5, 5),
    ("RF 8.3", "Selección del medicamento desde el catálogo",
     "Ofrecer al médico los medicamentos vigentes del catálogo al momento de recetar, sin "
     "incluir los descontinuados.", "Médico", 4, 4),
    ("RF 8.4", "Edición de la prescripción",
     "Modificar una receta, operación permitida únicamente al médico dueño de la consulta "
     "asociada.", "Médico", 4, 4),
    ("RF 8.5", "Eliminación de la prescripción",
     "Eliminar una receta, operación permitida únicamente al médico dueño de la consulta "
     "asociada.", "Médico", 4, 3),
    ("RF 8.6", "Consulta de las prescripciones propias por el paciente",
     "Permitir al paciente consultar únicamente las recetas que le fueron emitidas.",
     "Paciente", 5, 4),
    ("RF 8.7", "Validación de la dosis y la duración",
     "Rechazar una receta con una duración o una cantidad menor o igual que cero.",
     "Sistema", 4, 4),
    ("RF 8.8", "Consulta de las prescripciones por el administrador",
     "Permitir al administrador consultar las recetas emitidas en modo de solo lectura, como "
     "apoyo a la operación.", "Administrador", 3, 3),
]

RF9 = [
    ("RF 9.1", "Solicitud del examen de laboratorio",
     "Registrar la solicitud de un examen para un paciente, indicando el tipo de examen y la "
     "fecha, sin los campos de resultado.", "Médico", 5, 4),
    ("RF 9.2", "Carga del resultado del examen",
     "Registrar el resultado de un examen ya solicitado, operación reservada al "
     "administrador, que es quien opera el laboratorio.", "Administrador", 5, 5),
    ("RF 9.3", "Separación de los campos por rol",
     "Exponer campos distintos según quien abra la edición de un examen, de modo que el médico "
     "corrija su solicitud y el administrador cargue el resultado, rechazando el intento de "
     "cruzar ese límite aunque la petición se envíe directamente.", "Sistema", 5, 5),
    ("RF 9.4", "Consulta de los exámenes propios por el paciente",
     "Permitir al paciente consultar únicamente los exámenes que le corresponden, con su "
     "resultado cuando ya esté cargado.", "Paciente", 4, 4),
    ("RF 9.5", "Consulta de los exámenes solicitados por el médico",
     "Permitir al médico consultar los exámenes que él solicitó y su resultado.",
     "Médico", 4, 4),
    ("RF 9.6", "Eliminación del examen",
     "Eliminar un examen del sistema, operación reservada al administrador.",
     "Administrador", 3, 3),
    ("RF 9.7", "Validación de la fecha de la solicitud",
     "Rechazar una solicitud de examen fechada en el futuro.", "Sistema", 4, 3),
]

RF10 = [
    ("RF 10.1", "Registro de la especialidad",
     "Dar de alta una especialidad médica con su nombre y su descripción.",
     "Administrador", 4, 4),
    ("RF 10.2", "Edición de la especialidad",
     "Modificar el nombre o la descripción de una especialidad registrada.",
     "Administrador", 3, 3),
    ("RF 10.3", "Eliminación protegida de la especialidad",
     "Impedir la eliminación de una especialidad que tenga médicos asociados, para no dejar "
     "fichas huérfanas.", "Sistema", 4, 4),
    ("RF 10.4", "Registro del medicamento",
     "Dar de alta un medicamento con su nombre, su presentación y su descripción.",
     "Administrador", 4, 4),
    ("RF 10.5", "Edición del medicamento",
     "Modificar los datos de un medicamento del catálogo.", "Administrador", 3, 3),
    ("RF 10.6", "Descontinuación del medicamento",
     "Retirar un medicamento de la oferta cambiando su estado a descontinuado, de modo que "
     "deje de ofrecerse al recetar pero las recetas que ya lo usaron lo sigan mostrando.",
     "Administrador", 4, 4),
    ("RF 10.7", "Reactivación del medicamento",
     "Devolver a la oferta un medicamento previamente descontinuado.", "Administrador", 3, 2),
    ("RF 10.8", "Reserva de los catálogos al administrador",
     "Impedir que el médico y el paciente abran las pantallas de catálogo o consulten su "
     "contenido por la interfaz de detalle.", "Sistema", 4, 4),
]

# (código, nombre, alcance, por qué importa, requisitos)

MODULOS = [
    ("RF 1", "Autenticación y sesión",
     "Controla quién entra al sistema, con qué credenciales y a qué panel llega, e incluye el "
     "registro público con el que un paciente crea su propia cuenta.",
     "Es la puerta del sistema y de él dependen los otros nueve módulos, porque toda regla de "
     "permiso se resuelve leyendo el rol que quedó guardado en la sesión. La redirección "
     "automática por rol responde a un requisito expreso de la sustentación, ya que pedirle al "
     "usuario que elija su perfil sería dejar que un paciente escoja entrar como médico.", RF1),
    ("RF 2", "Gestión de usuarios",
     "Administra las cuentas de acceso del sistema, con su rol asignado y su estado.",
     "Es donde se decide de qué es capaz cada persona, porque el rol asignado aquí es el que "
     "después leen todos los controles de acceso. Las cuentas se dan de baja y no se borran, "
     "pues una cuenta eliminada dejaría sin autor conocido a las historias clínicas y a las "
     "recetas que firmó.", RF2),
    ("RF 3", "Gestión de médicos",
     "Mantiene la ficha profesional de cada médico, su especialidad, su vínculo con la cuenta "
     "con la que ingresa y su disponibilidad para ser agendado.",
     "Un médico dado de baja deja de ofrecerse al agendar pero conserva todo lo que firmó, que "
     "es la razón por la que la baja es lógica y no un borrado. El control de acceso separado "
     "de la ficha permite suspender el ingreso de un profesional sin sacarlo de la agenda ni "
     "romper las citas que ya tenía.", RF3),
    ("RF 4", "Gestión de pacientes",
     "Mantiene los datos personales y de contacto de las personas que reciben atención, "
     "vinculados a la cuenta con la que consultan lo suyo.",
     "El paciente es la entidad que más referencias recibe, porque de él cuelgan las citas, "
     "las historias, las consultas, las recetas y los exámenes. Por eso su baja es lógica y "
     "por eso el propio paciente no puede eliminar su perfil, ya que hacerlo dejaría su "
     "historia clínica sin titular.", RF4),
    ("RF 5", "Agendamiento de citas",
     "Reúne la reserva, la reprogramación, la cancelación y la consulta de las citas, junto "
     "con el calendario de disponibilidad desde el que el paciente reserva.",
     "Es el núcleo del sistema y el que sostiene el primer objetivo específico. Sus requisitos "
     "no describen solamente cómo se crea una cita, sino las condiciones que la hacen válida, "
     "que son la separación de treinta minutos entre citas del mismo médico, el máximo de una "
     "cita por paciente y por día, el rechazo de lo que ya pasó y la reserva atómica que "
     "impide que dos personas obtengan el mismo turno.", RF5),
    ("RF 6", "Historia clínica",
     "Registra la evolución del paciente a lo largo del tiempo, bajo la responsabilidad "
     "exclusiva del médico tratante.",
     "Aquí está la restricción que le da carácter al proyecto, porque el administrador tiene "
     "control total del sistema salvo sobre este módulo. La autoría se toma de la sesión y no "
     "del formulario, de manera que un registro clínico siempre queda a nombre de quien lo "
     "escribió y no de quien diga el campo oculto de la petición.", RF6),
    ("RF 7", "Consultas y diagnósticos",
     "Registra el diagnóstico y el plan de tratamiento que resultan de una cita atendida.",
     "Es la pieza de la que cuelgan las recetas, porque una prescripción se emite siempre "
     "sobre una consulta. Comparte con la historia clínica la regla de exclusividad, ya que un "
     "diagnóstico que pudiera escribir alguien distinto del médico dejaría de ser un "
     "diagnóstico, y comparte también la autoría tomada de la sesión, que se determina a "
     "partir del médico que tiene abierta la sesión y nunca del formulario enviado.", RF7),
    ("RF 8", "Prescripciones",
     "Cubre la emisión y la gestión de las recetas, con el medicamento, la dosis, la "
     "frecuencia y la duración del tratamiento.",
     "Cierra el acto clínico y es el tercero de los módulos reservados al médico. El "
     "medicamento se elige del catálogo y no se escribe libremente, de modo que una receta "
     "siempre apunte a un producto existente, y el catálogo ofrece solo lo vigente mientras "
     "las recetas antiguas siguen mostrando lo que en su momento se recetó.", RF8),
    ("RF 9", "Exámenes de laboratorio",
     "Cubre la solicitud del examen por parte del médico y la carga de su resultado por parte "
     "del laboratorio.",
     "Es el único módulo con los permisos partidos por campo dentro de una misma pantalla, "
     "porque solicitar y resolver son dos actos de dos personas distintas sobre una misma "
     "fila. El límite se comprueba en el servidor y no ocultando campos en el formulario, ya "
     "que un campo oculto se vuelve a mostrar desde el navegador.", RF9),
    ("RF 10", "Catálogos",
     "Mantiene las especialidades médicas y los medicamentos que el resto del sistema "
     "referencia.",
     "Se agrupan aparte del trabajo diario porque su frecuencia de uso es otra, pues son datos "
     "que se ajustan de vez en cuando y que después alimentan formularios que se usan todos "
     "los días. Ninguno de los dos se borra sin más, ya que la especialidad con médicos "
     "asociados no se elimina y el medicamento se descontinúa en lugar de desaparecer.", RF10),
]


# --- Requisitos no funcionales --------------------------------------------------
# (código, categoría, requisito, verificación)

RNF = [
    ("RNF 01", "Seguridad",
     "Las contraseñas deben almacenarse mediante una función de derivación de clave con "
     "endurecimiento de memoria, y nunca en texto legible.",
     "Inspección de la tabla de usuarios, en la que ninguna contraseña debe poder leerse."),
    ("RNF 02", "Seguridad",
     "Toda ruta del sistema, salvo el ingreso y el registro público, debe exigir una sesión "
     "iniciada.",
     "Prueba automatizada que solicita cada ruta sin sesión y espera la redirección al "
     "ingreso."),
    ("RNF 03", "Seguridad",
     "El rol debe comprobarse en el servidor en cada operación y no únicamente ocultando "
     "opciones en la interfaz.",
     "Pruebas que envían la petición directamente con una sesión del rol equivocado y esperan "
     "el rechazo."),
    ("RNF 04", "Seguridad",
     "La autoría de un registro clínico y la identidad de quien reserva una cita deben tomarse "
     "de la sesión y nunca de los datos enviados por el formulario.",
     "Prueba que envía el identificador de otra persona en la petición y comprueba que el "
     "registro queda a nombre de quien tiene la sesión."),
    ("RNF 05", "Seguridad",
     "Un usuario solo debe poder consultar los registros que le pertenecen, incluso cuando "
     "solicite el identificador de un registro ajeno.",
     "Pruebas de aislamiento sobre la interfaz de detalle con el identificador de otro "
     "paciente."),
    ("RNF 06", "Seguridad",
     "La llave con la que se firma la sesión no debe estar escrita en el código fuente ni "
     "versionarse en el repositorio.",
     "Revisión del repositorio, en el que la llave debe leerse del entorno o de un archivo "
     "excluido del control de versiones."),
    ("RNF 07", "Seguridad",
     "Toda consulta a la base debe enviarse con parámetros y nunca armando la sentencia por "
     "concatenación de texto.",
     "Revisión del código de acceso a datos."),
    ("RNF 08", "Fiabilidad",
     "Dos solicitudes simultáneas sobre el mismo horario de un médico deben resolverse en una "
     "sola cita agendada y un rechazo.",
     "Prueba de concurrencia con dos peticiones en paralelo sobre el mismo turno."),
    ("RNF 09", "Fiabilidad",
     "Toda operación de escritura debe confirmarse o deshacerse por completo, sin dejar "
     "registros a medias cuando falle un paso intermedio.",
     "Prueba que interrumpe el registro de un paciente y comprueba que no quedó la cuenta "
     "creada."),
    ("RNF 10", "Fiabilidad",
     "Cada petición debe atenderse con su propia conexión a la base, tomada de un conjunto "
     "reutilizable, para que dos peticiones simultáneas no compartan el mismo canal.",
     "Revisión del módulo de conexión y prueba con peticiones concurrentes."),
    ("RNF 11", "Fiabilidad",
     "Ninguna baja de una persona ni de un medicamento debe eliminar la fila de la base "
     "mientras existan registros que la referencien.",
     "Prueba que da de baja a un médico y comprueba que sus historias clínicas siguen "
     "consultables."),
    ("RNF 12", "Usabilidad",
     "El sistema debe informar el motivo exacto del rechazo cuando una validación falle, en "
     "lenguaje entendible y sin mostrar mensajes técnicos de la base.",
     "Revisión de los mensajes de las validaciones de citas, fechas y duplicados."),
    ("RNF 13", "Usabilidad",
     "El calendario de disponibilidad debe mostrar los horarios ocupados de un médico sin "
     "revelar la identidad de quien los ocupa.",
     "Consulta del calendario con una sesión de paciente."),
    ("RNF 14", "Usabilidad",
     "El panel de cada rol debe presentar únicamente los módulos que ese rol puede abrir.",
     "Ingreso con los tres roles y comparación del menú con la matriz de permisos."),
    ("RNF 15", "Usabilidad",
     "El sistema debe operar en español y presentar las fechas en el huso horario de Colombia.",
     "Revisión de las pantallas y de la conversión de fechas."),
    ("RNF 16", "Rendimiento",
     "Los listados deben paginarse en el servidor y no cargar la totalidad de los registros en "
     "una sola consulta.",
     "Revisión de las consultas de los listados y de su ordenamiento con desempate."),
    ("RNF 17", "Rendimiento",
     "La espera por un turno disputado no debe dejar la petición colgada de forma indefinida, "
     "sino resolverse en pocos segundos con un mensaje entendible.",
     "Prueba de concurrencia con la espera de bloqueo reducida."),
    ("RNF 18", "Mantenibilidad",
     "Las reglas críticas del sistema deben estar cubiertas por pruebas automatizadas que "
     "puedan ejecutarse con una sola orden.",
     "Ejecución de la batería de pruebas del proyecto."),
    ("RNF 19", "Mantenibilidad",
     "Todo cambio del esquema de la base debe quedar registrado como una migración numerada y "
     "aplicable en orden.",
     "Revisión de la carpeta de migraciones."),
    ("RNF 20", "Mantenibilidad",
     "Las reglas de fecha y las validaciones reutilizables deben vivir en módulos propios y no "
     "repetirse en cada ruta.",
     "Revisión de los módulos de validación."),
    ("RNF 21", "Mantenibilidad",
     "Las credenciales de la base y la llave de la sesión deben leerse de la configuración del "
     "entorno.",
     "Revisión del archivo de configuración y del repositorio."),
    ("RNF 22", "Portabilidad",
     "El sistema debe usarse desde cualquier sistema operativo mediante un navegador, sin "
     "instalación en el equipo del usuario.",
     "Acceso desde equipos con distintos sistemas operativos."),
    ("RNF 23", "Portabilidad",
     "El sistema debe instalarse sobre una pila de servidor libre y de uso común, sin "
     "componentes de licencia propietaria.",
     "Instalación completa siguiendo las instrucciones del proyecto."),
    ("RNF 24", "Escalabilidad",
     "Deben poder registrarse nuevas especialidades, medicamentos, médicos y sedes de atención "
     "sin modificar el código.",
     "Alta de una especialidad y de un médico nuevos por la interfaz."),
]


# --- Lo que se decidió no construir, que es la columna «Won't have» de MoSCoW ----
# (qué, por qué quedó fuera)

FUERA_DE_ALCANCE = [
    ("Notificación de la cita por correo o por mensaje de texto",
     "Exige un servicio de envío contratado y una política de reintentos que el alcance "
     "académico del proyecto no cubre, y su ausencia no impide agendar, reprogramar ni "
     "cancelar."),
    ("Teleconsulta o videollamada dentro del sistema",
     "Pertenece a la prestación del servicio y no a su agendamiento, que es lo que el objetivo "
     "general delimita."),
    ("Facturación, cobro y convenios con aseguradoras",
     "Es un dominio completo por sí mismo, con su propia normativa, y agregarlo convertiría el "
     "proyecto en otro distinto del que se formuló."),
    ("Firma digital certificada de la historia clínica",
     "Requiere una autoridad certificadora y un proceso de emisión de certificados que exceden "
     "la infraestructura disponible."),
    ("Cifrado de la información en reposo y en tránsito",
     "Depende de la infraestructura de despliegue y no del programa, razón por la cual el "
     "tercer objetivo específico se acotó de forma expresa al control de acceso por roles."),
    ("Respaldo automático y política de retención de la información",
     "Es una función de la administración del servidor de base de datos y no del sistema, y "
     "prometerla sin tenerla dejaría al documento afirmando algo que no puede demostrar."),
    ("Aplicación móvil nativa",
     "La interfaz responde desde el navegador del teléfono, de modo que una aplicación aparte "
     "duplicaría el esfuerzo sin agregar una capacidad nueva."),
    ("Interfaz de integración con sistemas externos",
     "No hay hoy ningún sistema con el que integrarse, y construir una interfaz sin consumidor "
     "sería trabajo sin destinatario."),
]


# --- Trazabilidad con los objetivos específicos ---------------------------------
# (objetivo, qué del sistema lo cumple, requisitos, pantallas)

TRAZABILIDAD = [
    ("OE 1", "Programación de la atención médica por el administrador y por el paciente",
     "RF 5, RF 3.4, RF 4.1",
     "Citas, Agendar cita y Calendario de disponibilidad"),
    ("OE 2", "Acto clínico bajo responsabilidad exclusiva del médico tratante",
     "RF 6, RF 7, RF 8, RF 9.1",
     "Historia clínica, Consultas, Recetas y Exámenes"),
    ("OE 3", "Confidencialidad mediante control de acceso basado en roles",
     "RF 1, RF 2, RF 6.2, RF 7.2, RF 8.2, RF 9.3, RF 10.8",
     "Ingreso, Usuarios y todos los listados con filtro por rol"),
]


# --- Actores del sistema --------------------------------------------------------

USUARIOS = [
    ("Administrador", "Gestiona la operación completa, que son los usuarios, los médicos, los "
     "pacientes, los catálogos, la agenda y los resultados de laboratorio. Su única "
     "restricción es que no crea ni modifica historias clínicas, consultas ni recetas, aunque "
     "sí puede consultarlas."),
    ("Médico", "Dueño exclusivo del acto clínico, es decir de la historia clínica, del "
     "diagnóstico y de la prescripción, y solicita los exámenes de laboratorio. Consulta su "
     "agenda pero no la modifica."),
    ("Paciente", "Consulta lo que le pertenece, que son sus citas, su historia clínica, sus "
     "diagnósticos, sus recetas y sus exámenes. Tiene dos capacidades de escritura, que son "
     "reservar su propia cita desde el calendario y cancelarla, y no puede eliminar su "
     "perfil."),
    ("Sistema", "Actor no humano al que se atribuyen las reglas que se ejecutan sin que nadie "
     "las solicite, como la validación de los conflictos de agenda, la reserva atómica del "
     "turno y la comprobación del rol en cada petición."),
]

ENTORNO = [
    ("Servidor de aplicación", "Python 3 con el marco de trabajo Flask"),
    ("Base de datos", "MySQL o MariaDB, con acceso mediante consultas parametrizadas"),
    ("Conector de base de datos", "mysql-connector-python, con conexiones tomadas de un pool"),
    ("Interfaz web", "Plantillas Jinja2 con Bootstrap 5 y JavaScript sin marco de trabajo"),
    ("Seguridad", "werkzeug.security con el algoritmo scrypt y sesiones por cookie firmada"),
    ("Pruebas", "pytest sobre una base de datos de prueba clonada del esquema real"),
    ("Cliente", "Navegador web vigente, sin instalación local"),
]


# --- Utilidades para quien consume el catálogo ----------------------------------

def todos():
    """Los requisitos funcionales en orden, con el módulo al que pertenecen."""
    salida = []
    for _, nombre_modulo, _, _, requisitos in MODULOS:
        for codigo, nombre, descripcion, actor, valor, urgencia in requisitos:
            salida.append((codigo, nombre, nombre_modulo, descripcion, actor, valor, urgencia))
    return salida


def por_codigo(codigo):
    for fila in todos():
        if fila[0] == codigo:
            return fila
    raise KeyError(codigo)


def por_moscow():
    """Los requisitos agrupados en las tres categorías que se derivan del puntaje."""
    grupos = {"Must have": [], "Should have": [], "Could have": []}
    for fila in todos():
        grupos[moscow(fila[5], fila[6])].append(fila)
    return grupos


def conteo():
    """Cifras del catálogo, para no escribirlas a mano en ningún documento."""
    grupos = por_moscow()
    return {
        "funcionales": len(todos()),
        "no_funcionales": len(RNF),
        "modulos": len(MODULOS),
        "fuera_de_alcance": len(FUERA_DE_ALCANCE),
        "must": len(grupos["Must have"]),
        "should": len(grupos["Should have"]),
        "could": len(grupos["Could have"]),
    }


if __name__ == "__main__":
    c = conteo()
    print(f"Requisitos funcionales: {c['funcionales']} en {c['modulos']} modulos")
    print(f"Requisitos no funcionales: {c['no_funcionales']}")
    print(f"MoSCoW  Must {c['must']}  Should {c['should']}  Could {c['could']}  "
          f"Wont {c['fuera_de_alcance']}")
    for codigo, nombre, _modulo, _desc, _actor, valor, urgencia in todos():
        print(f"  {codigo:9} {moscow(valor, urgencia):12} {puntaje(valor, urgencia):>4}  "
              f"{nombre}")
