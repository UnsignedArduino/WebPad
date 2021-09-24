from bottle import Bottle, run

app = Bottle()


@app.route("/")
def index() -> str:
    return ""


run(app, host="localhost", port=8080, debug=True)
