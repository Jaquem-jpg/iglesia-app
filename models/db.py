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
# FUNCIÓN HELPER PARA EJECUTAR CONSULTAS FÁCILMENTE
# ============================================================
def query_db(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta consultas SQL de forma segura con PostgreSQL.
    
    Ejemplos de uso:
    
    # SELECT - múltiples registros
    miembros = query_db("SELECT * FROM miembros ORDER BY nombre", fetchall=True)
    
    # SELECT - un solo registro
    usuario = query_db("SELECT * FROM usuarios WHERE id = %s", [1], fetchone=True)
    
    # SELECT con búsqueda
    resultados = query_db(
        "SELECT * FROM eventos WHERE titulo ILIKE %s",
        [f"%{busqueda}%"],
        fetchall=True
    )
    
    # INSERT
    query_db(
        "INSERT INTO miembros (nombre, telefono) VALUES (%s, %s)",
        ["Juan Perez", "+56912345678"],
        commit=True
    )
    
    # UPDATE
    query_db(
        "UPDATE miembros SET nombre = %s WHERE id = %s",
        ["Juan Carlos", 1],
        commit=True
    )
    
    # DELETE
    query_db("DELETE FROM eventos WHERE id = %s", [5], commit=True)
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