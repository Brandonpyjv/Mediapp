-- =====================================================================
-- Migración 006 — Baja lógica de pacientes (activo / inactivo)
-- Proyecto: MediApp
-- Fecha: 2026-09-02
-- =====================================================================
-- Decisión D11-a, aplicada ahora a `paciente` (mismo patrón ya resuelto
-- para `usuario` en la migración 002 y para `medico` en la migración
-- 005). Hasta ahora "Eliminar" un paciente hacía `DELETE FROM paciente`
-- de verdad: si tenía citas, consultas, historias, exámenes o recetas
-- asociadas, el borrado fallaba por la FK y el botón simplemente no
-- funcionaba (el único motivo por el que no se perdió historial fue esa
-- falla, no una protección real).
--
-- Con esta columna, dar de baja a un paciente pasa a ser un cambio de
-- estado: deja de ofrecerse al agendar citas nuevas o al registrar
-- historias/consultas/exámenes, pero conserva todo su historial clínico.
--
-- A diferencia de `medico`, el paciente no tiene un concepto de "acceso"
-- separado que gestionar aquí: su cuenta de acceso (`usuario.id_usuario`,
-- opcional) ya se activa/desactiva desde el módulo de Usuarios.
-- =====================================================================

ALTER TABLE `paciente`
  ADD COLUMN `estado` ENUM('activo','inactivo') NOT NULL DEFAULT 'activo' AFTER `id_usuario`;

-- Todos los pacientes existentes quedan como 'activo' por el DEFAULT.
