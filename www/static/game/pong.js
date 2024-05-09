const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const scale = 0.75;
const onePlayer = document.getElementById('playBtn1');
const twoPlayers = document.getElementById('playBtn2');
let keys = {}, prevKeys = {};
let first_message = 0;

const gameName = JSON.parse(document.getElementById('game_name').textContent);
const socket = new WebSocket(
	'wss://' + window.location.host + '/ws/game/' + gameName + '/'
);

onePlayer.addEventListener("click", actionOnePlayer);
twoPlayers.addEventListener("click", actionTwoPlayers);

function actionOnePlayer() {
    console.log ("One player")
}

function actionTwoPlayers() {
    console.log ("Two players")
}

socket.onmessage = function(event) {
    let position = JSON.parse(event.data);
    //console.log(position);    
    if (first_message == 0) {
        canvas.width = position.width * scale;
        canvas.height = position.height * scale;        
        first_message++;
    }
    else {
        // Clear the canvas and draw central dotted line
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.setLineDash([5, 15]);
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.strokeStyle = 'white';
        ctx.stroke();
        // Draw the ball
        ctx.beginPath();
        ctx.arc(position.ball_x * scale, position.ball_y * scale, position.ball_radius * scale, 0, 2 * Math.PI, false);
        ctx.fillStyle = 'red';
        ctx.fill();
        // Draw the paddles
        ctx.beginPath();
        ctx.fillStyle = 'blue';
        ctx.fillRect(position.left_paddle_x * scale, position.left_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);
        ctx.fillRect(position.right_paddle_x * scale, position.right_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);
        // Print the scores
        ctx.beginPath();
        ctx.fillStyle = 'white';
        ctx.font = `${40 * scale}px Arial`;
        ctx.fillText(`${position.score_left}`, canvas.width * 0.25 - 20 * scale, canvas.height / 12);
        ctx.fillText(`${position.score_right}`, canvas.width * 0.75 - 20 * scale, canvas.height / 12);
    }   
};

// Listen for keydown events and mark the key pressed as pressed :)
window.addEventListener('keydown', function(event) {
    keys[event.code] = true;
});

// Listen for keyup events and mark the key released as released :)
window.addEventListener('keyup', function(event) {
    keys[event.code] = false;
});

// Function to send the state of all keys to the server only when there are changes
function sendKeyStates() {
    if (JSON.stringify(keys) !== JSON.stringify(prevKeys)) {
        socket.send(JSON.stringify(keys));
        prevKeys = { ...keys };
    }
    requestAnimationFrame(sendKeyStates);   // v-sync fixed by monitor refresh
}

// Start the animation loop
sendKeyStates();