from flask import Blueprint, render_template, request, redirect, url_for, flash
from decorators import login_required, admin_required
from models.db import get_db

miembros_bp = Blueprint('miembros', __name__, url_prefix='/miembros')

@miembros_bp.route('/', methods=['GET'])
@login_required
def listar():
    search = request.args.get('search', '').strip()
    db = get_db()
    
    if search:
        miembros = db.execute(
            "SELECT * FROM miembros WHERE nombre LIKE ? ORDER BY nombre",
            (f'%{search}%',)
        ).fetchall()
    else:
        miembros = db.execute("SELECT * FROM miembros ORDER BY nombre").fetchall()
    
    return render_template("miembros.html", miembros=miembros, search=search)