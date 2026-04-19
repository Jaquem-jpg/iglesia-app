# models/db.py
import os
import sqlite3
from flask import g, current_app

def get_db():
    """Conecta a la base de datos (SQLite)"""
    if 'db' not in g:
        # Ruta de la base de datos
        if current_app.config.get('DATABASE'):
            db_path = current_app.config['DATABASE']
        else:
            # Por defecto en Render usa /data/iglesia.db
            db_path = os.path.join('/data', 'iglesia.db') if os.environ.get('RENDER') else 'iglesia.db'

        # Crear directorio si no existe (importante en Render)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row   # Permite acceder por nombre: row['nombre']

    return g.db


def close_db(e=None):
    """Cierra la conexión a la base de datos"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Inicializa la base de datos con el schema.sql"""
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'schema.sql')

    # Si no encuentra el schema en root_path, busca en el directorio padre
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print("❌ Error al inicializar la base de datos:", e)
        raise


# Helper opcional para consultas más limpias
def query_db(query, args=(), one=False):
    """Ejecuta una consulta y devuelve resultado"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv