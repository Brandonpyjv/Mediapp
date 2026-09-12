# Guía del desarrollador — MediApp

Para quien recibe el proyecto y necesita entender cómo funciona antes de tocarlo.

Esta guía cuenta **cómo se mueve la información** de punta a punta, qué habla con qué, qué hace
cada ruta y dónde vive cada regla. Es la puerta de entrada; cuando necesites el detalle de una
decisión, `ARQUITECTURA.md` lo explica a fondo y `BASE_DE_DATOS.md` cubre el esquema.

| Si buscas… | Ve a |
|---|---|
| Instalar y arrancar | `README.md` |
| Entender cómo funciona (este documento) | `GUIA_DEL_DESARROLLADOR.md` |
| El porqué de cada decisión técnica | `ARQUITECTURA.md` |
| El esquema, las tablas y las migraciones | `BASE_DE_DATOS.md` |
| Los permisos por rol, que mandan sobre todo | `CLAUDE.md` §2 |

---

## 1. Qué es, en una frase

Una aplicación web donde **el paciente agenda su propia cita** eligiendo un turno libre en un
calendario, y donde **solo el médico que atiende puede escribir en la historia clínica**.

Casi todo el valor del sistema está en **lo que impide**, no en lo que guarda. Esa idea explica
por qué el código está escrito como está, y es lo que hay que tener en la cabeza al modificarlo.

---

## 2. Las piezas y quién habla con quién

No hay microservicios ni capas de framework escondidas. Son cinco archivos de Python, unas
plantillas HTML y una base de datos.

```
   NAVEGADOR
      │  HTTP (formularios HTML y dos llamadas fetch)
      ▼
   index.py ──────────────► Flask: las 53 rutas, los permisos y las reglas de negocio
      │   │   │
      │   │   └──► date_validators.py   fechas, zona horaria de Colombia
      │   └──────► validators.py        formato de correo electrónico
      │
      ├──► templates/*.html   Jinja2 pinta el HTML en el servidor
      │
      ▼
   database.py ──────────► pool de conexiones, UNA por petición
      │
      ▼
   MySQL / MariaDB   base `mediapp`, 11 tablas
```

**Lo que hay que retener:** `index.py` es el centro. Toda escritura pasa por él, y por eso todas
las reglas se pueden hacer cumplir en un solo sitio. No hay una segunda puerta de entrada a la
base de datos.

| Archivo | Qué hace |
|---|---|
| `index.py` | La aplicación entera. Rutas, permisos, validaciones y consultas SQL. |
| `database.py` | Consigue una conexión a MySQL y la devuelve al terminar la petición. |
| `date_validators.py` | Interpreta y valida fechas en la zona horaria de Colombia. |
| `validators.py` | Valida el formato del correo electrónico. |
| `templates/` | Las plantillas Jinja2, una carpeta por módulo. |
| `Base/mediapp.sql` | El volcado con el esquema y los datos de demostración. |
| `Base/seed_demo.py` | Regenera los datos de demostración con fechas de hoy. |
| `tests/` | Las 91 pruebas automatizadas. |

---

## 3. Cómo funcionan las conexiones

Es la parte que más se malentiende, así que va con detalle.

### Una conexión por petición, sacada de un pool

`database.py` mantiene un **pool de 10 conexiones**. Cuando entra una petición, Flask saca una del
pool y la guarda en `g` (el objeto de contexto de la petición). Cuando la petición termina, la
conexión vuelve al pool con un `rollback()`.

En las rutas se usa siempre igual, `db.conexion`, y eso siempre significa «la conexión de la
petición que estoy atendiendo ahora». El truco está en que `database.py` **no declara una variable
llamada `conexion`**, sino que la resuelve al momento de leerla con el `__getattr__` de módulo. Si
alguien declarara esa variable global, Python la devolvería sin preguntar y todas las peticiones
volverían a compartir una sola conexión.

### Por qué no es una conexión global

Antes lo era, y traía dos problemas serios.

