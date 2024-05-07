const socket = new WebSocket(
	'wss://'
	+ window.location.host
	+ '/ws/chat/'
);

if (socket.readyState !== WebSocket.CLOSED) {
	document.getElementById("status").innerText = "Connected";
	document.getElementById("connection_status").src = "/static/chat/connected.png";
 }