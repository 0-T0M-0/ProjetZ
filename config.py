import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ztracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WebSocket optimizations
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or 'redis://'
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    SOCKETIO_MAX_HTTP_BUFFER_SIZE = 1000000  # 1MB
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*'
    SOCKETIO_ENGINEIO_LOGGER = False
    SOCKETIO_LOGGER = False