**Hilos.** Flask sirve con hilos, y las conexiones de `mysql-connector` no son seguras entre
hilos. Dos peticiones simultáneas se intercalaban sobre el mismo socket y podían cruzar
resultados en cualquier consulta.

**La transacción que nunca se cerraba.** `mysql-connector` no confirma sola. El primer `SELECT`
abría una transacción que no se cerraba jamás, así que la conexión seguía leyendo **la misma foto
de la base durante días**. Ese era el famoso síntoma de «los cambios hechos por phpMyAdmin no se
ven hasta reiniciar Flask». No era un caché, era una transacción abierta. El `rollback()` al
devolver la conexión al pool es lo que lo cierra.

### Configuración

Sale de variables de entorno, con los valores de XAMPP por omisión. **No hay que editar código**
para cambiar de servidor.

```
MEDIAPP_DB_HOST      localhost
MEDIAPP_DB_USER      root
MEDIAPP_DB_PASSWORD  (vacía)
MEDIAPP_DB           mediapp
```

De esto vive también la suite de pruebas, que apunta a `mediapp_test` poniendo `MEDIAPP_DB` antes
de importar la aplicación. Por eso ninguna prueba puede escribir por error en tu base de trabajo.

### La llave de sesión

Flask firma la cookie de sesión con una llave secreta que **no está en el código**, porque quien
la conozca puede fabricar una cookie válida y entrar como administrador sin contraseña. En
desarrollo se crea sola en `.flask_secret`, que está en `.gitignore`. En un servidor de verdad se
define `MEDIAPP_SECRET_KEY` y esa manda.

---

## 4. El recorrido de una petición

Sigamos una escritura real, un paciente reservando su cita, que es el camino donde se aplican
todas las reglas a la vez.

1. **El navegador envía un POST** a `/addCI` desde el calendario, con un campo oculto
   `origen=calendario`.

2. **`before_request` comprueba la sesión.** Consulta el estado de la cuenta en la base. Si al
   usuario lo desactivaron mientras tenía la sesión abierta, se le cierra aquí. No basta con
   bloquear el login, porque una cuenta desactivada no debe seguir operando.

3. **La ruta decide el permiso.** `addCI` no lleva decorador, porque el permiso depende de por
   dónde entra la petición. El administrador puede por cualquier vía; el paciente **solo desde el
   calendario**, porque el formulario completo permite elegir a qué paciente se le agenda y esa
   elección no es suya; el médico nunca.

4. **La identidad sale de la sesión.** Si quien agenda es un paciente, el `id_paciente` se toma de
   `_current_paciente_id()` y **el que venga en el formulario se ignora por completo**. Si se
   tomara del POST, un paciente podría agendarle una cita a otro manipulando la petición.

5. **Se valida la fecha** con `date_validators`, que rechaza las citas en el pasado usando la hora
   de Colombia y no la del servidor.

6. **Se comprueban y se reservan las dos reglas de negocio** con
   `_check_appointment_conflicts(..., bloquear=True)`. Esto es una sola operación, no dos, y la
   sección 6 explica por qué importa.

7. **Se inserta y se confirma.** El `commit()` suelta los candados.

8. **Se redirige** de vuelta al calendario con un mensaje flash.

Si algo falla en cualquier paso, se responde con el mensaje y **no se escribe nada**.

---

## 5. Las 53 rutas

El nombre sigue un patrón fijo. `xxMC` es el listado del módulo, y después vienen `addXX`,
`editXX`, `deleteXX`. Las que cambian datos son siempre `POST`.

**Las guardas** son tres decoradores. `@login_required` exige sesión iniciada, `@admin_required`
exige rol administrador, y `@medico_required` exige rol médico **y además** que la cuenta esté
vinculada a una ficha de médico, porque una cuenta con rol médico pero sin ficha no puede firmar
nada.

