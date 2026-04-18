from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models.db import init_db, close_db, get_db
from decorators import login_required, admin_required
# import pandas as pd  # COMENTADO TEMPORALMENTE
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']

# Inicializar base de datos solo si no existe
with app.app_context():
    db = get_db()
    try:
        # Verificar si la tabla usuarios existe
        db.execute("SELECT 1 FROM usuarios LIMIT 1")
        print("✅ Base de datos ya existe")
    except:
        print("📦 Creando base de datos por primera vez...")
        init_db()

app.teardown_appcontext(close_db)

# ==================== LOGIN ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        user = db.execute(
            "SELECT * FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        if user:
            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["rol"] = user["rol"]

            flash(f"✅ Bienvenido, {user['username']}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")

# ==================== REGISTRO ====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("❌ Usuario y contraseña son obligatorios", "warning")
            return redirect(url_for("register"))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, 'invitado')",
                (username, password)
            )
            db.commit()
            flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("⚠️ Ese nombre de usuario ya está registrado. Elige otro.", "danger")

    return render_template("register.html")

# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    flash("👋 Has cerrado sesión", "info")
    return redirect(url_for("login"))

# ==================== DASHBOARD ====================
@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ==================== VER USUARIOS (SOLO ADMIN) ====================
@app.route("/usuarios")
@admin_required
def listar_usuarios():
    db = get_db()
    usuarios = db.execute("SELECT id, username, rol FROM usuarios ORDER BY username").fetchall()
    return render_template("usuarios.html", usuarios=usuarios)

# ==================== ELIMINAR USUARIO (SOLO ADMIN) ====================
@app.route("/usuarios/eliminar/<int:user_id>", methods=["POST"])
@admin_required
def eliminar_usuario(user_id):
    db = get_db()
    if user_id == session.get("user_id"):
        flash("⛔ No puedes eliminar tu propia cuenta", "danger")
        return redirect(url_for("listar_usuarios"))
    
    db.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    db.commit()
    flash("🗑️ Usuario eliminado correctamente", "danger")
    return redirect(url_for("listar_usuarios"))

# ==================== EXPORTAR MIEMBROS A EXCEL (SOLO ADMIN) ====================
# COMENTADO TEMPORALMENTE - Problema con pandas en Python 3.14
# @app.route("/miembros/exportar")
# @admin_required
# def exportar_miembros():
#     db = get_db()
#     miembros = db.execute("SELECT nombre, telefono FROM miembros ORDER BY nombre").fetchall()
# 
#     df = pd.DataFrame(miembros, columns=["Nombre", "Teléfono (WhatsApp)"])
#     df.to_excel('miembros.xlsx', index=False, engine='openpyxl')
# 
#     return send_file(
#         'miembros.xlsx',
#         as_attachment=True,
#         download_name='Miembros_Iglesia.xlsx'
#     )

# ==================== BLUEPRINTS ====================
from routes.miembros import miembros_bp
from routes.eventos import eventos_bp

app.register_blueprint(miembros_bp)
app.register_blueprint(eventos_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)