import os
import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        # Asegurar que el directorio existe (importante para Render)
        db_path = current_app.config['DATABASE']
        db_dir = os.path.dirname(db_path)
        
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")  # Buen práctica
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa la base de datos con el schema.sql"""
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'schema.sql')
    
    # Si no encuentra en root_path, buscar en el directorio actual
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        print("✅ Base de datos inicializada correctamente en:", current_app.config['DATABASE'])
    except Exception as e:
        print("❌ Error al inicializar la base de datos:", e)
        raise