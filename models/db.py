# models/db.py
import os
import psycopg2
import psycopg2.extras
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

# ====================== HELPER PRINCIPAL ======================
def query_db(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """Ejecuta consultas de forma segura devolviendo diccionarios"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute(sql, params or ())

        if commit:
            conn.commit()
            return None
        elif fetchone:
            return cur.fetchone()
        elif fetchall:
            return cur.fetchall()
        return None

    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cur.close()