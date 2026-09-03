# -*- coding: utf-8 -*-
"""
E4 — Capítulo 2. Marco referencial del proyecto.

Este es el capítulo que **cita**, y de sus citas sale la lista de referencias de T17. Las
fuentes son todas verificables y se citan por parafraseo, sin número de página, de modo que no
se transcribe texto de ninguna de ellas.

Las referencias declaradas aquí viven en `FUENTES`, y `e4_cierre.py` construirá la lista
bibliográfica a partir de esa misma estructura. Escribirlas aparte llevaría a lo de siempre, que
es una fuente citada en el cuerpo que no aparece en la lista, o una lista con fuentes que nadie
citó.

🔴 **Aquí va la justificación de scrypt** (decisión D2). Se argumenta como lo que es, una
elección entre dos funciones de derivación de clave con propiedades distintas, apoyada en la
literatura que las define y en la recomendación de OWASP. El apartado 6.5 retoma el asunto desde
la implementación.
"""

# (clave, cita en el texto, referencia completa en APA 7)
FUENTES = {
    "res1995": ("Ministerio de Salud, 1999",
                "Ministerio de Salud. (1999). Resolución 1995 de 1999. Por la cual se "
                "establecen normas para el manejo de la Historia Clínica. Diario Oficial "
                "(Colombia)."),
    "ley1581": ("Ley 1581 de 2012",
                "Congreso de la República de Colombia. (2012). Ley 1581 de 2012. Por la cual "
                "se dictan disposiciones generales para la protección de datos personales. "
                "Diario Oficial No. 48.587."),
    "sandhu": ("Sandhu et al., 1996",
               "Sandhu, R. S., Coyne, E. J., Feinstein, H. L., y Youman, C. E. (1996). "
               "Role-based access control models. Computer, 29(2), 38-47."),
    "nist": ("Ferraiolo et al., 2001",
             "Ferraiolo, D. F., Sandhu, R., Gavrila, S., Kuhn, D. R., y Chandramouli, R. "
             "(2001). Proposed NIST standard for role-based access control. ACM Transactions "
             "on Information and System Security, 4(3), 224-274."),
    "bcrypt": ("Provos y Mazières, 1999",
               "Provos, N., y Mazières, D. (1999). A future-adaptable password scheme. "
               "Proceedings of the USENIX Annual Technical Conference, 81-91."),
    "scrypt": ("Percival, 2009",
               "Percival, C. (2009). Stronger key derivation via sequential memory-hard "
               "functions. BSDCan 2009."),
    "rfc7914": ("Percival y Josefsson, 2016",
                "Percival, C., y Josefsson, S. (2016). The scrypt password-based key "
                "derivation function (RFC 7914). Internet Engineering Task Force."),
    "owasp": ("OWASP, 2021",
              "Open Web Application Security Project. (2021). Password storage cheat sheet. "
              "OWASP Foundation."),
    "elmasri": ("Elmasri y Navathe, 2016",
                "Elmasri, R., y Navathe, S. B. (2016). Fundamentals of database systems "
                "(7.ª ed.). Pearson."),
    "sommerville": ("Sommerville, 2011",
                    "Sommerville, I. (2011). Ingeniería de software (9.ª ed.). Pearson "
                    "Educación."),
    "pressman": ("Pressman y Maxim, 2020",
                 "Pressman, R. S., y Maxim, B. R. (2020). Ingeniería del software: un enfoque "
                 "práctico (9.ª ed.). McGraw-Hill."),
    "iso25010": ("ISO/IEC, 2011",
                 "International Organization for Standardization. (2011). ISO/IEC 25010:2011. "
                 "Systems and software engineering: systems and software quality requirements "
                 "and evaluation (SQuaRE)."),
    "scrum": ("Schwaber y Sutherland, 2020",
              "Schwaber, K., y Sutherland, J. (2020). La Guía de Scrum: la guía definitiva de "
              "Scrum, las reglas del juego. Scrum.org."),
}


def cita(clave):
    return FUENTES[clave][0]


