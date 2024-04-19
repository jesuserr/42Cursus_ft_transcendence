// board
let board;
let boardWidth = 1200
let boardHeight = 900
let context;

// paddles
let paddleWidth = boardWidth / 35;
let paddleHeight = boardHeight / 5;
let paddleGap = boardWidth / 25;

let paddle1 = {
    x : paddleGap,
    y : boardHeight / 2 - paddleHeight / 2,
    width : paddleWidth,
    height : paddleHeight
}

let paddle2 = {
    x : boardWidth - paddleGap - paddleWidth,
    y : boardHeight / 2 - paddleHeight / 2,
    width : paddleWidth,
    height : paddleHeight
}

window.onload = function() {
    board = document.getElementById("board");
    board.height = boardHeight;
    board.width = boardWidth;
    context = board.getContext("2d");   //used for drawing on the board

    context.fillStyle = "blue";    
    context.fillRect(paddle1.x, paddle1.y, paddle1.width, paddle1.height);
    context.fillRect(paddle2.x, paddle2.y, paddle2.width, paddle2.height);
    
    requestAnimationFrame(update);
}

function update() {
    requestAnimationFrame(update);
    context.clearRect(0,0,board.width, board.height);
    context.fillStyle = "blue";
    context.fillRect(paddle1.x, paddle1.y, paddle1.width, paddle1.height);    
    context.fillRect(paddle2.x, paddle2.y, paddle2.width, paddle2.height);    
}
