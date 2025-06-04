from app import db
from datetime import datetime

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    normalized_x = db.Column(db.Float, nullable=False)
    normalized_y = db.Column(db.Float, nullable=False)
    pseudo = db.Column(db.String(50), nullable=False)
    salle = db.Column(db.String(50), nullable=False)
    groupe = db.Column(db.String(50), nullable=False)
    commentaire = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Position {self.pseudo} in {self.salle} at {self.timestamp}>'
