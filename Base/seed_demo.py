# -*- coding: utf-8 -*-
"""
seed_demo.py — Datos de demostración para MediApp
==================================================
Llena la base de datos con una clínica en funcionamiento: dos meses de
historial hacia atrás (citas atendidas, consultas con diagnóstico,
historias clínicas, exámenes de laboratorio y recetas) y varias semanas de
agenda hacia adelante, **dejando huecos libres a propósito** para poder
seguir agendando a mano durante una demostración.

Cómo se usa:

    python Base/seed_demo.py            # siembra (si ya había demo, la rehace)
    python Base/seed_demo.py --limpiar  # solo borra los datos de demostración

Por qué es un script y no un `.sql` con INSERTs:

1. **Las fechas son relativas a hoy.** Un volcado fijo envejece: al mes
   siguiente la "agenda de las próximas semanas" ya estaría en el pasado.
   Aquí se recalcula en cada ejecución con la zona horaria de Colombia,
   la misma que usa la aplicación.
2. **Las contraseñas se hashean con `werkzeug` (scrypt)**, igual que las
   crea la aplicación. Un INSERT a mano dejaría cuentas sin poder entrar.
3. **Respeta las reglas de negocio ya implementadas** en vez de generar
   datos que las violen: mínimo 30 minutos entre citas de un mismo médico
   y máximo una cita por paciente por día. *(Ya pasó una vez: dos citas
   del seed original quedaron a 1 minuto y, al activar la regla de los 30
   minutos, se volvieron imposibles de editar.)*
4. **Se puede volver a ejecutar.** Anota lo que insertó en
   `Base/demo_seed_manifest.json` y lo borra antes de sembrar de nuevo,
   así que una migración futura no obliga a rehacer nada a mano.

Lo que **nunca** toca: los datos que ya existían (las cuentas `admin` y
`tete`, los médicos Angel y Paulino, los 6 pacientes originales y sus
registros). La demo se suma a eso; el historial se reparte también entre
los médicos y pacientes originales para que sus pantallas no se vean
vacías al iniciar sesión con ellos.
"""
import json
import os
import random
import sys
import unicodedata
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from werkzeug.security import generate_password_hash

import date_validators as dv

MANIFIESTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'demo_seed_manifest.json')

# --- Parámetros de la demo (tocar aquí para más o menos volumen) ----------
DIAS_HACIA_ATRAS = 60           # dos meses de historial
SEMANAS_HACIA_ADELANTE = 4      # agenda futura
PACIENTES_NUEVOS = 54
# Cuántas citas por día en toda la clínica. El techo real lo pone la regla
# de "una cita por paciente por día": con 60 pacientes no puede haber más
# de 60 citas diarias. Con estos números cada médico queda con 3-5 citas de
# sus 14 turnos diarios: se ve una agenda con trabajo real y con huecos
# libres evidentes para seguir agendando a mano.
CITAS_POR_DIA_PASADO = (16, 24)
CITAS_POR_DIA_FUTURO = (20, 28)
PROB_CITA_CANCELADA = 0.06
PROB_CONSULTA_TRAS_CITA = 0.72
PROB_RECETA_TRAS_CONSULTA = 0.6
PROB_EXAMEN_CON_RESULTADO = 0.65

# Horario de atención. El almuerzo (12:00-14:00) queda fuera a propósito, y
# los turnos van de 30 en 30 minutos, que es la separación mínima exigida
# entre citas de un mismo médico (MINUTOS_ENTRE_CITAS en index.py).
FRANJAS = [(8, 12), (14, 17)]

random.seed(20260902)   # dataset reproducible: la misma semilla, los mismos datos

