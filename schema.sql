-- =========================================================
--  Sistema de Tickets de Soporte Técnico - Esquema de BD
--  Motor: SQLite
-- =========================================================

PRAGMA foreign_keys = ON;

-- Se borran en orden inverso a las dependencias (primero las que tienen FK)
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS equipos;
DROP TABLE IF EXISTS tecnicos;
DROP TABLE IF EXISTS clientes;

-- ---------------------------------------------------------
--  CLIENTES: personas o empresas que traen equipos
-- ---------------------------------------------------------
CREATE TABLE clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT    NOT NULL,
    telefono  TEXT,
    email     TEXT    UNIQUE
);

-- ---------------------------------------------------------
--  EQUIPOS: cada equipo pertenece a UN cliente (relación 1:N)
-- ---------------------------------------------------------
CREATE TABLE equipos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id  INTEGER NOT NULL,
    tipo        TEXT    NOT NULL CHECK (tipo IN ('PC escritorio', 'Notebook', 'Impresora', 'Monitor')),
    marca       TEXT    NOT NULL,
    modelo      TEXT,
    nro_serie   TEXT    UNIQUE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- ---------------------------------------------------------
--  TECNICOS: quienes resuelven los tickets
-- ---------------------------------------------------------
CREATE TABLE tecnicos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    especialidad  TEXT NOT NULL
);

-- ---------------------------------------------------------
--  TICKETS: una orden de reparación sobre un equipo,
--  asignada a un técnico. Es la tabla central del sistema.
-- ---------------------------------------------------------
CREATE TABLE tickets (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id      INTEGER NOT NULL,
    tecnico_id     INTEGER,                 -- puede quedar sin asignar
    fecha_ingreso  TEXT    NOT NULL DEFAULT (date('now')),  -- formato AAAA-MM-DD
    problema       TEXT    NOT NULL,
    estado         TEXT    NOT NULL DEFAULT 'Abierto'
                           CHECK (estado IN ('Abierto', 'En proceso', 'Resuelto')),
    costo          REAL    DEFAULT 0 CHECK (costo >= 0),
    FOREIGN KEY (equipo_id)  REFERENCES equipos(id),
    FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
);

-- =========================================================
--  DATOS DE EJEMPLO
-- =========================================================

INSERT INTO clientes (nombre, telefono, email) VALUES
    ('María González',        '099 123 456', 'maria.gonzalez@mail.com'),
    ('Juan Pérez',            '098 234 567', 'juan.perez@mail.com'),
    ('Escuela N.º 45',        '2401 1234',   'escuela45@anep.edu.uy'),
    ('Lucía Rodríguez',       '094 345 678', 'lucia.rodriguez@mail.com'),
    ('Ferretería El Tornillo','2908 5678',   'eltornillo@mail.com'),
    ('Martín Silva',          '091 456 789', 'martin.silva@mail.com'),
    ('Sofía Martínez',        '092 567 890', 'sofia.martinez@mail.com');

INSERT INTO equipos (cliente_id, tipo, marca, modelo, nro_serie) VALUES
    (1, 'Notebook',      'Lenovo',  'IdeaPad 3',      'LN-1001'),
    (2, 'PC escritorio', 'Genérica','Armada Ryzen 5', 'PC-2001'),
    (3, 'PC escritorio', 'HP',      'ProDesk 400',    'HP-3001'),
    (3, 'PC escritorio', 'HP',      'ProDesk 400',    'HP-3002'),
    (3, 'Impresora',     'Epson',   'L3250',          'EP-3003'),
    (4, 'Notebook',      'Dell',    'Inspiron 15',    'DL-4001'),
    (5, 'PC escritorio', 'Dell',    'OptiPlex 3080',  'DL-5001'),
    (5, 'Monitor',       'Samsung', 'S24F350',        'SM-5002'),
    (6, 'Notebook',      'Asus',    'VivoBook 15',    'AS-6001'),
    (1, 'Impresora',     'HP',      'DeskJet 2775',   'HP-1002'),
    (7, 'Notebook',      'Lenovo',  'ThinkPad E14',   'LN-7001');

INSERT INTO tecnicos (nombre, especialidad) VALUES
    ('Carlos Méndez',  'Hardware'),
    ('Ana Fernández',  'Redes'),
    ('Diego Castro',   'Software');

INSERT INTO tickets (equipo_id, tecnico_id, fecha_ingreso, problema, estado, costo) VALUES
    (1,  3,    '2026-07-03', 'Windows no arranca, pantalla azul',            'Resuelto',   1500),
    (2,  1,    '2026-07-10', 'No enciende, posible fuente quemada',          'Resuelto',   2800),
    (3,  2,    '2026-07-15', 'Sin conexión a internet',                      'Resuelto',    800),
    (5,  1,    '2026-07-22', 'Atasco de papel recurrente',                   'Resuelto',    600),
    (6,  3,    '2026-08-02', 'Muy lenta, limpieza de virus',                 'Resuelto',   1200),
    (7,  1,    '2026-08-09', 'Cambio de disco HDD a SSD',                    'Resuelto',   3500),
    (8,  1,    '2026-08-18', 'Pantalla con líneas verticales',               'Resuelto',    900),
    (4,  2,    '2026-08-25', 'No obtiene IP por DHCP',                       'Resuelto',    700),
    (9,  1,    '2026-09-05', 'Teclado con teclas que no responden',          'Resuelto',   1800),
    (1,  1,    '2026-09-14', 'Bisagra de pantalla rota',                     'En proceso', 2200),
    (3,  3,    '2026-09-20', 'Instalación de paquete de oficina',            'Resuelto',    500),
    (10, NULL, '2026-09-28', 'No imprime en color',                          'Abierto',       0),
    (7,  2,    '2026-10-01', 'Configurar red e impresora compartida',        'En proceso', 1000),
    (2,  1,    '2026-10-04', 'Ampliación de memoria RAM a 16 GB',            'Abierto',    2500),
    (6,  NULL, '2026-10-06', 'Pantalla parpadea al mover la tapa',           'Abierto',       0);
