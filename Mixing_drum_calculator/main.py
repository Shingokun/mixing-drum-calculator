import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Thiết lập phong cách cơ bản cho ứng dụng
    app.setStyle("Fusion")
    
    # Tạo và hiển thị cửa sổ chính
    window = MainWindow()
    window.show()
    
    # Bắt đầu vòng lặp sự kiện
    sys.exit(app.exec())

if __name__ == "__main__":
    main()