### Sesión

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/login` | GET, POST | ninguna | Valida credenciales, guarda el rol en la sesión y redirige a `/`. |
| `/logout` | GET | ninguna | Cierra la sesión. |
| `/register` | GET, POST | ninguna | Registro público. Crea siempre una cuenta de **paciente** (`id_rol = 2`). |
| `/` | GET | login | El panel. **Aquí ocurre la diferenciación por rol.** |

Conviene precisar cómo funciona el «acceso diferenciado», porque no está donde uno lo buscaría.
`/login` **no** manda a tres direcciones distintas, siempre redirige a `/`. Es `menu.html` el que
ramifica con `{% if session['rol'] == 'admin' %}` y pinta un panel distinto para cada rol. El
efecto para el usuario es el pedido, que al entrar caiga en lo suyo sin elegir perfil, pero si
buscas la bifurcación en el `login()` no la vas a encontrar.

Y ojo con la consecuencia: **que el menú no pinte un botón no protege nada**. Lo que protege son
las guardas de cada ruta. El menú decide qué se ve; el decorador decide qué se puede hacer.

### Usuarios, médicos, pacientes y catálogos (del administrador)

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/usMC` | GET | admin | Listado de usuarios. |
| `/addUS` `/editUS/<id>` | GET, POST | admin | Alta y edición de cuentas. |
| `/deleteUS/<id>` `/reactivateUS/<id>` | POST | admin | Baja **lógica** y reactivación. |
| `/medMC` | GET | admin | Listado de médicos. |
| `/addMED` `/editMED/<id>` | GET, POST | admin | Alta y edición de la ficha profesional. |
| `/deleteMED/<id>` `/reactivateMED/<id>` | POST | admin | Baja lógica y reactivación. |
| `/toggleAccesoMED/<id>` | POST | admin | Activa o corta el acceso del médico sin borrar su ficha. |
| `/paMC` | GET | login | Listado de pacientes. El paciente solo se ve a sí mismo. |
| `/addPA` `/editPA/<id>` | GET, POST | admin | Alta y edición de pacientes. |
| `/deletePA/<id>` `/reactivatePA/<id>` | POST | admin | Baja lógica y reactivación. |
| `/esMC` `/addES` `/editES/<id>` `/deleteES/<id>` | varios | admin | Catálogo de especialidades. |
| `/meMC` `/addME` `/editME/<id>` `/deleteME/<id>` `/reactivateME/<id>` | varios | admin | Catálogo de medicamentos. |

### Citas

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/ciMC` | GET | login | Listado. **Filtra por rol**, el médico ve las suyas y el paciente las suyas. |
| `/disponibilidad` | GET | login | El calendario semanal de turnos libres. |
| `/api/disponibilidad-semana` | GET | login | JSON que alimenta el calendario. |
| `/addCI` | GET, POST | *ver abajo* | Crea la cita. Permiso decidido **dentro** de la ruta. |
| `/editCI/<id>` | GET, POST | admin | Reprograma. Rechaza citas pasadas o canceladas. |
| `/cancelCI/<id>` | POST | login | Cancela. El paciente puede cancelar **la suya**. |
| `/deleteCI/<id>` | POST | admin | Elimina. |

`/addCI` es la única ruta **sin decorador**, y es a propósito. El permiso depende del origen de la
petición, así que se resuelve dentro con el criterio del punto 3 de la sección anterior. La otra
ruta que decide por dentro es `editEX`, más abajo.

### Acto clínico (exclusivo del médico)

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/hiMC` | GET | login | Listado de historias clínicas, filtrado por rol. |
| `/addHI` `/editHI/<id>` `/deleteHI/<id>` | varios | **medico** | Crear, editar y eliminar historia clínica. |
| `/coMC` | GET | login | Listado de consultas y diagnósticos. |
| `/addCO` `/editCO/<id>` `/deleteCO/<id>` | varios | **medico** | Diagnóstico y plan de tratamiento. |
| `/reMC` | GET | login | Listado de recetas. |
| `/addRE` `/editRE/<id>` `/deleteRE/<id>` | varios | **medico** | Prescripciones. |

Aquí está la restricción central del sistema. Los listados son `@login_required` porque el
administrador y el paciente **pueden leer**; las escrituras son `@medico_required`, así que el
administrador queda bloqueado aunque escriba la dirección a mano.

