from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, 
    QStackedWidget, QListWidget, QPushButton,
    QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from app.core.session import ProjectSession

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tính toán Hệ thống Dẫn động Thùng trộn")
        self.setMinimumSize(1200, 750)
        self.session = ProjectSession()
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Sidebar navigation
        self.nav = QListWidget()
        self.nav.setFixedWidth(200)
        steps = ["📁 Quản lý Dự án", "📥 Nhập thông số",
                 "⚙️ Chọn Động cơ",  "🔄 Bộ truyền Đai",
                 "⚙️ Hộp Giảm tốc", "📊 Xuất Báo cáo"]
        self.nav.addItems(steps)
        self.nav.currentRowChanged.connect(self._on_nav)

        # Stacked pages
        self.stack = QStackedWidget()
        # Import và thêm các trang UC
        from app.ui.uc01_project import UC01ProjectPage
        from app.ui.uc02_input import UC02InputPage
        from app.ui.uc03_motor import UC03MotorPage
        from app.ui.uc04_belt import UC04BeltPage
        from app.ui.uc05_gearbox import UC05GearboxPage
        from app.ui.uc06_report import UC06ReportPage

        self.page_uc01 = UC01ProjectPage(self.session, self)
        self.page_uc02 = UC02InputPage(self.session, self)
        self.page_uc03 = UC03MotorPage(self.session, self)
        self.page_uc04 = UC04BeltPage(self.session, self)
        self.page_uc05 = UC05GearboxPage(self.session, self)
        self.page_uc06 = UC06ReportPage(self.session, self)
        
        for page in [self.page_uc01, self.page_uc02, self.page_uc03,
                     self.page_uc04, self.page_uc05, self.page_uc06]:
            self.stack.addWidget(page)

        layout.addWidget(self.nav)
        layout.addWidget(self.stack)
        self._update_nav_lock()

    def _on_nav(self, idx: int):
        """Kiểm tra điều kiện trước khi cho phép chuyển bước"""
        lock_map = {
            2: self.session.uc02_done,
            3: self.session.uc03_done,
            4: self.session.uc04_done,
            5: self.session.uc04_done,
        }
        if idx in lock_map and not lock_map[idx]:
            QMessageBox.warning(self, "Chưa hoàn thành",
                "Vui lòng hoàn thành bước trước!")
            self.nav.setCurrentRow(self.stack.currentIndex())
            return
        self.stack.setCurrentIndex(idx)

    def _update_nav_lock(self):
        """Cập nhật màu sắc sidebar theo trạng thái"""
        states = [True, True, self.session.uc02_done,
                  self.session.uc03_done, self.session.uc04_done,
                  self.session.uc04_done]
        for i, enabled in enumerate(states):
            item = self.nav.item(i)
            item.setFlags(
                item.flags() | Qt.ItemIsEnabled if enabled
                else item.flags() & ~Qt.ItemIsEnabled
            )

    def on_step_completed(self, step: int):
        """Gọi từ các trang con khi hoàn thành"""
        if step == 2: self.session.uc02_done = True
        if step == 3: self.session.uc03_done = True
        if step == 4: self.session.uc04_done = True
        self._update_nav_lock()
        self.stack.setCurrentIndex(step)  # tự động sang bước tiếp