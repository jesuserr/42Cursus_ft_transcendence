//Connect the websocket to the server
const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/'
);

// When the socket is open, display the connection status
socket.onopen = function(e) {
	document.getElementById("STATUS").innerText = "Connected";
	document.getElementById("CONNECTION_STATUS").src = "/static/chat/connected.png";
	//send a message to the server to get the user's displayname
	socket.send(JSON.stringify({'GET_USERNAME': 'GET_USERNAME'}));
	//send a message to the server to get the list of users
	socket.send(JSON.stringify({'GET_USER_LIST': 'GET_USER_LIST'}));
	//send a message to the server to get the list of connected users
	socket.send(JSON.stringify({'GET_CONNECTED_USERS': 'GET_CONNECTED_USERS'}));

};
// When the socket is closed, display the connection status
socket.onclose = function (e) {
	document.getElementById("STATUS").innerText = "Disconnected";
	document.getElementById("CONNECTION_STATUS").src = "/static/chat/disconnect.png";
	document.getElementById("DISPLAYNAME").innerText = "";
 };
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
};

//function to fill connected user list
function Set_Connected_Users(data)
{
	document.getElementById("CONNECTEDUSERLIST").length = 0;
	for (let i = 0; i < data.SET_CONNECTED_USERS.length; i++) 
	{
		if (USERID != data.SET_CONNECTED_USERS[i].pk)
		{
			const opt = document.createElement("option");
			opt.value = data.SET_CONNECTED_USERS[i].pk;
			opt.text = data.SET_CONNECTED_USERS[i].fields.displayname;
			document.getElementById("CONNECTEDUSERLIST").add(opt, null)
		};
	};
};

//function to set the user's displayname
function Set_Username(data) {
	USERID = data.USER_ID;
	document.getElementById("DISPLAYNAME").innerText = data.SET_USERNAME;
};

//function to fill User list
function Set_User_List(data)
{
	document.getElementById("USERLIST").length = 0;
	for (let i = 0; i < data.SET_USER_LIST.length; i++) 
	{
		if (USERID != data.SET_USER_LIST[i].pk)
		{
			const opt = document.createElement("option");
			opt.value = data.SET_USER_LIST[i].pk;
			opt.text = data.SET_USER_LIST[i].fields.displayname;
			document.getElementById("USERLIST").add(opt, null)
		}
	};
};



// When the user clicks the send button, send the command to server
document.querySelector('#CHAT_ALL_USERS').onclick = function (e) {
		socket.send(JSON.stringify({'GET_USER_LIST': 'GET_USER_LIST'}));
	};
document.querySelector('#CHAT_SELECTED_USER').onclick = function (e) {
		socket.send(JSON.stringify({'CHAT_SELECTED_USER': ''}));
	};

