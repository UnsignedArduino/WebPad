"use strict";

let width;
let height;

let lastMouseX = -1;
let lastMouseY = -1;

let startMouseX;
let startMouseY;
const clickMaxDiff = 5;

let status = "Not connected";

const padY = 30;

let socket;
let pollingDelay = 25;

let padCanvas;
let needToClear = false;

let tapSound;

function preload() {
    tapSound = loadSound("tap.mp3");
}

function setup() {
    noPulldownRefresh();
    userStartAudio();
    width = windowWidth;
    height = windowHeight;
    createCanvas(width, height - 5);
    padCanvas = createGraphics(width, height - padY);
    clearPadCanvas();
    socket = io();
    socket.on("connect", () => {
        status = "Connected";
        console.log("Connected as socket ID " + socket.id)
    })
    socket.on("disconnect", () => {
        status = "Disconnected";
        console.log("Disconnected")
    })
    updateCursor();
}

function draw() {
    background(220);
    updateTopBarStuff();
    image(padCanvas, 0, padY);
}

function updateTopBarStuff() {
    padCanvas.fill(0, 0, 0);
    text("Status: " + status, 10, 20);
}

function updateCursor() {
    if (socket.connected) {
        padCanvas.stroke(0, 0, 0);
        padCanvas.fill(0, 0, 0);
    } else {
        padCanvas.stroke(255, 0, 0);
        padCanvas.fill(255, 0, 0);
    }
    if (mouseIsPressed) {
        let last_x = lastMouseX;
        let last_y = lastMouseY - padY;
        let x = mouseX;
        let y = mouseY - padY;
        if ((last_x == x && last_y == y) ||
            (x > windowWidth || x < 0) ||
            (y > windowHeight || y < padY / 2)) {
            setTimeout(updateCursor, pollingDelay);
            return;
        }
        if (needToClear) {
            clearPadCanvas();
        }
        if (lastMouseX != -1 && lastMouseY != -1) {
            padCanvas.line(last_x, last_y, x, y);
            let delta_x = x - last_x;
            let delta_y = y - last_y;
            socket.volatile.emit(
                "move_to", {"delta_x": delta_x, "delta_y": delta_y}
            )
        }
        padCanvas.circle(x, y, 2);
        lastMouseX = mouseX;
        lastMouseY = mouseY;
    }
    setTimeout(updateCursor, pollingDelay);
}

function leftClick() {
    socket.volatile.emit("click", "left");
    padCanvas.fill(180);
    padCanvas.rect(0, 0, width / 2, height - padY);
    tap();
    needToClear = true;
    setTimeout(clearPadCanvas, 100);
}

function rightClick() {
    socket.volatile.emit("click", "right");
    padCanvas.fill(180);
    padCanvas.rect(width / 2, 0, width / 2, height - padY);
    tap();
    needToClear = true;
    setTimeout(clearPadCanvas, 100);
}

function tap() {
    if (tapSound.isLoaded()) {
        tapSound.play();
    }
}

function clearPadCanvas() {
    padCanvas.clear()
    padCanvas.background(200);
    needToClear = false;
}

function mousePressed() {
    startMouseX = mouseX;
    startMouseY = mouseY;
}

function mouseReleased() {
    updateCursor();
    lastMouseX = -1;
    lastMouseY = -1;
    clearPadCanvas();
    if ((Math.abs(startMouseX - mouseX) <= clickMaxDiff) &&
        (Math.abs(startMouseY - mouseY) <= clickMaxDiff)) {
        if (mouseX <= width / 2) {
            leftClick();
        } else if (mouseX > width / 2) {
            rightClick();
        }
    }
    return false;
}

// https://stackoverflow.com/a/55832568/10291933
function noPulldownRefresh() {
    var touchStartHandler,
        touchMoveHandler,
        touchPoint;
    // Only needed for touch events on chrome.
    if ((window.chrome || navigator.userAgent.match("CriOS"))
        && "ontouchstart" in document.documentElement) {
        touchStartHandler = function() {
            // Only need to handle single-touch cases
            touchPoint = event.touches.length === 1 ? event.touches[0].clientY : null;
        };
        touchMoveHandler = function(event) {
            var newTouchPoint;
            // Only need to handle single-touch cases
            if (event.touches.length !== 1) {
                touchPoint = null;
                return;
            }
            // We only need to defaultPrevent when scrolling up
            // newTouchPoint = event.touches[0].clientY;
            // if (newTouchPoint > touchPoint) {
            //     event.preventDefault();
            // }
            // touchPoint = newTouchPoint;
            event.preventDefault();
        };
        document.addEventListener("touchstart", touchStartHandler, {
            passive: false
        });
        document.addEventListener("touchmove", touchMoveHandler, {
            passive: false
        });
    }
}