### Exámenes de laboratorio

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/exMC` | GET | login | Listado. |
| `/addEX` | GET, POST | **medico** | El médico **solicita** el examen. |
| `/editEX/<id>` | GET, POST | login + *ver abajo* | Permisos **divididos por campo**. |
| `/deleteEX/<id>` | POST | admin | Elimina. |

El reparto es intencional. Quien pide el examen es el médico, quien sube el resultado es el
laboratorio, que en este sistema es el administrador.

`editEX` es la segunda ruta que resuelve el permiso por dentro, y la única que lo divide **campo
por campo**. Lleva `@login_required`, rechaza a cualquiera que no sea médico o administrador, y
después reparte:

- el **médico que lo solicitó** corrige la solicitud, o sea paciente, tipo de examen y fecha de
  solicitud;
- el **administrador** carga el resultado, o sea la fecha y los hallazgos, y **no puede tocar la
  solicitud**.

Si tocas esta ruta, ten presente que el decorador no te cubre. La comprobación real está en el
cuerpo.

### Detalle

| Ruta | Método | Guarda | Qué hace |
|---|---|---|---|
| `/api/view/<module>/<id>` | GET | login | Devuelve un registro en JSON para el modal de detalle. |

Es **de solo lectura**. Antes existía un `api/save` gemelo que escribía, y se eliminó: dos caminos
de escritura hacia la misma tabla son dos sitios donde aplicar las mismas reglas, y tarde o
temprano uno de los dos se queda atrás. Además comprueba el rol **por módulo**, así que ver una
cita ajena por esta vía no es posible solo por tener sesión iniciada.

---

## 6. La lógica de negocio, y cómo está hecha

### Las dos reglas de la agenda

1. Entre dos citas del **mismo médico** deben mediar al menos **30 minutos**.
2. Un **paciente** no puede tener más de una cita **el mismo día**.

Las dos viven en `_check_appointment_conflicts()`, y las llaman `addCI` y `editCI`.

**Por qué no son restricciones de la base de datos.** Un `UNIQUE` prohíbe un *valor repetido*, y
esto no es un valor repetido sino **una distancia entre valores**. La base no puede expresar «que
no exista otra cita a menos de treinta minutos de esta». Por eso se comprueban en el servidor,
dentro de la misma operación que escribe. Es la pregunta técnica más probable en la sustentación.

Las citas canceladas se ignoran en las dos reglas, porque un horario cancelado vuelve a estar
libre.

### La reserva es atómica

Comprobar y luego insertar deja una ventana entre las dos operaciones. Si dos pacientes piden el
mismo turno a la vez, los dos comprueban, ninguno ve nada todavía, y los dos insertan.

La solución es que comprobar **sea** reservar. Con `bloquear=True`, las dos consultas se hacen
`FOR UPDATE`, lo que logra dos cosas a la vez:

- Leen la última versión confirmada de la base, no la foto que la transacción venía leyendo, así
  que sí ven la cita que otro acaba de confirmar.
- Dejan un candado sobre las filas leídas **y sobre los huecos entre ellas**, de modo que la
  segunda petición se queda esperando en su propia comprobación en vez de insertar.

El candado se suelta con el `commit()`. No bloquea la tabla entera: las consultas entran por
índice, así que se bloquea la agenda de ese médico y la de ese paciente, y dos reservas para
médicos distintos no se estorban.

> ⚠️ **Si escribes código que llame a esta función con `bloquear=True`, tienes que confirmar o
> deshacer enseguida.** Hasta que lo hagas, nadie más puede agendarle a ese médico ni a ese
> paciente.

### La autoría sale de la sesión, nunca del formulario

El mismo patrón en cuatro sitios, historia, consulta, receta y cita. El identificador de quien
firma se obtiene con `_current_medico_id()` o `_current_paciente_id()`, que lo leen de la sesión.
El campo equivalente que venga en el POST **se ignora**.

Es lo que impide que alguien firme un registro a nombre de otro manipulando la petición, y hay
pruebas automatizadas que envían el identificador de otra persona y comprueban que el registro
queda a nombre de quien tiene la sesión.

### Nada se borra

«Eliminar» un usuario, un médico, un paciente o un medicamento es `UPDATE ... SET estado =
'inactivo'`. Cancelar una cita es `UPDATE ... SET estado = 'cancelada'`.

La razón es que un registro borrado se lleva por delante lo que cuelga de él. Un paciente
eliminado se llevaría sus historias y sus citas, que son justamente el historial del centro. Por
eso las claves foráneas de `historia`, `consulta` y `examen` son `RESTRICT` explícito.

### El filtro de tres vías

Se repite en todos los listados y conviene reconocerlo, porque es el patrón que hay que copiar al
agregar un módulo nuevo:

```python
if rol == 'admin':      # lo ve todo
elif rol == 'medico':   # solo lo suyo, por _current_medico_id()
else:                   # solo lo suyo, por la sesión del paciente
```

**El filtro de rol se aplica antes de paginar, nunca después.** Si se pagina primero, la página 1
puede traer filas de otro paciente y luego descartarlas, y el usuario ve una página medio vacía
sin entender por qué. Peor todavía, las filas ajenas ya viajaron desde la base.

---

## 7. Cómo agregar algo sin romper nada

1. **Lee `CLAUDE.md` §2 primero.** La matriz de permisos por rol es la fuente autoritativa y manda
   sobre cualquier otra cosa.
2. **Copia el patrón de un módulo parecido.** Los diez módulos están escritos igual a propósito.
3. **Si la ruta escribe, ponle guarda.** Y si el permiso depende del origen de la petición, como
   en `addCI`, resuélvelo dentro y **déjalo comentado**.
4. **Si el registro tiene autor, tómalo de la sesión.** Nunca del formulario.
5. **Si eliminas, no elimines.** Marca el estado.
6. **Escribe la prueba.** Las reglas de este sistema son invisibles cuando se rompen, porque un
   control que deja de aplicarse no produce ningún error, solo permite algo que no debería.
7. **Corre `python -m pytest`** antes de dar nada por terminado.

---

## 8. Las pruebas

91 pruebas en seis archivos, en unos 7 segundos. Trabajan contra `mediapp_test`, que se crea y se
destruye sola clonando el esquema de `mediapp`, así que **no tocan tu base**.

| Archivo | Cuántas | Qué cubre |
|---|---|---|
| `test_permisos.py` | 32 | Qué puede hacer cada rol y qué no. |
| `test_citas.py` | 26 | Las dos reglas de la agenda y las fechas. |
| `test_datos.py` | 17 | Restricciones, claves foráneas y bajas lógicas. |
| `test_autenticacion.py` | 10 | Sesión, login y derivación de contraseñas. |
| `test_andamiaje.py` | 4 | Que la base de pruebas se arme bien. |
| `test_concurrencia.py` | 2 | Dos reservas simultáneas del mismo turno. |

Que el archivo más grande sea el de permisos no es casualidad: es donde está el valor del sistema.

---

## 9. Trampas conocidas

**`db.conexion` no es una variable, es una función disfrazada.** Se resuelve cada vez que se lee.
No la guardes en una variable local que sobreviva a la petición.

**Las fechas van en hora de Colombia.** Usa `date_validators`, no `datetime.now()` pelado, o las
validaciones de «cita en el pasado» fallarán según dónde corra el servidor.

**Una cuenta con rol médico puede no tener ficha de médico.** Quedan dos así en los datos de
demostración, residuo de cuando eliminar un médico lo borraba de verdad. `@medico_required` lo
detecta y avisa; si escribes una ruta de médico sin ese decorador, fallará con un error de base de
datos incomprensible.

**`john.hernandez` no entra.** Su cuenta está inactiva a propósito, para poder ver la baja lógica
funcionando. Se reactiva desde Usuarios con la sesión de `admin`.

**Los datos de demostración envejecen.** Las fechas son relativas al día en que se generaron, así
que la «agenda futura» queda atrás con el tiempo. Se refresca con `python Base/seed_demo.py`.
