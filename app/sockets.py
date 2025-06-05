from flask_socketio import Namespace, emit
from app import db
from app.models import Position
from datetime import datetime, time, timedelta
import schedule
import time as time_module
import threading
from functools import lru_cache
from sqlalchemy import desc

# Cache pour stocker les dernières positions
POSITIONS_CACHE = []
CACHE_TIMESTAMP = None
CACHE_DURATION = 60  # Durée du cache en secondes

def get_cached_positions():
    global POSITIONS_CACHE, CACHE_TIMESTAMP
    current_time = datetime.now()
    
    if (CACHE_TIMESTAMP is None or 
        (current_time - CACHE_TIMESTAMP).total_seconds() > CACHE_DURATION):
        # Mettre à jour le cache
        POSITIONS_CACHE = Position.query.order_by(desc(Position.timestamp)).limit(100).all()
        CACHE_TIMESTAMP = current_time
    
    return POSITIONS_CACHE

def clean_database():
    # Ne garder que les positions des dernières 24 heures
    cutoff_time = datetime.now() - timedelta(hours=24)
    Position.query.filter(Position.timestamp < cutoff_time).delete()
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
        positions = get_cached_positions()
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
        print("Received data:", data)
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
            commentaire=data.get('commentaire', ''),
            timestamp=datetime.fromtimestamp(data['timestamp'] / 1000)
        )
        db.session.add(position)
        db.session.commit()
        
        # Invalider le cache
        global CACHE_TIMESTAMP
        CACHE_TIMESTAMP = None
        
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
            
            # Invalider le cache
            global CACHE_TIMESTAMP
            CACHE_TIMESTAMP = None
            
            emit('position_deleted', {'id': data['id']}, broadcast=True)
        else:
            print("Position not found or unauthorized deletion attempt")
