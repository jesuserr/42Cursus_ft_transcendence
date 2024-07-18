// Paddle control pressing middle button and moving mouse, simulates key presses

window.addEventListener('mousedown', function(event) {
    if (event.button == 1)
        isMiddleButtonDown = true;
});

window.addEventListener('mouseup', function(event) {
    if (event.button == 1) {
        isMiddleButtonDown = false;
        if (position.player == 1) {
            keys['KeyW'] = false;
            keys['KeyS'] = false;
        } else {
            keys['KeyO'] = false;
            keys['KeyK'] = false;
        }
    }
});

window.addEventListener('mousemove', function(event) {
    if (event.clientY > previousMouseY && isMiddleButtonDown) {
        if (position.player == 1) {
            keys['KeyW'] = false;
            keys['KeyS'] = true;
        } else {
            keys['KeyO'] = false;
            keys['KeyK'] = true;
        }
    }
    else if (event.clientY < previousMouseY && isMiddleButtonDown) {
        if (position.player == 1) {
            keys['KeyW'] = true;
            keys['KeyS'] = false;
        } else {
            keys['KeyO'] = true;
            keys['KeyK'] = false;
        }
    }
    previousMouseY = event.clientY;
});