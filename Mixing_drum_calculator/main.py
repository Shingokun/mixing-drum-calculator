#!/usr/bin/env python3
# ============================================================
# main.py — Application entry point
# ============================================================
import sys
import os

# Ensure correct imports from the root directory
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from app.ui.main_window import MainWindow


def main():
    # Support for High DPI screens
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Mixing Drum Drive System Calculator")
    app.setOrganizationName("HCMUT - CO3111")

    # Set default application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()

    # Set Window Icon
    icon_path = os.path.join(os.path.dirname(__file__), "app", "ui", "resources", "icon.png")
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()