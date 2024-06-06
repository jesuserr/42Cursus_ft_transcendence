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
	if (data.hasOwnProperty("SET_USER_LIST"))
		Set_User_List(data);
	//if the command is "list_connected_users", display the list of connected users
	else if (data.hasOwnProperty("SET_CONNECTED_USERS"))
		Set_Connected_Users(data);
	//if the command is "list_blocked_users", display the list of blocked users
	else if (data.hasOwnProperty("SET_FRIENDS_USERS"))
		Set_Friends_Users(data);
	
};

socket.onopen = function(e) {
	//send a message to the server to get the list of blocked users
	socket.send(JSON.stringify({'GET_FRIENDS_USERS': 'GET_FRIENDS_USERS'}));

};

//function to fill blocked user list
function Set_Friends_Users(data)
{
	document.getElementById("friendsList").length = 0;
	for (let i = 0; i < data.SET_FRIENDS_USERS.length; i++) 
	{
		const opt = document.createElement("option");
		opt.value = data.SET_FRIENDS_USERS[i].pk;
		opt.text = data.SET_FRIENDS_USERS[i].fields.displayname;
		document.getElementById("friendsList").add(opt, null)
	};
};

// When the user clicks the block button, send the command to server
document.querySelector('#addFriend').onclick = function (e) {
    var userList = document.getElementById("userList");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to block, form the list of users");
    } else {
        socket.send(JSON.stringify({'FRIEND_USER': selectedOption.value}));
    }
};

// When the user clicks the unblock button, send the command to server
document.querySelector('#removeFriend').onclick = function (e) {
    var userList = document.getElementById("friendsList");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to unblock, form the list of blocked users");
    } else {
        socket.send(JSON.stringify({'UNFRIENDS_USER': selectedOption.value}));
    }
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