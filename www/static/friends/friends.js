const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/friends/'
);

socket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	if (data.hasOwnProperty("SET_USER_LIST"))
		Set_User_List(data);
	else if (data.hasOwnProperty("SET_CONNECTED_USERS"))
		Set_Connected_Users(data);
	else if (data.hasOwnProperty("SET_FRIENDS_USERS"))
		Set_Friends_Users(data);
};

socket.onopen = function(e) {
	socket.send(JSON.stringify({'GET_FRIENDS_USERS': 'GET_FRIENDS_USERS'}));
};

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

document.querySelector('#addFriend').onclick = function (e) {
    var userList = document.getElementById("userList");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to add to friends list, from the list of users");
    } else {
        socket.send(JSON.stringify({'FRIEND_USER': selectedOption.value}));
    }
};

document.querySelector('#removeFriend').onclick = function (e) {
    var userList = document.getElementById("friendsList");
    var selectedOption = userList.options[userList.selectedIndex];

    if (selectedOption == null || selectedOption.value == '') {
        alert("Please select a user to remove, from the list of friends users");
    } else {
        socket.send(JSON.stringify({'UNFRIENDS_USER': selectedOption.value}));
    }
};

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

function Set_Connected_Users(data) {
    let table = document.getElementById("userTable");
    // Borrar todas las filas existentes excepto el encabezado si existe
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }
    // Procesar los usuarios conectados
    data.SET_CONNECTED_USERS.forEach(user => {
        const row = table.insertRow(-1);
        row.id = user.fields.id;
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        cell1.textContent = user.fields.displayname;
        const img = document.createElement('img');
        img.src = '/static/friends/images/connected-plug-icon.png';
        img.width = 20;
        cell2.appendChild(img);
    });
}

document.getElementById('FriendStats').addEventListener('click', function() {
    const friendsList = document.getElementById('friendsList');
    const userList = document.getElementById('userList');
    let selectedEmail = null;
    if (friendsList.value) {
        selectedEmail = friendsList.value;
    } else if (userList.value) {
        selectedEmail = userList.value;
    }
    if (selectedEmail) {
        var formData = new FormData();
        formData.append("email", selectedEmail);
        fetch(`/stats/friendstat`, {
            method: "POST",
            body: formData,
        })
        .then(response => response.text()) 
        .then(html => {
            const content = parent.document.getElementById("content");
            content.innerHTML = html;
            // Ejecutar scripts después de cargar el contenido
            const scripts = content.querySelectorAll("script");
            scripts.forEach((oldScript) => {
                const newScript = document.createElement("script");
                // Si el script tiene un atributo src, copiarlo al nuevo script
                if (oldScript.src) {
                    newScript.src = oldScript.src;
                } else {
                    newScript.text = oldScript.text;
                }
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('Por favor, selecciona un amigo o un usuario.');
    }
});
