# PROMPT PARA QUE GEMINI ARME LAS DIAPOSITIVAS DE MEDIAPP

> Copia y pega todo lo que hay debajo de la línea. Adjunta además, si el entorno lo permite:
> `docs tesis/exposicion/Plantilla institucional.pptx` y las imágenes que se nombran en el §6.
>
> ⚠️ Si Gemini no puede leer tus archivos, pídele **el script de Python** (opción A del §2) y
> córrelo tú desde `D:\01. Proyectos\Mediapp\docs tesis\`. Es la vía que da un `.pptx` real con
> la plantilla institucional puesta.

---

Vas a construir la **presentación de sustentación de MediApp**, un trabajo de grado de
Tecnólogo en Análisis y Desarrollo de Software del SENA.

El documento escrito ya está terminado: son 143 páginas con seis capítulos, conclusiones,
referencias en APA 7 y cuatro anexos. **No tienes que inventar contenido**: todo lo que necesitas
está en este prompt. Tu trabajo es convertirlo en diapositivas que se puedan proyectar y
sustentar.

## 1. La razón de ser de este encargo

Este proyecto **ya se sustentó una vez y fue reprobado**. Entre las observaciones del evaluador,
dos apuntan directamente a la presentación:

- La presentación anterior era **«plana»**, y hay que rediseñarla.
- **«El diagrama de gantt de este documento es diferente al de la diapositiva.»** El cronograma
  de la presentación tiene que ser exactamente el mismo del documento, que es el archivo
  `FIG-cronograma.png` que se te entrega.

«Plana» significa muros de texto, viñetas genéricas y diapositivas que el ponente lee en voz
alta. Lo contrario **no es más adornos**: es que cada diapositiva tenga **una sola idea**, un
apoyo visual que la demuestre y el mínimo texto que la sostenga. Si una diapositiva se entiende
sin que nadie hable, sobra texto.

## 2. Qué tienes que entregar

**Opción A, la preferida:** un **script de Python con `python-pptx`** que abra
`docs tesis/exposicion/Plantilla institucional.pptx`, escriba encima y guarde
`docs tesis/exposicion/MediApp - Sustentación.pptx`. La plantilla trae el logo, la marca de agua
y la paleta institucional, y **no se rediseña**: se escribe dentro de ella.

**Opción B, si no puedes generar archivos:** el contenido completo diapositiva por diapositiva,
en el formato del §5, listo para vaciarlo a mano.

En los dos casos, entrega además **el guion de sustentación**: qué dice el ponente en cada
diapositiva, en dos o tres frases, redactado para decirse en voz alta y no para leerse.

## 3. Reglas de estilo que no son negociables

Vienen del propio proyecto y se comprueban en todo lo escrito:

- **Nada de guion largo ni de punto medio.** Los incisos van entre comas o paréntesis.
- **Nada de «afirmación breve: explicación».** La prosa va continua o partida en dos oraciones.
  Los dos puntos solo valen en etiquetas de dato y en títulos de obras citadas.
- 🔴 **La presentación no habla de la presentación.** No hay diapositivas del tipo «qué vamos a
  ver hoy», ni notas que expliquen por qué el documento está escrito de cierta forma, ni
  referencias a la evaluación anterior. Se habla del proyecto, no del trabajo de grado como
  objeto.
- **Ninguna cifra inventada.** Todas las que puedes usar están en el §4.

## 4. Los datos del proyecto

### Identificación

| Campo | Valor |
|---|---|
| Título | **MediApp: Sistema web de agendamiento de citas médicas y gestión de historias clínicas para la optimización de la atención en centros de salud** |
| Integrantes | ÁNGEL JESÚS HERNÁNDEZ ARÉVALO · RICHARD ALBERTO QUIÑONES QUIÑONES |
| Ficha | 3115426 |
| Programa | Tecnólogo en Análisis y Desarrollo de Software |
| Institución | Servicio Nacional de Aprendizaje (SENA) |
| Centro | Centro de la Industria, la Empresa y los Servicios (CIES) |
| Instructora | Heidy Lizbeth Adarme |
| Ciudad y año | Cúcuta, Norte de Santander, 2026 |

### Objetivo general

> Desarrollar MediApp, un sistema web de agendamiento de citas médicas con acceso diferenciado
> para administrador, médico y paciente, que permita gestionar la disponibilidad de la atención
> médica y controlar el historial clínico en centros de salud.

### Objetivos específicos

1. **Facilitar la programación de la atención médica** mediante un módulo interactivo que
   permita al administrador y al paciente agendar citas de forma intuitiva.
2. **Habilitar la gestión del acto clínico como responsabilidad exclusiva del médico tratante**
   para la creación y actualización de historias clínicas, diagnósticos y prescripciones.
3. **Garantizar la confidencialidad de la información médica** mediante un control de acceso
   basado en roles que restrinja la visualización y edición según el perfil del usuario.

Son tres y no cinco, y están redactados como **resultados y no como actividades**. El tercero
está acotado a propósito con «mediante control de acceso basado en roles», porque el sistema no
cifra la información y un objetivo que promete de más no puede declararse cumplido.

### Cifras verificadas (úsalas, no inventes otras)

| Dato | Valor |
|---|---|
| Módulos funcionales | 10 |
| Requisitos funcionales | 87 |
| Requisitos no funcionales | 24, en 7 categorías |
| Reparto MoSCoW | 42 *Must*, 25 *Should*, 20 *Could*, 8 *Won't* |
| Casos de uso | 60, en 11 diagramas |
| Relaciones UML | 24 inclusiones y 2 extensiones |
| Tablas de la base | 11, con 63 columnas y 14 claves foráneas |
| Rutas del servidor | 53 |
| Roles | 3 (administrador, médico, paciente) |
| Pruebas automatizadas | **91, todas pasando, en 6,9 segundos** |
| Migraciones aplicadas | 7 |
| Muestra de la encuesta | 48 usuarios de centros de salud |

### Los tres roles, en una línea cada uno

- **Administrador:** gestiona la operación completa, que son usuarios, médicos, pacientes,
  catálogos, laboratorio y la agenda entera. Su única restricción es que **no crea ni modifica
  historias clínicas, consultas ni recetas**, aunque sí puede consultarlas.
- **Médico:** dueño exclusivo del acto clínico, que son la historia clínica, el diagnóstico y la
  prescripción. **Su agenda es de solo lectura**, porque nunca agenda ni cambia sus propias
  citas.
- **Paciente:** consulta lo suyo, con dos únicas excepciones de escritura, que son **agendar su
  cita y cancelarla**.

### Las dos reglas de negocio propias

1. Entre dos atenciones del mismo médico deben mediar al menos **30 minutos**.
2. Un paciente no puede tener **más de una cita el mismo día**.

Ninguna de las dos puede declararse como restricción de la base de datos, porque no prohíben un
valor repetido sino **una distancia entre valores**, así que se comprueban en el servidor dentro
de la misma operación que escribe.

### Los tres hallazgos de la elicitación (encuesta a 48 personas)

- **26 (54 %)** solicitan hoy su cita presentándose en el centro y **34 (71 %)** se han
  desplazado únicamente para pedirla o cancelarla.
- **31 (65 %)** tardan más de media hora en que se la asignen, y **29 (60 %)** han recibido al
  menos una vez una cita cruzada con la de otro paciente.
- 🔴 **El hallazgo central:** **41 (85 %)** quieren elegir ellos mismos el horario libre y
  **39 (81 %)** quieren que quede agendada **de inmediato**, contra 5 que prefieren aprobación
  previa. Eso separa *querer ver* la agenda de *querer reservar* en ella.

### Las dos decisiones que hay que saber defender

**Decisión 1, scrypt y no bcrypt.** Las contraseñas se derivan con scrypt. Las dos funciones son
admitidas por las recomendaciones vigentes de seguridad en aplicaciones web; la diferencia es que
scrypt exige además una cantidad configurable de **memoria** durante el cálculo, y la memoria es
cara de multiplicar en el hardware especializado con el que se prueban contraseñas en paralelo.
No es una diferencia de solidez sino de propiedades frente a ese atacante.

**Decisión 2, el paciente agenda su propia cita sin aprobación previa.** Es una desviación
consciente del planteamiento inicial, que asignaba el agendamiento solo al administrador. La
justifica el hallazgo central de la encuesta: un agendamiento en el que la solicitud espera la
confirmación de un tercero conserva la demora que la herramienta viene a eliminar, y sustituye
una fila en la ventanilla por una fila electrónica. **El control no desaparece, se traslada**: el
administrador puede cancelar o reprogramar cualquier cita, incluidas las que reservó un paciente.
Y la delegación tiene un límite, porque **el paciente reserva únicamente para sí mismo**, ya que
su identidad se toma de la sesión y nunca del formulario.

## 5. La estructura de la presentación

Cinco secciones, unas 34 diapositivas. Cada fila de abajo es una diapositiva: su idea única, el
apoyo visual y el contenido. **Respeta el orden.**

### Sección I. Formulación

| # | Idea única | Apoyo visual | Contenido |
|---|---|---|---|
| 1 | Portada institucional | Plantilla | Datos del §4 |
| 2 | Portada del proyecto | Plantilla | El título completo de tres partes |
| 3 | El problema | `FIG-encuesta-resultados.png` | Conseguir una cita depende de un canal presencial y de la memoria de quien asigna. Las cifras del §4 |
| 4 | Justificación | Sin imagen, 3 datos grandes | 71 % se desplazó solo para pedir o cancelar; 65 % tarda más de media hora; 60 % ha sufrido un cruce |
| 5 | Objetivo general | Sin imagen | El enunciado literal |
| 6 | Objetivos específicos | Tres bloques | Los tres literales, uno por bloque |
| 7 | Alcance | Dos columnas | Izquierda, los 10 módulos. Derecha, las 8 capacidades excluidas |
| 8 | Riesgos del proyecto | Tabla de 4 filas | R3 acumular la documentación, R1 dejar una observación sin atender, R7 subestimar el trabajo escrito, R5 fallo del entorno. Con probabilidad, impacto y respuesta |
| 9 | Cronograma | 🔴 `FIG-cronograma.png` | **Esta imagen exacta, sin rehacerla.** Cinco fases, de marzo de 2025 a septiembre de 2026 |

### Sección II. Análisis

| # | Idea única | Apoyo visual | Contenido |
|---|---|---|---|
| 10 | Cómo se levantaron los requisitos | Tres iconos | Encuesta a 48 usuarios, entrevista al experto del dominio y observación directa en ventanilla |
| 11 | La encuesta | `FIG-encuesta-formulario.png` | 12 preguntas cerradas, 48 respuestas, Cúcuta |
| 12 | 🔴 El hallazgo central | `FIG-encuesta-contraste.png` | Preguntas 7 y 8 lado a lado. 85 % quiere elegir, 81 % quiere que quede en firme. **Es la diapositiva más importante de la sección** |
| 13 | La entrevista | Sin imagen, 4 puntos | Una consulta ocupa media hora; el médico recibe su agenda y no la arma; la historia clínica es reservada y quien la firma responde; el examen de laboratorio lo carga el administrativo |
| 14 | La observación | Sin imagen, 4 puntos | La disponibilidad se recuerda, no se consulta; ventanilla y teléfono ofrecieron el mismo turno; cancelar cuesta la misma fila que pedir; la anotación no registra quién la hizo |
| 15 | Partes interesadas | `FIG-stakeholders.png` | Los cuatro cuadrantes |
| 16 | Priorización | `FIG-moscow.png` | La regla que produce el reparto, no solo el reparto |
| 17 | Requisitos funcionales | Tabla de 10 filas | Los 10 módulos con su número de requisitos y cuántos son críticos |
| 18 | Requisitos no funcionales | Tabla | Las 7 categorías con un ejemplo cada una, y cómo se verifica |

### Sección III. Diseño

| # | Idea única | Apoyo visual | Contenido |
|---|---|---|---|
| 19 | Actores | Tres columnas | Los tres roles del §4, más el actor Sistema para las reglas que corren solas |
| 20 | Casos de uso | `DCU-00 general.png` | 60 casos en 11 diagramas, los tres actores presentes |
| 21 | Un módulo de cerca | `DCU-05 Agendamiento de citas.png` | El único donde concurren los tres actores |
| 22 | 🔴 Matriz de permisos | `FIG-permisos.png` | La única restricción del administrador y las dos excepciones de escritura del paciente |
| 23 | Arquitectura | `FIG-arquitectura.png` | Cuatro capas, cada una apoyada en la de abajo |
| 24 | Modelo de datos | `FIG-mer.png` | 11 tablas, dos centros que son médico y paciente |
| 25 | Modelo físico | `FIG-fisico.png` | Generado desde el propio motor MySQL |
| 26 | Mapa de navegación | `FIG-mapa-navegacion.png` | Ningún camino lleva de la vista de un rol a la de otro |

### Sección IV. Desarrollo

| # | Idea única | Apoyo visual | Contenido |
|---|---|---|---|
| 27 | Metodología | `FIG-scrum.png` | 10 sprints de dos semanas, uno por módulo |
| 28 | Tecnologías | Logos o tabla | Python 3.13, Flask 3.1, Jinja2, Bootstrap 5, MariaDB 10.4, pytest 8, Git |
| 29 | Las tres vistas | `IU-02`, `IU-03`, `IU-04` juntas | Cada rol ve solo lo que puede hacer |
| 30 | 🔴 El calendario | `IU-05 calendario de disponibilidad.jpg` | La pantalla que resuelve el problema. Turnos de 30 minutos, aviso de la separación mínima y el día marcado cuando ya se tiene cita |
| 31 | Seguridad | Sin imagen, 3 bloques | Los tres momentos de comprobación: sesión, rol y propiedad. Más scrypt |

### Sección V. Pruebas y cierre

| # | Idea única | Apoyo visual | Contenido |
|---|---|---|---|
| 32 | Las pruebas | Tabla de 6 filas | Los 6 archivos con su número de pruebas. **91, todas pasando** |
| 33 | 🔴 Evidencia 1 | `CP-01a` y `CP-01b` lado a lado | El médico registra la historia clínica y queda firmada a su nombre |
| 34 | 🔴 Evidencia 2 | `CP-02a` y `CP-02b` lado a lado | Una cita a 15 minutos de otra del mismo médico **se rechaza** |
| 35 | 🔴 Evidencia 3 | `CP-03a` y `CP-03b` lado a lado | El administrador no puede escribir una historia clínica, ni siquiera forzando la dirección |
| 36 | 🔴 Evidencia 4 | `CP-04a` y `CP-04b` lado a lado | El paciente reserva su turno y la cita queda a su nombre |
| 37 | Resultados | Tabla de 3 filas | Un objetivo específico por fila, con la evidencia que lo sostiene |
| 38 | Cierre | Sin imagen | La conclusión: en un sistema cuyo valor está en **lo que impide**, la verificación manual no alcanza, porque un control que deja de aplicarse no produce ningún error visible |

🔴 **Las cuatro diapositivas de evidencia son el corazón de la sustentación.** Van siempre con
las dos imágenes **lado a lado**, la de antes a la izquierda y la de después a la derecha, con un
rótulo pequeño en cada una. Un pantallazo suelto demuestra que la pantalla existe; el par
demuestra que la operación ocurrió. Dos de los cuatro casos prueban **rechazos y no altas**, que
es lo que de verdad hay que demostrar en este sistema.

## 6. Dónde está cada imagen

**Figuras generadas** (todas `.png`), en:
`D:\01. Proyectos\Mediapp\docs tesis\entregables\diagramas\`

```
DCU-00 general.png          FIG-arquitectura.png     FIG-mapa-navegacion.png
DCU-01 … DCU-10.png         FIG-conceptual.png       FIG-mer.png
FIG-cronograma.png          FIG-encuesta-formulario.png    FIG-moscow.png
FIG-fisico.png              FIG-encuesta-resultados.png    FIG-permisos.png
FIG-scrum.png               FIG-encuesta-contraste.png     FIG-stakeholders.png
```

**Capturas de la aplicación** (todas `.jpg`, 1568 × 726), en:
`D:\01. Proyectos\Mediapp\docs tesis\insumos\capturas\`

```
IU-01 inicio de sesion.jpg              MOD-01 … MOD-10 (un módulo cada una)
IU-02 panel del administrador.jpg       CP-01a historia clinica formulario.jpg
IU-03 panel del medico.jpg              CP-01b historia clinica creada.jpg
IU-04 panel del paciente.jpg            CP-02a cita en conflicto formulario.jpg
IU-05 calendario de disponibilidad.jpg  CP-02b cita en conflicto rechazada.jpg
                                        CP-03a historias vistas por el administrador.jpg
                                        CP-03b administrador rechazado al crear historia.jpg
                                        CP-04a paciente reserva su turno.jpg
                                        CP-04b cita agendada por el paciente.jpg
