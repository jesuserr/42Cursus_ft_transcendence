const tournamentName = JSON.parse(document.getElementById('tournament_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + tournamentName + '/');


socket.onmessage = function (e) {
	const data = JSON.parse(e.data);
	console.log(data);
	if (data.hasOwnProperty("SET_USER_LIST"))
		Set_User_List(data);
	else if (data.hasOwnProperty("SET_CONNECTED_USERS"))
		Set_Connected_Users(data);
	else if (data.hasOwnProperty("SET_FRIENDS_USERS"))
		Set_Friends_Users(data);
};