const tournamentName = JSON.parse(document.getElementById('tournament_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + tournamentName + '/');


socket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	console.log(data);
	if (data.hasOwnProperty("SET_CONNECTED_USER_LIST"))
		Set_Connected_User_List(data);

};

function Set_Connected_User_List(data) {
    let table = document.getElementById("userTable");

    let existingRows = new Map(Array.from(table.children).map(row => [row.dataset.email, row]));

    let userList = data["SET_CONNECTED_USER_LIST"];

    for (let user of userList) {
        let email = user.fields.email;

        if (!existingRows.has(email)) {
            let row = document.createElement("tr");
            row.dataset.email = email;  // Almacena el email en un atributo de datos personalizado

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

document.querySelector('#play').onclick = function (e) {
   
    socket.send(JSON.stringify({'PLAY': 'PLAY'}));
   
};