//Connect the websocket to the server
const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/'
);

// When the socket is open, display the connection status
if (socket.readyState != WebSocket.CLOSED) {
	document.getElementById("status").innerText = "Connected";
	document.getElementById("connection_status").src = "/static/chat/connected.png";
};
// When the socket is closed, display the connection status
socket.onclose = function (e) {
	document.getElementById("status").innerText = "Disconnected";
	document.getElementById("connection_status").src = "/static/chat/disconnect.png";
 };
//when socket reveives a message, decode the command and run the appropriate function
socket.onmessage = function (e) {
	//parse the data
	const data = JSON.parse(e.data);
	//To deleted, show the data in the console
	console.log(data);
	//check the command and run the appropriate function
	//if the command is "User", display the user's displayname
	if (data.hasOwnProperty("User")) {
		document.getElementById("displayname").innerText = data.User;
	}
	//if the command is "list_users", display the list of users
	else if (data.hasOwnProperty("list_users")) {
		for (let i = 0; i < data.list_users.length; i++) {
			const opt = document.createElement("option");
			opt.value = data.list_users[i].pk;
			opt.text = data.list_users[i].fields.displayname;
			document.getElementById("userlist").add(opt, null)
		};
	};
};

// When the user clicks the send button, send the command to server
document.querySelector('#chat_all_users').onclick = function (e) {
		socket.send(JSON.stringify({'list_users': 'list_all_users'}));
	};
document.querySelector('#chat_selected_user').onclick = function (e) {
		socket.send(JSON.stringify({'chat_selected_user': ''}));
	};