# --- Catálogo de contenido clínico ---------------------------------------
PILA = [
    'Camila', 'Andrés', 'Valentina', 'Santiago', 'Isabella', 'Mateo', 'Sofía',
    'Sebastián', 'Mariana', 'Nicolás', 'Daniela', 'Tomás', 'Luciana', 'Emiliano',
    'Antonia', 'Martín', 'Gabriela', 'Samuel', 'Juliana', 'Alejandro', 'Paulina',
    'Felipe', 'Renata', 'Joaquín', 'Catalina', 'Esteban', 'Manuela', 'Julián',
    'Carolina', 'Diego', 'Adriana', 'Óscar', 'Natalia', 'Camilo', 'Ximena', 'Iván',
]
APELLIDOS = [
    'Restrepo', 'Gutiérrez', 'Ospina', 'Mejía', 'Cárdenas', 'Villamizar', 'Beltrán',
    'Rojas', 'Peñaloza', 'Arango', 'Cifuentes', 'Escobar', 'Bermúdez', 'Salazar',
    'Zapata', 'Cadena', 'Pineda', 'Otálora', 'Riaño', 'Nieto', 'Cuéllar',
    'Bustamante', 'Mosquera', 'Lozano', 'Acevedo', 'Rincón', 'Valderrama', 'Guzmán',
    'Cortés', 'Ariza', 'Prieto', 'Sandoval', 'Barrera', 'Espinosa', 'Trujillo', 'Vergara',
]

MEDICOS_NUEVOS = [
    ('Laura Jiménez',   'Pediatria',      'laura.jimenez'),
    ('Ricardo Ballén',  'Dermatología',   'ricardo.ballen'),
    ('Marcela Ordóñez', 'Ginecólogo',     'marcela.ordonez'),
    ('Hernán Castaño',  'Oftalmología',   'hernan.castano'),
]

MOTIVOS = [
    'Control de rutina', 'Dolor abdominal persistente', 'Cefalea recurrente',
    'Control de presión arterial', 'Revisión de resultados de laboratorio',
    'Cuadro gripal', 'Dolor lumbar', 'Control de tratamiento',
    'Erupción en la piel', 'Malestar general y fiebre', 'Chequeo anual',
    'Seguimiento posoperatorio', 'Dificultad para dormir', 'Dolor de garganta',
]

DIAGNOSTICOS = [
    ('Infección respiratoria alta', 'Reposo, hidratación y antibiótico por 7 días'),
    ('Hipertensión arterial controlada', 'Continuar antihipertensivo y dieta baja en sodio'),
    ('Gastritis aguda', 'Protector gástrico por 14 días y evitar irritantes'),
    ('Migraña sin aura', 'Analgésico en crisis y control de factores desencadenantes'),
    ('Lumbalgia mecánica', 'Antiinflamatorio por 5 días y terapia física'),
    ('Dermatitis de contacto', 'Crema tópica dos veces al día por 10 días'),
    ('Faringitis bacteriana', 'Antibiótico por 7 días y control en una semana'),
    ('Anemia ferropénica leve', 'Suplemento de hierro por 3 meses y control'),
    ('Diabetes tipo 2 en control', 'Mantener metformina y control nutricional'),
    ('Conjuntivitis alérgica', 'Colirio antihistamínico y evitar alérgenos'),
    ('Cuadro viral inespecífico', 'Manejo sintomático e hidratación abundante'),
    ('Control prenatal normal', 'Ácido fólico, control en cuatro semanas'),
]

ANTECEDENTES = [
    ('Antecedentes familiares de hipertensión', 'Padre y abuelo con diagnóstico temprano'),
    ('Alergia documentada a la penicilina', 'Reacción cutánea registrada en 2019'),
    ('Cirugía de apendicectomía', 'Procedimiento sin complicaciones'),
    ('Antecedente de asma en la infancia', 'Sin crisis en los últimos años'),
    ('Fumador ocasional', 'Se recomienda cesación; acepta seguimiento'),
    ('Antecedentes familiares de diabetes', 'Madre con diagnóstico tipo 2'),
    ('Fractura de radio derecho', 'Consolidada, sin secuelas funcionales'),
    ('Intolerancia a la lactosa', 'Manejo dietario, sin medicación'),
    ('Control de peso y actividad física', 'Plan de ejercicio tres veces por semana'),
    ('Migrañas recurrentes desde la adolescencia', 'Responde bien al tratamiento habitual'),
]

