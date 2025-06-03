from flask_socketio import Namespace, emit
from app import db
from app.models import Position
from datetime import datetime, time
import schedule
import time as time_module
import threading

def clean_database():
    Position.query.delete()
    db.session.commit()
    print("Database cleaned at", datetime.now())

def run_scheduler():
    schedule.every().day.at("18:00").do(clean_database)
    while True:
        schedule.run_pending()
        time_module.sleep(60)

# Démarrer le scheduler dans un thread séparé
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

class ws(Namespace):
    def on_connect(self):
        print('Client connected')
        positions = Position.query.all()
        for position in positions:
            emit('new_position', {
                'normalizedX': position.normalized_x,
                'normalizedY': position.normalized_y,
                'pseudo': position.pseudo,
                'salle': position.salle,
                'groupe': position.groupe,
                'timestamp': position.timestamp.timestamp() * 1000
            })

    def on_disconnect(self, reason=None):
        print(f'Client disconnected: {reason}')

    def on_report_position(self, data):
        print("Received data:", data)  # Debugging line
        required_keys = ['normalizedX', 'normalizedY', 'pseudo', 'salle', 'groupe', 'timestamp']
        if not all(key in data for key in required_keys):
            print("Missing required keys in data")
            return
        position = Position(
            normalized_x=data['normalizedX'],
            normalized_y=data['normalizedY'],
            pseudo=data['pseudo'],
            salle=data['salle'],
            groupe=data['groupe'],
            timestamp=datetime.fromtimestamp(data['timestamp'] / 1000)
        )
        db.session.add(position)
        db.session.commit()
        emit('new_position', data, broadcast=True)
