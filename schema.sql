CREATE TABLE IF NOT EXISTS miembros (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT,
    lugar TEXT,
    descripcion TEXT
);

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