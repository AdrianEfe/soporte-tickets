"""Consultas SQL predefinidas que se muestran en la página de Reportes.

Cada reporte tiene un título, una explicación de qué concepto de SQL usa
y la consulta en sí. La página muestra el SQL junto con el resultado.
"""

REPORTES = [
    {
        "titulo": "Tickets abiertos, del más viejo al más nuevo",
        "concepto": "SELECT + WHERE (filtrar) + ORDER BY (ordenar)",
        "sql": """SELECT id, fecha_ingreso, problema
FROM tickets
WHERE estado = 'Abierto'
ORDER BY fecha_ingreso;""",
    },
    {
        "titulo": "Tickets que cuestan más de $2000, del más caro al más barato",
        "concepto": "WHERE con un número + ORDER BY ... DESC",
        "sql": """SELECT id, problema, costo
FROM tickets
WHERE costo > 2000
ORDER BY costo DESC;""",
    },
    {
        "titulo": "Tickets relacionados con la pantalla",
        "concepto": "LIKE: buscar un texto dentro de otro",
        "sql": """SELECT id, problema, estado
FROM tickets
WHERE problema LIKE '%pantalla%';""",
    },
    {
        "titulo": "Cantidad de tickets en cada estado",
        "concepto": "COUNT (contar) + GROUP BY (agrupar)",
        "sql": """SELECT estado, COUNT(*)
FROM tickets
GROUP BY estado;""",
    },
    {
        "titulo": "Total facturado (tickets resueltos)",
        "concepto": "SUM (sumar)",
        "sql": """SELECT SUM(costo)
FROM tickets
WHERE estado = 'Resuelto';""",
    },
    {
        "titulo": "Cada equipo con el nombre de su dueño",
        "concepto": "JOIN: unir dos tablas",
        "sql": """SELECT equipos.tipo, equipos.marca, equipos.modelo, clientes.nombre
FROM equipos
JOIN clientes ON equipos.cliente_id = clientes.id;""",
    },
    {
        "titulo": "Tickets con el nombre del técnico que los atiende",
        "concepto": "JOIN: unir dos tablas",
        "sql": """SELECT tickets.id, tickets.problema, tecnicos.nombre
FROM tickets
JOIN tecnicos ON tickets.tecnico_id = tecnicos.id;""",
    },
    {
        "titulo": "Cantidad de tickets de cada técnico",
        "concepto": "JOIN + COUNT + GROUP BY",
        "sql": """SELECT tecnicos.nombre, COUNT(*)
FROM tickets
JOIN tecnicos ON tickets.tecnico_id = tecnicos.id
GROUP BY tecnicos.nombre;""",
    },
]
