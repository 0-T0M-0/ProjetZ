from flask_socketio import Namespace, emit
from app import db
from app.models import Position
from datetime import datetime

class ws(Namespace):
    def on_connect(self):
        print('Client connected')
        positions = Position.query.all()
        for position in positions:
            emit('new_position', {
                'x': position.x,
                'y': position.y,
                'pseudo': position.pseudo,
                'salle': position.salle,
                'groupe': position.groupe,
                'timestamp': position.timestamp.timestamp() * 1000
            })

    def on_disconnect(self):
        print('Client disconnected')

    def on_report_position(self, data):
        print("Received data:", data)  # Debugging line
        required_keys = ['x', 'y', 'pseudo', 'salle', 'groupe', 'timestamp']
        if not all(key in data for key in required_keys):
            print("Missing required keys in data")
            return
        position = Position(x=data['x'], y=data['y'], pseudo=data['pseudo'], salle=data['salle'], groupe=data['groupe'], timestamp=datetime.fromtimestamp(data['timestamp'] / 1000))
        db.session.add(position)
        db.session.commit()
        emit('new_position', data, broadcast=True)
