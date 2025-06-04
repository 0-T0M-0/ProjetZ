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
                'id': position.id,
                'normalizedX': position.normalized_x,
                'normalizedY': position.normalized_y,
                'pseudo': position.pseudo,
                'salle': position.salle,
                'groupe': position.groupe,
                'commentaire': position.commentaire,
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
            commentaire=data.get('commentaire', ''),  # Utiliser get() pour gérer le cas où commentaire n'est pas présent
            timestamp=datetime.fromtimestamp(data['timestamp'] / 1000)
        )
        db.session.add(position)
        db.session.commit()
        data['id'] = position.id
        emit('new_position', data, broadcast=True)

    def on_delete_position(self, data):
        print("Received delete request:", data)
        if 'id' not in data or 'pseudo' not in data:
            print("Missing required keys in delete request")
            return
        
        position = Position.query.get(data['id'])
        if position and position.pseudo == data['pseudo']:
            db.session.delete(position)
            db.session.commit()
            emit('position_deleted', {'id': data['id']}, broadcast=True)
        else:
            print("Position not found or unauthorized deletion attempt")
