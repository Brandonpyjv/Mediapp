# Guion de Sustentación - MediApp

**Recomendación general:** No leer las diapositivas. El texto visual es el mínimo para apoyar la idea; el ponente desarrolla el resto hablado.

## Sección I. Formulación

**[Diapositiva Divisoria I]**
*Ponente:* "Buenos días. Daremos inicio a la sustentación del proyecto MediApp, comenzando por su formulación."

**1. Portada institucional**
*Ponente:* (Espera a que presenten o introduce formalmente al equipo y la ficha, si es el caso).

**2. Portada del proyecto**
*Ponente:* "Nuestro proyecto se titula MediApp: Sistema web de agendamiento de citas médicas y gestión de historias clínicas para la optimización de la atención en centros de salud."

**3. El problema**
*Ponente:* "Actualmente, conseguir una cita médica depende casi en su totalidad de que el paciente acuda presencialmente y de la memoria o anotaciones manuales de quien asigna los turnos en la ventanilla."

**4. Justificación**
*Ponente:* "Esto genera tres problemas graves: el 71 % de los usuarios ha tenido que desplazarse solo para pedir o cancelar una cita; el 65 % tarda más de media hora en ser atendido para este trámite, y el 60 % ha sufrido cruces de horarios por errores manuales."

**5. Objetivo general**
*Ponente:* "Por ello, nuestro objetivo general es desarrollar MediApp, un sistema web de agendamiento con acceso diferenciado para administrador, médico y paciente, que permita gestionar la disponibilidad y controlar el historial clínico."

**6. Objetivos específicos**
*Ponente:* "Para lograrlo, nos planteamos tres objetivos específicos: facilitar la programación de citas, habilitar la gestión exclusiva del acto clínico por parte del médico, y garantizar la confidencialidad mediante un control de roles."

**7. Alcance**
*Ponente:* "El sistema final cuenta con 10 módulos funcionales. Es importante destacar que hemos excluido intencionalmente capacidades como la facturación, los pagos y el manejo de inventario de farmacia para mantener el foco en nuestra propuesta de valor."

**8. Riesgos del proyecto**
*Ponente:* "Durante la planeación identificamos cuatro riesgos principales. El más crítico era dejar observaciones sin atender, lo cual mitigamos con una revisión cruzada constante y un seguimiento estricto de las directrices."

**9. Cronograma**
*Ponente:* "El desarrollo se ejecutó en cinco fases, desde marzo de 2025 hasta septiembre de 2026, cumpliendo los tiempos estipulados para cada etapa."

## Sección II. Análisis

**[Diapositiva Divisoria II]**
*Ponente:* "Pasemos a la fase de Análisis, donde entendimos las necesidades reales de los usuarios."

**10. Levantamiento de requisitos**
*Ponente:* "Para levantar los requisitos utilizamos tres fuentes: encuestas a pacientes, entrevista a un experto del dominio de salud y observación directa en la ventanilla de atención."

**11. La encuesta**
*Ponente:* "Aplicamos un formulario de 12 preguntas cerradas a una muestra de 48 usuarios reales de centros de salud en la ciudad de Cúcuta."

**12. El hallazgo central**
*Ponente:* "El hallazgo que guio nuestro diseño fue rotundo: el 85 % de los pacientes quiere elegir su propio horario, y el 81 % exige que la cita quede agendada de inmediato, sin aprobaciones previas. Por eso, delegamos la reserva al paciente."

**13. La entrevista**
*Ponente:* "De la entrevista concluimos que el médico no arma su agenda, solo la recibe. Además, el médico es el dueño y responsable exclusivo del acto clínico y de lo que se firma en la historia."

**14. La observación**
*Ponente:* "Al observar la ventanilla notamos que pedir y cancelar una cita cuesta la misma fila. Además, la disponibilidad se maneja de memoria y las anotaciones en papel no dejan rastro de quién hizo qué."

**15. Partes interesadas**
*Ponente:* "Mapeamos a los involucrados en cuatro cuadrantes, donde el paciente y el médico son los actores clave que se benefician directamente del nuevo flujo."

**16. Priorización**
*Ponente:* "Aplicamos el método MoSCoW, enfocándonos primero en los 42 requisitos críticos o 'Must', lo que garantizó tener el sistema base operativo antes de añadir extras."

**17. Requisitos funcionales**
*Ponente:* "Consolidamos un total de 87 requisitos funcionales, distribuidos estratégicamente a través de los 10 módulos del sistema."

**18. Requisitos no funcionales**
*Ponente:* "Establecimos 24 requisitos de calidad en 7 categorías, como seguridad y rendimiento, con mecanismos claros para verificar que cada uno se cumpla en el sistema real."

## Sección III. Diseño

