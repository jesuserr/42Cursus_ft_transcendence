// Paddle control touching screen, simulates key presses
// Default browser actions like scrolling or refresh are prevented

gameContainer.addEventListener('touchend', function(event) {
    event.preventDefault();
    if (position.player == 1) {
        keys['KeyW'] = false;
        keys['KeyS'] = false;
    } else {
        keys['KeyO'] = false;
        keys['KeyK'] = false;
    }
}, {passive: false});

gameContainer.addEventListener('touchmove', function(event) {
    event.preventDefault();
    const currentTouchY = event.touches[0].clientY;
    if (currentTouchY > previousTouchY) {
        if (position.player == 1) {
            keys['KeyW'] = false;
            keys['KeyS'] = true;
        } else {
            keys['KeyO'] = false;
            keys['KeyK'] = true;
        }
    }
    else if (currentTouchY < previousTouchY) {
        if (position.player == 1) {
            keys['KeyW'] = true;
            keys['KeyS'] = false;
        } else {
            keys['KeyO'] = true;
            keys['KeyK'] = false;
        }
    }
    previousTouchY = currentTouchY;
}, {passive: false});