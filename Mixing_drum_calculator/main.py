#!/usr/bin/env python3
# ============================================================
# main.py — Điểm khởi động ứng dụng
# ============================================================
import sys
import os

# Đảm bảo import đúng từ thư mục gốc
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.ui.main_window import MainWindow


def main():
    # High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Tính toán Hệ thống Dẫn động Thùng trộn")
    app.setOrganizationName("HCMUT - CO3111")

    # Font mặc định
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()