```

**Plantilla:** `D:\01. Proyectos\Mediapp\docs tesis\exposicion\Plantilla institucional.pptx`

## 7. Cómo quiero que se vea

- **Una idea por diapositiva.** Si hay dos, son dos diapositivas.
- **Máximo seis líneas de texto** por diapositiva, y ninguna de más de dos renglones.
- Las diapositivas con figura le dan a la imagen **al menos la mitad del espacio**, y el texto
  acompaña, no compite.
- El color de las figuras del proyecto es el morado **`#9B59B6`**, con **`#8E44AD`** para los
  tonos oscuros. Si necesitas acentos, sal de ahí.
- Numera las diapositivas desde la tercera.
- Cada sección abre con una diapositiva divisoria que solo lleva su número romano y su nombre.

## 8. Antes de darlo por terminado

Comprueba, y dime si algo no se cumple:

1. El cronograma de la diapositiva 9 es el archivo `FIG-cronograma.png`, sin rehacer.
2. Ninguna diapositiva tiene guion largo, punto medio ni el patrón «afirmación: explicación».
3. Las cuatro diapositivas de evidencia llevan sus dos imágenes lado a lado.
4. Ninguna cifra aparece que no esté en el §4 de este prompt.
5. Los tres objetivos específicos aparecen literales en la diapositiva 6 y vuelven a aparecer en
   la 37, cada uno con la evidencia que lo sostiene.
6. Ninguna diapositiva habla de la presentación, del documento escrito ni de la evaluación
   anterior.

**Empieza proponiéndome el esquema completo de las 38 diapositivas con su título y su idea única,
y espera mi visto bueno antes de generar nada.**
