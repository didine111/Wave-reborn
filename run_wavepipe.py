import subprocess
import webbrowser
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import config

UVICORN = os.path.join(BASE_DIR, "venv/bin/uvicorn")
BACKEND_PORT = config.get_backend_port()
BACKEND_HOST = config.get_backend_host()

# Check if uvicorn exists
if not os.path.exists(UVICORN):
    print("ERROR: uvicorn not found in venv!", file=sys.stderr)
    print("Please run start.py first to setup the environment.", file=sys.stderr)
    sys.exit(1)

# -------------------
# Запуск backend
# -------------------
backend_proc = subprocess.Popen([UVICORN, "backend:app", "--reload", f"--port={BACKEND_PORT}"], cwd=BASE_DIR)
time.sleep(2)

# -------------------
# Открываем фронтенд
# -------------------
webbrowser.open(f"http://{BACKEND_HOST}:{BACKEND_PORT}/")

try:
    backend_proc.wait()
except KeyboardInterrupt:
    backend_proc.terminate()
    backend_proc.wait()
