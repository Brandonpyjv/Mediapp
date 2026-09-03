# -*- coding: utf-8 -*-
"""
E3 — Documentación de los casos de uso de MediApp.

Los casos salen de `casos_de_uso.py`, el mismo catálogo del que se dibujan los diagramas de E2.
Aquí se les agregan los campos de comportamiento, que son las precondiciones, la secuencia
normal, los flujos alternos, las postcondiciones y las excepciones.

**Dos niveles de detalle, a propósito.** Documentar los sesenta casos con ficha completa produce
setenta páginas en las que los casos que deciden si el sistema sirve, esto es, reservar una
cita, validar la agenda y firmar la historia clínica, quedan sepultados entre fichas que repiten
el mismo formulario de un mantenimiento de catálogo. Los dieciocho casos críticos llevan ficha
completa y los cuarenta y dos restantes van en formato breve, con su precondición y su resultado
esperado, que es lo que de ellos hay que verificar.

🔴 **Dos exigencias del evaluador se resuelven aquí.** La primera es la **trazabilidad con el
modelo de datos**, que en cada ficha ocupa una fila propia y al final del documento una matriz
que recorre las once tablas. La segunda es que **en los casos de uso no va código SQL** (O12),
así que las tablas se nombran y nunca se consultan, y `verificar.py` lo comprueba sobre el
documento ya generado.

    python e3_documentacion.py
"""
from pathlib import Path

import casos_de_uso as catalogo
from apa import DocumentoAPA, inicial_minuscula

SALIDA = Path(__file__).resolve().parent.parent / "entregables"
ARCHIVO = SALIDA / "MediApp - Documentacion de Casos de Uso.docx"

# --- Fichas completas: los casos de los que depende que el sistema sirva ---------
# codigo: (precondiciones, secuencia normal, flujos alternos, postcondiciones, excepciones)

