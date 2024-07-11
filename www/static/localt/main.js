let playerCount = 3;

document.getElementById('addPlayer').addEventListener('click', function() {
    playerCount++;
    const playersContainer = document.getElementById('playersContainer');
    
    const playerEntry = document.createElement('div');
    playerEntry.classList.add('player-entry');
    
    const newPlayerLabel = document.createElement('label');
    newPlayerLabel.setAttribute('for', 'player' + playerCount);
    newPlayerLabel.textContent = 'Player ' + playerCount + ':';
    
    const newPlayerInput = document.createElement('input');
    newPlayerInput.type = 'text';
    newPlayerInput.id = 'player' + playerCount;
    newPlayerInput.name = 'player' + playerCount;
    newPlayerInput.required = true;
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.classList.add('removePlayer');
    removeButton.textContent = 'Remove';
    
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
            errorMessage.textContent = 'Player names can only contain letters and numbers: ' + player;
            errorMessage.style.display = 'block';
            return;
        }
        if (players.includes(player)) {
            errorMessage.textContent = 'Duplicate player names are not allowed: ' + player;
            errorMessage.style.display = 'block';
            return;
        }
        players.push(player);
    }

    if (players.length < 3) {
        errorMessage.textContent = 'At least 3 players are required.';
        errorMessage.style.display = 'block';
        return;
    }

    // Shuffle players randomly
    players.sort(() => Math.random() - 0.5);

    // Save shuffled players in localStorage
    localStorage.setItem('players', JSON.stringify(players));

    // Create tournament table
    createTournamentTable(players);

    // Start the first game
    startNextGame();
});

function updatePlayerLabels() {
    const playerEntries = document.querySelectorAll('.player-entry');
    playerCount = playerEntries.length;

    playerEntries.forEach((entry, index) => {
        const label = entry.querySelector('label');
        const input = entry.querySelector('input');
        
        label.setAttribute('for', 'player' + (index + 1));
        label.textContent = 'Player ' + (index + 1) + ':';
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
        statusCell.textContent = 'Pending';
        
        row.appendChild(playerCell);
        row.appendChild(statusCell);
        
        tournamentBody.appendChild(row);
    });

    document.getElementById('mainContainer').style.display = 'flex';
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

function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

function startNextGame() {
    const players = JSON.parse(localStorage.getItem('players'));

    if (players.length < 2) {
        document.getElementById('winner').innerText = players[0];
        document.getElementById('result').style.display = 'block';
        document.getElementById('gameContainer').style.display = 'none';
        document.getElementById('tournamentTable').style.display = 'none';
        return;
    }

    const player1 = players.shift();
    const player2 = players.shift();
    localStorage.setItem('players', JSON.stringify(players));
    
    updateTournamentTable(player1, 'Playing');
    updateTournamentTable(player2, 'Playing');
    
    const iframe = document.getElementById('pongGame');
    const randomString = generateRandomString(10); // Generate a random string of length 10
    const remotePongGameUrl = `/game6/${randomString}`;
    const baseUrl = window.location.origin; // Get the current domain origin
    const url = new URL(remotePongGameUrl, baseUrl);

    url.searchParams.set('player1', player1);
    url.searchParams.set('player2', player2);
    iframe.src = url.toString();

    document.getElementById('gameContainer').style.display = 'block';
    document.getElementById('playerForm').style.display = 'none';
}

window.addEventListener('message', function(event) {
    const baseUrl = window.location.origin; // Ensure the message comes from the same origin
    if (event.origin === baseUrl) {
        const winner = event.data.winner;
        const players = JSON.parse(localStorage.getItem('players'));
        const iframe = document.getElementById('pongGame');
        const urlParams = new URLSearchParams(new URL(iframe.src).search);
        const player1 = urlParams.get('player1');
        const player2 = urlParams.get('player2');
        const loser = winner === player1 ? player2 : player1;

        updateTournamentTable(winner, 'Round Winner');
        updateTournamentTable(loser, 'Loser');

        if (players.length === 0) {
            // End of tournament
            document.getElementById('winner').innerText = winner;
            document.getElementById('result').style.display = 'block';
            document.getElementById('gameContainer').style.display = 'none';
            document.getElementById('tournamentTable').style.display = 'none';
        } else {
            players.push(winner);
            localStorage.setItem('players', JSON.stringify(players));
            startNextGame();
        }
    }
});

document.getElementById('restartButton').addEventListener('click', function() {
    location.reload(); // Reload the page to start a new tournament
});
