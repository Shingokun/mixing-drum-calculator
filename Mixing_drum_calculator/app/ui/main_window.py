# ============================================================
# main_window.py — Main Window (Wizard Form)
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
from app.ui.i18n import _, tr
from app.ui.uc01_project   import UC01ProjectPage
from app.ui.uc02_input    import UC02InputPage
from app.ui.uc03_motor    import UC03MotorPage
from app.ui.uc04_belt     import UC04BeltPage
from app.ui.uc05_gearbox  import UC05GearboxPage
from app.ui.uc06_report   import UC06ReportPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = ProjectSession()
        self.setWindowTitle(_("app_title"))
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

        # Brand header
        self.brand_lbl = QLabel(_("brand"))
        self.brand_lbl.setFixedHeight(60)
        self.brand_lbl.setStyleSheet(
            "background:#071020; color:#2E86DE; font-size:15px;"
            "font-weight:bold; border-bottom:2px solid #263748;"
            "padding-left:16px;"
        )
        sb_layout.addWidget(self.brand_lbl)

        # Navigation list
        self.nav = QListWidget()
        self.nav.setFocusPolicy(Qt.NoFocus)
        self.nav.setSpacing(2)
        self._nav_items: list[QListWidgetItem] = []
        self._init_nav_items()

        self.nav.currentRowChanged.connect(self._on_nav_changed)
        sb_layout.addWidget(self.nav, 1)

        # Language Toggle button
        self.btn_lang = QPushButton(_("lang_toggle"))
        self.btn_lang.setProperty("variant", "secondary")
        self.btn_lang.style().unpolish(self.btn_lang)
        self.btn_lang.style().polish(self.btn_lang)
        self.btn_lang.setStyleSheet("margin: 4px 12px; border-radius:6px;")
        self.btn_lang.clicked.connect(self._toggle_language)
        sb_layout.addWidget(self.btn_lang)

        # Quick save button
        self.btn_save_sb = QPushButton("💾 " + _("save_project"))
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

        # Initialize navigation
        self.nav.setCurrentRow(0)
        self._update_nav_state()

    def _init_nav_items(self):
        self.nav.clear()
        self._nav_items = []
        nav_data = [
            ("🏠", "nav_uc01"),
            ("📥", "nav_uc02"),
            ("⚙️", "nav_uc03"),
            ("🔄", "nav_uc04"),
            ("🔩", "nav_uc05"),
            ("📊", "nav_uc06"),
        ]
        for icon, key in nav_data:
            item = QListWidgetItem(f"  {icon}  {_(key)}")
            item.setSizeHint(QSize(220, 52))
            self.nav.addItem(item)
            self._nav_items.append(item)

    def _toggle_language(self):
        new_lang = "vi" if tr.get_lang() == "en" else "en"
        tr.set_lang(new_lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(_("app_title"))
        self.brand_lbl.setText(_("brand"))
        self.btn_lang.setText(_("lang_toggle"))
        self.btn_save_sb.setText("💾 " + _("save_project"))
        
        current_row = self.nav.currentRow()
        self._init_nav_items()
        self.nav.setCurrentRow(current_row)
        self._update_nav_state()
        
        # Trigger retranslate on child pages
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if hasattr(page, "retranslate_ui"):
                page.retranslate_ui()

    # ─── Navigation logic ─────────────────────────────────
    def _on_nav_changed(self, idx: int):
        # Map UC index → prerequisite step that must be completed
        lock_map = {
            1: None,
            2: "uc02_done",
            3: "uc03_done",
            4: "uc04_done",
            5: "uc04_done",
        }
        req_attr = lock_map.get(idx)
        if req_attr and not getattr(self.session, req_attr, False):
            QMessageBox.warning(
                self, _("incomplete_step"),
                _("incomplete_msg")
            )
            # Revert selection
            self.nav.blockSignals(True)
            self.nav.setCurrentRow(self.stack.currentIndex())
            self.nav.blockSignals(False)
            return
        self.stack.setCurrentIndex(idx)

    def _update_nav_state(self):
        """Enable/disable nav items based on session state"""
        states = [
            True,                       # UC01 always accessible
            True,                       # UC02 always accessible
            self.session.uc02_done,
            self.session.uc03_done,
            self.session.uc04_done,
            self.session.uc04_done,
        ]
        nav_keys = ["nav_uc01", "nav_uc02", "nav_uc03", "nav_uc04", "nav_uc05", "nav_uc06"]
        nav_icons = ["🏠", "📥", "⚙️", "🔄", "🔩", "📊"]
        
        for i, (item, enabled) in enumerate(zip(self._nav_items, states)):
            flags = item.flags()
            if enabled:
                item.setFlags(flags | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                item.setFlags(flags & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)

            # Status checkmarks
            done_flags = [False, self.session.uc02_done, self.session.uc03_done,
                          self.session.uc04_done, self.session.uc05_done, False]
            prefix = "✓ " if done_flags[i] else "   "
            label = _(nav_keys[i])
            icon  = nav_icons[i]
            item.setText(f" {prefix}{icon}  {label}")

    def on_step_completed(self, step_page_idx: int):
        """Called by child pages when a step is finished"""
        self._update_nav_state()
        self.page_uc01.refresh()

        next_idx = min(step_page_idx + 1, self.stack.count() - 1)
        lock_map = {1: None, 2: "uc02_done", 3: "uc03_done", 4: "uc04_done", 5: "uc04_done"}
        req = lock_map.get(next_idx)
        if req is None or getattr(self.session, req, False):
            self.nav.blockSignals(True)
            self.nav.setCurrentRow(next_idx)
            self.nav.blockSignals(False)
            self.stack.setCurrentIndex(next_idx)

        if next_idx == 5:
            self.page_uc06.refresh()

    def refresh_all(self):
        """Refresh all pages after loading a project file"""
        self._update_nav_state()
        for page in [self.page_uc01, self.page_uc02, self.page_uc03,
                     self.page_uc04, self.page_uc05]:
            if hasattr(page, 'refresh'):
                page.refresh()
        if self.session.uc04_done:
            self.page_uc06.refresh()

    def _quick_save(self):
        """Quick save or open save dialog"""
        if self.session.filepath:
            try:
                self.session.save(self.session.filepath)
                self.btn_save_sb.setText("✅ " + _("saved_success"))
                from PySide6.QtCore import QTimer
                QTimer.singleShot(1500, lambda: self.btn_save_sb.setText("💾 " + _("save_project")))
            except Exception as e:
                QMessageBox.critical(self, _("error"), str(e))
        else:
            self.page_uc01._save_project()

    def closeEvent(self, event):
        if self.session.uc02_done:
            reply = QMessageBox.question(
                self, _("exit_app"),
                _("exit_save_msg"),
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
