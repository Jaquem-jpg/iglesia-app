# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models.db import init_db, close_db, get_db
from decorators import login_required, admin_required
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']

# Inicializar base de datos
with app.app_context():
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
            flash("✅ Registro exitoso", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("⚠️ Ese usuario ya existe", "danger")

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

# ==================== EXPORTAR MIEMBROS A EXCEL ====================
@app.route("/miembros/exportar")
@admin_required
def exportar_miembros():
    db = get_db()
    miembros = db.execute("SELECT nombre, telefono FROM miembros ORDER BY nombre").fetchall()

    import pandas as pd
    df = pd.DataFrame(miembros, columns=["Nombre", "Teléfono (WhatsApp)"])
    df.to_excel('miembros.xlsx', index=False)

    return send_file(
        'miembros.xlsx',
        as_attachment=True,
        download_name='Miembros_Iglesia.xlsx'
    )

# ==================== BLUEPRINTS ====================
from routes.miembros import miembros_bp
from routes.eventos import eventos_bp

app.register_blueprint(miembros_bp)
app.register_blueprint(eventos_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)