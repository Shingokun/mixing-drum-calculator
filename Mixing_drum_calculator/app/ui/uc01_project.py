# ============================================================
# uc01_project.py — Quản lý dự án
# ============================================================
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from app.core.session import ProjectSession


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

        # ── Tiêu đề ──────────────────────────────────
        title = QLabel("Hệ thống Dẫn động Thùng trộn")
        title.setProperty("type", "title")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        sub = QLabel("Ứng dụng hỗ trợ tính toán thiết kế chi tiết máy · CO3111")
        sub.setProperty("type", "subtitle")
        sub.setAlignment(Qt.AlignCenter)
        root.addWidget(sub)

        root.addSpacing(30)

        # ── Đường kẻ ──────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        root.addWidget(line)
        root.addSpacing(40)

        # ── 3 Card hành động ──────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)

        cards_row.addWidget(self._make_card(
            "＋", "Dự án Mới",
            "Tạo phiên tính toán mới từ đầu.",
            self._new_project, "accent"
        ))
        cards_row.addWidget(self._make_card(
            "📂", "Mở Dự án",
            "Tải lại file dự án đã lưu (.json).",
            self._open_project, "secondary"
        ))
        cards_row.addWidget(self._make_card(
            "💾", "Lưu Dự án",
            "Lưu phiên làm việc hiện tại xuống file.",
            self._save_project, "secondary"
        ))
        root.addLayout(cards_row)
        root.addSpacing(40)

        # ── Thông tin dự án hiện tại ──────────────────
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

        sf_hdr = QLabel("Trạng thái dự án hiện tại")
        sf_hdr.setProperty("type", "section")
        sf_layout.addWidget(sf_hdr)

        self.status_lbl = QLabel("Chưa có dự án nào được mở.")
        self.status_lbl.setStyleSheet("color: #7F8C8D;")
        sf_layout.addWidget(self.status_lbl)

        self.progress_row = QHBoxLayout()
        self.progress_row.setSpacing(8)
        self._step_badges = []
        steps = ["UC02\nNhập liệu", "UC03\nĐộng cơ",
                 "UC04\nBộ đai", "UC05\nHộp giảm tốc"]
        for step in steps:
            badge = QLabel(step)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(90, 56)
            badge.setStyleSheet(self._badge_style(False))
            self._step_badges.append(badge)
            self.progress_row.addWidget(badge)
        self.progress_row.addStretch()
        sf_layout.addLayout(self.progress_row)

        root.addWidget(self.status_frame)
        root.addStretch()

        # ── Thông tin nhóm ────────────────────────────
        team = QLabel(
            "Đồ án môn học Đa ngành CO3111 · Trường ĐH Bách Khoa TP.HCM\n"
            "GV hướng dẫn: Trương Vĩnh Lân"
        )
        team.setStyleSheet("color: #3D5166; font-size: 11px;")
        team.setAlignment(Qt.AlignCenter)
        root.addWidget(team)

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
                self, "Xác nhận",
                "Tạo dự án mới sẽ xóa toàn bộ dữ liệu hiện tại. Tiếp tục?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        self.session.reset()
        self._update_status("Dự án mới đã được tạo.")
        self.mw.on_step_completed(0)

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Mở dự án", "", "Project Files (*.json)"
        )
        if not path:
            return
        try:
            loaded = ProjectSession.load(path)
            # Copy sang session hiện tại
            self.session.__dict__.update(loaded.__dict__)
            self._update_status(f"Đã mở: {os.path.basename(path)}")
            self.mw.refresh_all()
            QMessageBox.information(self, "Thành công", "Đã tải dự án thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"File không hợp lệ:\n{e}")

    def _save_project(self):
        if not self.session.uc02_done:
            QMessageBox.warning(self, "Chưa có dữ liệu",
                                "Chưa có dữ liệu nào để lưu.")
            return
        path = self.session.filepath or ""
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self, "Lưu dự án", "du_an_thung_tron.json",
                "Project Files (*.json)"
            )
        if not path:
            return
        try:
            self.session.save(path)
            self._update_status(f"Đã lưu: {os.path.basename(path)}")
            QMessageBox.information(self, "Đã lưu", f"Dự án đã được lưu tại:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{e}")

    def _update_status(self, msg: str):
        self.status_lbl.setText(msg)

    def refresh(self):
        states = [self.session.uc02_done, self.session.uc03_done,
                  self.session.uc04_done, self.session.uc05_done]
        for badge, done in zip(self._step_badges, states):
            badge.setStyleSheet(self._badge_style(done))
        done_count = sum(states)
        if done_count == 0:
            self.status_lbl.setText("Dự án mới — chưa có bước nào hoàn thành.")
        else:
            self.status_lbl.setText(f"Đã hoàn thành {done_count}/4 bước tính toán.")