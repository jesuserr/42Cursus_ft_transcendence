const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const textSize = 50;
let scale = 1.00;
let scaleFactor = 0.867;
let browserHeight = 0;
let browserWidth = 0;
let countdown = 5;
let keys = {};
let messageNumber = 0;
let prevBallXSpeed = 0;
let muted = false;
let position = 0;

let countdownBeep = new Audio(`/static/game/sounds/beep_countdown.mp3`);
let countdownGo = new Audio(`/static/game/sounds/go_countdown.mp3`);
let pingSound = new Audio(`/static/game/sounds/ping.mp3`);
let pongSound = new Audio(`/static/game/sounds/pong.mp3`);
let pointSound = new Audio(`/static/game/sounds/point.mp3`);
let winSound = new Audio(`/static/game/sounds/win.mp3`);

const gameName = JSON.parse(document.getElementById('game_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/game2/' + gameName + '/');

// ***************************** DRAW FUNCTIONS ********************************

function initGameboard() {
    canvas.style.display = 'block';
    drawGameboard();
    if (position.player == 1) {
        if (messageNumber == 0)
            drawText(textSize, "Waiting for Player 2...", 1, 0, 0, 3.5);
        else if (countdown % 2)
            drawText(textSize, "Get ready!!", 0, canvas.width * 0.15, canvas.height / 3.5, 0);
        drawText(textSize / 3, "Key W: Up", 0, canvas.width / 100, canvas.height * 0.95, 0);
        drawText(textSize / 3, "Key S: Down", 0, canvas.width / 100, canvas.height * 0.98, 0);
    }
    else {
        if (countdown % 2)
            drawText(textSize, "Get ready!!", 0, canvas.width * 0.65, canvas.height / 3.5, 0);
        drawText(textSize / 3, "Key \u2191: Up", 0, canvas.width * 0.91, canvas.height * 0.95, 0);
        drawText(textSize / 3, "Key \u2193: Down", 0, canvas.width * 0.91, canvas.height * 0.98, 0);
    }
    drawText(textSize, "Press M to mute", 1, 0, 0, 1.3); 
}

function drawGameboard() {
    if (window.innerHeight != browserHeight || window.innerWidth != browserWidth)
        determineScale();
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
    // Draw the paddles with gradient
    ctx.beginPath();
    let gradientLeft = ctx.createLinearGradient(position.left_paddle_x * scale, 0, (position.left_paddle_x + position.paddle_width) * scale, 0);
    gradientLeft.addColorStop(0, 'black');
    gradientLeft.addColorStop(1, 'blue');
    ctx.fillStyle = gradientLeft;
    ctx.fillRect(position.left_paddle_x * scale, position.left_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);
    let gradientRight = ctx.createLinearGradient(position.right_paddle_x * scale, 0, (position.right_paddle_x + position.paddle_width) * scale, 0);
    gradientRight.addColorStop(0, 'blue');
    gradientRight.addColorStop(1, 'black');
    ctx.fillStyle = gradientRight;
    ctx.fillRect(position.right_paddle_x * scale, position.right_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);
    // Print the scores
    drawText(textSize, `${position.score_left}`, 0, canvas.width * 0.25 - textSize / 2 * scale, canvas.height / 12, 0);
    drawText(textSize, `${position.score_right}`, 0, canvas.width * 0.75 - textSize / 2 * scale, canvas.height / 12, 0);
    if (muted)
        drawText(textSize / 3, "Muted", 0, canvas.width / 100, canvas.height * 0.02, 0);
}

function determineScale() {
    browserWidth = window.innerWidth;
    browserHeight = window.innerHeight;
    let scaleX = scaleFactor * browserWidth / position.width;
    let scaleY = scaleFactor * browserHeight / position.height;
    scale = Math.min(scaleX, scaleY);
    canvas.width = position.width * scale;
    canvas.height = position.height * scale;
    canvas.style.border = `${scale * 10}px solid white`;
}

function drawCountdown() {    
    if (position.player != 0) {
        let countdownInterval = setInterval(() => {
            if (countdown >= 0 && position.player !=0) {
                initGameboard();
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
                countdown--;
            } else {
                clearInterval(countdownInterval);
                keys['F15'] = true;         // Informs server countdown is over            
                messageNumber++;            // Never come back here
            }
        }, 1000);
    }
    else {
        drawGameboard(position);
        setTimeout(function() {drawWinners()}, 500);
    }
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

function drawWinners() {
    if (!muted)
        winSound.play();
    if (position.score_left > position.score_right)
        drawText(textSize, "Left player wins!!", 1, 0, 0, 3.5);
    else
        drawText(textSize, "Right player wins!!", 1, 0, 0, 3.5);
    if (position.player == 0)
        drawText(textSize, "Opponent disconnected!!", 1, 0, 0, 1.3);
}

// ***************************** SOUND EFFECTS *********************************

function makeNoises() {
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
    position = JSON.parse(event.data);
    if (messageNumber == 0) {
        initGameboard();
        messageNumber++;
    }
    else if (messageNumber == 1)
        drawCountdown();
    else {        
        drawGameboard(position);
        if (!muted)
            makeNoises();
        if (position.winner) {
            if (!muted)
                pointSound.play();            
            setTimeout(function() {drawWinners()}, 500);
        }
    }
}

// Listen for keydown events and mark the key pressed as pressed :)
window.addEventListener('keydown', function(event) {
    keys[event.code] = true;    
    if (event.code == 'KeyM')
        muted = !muted;
});

// Listen for keyup events and mark the key released as released :)
window.addEventListener('keyup', function(event) {
    keys[event.code] = false;
});

// ******************************* MAIN LOOP ***********************************

function animationLoop() {
    if (!position.winner) {
        if (messageNumber > 1)
            socket.send(JSON.stringify(keys));
        requestAnimationFrame(animationLoop);
    }
}

// Start the animation loop
animationLoop();