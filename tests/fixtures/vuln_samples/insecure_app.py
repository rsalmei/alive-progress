# INTENTIONALLY INSECURE: fixture for security-scanner tests. Do not use in production.
import hashlib
import os
import pickle
import sqlite3
import subprocess

from flask import Flask, request, send_file

app = Flask(__name__)
DB = "app.db"


@app.route("/users/search")
def search_users():
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB)
    # SQL injection: user input concatenated into the query
    rows = conn.execute("SELECT id, name, email FROM users WHERE name = '" + name + "'").fetchall()
    return {"users": rows}


@app.route("/users/fingerprint")
def fingerprint():
    value = request.args.get("value", "")
    # Weak hash
    return {"fingerprint": hashlib.md5(value.encode()).hexdigest()}


@app.route("/report/filter")
def report_filter():
    expr = request.args.get("filter", "True")
    # Code injection
    return {"result": eval(expr)}


@app.route("/tools/ping")
def ping():
    host = request.args.get("host", "localhost")
    # Command injection
    out = subprocess.check_output("ping -c 1 " + host, shell=True)
    return {"output": out.decode()}


@app.route("/files")
def read_file():
    path = request.args.get("path", "")
    # Path traversal
    return send_file(os.path.join("/srv/files", path))


@app.route("/state/load", methods=["POST"])
def load_state():
    # Insecure deserialization
    return {"state": str(pickle.loads(request.data))}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
