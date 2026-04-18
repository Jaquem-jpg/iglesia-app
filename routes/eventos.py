# routes/eventos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import get_db
from decorators import login_required, admin_required

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

@eventos_bp.route('/')
@login_required
def listar():
    search = request.args.get('search', '').strip()
    db = get_db()
    
    if search:
        query = """
            SELECT * FROM eventos 
            WHERE titulo LIKE ? OR lugar LIKE ? OR descripcion LIKE ?
            ORDER BY fecha, hora
        """
        eventos = db.execute(query, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        eventos = db.execute("SELECT * FROM eventos ORDER BY fecha, hora").fetchall()
    
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
        db = get_db()
        db.execute("""
            INSERT INTO eventos (titulo, fecha, hora, lugar, descripcion) 
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, fecha, hora, lugar, descripcion))
        db.commit()
        flash('✅ Evento agregado correctamente', 'success')
    else:
        flash('⚠️ Título y fecha son obligatorios', 'warning')
    
    return redirect(url_for('eventos.listar'))

@eventos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    db = get_db()
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        lugar = request.form.get('lugar', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if titulo and fecha:
            db.execute("""
                UPDATE eventos 
                SET titulo = ?, fecha = ?, hora = ?, lugar = ?, descripcion = ?
                WHERE id = ?
            """, (titulo, fecha, hora, lugar, descripcion, id))
            db.commit()
            flash('✏️ Evento actualizado', 'success')
            return redirect(url_for('eventos.listar'))
    
    evento = db.execute("SELECT * FROM eventos WHERE id = ?", (id,)).fetchone()
    return render_template("editar_evento.html", evento=evento)

@eventos_bp.route('/eliminar/<int:id>', methods=['POST'])
@admin_required
def eliminar(id):
    db = get_db()
    db.execute("DELETE FROM eventos WHERE id = ?", (id,))
    db.commit()
    flash('🗑️ Evento eliminado', 'danger')
    return redirect(url_for('eventos.listar'))