CONCEPTUAL = [
    ("Historia clínica",
     "registro cronológico de las condiciones de salud de un paciente y de los actos que "
     "sobre él se realizan. Es un documento reservado, y su diligenciamiento corresponde al "
     "personal que interviene directamente en la atención."),
    ("Acto clínico",
     "conjunto de registros que el profesional produce sobre un paciente al atenderlo, que en "
     "este sistema son la historia clínica, el diagnóstico con su plan de tratamiento y la "
     "prescripción."),
    ("Cita médica",
     "reserva de una franja de tiempo de un profesional para atender a un paciente "
     "determinado, con una fecha, una hora y un motivo."),
    ("Disponibilidad",
     "conjunto de franjas de tiempo de un profesional que no están ocupadas por otra cita ni "
     "alcanzadas por la separación mínima que debe existir entre dos atenciones."),
    ("Rol",
     "conjunto de permisos que se concede a una función dentro de la organización y no a una "
     "persona concreta. Las personas reciben los permisos por pertenecer al rol."),
    ("Control de acceso basado en roles",
     "modelo de autorización en el que los permisos se asignan a roles y los roles a los "
     "usuarios, de modo que cambiar lo que alguien puede hacer se resuelve cambiándole el rol "
     "y no revisando permiso por permiso."),
    ("Sesión",
     "estado que el sistema conserva entre peticiones para recordar quién está autenticado y "
     "con qué rol, y del que se toma la identidad de quien firma un registro."),
    ("Función de derivación de clave",
     "algoritmo que transforma una contraseña en un valor almacenable del que no puede "
     "recuperarse la original, diseñado de forma deliberada para ser costoso de calcular."),
    ("Hash de contraseña",
     "resultado de aplicar una función de derivación de clave a una contraseña. Es lo único "
     "que el sistema almacena, y comprobar una contraseña consiste en derivarla de nuevo y "
     "comparar, nunca en descifrar lo guardado."),
    ("Transacción",
     "conjunto de operaciones sobre la base de datos que se confirman todas o no se confirma "
     "ninguna, de manera que una falla intermedia no deja registros a medias."),
    ("Condición de carrera",
     "situación en la que dos operaciones simultáneas leen el mismo estado antes de que "
     "cualquiera escriba, y ambas concluyen que pueden actuar cuando solo una debería."),
    ("Bloqueo",
     "mecanismo por el cual una transacción impide que otra lea o modifique las filas que "
     "está a punto de cambiar, hasta que confirme o deshaga."),
    ("Baja lógica",
     "retiro de un registro de la operación cambiando su estado en lugar de borrarlo, de modo "
     "que lo que lo referencia siga siendo consultable."),
    ("Clave foránea",
     "columna que referencia la clave primaria de otra tabla, con lo que la base impide que "
     "quede apuntando a una fila que no existe."),
]

TECNOLOGICO = [
    ("Python",
     "lenguaje de programación interpretado y de tipado dinámico, con el que se construyó la "
     "totalidad de la lógica del servidor."),
    ("Flask",
     "marco de trabajo web para Python que resuelve el enrutamiento de las peticiones, la "
     "gestión de la sesión y el renderizado de las plantillas. Se eligió por ser un marco "
     "reducido, que no impone una estructura de proyecto y deja a la vista lo que ocurre en "
     "cada petición, lo que resulta apropiado para un trabajo cuyo propósito incluye "
     "comprender el mecanismo y no solo usarlo."),
    ("Jinja2",
     "motor de plantillas con el que el servidor arma el HTML antes de enviarlo al navegador, "
     "de manera que la decisión de qué mostrar a cada rol se toma en el servidor."),
    ("Bootstrap",
     "biblioteca de estilos que proporciona la rejilla y los componentes de la interfaz, y con "
     "la que las pantallas se adaptan al ancho del dispositivo."),
    ("MySQL",
     "sistema gestor de bases de datos relacionales que almacena las once tablas del esquema. "
     "Aporta las claves foráneas que sostienen la integridad y el bloqueo de filas con el que "
     "se resuelve la reserva simultánea de un mismo horario."),
    ("mysql-connector-python",
     "conector oficial que comunica la aplicación con el gestor de base de datos, empleado con "
     "consultas parametrizadas y con un conjunto reutilizable de conexiones."),
    ("werkzeug.security",
     "biblioteca que acompaña a Flask y que proporciona la derivación y la verificación de las "
     "contraseñas mediante scrypt."),
    ("pytest",
     "herramienta con la que se escribieron y se ejecutan las pruebas automatizadas que "
     "verifican las reglas críticas del sistema."),
    ("Git",
     "sistema de control de versiones con el que se registró la evolución del proyecto."),
]


def escribir(d):
    d.titulo("Capítulo 2. Marco referencial del proyecto", nivel=1, nueva_pagina=True)
    _teorico(d)
    _conceptual(d)
    _tecnologico(d)


def _concepto(d, termino, texto):
    p = d.parrafo()
    p.add_run(f"{termino}. ").bold = True
    p.add_run(texto)
    return p


