# Z-tracker

## Description
Z-tracker est une application Flask pour localiser le Z dans un bâtiment en temps réel. Elle utilise Flask, Flask-SocketIO, Flask-SQLAlchemy et une carte interactive avec JavaScript.

## Installation
1. Cloner le dépôt
2. Créer un environnement virtuel et l'activer
3. Installer les dépendances : `pip install -r requirements.txt`
4. Exécuter l'application : `python run.py`

## Fonctionnalités
- Page /map affiche la carte et un canvas superposé.
- L'utilisateur clique sur la carte pour signaler la position du Z (coordonnées + pseudo + salle).
- Le serveur reçoit via WebSocket l'événement 'report_position', sauvegarde en base et diffuse à tous les clients via 'new_position'.
- Le frontend dessine les positions en cercles rouges avec labels (pseudo, salle, heure).
- Gestion du namespace Socket.IO '/ws' côté client et serveur.

## Architecture projet
```bash
z-tracker/
│
├── app/
│   ├── __init__.py           # Initialisation Flask
│   ├── routes.py             # Routes web (pages HTML)
│   ├── api.py                # API REST (POST et GET)
│   ├── sockets.py            # WebSocket (via Flask-SocketIO)
│   ├── models.py             # Modèles de données (user, agent Z)
│   ├── templates/            # Fichiers HTML (Jinja2)
│   │   └── index.html
│   └── static/
│       ├── js/
│       │   └── map.js        # Gestion JS de la carte + Socket.IO
│       ├── css/
│       │   └── style.css
│       └── images/
│           └── map.png       # Plan simplifié du bâtiment
│
├── run.py                   # Point d’entrée Flask
├── config.py                # Configuration de l’application
├── requirements.txt         # Dépendances
└── README.md
```