DETALLE = {
"CU-01": (
    ["El usuario tiene una cuenta creada en el sistema.",
     "La cuenta se encuentra en estado activo."],
    ["El usuario abre la pantalla de ingreso.",
     "El usuario escribe su nombre de usuario y su contraseña.",
     "El sistema busca la cuenta por su nombre de usuario.",
     "El sistema deriva la contraseña recibida y la compara contra el valor almacenado, sin "
     "descifrar nada, porque lo guardado no es la contraseña sino su hash.",
     "El sistema guarda en la sesión el identificador del usuario y el rol de la cuenta.",
     "El sistema determina el rol y lleva al usuario al tablero que le corresponde."],
    [("La cuenta pertenece a un médico sin ficha profesional vinculada",
      ["El sistema permite el ingreso pero advierte que la cuenta no está vinculada a una "
       "ficha de médico.",
       "El sistema impide abrir las pantallas del acto clínico, porque un registro clínico sin "
       "médico identificable no puede firmarse."])],
    ["La sesión queda abierta con el rol del usuario.",
     "El usuario se encuentra en el tablero de su perfil."],
    ["Si el nombre de usuario no existe o la contraseña no corresponde, el sistema rechaza el "
     "ingreso con un mismo mensaje para los dos casos, de modo que no se revele cuáles nombres "
     "de usuario existen.",
     "Si la cuenta está inactiva, el sistema rechaza el ingreso."],
),
"CU-03": (
    ["La persona no tiene todavía una cuenta en el sistema.",
     "La persona no está registrada como paciente con ese número de documento."],
    ["La persona abre la pantalla de registro desde el ingreso.",
     "La persona diligencia sus datos personales y las credenciales con las que entrará.",
     "El sistema comprueba que todos los campos obligatorios vengan diligenciados.",
     "El sistema valida el formato del correo y que la fecha de nacimiento no sea futura.",
     "El sistema comprueba que el nombre de usuario no esté en uso.",
     "El sistema comprueba que el número de documento no pertenezca a otro paciente.",
     "El sistema crea la cuenta con el rol de paciente y guarda la contraseña como hash.",
     "El sistema crea la ficha del paciente vinculada a esa cuenta, dentro de la misma "
     "transacción.",
     "El sistema confirma el registro e invita a iniciar sesión."],
    [],
    ["La persona queda registrada a la vez como usuario y como paciente.",
     "La cuenta puede iniciar sesión y consultar lo que le pertenece.",
     "La contraseña no queda legible en ninguna parte."],
    ["Si el nombre de usuario ya existe, el sistema rechaza el registro y lo informa, "
     "conservando lo diligenciado para que no haya que escribirlo de nuevo.",
     "Si el número de documento ya pertenece a un paciente, el sistema rechaza el registro.",
     "Si falla la creación de la ficha del paciente después de haber creado la cuenta, el "
     "sistema deshace la transacción completa, de manera que no queden cuentas sin paciente."],
),
"CU-05": (
    ["El usuario dirige una petición a cualquier pantalla u operación del sistema."],
    ["El sistema comprueba que exista una sesión abierta.",
     "El sistema lee el rol guardado en la sesión.",
     "El sistema comprueba que ese rol tenga permitida la operación solicitada.",
     "Si la operación recae sobre un registro concreto, el sistema comprueba además que el "
     "registro pertenezca a quien lo solicita.",
     "El sistema atiende la petición o la rechaza según el resultado de las comprobaciones."],
    [("La pantalla es un listado que varios roles pueden abrir",
      ["El sistema no rechaza la petición, sino que acota lo que devuelve.",
       "El médico recibe únicamente lo suyo, el paciente únicamente lo suyo y el "
       "administrador el conjunto completo."])],
    ["El usuario solo alcanza lo que su rol tiene permitido.",
     "El usuario solo ve los registros que le pertenecen, cuando el módulo es de los "
     "acotados por propiedad."],
    ["Si no hay sesión abierta, el sistema lleva a la pantalla de ingreso.",
     "Si el rol no tiene permitida la operación, el sistema la rechaza y lo informa, aunque la "
     "petición se haya enviado directamente sin pasar por la interfaz.",
     "Si el registro solicitado pertenece a otra persona, el sistema rechaza la consulta en "
     "lugar de devolver el dato."],
),
"CU-10": (
    ["El administrador ha iniciado sesión.",
     "Existe la especialidad a la que se asignará el médico.",
     "Existe la cuenta de usuario con la que el médico ingresará al sistema."],
    ["El administrador abre el módulo de médicos y solicita registrar uno nuevo.",
     "El sistema presenta el formulario con las especialidades y las cuentas disponibles.",
     "El administrador diligencia el nombre, el documento, la especialidad y los datos de "
     "contacto, y elige la cuenta que quedará vinculada.",
     "El sistema valida los datos y comprueba que el documento no esté ya registrado.",
     "El sistema registra la ficha en estado activo y con el acceso habilitado.",
     "El sistema confirma el registro y el médico queda disponible para ser agendado."],
    [],
    ["El médico queda registrado y se ofrece al agendar una cita.",
     "El médico puede ingresar al sistema con la cuenta vinculada y firmar lo que atienda."],
    ["Si el número de documento ya pertenece a otro médico, el sistema rechaza el alta.",
     "Si la cuenta elegida no tiene el rol de médico, el profesional no podrá abrir las "
     "pantallas del acto clínico aunque su ficha exista."],
),
"CU-20": (
    ["El administrador ha iniciado sesión.",
     "Existen el paciente y el médico, ambos en estado activo."],
    ["El administrador abre el módulo de citas y solicita agendar una nueva.",
     "El sistema presenta el formulario con los pacientes y los médicos activos.",
     "El administrador elige el paciente, el médico, la fecha, la hora y el motivo.",
     "El sistema comprueba que la fecha y la hora no hayan transcurrido.",
     "El sistema valida las reglas de la agenda dentro de una transacción con bloqueo.",
     "El sistema registra la cita en estado agendada y confirma la operación."],
    [("El paciente elegido está inactivo",
      ["El sistema no lo ofrece en el formulario, salvo que ya sea el paciente de la cita que "
       "se está editando, para no perder el vínculo de una cita existente."])],
    ["La cita queda agendada y aparece en la agenda del médico y en la del paciente.",
     "El horario deja de estar disponible para ese médico durante la franja de separación."],
    ["Si el paciente ya tiene una cita ese día, el sistema rechaza el agendamiento y lo "
     "informa.",
     "Si el médico tiene otra cita a menos de la separación mínima, el sistema lo rechaza y "
     "pide elegir otro horario.",
     "Si la fecha y la hora ya transcurrieron, el sistema rechaza el agendamiento.",
     "Si otra petición tiene tomado el turno en ese instante, el sistema espera unos segundos "
     "y, de no liberarse, informa que el horario está siendo disputado."],
),
"CU-21": (
    ["El administrador ha iniciado sesión.",
     "La cita existe, no está cancelada y su fecha y hora no han transcurrido."],
    ["El administrador abre la cita que desea reprogramar.",
     "El sistema presenta los datos actuales de la cita.",
     "El administrador cambia la fecha, la hora, el médico o el motivo.",
     "El sistema vuelve a comprobar que la nueva fecha y hora no hayan transcurrido.",
     "El sistema valida las reglas de la agenda sobre los datos nuevos, excluyendo de la "
     "comprobación a la propia cita que se está modificando.",
     "El sistema guarda los cambios y confirma la operación."],
    [("La cita la había reservado el propio paciente",
      ["El procedimiento es el mismo, porque el administrador conserva el control de la agenda "
       "a posteriori y puede reprogramar cualquier cita, sin importar quién la haya "
       "solicitado."])],
    ["La cita queda con los datos nuevos y sigue en estado agendada.",
     "El horario anterior vuelve a estar disponible y el nuevo queda ocupado."],
    ["Si la cita ya está cancelada, el sistema no permite modificarla.",
     "Si la cita ya transcurrió, el sistema no permite modificarla, comparando la hora y no "
     "solamente el día.",
     "Si los datos nuevos chocan con otra cita, el sistema rechaza el cambio y conserva la "
     "cita como estaba."],
),
"CU-24": (
    ["El paciente ha iniciado sesión.",
     "El paciente está consultando el calendario de disponibilidad de un médico.",
     "El horario elegido aparece libre en el calendario."],
    ["El paciente elige un horario libre del calendario y solicita reservarlo.",
     "El sistema toma el identificador del paciente de la sesión en curso y descarta cualquier "
     "paciente que venga en la petición.",
     "El sistema comprueba que la fecha y la hora no hayan transcurrido.",
     "El sistema valida las reglas de la agenda dentro de una transacción con bloqueo.",
     "El sistema registra la cita en estado agendada, sin ninguna aprobación previa.",
     "El sistema confirma la reserva al paciente."],
    [("Dos pacientes piden el mismo horario a la vez",
      ["El primero en obtener el bloqueo completa su reserva.",
       "El segundo encuentra el horario ya tomado al levantarse el bloqueo y recibe el rechazo "
       "con el motivo."])],
    ["La cita queda agendada a nombre de quien la solicitó.",
     "El horario deja de aparecer libre en el calendario de ese médico."],
    ["Si el paciente ya tiene una cita ese día, el sistema rechaza la reserva y lo informa en "
     "segunda persona, porque la está pidiendo para sí mismo.",
     "Si el horario ya fue tomado, el sistema rechaza la reserva y pide elegir otro.",
     "Si la petición llega con el identificador de otro paciente, el sistema la ignora y "
     "registra la cita a nombre de quien tiene la sesión."],
),
"CU-27": (
    ["El paciente o el administrador ha iniciado sesión.",
     "Existe al menos un médico en estado activo."],
    ["El usuario abre el calendario de disponibilidad.",
     "El usuario elige el médico y la semana que desea consultar.",
     "El sistema reúne las citas vigentes de ese médico en esa semana.",
     "El sistema marca como ocupadas las franjas alcanzadas por la separación mínima.",
     "El sistema presenta la semana indicando qué horarios están libres y cuáles ocupados, sin "
     "revelar la identidad de quien los ocupa."],
    [("La semana consultada ya transcurrió",
      ["El sistema presenta la semana con todas las franjas cerradas, porque no puede "
       "agendarse sobre lo que ya pasó."])],
    ["El usuario conoce los horarios libres de ese médico.",
     "El usuario no obtiene ningún dato de los pacientes que ocupan los demás horarios."],
    ["Si el médico está inactivo, no se ofrece en el selector.",
     "Si una cita se cancela mientras se mira el calendario, su horario vuelve a estar libre en "
     "la siguiente consulta."],
),
"CU-28": (
    ["Se está intentando agendar, reservar o reprogramar una cita.",
     "Se conocen el paciente, el médico y la fecha con su hora."],
    ["El sistema comprueba que la fecha y la hora no hayan transcurrido.",
     "El sistema busca si el paciente tiene otra cita vigente ese mismo día.",
     "El sistema busca si el médico tiene otra cita vigente dentro de la franja de separación "
     "mínima alrededor de la hora pedida.",
     "El sistema descarta de ambas búsquedas las citas canceladas.",
     "El sistema devuelve el motivo del rechazo o autoriza a guardar."],
    [("Se está reprogramando una cita existente",
      ["El sistema excluye de las dos búsquedas a la propia cita que se modifica.",
       "Sin esa exclusión, toda cita chocaría consigo misma y no podría cambiarse el motivo "
       "sin cambiar también la hora."])],
    ["La cita solo llega a guardarse si no rompe ninguna de las tres reglas.",
     "Quien la solicitó recibe el motivo exacto cuando se rechaza."],
    ["Si la fecha recibida no es válida, el sistema rechaza la operación.",
     "Si el paciente ya tiene cita ese día, el sistema devuelve ese motivo.",
     "Si el médico no tiene la separación mínima libre, el sistema devuelve ese motivo."],
),
"CU-29": (
    ["Se ha autorizado el guardado de una cita tras validar las reglas de la agenda."],
    ["El sistema abre una transacción.",
     "El sistema repite las comprobaciones de la agenda tomando un bloqueo sobre las filas "
     "consultadas y sobre los huecos entre ellas.",
     "El bloqueo obliga a leer la última versión confirmada y no la que la transacción venía "
     "viendo, de modo que sí aparece la cita que otra petición acaba de confirmar.",
     "El sistema inserta la cita.",
     "El sistema confirma la transacción, con lo que libera el bloqueo."],
    [("Otra petición tiene tomado el bloqueo",
      ["La petición espera unos segundos a que se libere.",
       "Si se libera a tiempo, vuelve a comprobar y encuentra el horario ocupado, por lo que "
       "rechaza la reserva.",
       "Si no se libera, el sistema traduce la espera agotada a un mensaje que informa que el "
       "horario está siendo disputado."])],
    ["De dos solicitudes simultáneas sobre el mismo horario, una obtiene la cita y la otra un "
     "rechazo.",
     "El bloqueo queda liberado al confirmar o al deshacer la transacción."],
    ["Si la operación falla después de tomar el bloqueo, el sistema deshace la transacción y "
     "libera el bloqueo, de manera que el horario no quede retenido.",
     "El bloqueo recae sobre la agenda de ese médico y la de ese paciente, no sobre la tabla "
     "completa, así que dos reservas para médicos distintos no se estorban."],
),
"CU-30": (
    ["El paciente ha iniciado sesión.",
     "La cita le pertenece, está en estado agendada y su fecha y hora no han transcurrido."],
    ["El paciente abre sus citas y solicita cancelar una.",
     "El sistema comprueba que la cita pertenezca a quien la solicita.",
     "El sistema comprueba que la cita no esté ya cancelada ni haya transcurrido.",
     "El sistema cambia el estado de la cita a cancelada, sin borrarla.",
     "El sistema confirma la cancelación."],
    [],
    ["La cita queda en estado cancelada y deja de contar como cita del día del paciente.",
     "El horario vuelve a aparecer libre en el calendario de ese médico.",
     "La cita permanece en la base como parte del historial."],
    ["Si la cita pertenece a otro paciente, el sistema rechaza la operación.",
     "Si la cita ya transcurrió, el sistema no permite cancelarla.",
     "Si la cita ya estaba cancelada, el sistema no repite la operación."],
),
"CU-31": (
    ["El médico ha iniciado sesión y su cuenta está vinculada a una ficha profesional.",
     "El paciente sobre el que se escribe está registrado."],
    ["El médico abre el módulo de historia clínica y solicita un registro nuevo.",
     "El sistema presenta el formulario con los pacientes registrados.",
     "El médico elige el paciente y escribe la fecha, la descripción de la evolución y sus "
     "observaciones.",
     "El sistema comprueba que la fecha no sea futura.",
     "El sistema toma el identificador del médico de la sesión en curso y no del formulario.",
     "El sistema guarda el registro y confirma la operación."],
    [("La cuenta tiene el rol de médico pero no está vinculada a una ficha profesional",
      ["El sistema no presenta el formulario y advierte que la cuenta debe vincularse antes de "
       "continuar.",
       "Sin ese aviso, el guardado fallaría con un error de base de datos incomprensible, "
       "porque la autoría quedaría vacía."])],
    ["El registro queda incorporado a la historia clínica del paciente.",
     "El registro queda firmado por el médico que lo escribió.",
     "El paciente puede consultarlo y no modificarlo."],
    ["Si la fecha es futura, el sistema rechaza el registro.",
     "Si quien envía la petición no es un médico, el sistema la rechaza aunque venga "
     "directamente y no desde el formulario.",
     "Si la petición trae el identificador de otro médico, el sistema lo ignora y firma el "
     "registro con el de la sesión."],
),
"CU-34": (
    ["Se recibe una petición de crear, modificar o eliminar un registro de historia clínica."],
    ["El sistema comprueba que exista una sesión abierta.",
     "El sistema comprueba que el rol de la sesión sea el de médico.",
     "El sistema comprueba que la cuenta esté vinculada a una ficha profesional.",
     "Si la operación recae sobre un registro existente, el sistema comprueba que lo haya "
     "escrito ese mismo médico.",
     "El sistema atiende la petición o la rechaza."],
    [("La petición proviene del administrador",
      ["El sistema la rechaza, aunque el administrador tenga control total sobre el resto del "
       "sistema.",
       "Es la única restricción del perfil administrativo y es la que da carácter al "
       "proyecto."])],
    ["Solo el médico escribe en la historia clínica.",
     "Solo el médico que creó un registro puede corregirlo o eliminarlo.",
     "El administrador y el paciente conservan la consulta."],
    ["Si el rol no es el de médico, el sistema rechaza la operación y lo informa.",
     "Si el registro fue escrito por otro médico, el sistema rechaza la corrección y el "
     "borrado.",
     "La comprobación se hace en el servidor, de modo que ocultar el botón en la pantalla no "
     "es lo que impide la operación."],
),
"CU-37": (
    ["El médico ha iniciado sesión y su cuenta está vinculada a una ficha profesional.",
     "El paciente atendido está registrado."],
    ["El médico abre el módulo de consultas y solicita registrar una nueva.",
     "El sistema presenta el formulario con los pacientes registrados.",
     "El médico elige el paciente y escribe la fecha, el diagnóstico y el plan de tratamiento.",
     "El sistema comprueba que la fecha no sea futura.",
     "El sistema toma el identificador del médico de la sesión en curso y no del formulario.",
     "El sistema guarda la consulta y confirma la operación."],
    [("Del diagnóstico se derivan medicamentos",
      ["El médico registra después una o varias recetas sobre esta consulta.",
       "Se modela aparte porque una consulta puede no llevar prescripción."])],
    ["El diagnóstico queda registrado a nombre del paciente y firmado por el médico que lo "
     "escribió.",
     "La consulta queda disponible para colgar de ella las prescripciones.",
     "El paciente puede consultarla y no modificarla."],
    ["Si la fecha es futura, el sistema rechaza el registro.",
     "Si quien envía la petición no es un médico, el sistema la rechaza.",
     "Si la petición trae el identificador de otro médico, el sistema lo ignora y firma la "
     "consulta con el de la sesión."],
),
"CU-43": (
    ["El médico ha iniciado sesión y su cuenta está vinculada a una ficha profesional.",
     "Existe la consulta sobre la que se prescribe y la registró ese mismo médico.",
     "Existe al menos un medicamento vigente en el catálogo."],
    ["El médico abre el módulo de recetas y solicita emitir una nueva.",
     "El sistema presenta el formulario con las consultas propias y los medicamentos vigentes.",
     "El médico elige la consulta y el medicamento, e indica la dosis, la frecuencia y la "
     "duración del tratamiento.",
     "El sistema comprueba que la duración y la cantidad sean mayores que cero.",
     "El sistema guarda la receta vinculada a la consulta y al medicamento.",
     "El sistema confirma la emisión."],
    [("El medicamento fue descontinuado después de emitida la receta",
      ["La receta conserva el medicamento y lo sigue mostrando con normalidad.",
       "El medicamento deja de ofrecerse únicamente al emitir recetas nuevas."])],
    ["La receta queda emitida y asociada a la consulta que la motivó.",
     "El paciente puede consultarla con su posología.",
     "El administrador puede consultarla y no modificarla."],
    ["Si la duración o la cantidad son menores o iguales que cero, el sistema rechaza la "
     "receta.",
     "Si la consulta pertenece a otro médico, el sistema rechaza la emisión.",
     "Si quien envía la petición no es un médico, el sistema la rechaza."],
),
"CU-50": (
    ["El médico ha iniciado sesión y su cuenta está vinculada a una ficha profesional.",
     "El paciente para el que se solicita el examen está registrado."],
    ["El médico abre el módulo de exámenes y solicita registrar uno nuevo.",
     "El sistema presenta el formulario únicamente con los campos de la solicitud, sin los del "
     "resultado.",
     "El médico elige el paciente, el tipo de examen y la fecha.",
     "El sistema comprueba que la fecha no sea futura.",
     "El sistema registra la solicitud sin resultado y confirma la operación."],
    [],
    ["El examen queda solicitado y a la espera de que el laboratorio cargue su resultado.",
     "El paciente ve el examen solicitado, todavía sin resultado."],
    ["Si la fecha es futura, el sistema rechaza la solicitud.",
     "Si la petición trae campos de resultado, el sistema los descarta, porque cargar el "
     "resultado no es del médico.",
     "Si quien envía la petición no es un médico, el sistema la rechaza."],
),
"CU-51": (
    ["El administrador ha iniciado sesión.",
     "El examen fue solicitado previamente por un médico."],
    ["El administrador abre el módulo de exámenes y elige el examen solicitado.",
     "El sistema presenta el formulario únicamente con los campos del resultado, dejando la "
     "solicitud en modo de consulta.",
     "El administrador registra el resultado del examen.",
     "El sistema guarda el resultado y confirma la operación."],
    [],
    ["El examen queda con su resultado registrado.",
     "El paciente y el médico solicitante pueden consultar el resultado."],
    ["Si la petición pretende modificar los campos de la solicitud, el sistema los descarta, "
     "porque corregir la solicitud es del médico.",
     "Si el examen no existe, el sistema informa que no hay nada que resolver."],
),
"CU-52": (
    ["Se recibe una petición de modificar un examen."],
    ["El sistema comprueba que exista una sesión abierta.",
     "El sistema lee el rol de la sesión.",
     "Si el rol es el de médico, el sistema habilita los campos de la solicitud y descarta "
     "cualquier campo de resultado que venga en la petición.",
     "Si el rol es el de administrador, el sistema habilita los campos del resultado y descarta "
     "cualquier campo de la solicitud.",
     "El sistema guarda únicamente los campos habilitados para ese rol."],
    [("El médico que intenta corregir no es el que solicitó el examen",
      ["El sistema rechaza la corrección, porque la solicitud pertenece a quien la hizo."])],
    ["Cada rol modifica solo la parte del examen que le corresponde.",
     "Ninguno de los dos puede escribir sobre la parte del otro."],
    ["Si la petición se envía directamente con los campos del otro rol, el sistema los "
     "descarta, de modo que el límite no depende de que la pantalla oculte los campos.",
     "Si el rol es el de paciente, el sistema rechaza la operación completa."],
),
}

