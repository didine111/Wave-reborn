#!/bin/bash
# Запуск Wave Reborn с системным треем

cd "$(dirname "$0")"

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем приложение с треем
python tray_app.py
