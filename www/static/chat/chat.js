//Connect the websocket to the server
const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/'
);

currentchat = '';

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
	//send a message to the server to get the list of blocked users
	socket.send(JSON.stringify({'GET_BLOCKED_USERS': 'GET_BLOCKED_USERS'}));
	//send a message to the server to get the history of the chat room
	socket.send(JSON.stringify({'GET_CHAT_HISTORY': '', 'LENGTH': 100}));

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
	//if the command is "list_blocked_users", display the list of blocked users
	else if (data.hasOwnProperty("SET_BLOCKED_USERS"))
		Set_Blocked_Users(data);
	//if the command is "chat_message", display the chat message
	else if (data.hasOwnProperty("NEW_ROOM_MSG"))
		New_Room_msg(data['NEW_ROOM_MSG']);
	//if the command is "chat_history", display the chat history
	else if (data.hasOwnProperty("SET_CHAT_HISTORY"))
		Set_Chat_History(data);
};

function Set_Chat_History(alldata)
{
	let data = alldata['DATA']
	if (alldata['SET_CHAT_HISTORY'] == '')
	{
		
		document.getElementById('CHATTEXT').value = '';
		for (let i = 0; i < data.length; i++) 
		{
			document.getElementById('CHATTEXT').value += data[i].fields.displayname + ': ' + data[i].fields.message + '\n';
			document.getElementById('CHATTEXT').scrollTop = document.getElementById('CHATTEXT').scrollHeight;
		}
	}
	else
	{
		document.getElementById('CHATTEXT').value = '';
		for (let i = 0; i < data.length; i++) 
		{
			document.getElementById('CHATTEXT').value += data[i].fields.displaynamefrom + ': ' + data[i].fields.message + '\n';
			document.getElementById('CHATTEXT').scrollTop = document.getElementById('CHATTEXT').scrollHeight;
		}
	}
}

//Press enter to send the chat message
const messageInput = document.getElementById('CHAT_MSG_INPUT');
messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendButton.click();
    }
});

//function to display the room chat message
function New_Room_msg(data)
{
	document.getElementById('CHATTEXT').value += data.displayname + ': ' + data.message + '\n';
	document.getElementById('CHATTEXT').scrollTop = document.getElementById('CHATTEXT').scrollHeight;
}

//Send chat message to the server
const sendButton = document.getElementById('SEND_MSG');
sendButton.addEventListener('click', function() {
	const messageInput = document.getElementById('CHAT_MSG_INPUT');
	const message = messageInput.value;
	if (messageInput.value != '') 
	{
		if (currentchat == '')
		{
			socket.send(JSON.stringify({ 'SEND_MESSAGE_ROOM': message }));
			messageInput.value = '';
		}
		else
		{
			socket.send(JSON.stringify({ 'SEND_PRIVATE_MSG': currentchat, 'DISPLAYNAMETO': currentchatdisplayname , 'MESSAGE': message }));
			messageInput.value = '';
		}
	}
});

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
	USERDISPLAYNAME = data.SET_USERNAME;
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

//function to fill blocked user list
function Set_Blocked_Users(data)
{
	document.getElementById("BLOCKUSERS").length = 0;
	for (let i = 0; i < data.SET_BLOCKED_USERS.length; i++) 
	{
		const opt = document.createElement("option");
		opt.value = data.SET_BLOCKED_USERS[i].pk;
		opt.text = data.SET_BLOCKED_USERS[i].fields.displayname;
		document.getElementById("BLOCKUSERS").add(opt, null)
	};
};

// When the user clicks the block button, send the command to server
document.querySelector('#BLOCK_SELECTED_USER').onclick = function (e) {
    var userList = document.getElementById("USERLIST");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to block, form the list of users");
    } else {
        socket.send(JSON.stringify({'BLOCK_USER': selectedOption.value}));
    }
};

// When the user clicks the unblock button, send the command to server
document.querySelector('#UNBLOCK_SELECTED_USER').onclick = function (e) {
    var userList = document.getElementById("BLOCKUSERS");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to unblock, form the list of blocked users");
    } else {
        socket.send(JSON.stringify({'UNBLOCK_USER': selectedOption.value}));
    }
};


// When the user clicks the send button, send the command to server
document.querySelector('#CHAT_ALL_USERS').onclick = function (e) 
{
	document.getElementById("CURRENTUSER").innerText = 'General';
	currentchat = '';
	socket.send(JSON.stringify({'GET_CHAT_HISTORY': '', 'LENGTH': 100}));
};

//when the user clicks chat with selected user, send the command to server
document.querySelector('#CHAT_SELECTED_USER').onclick = function (e) {
	var userList = document.getElementById("USERLIST");
	var connectedUserList = document.getElementById("CONNECTEDUSERLIST");
	var selectedOptionUserList = userList.options[userList.selectedIndex];
	var selectedOptionConnectedUserList = connectedUserList.options[connectedUserList.selectedIndex];

	if ((selectedOptionUserList == null || selectedOptionUserList.value == '') &&
		(selectedOptionConnectedUserList == null || selectedOptionConnectedUserList.value == '')) {
		alert("Please select a user to chat with, form the list of users or connected users");
	} else {
		var selectedUser = selectedOptionUserList ? selectedOptionUserList.value : selectedOptionConnectedUserList.value;
		var selectedUserDisplayname = selectedOptionUserList ? selectedOptionUserList.text : selectedOptionConnectedUserList.text;
		currentchat = selectedUser;
		currentchatdisplayname = selectedUserDisplayname;
		//put the selected user in normal
		if (selectedOptionConnectedUserList)
			selectedOptionConnectedUserList.style.fontWeight = 'normal';
		if (selectedOptionUserList)
			selectedOptionUserList.style.fontWeight = 'normal';
		document.getElementById("CURRENTUSER").innerText = selectedUserDisplayname;
		socket.send(JSON.stringify({'GET_CHAT_HISTORY': selectedUser, 'LENGTH': 100}));
	}
};

// Unselect the other select elements when one is selected
var selects = document.querySelectorAll('select');
selects.forEach(function(select) {
    select.addEventListener('change', function() {
        selects.forEach(function(otherSelect) {
            if (otherSelect !== select) {
                otherSelect.selectedIndex = -1;
            }
        });
    });
});