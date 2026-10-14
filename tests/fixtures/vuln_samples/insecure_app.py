# Hardened version of the security-scanner test fixture.
#
# Every route below is unchanged in path and method; only the implementations
# have been rewritten to remove the injection, traversal, weak-crypto and
# deserialization flaws the original fixture demonstrated.
import ast
import hashlib
import ipaddress
import json
import os
import re
import sqlite3
import subprocess

from flask import Flask, abort, jsonify, request, send_file

app = Flask(__name__)
DB = "app.db"

# Directory that /files is allowed to serve from. Resolved once so symlinks in
# the base path itself can't shift the boundary at request time.
FILES_ROOT = os.path.realpath("/srv/files")

MAX_INPUT_LEN = 256
MAX_UPLOAD_BYTES = 64 * 1024


@app.route("/users/search")
def search_users():
    name = request.args.get("name", "")
    if len(name) > MAX_INPUT_LEN:
        abort(400, "name too long")

    conn = sqlite3.connect(DB)
    try:
        # Parameterized: the value is bound by the driver, never spliced into SQL.
        rows = conn.execute(
            "SELECT id, name, email FROM users WHERE name = ?", (name,)
        ).fetchall()
    finally:
        conn.close()

    return jsonify({"users": [list(row) for row in rows]})


@app.route("/users/fingerprint")
def fingerprint():
    value = request.args.get("value", "")
    if len(value) > MAX_INPUT_LEN:
        abort(400, "value too long")

    # SHA-256 instead of MD5. Note this is a fingerprint of a non-secret value;
    # if this ever digests passwords or other secrets it must move to a slow,
    # salted KDF (scrypt/argon2/bcrypt), not a bare cryptographic hash.
    return jsonify({"fingerprint": hashlib.sha256(value.encode("utf-8")).hexdigest()})


# --- safe filter expression evaluation -------------------------------------

# Fields a filter expression is allowed to reference. Anything else is rejected.
FILTER_FIELDS = {
    "status": "active",
    "role": "user",
    "age": 30,
}

_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or,
    ast.UnaryOp, ast.Not,
    ast.Compare,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    ast.Name, ast.Load,
    ast.Constant,
    ast.List, ast.Tuple,
)

_MAX_FILTER_NODES = 50


def _eval_filter(node):
    """Evaluate a pre-validated expression node. No calls, no attributes, no names
    outside FILTER_FIELDS, so there is no path to arbitrary code execution."""
    if isinstance(node, ast.Expression):
        return _eval_filter(node.body)

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        return FILTER_FIELDS[node.id]

    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_filter(elt) for elt in node.elts]

    if isinstance(node, ast.UnaryOp):  # only Not survives validation
        return not _eval_filter(node.operand)

    if isinstance(node, ast.BoolOp):
        values = (_eval_filter(v) for v in node.values)
        if isinstance(node.op, ast.And):
            return all(values)
        return any(values)

    if isinstance(node, ast.Compare):
        left = _eval_filter(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_filter(comparator)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            elif isinstance(op, ast.In):
                ok = left in right
            else:  # ast.NotIn
                ok = left not in right
            if not ok:
                return False
            left = right
        return True

    raise ValueError("unsupported expression")


@app.route("/report/filter")
def report_filter():
    expr = request.args.get("filter", "True")
    if len(expr) > MAX_INPUT_LEN:
        abort(400, "filter too long")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        abort(400, "invalid filter expression")

    nodes = list(ast.walk(tree))
    if len(nodes) > _MAX_FILTER_NODES:
        abort(400, "filter expression too complex")

    for node in nodes:
        if not isinstance(node, _ALLOWED_NODES):
            abort(400, "unsupported syntax in filter expression")
        if isinstance(node, ast.Name) and node.id not in FILTER_FIELDS:
            abort(400, "unknown field in filter expression")

    try:
        result = _eval_filter(tree)
    except (ValueError, TypeError, KeyError):
        abort(400, "invalid filter expression")

    return jsonify({"result": bool(result)})


# --- host validation --------------------------------------------------------

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


def _valid_host(host):
    if not host or len(host) > 253:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(host))


@app.route("/tools/ping")
def ping():
    host = request.args.get("host", "localhost")
    # Strict allowlist: an IP literal or a syntactically valid hostname. This also
    # rules out a leading "-", so the value can't be read as a ping flag.
    if not _valid_host(host):
        abort(400, "invalid host")

    try:
        # Argument list, shell=False: no shell metacharacter interpretation.
        proc = subprocess.run(
            ["ping", "-c", "1", host],
            shell=False,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        abort(504, "ping timed out")

    return jsonify(
        {
            "output": proc.stdout.decode("utf-8", "replace"),
            "exit_code": proc.returncode,
        }
    )


@app.route("/files")
def read_file():
    path = request.args.get("path", "")
    if not path or len(path) > 1024:
        abort(400, "invalid path")
    if os.path.isabs(path) or "\x00" in path:
        abort(400, "invalid path")

    # Resolve the full candidate path, then confirm it is still inside the root.
    # realpath collapses "..", so traversal and symlink escapes both fail here.
    candidate = os.path.realpath(os.path.join(FILES_ROOT, path))
    if candidate != FILES_ROOT and not candidate.startswith(FILES_ROOT + os.sep):
        abort(403, "path outside permitted directory")
    if not os.path.isfile(candidate):
        abort(404, "not found")

    return send_file(candidate)


@app.route("/state/load", methods=["POST"])
def load_state():
    # JSON instead of pickle: pickle.loads on request data is remote code
    # execution by design, and no amount of validation makes it safe.
    raw = request.get_data(cache=False)
    if len(raw) > MAX_UPLOAD_BYTES:
        abort(413, "payload too large")

    try:
        state = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        abort(400, "body must be valid UTF-8 JSON")

    return jsonify({"state": state})


if __name__ == "__main__":
    # Debugger off (the Werkzeug console is RCE for anyone who can reach it) and
    # bound to loopback rather than every interface.
    app.run(host="127.0.0.1", port=5000, debug=False)