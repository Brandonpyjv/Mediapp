# MediApp

Sistema web de **agendamiento de citas clínicas** desarrollado con **Flask** y **MySQL/MariaDB**.

Permite gestionar pacientes, médicos, especialidades, citas, consultas, historias clínicas,
exámenes de laboratorio, medicamentos y recetas, con control de acceso por roles
(Administrador, Médico y Paciente).

> 📖 **¿Vas a trabajar sobre el código?** Este README te deja el proyecto corriendo. Para entender
> **cómo funciona** por dentro, lee después **[`GUIA_DEL_DESARROLLADOR.md`](GUIA_DEL_DESARROLLADOR.md)**,
> que explica el recorrido de una petición, las 53 rutas y dónde vive cada regla de negocio.

---

## Requisitos previos

Antes de empezar necesitas tener instalado:

| Software | Versión | Notas |
|---|---|---|
| **Python** | 3.9 o superior | Probado en 3.13. Marca *"Add Python to PATH"* al instalar. |
| **XAMPP** | cualquiera reciente | Se usa por su servidor **MySQL/MariaDB** y **phpMyAdmin**. |
| **Git** | cualquiera | Para clonar el repositorio. |

> No hace falta Apache: el proyecto trae su propio servidor web. De XAMPP solo se usa la base de datos.

