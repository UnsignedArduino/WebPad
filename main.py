import logging
import socket
from pathlib import Path

import pyautogui
import socketio
from aiohttp import web

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"
SKETCH_JS_PATH = WEB_APP_PATH / "sketch.js"

routes = web.RouteTableDef()
sio = socketio.AsyncServer(async_mode="aiohttp")

pyautogui.PAUSE = 0.025


@routes.get("/")
async def index_html(_) -> web.Response:
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


@routes.get("/{filename}")
async def static_file(request: web.Request) -> web.Response:
    try:
        filename = request.match_info.get("filename")
    except KeyError:
        return web.Response(status=404)
    if filename == "sketch.js":
        js = SKETCH_JS_PATH.read_text()
        return web.Response(text=js, content_type="text/javascript")
    else:
        path = WEB_APP_PATH / filename
        if not path.exists():
            return web.Response(status=404)
        stuff = path.read_text(encoding="utf-8")
        mimetypes = {".js": "text/javascript",
                     ".html": "text/html"}
        mimetype = mimetypes.get(path.suffix, "text/plain")
        return web.Response(text=stuff, content_type=mimetype)


@sio.event
async def connect(sid: str, environ: dict):
    logger.info(f"Connected to Socket {sid}")
    logging.debug(f"Request info: {environ}")


@sio.on("move_to")
async def move_to(sid: str, data: dict):
    pyautogui.moveRel(round(data["delta_x"]), round(data["delta_y"]))


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
