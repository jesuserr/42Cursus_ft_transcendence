// Paddle control pressing middle button and moving mouse, simulates key presses

window.addEventListener('mousedown', function(event) {
    if (event.button == 1)
        isMiddleButtonDown = true;
});

window.addEventListener('mouseup', function(event) {
    if (event.button == 1) {
        isMiddleButtonDown = false;
        keys['KeyW'] = false;
        keys['KeyS'] = false;
    }
});

window.addEventListener('mousemove', function(event) {
    if (event.clientY > previousMouseY && isMiddleButtonDown) {
        keys['KeyW'] = false;
        keys['KeyS'] = true;
    }
    else if (event.clientY < previousMouseY && isMiddleButtonDown) {
        keys['KeyW'] = true;
        keys['KeyS'] = false;
    }
    previousMouseY = event.clientY;
});