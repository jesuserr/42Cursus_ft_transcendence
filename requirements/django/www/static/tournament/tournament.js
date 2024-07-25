document.addEventListener('DOMContentLoaded', () => {
    const tournamentName = JSON.parse(document.getElementById('tournament_name').textContent);
    document.getElementById('iframechat').src = `/chat/${tournamentName}`;

    const playButton = document.getElementById('play');
    const mainContainer = document.getElementById('mainContainer');
    const tstatus = document.getElementById('tstatus');
    const iframegame = document.getElementById('iframegame');

    playButton.addEventListener('click', () => {
        if (playButton.textContent === 'Waiting for players') {
            playButton.textContent = 'Tournament started';
            mainContainer.classList.add('tournament-started');
            tstatus.classList.add('visible');
            iframegame.focus();
        } else if (playButton.textContent === 'Tournament started') {
            playButton.textContent = 'Tournament finished';
            mainContainer.classList.remove('tournament-started');
            tstatus.classList.remove('visible');
        } else if (playButton.textContent === 'Tournament finished') {
            playButton.textContent = 'Waiting for players';
        }
    });

    const socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + tournamentName + '/');

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.hasOwnProperty("SET_CONNECTED_USER_LIST"))
            Set_Connected_User_List(data);
        else if (data.hasOwnProperty("SET_BUTTON_PLAY_STATUS"))
            Set_Button_Play_Status(data['SET_BUTTON_PLAY_STATUS']);
        else if (data.hasOwnProperty("REFRESH_TOURNAMENT_STATUS")) // Asegurarse de que el nombre sea correcto
            Refresh_Tournament_Status(data);
        else if (data.hasOwnProperty("START_GAME"))
            Start_Game(data['START_GAME']);
        else if (data.hasOwnProperty("TOURNAMENT_FINISHED"))
            Tournament_Finished(data['TOURNAMENT_FINISHED']);
        else if (data.hasOwnProperty("TOURNAMENT_LIST"))
            Tournament_List(data['TOURNAMENT_LIST']);
    };

    function Refresh_Tournament_Status(data) {
        let statusElement = document.querySelector('#tstatus');
        statusElement.classList.add('visible');
        let table = document.querySelector('#tstatusTable tbody');
        table.innerHTML = ""; // Clear existing rows
        let userList = data["REFRESH_TOURNAMENT_STATUS"];
        for (let user of userList) {
            let row = document.createElement('tr');
            let displayNameCell = document.createElement('td');
            displayNameCell.textContent = user.fields.display_name;
            row.appendChild(displayNameCell);
            let statusCell = document.createElement('td');
            statusCell.textContent = user.fields.status;
            row.appendChild(statusCell);
            table.appendChild(row);
        }
    }

    function Set_Button_Play_Status(data) {
        let playButton = document.querySelector('#play');
        playButton.disabled = data.status;
        playButton.textContent = data.text;
        const mainContainer = document.getElementById('mainContainer');
        const tstatus = document.getElementById('tstatus');
        if (data.text === 'Tournament started') {
            mainContainer.classList.add('tournament-started');
            tstatus.classList.add('visible');
        } else if (data.text === 'Tournament finished') {
            mainContainer.classList.remove('tournament-started');
            tstatus.classList.remove('visible');
        } else {
            mainContainer.classList.remove('tournament-started');
            tstatus.classList.remove('visible');
        }
    }

    document.querySelector('#play').onclick = function (e) {
        socket.send(JSON.stringify({'PLAY': 'PLAY'}));
    };

    function Set_Connected_User_List(data) {
        let table = document.getElementById("userTable");
        let existingRows = new Map(Array.from(table.children).map(row => [row.dataset.email, row]));
        let userList = data["SET_CONNECTED_USER_LIST"];
        for (let user of userList) {
            let email = user.fields.email;
            if (!existingRows.has(email)) {
                let row = document.createElement("tr");
                row.dataset.email = email;
                let displayNameCell = document.createElement("td");
                displayNameCell.textContent = user.fields.display_name;
                row.appendChild(displayNameCell);
                table.appendChild(row);
            } else {
                existingRows.delete(email);
            }
        }
        existingRows.forEach((row, email) => {
            table.removeChild(row);
        });
    }

    function Tournament_List(data) {
        var tournamentTable = document.getElementById('tournamentTable');
        var tableBody = tournamentTable.getElementsByTagName('tbody')[0];
        tableBody.innerHTML = "";
        for (var i = 0; i < data.length; i++) {
            var tournament = data[i];
            var row = document.createElement('tr');
            var nameCell = document.createElement('td');
            nameCell.textContent = tournament.tournament_name;
            row.appendChild(nameCell);
            var countCell = document.createElement('td');
            countCell.textContent = tournament.user_count;
            row.appendChild(countCell);
            var statusCell = document.createElement('td');
            statusCell.textContent = tournament.status;
            row.appendChild(statusCell);
            tableBody.appendChild(row);
        }
    }

    function Tournament_Finished(data) {
        var winnerElement = document.getElementById('winner');
        winnerElement.textContent = "The winner is " + data;
    }

	function Start_Game(data) {
		var iframe = document.getElementById('iframegame');
		iframe.src = data.name;
		setTimeout(function() {
			iframe.focus();
		}, 100); 
	}

    document.getElementById('create').addEventListener('click', function() {
        var tournamentName = document.getElementById('tournamentName').value;
        if (tournamentName !== '') {
            var urlPattern = /^[a-zA-Z0-9-._~:/?#[\]@!$&'()*+,;=]+$/;
            var tripleUnderscorePattern = /___/;
            if (urlPattern.test(tournamentName) && !tripleUnderscorePattern.test(tournamentName)) {
                window.location.href = "/tournament/" + tournamentName;
            } else {
                alert('The tournament name contains invalid characters or three consecutive underscores.');
            }
        } else {
            alert('The name of the tournament cannot be empty.');
        }
    });

    const tournamentTable = document.getElementById('tournamentTable');
    tournamentTable.addEventListener('click', (event) => {
        if (event.target.tagName === 'TD' && event.target.cellIndex === 0) {
            document.getElementById('tournamentName').value = event.target.textContent;
        }
    });
});
