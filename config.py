# config.py
import os

class Config:
    # Clave secreta (cámbiala por una segura en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'iglesia-app-secret-key-2026-cambia-esta-clave')

    # Configuración de la base de datos SQLite
    if os.environ.get('RENDER') or os.path.exists('/data'):
        # En Render con Disco persistente
        DATABASE = '/data/iglesia.db'
    else:
        # En local
        DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iglesia.db')

    # Otras configuraciones útiles
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'