def _teorico(d):
    d.titulo("2.1 Marco teórico", nivel=2)
    d.parrafo(
        "El marco teórico reúne los fundamentos sobre los que se sostiene la solución "
        "propuesta, esto es, la naturaleza reservada de la historia clínica, la programación "
        "de la atención entendida como una asignación de recursos sujeta a restricciones, el "
        "control de la concurrencia sobre un recurso compartido, el modelo de acceso basado en "
        "roles y el almacenamiento seguro de las credenciales."
    )

    _concepto(d, "La historia clínica como documento reservado",
              "La historia clínica no es un archivo administrativo más. La normativa "
              "colombiana la define como un documento privado, sometido a reserva, cuyo "
              "diligenciamiento corresponde únicamente al personal que interviene de forma "
              f"directa en la atención del paciente ({cita('res1995')}). A esa reserva se "
              "suma el régimen general de protección de datos personales, que clasifica los "
              "datos relativos a la salud como datos sensibles y sujeta su tratamiento a "
              f"condiciones más estrictas que las de un dato corriente ({cita('ley1581')}). "
              "De ahí se desprende la consecuencia técnica que atraviesa este proyecto, y es "
              "que la autoría de un registro clínico y el alcance de quien puede leerlo no "
              "son preferencias de configuración sino condiciones que el sistema debe "
              "sostener por diseño.")

    _concepto(d, "El agendamiento como asignación de recursos con restricciones",
              "Programar la atención de un centro de salud consiste en asignar un recurso "
              "escaso, que es el tiempo del profesional, a un conjunto de solicitudes que "
              "compiten por él. El problema no está en registrar la asignación sino en "
              "verificar que cumple las restricciones del dominio, entre ellas que un "
              "profesional no puede atender dos consultas a la vez, que entre dos atenciones "
              "debe mediar el tiempo que la consulta dura y que no puede programarse una "
              "atención sobre un instante que ya transcurrió. Un registro que se limita a "
              "guardar lo que se le escribe traslada esa verificación a la persona que "
              "agenda, y con ella la posibilidad de equivocarse.")

    _concepto(d, "Concurrencia sobre un recurso compartido",
              "Cuando varias personas pueden reservar el mismo recurso, aparece una "
              "dificultad que no existe cuando trabaja una sola. Dos solicitudes simultáneas "
              "pueden consultar la disponibilidad antes de que cualquiera de las dos escriba, "
              "de modo que ambas encuentran el horario libre y ambas lo reservan. La teoría "
              "de bases de datos describe esta situación entre las anomalías que el control "
              "de concurrencia debe evitar, y ofrece como solución que la comprobación y la "
              "escritura ocurran dentro de una misma transacción que mantenga bloqueadas las "
              f"filas consultadas hasta confirmar ({cita('elmasri')}). La consecuencia de "
              "diseño es que la validación de la agenda no puede resolverse consultando "
              "primero y guardando después, porque entre ambas operaciones cabe otra "
              "petición.")

    _concepto(d, "Control de acceso basado en roles",
              "El modelo de control de acceso basado en roles propone que los permisos no se "
              "asignen a las personas sino a los roles que estas desempeñan, y que las "
              f"personas los reciban por pertenecer a un rol ({cita('sandhu')}). La "
              "propuesta de estandarización posterior formaliza sus elementos y sus "
              "relaciones, y precisa que la asignación de permisos es una decisión de la "
              f"organización y no del usuario ({cita('nist')}). Su ventaja frente a conceder "
              "permisos uno a uno es que el permiso queda enunciado sobre la función y no "
              "sobre el individuo, de modo que incorporar a un profesional nuevo consiste en "
              "asignarle un rol y no en revisar una lista de autorizaciones.")

    _concepto(d, "La diferencia entre ocultar y prohibir",
              "Un sistema puede dejar de mostrar una opción a quien no debe usarla, y esa es "
              "una decisión de interfaz. Puede además rechazar la operación cuando llega, y "
              "esa es una decisión de autorización. Las dos se ven igual mientras el usuario "
              "se comporte como se espera, pero se distinguen en cuanto la petición se envía "
              "por fuera de la interfaz, porque una opción oculta vuelve a estar disponible y "
              "una comprobación del servidor no. Por esa razón el control de acceso se "
              "considera una propiedad del servidor, y lo que la interfaz hace es "
              "acompañarla, no sustituirla.")

    _concepto(d, "Almacenamiento de contraseñas y funciones de derivación de clave",
              "Una contraseña no se guarda, se deriva. El sistema almacena únicamente el "
              "resultado de aplicarle una función de derivación de clave, y comprobarla "
              "consiste en volver a derivar la que el usuario escribe y comparar los dos "
              "resultados, nunca en descifrar lo almacenado. Estas funciones se diseñan de "
              "forma deliberada para ser costosas, porque de ese costo depende cuánto tarda "
              "quien intente adivinar contraseñas a partir de una base de datos sustraída.")

    _concepto(d, "Por qué scrypt y no bcrypt",
              "Las dos funciones más difundidas para esta tarea responden a amenazas de "
              "épocas distintas. La primera de ellas se diseñó para que su costo pudiera "
              "aumentarse con el tiempo mediante un parámetro, de modo que el avance del "
              f"hardware no la volviera obsoleta ({cita('bcrypt')}). Su costo, sin embargo, "
              "es fundamentalmente de cómputo, y el cómputo es precisamente lo que resulta "
              "barato de paralelizar en tarjetas gráficas y en circuitos dedicados.")
    d.parrafo(
        "La función empleada en este proyecto pertenece a una generación posterior, cuyo "
        "planteamiento consiste en exigir además una cantidad configurable de memoria durante "
        f"el cálculo ({cita('scrypt')}). La memoria es un recurso caro de multiplicar en el "
        "hardware especializado, de manera que un atacante que quiera probar miles de "
        "contraseñas en paralelo necesita miles de veces esa memoria, y el ataque deja de "
        "abaratarse simplemente añadiendo unidades de cálculo. La función quedó posteriormente "
        f"especificada como estándar de Internet ({cita('rfc7914')}), lo que la sitúa entre "
        "las opciones documentadas y no entre las soluciones improvisadas."
    )
    d.parrafo(
        "Ambas funciones se consideran aceptables para el almacenamiento de contraseñas en las "
        "recomendaciones vigentes de seguridad en aplicaciones web, que las enumeran junto a "
        "otras derivadas del mismo principio y desaconsejan en cambio el uso de funciones de "
        f"resumen de propósito general, que no fueron diseñadas para esta tarea "
        f"({cita('owasp')}). La elección de una función con endurecimiento de memoria "
        "responde, por tanto, a una diferencia de propiedades frente a un atacante con "
        "hardware especializado, y no a una preferencia de implementación. En el apartado 6.5 "
        "se describe cómo queda aplicada dentro del sistema."
    )

    _concepto(d, "Calidad del software y verificación",
              "La calidad de un producto de software se describe mediante atributos que "
              "pueden evaluarse por separado, entre ellos la funcionalidad, la fiabilidad, la "
              f"usabilidad, la seguridad y la mantenibilidad ({cita('iso25010')}). Un "
              "atributo enunciado sin una forma de comprobarlo no es un requisito sino una "
              "aspiración, razón por la cual la especificación de este proyecto acompaña cada "
              "requisito no funcional con el modo en que se verifica. La verificación "
              "automatizada añade una propiedad que la manual no tiene, y es que puede "
              f"repetirse íntegra después de cada cambio sin depender de que alguien recuerde "
              f"hacerlo ({cita('pressman')}).")

    _concepto(d, "Ingeniería de requisitos",
              "La especificación de requisitos distingue entre lo que el sistema debe hacer y "
              "las condiciones bajo las cuales debe hacerlo, y advierte que los defectos "
              "introducidos en esta etapa son los más costosos de corregir, porque se "
              f"propagan a todo lo que se construye después ({cita('sommerville')}). De ese "
              "principio se desprende la organización del capítulo 4, donde los requisitos se "
              "enuncian, se priorizan y se hacen trazables hasta los casos de uso y hasta las "
              "tablas sobre las que operan.")


def _conceptual(d):
    d.titulo("2.2 Marco conceptual", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Se relacionan a continuación los términos empleados a lo largo del documento, con el "
        "significado preciso que tienen dentro del dominio de la atención en salud y de este "
        "proyecto en particular."
    )
    d.vinetas(CONCEPTUAL)


def _tecnologico(d):
    d.titulo("2.3 Marco tecnológico", nivel=2, nueva_pagina=True)
    d.parrafo(
        "Se describen las tecnologías empleadas en la construcción de la solución, indicando "
        "la función que cumple cada una dentro del sistema. La selección respondió a tres "
        "condiciones, que son la disponibilidad de herramientas libres, la posibilidad de "
        "instalar el conjunto en un equipo corriente sin costo de licenciamiento y la "
        "conveniencia formativa de emplear componentes cuyo funcionamiento quede a la vista."
    )
    d.vinetas(TECNOLOGICO)
    d.parrafo(
        "El desarrollo se condujo con la metodología ágil Scrum, cuyos elementos y ciclo se "
        f"describen en el capítulo 3 ({cita('scrum')})."
    )


# Marca que lee el ensamblador: este capítulo ya está escrito contra MediApp.
ADAPTADO_A_MEDIAPP = True
