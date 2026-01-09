#!/usr/bin/env python3
"""
Wave Reborn - System Tray Application
Запускает backend сервер и предоставляет иконку в трее для управления
"""
import sys
import os
import subprocess
import webbrowser
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import signal

# Пути
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_DIR, "venv")

class WaveRebornTray:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.backend_process = None

        # Создаем иконку для трея (используем стандартную)
        self.tray_icon = QSystemTrayIcon()

        # Пытаемся установить иконку
        self.setup_icon()

        # Создаем меню
        self.create_menu()

        # Показываем иконку
        self.tray_icon.show()

        # Запускаем backend при старте
        self.start_backend()

        # Обработка сигналов для корректного завершения
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_icon(self):
        """Устанавливает иконку для трея"""
        # Пытаемся загрузить кастомную иконку
        icon_path = os.path.join(PROJECT_DIR, "wave_icon.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Используем стандартную иконку Qt
            icon = self.app.style().standardIcon(self.app.style().SP_MediaPlay)

        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Wave Reborn Audio Mixer")

    def create_menu(self):
        """Создает контекстное меню для иконки трея"""
        menu = QMenu()

        # Открыть интерфейс
        open_action = QAction("🌐 Open Mixer", self.app)
        open_action.triggered.connect(self.open_interface)
        menu.addAction(open_action)

        # Открыть настройки
        settings_action = QAction("⚙️ Settings", self.app)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Перезапустить backend
        restart_action = QAction("🔄 Restart Backend", self.app)
        restart_action.triggered.connect(self.restart_backend)
        menu.addAction(restart_action)

        menu.addSeparator()

        # Статус
        self.status_action = QAction("⚫ Status: Starting...", self.app)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)

        menu.addSeparator()

        # Выход
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # Двойной клик открывает интерфейс
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        """Обработчик клика по иконке трея"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_interface()

    def start_backend(self):
        """Запускает backend сервер"""
        if self.backend_process:
            return

        try:
            uvicorn_path = os.path.join(VENV_DIR, "bin", "uvicorn")

            self.backend_process = subprocess.Popen(
                [uvicorn_path, "backend:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=PROJECT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Обновляем статус через небольшую задержку
            QTimer.singleShot(2000, self.update_status)

            self.tray_icon.showMessage(
                "Wave Reborn",
                "Backend server started on http://127.0.0.1:8000",
                QSystemTrayIcon.Information,
                2000
            )

        except Exception as e:
            self.tray_icon.showMessage(
                "Wave Reborn - Error",
                f"Failed to start backend: {str(e)}",
                QSystemTrayIcon.Critical,
                3000
            )

    def stop_backend(self):
        """Останавливает backend сервер"""
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None
            self.status_action.setText("⚫ Status: Stopped")

    def restart_backend(self):
        """Перезапускает backend сервер"""
        self.stop_backend()
        QTimer.singleShot(1000, self.start_backend)

    def update_status(self):
        """Обновляет статус в меню"""
        if self.backend_process and self.backend_process.poll() is None:
            self.status_action.setText("🟢 Status: Running")
        else:
            self.status_action.setText("🔴 Status: Stopped")

    def open_interface(self):
        """Открывает веб-интерфейс в браузере"""
        webbrowser.open("http://127.0.0.1:8000/")

    def open_settings(self):
        """Открывает страницу настроек в браузере"""
        webbrowser.open("http://127.0.0.1:8000/settings.html")

    def quit_app(self):
        """Завершает приложение"""
        self.stop_backend()
        self.tray_icon.hide()
        self.app.quit()

    def signal_handler(self, signum, frame):
        """Обработчик системных сигналов"""
        self.quit_app()

    def run(self):
        """Запускает приложение"""
        return self.app.exec_()

if __name__ == "__main__":
    tray_app = WaveRebornTray()
    sys.exit(tray_app.run())
