-- =========================================================
--  Consultas de práctica - Sistema de Tickets de Soporte
--  Se pueden ejecutar en la página "Consulta libre" (solo SELECT)
--  o en DB Browser for SQLite abriendo soporte.db
-- =========================================================

-- 1) Ver todo el contenido de una tabla
SELECT * FROM clientes;

-- 2) Elegir columnas y ordenar
SELECT nombre, telefono FROM clientes ORDER BY nombre;

-- 3) Filtrar con WHERE
SELECT * FROM tickets WHERE estado = 'Abierto';

-- 4) Dos condiciones a la vez (AND)
SELECT * FROM tickets WHERE estado = 'Resuelto' AND costo > 1000;

-- 5) Buscar un texto (LIKE)
SELECT * FROM tickets WHERE problema LIKE '%pantalla%';

-- 6) Tickets sin técnico asignado (se usa IS NULL, no "= NULL")
SELECT id, problema FROM tickets WHERE tecnico_id IS NULL;

-- 7) Contar
SELECT COUNT(*) FROM tickets;

-- 8) Sumar
SELECT SUM(costo) FROM tickets WHERE estado = 'Resuelto';

-- 9) Contar por grupos: cuántos tickets hay en cada estado
SELECT estado, COUNT(*) FROM tickets GROUP BY estado;

-- 10) JOIN: cada equipo con el nombre de su dueño
SELECT equipos.tipo, equipos.marca, clientes.nombre
FROM equipos
JOIN clientes ON equipos.cliente_id = clientes.id;

-- 11) JOIN: cada ticket con el nombre del técnico
SELECT tickets.id, tickets.problema, tecnicos.nombre
FROM tickets
JOIN tecnicos ON tickets.tecnico_id = tecnicos.id;

-- =========================================================
--  Consultas que MODIFICAN datos (la app las usa por dentro;
--  para probarlas a mano, usar DB Browser for SQLite)
-- =========================================================

-- INSERT: agregar un técnico
INSERT INTO tecnicos (nombre, especialidad) VALUES ('Laura Gómez', 'Hardware');

-- UPDATE: cambiar el estado de un ticket
UPDATE tickets SET estado = 'Resuelto' WHERE id = 14;

-- DELETE: borrar un ticket
DELETE FROM tickets WHERE id = 15;

-- Ojo: UPDATE y DELETE sin WHERE afectan a TODAS las filas.
