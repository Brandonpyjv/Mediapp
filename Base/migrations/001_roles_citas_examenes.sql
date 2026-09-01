-- =====================================================================
-- Migración 001 — Roles, cancelación de citas y exámenes
-- Proyecto: MediApp
-- Fecha: 2026-08-31
-- =====================================================================
-- Aplica las decisiones de arquitectura D1, D7 y D8.
-- Es idempotente en lo posible y se ejecuta dentro de una transacción
-- para las operaciones que lo permiten.
--
-- ADVERTENCIA: en MySQL/MariaDB las sentencias DDL (ALTER/DROP) hacen
-- COMMIT implícito. Hacer respaldo antes de ejecutar.
-- =====================================================================

-- ---------------------------------------------------------------------
-- D1 — Rol Médico e identidad autenticable del médico
-- ---------------------------------------------------------------------
-- Hasta ahora el sistema solo tenía 2 roles (admin, paciente) y la tabla
-- `medico` era un catálogo sin vínculo con `usuario`, por lo que un
-- médico no podía iniciar sesión. Esto habilita el tercer rol real.

INSERT INTO `rol` (`id_rol`, `nombre_rol`) VALUES (3, 'medico');

ALTER TABLE `medico`
  ADD COLUMN `id_usuario` INT(11) NULL DEFAULT NULL AFTER `id_especialidad`,
  ADD CONSTRAINT `fk_medico_usuario`
    FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
    ON DELETE SET NULL ON UPDATE CASCADE;

-- ---------------------------------------------------------------------
-- D8 — Cancelación de citas por el paciente + disponibilidad
-- ---------------------------------------------------------------------
-- El paciente puede cancelar su propia cita. NO se borra la fila: se
-- marca como 'cancelada' para preservar la trazabilidad clínica y el
-- registro histórico (requisito legal y de sustentación).

ALTER TABLE `cita`
  ADD COLUMN `estado` ENUM('agendada','cancelada') NOT NULL DEFAULT 'agendada' AFTER `motivo`;

-- Las citas ya existentes quedan como 'agendada' por el DEFAULT.

-- Se elimina el índice único (id_medico, fecha).
--
-- MOTIVO: con la cancelación activada, una cita cancelada permanece en
-- la tabla. Ese UNIQUE impediría volver a agendar el mismo horario que
-- acaba de liberarse (error "Duplicate entry"), rompiendo justamente la
-- función de disponibilidad que se quiere implementar.
--
-- La regla de no solapamiento se aplica ahora en la capa de aplicación
-- (`_check_appointment_conflicts`), que además es MÁS estricta: exige
-- 30 minutos de separación, algo que un UNIQUE no puede expresar, y
-- sabe ignorar las citas canceladas.
--
-- ORDEN OBLIGATORIO: la FK `cita_ibfk_2` (id_medico) se apoya en el
-- índice `uq_medico_fecha`. Hay que crear primero el índice sustituto,
-- o MySQL rechaza el DROP con el error 1553
-- ("Cannot drop index: needed in a foreign key constraint").
CREATE INDEX `idx_cita_medico_fecha` ON `cita` (`id_medico`, `fecha`);

ALTER TABLE `cita` DROP INDEX `uq_medico_fecha`;

-- ---------------------------------------------------------------------
-- D7 — Exámenes de laboratorio (permisos divididos por campo)
-- ---------------------------------------------------------------------
-- Flujo acordado:
--   * Médico       -> SOLICITA: id_medico, tipo_examen, fecha_solicitud
--   * Admin (lab)  -> CARGA:    resultado, fecha_resultado
--
-- Se elimina el UNIQUE (id_paciente, id_medico), que impedía que un
-- mismo médico solicitara más de un examen al mismo paciente en toda la
-- vida del sistema. Con el flujo aprobado, un médico debe poder ordenar
-- múltiples exámenes al mismo paciente.
--
-- Mismo orden obligatorio que en `cita`: primero el índice sustituto
-- (la FK `examen_ibfk_1` sobre id_paciente se apoya en el UNIQUE), y
-- después el DROP.
CREATE INDEX `idx_examen_paciente` ON `examen` (`id_paciente`);

ALTER TABLE `examen` DROP INDEX `id_examen`;
