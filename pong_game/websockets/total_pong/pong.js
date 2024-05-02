const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const socket = new WebSocket('ws://localhost:8765');

socket.onmessage = function(event) {
    const position = JSON.parse(event.data);

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the ball
    ctx.beginPath();
    ctx.arc(position.ball_x, position.ball_y, position.ball_radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = 'red';
    ctx.fill();
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#003300';
    ctx.stroke();

    // Draw the paddles
    ctx.fillStyle = 'blue';
    ctx.fillRect(position.left_paddle_x, position.left_paddle_y, position.paddle_width, position.paddle_height);
    ctx.fillRect(position.right_paddle_x, position.right_paddle_y, position.paddle_width, position.paddle_height);
};