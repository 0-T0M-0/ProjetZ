from app import create_app, db
from app.models import Position
from datetime import datetime, timedelta
import time

def create_test_data():
    app = create_app()
    with app.app_context():
        # Nettoyer la base de données
        Position.query.delete()
        db.session.commit()

        # Créer des positions du matin (avant 13h)
        morning_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        morning_positions = [
            Position(x=100, y=100, pseudo="Test1", salle="A012", groupe="P01", timestamp=morning_time),
            Position(x=200, y=200, pseudo="Test2", salle="J101", groupe="P02", timestamp=morning_time + timedelta(minutes=30)),
            Position(x=300, y=300, pseudo="Test3", salle="L208", groupe="P03", timestamp=morning_time + timedelta(hours=1))
        ]

        # Créer des positions de l'après-midi (après 13h)
        afternoon_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        afternoon_positions = [
            Position(x=150, y=150, pseudo="Test4", salle="A013", groupe="P04", timestamp=afternoon_time),
            Position(x=250, y=250, pseudo="Test5", salle="J102", groupe="P05", timestamp=afternoon_time + timedelta(minutes=30)),
            Position(x=350, y=350, pseudo="Test6", salle="L209", groupe="P06", timestamp=afternoon_time + timedelta(hours=1))
        ]

        # Ajouter toutes les positions à la base de données
        for position in morning_positions + afternoon_positions:
            db.session.add(position)
        
        db.session.commit()
        print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data() 