const tournamentName = JSON.parse(document.getElementById('tournament_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + tournamentName + '/');


socket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	//console.log(data);
	if (data.hasOwnProperty("SET_CONNECTED_USER_LIST"))
		Set_Connected_User_List(data);
	else if (data.hasOwnProperty("SET_BUTTON_PLAY_STATUS"))
		Set_Button_Play_Status(data['SET_BUTTON_PLAY_STATUS']);
	else if (data.hasOwnProperty("REFRESH_TURNAMENT_STATUS"))
		Refresh_Tournament_Status(data);
	else if (data.hasOwnProperty("START_GAME"))
		Start_Game(data['START_GAME']);
	else if (data.hasOwnProperty("TOURNAMENT_FINISHED"))
		Tournament_Finished(data['TOURNAMENT_FINISHED'])
	else if (data.hasOwnProperty("TOURNAMENT_LIST"))
		Tournament_List(data['TOURNAMENT_LIST'])
};

document.addEventListener('DOMContentLoaded', function() {
    var tabla = document.getElementById('tournamentTable');
    tabla.addEventListener('click', function(e) {
        if (e.target.tagName === 'TD' && e.target.cellIndex === 0) {
            var esTitulo = e.target.closest('tr').rowIndex === 0;
            if (!esTitulo) {
                var valorCelda = e.target.textContent; 
                document.getElementById('tournamentName').value = valorCelda; 
            }
        }
    });
});

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
};

function Tournament_Finished(data) {
	var winnerElement = document.getElementById('winner');
    winnerElement.textContent = "The winner is " + data;
}

function Start_Game(data) {
    var iframe = document.getElementById('iframegame');
    iframe.src = data.name;
}

function Refresh_Tournament_Status(data) {
    let statusElement = document.querySelector('#tstatus');
    statusElement.textContent = "Tournament status";
    let table = document.querySelector('#tstatusTable');
    table.style.display = 'table'; 
    let userList = data["REFRESH_TURNAMENT_STATUS"];
    for (let user of userList) {
        let row = document.getElementById(user.fields.email);
        if (!row) {
            row = document.createElement('tr');
            row.id = user.fields.email;
            let displayNameCell = document.createElement('td');
            displayNameCell.textContent = user.fields.display_name;
            row.appendChild(displayNameCell);
            let statusCell = document.createElement('td');
            statusCell.textContent = user.fields.status;
            row.appendChild(statusCell);
            table.appendChild(row);
        } else {
            row.cells[0].textContent = user.fields.display_name;
            row.cells[1].textContent = user.fields.status;
        }
    }
}

function Set_Button_Play_Status(data) {
	let playButton = document.querySelector('#play');
	playButton.disabled = data.status;
	playButton.textContent = data.text;
	if (data.text == 'Waiting for players') {
		var table = document.getElementById('tstatus');
		table.innerHTML = ""; 
		table.setAttribute('disabled', true); 
	}
}

document.querySelector('#play').onclick = function (e) {
    socket.send(JSON.stringify({'PLAY': 'PLAY'}));
};


function Set_Connected_User_List(data) {
    let table = document.getElementById("userTable");
    let existingRows = new Map(Array.from(table.children).map(row => [row.dataset.email, row]));
    let userList = data["SET_CONNECTED_USER_LIST"];
    let playButton = document.querySelector('#play');
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

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create').addEventListener('click', function() {
        var tournamentName = document.getElementById('tournamentName').value;
        if (tournamentName !== '') {
            var urlPattern = /^[a-zA-Z0-9-._~:/?#[\]@!$&'()*+,;=]+$/;
            if (urlPattern.test(tournamentName)) {
                window.location.href = "/tournament/" + tournamentName;
            } else {
                alert('The tournament name contains invalid characters.');
            }
        } else {
            alert('The name of the tournament cannot be empty.');
        }
    });
});