> **XAMPP no es obligatorio.** Sirve igual un **MySQL Server** o un **MariaDB** instalados por su
> cuenta, que es como está montada la máquina de desarrollo. Lo único que el proyecto necesita es
> un servidor MySQL o MariaDB al que pueda conectarse. Si usas uno independiente, el cliente de
> línea de comandos suele estar en `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`, y si
> tu instalación pide contraseña para `root`, defínela como dice el paso 6.

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Brandonpyjv/Mediapp.git
cd Mediapp
```

### 2. Crear un entorno virtual (recomendado)

Aísla las librerías del proyecto para no ensuciar tu instalación global de Python.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Sabrás que funcionó porque aparece `(venv)` al inicio de la línea de tu terminal.

> Si en PowerShell te sale un error de *"ejecución de scripts está deshabilitada"*, ejecuta:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Levantar la base de datos

1. Abre el **Panel de Control de XAMPP**.
2. Pulsa **Start** en el módulo **MySQL**.
   *(No hace falta arrancar Apache.)*

### 5. Importar la base de datos

El archivo `Base/mediapp.sql` ya incluye la instrucción `CREATE DATABASE`, así que **no necesitas
crear la base de datos a mano**: se crea sola al importar. Elige una de las dos opciones:

**Opción A — phpMyAdmin (más fácil)**
1. Entra a <http://localhost/phpmyadmin>
2. Ve a la pestaña **Importar**.
3. **Seleccionar archivo** → elige `Base/mediapp.sql` del proyecto.
4. Baja hasta el final y pulsa **Importar** / **Continuar**.

**Opción B — Línea de comandos**
```bash
C:\xampp\mysql\bin\mysql.exe -u root < Base/mediapp.sql
```
*(Ajusta la ruta si instalaste XAMPP en otra carpeta. En Linux/macOS basta con `mysql -u root`.)*

> ⚠️ **Cuidado si ya tenías la base de datos creada.** Este archivo borra y vuelve a crear las 11
> tablas (`DROP TABLE IF EXISTS`), así que **reemplaza cualquier dato que tuvieras** por los datos
> de ejemplo. Si ya venías trabajando con información propia, haz una copia de seguridad antes
> (en phpMyAdmin: pestaña **Exportar**).

Al terminar deberías ver la base de datos `mediapp` con **11 tablas**:
`cita`, `consulta`, `especialidad`, `examen`, `historia`, `medicamento`, `medico`, `paciente`,
`receta`, `rol`, `usuario`.

### 6. Configurar la conexión (solo si hace falta)

Por defecto el proyecto se conecta con la configuración estándar de XAMPP
(usuario `root`, **sin contraseña**, base `mediapp`). **No hace falta tocar el código**: si tu
MySQL tiene otra configuración, se cambia con variables de entorno.

```bash
set MEDIAPP_DB_HOST=localhost
set MEDIAPP_DB_USER=root
set MEDIAPP_DB_PASSWORD=tu_contraseña
set MEDIAPP_DB=mediapp
```

En PowerShell es `$env:MEDIAPP_DB_PASSWORD = "tu_contraseña"`, y en Linux o macOS `export`.
Cualquiera que no definas conserva el valor de XAMPP.

### 6.1. La llave de sesión

Flask firma la cookie de sesión con una llave secreta. **No está en el código**, porque quien la
conozca puede fabricar una cookie válida y entrar como administrador sin contraseña.

- **En desarrollo no tienes que hacer nada:** la primera vez que arranques, el proyecto crea el
  archivo `.flask_secret` con una llave aleatoria y la reutiliza en los arranques siguientes, así
  que tu sesión no se cae cada vez que el recargador reinicia. Ese archivo está en `.gitignore` y
  **no se sube nunca**.
- **En un servidor de verdad**, define `MEDIAPP_SECRET_KEY` en el entorno y esa manda sobre el
  archivo.

---

## Cómo arrancar el proyecto

Con el entorno virtual activado y **MySQL corriendo en XAMPP**:

```bash
python index.py
```

Abre <http://127.0.0.1:5000>

Para detener el servidor: `Ctrl + C`.

### Recarga automática

**No necesitas cerrar y reabrir el programa cada vez que cambias algo.** El proyecto arranca con
`debug=True`, así que el servidor de desarrollo de Flask trae la recarga incorporada: guardas un
archivo `.py` y se reinicia solo. También muestra una página de error detallada en el navegador
cuando algo falla, lo que ayuda mucho a depurar.

Para los cambios en plantillas HTML y CSS basta con refrescar el navegador con `Ctrl + F5`.

---

## Credenciales de prueba

La base de datos de ejemplo trae estos usuarios:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `12345` | Administrador |
| `tete` | `12345` | Paciente |
| `angel.quinones` | `Medico123` | Médico |
| `paulino.velandia` | `Medico123` | Médico |

> `john.hernandez` también existe con `Medico123`, pero su cuenta está **inactiva** y por eso el
> login la rechaza. Está así a propósito, para poder ver la baja lógica funcionando. Si quieres
> entrar con ella, reactívala desde **Usuarios** con la sesión de `admin`.

> 🔒 **Son credenciales de demostración de un entorno local.** No las uses en un despliegue real y
> cámbialas antes de publicar el proyecto en cualquier servidor accesible desde internet.

También puedes crear tu propia cuenta de paciente desde el botón **Registrarse** de la pantalla de
inicio de sesión.

### Datos de demostración

La base incluye una clínica en funcionamiento: **dos meses de historial** (citas atendidas,
consultas con diagnóstico, historias clínicas, exámenes y recetas) y **cuatro semanas de agenda
futura con turnos libres** para poder seguir agendando a mano. Vienen además 4 médicos y 54
pacientes adicionales; los médicos entran con `Medico123` y los pacientes con `Paciente123`.

Las fechas son relativas al día en que se generaron, así que con el tiempo la "agenda futura" queda
atrás. Para refrescarla:

```bash
python Base/seed_demo.py            # rehace los datos de demostración con fechas de hoy
python Base/seed_demo.py --limpiar  # los quita y deja solo los datos originales
```

El script respeta las reglas del sistema (30 minutos entre citas de un mismo médico, una cita por
paciente por día) y se niega a guardar nada si detecta un choque.

---

## Roles del sistema

| Rol | Qué puede hacer |
|---|---|
| **Administrador** | Gestiona usuarios, médicos, especialidades, pacientes y citas. Carga los resultados de los exámenes de laboratorio. Puede *ver* las historias clínicas, pero **no crearlas ni modificarlas**. |
| **Médico** | Crea y edita historias clínicas, diagnósticos y recetas. Solicita exámenes. Consulta su agenda de citas en **modo lectura**. |
| **Paciente** | Consulta sus propias citas, consultas y recetas. Puede cancelar sus citas. No modifica datos clínicos. |

---

## Estructura del proyecto

```
Mediapp/
├── GUIA_DEL_DESARROLLADOR.md # Cómo funciona el software: conexiones, rutas y lógica
├── ARQUITECTURA.md           # El porqué de cada decisión técnica
├── BASE_DE_DATOS.md          # Esquema, tablas y migraciones
├── index.py                  # Aplicación Flask: rutas, lógica y control de acceso
├── database.py               # Conexión a MySQL: un pool que da una conexión por petición
├── date_validators.py        # Validación de fechas (zona horaria de Colombia)
├── validators.py             # Otras validaciones de formulario (correo electrónico)
├── requirements.txt          # Dependencias de Python
├── pytest.ini                # Configuración de las pruebas
├── tests/                    # 91 pruebas automatizadas (ver más abajo)
├── Base/
│   ├── mediapp.sql           # Volcado de la base de datos (esquema + datos de ejemplo)
│   ├── seed_demo.py          # Datos de demostración con fechas relativas a hoy
│   └── migrations/           # Scripts de cambios al esquema, en orden
├── docs tesis/               # Generadores y entregables del trabajo de grado
└── templates/                # Plantillas HTML (Jinja2)
    ├── base.html             # Plantilla base y menú lateral
    ├── login.html
    ├── register.html
    ├── static/               # CSS, imágenes e íconos
    └── ...                   # Una carpeta por módulo (citas, pacientes, medicos, etc.)
