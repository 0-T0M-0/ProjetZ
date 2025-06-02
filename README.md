# ProjetZ

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
