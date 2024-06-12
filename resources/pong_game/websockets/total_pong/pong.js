const canvas = document.getElementById('canvas');
canvas.style.display = 'block';
canvas.style.margin = '0 auto';
const ctx = canvas.getContext('2d');
const scale = 1.00;
const keys = {};
let prevKeys= {};
const socket = new WebSocket('ws://localhost:8765');

socket.onmessage = function(event) {
    const position = JSON.parse(event.data);
    canvas.width = position.width * scale;
    canvas.height = position.height * scale;

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the ball
    ctx.beginPath();
    ctx.arc(position.ball_x * scale, position.ball_y * scale, position.ball_radius * scale, 0, 2 * Math.PI, false);
    ctx.fillStyle = 'red';
    ctx.fill();

    // Draw the paddles
    ctx.fillStyle = 'blue';
    ctx.fillRect(position.left_paddle_x * scale, position.left_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);
    ctx.fillRect(position.right_paddle_x * scale, position.right_paddle_y * scale, position.paddle_width * scale, position.paddle_height * scale);

    // Print the scores
    ctx.fillStyle = 'white';
    ctx.font = `${40 * scale}px Arial`;
    ctx.fillText(`${position.score_left}`, canvas.width * 0.25 - 20 * scale, canvas.height / 12);
    ctx.fillText(`${position.score_right}`, canvas.width * 0.75 - 20 * scale, canvas.height / 12);    
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