EXAMENES = [
    ('Hemograma completo', 'Valores dentro de los rangos normales'),
    ('Glucemia en ayunas', 'Glucosa en 92 mg/dL, dentro de lo esperado'),
    ('Perfil lipídico', 'Colesterol total levemente elevado, se sugiere dieta'),
    ('Uroanálisis', 'Sin evidencia de infección urinaria'),
    ('Radiografía de tórax', 'Campos pulmonares libres, sin hallazgos'),
    ('Ecografía abdominal', 'Órganos de tamaño y ecogenicidad normales'),
    ('Prueba de función hepática', 'Transaminasas dentro de rangos normales'),
    ('Electrocardiograma', 'Ritmo sinusal, sin alteraciones agudas'),
    ('Hemoglobina glicosilada', 'HbA1c en 6.1%, control aceptable'),
    ('Cultivo de secreción faríngea', 'Aislamiento de estreptococo del grupo A'),
]

MEDICAMENTOS_NUEVOS = [
    ('Amoxicilina', 'Antibiótico betalactámico de amplio espectro', '500 mg'),
    ('Ibuprofeno', 'Antiinflamatorio no esteroideo', '400 mg'),
    ('Omeprazol', 'Inhibidor de la bomba de protones', '20 mg'),
    ('Losartán', 'Antihipertensivo antagonista de receptores', '50 mg'),
    ('Metformina', 'Antidiabético oral', '850 mg'),
    ('Loratadina', 'Antihistamínico de segunda generación', '10 mg'),
    ('Salbutamol', 'Broncodilatador inhalado', '100 mcg'),
    ('Sulfato ferroso', 'Suplemento de hierro', '300 mg'),
    ('Acetaminofén', 'Analgésico y antipirético', '500 mg'),
    ('Naproxeno', 'Antiinflamatorio no esteroideo', '250 mg'),
    ('Hidrocortisona tópica', 'Corticoide de uso dermatológico', '1%'),
    ('Ácido fólico', 'Suplemento vitamínico para el embarazo', '1 mg'),
]

INDICACIONES = [
    'Cada 8 horas después de las comidas',
    'Una vez al día en ayunas',
    'Cada 12 horas por 7 días',
    'Aplicar en la zona afectada dos veces al día',
    'Cada 8 horas solo si hay dolor',
    'Una vez al día antes de dormir',
]

DIRECCIONES = [
    'Calle 45 #12-34', 'Carrera 7 #80-15', 'Avenida 68 #40-22', 'Calle 100 #19-51',
    'Carrera 15 #93-60', 'Diagonal 34 #22-18', 'Transversal 21 #56-09',
    'Calle 26 #68-30', 'Carrera 30 #45-77', 'Calle 72 #10-42',
]


def conectar():
    return mysql.connector.connect(host='localhost', user='root', passwd='',
                                   database='mediapp', charset='utf8mb4')


def clave_comparacion(texto):
    """Normaliza como lo hace la base de datos al comparar.

    La colación de la BD es `utf8mb4_general_ci`: ignora mayúsculas **y
    tildes**, así que para el índice UNIQUE de `medicamento.nombre` un
    "Losartán" nuevo choca contra el "Losartan" que ya existía. Comparar
    con `==` de Python no detecta eso y el INSERT falla.
    """
    return (unicodedata.normalize('NFD', texto or '')
            .encode('ascii', 'ignore').decode('ascii').lower().strip())


def cargar_manifiesto():
    if os.path.exists(MANIFIESTO):
        with open(MANIFIESTO, encoding='utf-8') as f:
            return json.load(f)
    return {}


