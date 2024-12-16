from flask import Flask
from asgiref.wsgi import WsgiToAsgi
from app import create_app

# Crea la instancia de Flask usando tu factory function
app = create_app()

# Convierte la app WSGI a ASGI
asgi_app = WsgiToAsgi(app)
