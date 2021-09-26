"use strict";

let width;
let height;

let lastMouseX = -1;
let lastMouseY = -1;

let status = "Not connected";
let startPong;

const padY = 30;

let socket;
let pollingDelay = 100;

let padCanvas;

function setup() {
    noPulldownRefresh();
    noScrolling();
    width = windowWidth;
    height = windowHeight;
    createCanvas(width, height - 5);
    padCanvas = createGraphics(width, height - padY);
    padCanvas.clear();
    padCanvas.background(200);
    socket = io();
    socket.on("connect", () => {
        status = "Connected";
        console.log("Connected as socket ID " + socket.id)
        ping();
    })
    socket.on("our_pong", () => {
        let latency = Date.now() - startPong;
        status = "Connected - latency is " + latency + " ms"
        setTimeout(ping, 1000);
    })
    socket.on("disconnect", () => {
        status = "Disconnected";
        console.log("Disconnected")
    })
    updateCursor();
}

function ping() {
    startPong = Date.now();
    socket.emit("our_ping");
}

function draw() {
    background(220);
    updateTopBarStuff();
    image(padCanvas, 0, padY);
}

function updateTopBarStuff() {
    fill(0, 0, 0);
    text("Status: " + status, 10, 20);
}

function updateCursor() {
    if (socket.connected) {
        stroke(0, 0, 0);
        fill(0, 0, 0);
    } else {
        stroke(255, 0, 0);
        fill(255, 0, 0);
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

function mouseReleased() {
    lastMouseX = -1;
    lastMouseY = -1;
    padCanvas.clear();
    padCanvas.background(200);
    return false;
}

// https://stackoverflow.com/q/2890361/10291933
function noScrolling() {
    document.ontouchstart = (e) => {
        e.preventDefault();
    }
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
            newTouchPoint = event.touches[0].clientY;
            if (newTouchPoint > touchPoint) {
                event.preventDefault();
            }
            touchPoint = newTouchPoint;
        };

        document.addEventListener("touchstart", touchStartHandler, {
            passive: false
        });

        document.addEventListener("touchmove", touchMoveHandler, {
            passive: false
        });

    }
}
