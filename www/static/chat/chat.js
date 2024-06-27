const roomName = JSON.parse(document.getElementById('room_name').textContent);
//Connect the websocket to the server
const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/' + roomName + '/'
);

currentchat = '';

// When the socket is open, display the connection status
socket.onopen = function(e) {
	//document.getElementById("STATUS").innerText = "Connected";
	//document.getElementById("CONNECTION_STATUS").src = "/static/chat/connected.png";
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
	//document.getElementById("STATUS").innerText = "Disconnected";
	//document.getElementById("CONNECTION_STATUS").src = "/static/chat/disconnect.png";
	//document.getElementById("DISPLAYNAME").innerText = "";
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
	//if a private message is received, display the private message
	else if (data.hasOwnProperty("NEW_PRIVATE_MSG"))
		New_Private_msg(data['NEW_PRIVATE_MSG']);
	//if a user is typing, display the typing message
	else if (data.hasOwnProperty("TYPING"))
		Typing(data);
};

//function to display the typing message
function Typing(data)
{
	if (currentchat == data['TYPING'] || (data['TYPING'] != '' && currentchat == data['WHOEMAIL']))
	{
		document.getElementById('MSG_STATUS_USERS').innerText = data['WHO'] + ' is typing...';
		setTimeout(function() {
			document.getElementById('MSG_STATUS_USERS').innerText = '...';
		}, 500);
	}
}

//function to display the private message
function New_Private_msg(data) {
    if (currentchat == data.emailto || currentchat == data.emailfrom) {
        let chatTextDiv = document.getElementById('CHATTEXT');
        let messageDiv = document.createElement('div');
        messageDiv.textContent = data.displaynamefrom + ': ' + data.message;
        chatTextDiv.appendChild(messageDiv);
        chatTextDiv.scrollTop = chatTextDiv.scrollHeight;
    } else {
        let userListDiv = document.getElementById('CONNECTEDUSERLIST');
        let userDivs = userListDiv.querySelectorAll('div');
        userDivs.forEach(div => {
            if (div.dataset.pk == data.emailfrom) {
                div.style.fontWeight = 'bold';
                div.style.color = 'red';
            }
        });
    }
}

