import logging
import socket
from pathlib import Path

from bottle import Bottle, run, static_file

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"
SKETCH_JS_PATH = WEB_APP_PATH / "sketch.js"

app = Bottle()


@app.route("/")
def index() -> str:
    return INDEX_HTML_PATH.read_text()


@app.route("/<filename>")
def static(filename: str) -> str:
    if filename == "sketch.js":
        js = SKETCH_JS_PATH.read_text()
        js = js.replace("const ipAddr = null;",
                        f"const ipAddr = \"{ip}\";")
        return js
    else:
        return static_file(filename, WEB_APP_PATH)


logger.debug("Obtaining IP address")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]


logger.info(f"Starting server at http://{ip}")
run(app, host="0.0.0.0", port=80, debug=True)
