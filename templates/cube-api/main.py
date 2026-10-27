from flask import Flask, jsonify

from cube_client import CubeClient

app = Flask(__name__)


@app.route("/health")
def health():
    return "ok"


@app.route("/")
def index():
    rows = CubeClient().load({"measures": ["revenue.revenue"]})
    return jsonify(rows)
