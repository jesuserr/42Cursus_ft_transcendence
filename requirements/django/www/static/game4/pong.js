const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const textSize = 35;
let scale = 1.00;
let scaleFactor = 0.867;
let browserHeight = 0;
let browserWidth = 0;
let countdown = 5;                  // timeout = 10 in gameconsumers4.py
let keys = {};
let messageNumber = 0;
let prevBallXSpeed = 0;
let muted = false;
let position = 0;

let isMiddleButtonDown = false;     // mouseControls.js related
let previousMouseY = 0;             // mouseControls.js related
let previousTouchY = 0;             // touchControls.js related

let countdownBeep = new Audio(`/static/game/sounds/beep_countdown.mp3`);
let countdownGo = new Audio(`/static/game/sounds/go_countdown.mp3`);
let pingSound = new Audio(`/static/game/sounds/ping.mp3`);
let pongSound = new Audio(`/static/game/sounds/pong.mp3`);
let pointSound = new Audio(`/static/game/sounds/point.mp3`);
let winSound = new Audio(`/static/game/sounds/win.mp3`);

var font = new FontFaceObserver('Press Start 2P');

const gameName = JSON.parse(document.getElementById('game_name').textContent);
const socket = new WebSocket('wss://' + window.location.host + '/ws/game4/' + gameName + '/');

// ***************************** DRAW FUNCTIONS ********************************

function drawCountdown() {
    initGameboard();
    let countdownInterval = setInterval(() => {
        if (countdown >= 0) {
            drawGameboard();            
            drawText(textSize, "M to mute / P to pause", 1, 0, 0, 1.3);
            drawText(textSize, "Player 1", 2, 0, 0, 1.06);
            drawText(textSize, "Player 2", 3, 0, 0, 1.06);
            drawText(textSize / 2, "Key W: Up / Key S: Down", 2, 0, 0, 1.02);
            drawText(textSize / 2, "Key O: Up / Key K: Down", 3, 0, 0, 1.02);
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
            keys['F14'] = false;        // Set game state as unpaused
            socket.send(JSON.stringify(keys));
            messageNumber++;            // Never come back here
        }
    }, 1000);
}

function initGameboard() {
    canvas.style.display = 'block';
    drawGameboard();
    drawText(textSize, "Get Ready!!", 1, 0, 0, 3.5);
    drawText(textSize, "M to mute / P to pause", 1, 0, 0, 1.3);
    drawText(textSize, "Player 1", 2, 0, 0, 1.06);
    drawText(textSize, "Player 2", 3, 0, 0, 1.06);
    drawText(textSize / 2, "Key W: Up / Key S: Down", 2, 0, 0, 1.02);
    drawText(textSize / 2, "Key O: Up / Key K: Down", 3, 0, 0, 1.02);
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
    drawText(textSize, "Player 1", 2, 0, 0, 1.06);
    drawText(textSize, "Player 2", 3, 0, 0, 1.06);    
    if (muted)
        drawText(textSize / 3, "Muted", 0, canvas.width / 100, canvas.height * 0.03, 0);
    if (keys['F14'] && messageNumber > 0)
        drawText(textSize / 3, "Paused", 0, canvas.width * 0.94, canvas.height * 0.03, 0);
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

function drawText(size, text, center, x, y, height) {    
    ctx.beginPath();
    ctx.fillStyle = 'white';
    ctx.font = `${size * scale}px 'Press Start 2P'`;
    let textWidth = ctx.measureText(text).width;
    if (center == 1)
        ctx.fillText(text, (canvas.width - textWidth) / 2, canvas.height / height);
    else if (center == 2)
        ctx.fillText(text, ((canvas.width / 2) - textWidth) / 2, canvas.height / height);
    else if (center == 3)
        ctx.fillText(text, (canvas.width / 2) + ((canvas.width / 2) - textWidth) / 2, canvas.height / height);
    else
        ctx.fillText(text, x, y);
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
    if (messageNumber == 0)
        drawCountdown();
    else {
        drawGameboard(position);
        if (!muted)
            makeNoises();
        if (position.winner) {
            if (!muted)
                pointSound.play();
            setTimeout(function() {
                if (!muted)
                    winSound.play();
                if (position.score_left > position.score_right)
                    drawText(textSize, "Player 1 wins!!", 1, 0, 0, 3.5);
                else
                    drawText(textSize, "Player 2 wins!!", 1, 0, 0, 3.5);
            }, 500);
        }
    }
}

// Listen for keydown events and mark the key pressed as pressed :)
window.addEventListener('keydown', function(event) {
    keys[event.code] = true;
    if (event.code == 'KeyM')
        muted = !muted;
    if (event.code == 'KeyP')
        keys['F14'] = !keys['F14'];
});

// Listen for keyup events and mark the key released as released :)
window.addEventListener('keyup', function(event) {
    keys[event.code] = false;
});

// ******************************* MAIN LOOP ***********************************

function animationLoop() {
    if (!position.winner) {
        if (messageNumber > 0)
            socket.send(JSON.stringify(keys));
        requestAnimationFrame(animationLoop);
    }
}

// Start the animation loop when the font is loaded
font.load().then(function () {    
    animationLoop();
  }).catch(function () {    
    console.log('Font is not available');
    animationLoop();
  });

// ****************************** PLAY AGAIN ***********************************

// When socket is closed, draw button to play again
socket.onclose = function(event) {
    setTimeout(function() {
        drawPlayAgainButton();
    }, 2000);
};

function drawPlayAgainButton() {
    ctx.clearRect(canvas.width / 3, canvas.height / 1.45, canvas.width / 3, canvas.height / 9);
    ctx.beginPath();
    ctx.setLineDash([]);
    ctx.lineWidth = scale * 6;
    ctx.strokeStyle = 'white';
    ctx.rect(canvas.width / 3, canvas.height / 1.45, canvas.width / 3, canvas.height / 9);
    ctx.stroke();
    drawText(textSize, "Play again", 1, 0, 0, 1.3);
    canvas.addEventListener('click', function(event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left - ctx.lineWidth * 2;
        const y = event.clientY - rect.top - ctx.lineWidth * 2;
        if (isClickInsideButton(x, y))
            window.location.reload();
    });
    window.addEventListener('keydown', function(event) {
        if (event.code === 'Space' || event.code === 'Enter' || event.code === 'KeyY')
            window.location.reload();
    });
    window.addEventListener('touchstart', function(event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.touches[0].clientX - rect.left - ctx.lineWidth * 2;
        const y = event.touches[0].clientY - rect.top - ctx.lineWidth * 2;
        if (isClickInsideButton(x, y))
            window.location.reload();
    });
}

function isClickInsideButton(x, y) {
    return x > canvas.width / 3 && y > canvas.height / 1.45 && x < canvas.width / 1.5 && y < canvas.height * 0.8;
}