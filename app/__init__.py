from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*')

    from app.routes import main
    app.register_blueprint(main)

    from app.sockets import ws
    socketio.on_namespace(ws('/ws'))

    return app