# --- Formato breve: precondición y resultado esperado ----------------------------

BREVE = {
"CU-02": ("El usuario acaba de autenticarse correctamente.",
          "Llega al tablero de su rol sin haber elegido perfil."),
"CU-04": ("Hay una sesión abierta.",
          "La sesión termina y el sistema queda sin acceso hasta un nuevo ingreso."),
"CU-06": ("El administrador ha iniciado sesión.",
          "La cuenta queda creada con su rol y su contraseña guardada como hash."),
"CU-07": ("El administrador ha iniciado sesión.",
          "Obtiene el listado paginado de cuentas, con su rol y su estado."),
"CU-08": ("La cuenta existe.",
          "El nombre de usuario, el rol o la contraseña quedan actualizados; si la contraseña "
          "se deja vacía, se conserva la anterior."),
"CU-09": ("La cuenta existe.",
          "La cuenta queda desactivada o reactivada, sin borrarse ni perder lo que firmó."),
"CU-11": ("El administrador ha iniciado sesión.",
          "Obtiene los médicos registrados con su especialidad y su estado."),
"CU-12": ("El médico existe.",
          "Los datos de contacto y la especialidad quedan actualizados."),
"CU-13": ("El médico existe.",
          "El médico deja de ofrecerse al agendar, o vuelve a ofrecerse, conservando sus citas "
          "e historias."),
"CU-14": ("El médico existe y tiene una cuenta vinculada.",
          "El ingreso de esa cuenta queda habilitado o suspendido, sin alterar la agenda."),
"CU-15": ("El administrador ha iniciado sesión.",
          "El paciente queda registrado, con su fecha de nacimiento validada y su documento "
          "sin duplicar."),
"CU-16": ("El administrador o el médico ha iniciado sesión.",
          "Obtiene el directorio de pacientes; el médico solo puede consultarlo."),
"CU-17": ("El paciente existe.",
          "Los datos personales y de contacto quedan actualizados."),
"CU-18": ("El paciente existe.",
          "El paciente queda dado de baja o reactivado, conservando su historial y sus citas."),
"CU-19": ("El paciente ha iniciado sesión.",
          "Consulta sus datos personales, sin opción de eliminar el perfil."),
"CU-22": ("La cita existe y el administrador ha iniciado sesión.",
          "La cita se retira del sistema."),
"CU-23": ("El administrador ha iniciado sesión.",
          "Obtiene el listado paginado de citas, con filtro por estado y por fecha."),
"CU-25": ("El paciente ha iniciado sesión.",
          "Obtiene únicamente sus citas, con su estado y el médico que lo atenderá."),
"CU-26": ("El médico ha iniciado sesión.",
          "Obtiene únicamente las citas que le fueron asignadas, sin poder modificarlas."),
"CU-32": ("El registro clínico existe y lo escribió el médico de la sesión.",
          "El registro queda corregido, conservando su autoría."),
"CU-33": ("El registro clínico existe y lo escribió el médico de la sesión.",
          "El registro se retira de la historia clínica del paciente."),
"CU-35": ("El paciente ha iniciado sesión.",
          "Consulta únicamente su propia historia clínica, sin poder modificarla."),
"CU-36": ("El administrador ha iniciado sesión.",
          "Consulta las historias clínicas en modo de solo lectura."),
"CU-38": ("La consulta existe y la registró el médico de la sesión.",
          "El diagnóstico o el tratamiento quedan corregidos."),
"CU-39": ("La consulta existe y la registró el médico de la sesión.",
          "La consulta se retira del sistema."),
"CU-40": ("Se recibe una petición de escribir sobre una consulta.",
          "Solo se atiende si proviene del médico; el administrador y el paciente quedan "
          "rechazados."),
"CU-41": ("El paciente ha iniciado sesión.",
          "Consulta únicamente sus diagnósticos y su plan de tratamiento."),
"CU-42": ("El administrador ha iniciado sesión.",
          "Consulta las consultas registradas en modo de solo lectura."),
"CU-44": ("El médico está emitiendo o corrigiendo una receta.",
          "El selector ofrece los medicamentos vigentes y deja fuera los descontinuados."),
"CU-45": ("La receta existe y la consulta asociada es del médico de la sesión.",
          "La receta queda corregida en su medicamento o en su posología."),
"CU-46": ("La receta existe y la consulta asociada es del médico de la sesión.",
          "La receta se retira del sistema."),
"CU-47": ("Se recibe una petición de escribir sobre una receta.",
          "Solo se atiende si proviene del médico dueño de la consulta asociada."),
"CU-48": ("El paciente ha iniciado sesión.",
          "Consulta únicamente las recetas que le fueron emitidas, con su posología."),
"CU-49": ("El administrador ha iniciado sesión.",
          "Consulta las recetas emitidas en modo de solo lectura."),
"CU-53": ("El paciente ha iniciado sesión.",
          "Consulta únicamente sus exámenes, con el resultado cuando ya esté cargado."),
"CU-54": ("El médico ha iniciado sesión.",
          "Consulta los exámenes que él solicitó y su resultado."),
"CU-55": ("El examen existe y el administrador ha iniciado sesión.",
          "El examen se retira del sistema."),
"CU-56": ("El administrador ha iniciado sesión.",
          "La especialidad queda registrada o actualizada con su nombre y su descripción."),
"CU-57": ("Se intenta eliminar una especialidad.",
          "El borrado se rechaza si tiene médicos asociados, de modo que ninguna ficha quede "
          "sin especialidad."),
"CU-58": ("El administrador ha iniciado sesión.",
          "El medicamento queda registrado o actualizado en el catálogo."),
"CU-59": ("El medicamento existe.",
          "El medicamento deja de ofrecerse al recetar, o vuelve a ofrecerse, y las recetas "
          "que ya lo usaron lo siguen mostrando."),
"CU-60": ("Se recibe una petición sobre un catálogo.",
          "Solo se atiende si proviene del administrador, tanto en la pantalla como en la "
          "consulta de detalle."),
}