def guardar_manifiesto(datos):
    with open(MANIFIESTO, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2)


def limpiar(cn):
    """Borra lo que sembró la ejecución anterior, en orden seguro para las
    claves foráneas. Lo que no esté en el manifiesto no se toca."""
    manifiesto = cargar_manifiesto()
    if not manifiesto:
        print('No hay datos de demostración previos que borrar.')
        return
    cursor = cn.cursor()
    orden = [
        ('receta', 'id_receta'), ('examen', 'id_examen'), ('historia', 'id_historia'),
        ('consulta', 'id_consulta'), ('cita', 'id_cita'), ('medico', 'id_medico'),
        ('paciente', 'id_paciente'), ('usuario', 'id_usuario'),
        ('medicamento', 'id_medicamento'),
    ]
    for tabla, pk in orden:
        ids = manifiesto.get(tabla, [])
        if not ids:
            continue
        marcas = ','.join(['%s'] * len(ids))
        cursor.execute(f"DELETE FROM {tabla} WHERE {pk} IN ({marcas})", tuple(ids))
        print(f'  {tabla}: {cursor.rowcount} filas borradas')
    cn.commit()
    cursor.close()
    if os.path.exists(MANIFIESTO):
        os.remove(MANIFIESTO)


def turnos_del_dia(dia):
    """Todos los turnos de 30 minutos de un día, dentro del horario de
    atención. El almuerzo queda fuera por diseño."""
    turnos = []
    for desde, hasta in FRANJAS:
        hora = datetime(dia.year, dia.month, dia.day, desde, 0)
        fin = datetime(dia.year, dia.month, dia.day, hasta, 0)
        while hora < fin:
            turnos.append(hora)
            hora += timedelta(minutes=30)
    return turnos


