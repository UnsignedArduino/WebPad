import logging
import socket
from pathlib import Path

from bottle import Bottle, run, static_file

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

WEBPAD_PORT = 2356

CACHE_SKETCH_JS = False

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"
P5_JS_PATH = WEB_APP_PATH / "p5.js"
SKETCH_JS_PATH = WEB_APP_PATH / "sketch.js"

logger.debug(f"Loading files")
index_html = INDEX_HTML_PATH.read_text()
p5_js = P5_JS_PATH.read_text(encoding="utf-8")
sketch_js = SKETCH_JS_PATH.read_text()

app = Bottle()


@app.route("/")
def index() -> str:
    return index_html


@app.route("/p5.js")
def static() -> str:
    return p5_js


@app.route("/sketch.js")
def static() -> str:
    if not CACHE_SKETCH_JS:
        js = SKETCH_JS_PATH.read_text()
    else:
        js = sketch_js
    js = js.replace("const ipAddr = null;",
                    f"const ipAddr = \"{ip}\";")
    js = js.replace("const port = null;",
                    f"const port = {WEBPAD_PORT};")
    return js


logger.debug("Obtaining IP address")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]


logger.info(f"Starting server at http://{ip}")
run(app, host="0.0.0.0", port=80, debug=True)
