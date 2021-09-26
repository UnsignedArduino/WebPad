import logging
import socket
from pathlib import Path

import socketio
from aiohttp import web

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"
SKETCH_JS_PATH = WEB_APP_PATH / "sketch.js"

routes = web.RouteTableDef()
sio = socketio.AsyncServer(async_mode="aiohttp")


@routes.get("/")
async def index_html(_) -> web.Response:
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


@routes.get("/{filename}")
async def static_file(request: web.Request) -> web.Response:
    filename = request.match_info.get("filename", "index.html")
    if filename == "sketch.js":
        js = SKETCH_JS_PATH.read_text()
        js = js.replace("const ipAddr = null;",
                        f"const ipAddr = \"{ip}\";")
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
async def connect(sid, environ, auth):
    print("Connect")
    print(sid)
    print(environ)
    print(auth)
    print()


@sio.on("count")
async def count(sid, data):
    print("Count")
    print(sid)
    print(data)
    print()


@sio.event
async def disconnect(sid):
    print("Disconnect")
    print(sid)
    print()


logger.debug("Obtaining IP address")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]


app = web.Application()
sio.attach(app)
app.add_routes(routes)

logger.info(f"Starting server at http://{ip}")
web.run_app(app, host="0.0.0.0", port=80)
