# config.py
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'iglesia-app-secret-key-2026-cambia-esta-clave')

# Configuración de la base de datos SQLite
if os.environ.get('RENDER'):
    # Path recomendado para Render con disco persistente
    DATABASE = '/opt/render/project/src/data/iglesia.db'
else:
    # En local
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iglesia.db')