-- =====================================================================
-- Migración 003 — UNIQUE en medicamento.nombre
-- Proyecto: MediApp
-- Fecha: 2026-09-01
-- =====================================================================
-- El catálogo de medicamentos no tenía restricción de unicidad en el
-- nombre, así que era posible registrar el mismo medicamento dos veces
-- (por ejemplo "Paracetamol" y otra vez "Paracetamol"). La aplicación ya
-- validaba esto en `addME` antes de esta migración (SELECT previo al
-- INSERT), pero esa comprobación era solo de aplicación, no de base de
-- datos — no protegía contra condiciones de carrera ni contra futuras
-- vías de inserción que la pasaran por alto.
--
-- A diferencia de `cita`/`examen` (migración 001), aquí SÍ tiene sentido
-- un UNIQUE real: un medicamento no tiene estado "cancelado" que deba
-- liberar el nombre para reutilizarlo, así que no hay conflicto con
-- ninguna regla de negocio existente.
-- =====================================================================

ALTER TABLE `medicamento`
  ADD UNIQUE INDEX `idx_medicamento_nombre` (`nombre`);
