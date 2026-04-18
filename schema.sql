-- schema.sql - Versión limpia para iglesia

CREATE TABLE IF NOT EXISTS miembros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT,
    lugar TEXT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'invitado'   -- admin o invitado
);

-- Usuario administrador inicial (puedes cambiar la contraseña después)
INSERT OR IGNORE INTO usuarios (username, password, rol) 
VALUES ('admin', 'iglesia123', 'admin');