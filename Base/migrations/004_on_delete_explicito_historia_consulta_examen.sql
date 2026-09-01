-- =====================================================================
-- Migración 004 — ON DELETE/UPDATE RESTRICT explícito en historia,
-- consulta y examen
-- Proyecto: MediApp
-- Fecha: 2026-09-01
-- =====================================================================
-- Las FK de `historia`, `consulta` y `examen` hacia `paciente` y `medico`
-- nunca declararon una regla ON DELETE/ON UPDATE — MySQL aplica RESTRICT
-- por defecto en ese caso (verificado contra la BD real: las 6 FK ya
-- reportan DELETE_RULE = RESTRICT, UPDATE_RULE = RESTRICT en
-- information_schema.REFERENTIAL_CONSTRAINTS).
--
-- Esta migración NO cambia ningún comportamiento: RESTRICT sigue siendo
-- RESTRICT. Es puramente para que el propio archivo `.sql` documente la
-- intención explícitamente ("un historial clínico, una consulta o un
-- examen no se pueden borrar en cascada solo porque se borró el paciente
-- o el médico") en vez de depender de que quien lo lea sepa que "sin
-- especificar nada, MySQL usa RESTRICT".
--
-- MySQL no permite ALTERAR solo la regla ON DELETE de una FK existente:
-- hay que eliminarla y volver a crearla con el mismo nombre. El índice
-- que ya usa cada FK (incluido idx_examen_paciente, sustituto del UNIQUE
-- eliminado en la migración 001) no se toca — DROP FOREIGN KEY solo
-- quita la restricción, no el índice.
-- =====================================================================

ALTER TABLE `consulta` DROP FOREIGN KEY `consulta_ibfk_1`;
ALTER TABLE `consulta` ADD CONSTRAINT `consulta_ibfk_1`
  FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `consulta` DROP FOREIGN KEY `consulta_ibfk_2`;
ALTER TABLE `consulta` ADD CONSTRAINT `consulta_ibfk_2`
  FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `examen` DROP FOREIGN KEY `examen_ibfk_1`;
ALTER TABLE `examen` ADD CONSTRAINT `examen_ibfk_1`
  FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `examen` DROP FOREIGN KEY `examen_ibfk_2`;
ALTER TABLE `examen` ADD CONSTRAINT `examen_ibfk_2`
  FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `historia` DROP FOREIGN KEY `historia_ibfk_1`;
ALTER TABLE `historia` ADD CONSTRAINT `historia_ibfk_1`
  FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `historia` DROP FOREIGN KEY `historia_ibfk_2`;
ALTER TABLE `historia` ADD CONSTRAINT `historia_ibfk_2`
  FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
  ON DELETE RESTRICT ON UPDATE RESTRICT;