def sembrar(cn):
    cursor = cn.cursor(dictionary=True)
    manifiesto = {t: [] for t in ['usuario', 'paciente', 'medico', 'cita', 'consulta',
                                  'historia', 'examen', 'medicamento', 'receta']}

    hoy = dv.today_colombia()

    # --- Catálogos existentes que se reutilizan --------------------------
    cursor.execute("SELECT id_especialidad, nombre FROM especialidad")
    especialidades = {e['nombre']: e['id_especialidad'] for e in cursor.fetchall()}
    cursor.execute("SELECT id_rol FROM rol WHERE nombre_rol = 'medico'")
    rol_medico = cursor.fetchone()['id_rol']
    cursor.execute("SELECT id_rol FROM rol WHERE nombre_rol = 'paciente'")
    rol_paciente = cursor.fetchone()['id_rol']

    # --- Medicamentos ----------------------------------------------------
    cursor.execute("SELECT nombre FROM medicamento")
    ya_existen = {clave_comparacion(m['nombre']) for m in cursor.fetchall()}
    for nombre, desc, dosis in MEDICAMENTOS_NUEVOS:
        if clave_comparacion(nombre) in ya_existen:
            continue
        ya_existen.add(clave_comparacion(nombre))
        cursor.execute("INSERT INTO medicamento (nombre, descripcion, dosis) VALUES (%s,%s,%s)",
                       (nombre, desc, dosis))
        manifiesto['medicamento'].append(cursor.lastrowid)
    cursor.execute("SELECT id_medicamento FROM medicamento")
    medicamentos = [m['id_medicamento'] for m in cursor.fetchall()]
    print(f'Medicamentos en catálogo: {len(medicamentos)}')

    # --- Médicos nuevos, con su cuenta de acceso -------------------------
    clave = generate_password_hash('Medico123')
    for i, (nombre, especialidad, usuario) in enumerate(MEDICOS_NUEVOS):
        cursor.execute("INSERT INTO usuario (username, password, id_rol, estado) VALUES (%s,%s,%s,'activo')",
                       (usuario, clave, rol_medico))
        id_usuario = cursor.lastrowid
        manifiesto['usuario'].append(id_usuario)
        cursor.execute("""INSERT INTO medico (nombre, numero_identidad, telefono, email,
                                              id_especialidad, id_usuario)
                          VALUES (%s,%s,%s,%s,%s,%s)""",
                       (nombre, 90000001 + i, f'31{random.randint(10000000, 99999999)}',
                        f'{usuario}@mediapp.com', especialidades[especialidad], id_usuario))
        manifiesto['medico'].append(cursor.lastrowid)

    cursor.execute("SELECT id_medico FROM medico ORDER BY id_medico")
    medicos = [m['id_medico'] for m in cursor.fetchall()]
    print(f'Médicos activos en la agenda: {len(medicos)}')

    # --- Pacientes nuevos (algunos con cuenta, otros no) ------------------
    # Los nombres salen de combinar nombre de pila y apellido sin repetir la
    # pareja, para que ningún usuario generado choque con otro.
    parejas = [(p, a) for p in PILA for a in APELLIDOS]
    nombres = [f'{p} {a}' for p, a in random.sample(parejas, PACIENTES_NUEVOS)]
    clave_paciente = generate_password_hash('Paciente123')
    for i, nombre in enumerate(nombres):
        id_usuario = None
        # El usuario y el correo se generan sin tildes: el validador de
        # correo de la aplicación (validators.py) solo acepta ASCII, así que
        # sembrar "bermúdez@correo.com" dejaría un paciente que la propia
        # pantalla de edición rechazaría al guardar.
        identificador = clave_comparacion(nombre.split()[0]) + '.' + clave_comparacion(nombre.split()[1])
        # Dos de cada tres pacientes pueden entrar al sistema a ver lo suyo;
        # el resto son atenciones sin cuenta, que también existen en la vida real.
        if i % 3 != 2:
            cursor.execute("INSERT INTO usuario (username, password, id_rol, estado) VALUES (%s,%s,%s,'activo')",
                           (identificador, clave_paciente, rol_paciente))
            id_usuario = cursor.lastrowid
            manifiesto['usuario'].append(id_usuario)
        nacimiento = hoy - timedelta(days=random.randint(18 * 365, 78 * 365))
        cursor.execute("""INSERT INTO paciente (nombre, tipo_documento, numero_documento,
                                                fecha_nacimiento, telefono, direccion, email, id_usuario)
                          VALUES (%s,'CC',%s,%s,%s,%s,%s,%s)""",
                       (nombre, str(90100001 + i), nacimiento,
                        f'30{random.randint(10000000, 99999999)}',
                        random.choice(DIRECCIONES),
                        identificador + '@correo.com',
                        id_usuario))
        manifiesto['paciente'].append(cursor.lastrowid)

    cursor.execute("SELECT id_paciente FROM paciente ORDER BY id_paciente")
    pacientes = [p['id_paciente'] for p in cursor.fetchall()]
    print(f'Pacientes en el sistema: {len(pacientes)}')

    # --- Citas ------------------------------------------------------------
    # Se respetan las dos reglas de negocio del sistema:
    #   * un mismo médico, mínimo 30 minutos entre citas
    #   * un mismo paciente, máximo una cita por día
    ocupado_medico = set()     # (id_medico, datetime)
    ocupado_paciente = set()   # (id_paciente, fecha)
    citas_pasadas = []

    # Se cargan primero las citas que YA existían: si no, la demo choca
    # contra ellas y genera datos que violan las reglas del sistema —
    # exactamente lo que le pasó al seed original con las citas 4 y 5.
    cursor.execute("SELECT id_paciente, id_medico, fecha FROM cita WHERE estado <> 'cancelada'")
    for fila in cursor.fetchall():
        ocupado_paciente.add((fila['id_paciente'], fila['fecha'].date()))
        # Se bloquea toda la ventana de +/- 30 minutos alrededor de la cita
        # existente, que es la separación mínima que exige la regla D4.
        for desplazamiento in range(-29, 30):
            ocupado_medico.add((fila['id_medico'], fila['fecha'] + timedelta(minutes=desplazamiento)))

    def agendar(dia, cuantas):
        creadas = 0
        intentos = 0
        while creadas < cuantas and intentos < cuantas * 12:
            intentos += 1
            medico = random.choice(medicos)
            paciente = random.choice(pacientes)
            turno = random.choice(turnos_del_dia(dia))
            if (medico, turno) in ocupado_medico:
                continue
            if (paciente, dia) in ocupado_paciente:
                continue
            estado = 'cancelada' if random.random() < PROB_CITA_CANCELADA else 'agendada'
            cursor.execute("""INSERT INTO cita (fecha, motivo, estado, id_paciente, id_medico)
                              VALUES (%s,%s,%s,%s,%s)""",
                           (turno, random.choice(MOTIVOS), estado, paciente, medico))
            id_cita = cursor.lastrowid
            manifiesto['cita'].append(id_cita)
            ocupado_medico.add((medico, turno))
            ocupado_paciente.add((paciente, dia))
            if turno.date() < hoy and estado == 'agendada':
                citas_pasadas.append((paciente, medico, turno))
            creadas += 1
        return creadas

    dia = hoy - timedelta(days=DIAS_HACIA_ATRAS)
    while dia < hoy:
        if dia.weekday() < 5:      # solo días hábiles
            agendar(dia, random.randint(*CITAS_POR_DIA_PASADO))
        dia += timedelta(days=1)
    pasadas = len(manifiesto['cita'])

    dia = hoy + timedelta(days=1)
    fin = hoy + timedelta(weeks=SEMANAS_HACIA_ADELANTE)
    while dia <= fin:
        if dia.weekday() < 5:
            agendar(dia, random.randint(*CITAS_POR_DIA_FUTURO))
        dia += timedelta(days=1)
    print(f'Citas: {pasadas} en los últimos {DIAS_HACIA_ATRAS} días, '
          f'{len(manifiesto["cita"]) - pasadas} en las próximas {SEMANAS_HACIA_ADELANTE} semanas')

    # --- Consultas (el acto clínico de una cita ya atendida) --------------
    consultas = []
    for paciente, medico, turno in citas_pasadas:
        if random.random() > PROB_CONSULTA_TRAS_CITA:
            continue
        diagnostico, tratamiento = random.choice(DIAGNOSTICOS)
        cursor.execute("""INSERT INTO consulta (fecha, diagnostico, tratamiento, id_paciente, id_medico)
                          VALUES (%s,%s,%s,%s,%s)""",
                       (turno + timedelta(minutes=10), diagnostico, tratamiento, paciente, medico))
        id_consulta = cursor.lastrowid
        manifiesto['consulta'].append(id_consulta)
        consultas.append((id_consulta, paciente, medico, turno))
    print(f'Consultas registradas: {len(consultas)}')

    # --- Recetas (cuelgan de una consulta) --------------------------------
    for id_consulta, paciente, medico, turno in consultas:
        if random.random() > PROB_RECETA_TRAS_CONSULTA:
            continue
        for _ in range(random.randint(1, 2)):
            cursor.execute("""INSERT INTO receta (id_consulta, id_medicamento, cantidad, indicaciones)
                              VALUES (%s,%s,%s,%s)""",
                           (id_consulta, random.choice(medicamentos), random.randint(1, 3),
                            random.choice(INDICACIONES)))
            manifiesto['receta'].append(cursor.lastrowid)
    print(f'Recetas emitidas: {len(manifiesto["receta"])}')

    # --- Historias clínicas (antecedentes, no ligadas a una cita) ---------
    for paciente in random.sample(pacientes, int(len(pacientes) * 0.8)):
        for descripcion, notas in random.sample(ANTECEDENTES, random.randint(1, 3)):
            fecha = datetime.combine(hoy - timedelta(days=random.randint(1, DIAS_HACIA_ATRAS)),
                                     datetime.min.time()) + timedelta(hours=random.randint(8, 16))
            cursor.execute("""INSERT INTO historia (id_paciente, id_medico, fecha, descripcion, notas)
                              VALUES (%s,%s,%s,%s,%s)""",
                           (paciente, random.choice(medicos), fecha, descripcion, notas))
            manifiesto['historia'].append(cursor.lastrowid)
    print(f'Historias clínicas: {len(manifiesto["historia"])}')

    # --- Exámenes de laboratorio -----------------------------------------
    # Unos ya tienen resultado cargado por el laboratorio (admin) y otros
    # siguen pendientes: así se ve el flujo de D7 en las dos puntas.
    for paciente, medico, turno in random.sample(citas_pasadas, min(len(citas_pasadas), 160)):
        tipo, resultado = random.choice(EXAMENES)
        solicitud = turno + timedelta(minutes=20)
        if random.random() < PROB_EXAMEN_CON_RESULTADO:
            entrega = solicitud + timedelta(days=random.randint(1, 5), hours=random.randint(1, 6))
            if entrega.date() >= hoy:       # un resultado no puede ser del futuro
                entrega = None
        else:
            entrega = None
        cursor.execute("""INSERT INTO examen (id_paciente, id_medico, tipo_examen,
                                              fecha_solicitud, fecha_resultado, resultado)
                          VALUES (%s,%s,%s,%s,%s,%s)""",
                       (paciente, medico, tipo, solicitud, entrega,
                        resultado if entrega else None))
        manifiesto['examen'].append(cursor.lastrowid)
    print(f'Exámenes de laboratorio: {len(manifiesto["examen"])}')

    # --- Comprobación antes de confirmar ---------------------------------
    # El script no debe poder dejar datos que la propia aplicación
    # considere inválidos. Se revisan las dos reglas de citas con el mismo
    # criterio del backend; si algo falla, se deshace todo y no se guarda
    # el manifiesto.
    cursor.execute("""
        SELECT COUNT(*) AS n FROM cita a JOIN cita b
          ON a.id_medico = b.id_medico AND a.id_cita < b.id_cita
         AND a.estado <> 'cancelada' AND b.estado <> 'cancelada'
         AND ABS(TIMESTAMPDIFF(MINUTE, a.fecha, b.fecha)) < 30
    """)
    choques_medico = cursor.fetchone()['n']
    cursor.execute("""
        SELECT COUNT(*) AS n FROM (
            SELECT id_paciente FROM cita WHERE estado <> 'cancelada'
            GROUP BY id_paciente, DATE(fecha) HAVING COUNT(*) > 1
        ) AS repetidas
    """)
    choques_paciente = cursor.fetchone()['n']
    if choques_medico or choques_paciente:
        cn.rollback()
        cursor.close()
        raise SystemExit(
            f'ABORTADO: los datos generados violan las reglas de negocio '
            f'({choques_medico} choques de 30 min entre citas del mismo médico, '
            f'{choques_paciente} pacientes con más de una cita el mismo día). '
            f'No se guardó nada.')
    print('Reglas de negocio verificadas: sin choques de horario.')

    cn.commit()
    cursor.close()
    guardar_manifiesto(manifiesto)
    print(f'\nManifiesto guardado en {MANIFIESTO}')


def main():
    cn = conectar()
    try:
        print('Borrando datos de demostración anteriores (si los hay)...')
        limpiar(cn)
        if '--limpiar' in sys.argv:
            print('Listo: solo se limpió.')
            return
        print('\nSembrando datos de demostración...')
        sembrar(cn)
        print('\nCuentas de prueba creadas: médicos con contraseña "Medico123", '
              'pacientes con "Paciente123".')
    finally:
        cn.close()


if __name__ == '__main__':
    main()
