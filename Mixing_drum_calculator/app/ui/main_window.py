# ============================================================
# main_window.py — Cửa sổ chính (Wizard Form)
# ============================================================
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSizePolicy, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from app.core.session import ProjectSession
from app.ui.style import GLOBAL_STYLE
from app.ui.uc01_project  import UC01ProjectPage
from app.ui.uc02_input    import UC02InputPage
from app.ui.uc03_motor    import UC03MotorPage
from app.ui.uc04_belt     import UC04BeltPage
from app.ui.uc05_gearbox  import UC05GearboxPage
from app.ui.uc06_report   import UC06ReportPage


NAV_ITEMS = [
    ("🏠", "Quản lý Dự án",        "UC01"),
    ("📥", "Nhập Thông số",         "UC02"),
    ("⚙️", "Chọn Động cơ",          "UC03"),
    ("🔄", "Bộ truyền Đai",         "UC04"),
    ("🔩", "Hộp Giảm tốc",          "UC05"),
    ("📊", "Xuất Báo cáo",          "UC06"),
]

# Map UC index → bước prerequisite phải hoàn thành
LOCK_MAP = {
    1: None,           # UC02: cần uc02_done → False → unlock after UC01 new
    2: "uc02_done",
    3: "uc03_done",
    4: "uc04_done",
    5: "uc04_done",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = ProjectSession()
        self.setWindowTitle("Hệ thống Dẫn động Thùng trộn")
        self.setMinimumSize(1180, 720)
        self.resize(1280, 800)
        self.setStyleSheet(GLOBAL_STYLE)
        self._build_ui()

    # ─── Build UI ────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #0A1628;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Logo / brand strip
        brand = QLabel("  ⚙ HTDĐ Thùng trộn ")
        brand.setFixedHeight(60)
        brand.setStyleSheet(
            "background:#071020; color:#2E86DE; font-size:15px;"
            "font-weight:bold; border-bottom:2px solid #263748;"
            "padding-left:16px;"
        )
        sb_layout.addWidget(brand)

        # Nav list
        self.nav = QListWidget()
        self.nav.setFocusPolicy(Qt.NoFocus)
        self.nav.setSpacing(2)
        self._nav_items: list[QListWidgetItem] = []

        for icon, label, code in NAV_ITEMS:
            item = QListWidgetItem(f"  {icon}  {label}")
            item.setSizeHint(QSize(220, 52))
            self.nav.addItem(item)
            self._nav_items.append(item)

        self.nav.currentRowChanged.connect(self._on_nav_changed)
        sb_layout.addWidget(self.nav, 1)

        # Save shortcut at bottom
        self.btn_save_sb = QPushButton("💾  Lưu dự án")
        self.btn_save_sb.setProperty("variant", "secondary")
        self.btn_save_sb.style().unpolish(self.btn_save_sb)
        self.btn_save_sb.style().polish(self.btn_save_sb)
        self.btn_save_sb.setStyleSheet(
            "margin:10px 12px 12px 12px; border-radius:6px;"
        )
        self.btn_save_sb.clicked.connect(self._quick_save)
        sb_layout.addWidget(self.btn_save_sb)

        main_layout.addWidget(sidebar)

        # ── Separator ─────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #263748; background:#263748;")
        sep.setFixedWidth(2)
        main_layout.addWidget(sep)

        # ── Stacked pages ─────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.page_uc01 = UC01ProjectPage(self.session, self)
        self.page_uc02 = UC02InputPage(self.session, self)
        self.page_uc03 = UC03MotorPage(self.session, self)
        self.page_uc04 = UC04BeltPage(self.session, self)
        self.page_uc05 = UC05GearboxPage(self.session, self)
        self.page_uc06 = UC06ReportPage(self.session, self)

        for page in [self.page_uc01, self.page_uc02, self.page_uc03,
                     self.page_uc04, self.page_uc05, self.page_uc06]:
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack, 1)

        # Start at trang đầu
        self.nav.setCurrentRow(0)
        self._update_nav_state()

    # ─── Navigation logic ─────────────────────────────────
    def _on_nav_changed(self, idx: int):
        req_attr = LOCK_MAP.get(idx)
        if req_attr and not getattr(self.session, req_attr, False):
            QMessageBox.warning(
                self, "Chưa hoàn thành",
                "Vui lòng hoàn thành bước trước đó trước khi tiếp tục."
            )
            # Revert selection (avoid recursion with blockSignals)
            self.nav.blockSignals(True)
            self.nav.setCurrentRow(self.stack.currentIndex())
            self.nav.blockSignals(False)
            return
        self.stack.setCurrentIndex(idx)

    def _update_nav_state(self):
        """Dim/enable nav items theo trạng thái session"""
        states = [
            True,                       # UC01 luôn accessible
            True,                       # UC02 luôn accessible
            self.session.uc02_done,
            self.session.uc03_done,
            self.session.uc04_done,
            self.session.uc04_done,
        ]
        for i, (item, enabled) in enumerate(zip(self._nav_items, states)):
            flags = item.flags()
            if enabled:
                item.setFlags(flags | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                item.setFlags(flags & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
            # Visual cue: checkmark on done steps
            icon_map = ["🏠", "📥", "⚙️", "🔄", "🔩", "📊"]
            done_flags = [False, self.session.uc02_done, self.session.uc03_done,
                          self.session.uc04_done, self.session.uc05_done, False]
            prefix = "✓ " if done_flags[i] else "   "
            label = NAV_ITEMS[i][1]
            icon  = NAV_ITEMS[i][0]
            item.setText(f" {prefix}{icon}  {label}")

    # ─── Called by child pages when step is done ──────────
    def on_step_completed(self, step_page_idx: int):
        """
        step_page_idx: index trong stack (0=UC01, 1=UC02, …)
        Sau khi hoàn thành, tự động chuyển sang trang tiếp.
        """
        self._update_nav_state()
        self.page_uc01.refresh()

        next_idx = min(step_page_idx + 1, self.stack.count() - 1)
        # Nếu trang tiếp đã unlock thì chuyển
        req = LOCK_MAP.get(next_idx)
        if req is None or getattr(self.session, req, False):
            self.nav.blockSignals(True)
            self.nav.setCurrentRow(next_idx)
            self.nav.blockSignals(False)
            self.stack.setCurrentIndex(next_idx)

        # Nếu chuyển sang UC06, refresh report
        if next_idx == 5:
            self.page_uc06.refresh()

    def refresh_all(self):
        """Refresh toàn bộ sau khi load file"""
        self._update_nav_state()
        for page in [self.page_uc01, self.page_uc02, self.page_uc03,
                     self.page_uc04, self.page_uc05]:
            if hasattr(page, 'refresh'):
                page.refresh()
        if self.session.uc04_done:
            self.page_uc06.refresh()

    def _quick_save(self):
        """Lưu nhanh (nếu đã có filepath) hoặc mở dialog"""
        if self.session.filepath:
            try:
                self.session.save(self.session.filepath)
                # Flash button color
                self.btn_save_sb.setText("✅ Đã lưu!")
                from PySide6.QtCore import QTimer
                QTimer.singleShot(1500, lambda: self.btn_save_sb.setText("💾  Lưu dự án"))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))
        else:
            self.page_uc01._save_project()

    # ─── Window close ────────────────────────────────────
    def closeEvent(self, event):
        if self.session.uc02_done:
            reply = QMessageBox.question(
                self, "Thoát ứng dụng",
                "Bạn có muốn lưu dự án trước khi thoát không?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.page_uc01._save_project()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()