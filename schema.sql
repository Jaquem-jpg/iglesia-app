-- Tabla de miembros (con nuevo campo notas)
CREATE TABLE IF NOT EXISTS miembros (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT,
    notas TEXT
);

-- Tabla de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME,
    lugar TEXT,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'invitado'
);

-- Usuario admin inicial
INSERT INTO usuarios (username, password, rol)
VALUES ('admin', 'iglesia123', 'admin')
ON CONFLICT (username) DO NOTHING;