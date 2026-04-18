import os
import psycopg2
from flask import g, current_app

def get_db():
    if 'db' not in g:
        database_url = current_app.config['DATABASE_URL']
        g.db = psycopg2.connect(database_url)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa la base de datos con schema_postgres.sql"""
    db = get_db()
    cur = db.cursor()
    
    # Buscar schema_postgres.sql
    schema_path = os.path.join(current_app.root_path, 'schema_postgres.sql')
    
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema_postgres.sql')
    
    try:
        # Leer el archivo SQL
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar línea por línea (evita problemas de transacción)
        for statement in sql.split(';'):
            if statement.strip():
                cur.execute(statement)
        
        db.commit()
        print("✅ Base de datos PostgreSQL inicializada correctamente")
    except Exception as e:
        print("❌ Error al inicializar:", e)
        db.rollback()
        raise
    finally:
        cur.close()