document.addEventListener('DOMContentLoaded', () => {
    const socket = io('/ws');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const map = document.getElementById('map');
    const formContainer = document.getElementById('form-container');
    const positionForm = document.getElementById('position-form');
    let positions = [];
    let userInfo = { pseudo: '', groupe: '' };
    let infoWindow = null;
    let clickX, clickY;

    // Fonction pour redimensionner le canvas en fonction de la taille de la fenêtre
    function resizeCanvas() {
        canvas.width = map.width;
        canvas.height = map.height;
        // Redessiner toutes les positions après le redimensionnement
        positions.forEach(pos => drawPosition(pos));
    }

    // Écouter le redimensionnement de la fenêtre
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            formContainer.style.display = 'none';
            if (infoWindow) {
                infoWindow.remove();
                infoWindow = null;
            }
        }
    });

    canvas.addEventListener('click', (event) => {
        const rect = canvas.getBoundingClientRect();
        // Convertir les coordonnées en valeurs normalisées (0-1)
        const normalizedX = (event.clientX - rect.left) / rect.width;
        const normalizedY = (event.clientY - rect.top) / rect.height;
        
        // Convertir en coordonnées canvas pour l'affichage
        clickX = normalizedX * canvas.width;
        clickY = normalizedY * canvas.height;

        let clickedOnDrop = false;
        positions.forEach(position => {
            // Convertir les coordonnées stockées en coordonnées canvas pour la comparaison
            const posX = position.normalizedX * canvas.width;
            const posY = position.normalizedY * canvas.height;
            if (Math.sqrt(Math.pow(posX - clickX, 2) + Math.pow(posY - clickY, 2)) < 20) {
                clickedOnDrop = true;
                if (infoWindow) {
                    infoWindow.remove();
                    infoWindow = null;
                } else {
                    infoWindow = document.createElement('div');
                    infoWindow.className = 'info-window';
                    infoWindow.style.left = `${event.clientX + 20}px`;
                    infoWindow.style.top = `${event.clientY - 50}px`;
                    infoWindow.innerHTML = `
                        <p>Pseudo: ${position.pseudo}</p>
                        <p>Salle: ${position.salle}</p>
                        <p>Groupe: ${position.groupe}</p>
                        <p>Heure: ${new Date(position.timestamp).toLocaleTimeString()}</p>
                    `;
                    document.body.appendChild(infoWindow);
                }
            }
        });
        if (!clickedOnDrop) {
            if (infoWindow) {
                infoWindow.remove();
                infoWindow = null;
            }
            if (formContainer.style.display === 'block') {
                formContainer.style.display = 'none';
            } else {
                formContainer.style.display = 'block';
                formContainer.style.left = `${event.clientX}px`;
                formContainer.style.top = `${event.clientY}px`;
                if (userInfo.pseudo) {
                    document.getElementById('pseudo').value = userInfo.pseudo;
                }
                if (userInfo.groupe) {
                    document.getElementById('groupe').value = userInfo.groupe;
                }
            }
        }
    });

    positionForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const pseudo = document.getElementById('pseudo').value;
        const salle = document.getElementById('salle').value;
        const groupe = document.getElementById('groupe').value;
        userInfo = { pseudo, groupe };
        
        // Utiliser les coordonnées normalisées pour l'envoi
        const normalizedX = clickX / canvas.width;
        const normalizedY = clickY / canvas.height;
        
        socket.emit('report_position', { 
            normalizedX, 
            normalizedY,
            pseudo, 
            salle, 
            groupe, 
            timestamp: Date.now() 
        });
        
        formContainer.style.display = 'none';
        positionForm.reset();
    });

    function getPositions() {
        return positions;
    }

    function isMorningEvent(timestamp) {
        const date = new Date(timestamp);
        return date.getHours() < 13;
    }

    function updateTable() {
        const table = document.getElementById('positions-table');
        if (!table) return;
        table.innerHTML = '';
        const header = document.createElement('tr');
        header.innerHTML = '<th onclick="sortTable(0)">Salle</th><th onclick="sortTable(1)">Horaire</th>';
        table.appendChild(header);
        positions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).forEach(position => {
            const row = document.createElement('tr');
            const isMorning = isMorningEvent(position.timestamp);
            const currentHour = new Date().getHours();
            if (currentHour >= 13 && isMorning) {
                row.style.color = '#888';
                row.style.fontStyle = 'italic';
            }
            row.innerHTML = `<td>${position.salle}</td><td>${new Date(position.timestamp).toLocaleTimeString()}</td>`;
            table.appendChild(row);
        });
    }

    function sortTable(n) {
        const table = document.getElementById('positions-table');
        const rows = Array.from(table.rows).slice(1);
        const sortedRows = rows.sort((a, b) => {
            const x = a.cells[n].textContent;
            const y = b.cells[n].textContent;
            return x.localeCompare(y);
        });
        rows.forEach(row => table.removeChild(row));
        sortedRows.forEach(row => table.appendChild(row));
    }

    function getSalleDistance(salle1, salle2) {
        // Si les salles sont dans le même bâtiment (même lettre)
        if (salle1[0] === salle2[0]) {
            // Si c'est le même étage
            if (salle1[1] === salle2[1]) {
                return Math.abs(parseInt(salle1.slice(2)) - parseInt(salle2.slice(2)));
            }
            // Si étages différents
            return Math.abs(parseInt(salle1[1]) - parseInt(salle2[1])) * 10;
        }
        // Si bâtiments différents
        return 100;
    }

    function predictNextSalle(positions) {
        if (positions.length < 2) return null;

        const lastHour = Date.now() - 3600000; // 1 heure en millisecondes
        const recentPositions = positions.filter(p => p.timestamp > lastHour);
        
        if (recentPositions.length === 0) return null;

        // Trier les positions par timestamp
        recentPositions.sort((a, b) => b.timestamp - a.timestamp);
        
        // Obtenir la dernière salle visitée
        const lastSalle = recentPositions[0].salle;
        
        // Créer un ensemble des salles déjà visitées dans la dernière heure
        const visitedSalles = new Set(recentPositions.map(p => p.salle));
        
        // Liste de toutes les salles possibles
        const allSalles = [
            'A012', 'A013', 'A016', 'A017', 'A101', 'A108', 'A110', 'A111', 'A115', 'A116',
            'D03', 'J006', 'J008', 'J009', 'J012', 'J101', 'J106', 'j107', 'J108', 'J204',
            'L208', 'L209', 'L211', 'L212', 'Foyer', 'Crous', 'Autre'
        ];
        
        // Filtrer les salles non visitées
        const unvisitedSalles = allSalles.filter(salle => !visitedSalles.has(salle));
        
        if (unvisitedSalles.length === 0) return null;
        
        // Trouver la salle non visitée la plus proche
        let closestSalle = unvisitedSalles[0];
        let minDistance = getSalleDistance(lastSalle, closestSalle);
        
        for (let i = 1; i < unvisitedSalles.length; i++) {
            const distance = getSalleDistance(lastSalle, unvisitedSalles[i]);
            if (distance < minDistance) {
                minDistance = distance;
                closestSalle = unvisitedSalles[i];
            }
        }
        
        return closestSalle;
    }

    function updatePrediction() {
        const prediction = predictNextSalle(positions);
        const predictionElement = document.getElementById('prediction');
        if (prediction) {
            predictionElement.textContent = `Prochaine salle probable : ${prediction}`;
        } else {
            predictionElement.textContent = 'Pas assez de données pour prédire';
        }
    }

    socket.on('new_position', (data) => {
        console.log('Received new position:', data);
        positions.push(data);
        drawPosition(data);
        updateTable();
        updatePrediction();
    });

    function drawPosition(data) {
        // Convertir les coordonnées normalisées en coordonnées canvas
        const x = data.normalizedX * canvas.width;
        const y = data.normalizedY * canvas.height;
        const r = 10; // rayon de la partie arrondie
        const h = 26; // hauteur totale de la goutte
    
        ctx.save();
    
        const isMorning = isMorningEvent(data.timestamp);
        const currentHour = new Date().getHours();
        if (currentHour >= 13 && isMorning) {
            ctx.globalAlpha = 0.5;
        }
    
        ctx.beginPath();
        // Partie ronde en haut
        ctx.arc(x, y - h / 2, r, Math.PI, 0, false);
    
        // Courbes vers la pointe en bas
        ctx.bezierCurveTo(x + r, y - h / 2 + r, x + 4, y + h / 2 - 4, x, y + h / 2);
        ctx.bezierCurveTo(x - 4, y + h / 2 - 4, x - r, y - h / 2 + r, x - r, y - h / 2);
    
        ctx.closePath();
    
        // Dégradé radial vers le bas
        const gradient = ctx.createRadialGradient(x, y - h / 2, 2, x, y, h / 1.2);
        gradient.addColorStop(0, '#6fbaff');
        gradient.addColorStop(1, '#2a75d1');
    
        ctx.fillStyle = gradient;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.15)';
        ctx.shadowBlur = 3;
        ctx.fill();
    
        ctx.restore();
    
        // Petit reflet blanc
        ctx.beginPath();
        ctx.arc(x - 3, y - h / 2, 2.5, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();
    
        // Texte salle + temps
        ctx.fillStyle = currentHour >= 13 && isMorning ? '#888' : 'black';
        ctx.font = '12px sans-serif';
        const timeAgo = getTimeAgo(data.timestamp);
        ctx.fillText(`${data.salle}, il y a ${timeAgo}`, x + 14, y);
    }

    function getTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        if (isNaN(past.getTime())) {
            return 'heure inconnue';
        }
        const diff = Math.max(0, Math.floor((now - past) / 60000));
        if (diff < 60) {
            return `${diff} min`;
        } else {
            return `${Math.floor(diff / 60)} h`;
        }
    }
});
