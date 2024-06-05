const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/friends/'
);

const users = [
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
});