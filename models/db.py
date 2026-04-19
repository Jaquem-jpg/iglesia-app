import os
import psycopg2
from flask import g

# ================================
# CONEXIÓN A BASE DE DATOS
# ================================
def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(os.environ["DATABASE_URL"])
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ================================
# INICIALIZAR BASE DE DATOS
# ================================
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


# ================================
# HELPER PARA CONSULTAS SQL
# ================================
def query_db(sql, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(sql, params or ())

        result = None

        if commit:
            conn.commit()
        elif fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()

        return result

    except Exception as e:
        if commit:
            conn.rollback()
        raise e

    finally:
        cur.close()