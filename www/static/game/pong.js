const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const scale = 1.00;
const onePlayer = document.getElementById('playBtn1');
const twoPlayers = document.getElementById('playBtn2');
const textSize = 50;
let countdown = 5;
let keys = {}, prevKeys = {};
let messageNumber = 0;
let players = 0;

let countdownSound = new Audio(`/static/game/${countdown}_countdown.mp3`);
const gameName = JSON.parse(document.getElementById('game_name').textContent);
const socket = new WebSocket(
	'wss://' + window.location.host + '/ws/game/' + gameName + '/'
);

// ***************************** DRAW FUNCTIONS ********************************

function drawGameboard(position) {
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
    drawText(textSize, `${position.score_left}`, 0, canvas.width * 0.25 - textSize / 2 * scale, canvas.height / 12, 0);
    drawText(textSize, `${position.score_right}`, 0, canvas.width * 0.75 - textSize / 2 * scale, canvas.height / 12, 0);
}

function drawCountdown(position) {
    let countdownInterval = setInterval(() => {
        if (countdown >= 0) {
            drawGameboard(position);
            countdownSound.play();
            if (countdown > 0)
                drawText(textSize, `${countdown}`, 1, 0, 0, 3.5);
            else
                drawText(textSize, "Go!!", 1, 0, 0, 3.5);
            drawText(textSize / 3, "Key W: Up", 0, canvas.width / 100, canvas.height * 0.95, 0);
            drawText(textSize / 3, "Key S: Down", 0, canvas.width / 100, canvas.height * 0.98, 0);
            if (players == 2) {
                drawText(textSize / 3, "Key \u2191: Up", 0, canvas.width * 0.91, canvas.height * 0.95, 0);
                drawText(textSize / 3, "Key \u2193: Down", 0, canvas.width * 0.91, canvas.height * 0.98, 0);
            }
            countdown--;
        } else {
            clearInterval(countdownInterval);
            keys['Digit0'] = true;
        }
    }, 1000);
    messageNumber++;
}

function drawText(size, text, center, x, y, height) {    
    ctx.beginPath();
    ctx.fillStyle = 'white';
    ctx.font = `${size * scale}px Courier`;
    let textWidth = ctx.measureText(text).width;
    if (center == 1)
        ctx.fillText(text, (canvas.width - textWidth) / 2, canvas.height / height);
    else
        ctx.fillText(text, x, y);
}

// **************************** EVENT LISTENERS ********************************

// Listen messages from server
socket.onmessage = function(event) {
    let position = JSON.parse(event.data);
    if (messageNumber == 0) {
        canvas.style.display = 'block';
        onePlayer.style.display = 'inline';
        twoPlayers.style.display = 'inline';
        canvas.width = position.width * scale;
        canvas.height = position.height * scale;
        drawGameboard(position);
        drawText(textSize, "Select game mode", 1, 0, 0, 3.5);
        drawText(textSize, "Press 1 for Player vs CPU", 1, 0, 0, 1.4);
        drawText(textSize, "Press 2 for Player vs Player", 1, 0, 0, 1.25);
        messageNumber++;
    }
    else if (messageNumber == 1)
        drawCountdown(position);
    else
        drawGameboard(position);
    if (position.winner && position.score_left > position.score_right)
        drawText(textSize, "Left player wins!!", 1, 0, 0, 3.5);
    else if (position.winner && position.score_left < position.score_right)
        drawText(textSize, "Right player wins!!", 1, 0, 0, 3.5);
};

// Listen for keydown events and mark the key pressed as pressed :)
window.addEventListener('keydown', function(event) {
    keys[event.code] = true;
    if ((event.code) == 'Digit1' && players == 0)
        players = 1;
    if ((event.code) == 'Digit2' && players == 0)
        players = 2;
});

// Listen for keyup events and mark the key released as released :)
window.addEventListener('keyup', function(event) {
    keys[event.code] = false;
});

onePlayer.addEventListener("click", function() {
    keys['Digit1'] = true;
    if (players == 0)
        players = 1;
});

twoPlayers.addEventListener("click", function() {
    keys['Digit2'] = true;
    if (players == 0)
        players = 2;
});

// ******************************* MAIN LOOP ***********************************

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