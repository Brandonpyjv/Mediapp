-- =====================================================================
-- Migración 007 — Baja lógica de medicamentos (activo / descontinuado)
-- Proyecto: MediApp
-- Fecha: 2026-09-02
-- =====================================================================
-- Decisión D12 (opción D12-a), mismo principio ya aplicado a `usuario`
-- (migración 002), `medico` (migración 005) y `paciente` (migración
-- 006). Hasta ahora "Eliminar" un medicamento hacía `DELETE FROM
-- medicamento` de verdad, y solo funcionaba si ninguna receta lo había
-- usado nunca — la FK lo rechazaba en cualquier otro caso.
--
-- A diferencia de `medico`/`paciente`, los dos valores no son
-- 'activo'/'inactivo' sino 'activo'/'descontinuado': un medicamento
-- descontinuado ya no se puede recetar, pero las recetas históricas que
-- ya lo usaron lo siguen mostrando con normalidad — que es justamente
-- lo que se perdería si se borrara.
--
-- Alternativa D12-b (`'activo','inactivo','agotado'`, control de stock)
-- quedó descartada por estar fuera del alcance del proyecto.
-- =====================================================================

ALTER TABLE `medicamento`
  ADD COLUMN `estado` ENUM('activo','descontinuado') NOT NULL DEFAULT 'activo' AFTER `dosis`;

-- Todos los medicamentos existentes quedan como 'activo' por el DEFAULT.
