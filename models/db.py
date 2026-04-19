import os
import psycopg2
from flask import g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(os.environ["DATABASE_URL"])
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    try:
        cur.execute(sql)
        db.commit()
        print("✅ DB creada correctamente")
    except Exception as e:
        db.rollback()
        print("❌ Error en schema.sql:", e)
        raise
    finally:
        cur.close()

# ============================================================
# FUNCIÓN HELPER PARA EJECUTAR CONSULTAS (OPCIONAL pero útil)
# ============================================================
def query_db(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta consultas SQL de forma segura con PostgreSQL.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql, params or ())
        
        if commit:
            conn.commit()
            result = None
        elif fetchall:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()
        else:
            result = None
            
        return result
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()