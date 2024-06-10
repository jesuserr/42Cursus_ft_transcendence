const gameBoard = document.querySelector("#gameBoard");
const ctx = gameBoard.getContext("2d");
const width = gameBoard.width;
const height = gameBoard.height;
const boardBackground = "black";
const paddleColor = "blue";
const ballColor = "red";
const ballRadius = width / 100;
const paddleWidth = width / 35;
const paddleHeight = height / 5;
const paddleGap = width / 25;

let intervalID;
let ballX = width / 2;
let ballY = height / 2;

let leftPaddle = {
    width: paddleWidth,
    height: paddleHeight,
    x: paddleGap,
    y: (height / 2) - (paddleHeight / 2)
};
let rightPaddle = {
    width: paddleWidth,
    height: paddleHeight,
    x: width - paddleGap - paddleWidth,
    y: (height / 2) - (paddleHeight / 2)
};

window.onload = function gameStart(){
    drawBall(ballX, ballY);    
    nextTick();
};

function nextTick(){
    intervalID = setTimeout(() => {
        clearBoard();
        drawPaddles();
        drawBall(ballX, ballY);
        nextTick();
    }, 10)
};

function clearBoard(){
    ctx.fillStyle = boardBackground;
    ctx.fillRect(0, 0, width, height);
};

function drawPaddles(){
    ctx.fillStyle = paddleColor;
    ctx.fillRect(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height);
    ctx.fillRect(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height);
};

function drawBall(ballX, ballY){
    ctx.fillStyle = ballColor;
    ctx.beginPath();
    ctx.arc(ballX, ballY, ballRadius, 0, 2 * Math.PI);
    ctx.fill();
};
