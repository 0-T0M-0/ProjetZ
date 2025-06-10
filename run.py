import eventlet
eventlet.monkey_patch()

import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        debug=False,  # Désactiver le mode debug en production
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 2000)),
        use_reloader=False,  # Désactiver le rechargement automatique
        log_output=False,  # Désactiver les logs
        allow_unsafe_werkzeug=True  # Nécessaire pour le développement
    )
