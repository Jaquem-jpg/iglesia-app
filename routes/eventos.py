# routes/eventos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import query_db
from decorators import login_required, admin_required

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

# LISTAR EVENTOS - Versión mínima y segura
@eventos_bp.route('/')
@login_required
def listar():
    search = request.args.get('search', '').strip()

    if search:
        eventos = query_db("""
            SELECT * FROM eventos 
            WHERE titulo ILIKE %s 
               OR lugar ILIKE %s 
               OR descripcion ILIKE %s
            ORDER BY fecha DESC, hora DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%"), fetchall=True)
    else:
        eventos = query_db(
            "SELECT * FROM eventos ORDER BY fecha DESC, hora DESC",
            fetchall=True
        )

    return render_template("eventos.html", eventos=eventos, search=search)


# AGREGAR EVENTO
@eventos_bp.route('/agregar', methods=['POST'])
@admin_required
def agregar():
    titulo = request.form.get('titulo', '').strip()
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    lugar = request.form.get('lugar', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if titulo and fecha:
        query_db("""
            INSERT INTO eventos (titulo, fecha, hora, lugar, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, fecha, hora, lugar, descripcion), commit=True)
        flash('✅ Evento agregado correctamente', 'success')
    else:
        flash('⚠️ Título y fecha son obligatorios', 'warning')

    return redirect(url_for('eventos.listar'))


# EDITAR EVENTO
@eventos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        lugar = request.form.get('lugar', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if titulo and fecha:
            query_db("""
                UPDATE eventos 
                SET titulo=%s, fecha=%s, hora=%s, lugar=%s, descripcion=%s
                WHERE id=%s
            """, (titulo, fecha, hora, lugar, descripcion, id), commit=True)
            flash('✏️ Evento actualizado', 'success')
            return redirect(url_for('eventos.listar'))

    evento = query_db("SELECT * FROM eventos WHERE id=%s", (id,), fetchone=True)
    return render_template("editar_evento.html", evento=evento)


# ELIMINAR EVENTO
@eventos_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    query_db("DELETE FROM eventos WHERE id=%s", (id,), commit=True)
    flash('🗑️ Evento eliminado', 'danger')
    return redirect(url_for('eventos.listar'))