# models/db.py
import os
import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        
        # Crear el directorio del disco de forma segura
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row   # ← Esto arregla el error 'tuple object' has no attribute 'id'
    
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'schema.sql')
    
    # Fallback si no encuentra el schema
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print("❌ Error al inicializar la base de datos:", str(e))
        raise