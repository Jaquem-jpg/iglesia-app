# routes/eventos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import query_db
from decorators import login_required, admin_required
from datetime import date

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')


@eventos_bp.route('/')
@login_required
def listar():
    filtro = request.args.get('filtro', 'proximos')
    search = request.args.get('search', '').strip()

    hoy = date.today()

    if search:
        base_sql = """
            SELECT * FROM eventos 
            WHERE (titulo ILIKE %s OR lugar ILIKE %s OR descripcion ILIKE %s)
        """
        params = [f"%{search}%", f"%{search}%", f"%{search}%"]
    else:
        base_sql = "SELECT * FROM eventos"
        params = []

    if filtro == 'proximos':
        sql = base_sql + " AND fecha >= %s ORDER BY fecha ASC, hora ASC"
        params.append(hoy)
    else:
        sql = base_sql + " AND fecha < %s ORDER BY fecha DESC, hora DESC"
        params.append(hoy)

    eventos = query_db(sql, params, fetchall=True)

    return render_template(
        "eventos.html", 
        eventos=eventos, 
        search=search, 
        filtro=filtro
    )


# Resto de rutas (agregar, editar, eliminar) se mantienen igual
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


@eventos_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    query_db("DELETE FROM eventos WHERE id=%s", (id,), commit=True)
    flash('🗑️ Evento eliminado', 'danger')
    return redirect(url_for('eventos.listar'))