def _vinetas(elementos):
    return "\n".join(f"- {e}" for e in elementos) if elementos else "No aplica."


def _pasos(elementos):
    return "\n".join(f"{i}. {e}" for i, e in enumerate(elementos, start=1))


def _alternos(bloques):
    if not bloques:
        return "No aplica."
    partes = []
    for nombre, pasos in bloques:
        partes.append(f"{nombre}:")
        partes.extend(f"   {i}. {p}" for i, p in enumerate(pasos, start=1))
    return "\n".join(partes)


def construir():
    d = DocumentoAPA()
    d.portada(
        titulo="MEDIAPP",
        subtitulo="Documentación de casos de uso",
        integrantes=["ÁNGEL JESÚS HERNÁNDEZ ARÉVALO",
                     "RICHARD ALBERTO QUIÑONES QUIÑONES"],
        grado="Ficha 3115426\nTecnólogo en Análisis y Desarrollo de Software",
        institucion=["SERVICIO NACIONAL DE APRENDIZAJE (SENA)",
                     "Centro de la Industria, la Empresa y los Servicios (CIES)",
                     "Tecnólogo en Análisis y Desarrollo de Software"],
        ciudad="CÚCUTA, NORTE DE SANTANDER",
        anio=2026,
    )
    d.tabla_contenido()

    _introduccion(d)
    _fichas(d)
    _breves(d)
    _trazabilidad(d)

    SALIDA.mkdir(parents=True, exist_ok=True)
    d.guardar(ARCHIVO)
    return d


