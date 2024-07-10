// Paddle control touching screen, simulates key presses
// Default browser actions like scrolling or refresh are prevented

gameContainer.addEventListener('touchend', function(event) {
    event.preventDefault();
    keys['KeyW'] = false;
    keys['KeyS'] = false;
}, {passive: false});

gameContainer.addEventListener('touchmove', function(event) {
    event.preventDefault();
    const currentTouchY = event.touches[0].clientY;
    if (currentTouchY > previousTouchY) {
            keys['KeyW'] = false;
            keys['KeyS'] = true;
    }
    else if (currentTouchY < previousTouchY) {
            keys['KeyW'] = true;
            keys['KeyS'] = false;
    }
    previousTouchY = currentTouchY;
}, {passive: false});