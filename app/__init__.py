from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO(
    async_mode='eventlet',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialisation des extensions
    db.init_app(app)
    socketio.init_app(app)

    # Enregistrement des blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Enregistrement des namespaces WebSocket
    from app.sockets import ws
    socketio.on_namespace(ws('/ws'))

    # Création du contexte de l'application
    with app.app_context():
        db.create_all()

    return app
