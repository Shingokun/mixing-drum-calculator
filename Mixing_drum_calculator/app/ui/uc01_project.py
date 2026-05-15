# ============================================================
# uc01_project.py — Project Management
# ============================================================
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from app.core.session import ProjectSession
from app.ui.i18n import _


class UC01ProjectPage(QWidget):
    session_loaded = Signal()

    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(50, 40, 50, 40)
        root.setSpacing(0)

        # ── Title ──────────────────────────────────
        self.title_lbl = QLabel(_("app_title"))
        self.title_lbl.setProperty("type", "title")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.title_lbl)

        self.sub_lbl = QLabel("Multi-disciplinary Project · HCMUT")
        self.sub_lbl.setProperty("type", "subtitle")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.sub_lbl)

        root.addSpacing(30)

        # ── Separator ──────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        root.addWidget(line)
        root.addSpacing(40)

        # ── 3 Action Cards ──────────────────────────
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(24)
        self._init_cards()
        root.addLayout(self.cards_row)
        root.addSpacing(40)

        # ── Current Project Info ──────────────────
        self.status_frame = QFrame()
        self.status_frame.setObjectName("StatusFrame")
        self.status_frame.setStyleSheet("""
            QFrame#StatusFrame {
                background-color: #162130;
                border: 1px solid #263748;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        sf_layout = QVBoxLayout(self.status_frame)
        sf_layout.setContentsMargins(20, 16, 20, 16)
        sf_layout.setSpacing(8)

        self.sf_hdr = QLabel(_("project_status"))
        self.sf_hdr.setProperty("type", "section")
        sf_layout.addWidget(self.sf_hdr)

        self.status_lbl = QLabel(_("no_project"))
        self.status_lbl.setStyleSheet("color: #7F8C8D;")
        sf_layout.addWidget(self.status_lbl)

        self.progress_row = QHBoxLayout()
        self.progress_row.setSpacing(8)
        self._step_badges = []
        self._init_progress_row()
        sf_layout.addLayout(self.progress_row)

        root.addWidget(self.status_frame)
        root.addStretch()

        # ── Team Info ────────────────────────────
        self.team_lbl = QLabel(_("group_info"))
        self.team_lbl.setStyleSheet("color: #3D5166; font-size: 11px;")
        self.team_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.team_lbl)

    def _init_cards(self):
        # Clear existing cards if any
        while self.cards_row.count():
            child = self.cards_row.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.cards_row.addWidget(self._make_card(
            "＋", _("new_project"),
            "Create a new calculation session.",
            self._new_project, "accent"
        ))
        self.cards_row.addWidget(self._make_card(
            "📂", _("open_project"),
            "Load an existing project (.json).",
            self._open_project, "secondary"
        ))
        self.cards_row.addWidget(self._make_card(
            "💾", _("save_project"),
            "Save the current session to a file.",
            self._save_project, "secondary"
        ))

    def _init_progress_row(self):
        while self.progress_row.count():
            child = self.progress_row.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._step_badges = []
        steps = _("step_badges")
        for step in steps:
            badge = QLabel(step)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(90, 56)
            badge.setStyleSheet(self._badge_style(False))
            self._step_badges.append(badge)
            self.progress_row.addWidget(badge)
        self.progress_row.addStretch()

    def retranslate_ui(self):
        self.title_lbl.setText(_("app_title"))
        self.sf_hdr.setText(_("project_status"))
        self.team_lbl.setText(_("group_info"))
        self._init_cards()
        self._init_progress_row()
        self.refresh()

    def _badge_style(self, done: bool) -> str:
        if done:
            return ("background:#10AC84; color:#fff; border-radius:6px;"
                    "font-size:11px; font-weight:bold;")
        return ("background:#1C2B3A; color:#3D5166; border-radius:6px;"
                "font-size:11px; border: 1px solid #263748;")

    def _make_card(self, icon: str, title: str, desc: str,
                   callback, variant: str) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        ico = QLabel(f"<div style='font-size:36px; text-align:center;'>{icon}</div>")
        ico.setAlignment(Qt.AlignCenter)
        layout.addWidget(ico)

        t = QLabel(title)
        t.setStyleSheet("font-size:16px; font-weight:bold; color:#DFE6ED;")
        t.setAlignment(Qt.AlignCenter)
        layout.addWidget(t)

        d = QLabel(desc)
        d.setStyleSheet("font-size:12px; color:#7F8C8D;")
        d.setAlignment(Qt.AlignCenter)
        d.setWordWrap(True)
        layout.addWidget(d)

        layout.addSpacing(8)

        btn = QPushButton(title)
        btn.setProperty("variant", variant)
        btn.style().unpolish(btn); btn.style().polish(btn)
        btn.clicked.connect(callback)
        layout.addWidget(btn)

        return card

    def _new_project(self):
        if self.session.uc02_done:
            reply = QMessageBox.question(
                self, _("confirm"),
                _("new_project_msg"),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        self.session.reset()
        self.refresh()
        self.mw.on_step_completed(0)

    def _open_project(self):
        path, _filter = QFileDialog.getOpenFileName(
            self, _("open_project"), "", "Project Files (*.json)"
        )
        if not path:
            return
        try:
            loaded = ProjectSession.load(path)
            self.session.__dict__.update(loaded.__dict__)
            self.mw.refresh_all()
            QMessageBox.information(self, _("success"), _("load_success"))
        except Exception as e:
            QMessageBox.critical(self, _("error"), f"{_('invalid_file')}\n{e}")

    def _save_project(self):
        if not self.session.uc02_done:
            QMessageBox.warning(self, _("error"), _("no_data"))
            return
        path = self.session.filepath or ""
        if not path:
            path, _filter = QFileDialog.getSaveFileName(
                self, _("save_project"), "project.json",
                "Project Files (*.json)"
            )
        if not path:
            return
        try:
            self.session.save(path)
            self.refresh()
            QMessageBox.information(self, _("success"), f"{_('saved_success')}\n{path}")
        except Exception as e:
            QMessageBox.critical(self, _("error"), f"Could not save file:\n{e}")

    def refresh(self):
        states = [self.session.uc02_done, self.session.uc03_done,
                  self.session.uc04_done, self.session.uc05_done]
        for badge, done in zip(self._step_badges, states):
            badge.setStyleSheet(self._badge_style(done))

        done_count = sum(states)
        if self.session.filepath:
            fname = os.path.basename(self.session.filepath)
            self.status_lbl.setText(f"{fname} — {_('step_completed', done=done_count)}")
        elif done_count > 0:
            self.status_lbl.setText(_("step_completed", done=done_count))
        else:
            self.status_lbl.setText(_("no_project"))