def _introduccion(d):
    total = len(catalogo.todos())
    d.titulo("1. Introducción", nivel=1)
    d.parrafo(
        f"Este documento describe el comportamiento de los {total} casos de uso de MediApp. "
        "Mientras el anexo de diagramas muestra quién participa en cada caso y cómo se "
        "relacionan entre sí, aquí se detalla qué debe cumplirse antes de ejecutarlo, qué pasos "
        "recorre, qué ocurre cuando el recorrido se aparta de lo previsto y en qué estado queda "
        "el sistema al terminar."
    )
    d.parrafo(
        "El catálogo de casos es el mismo del anexo de diagramas y del capítulo de diseño del "
        "documento de grado. Los tres se generan de una sola lista, de modo que no puede "
        "ocurrir que el diagrama muestre un caso que la documentación no describe."
    )

    d.titulo("1.1 Dos niveles de detalle", nivel=2)
    d.parrafo(
        f"Los casos se documentan en dos formatos. Los {len(DETALLE)} casos críticos llevan "
        f"ficha completa y los {len(BREVE)} restantes se presentan en formato breve, con su "
        "precondición y su resultado esperado."
    )
    d.parrafo(
        "La distinción responde a una decisión sobre la utilidad del documento y no a una "
        "economía de esfuerzo. Documentar los sesenta casos con ficha completa produce un anexo "
        "en el que los casos que deciden si el sistema sirve, esto es, reservar una cita, "
        "validar la agenda y firmar la historia clínica, quedan sepultados entre fichas que "
        "repiten el mismo formulario de un mantenimiento de catálogo. Un caso como el registro "
        "de una especialidad recorre el camino que recorren todos, porque el usuario abre el "
        "módulo, el sistema presenta lo existente, el usuario registra o modifica, el sistema "
        "valida, guarda y confirma, y de él solo hace falta saber qué debe cumplirse y qué debe "
        "observarse al final."
    )
    d.parrafo(
        "Son críticos los casos que sostienen alguno de los tres objetivos específicos, los que "
        "aplican una regla de negocio propia del centro de salud y los que resuelven una "
        "situación que un sistema descuidado resolvería mal, como dos personas pidiendo el "
        "mismo horario en el mismo instante."
    )

    d.titulo("1.2 Estructura de la ficha", nivel=2)
    d.vinetas([
        ("Módulo", "conjunto funcional al que pertenece el caso."),
        ("Actores", "quién participa. Los casos atribuidos al Sistema se ejecutan como parte "
                    "de otro caso y nadie los inicia por separado."),
        ("Requisitos que cubre", "requisitos funcionales que el caso realiza, según el anexo "
                                 "de especificación."),
        ("Tablas que toca", "tablas del modelo de datos sobre las que opera el caso."),
        ("Descripción", "objetivo que persigue el actor, en una frase."),
        ("Precondiciones", "lo que debe ser cierto antes de ejecutarlo."),
        ("Secuencia normal", "recorrido cuando todo ocurre como se espera."),
        ("Flujos alternos", "variantes que también terminan bien."),
        ("Postcondiciones", "estado en que queda el sistema al terminar."),
        ("Excepciones", "situaciones que impiden completar el caso y cómo responde el "
                        "sistema."),
    ])
    d.parrafo(
        "La fila de tablas responde a una exigencia expresa de los evaluadores del proyecto, "
        "que pidieron que los casos de uso fueran trazables al modelo de datos. Los mismos "
        "evaluadores observaron que en los casos de uso no debe aparecer código, de modo que "
        "las tablas se nombran y en ningún punto de este documento se transcribe una sentencia "
        "de consulta. El capítulo 4 reúne esa trazabilidad en una sola matriz."
    )


