from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

from models.db import init_db, close_db, get_db
from decorators import login_required, admin_required

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'iglesia-secret-key-2024')

# ==================== INICIALIZAR DB (FIX REAL) ====================
with app.app_context():
    try:
        init_db()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print("❌ Error inicializando DB:", e)

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


# ==================== REGISTER ====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("❌ Campos obligatorios", "warning")
            return redirect(url_for("register"))

        db = get_db()
        cur = db.cursor()

        try:
            cur.execute(
                "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, 'invitado')",
                (username, password)
            )
            db.commit()
            flash("✅ Usuario creado", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("⚠️ Usuario ya existe", "danger")
        finally:
            cur.close()

    return render_template("register.html")


# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    flash("👋 Sesión cerrada", "info")
    return redirect(url_for("login"))


# ==================== DASHBOARD ====================
@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ==================== USUARIOS ====================
@app.route("/usuarios")
@admin_required
def listar_usuarios():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, username, rol FROM usuarios ORDER BY username")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/eliminar/<int:user_id>", methods=["POST"])
@admin_required
def eliminar_usuario(user_id):
    db = get_db()

    if user_id == session.get("user_id"):
        flash("⛔ No puedes eliminarte a ti mismo", "danger")
        return redirect(url_for("listar_usuarios"))

    cur = db.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    db.commit()
    cur.close()

    flash("🗑️ Usuario eliminado", "danger")
    return redirect(url_for("listar_usuarios"))


# ==================== BLUEPRINTS ====================
from routes.miembros import miembros_bp
from routes.eventos import eventos_bp

app.register_blueprint(miembros_bp)
app.register_blueprint(eventos_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)