**[Diapositiva Divisoria III]**
*Ponente:* "Con los requisitos claros, entramos a la fase de Diseño del sistema."

**19. Actores**
*Ponente:* "Definimos tres roles humanos: Administrador, Médico y Paciente. Además, incluimos al 'Sistema' como un cuarto actor que ejecuta reglas automáticas."

**20. Casos de uso**
*Ponente:* "Estructuramos las interacciones en 60 casos de uso repartidos en 11 diagramas, abarcando todas las capacidades operativas requeridas."

**21. Un módulo de cerca**
*Ponente:* "El agendamiento de citas es nuestro módulo central y el único donde concurren los tres actores humanos, cada uno con acciones y límites precisos."

**22. Matriz de permisos**
*Ponente:* "Nuestra matriz de permisos es estricta: el administrador no puede alterar historias clínicas, y el paciente solo tiene permiso de escritura para agendar y cancelar sus propias citas."

**23. Arquitectura**
*Ponente:* "El sistema sigue una arquitectura de cuatro capas, desde la base de datos hasta la vista del usuario, asegurando que cada capa solo se comunique con la inmediatamente inferior."

**24. Modelo de datos**
*Ponente:* "El modelo relacional consta de 11 tablas. Las entidades Médico y Paciente actúan como los centros de gravedad sobre los que orbitan las citas y los registros clínicos."

**25. Modelo físico**
*Ponente:* "Este diseño se tradujo directamente en un esquema físico generado e implementado en el motor de MariaDB."

**26. Mapa de navegación**
*Ponente:* "El mapa de navegación garantiza el aislamiento: no existe ningún camino físico en la interfaz que lleve a la vista de un rol hacia la de otro."

## Sección IV. Desarrollo

**[Diapositiva Divisoria IV]**
*Ponente:* "En la fase de Desarrollo materializamos el diseño."

**27. Metodología**
*Ponente:* "Seguimos la metodología Scrum, dividiendo la construcción en 10 sprints de dos semanas, lo que nos permitió entregar un módulo funcional en cada iteración."

**28. Tecnologías**
*Ponente:* "Nuestra pila tecnológica se apoya en Python 3.13 con Flask para el servidor web, MariaDB para los datos y Bootstrap 5 para el diseño adaptativo."

**29. Las tres vistas**
*Ponente:* "Desarrollamos interfaces exclusivas para cada rol. El sistema evalúa quién inicia sesión y muestra únicamente los paneles y opciones que el usuario está autorizado a usar."

**30. El calendario**
*Ponente:* "El corazón de la solución es el calendario. Aquí se calculan automáticamente los turnos de 30 minutos, las separaciones mínimas y se evita que un paciente tome más de una cita diaria."

**31. Seguridad**
*Ponente:* "La seguridad opera en tres niveles por cada petición: verifica que haya sesión, que el rol sea correcto y que el recurso le pertenezca. Además, aseguramos las contraseñas usando scrypt."

## Sección V. Pruebas y cierre

**[Diapositiva Divisoria V]**
*Ponente:* "Finalmente, en la etapa de Pruebas certificamos el funcionamiento del producto."

**32. Las pruebas**
*Ponente:* "Construimos una batería de 91 pruebas automatizadas que se ejecutan en 6,9 segundos. Todas pasan correctamente, validando desde rutas hasta reglas de negocio."

**33. Evidencia 1 (Responsabilidad médica)**
*Ponente:* "Como evidencia, veamos la historia clínica. Solo el médico puede diligenciarla, y una vez guardada, queda irrevocablemente firmada a su nombre."

**34. Evidencia 2 (Regla de negocio 1)**
*Ponente:* "Aquí probamos la primera regla: si se intenta agendar una cita a menos de 30 minutos de otra del mismo médico, el sistema la rechaza inmediatamente en el servidor."

**35. Evidencia 3 (Privacidad de datos)**
*Ponente:* "Validamos la privacidad de los datos: incluso si el administrador fuerza la dirección URL para intentar crear una historia clínica, el sistema intercepta la acción y lo bloquea."

**36. Evidencia 4 (Autogestión y Regla 2)**
*Ponente:* "Y demostramos el agendamiento directo. El paciente reserva su turno sin depender de nadie, su identidad se extrae de su sesión cifrada y la cita queda a su nombre."

**37. Resultados**
*Ponente:* "Con esto, hemos cumplido los tres objetivos específicos: un sistema fácil de agendar, un control clínico reservado solo al médico, y una confidencialidad garantizada mediante roles."

**38. Cierre**
*Ponente:* "Para concluir, el verdadero valor de MediApp no está solo en lo que permite hacer, sino en lo que impide. Un control manual puede obviarse o fallar; en el sistema, estas restricciones de negocio son inquebrantables, pues una regla que deja de aplicarse no produce ningún error visible."
