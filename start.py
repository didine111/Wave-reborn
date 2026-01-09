#!/usr/bin/env python3
import os
import sys
import subprocess
import webbrowser
import time

# Папка проекта (где лежит backend.py и index.html)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Import configuration
sys.path.insert(0, PROJECT_DIR)
import config

# Порты из конфигурации
BACKEND_PORT = config.get_backend_port()
FRONTEND_PORT = config.get_frontend_port()
BACKEND_HOST = config.get_backend_host()

# 1️⃣ Создаём виртуальное окружение, если его нет
VENV_DIR = os.path.join(PROJECT_DIR, "venv")
if not os.path.exists(VENV_DIR):
    print("Создаём виртуальное окружение...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR])

# 2️⃣ Активируем виртуальное окружение
if os.name == "nt":
    activate_script = os.path.join(VENV_DIR, "Scripts", "activate")
else:
    activate_script = os.path.join(VENV_DIR, "bin", "activate")
    
activate_cmd = f"source {activate_script}"
# используем env переменные для subprocess ниже

# 3️⃣ Устанавливаем зависимости
print("Устанавливаем зависимости...")
subprocess.run([os.path.join(VENV_DIR, "bin", "pip"), "install", "--upgrade", "pip"])
subprocess.run([os.path.join(VENV_DIR, "bin", "pip"), "install", "fastapi", "uvicorn[standard]"])

# 4️⃣ Запускаем backend (который обслуживает и фронтенд)
print("Запускаем backend сервер...")

backend_cmd = [
    os.path.join(VENV_DIR, "bin", "uvicorn"),
    "backend:app",
    "--reload",
    f"--host={BACKEND_HOST}",
    f"--port={BACKEND_PORT}"
]

# запускаем backend в отдельном процессе
backend_proc = subprocess.Popen(backend_cmd, cwd=PROJECT_DIR)

# небольшой таймаут, чтобы backend успел стартовать
time.sleep(2)

# 5️⃣ Открываем браузер с фронтендом (backend обслуживает статические файлы)
webbrowser.open(f"http://127.0.0.1:{BACKEND_PORT}/")

# 6️⃣ Держим скрипт живым, пока работает backend
try:
    backend_proc.wait()
except KeyboardInterrupt:
    print("Закрываем сервер...")
    backend_proc.terminate()
