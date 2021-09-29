import logging
import socket
from pathlib import Path

import pyautogui
import socketio
from aiohttp import web

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

ACCEPTING_CONNS = True
ALLOW_SOUND = True
SPEED = 1.0
ALLOW_MOVE = True
ALLOW_CLICK = True

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"
SKETCH_JS_PATH = WEB_APP_PATH / "sketch.js"

routes = web.RouteTableDef()
sio = socketio.AsyncServer(async_mode="aiohttp")

pyautogui.PAUSE = 0


def js_bool(py_bool: bool) -> str:
    return "true" if py_bool else "false"


@routes.get("/")
async def index_html(_) -> web.Response:
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


@routes.get("/{filename}")
async def static_file(request: web.Request) -> web.Response:
    try:
        filename = request.match_info.get("filename")
        logger.debug(f"Request for file {filename}")
    except KeyError:
        return web.Response(status=404)
    if filename == "sketch.js":
        js = SKETCH_JS_PATH.read_text()
        js = js.replace("const allowSounds = true;",
                        f"const allowSounds = {js_bool(ALLOW_SOUND)};")
        js = js.replace("const allowMove = true;",
                        f"const allowMove = {js_bool(ALLOW_MOVE)};")
        js = js.replace("const allowClick = true;",
                        f"const allowClick = {js_bool(ALLOW_CLICK)};")
        return web.Response(text=js, content_type="text/javascript")
    else:
        path = WEB_APP_PATH / filename
        if not path.exists():
            return web.Response(status=404)
        mimetypes = {".js": "text/javascript",
                     ".html": "text/html",
                     ".mp3": "audio/mpeg"}
        mimetype = mimetypes.get(path.suffix, "text/plain")
        try:
            stuff = path.read_text(encoding="utf-8")
            return web.Response(text=stuff, content_type=mimetype)
        except UnicodeDecodeError:
            stuff = path.read_bytes()
            return web.Response(body=stuff, content_type=mimetype)


@sio.event
async def connect(sid: str, environ: dict, auth: dict):
    logger.info(f"Connecting to Socket {sid}")
    logger.debug(f"Request info: {environ}")
    logger.debug(f"Authentication: {auth}")
    if not ACCEPTING_CONNS:
        logger.info("Automatically denied")
        return False
    accept = input(f"A WebPad device (appears to be: {auth['device']}) is "
                   f"trying to connect. Accept? (y/n) ").lower()
    if accept in ("y", "yes"):
        logger.info("WebPad accepted!")
    else:
        logger.info("WebPad denied")
        return False


@sio.on("move_to")
async def move_to(sid: str, data: dict):
    if ALLOW_MOVE:
        pyautogui.moveRel(round(data["delta_x"] * SPEED),
                          round(data["delta_y"] * SPEED))


@sio.on("click")
async def click(sid: str, data: str):
    if ALLOW_CLICK:
        pyautogui.click(button=data)


@sio.event
async def disconnect(sid: str):
    logger.warning(f"Disconnect from Socket {sid}")


logger.debug("Obtaining IP address")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]


app = web.Application()
sio.attach(app)
app.add_routes(routes)

logger.info(f"Starting server at http://{ip}")
web.run_app(app, host="0.0.0.0", port=80)
