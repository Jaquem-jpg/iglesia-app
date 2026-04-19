from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import query_db
from decorators import login_required, admin_required

miembros_bp = Blueprint('miembros', __name__, url_prefix='/miembros')

@miembros_bp.route('/')
@login_required
def listar():
    search = request.args.get('search', '').strip()
    
    if search:
        miembros = query_db(
            "SELECT * FROM miembros WHERE nombre ILIKE %s ORDER BY nombre",
            (f"%{search}%",),
            fetchall=True
        )
    else:
        miembros = query_db("SELECT * FROM miembros ORDER BY nombre", fetchall=True)
    
    return render_template("miembros.html", miembros=miembros, search=search)

@miembros_bp.route('/agregar', methods=['POST'])
@admin_required
def agregar():
    nombre = request.form.get('nombre', '').strip()
    codigo_pais = request.form.get('codigo_pais')
    telefono = request.form.get('telefono', '').strip()

    if nombre and codigo_pais and telefono:
        numero_completo = codigo_pais + telefono.replace("-", "").replace(" ", "")
        
        query_db(
            "INSERT INTO miembros (nombre, telefono) VALUES (%s, %s)",
            (nombre, numero_completo),
            commit=True
        )
        flash('✅ Miembro agregado correctamente', 'success')
    else:
        flash('⚠️ Nombre, código de país y teléfono son obligatorios', 'warning')
    
    return redirect(url_for('miembros.listar'))

@miembros_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        codigo_pais = request.form.get('codigo_pais')
        telefono = request.form.get('telefono', '').strip()

        if nombre and codigo_pais and telefono:
            numero_completo = codigo_pais + telefono.replace("-", "").replace(" ", "")
            
            query_db(
                "UPDATE miembros SET nombre = %s, telefono = %s WHERE id = %s",
                (nombre, numero_completo, id),
                commit=True
            )
            flash('✏️ Miembro actualizado correctamente', 'success')
            return redirect(url_for('miembros.listar'))
        else:
            flash('⚠️ Nombre, código de país y teléfono son obligatorios', 'warning')

    miembro = query_db("SELECT * FROM miembros WHERE id = %s", (id,), fetchone=True)
    return render_template("editar_miembro.html", miembro=miembro)

@miembros_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    query_db("DELETE FROM miembros WHERE id = %s", (id,), commit=True)
    flash('🗑️ Miembro eliminado', 'danger')
    return redirect(url_for('miembros.listar'))