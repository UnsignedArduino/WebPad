import logging
from pathlib import Path

from bottle import Bottle, run, static_file

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)

WEB_APP_PATH = Path.cwd() / "webapp"
INDEX_HTML_PATH = WEB_APP_PATH / "index.html"

logger.debug(f"Loading files")
index_html = INDEX_HTML_PATH.read_text()

app = Bottle()


@app.route("/")
def index() -> str:
    return index_html


@app.route("/<filepath:path>")
def static(filepath: str) -> str:
    return static_file(filepath, root=str(WEB_APP_PATH))


logger.debug("Starting server")
run(app, host="localhost", port=8080, debug=True)
