-- =====================================================================
-- Migración 005 — Baja lógica de médicos (activo / inactivo)
-- Proyecto: MediApp
-- Fecha: 2026-09-02
-- =====================================================================
-- Decisión D11-a. Hasta ahora "Eliminar" un médico hacía `DELETE FROM
-- medico` de verdad: se perdía la ficha del profesional que firmó
-- historias clínicas, consultas y recetas, y su cuenta de acceso quedaba
-- huérfana (con rol médico pero sin ficha, capaz de iniciar sesión sin
-- poder usar nada). De ahí salieron las cuentas `john.hernandez` y
-- `brandon`, que hoy siguen sin ficha asociada.
--
-- Con esta columna, dar de baja a un médico pasa a ser un cambio de
-- estado: deja de aparecer para agendar citas nuevas, pero conserva todo
-- lo que firmó. Mismo principio ya aplicado a `usuario` (migración 002)
-- y a `cita` (migración 001).
--
-- Importante: el estado del MÉDICO y el estado de su CUENTA son cosas
-- distintas y se manejan por separado (D11-a). Un médico puede estar
-- activo sin poder iniciar sesión (de licencia, por ejemplo), o seguir
-- teniendo acceso a consultar lo suyo aunque ya no reciba citas nuevas.
-- =====================================================================

ALTER TABLE `medico`
  ADD COLUMN `estado` ENUM('activo','inactivo') NOT NULL DEFAULT 'activo' AFTER `id_usuario`;

-- Todos los médicos existentes quedan como 'activo' por el DEFAULT.
