const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/friends/'
);


//when socket reveives a message, decode the command and run the appropriate function
socket.onmessage = function (e) {
	//parse the data
	const data = JSON.parse(e.data);
	//To deleted, show the data in the console
	console.log(data);
	//check the command and run the appropriate function
	//if the command is "User", display the user's displayname
	if (data.hasOwnProperty("SET_USERNAME")) 
		Set_Username(data);
	//if the command is "list_users", display the list of users
	else if (data.hasOwnProperty("SET_USER_LIST"))
		Set_User_List(data);
	//if the command is "list_connected_users", display the list of connected users
	else if (data.hasOwnProperty("SET_CONNECTED_USERS"))
		Set_Connected_Users(data);
	//if the command is "list_blocked_users", display the list of blocked users
	else if (data.hasOwnProperty("SET_BLOCKED_USERS"))
		Set_Blocked_Users(data);
	//if the command is "chat_message", display the chat message
	else if (data.hasOwnProperty("NEW_ROOM_MSG"))
		New_Room_msg(data['NEW_ROOM_MSG']);
	//if the command is "chat_history", display the chat history
	else if (data.hasOwnProperty("SET_CHAT_HISTORY"))
		Set_Chat_History(data);
	//if a private message is received, display the private message
	else if (data.hasOwnProperty("NEW_PRIVATE_MSG"))
		New_Private_msg(data['NEW_PRIVATE_MSG']);
	//if a user is typing, display the typing message
	else if (data.hasOwnProperty("TYPING"))
		Typing(data);
};

//function to fill User list
function Set_User_List(data) {
    let select = document.getElementById("userList");
    let options = new Map();
    for (let i = 0; i < select.options.length; i++) {
        let option = select.options[i];
        options.set(option.value, option);
    }
    for (let i = 0; i < data.SET_USER_LIST.length; i++) {
        let user = data.SET_USER_LIST[i];
        let option = document.createElement("option");
        option.value = user.fields.email;
        option.text = user.fields.displayname;
        select.add(option, null);
    }
    for (let option of options.values()) {
        select.removeChild(option);
    }
}

//function to fill connected user list
function Set_Connected_Users(data) {
    let table = document.getElementById("userTable");
	let rows = new Map();

	// Guardar las filas existentes en el mapa
	for (let i = 0; i < table.rows.length; i++) {
		let row = table.rows[i];
		rows.set(row.id, row);
	}

	// Añadir nuevas filas a la tabla
	for (let i = 0; i < data.SET_CONNECTED_USERS.length; i++) {
		let user = data.SET_CONNECTED_USERS[i];
		const row = userTable.insertRow(-1);
		const cell1 = row.insertCell(0);
		const cell2 = row.insertCell(1);
		cell1.textContent = user.fields.displayname;
		const img = document.createElement('img');
		img.src = '/static/friends/images/connected-plug-icon.png';
		img.width = 20;  
		cell2.appendChild(img);
	}


}

/*const users = [
    { name: 'Usuario 1', isConnected: true },
    { name: 'Usuario 2', isConnected: false },
    // ...
];

const userTable = document.getElementById('userTable');
users.forEach(user => {
    const row = userTable.insertRow(-1);
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);
    cell1.textContent = user.name;
    const img = document.createElement('img');
    img.src = user.isConnected ? '/static/friends/images/connected-plug-icon.png' : '/static/friends/images/disconnect-plug-icon.png';
    img.width = 20;  
    cell2.appendChild(img);
});*/