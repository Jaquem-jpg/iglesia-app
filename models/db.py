# models/db.py
import os
import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        # Path de la base de datos
        if os.environ.get('RENDER'):
            db_path = '/opt/render/project/src/data/iglesia.db'
        else:
            db_path = 'iglesia.db'

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row   # ← Esto arregla el error del tuple
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'schema.sql')
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print("❌ Error al inicializar DB:", str(e))
        raise