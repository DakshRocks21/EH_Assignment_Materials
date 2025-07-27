import hmac
import hashlib
import json
import logging
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

from flask import Flask, request, abort

CONFIG_PATH = Path(__file__).with_name("config.json")
CONFIG: Dict[str, Any] = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

SECRET: bytes = CONFIG["secret"].encode() 
SUPERVISOR_CONF_DIR = Path(CONFIG["supervisor_conf_dir"])

app = Flask(__name__)

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
        logging.info(proc.stdout.strip())

def signature_ok(raw: bytes, header: str | None) -> bool:
    if header is None or not header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)

def supervisor_program_exists(name: str) -> bool:
    """Return True if Supervisor already knows about *name*."""
    try:
        run(["supervisorctl", "status", name])
        return True
    except subprocess.CalledProcessError:
        return False


def write_supervisor_program_conf(program: str, app_dir: Path) -> None:
    """
    Create <conf.d>/<program>.conf pointing to `python app.py` in *app_dir*.
    """
    SUPERVISOR_CONF_DIR.mkdir(parents=True, exist_ok=True)
    conf_path = SUPERVISOR_CONF_DIR / f"{program}.conf"

    python_exe = sys.executable.replace("\\", "/")          # forward-slashes
    app_py = (app_dir / "main.py").as_posix()

    conf = (
        f"[program:{program}]\n"
        f"command={python_exe} {app_py}\n"
        f"directory={app_dir.as_posix()}\n"
        f"autostart=true\n"
        f"autorestart=true\n"
        f"stderr_logfile={app_dir.as_posix()}/stderr.log\n"
        f"stdout_logfile={app_dir.as_posix()}/stdout.log\n"
    )
    conf_path.write_text(conf, encoding="utf-8")
    logging.info("Wrote %s", conf_path)


def supervisor_reload() -> None:
    """Tell Supervisor to pick up new/changed *.conf files."""
    run(["supervisorctl", "reread"])
    run(["supervisorctl", "update"])


def restart_supervisor_program(name: str) -> None:
    run(["supervisorctl", "restart", name])

def bootstrap_all_projects() -> None:
    """
    Ensure every project in config.json is cloned, dependencies installed,
    and its Supervisor program exists and is running.
    """
    for repo_full_name, proj in CONFIG["projects"].items():
        path    = Path(proj["path"])
        program = proj["service"]
        
        # 1 · Clone if missing
        if not path.exists():
            clone_url = f"https://github.com/{repo_full_name}"
            path.parent.mkdir(parents=True, exist_ok=True)
            logging.info("Cloning %s → %s", repo_full_name, path)
            run(["git", "clone", "--depth", "1", clone_url, str(path)])

        # 2 · Install/upgrade deps
        req = path / "requirements.txt"
        print(req)
        if req.exists():
            logging.info("Installing requirements for %s", repo_full_name)
            run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])

        # 3 · Write *.conf the first time
        conf_path = SUPERVISOR_CONF_DIR / f"{program}.conf"
        if not conf_path.exists():
            logging.info("Creating Supervisor program %s", program)
            write_supervisor_program_conf(program, path)
            supervisor_reload()

        # 4 · (Re)start program so the new code is running
        restart_supervisor_program(program)

@app.get("/")
def index() -> str:
    return "Webhook server is running.\n"

@app.post("/webhook")
def webhook() -> str:
    print("got da webhookkk")
    raw = request.data
    if not signature_ok(raw, request.headers.get("X-Hub-Signature-256")):
        abort(401, "bad signature")

    payload = request.get_json(force=True, silent=True) or {}
    full_name: str = payload.get("repository", {}).get("full_name", "")
    sha: str = payload.get("after", "")
    print(full_name)

    project = CONFIG["projects"].get(full_name)
    if not project:
        abort(403, f"repository {full_name!r} not allowed")

    path = Path(project["path"])
    program = project["service"]

    # 1st-time clone? (unlikely—bootstrap did it)
    if not path.exists():
        clone_url = payload["repository"]["ssh_url"]
        path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", clone_url, str(path)])

    # fetch & reset
    run(["git", "-C", str(path), "pull", "--force"])

    print("resetteeed")

    # update deps if requirements.txt present
    req = path / "requirements.txt"
    if req.exists():
        print("requiring")
        run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])
    print("reeeestarrtting")
    # restart the Supervisor program
    restart_supervisor_program(program)

    return "ok\n"


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # First-run bootstrap
    bootstrap_all_projects()

    from waitress import serve
    host, port = ("0.0.0.0", 8000) if len(sys.argv) < 3 else (sys.argv[1], int(sys.argv[2]))
    logging.info("Listening on http://%s:%s", host, port)
    serve(app, host=host, port=port, threads=4)
