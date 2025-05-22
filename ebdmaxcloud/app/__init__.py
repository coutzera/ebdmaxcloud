from flask import Flask
from app.controllers.pedido_controller import pedido_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(pedido_bp)

    return app

app = create_app()