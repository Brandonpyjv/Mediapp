-- =====================================================================
-- Migración 002 — Baja lógica de usuarios (activo / inactivo)
-- Proyecto: MediApp
-- Fecha: 2026-08-31
-- =====================================================================
-- Principio pedido por el autor: un `usuario` (cuenta de acceso) NUNCA
-- se elimina físicamente. Al "eliminar" un usuario, se desactiva
-- (estado -> 'inactivo'), preservando el registro e historial.
--
-- Mismo criterio ya aplicado a `cita.estado` en la migración 001.
-- =====================================================================

ALTER TABLE `usuario`
  ADD COLUMN `estado` ENUM('activo','inactivo') NOT NULL DEFAULT 'activo' AFTER `id_rol`;

-- Todas las cuentas existentes quedan como 'activo' por el DEFAULT.