function Set_Chat_History(alldata) {
    let data = alldata['DATA'];
    let chatContainer = document.getElementById('CHATTEXT');
    chatContainer.innerHTML = '';

    if (alldata['SET_CHAT_HISTORY'] == '') {
        for (let i = 0; i < data.length; i++) {
            let messageElement = document.createElement("span");
            messageElement.textContent = data[i].fields.displayname + ': ' + data[i].fields.message;
            chatContainer.appendChild(messageElement);
            chatContainer.appendChild(document.createElement("br"));
        }
    } else {
        for (let i = 0; i < data.length; i++) {
            let messageElement = document.createElement("span");
            messageElement.textContent = data[i].fields.displaynamefrom + ': ' + data[i].fields.message;
            chatContainer.appendChild(messageElement);
            chatContainer.appendChild(document.createElement("br"));
        }
    }
    chatContainer.scrollTop = chatContainer.scrollHeight;
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
function New_Room_msg(data) {
    if (currentchat == '') {
        let chatContainer = document.getElementById('CHATTEXT');
        let messageElement = document.createElement("span");
        messageElement.textContent = data.displayname + ': ' + data.message;
        chatContainer.appendChild(messageElement);
        chatContainer.appendChild(document.createElement("br"));
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
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
function Set_Connected_Users(data) {
    let container = document.getElementById("CONNECTEDUSERLIST");
    container.innerHTML = '';
    for (let i = 0; i < data.SET_CONNECTED_USERS.length; i++) {
        let user = data.SET_CONNECTED_USERS[i];
        if (USERID != user.pk) {
            let userElement = document.createElement("div");
            userElement.textContent = user.fields.displayname;
            userElement.className = "connected-user";
            // Guardar el pk del usuario como un atributo de datos en el div
            userElement.setAttribute('data-pk', user.pk);
            container.appendChild(userElement);
        }
    }
}

//function to set the user's displayname
function Set_Username(data) {
	USERID = data.USER_ID;
	USERDISPLAYNAME = data.SET_USERNAME;
	//document.getElementById("DISPLAYNAME").innerText = data.SET_USERNAME;
};

//function to fill User list
function Set_User_List(data) {
    let container = document.getElementById("USERLIST");
    let usersMap = new Map();
    container.childNodes.forEach(child => {
        if (child.nodeType === Node.ELEMENT_NODE) { 
            usersMap.set(child.getAttribute("data-email"), child);
        }
    });
    data.SET_USER_LIST.forEach(user => {
        if (USERID !== user.fields.email) { 
            if (!usersMap.has(user.fields.email)) { 
                let userDiv = document.createElement("div");
                userDiv.setAttribute("data-email", user.fields.email);
                userDiv.textContent = user.fields.displayname;
                container.appendChild(userDiv);
            } 
            usersMap.delete(user.fields.email); 
        }
    });
    usersMap.forEach((value, key) => {
        container.removeChild(value);
    });
}

//function to fill blocked user list
function Set_Blocked_Users(data) {
    const blockUsersDiv = document.getElementById("BLOCKUSERS");
    // Limpiar el contenido del div
    blockUsersDiv.innerHTML = '';
    // Iterar sobre los usuarios bloqueados y añadirlos al div
    data.SET_BLOCKED_USERS.forEach(user => {
        const userDiv = document.createElement("div");
        userDiv.textContent = user.fields.displayname;
        // Opcional: Asignar el pk como un atributo data-pk
        userDiv.setAttribute("data-pk", user.pk);
        blockUsersDiv.appendChild(userDiv);
    });
}

// Añadir evento click a todos los elementos seleccionables dentro de CONNECTEDUSERLIST
document.addEventListener('DOMContentLoaded', function() {
    // Usar delegación de eventos para manejar clics en elementos div dentro de CONNECTEDUSERLIST
    document.querySelector('#CONNECTEDUSERLIST').addEventListener('click', function(e) {
        // Verificar si el elemento clickeado es un div
        if (e.target.tagName === 'DIV') {
            // Eliminar la clase selected de todos los elementos div
            this.querySelectorAll('div').forEach(el => {
                el.classList.remove('selected');
            });
            // Añadir la clase selected al elemento clickeado
            e.target.classList.add('selected');
        }
    });
});

// Ajustar el código del botón BLOCK_SELECTED_USER para usar el elemento seleccionado
document.querySelector('#BLOCK_SELECTED_USER').onclick = function (e) {
    var selectedUser = document.querySelector('#CONNECTEDUSERLIST .selected');

    if (!selectedUser || selectedUser.dataset.value == '') {
        alert("Please select a user to block, from the list of users");
    } else {
		console.log(selectedUser.dataset.pk);
        socket.send(JSON.stringify({'BLOCK_USER': selectedUser.dataset.pk}));
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
    var selectedUserDiv = userList.querySelector(".selected") || connectedUserList.querySelector(".selected");

    if (!selectedUserDiv) {
        alert("Please select a user to chat with, from the list of users or connected users");
    } else {
        var selectedUserId = selectedUserDiv.dataset.pk;
        var selectedUserDisplayname = selectedUserDiv.textContent;
        currentchat = selectedUserId;
        currentchatdisplayname = selectedUserDisplayname;

        // Resetear la selección visual de los usuarios
        var allUserDivs = userList.querySelectorAll("div");
        allUserDivs.forEach(div => {
            div.classList.remove('selected');
            div.style.fontWeight = 'normal';
            div.style.color = 'white';
        });

        var allConnectedUserDivs = connectedUserList.querySelectorAll("div");
        allConnectedUserDivs.forEach(div => {
            div.classList.remove('selected');
            div.style.fontWeight = 'normal';
            div.style.color = 'white';
        });

        document.getElementById("CURRENTUSER").innerText = selectedUserDisplayname;
        socket.send(JSON.stringify({'GET_CHAT_HISTORY': selectedUserId, 'LENGTH': 100}));
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

// when user is typing, send the command to server
var chatInput = document.getElementById('CHAT_MSG_INPUT');
chatInput.addEventListener('input', function() 
{
	socket.send(JSON.stringify({'TYPING': currentchat}));
});