def _fichas(d):
    d.titulo("2. Casos de uso críticos", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Las fichas siguen el orden de los módulos. Cada una es autosuficiente y puede leerse "
        "sin haber leído la anterior, que es como se consulta esta clase de documento."
    )

    completo = {c[0]: c for c in catalogo.todos()}
    for indice, codigo in enumerate(DETALLE, start=1):
        _, nombre, modulo, actores, descripcion, rf, tablas = completo[codigo]
        precondiciones, flujo, alternos, postcondiciones, excepciones = DETALLE[codigo]

        d.titulo(f"2.{indice} {codigo}. {nombre}", nivel=2, nueva_pagina=True)
        d.tabla(
            f"Ficha del caso de uso {codigo}, {inicial_minuscula(nombre)}",
            ["CASO DE USO", f"{codigo}. {nombre}"],
            [
                ["Módulo", modulo],
                ["Actores", ", ".join(actores) if actores else
                 "Ninguno. Es un caso incluido que ejecuta el sistema."],
                ["Requisitos que cubre", rf],
                ["Tablas que toca", ", ".join(tablas)],
                ["Descripción", descripcion],
                ["Precondiciones", _vinetas(precondiciones)],
                ["Secuencia normal", _pasos(flujo)],
                ["Flujos alternos", _alternos(alternos)],
                ["Postcondiciones", _vinetas(postcondiciones)],
                ["Excepciones", _vinetas(excepciones)],
            ],
            nota="Elaboración propia.",
            anchos=[3.6, 12.7],
        )


