"use strict";

let width;
let height;

let lastMouseX = -1;
let lastMouseY = -1;

let status = "Disconnected";

const padX = 0;
const padY = 30;

const ipAddr = null;

let padCanvas;

function setup() {
    noPulldownRefresh();
    width = windowWidth;
    height = windowHeight;
    createCanvas(width, height - 5);
    padCanvas = createGraphics(width - padX, height - padY);
    padCanvas.clear();
    padCanvas.background(200);
}

function draw() {
    background(220);
    updateTopBarStuff();
    updateCursor();
    image(padCanvas, padX, padY);
}

function updateTopBarStuff() {
    fill(0);
    text("Status: " + status, 10, 20);
}

function updateCursor() {
    stroke(0);
    if (mouseIsPressed) {
        if (lastMouseX != -1 && lastMouseY != -1) {
            padCanvas.line(lastMouseX - padX, lastMouseY - padY,
                           mouseX - padX, mouseY - padY);
        }
        fill(0);
        padCanvas.circle(mouseX - padX, mouseY - padY, 2);
        lastMouseX = mouseX;
        lastMouseY = mouseY;
    }
}

function mouseReleased() {
    lastMouseX = -1;
    lastMouseY = -1;
    padCanvas.clear();
    padCanvas.background(200);
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
