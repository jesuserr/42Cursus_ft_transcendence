const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const scale = 1.00;
const onePlayer = document.getElementById('playBtn1');
const twoPlayers = document.getElementById('playBtn2');
const textSize = 50;
let countdown = 3;
let keys = {}, prevKeys = {};
let messageNumber = 0;
let players = 0;
let prevBallXSpeed = 0;
let muted = false;

let countdownBeep = new Audio(`/static/game/sounds/beep_countdown.mp3`);
let countdownGo = new Audio(`/static/game/sounds/go_countdown.mp3`);
let pingSound = new Audio(`/static/game/sounds/ping.mp3`);
let pongSound = new Audio(`/static/game/sounds/pong.mp3`);
let pointSound = new Audio(`/static/game/sounds/point.mp3`);
let winSound = new Audio(`/static/game/sounds/win.mp3`);

const gameName = JSON.parse(document.getElementById('game_name').textContent);
const socket = new WebSocket(
	'wss://' + window.location.host + '/ws/game/' + gameName + '/'
);

// ***************************** DRAW FUNCTIONS ********************************

function initGameboard(position) {
    canvas.style.display = 'block';
    onePlayer.style.display = 'inline';
    twoPlayers.style.display = 'inline';
    canvas.width = position.width * scale;
    canvas.height = position.height * scale;
    drawGameboard(position);
    drawText(textSize, "Select game mode", 1, 0, 0, 3.5);
    drawText(textSize, "Press 1 for Player vs CPU", 1, 0, 0, 1.40);
    drawText(textSize, "Press 2 for Player vs Player", 1, 0, 0, 1.25);
    drawText(textSize, "M to mute / P to pause", 1, 0, 0, 1.13);
    messageNumber++;
}

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
    if (muted)
        drawText(textSize / 3, "Muted", 0, canvas.width / 100, canvas.height * 0.02, 0);
    if (keys['F14'])
        drawText(textSize / 3, "Paused", 0, canvas.width * 0.95, canvas.height * 0.02, 0);
}

function drawCountdown(position) {
    let countdownInterval = setInterval(() => {
        if (countdown >= 0) {
            drawGameboard(position);
            if (countdown > 0) {
                drawText(textSize, `${countdown}`, 1, 0, 0, 3.5);
                if (!muted)
                    countdownBeep.play();
            }
            else {
                drawText(textSize, "Go!!", 1, 0, 0, 3.5);
                if (!muted)
                    countdownGo.play();
            }
            drawText(textSize / 3, "Key W: Up", 0, canvas.width / 100, canvas.height * 0.95, 0);
            drawText(textSize / 3, "Key S: Down", 0, canvas.width / 100, canvas.height * 0.98, 0);
            if (players == 2) {
                drawText(textSize / 3, "Key \u2191: Up", 0, canvas.width * 0.91, canvas.height * 0.95, 0);
                drawText(textSize / 3, "Key \u2193: Down", 0, canvas.width * 0.91, canvas.height * 0.98, 0);
            }
            countdown--;
        } else {
            clearInterval(countdownInterval);
            keys['F15'] = true;         // Informs server countdown is over
            keys['F14'] = false;        // Set game state as unpaused
            messageNumber++;            // Never come back here
        }
    }, 1000);
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

// ***************************** SOUND EFFECTS *********************************

function makeNoises(position) {
    if ((position.ball_x <= position.left_paddle_x || 
    position.ball_x >= position.right_paddle_x + position.paddle_width) &&
    pointSound.paused)
        pointSound.play();
    else if (prevBallXSpeed * position.ball_x_speed < 0) {
        if (position.ball_x > position.width / 2)
            pingSound.play();
        else if (position.ball_x < position.width / 2)
            pongSound.play();
    }        
    prevBallXSpeed = position.ball_x_speed;
}

// **************************** EVENT LISTENERS ********************************

// Listen messages from server
socket.onmessage = function(event) {
    let position = JSON.parse(event.data);
    if (messageNumber == 0)
        initGameboard(position);
    else if (messageNumber == 1)
        drawCountdown(position);
    else {
        if (!muted)
            makeNoises(position);
        drawGameboard(position);                // Where the play is drawn
    }
    if (position.winner) {
        setTimeout(function() {
            if (!muted)
                winSound.play();
            if (position.score_left > position.score_right)
                drawText(textSize, "Left player wins!!", 1, 0, 0, 3.5);
            else
                drawText(textSize, "Right player wins!!", 1, 0, 0, 3.5);
        }, 500);
    }
};

// Listen for keydown events and mark the key pressed as pressed :)
window.addEventListener('keydown', function(event) {
    keys[event.code] = true;
    if ((event.code) == 'Digit1' && players == 0)
        players = 1;
    if ((event.code) == 'Digit2' && players == 0)
        players = 2;
    if (event.code == 'KeyM')
        muted = !muted;
    if (event.code == 'KeyP')
        keys['F14'] = !keys['F14'];
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