def _breves(d):
    d.titulo("3. Casos de uso complementarios", nivel=1, nueva_pagina=True)
    d.parrafo(
        f"Los {len(BREVE)} casos restantes se presentan agrupados por módulo, con la condición "
        "que debe cumplirse para ejecutarlos y el resultado que debe observarse al terminar. "
        "En su mayoría corresponden a consultas y a mantenimiento de catálogos, cuyo recorrido "
        "es el mismo en todos los casos."
    )
    d.parrafo(
        "El formato breve no significa que estos casos estén menos verificados. La precondición "
        "y el resultado esperado son justamente los dos datos que necesita una prueba, así que "
        "cada fila de estas tablas puede leerse como el enunciado de un caso de prueba."
    )

    for _codigo_dcu, nombre_modulo, _izq, _der, casos, *_ in catalogo.MODULOS:
        suyos = [(c, n, a, tab) for c, n, a, _desc, _rf, tab in casos if c in BREVE]
        if not suyos:
            continue
        d.tabla(
            f"Casos complementarios del módulo de {inicial_minuscula(nombre_modulo)}",
            ["Código", "Caso de uso", "Actores", "Precondición", "Resultado esperado"],
            [[c, n, ", ".join(a) if a else "Sistema", BREVE[c][0], BREVE[c][1]]
             for c, n, a, _tab in suyos],
            nota="Elaboración propia.",
            anchos=[1.5, 3.2, 2.9, 4.4, 4.5],
        )