```

## Pruebas automatizadas

El proyecto trae **91 pruebas**. Se corren desde la raíz, con MySQL arriba:

```bash
python -m pytest             # todas, unos 6 segundos
python -m pytest -v          # una línea por prueba
```

**No tocan tu base de datos.** Trabajan contra `mediapp_test`, que se crea y se destruye sola en
cada corrida clonando el esquema de `mediapp`. Por eso necesitas tener importada la base normal
antes de correrlas.

Cubren las reglas que no se pueden romper sin que nadie lo note: quién puede crear o modificar
una historia clínica, la separación mínima entre citas de un mismo médico, que un paciente no
tenga dos citas el mismo día, que nadie agende en el pasado, que dos personas pidiendo el mismo
turno a la vez no lo consigan las dos, que dar de baja no borre, y que ningún paciente alcance la
información de otro.

---

### Sobre las migraciones

La carpeta `Base/migrations/` contiene los cambios al esquema aplicados después del volcado inicial.

**No necesitas ejecutarlos si importaste `Base/mediapp.sql`**, porque ese archivo ya los incluye.
Solo son relevantes si tienes una base de datos antigua y quieres actualizarla sin perder tus datos.

---

## Solución de problemas

**`ModuleNotFoundError: No module named 'flask'`**
No activaste el entorno virtual o no instalaste las dependencias.
Repite los pasos 2 y 3.

**`2003: Can't connect to MySQL server on 'localhost'`**
MySQL no está corriendo. Abre el Panel de Control de XAMPP y pulsa **Start** en MySQL.

**`1049: Unknown database 'mediapp'`**
No importaste la base de datos. Vuelve al paso 5.

**`1045: Access denied for user 'root'@'localhost'`**
Tu MySQL tiene contraseña y el proyecto está configurado sin ella. **No edites `database.py`**,
define `MEDIAPP_DB_PASSWORD` en el entorno como se explica en el paso 6.

**El puerto 5000 está ocupado**
Cambia la última línea de `index.py` por:
```python
app.run(debug=True, port=5001)
```

**Cambié el código y no se refleja en el navegador**
Si tocaste un archivo `.py`, mira la consola: debería aparecer un mensaje de reinicio del servidor.
Si cambiaste HTML o CSS, refresca con `Ctrl + F5` para saltarte la caché del navegador.
