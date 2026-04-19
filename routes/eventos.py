from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import get_db
from decorators import login_required, admin_required

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

@eventos_bp.route('/')
@login_required
def listar():
    search = request.args.get('search', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    
    if search:
        cursor.execute("""
            SELECT * FROM eventos 
            WHERE titulo ILIKE %s OR lugar ILIKE %s OR descripcion ILIKE %s
            ORDER BY fecha, hora
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
        eventos = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM eventos ORDER BY fecha, hora")
        eventos = cursor.fetchall()
    
    cursor.close()
    return render_template("eventos.html", eventos=eventos, search=search)

# ==================== RUTAS DE ADMINISTRACIÓN (SOLO ADMIN) ====================

@eventos_bp.route('/agregar', methods=['POST'])
@admin_required
def agregar():
    titulo = request.form.get('titulo', '').strip()
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    lugar = request.form.get('lugar', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if titulo and fecha:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO eventos (titulo, fecha, hora, lugar, descripcion) 
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, fecha, hora, lugar, descripcion))
        conn.commit()
        cursor.close()
        flash('✅ Evento agregado correctamente', 'success')
    else:
        flash('⚠️ Título y fecha son obligatorios', 'warning')
    
    return redirect(url_for('eventos.listar'))

@eventos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        lugar = request.form.get('lugar', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if titulo and fecha:
            cursor.execute("""
                UPDATE eventos 
                SET titulo = %s, fecha = %s, hora = %s, lugar = %s, descripcion = %s
                WHERE id = %s
            """, (titulo, fecha, hora, lugar, descripcion, id))
            conn.commit()
            flash('✏️ Evento actualizado', 'success')
            cursor.close()
            return redirect(url_for('eventos.listar'))
    
    cursor.execute("SELECT * FROM eventos WHERE id = %s", (id,))
    evento = cursor.fetchone()
    cursor.close()
    return render_template("editar_evento.html", evento=evento)

@eventos_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    flash('🗑️ Evento eliminado', 'danger')
    return redirect(url_for('eventos.listar'))