import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'iglesia-secret-key-2024')
    
    # Detectar si estamos en Render
    IS_RENDER = os.environ.get('RENDER', False)
    
    if IS_RENDER:
        # En Render, usar disco persistente
        DATABASE = '/data/iglesia.db'
    else:
        # Local: usar archivo en el mismo directorio
        DATABASE = 'iglesia.db'