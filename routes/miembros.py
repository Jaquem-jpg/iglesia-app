from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from models.db import get_db
from decorators import login_required, admin_required
import csv
from io import StringIO

miembros_bp = Blueprint('miembros', __name__, url_prefix='/miembros')

@miembros_bp.route('/')
@login_required
def listar():
    search = request.args.get('search', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    
    if search:
        cursor.execute("SELECT * FROM miembros WHERE nombre ILIKE %s ORDER BY nombre", (f"%{search}%",))
        miembros = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM miembros ORDER BY nombre")
        miembros = cursor.fetchall()
    
    cursor.close()
    return render_template("miembros.html", miembros=miembros, search=search)

@miembros_bp.route('/exportar')
@login_required
def exportar():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM miembros ORDER BY nombre")
    miembros = cursor.fetchall()
    cursor.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Teléfono'])
    for m in miembros:
        writer.writerow([m[0], m[1], m[2]])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=miembros.csv'}
    )

# ==================== AGREGAR MIEMBRO ====================
@miembros_bp.route('/agregar', methods=['POST'])
@admin_required
def agregar():
    nombre = request.form.get('nombre', '').strip()
    codigo_pais = request.form.get('codigo_pais')
    telefono = request.form.get('telefono', '').strip()

    if nombre and codigo_pais and telefono:
        numero_completo = codigo_pais + telefono.replace("-", "").replace(" ", "")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO miembros (nombre, telefono) VALUES (%s, %s)", 
                      (nombre, numero_completo))
        conn.commit()
        cursor.close()
        flash('✅ Miembro agregado correctamente', 'success')
    else:
        flash('⚠️ Nombre, código de país y teléfono son obligatorios', 'warning')
    
    return redirect(url_for('miembros.listar'))

# ==================== EDITAR MIEMBRO ====================
@miembros_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        codigo_pais = request.form.get('codigo_pais')
        telefono = request.form.get('telefono', '').strip()

        if nombre and codigo_pais and telefono:
            numero_completo = codigo_pais + telefono.replace("-", "").replace(" ", "")
            
            cursor.execute("UPDATE miembros SET nombre = %s, telefono = %s WHERE id = %s", 
                          (nombre, numero_completo, id))
            conn.commit()
            flash('✏️ Miembro actualizado correctamente', 'success')
            cursor.close()
            return redirect(url_for('miembros.listar'))
        else:
            flash('⚠️ Nombre, código de país y teléfono son obligatorios', 'warning')

    cursor.execute("SELECT * FROM miembros WHERE id = %s", (id,))
    miembro = cursor.fetchone()
    cursor.close()
    return render_template("editar_miembro.html", miembro=miembro)

# ==================== ELIMINAR MIEMBRO ====================
@miembros_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM miembros WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    flash('🗑️ Miembro eliminado', 'danger')
    return redirect(url_for('miembros.listar'))