const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/'
);

if (socket.readyState != WebSocket.CLOSED) {
	document.getElementById("status").innerText = "Connected";
	document.getElementById("connection_status").src = "/static/chat/connected.png";
};

 socket.onclose = function (e) {
	document.getElementById("status").innerText = "Disconnected";
	document.getElementById("connection_status").src = "/static/chat/disconnect.png";
 };

 socket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	//esto rellena el select
	for (let i = 0; i < data.list_users.length; i++) {
		const opt = document.createElement("option");
		opt.value = data.list_users[i].pk;
		opt.text = data.list_users[i].fields.displayname;
		document.getElementById("userlist").add(opt, null)
	};


	if (data.hasOwnProperty("User")) {
		document.getElementById("displayname").innerText = data.User;
	};
};

document.querySelector('#chat_all_users').onclick = function (e) {
		socket.send(JSON.stringify({'list_users': 'list_all_users'}));
	};
document.querySelector('#chat_selected_user').onclick = function (e) {
		socket.send(JSON.stringify({'chat_selected_user': ''}));
	};

