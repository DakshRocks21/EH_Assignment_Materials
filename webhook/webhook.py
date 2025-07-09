#!/usr/bin/env python3
import hmac, hashlib, json, subprocess, sys, shlex
from pathlib import Path
from typing import Dict, Any

from flask import Flask, request, abort

CONFIG_PATH = Path(__file__).with_name("config.json")
CONFIG: Dict[str, Any] = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

SECRET: bytes = CONFIG["secret"].encode()

app = Flask(__name__)


def signature_ok(raw: bytes, header: str | None) -> bool:
    if header is None or not header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)


def run(cmd: str | list[str]) -> None:
    """
    Run a command and raise if non-zero exit status.
    Accepts either a list (no shell) or a single string (shell=True).
    Captures output so GitHub isn’t blocked by long console spew.
    """
    kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if isinstance(cmd, list):
        proc = subprocess.run(cmd, **kwargs, check=True)
    else:
        proc = subprocess.run(cmd, shell=True, **kwargs, check=True)
    if proc.stdout:
        print(proc.stdout.strip())


def restart_windows_service(name: str) -> None:
    """
    Attempt a gentle Restart-Service; fall back to sc stop/start
    for older PowerShell versions.
    """
    try:
        run(["powershell", "-NoProfile", "-Command", f"Restart-Service -Name {shlex.quote(name)} -Force"])
    except subprocess.CalledProcessError:
        # Fallback: sc stop & start (best-effort)
        run(f"sc stop {shlex.quote(name)}")
        run(f"sc start {shlex.quote(name)}")


@app.post("/webhook")
def webhook() -> str:
    raw = request.data
    if not signature_ok(raw, request.headers.get("X-Hub-Signature-256")):
        abort(401, "bad signature")

    payload = request.get_json(force=True, silent=True) or {}
    full_name: str = payload.get("repository", {}).get("full_name", "")
    sha: str = payload.get("after", "")

    project = CONFIG["projects"].get(full_name)
    if not project:
        abort(403, f"repository {full_name!r} not allowed")

    path = Path(project["path"])
    svc = project["service"]

    # 1st-time clone?
    if not path.exists():
        clone_url = payload["repository"]["ssh_url"]
        path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", clone_url, str(path)])

    # fetch & reset
    run(["git", "-C", str(path), "fetch", "--quiet", "origin"])
    run(["git", "-C", str(path), "reset", "--hard", sha])

    # update deps if requirements.txt present
    req = path / "requirements.txt"
    if req.exists():
        run([sys.executable, "-m", "pip", "install", "--quiet", "-r", str(req)])

    # restart the Windows service
    restart_windows_service(svc)

    return "ok\n"


if __name__ == "__main__":
    # waitress works everywhere, unlike gunicorn
    from waitress import serve

    host, port = ("0.0.0.0", 8000) if len(sys.argv) < 3 else (sys.argv[1], int(sys.argv[2]))
    print(f"Listening on http://{host}:{port}")
    serve(app, host=host, port=port)
