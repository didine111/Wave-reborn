#!/usr/bin/env python3
"""
Создает простую иконку для системного трея
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt
import sys
import os

def create_icon():
    """Создает иконку Wave Reborn"""
    # Создаем приложение (необходимо для Qt)
    app = QApplication(sys.argv)

    # Создаем pixmap
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    # Рисуем
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Фон (градиент синего)
    gradient_color = QColor(59, 130, 246)  # #3b82f6
    painter.setBrush(gradient_color)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size, size, 12, 12)

    # Буква W
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Arial", 36, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "W")

    painter.end()

    # Сохраняем
    icon_path = os.path.join(os.path.dirname(__file__), "wave_icon.png")
    pixmap.save(icon_path)
    print(f"Icon created: {icon_path}")

    return icon_path

if __name__ == "__main__":
    create_icon()
