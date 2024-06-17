const tournamentName = JSON.parse(document.getElementById('tournament_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/tournament/' + tournamentName + '/');