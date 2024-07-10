let playerCount = 3;

document.getElementById('addPlayer').addEventListener('click', function() {
    playerCount++;
    const playersContainer = document.getElementById('playersContainer');
    
    const playerEntry = document.createElement('div');
    playerEntry.classList.add('player-entry');
    
    const newPlayerLabel = document.createElement('label');
    newPlayerLabel.setAttribute('for', 'player' + playerCount);
    newPlayerLabel.textContent = 'Jugador ' + playerCount + ':';
    
    const newPlayerInput = document.createElement('input');
    newPlayerInput.type = 'text';
    newPlayerInput.id = 'player' + playerCount;
    newPlayerInput.name = 'player' + playerCount;
    newPlayerInput.required = true;
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.classList.add('removePlayer');
    removeButton.textContent = 'Eliminar';
    
    removeButton.addEventListener('click', function() {
        playersContainer.removeChild(playerEntry);
        updatePlayerLabels();
    });
    
    playerEntry.appendChild(newPlayerLabel);
    playerEntry.appendChild(newPlayerInput);
    playerEntry.appendChild(removeButton);
    playerEntry.appendChild(document.createElement('br'));
    
    playersContainer.appendChild(playerEntry);
});

document.getElementById('playerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const players = [];
    const playerInputs = document.querySelectorAll('#playersContainer input[type="text"]');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.style.display = 'none';
    
    for (const input of playerInputs) {
        const player = input.value.trim();
        const alphanumeric = /^[a-zA-Z0-9]+$/;
        if (!alphanumeric.test(player)) {
            errorMessage.textContent = 'Los nombres de los jugadores solo pueden contener letras y números: ' + player;
            errorMessage.style.display = 'block';
            return;
        }
        if (players.includes(player)) {
            errorMessage.textContent = 'No se permiten nombres de jugadores repetidos: ' + player;
            errorMessage.style.display = 'block';
            return;
        }
        players.push(player);
    }

    if (players.length < 3) {
        errorMessage.textContent = 'Se requieren al menos 3 jugadores.';
        errorMessage.style.display = 'block';
        return;
    }

    // Mezclar jugadores de manera aleatoria
    players.sort(() => Math.random() - 0.5);

    // Guardar los jugadores mezclados en localStorage
    localStorage.setItem('players', JSON.stringify(players));

    // Crear la tabla de torneo
    createTournamentTable(players);

    // Iniciar el primer juego
    startNextGame();
});

function updatePlayerLabels() {
    const playerEntries = document.querySelectorAll('.player-entry');
    playerCount = playerEntries.length;

    playerEntries.forEach((entry, index) => {
        const label = entry.querySelector('label');
        const input = entry.querySelector('input');
        
        label.setAttribute('for', 'player' + (index + 1));
        label.textContent = 'Jugador ' + (index + 1) + ':';
        input.id = 'player' + (index + 1);
        input.name = 'player' + (index + 1);
    });
}

function createTournamentTable(players) {
    const tournamentBody = document.getElementById('tournamentBody');
    tournamentBody.innerHTML = '';
    
    players.forEach(player => {
        const row = document.createElement('tr');
        
        const playerCell = document.createElement('td');
        playerCell.textContent = player;
        
        const statusCell = document.createElement('td');
        statusCell.textContent = 'Pendiente';
        
        row.appendChild(playerCell);
        row.appendChild(statusCell);
        
        tournamentBody.appendChild(row);
    });

    document.getElementById('tournamentTable').style.display = 'block';
}

function updateTournamentTable(player, status) {
    const rows = document.querySelectorAll('#tournamentBody tr');
    rows.forEach(row => {
        if (row.cells[0].textContent === player) {
            row.cells[1].textContent = status;
        }
    });
}

function startNextGame() {
    const players = JSON.parse(localStorage.getItem('players'));

    if (players.length < 2) {
        document.getElementById('winner').innerText = players[0];
        document.getElementById('result').style.display = 'block';
        document.getElementById('gameContainer').style.display = 'none';
        updateTournamentTable(players[0], 'Ganador');
        return;
    }

    const player1 = players.shift();
    const player2 = players.shift();
    localStorage.setItem('players', JSON.stringify(players));
    
    updateTournamentTable(player1, 'Jugando');
    updateTournamentTable(player2, 'Jugando');
    
    const iframe = document.getElementById('pongGame');
    const remotePongGameUrl = "/game6/general";
    const baseUrl = window.location.origin; // Obtiene el origen del dominio actual
    const url = new URL(remotePongGameUrl, baseUrl);

    url.searchParams.set('player1', player1);
    url.searchParams.set('player2', player2);
    iframe.src = url.toString();

    document.getElementById('gameContainer').style.display = 'block';
    document.getElementById('playerForm').style.display = 'none';
    
    window.addEventListener('message', function(event) {
        if (event.origin === baseUrl) {
            const winner = event.data.winner;
            const loser = winner === player1 ? player2 : player1;
            
            updateTournamentTable(winner, 'Ganador de ronda');
            updateTournamentTable(loser, 'Perdedor');

            players.push(winner);
            localStorage.setItem('players', JSON.stringify(players));
            startNextGame();
        }
    }, { once: true });
}
