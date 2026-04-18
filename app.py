from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models.db import init_db, close_db, get_db
from decorators import login_required, admin_required
import os

app = Flask(__name__)

# ==================== CONFIGURACIÓN ====================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'iglesia-secret-key-2024')

# Usar PostgreSQL en producción (Render) o SQLite en local
if os.environ.get('DATABASE_URL'):
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
    print("✅ Usando PostgreSQL en producción")
else:
    # Local: usar SQLite
    app.config['DATABASE'] = 'iglesia.db'
    print("✅ Usando SQLite local")

# ==================== INICIALIZAR BASE DE DATOS ====================
with app.app_context():
    try:
        if os.environ.get('DATABASE_URL'):
            # PostgreSQL
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT 1 FROM usuarios LIMIT 1")
            cur.close()
            print("✅ PostgreSQL: Base de datos ya existe")
        else:
            # SQLite local
            import sqlite3
            conn = sqlite3.connect('iglesia.db')
            conn.close()
            print("✅ SQLite local listo")
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
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session["logged_in"] = True
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["rol"] = user[3]

            flash(f"✅ Bienvenido, {user[1]}", "success")
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
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, 'invitado')",
                (username, password)
            )
            db.commit()
            flash("✅ Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("⚠️ Ese nombre de usuario ya está registrado. Elige otro.", "danger")
        finally:
            cur.close()

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
    cur = db.cursor()
    cur.execute("SELECT id, username, rol FROM usuarios ORDER BY username")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("usuarios.html", usuarios=usuarios)

# ==================== ELIMINAR USUARIO (SOLO ADMIN) ====================
@app.route("/usuarios/eliminar/<int:user_id>", methods=["POST"])
@admin_required
def eliminar_usuario(user_id):
    db = get_db()
    if user_id == session.get("user_id"):
        flash("⛔ No puedes eliminar tu propia cuenta", "danger")
        return redirect(url_for("listar_usuarios"))
    
    cur = db.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    db.commit()
    cur.close()
    flash("🗑️ Usuario eliminado correctamente", "danger")
    return redirect(url_for("listar_usuarios"))

# ==================== EXPORTAR MIEMBROS (COMENTADO) ====================
# @app.route("/miembros/exportar")
# @admin_required
# def exportar_miembros():
#     flash("⏳ Función de exportación en desarrollo", "info")
#     return redirect(url_for("dashboard"))

# ==================== BLUEPRINTS ====================
from routes.miembros import miembros_bp
from routes.eventos import eventos_bp

app.register_blueprint(miembros_bp)
app.register_blueprint(eventos_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)