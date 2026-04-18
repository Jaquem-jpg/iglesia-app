# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("🔒 Debes iniciar sesión primero", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("⛔ Solo los administradores pueden realizar esta acción", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function