def _trazabilidad(d):
    d.titulo("4. Trazabilidad con el modelo de datos", nivel=1, nueva_pagina=True)
    d.parrafo(
        "Cada ficha declara las tablas sobre las que opera su caso. Este capítulo reúne esa "
        "información en dos matrices que la recorren en los dos sentidos, porque son dos "
        "preguntas distintas y las dos hay que poder responderlas."
    )
    d.parrafo(
        "La primera pregunta es qué datos toca un caso de uso, y sirve para saber qué hay que "
        "preparar antes de probarlo y qué queda afectado cuando falla. La segunda es qué casos "
        "tocan una tabla, y sirve para saber a qué le afecta un cambio en el modelo de datos y "
        "para comprobar que ninguna tabla del esquema quedó sin caso de uso que la justifique, "
        "porque una tabla que ningún caso toca es una tabla que el sistema no necesita."
    )

    d.titulo("4.1 De cada caso de uso a las tablas que toca", nivel=2)
    d.tabla(
        "Tablas del modelo de datos que toca cada caso de uso",
        ["Código", "Caso de uso", "Tablas que toca"],
        [[c, n, ", ".join(tab)] for c, n, _m, _a, _d, _rf, tab in catalogo.todos()],
        nota="Elaboración propia. Se indican los nombres de las tablas y no las sentencias que "
             "las consultan.",
        anchos=[1.6, 7.4, 7.5],
    )

    d.titulo("4.2 De cada tabla a los casos de uso que la tocan", nivel=2,
             nueva_pagina=True)
    por_tabla = catalogo.por_tabla()
    d.tabla(
        "Casos de uso que operan sobre cada tabla del modelo de datos",
        ["Tabla", "Casos", "Casos de uso que la tocan"],
        [[tabla, str(len(casos)), ", ".join(casos)] for tabla, casos in por_tabla.items()],
        nota="Elaboración propia. Las once tablas corresponden al esquema relacional descrito "
             "en el anexo de diccionario de datos.",
        anchos=[2.6, 1.4, 12.5],
    )

    sin_casos = [t for t, casos in por_tabla.items() if not casos]
    mas_tocada = max(por_tabla.items(), key=lambda x: len(x[1]))
    d.parrafo(
        f"Las {len(por_tabla)} tablas del esquema quedan cubiertas y ninguna se queda sin caso "
        f"de uso que la justifique. La más referenciada es {mas_tocada[0]}, con "
        f"{len(mas_tocada[1])} casos, lo que corresponde a su posición en el modelo, porque de "
        "ella cuelgan las citas, las historias, las consultas, las recetas y los exámenes."
        if not sin_casos else
        f"Quedan sin cubrir las siguientes tablas: {', '.join(sin_casos)}."
    )
    d.parrafo(
        "Con esta matriz y la de trazabilidad entre objetivos y requisitos del anexo de "
        "especificación puede recorrerse el camino completo, que va del objetivo del proyecto "
        "al requisito que lo concreta, de este al caso de uso que lo realiza y de allí a los "
        "datos sobre los que opera. Ese recorrido es lo que solicitaron los evaluadores y es "
        "también lo que permite responder, ante un cambio en cualquiera de los cuatro niveles, "
        "qué más queda afectado."
    )


if __name__ == "__main__":
    documento = construir()
    codigos = {c[0] for c in catalogo.todos()}
    faltan = [c for c in codigos if c not in DETALLE and c not in BREVE]
    sobran = [c for c in list(DETALLE) + list(BREVE) if c not in codigos]
    repetidos = [c for c in DETALLE if c in BREVE]
    print(f"Generado: {ARCHIVO}")
    print(f"Fichas completas: {len(DETALLE)}  Breves: {len(BREVE)}  "
          f"Total: {len(DETALLE) + len(BREVE)} de {len(codigos)}")
    if faltan:
        print(f"  AVISO sin documentar: {sorted(faltan)}")
    if sobran:
        print(f"  AVISO documentados pero fuera del catalogo: {sorted(sobran)}")
    if repetidos:
        print(f"  AVISO en los dos formatos a la vez: {sorted(repetidos)}")
    print(f"Tablas: {documento.n_tabla}")
    if faltan or sobran or repetidos:
        raise SystemExit(1)
