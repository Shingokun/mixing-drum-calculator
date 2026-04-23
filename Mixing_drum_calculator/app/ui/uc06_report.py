# ============================================================
# uc06_report.py — Tổng hợp & Xuất báo cáo
# ============================================================
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QFileDialog,
    QMessageBox, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal as QSignal
from app.core.session import ProjectSession
from app.ui.widgets.result_table import ResultTable


class _ExportWorker(QThread):
    done = QSignal(str)
    error = QSignal(str)

    def __init__(self, session, filepath, fmt):
        super().__init__()
        self.session = session
        self.filepath = filepath
        self.fmt = fmt

    def run(self):
        try:
            if self.fmt == "excel":
                from app.export.excel_exporter import export_excel
                export_excel(self.session, self.filepath)
            else:
                from app.export.pdf_exporter import export_pdf
                export_pdf(self.session, self.filepath)
            self.done.emit(self.filepath)
        except Exception as e:
            self.error.emit(str(e))


class UC06ReportPage(QWidget):
    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        hdr = QLabel("Bước 5 · Tổng Hợp & Xuất Báo Cáo")
        hdr.setProperty("type", "title")
        root.addWidget(hdr)
        sub = QLabel("Xem lại toàn bộ kết quả và xuất file thuyết minh Excel hoặc PDF.")
        sub.setProperty("type", "subtitle")
        root.addWidget(sub)
        root.addSpacing(20)

        # ── Bảng tổng hợp ─────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(16)
        cl.setContentsMargins(0, 0, 4, 0)

        # Bảng động học trục
        g_shaft = QGroupBox("⚙️  Bảng động học các trục")
        gsl = QVBoxLayout(g_shaft)
        self.tbl_shaft = ResultTable(
            ["Thông số", "Trục ĐC", "Trục I", "Trục II", "Trục III"]
        )
        self.tbl_shaft.setMaximumHeight(160)
        gsl.addWidget(self.tbl_shaft)
        cl.addWidget(g_shaft)

        # Bảng đai
        g_belt = QGroupBox("🔄  Bộ truyền đai thang")
        gbl = QVBoxLayout(g_belt)
        self.tbl_belt = ResultTable(["Thông số", "Giá trị", "Đơn vị"])
        self.tbl_belt.setMaximumHeight(300)
        gbl.addWidget(self.tbl_belt)
        cl.addWidget(g_belt)

        # Bảng bánh răng
        g_gear = QGroupBox("🔩  Bánh răng côn cấp nhanh")
        ggl = QVBoxLayout(g_gear)
        self.tbl_gear = ResultTable(["Thông số", "Giá trị", "Đơn vị", "Kết quả"])
        self.tbl_gear.setMaximumHeight(500)
        ggl.addWidget(self.tbl_gear)
        cl.addWidget(g_gear)

        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Trạng thái kiểm bền ────────────────────────
        self.lbl_overall = QLabel("")
        self.lbl_overall.setAlignment(Qt.AlignCenter)
        self.lbl_overall.setVisible(False)
        root.addWidget(self.lbl_overall)
        root.addSpacing(16)

        # ── Nút xuất ──────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.btn_refresh = QPushButton("🔄  Cập nhật bảng tổng hợp")
        self.btn_refresh.setProperty("variant", "secondary")
        self.btn_refresh.style().unpolish(self.btn_refresh)
        self.btn_refresh.style().polish(self.btn_refresh)
        self.btn_refresh.clicked.connect(self.refresh)
        btn_row.addWidget(self.btn_refresh)

        btn_row.addStretch()

        self.btn_excel = QPushButton("📊  Xuất Excel (.xlsx)")
        self.btn_excel.setProperty("variant", "success")
        self.btn_excel.style().unpolish(self.btn_excel)
        self.btn_excel.style().polish(self.btn_excel)
        self.btn_excel.clicked.connect(self._export_excel)
        btn_row.addWidget(self.btn_excel)

        self.btn_pdf = QPushButton("📄  Xuất PDF")
        self.btn_pdf.clicked.connect(self._export_pdf)
        btn_row.addWidget(self.btn_pdf)

        root.addLayout(btn_row)
        root.addSpacing(8)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar { background:#1C2B3A; border:none; border-radius:3px; }
            QProgressBar::chunk { background:#2E86DE; border-radius:3px; }
        """)
        root.addWidget(self.progress)

    # ─────────────────────────────────────────────────
    def refresh(self):
        s = self.session
        m = s.motor
        b = s.belt
        c = s.gearbox.cone

        # Bảng trục
        self.tbl_shaft.clear_data()
        self.tbl_shaft.add_row([
            "Công suất (kW)",
            f"{m.shaft_powers.get('dc',0):.4f}",
            f"{m.shaft_powers.get('I',0):.4f}",
            f"{m.shaft_powers.get('II',0):.4f}",
            f"{m.shaft_powers.get('III',0):.4f}",
        ])
        self.tbl_shaft.add_row([
            "Tốc độ (vg/ph)",
            f"{m.shaft_rpms.get('dc',0):.1f}",
            f"{m.shaft_rpms.get('I',0):.2f}",
            f"{m.shaft_rpms.get('II',0):.2f}",
            f"{m.shaft_rpms.get('III',0):.2f}",
        ])
        self.tbl_shaft.add_row([
            "Momen (N·mm)",
            f"{m.shaft_torques.get('dc',0):.2f}",
            f"{m.shaft_torques.get('I',0):.2f}",
            f"{m.shaft_torques.get('II',0):.2f}",
            f"{m.shaft_torques.get('III',0):.2f}",
        ])

        # Bảng đai
        self.tbl_belt.clear_data()
        belt_rows = [
            ("Đường kính bánh đai nhỏ d₁", f"{b.d1_mm:.1f}", "mm"),
            ("Đường kính bánh đai lớn d₂",  f"{b.d2_mm:.1f}", "mm"),
            ("Vận tốc đai v",               f"{b.belt_velocity_ms:.3f}", "m/s"),
            ("Chiều dài đai L",             f"{b.belt_length_mm:.0f}", "mm"),
            ("Khoảng cách trục a",          f"{b.center_distance_mm:.1f}", "mm"),
            ("Góc ôm bánh nhỏ α₁",         f"{b.alpha1_deg:.2f}", "°"),
            ("Số dây đai z",                str(b.num_belts), "dây"),
            ("Lực vòng F_t",               f"{b.Ft_N:.1f}", "N"),
            ("Lực căng F₀",               f"{b.F0_N:.1f}", "N"),
        ]
        for row in belt_rows:
            self.tbl_belt.add_row(list(row))

        # Bảng bánh răng
        self.tbl_gear.clear_data()
        self.tbl_gear.add_section_header("Ứng suất cho phép")
        self.tbl_gear.add_row(["[σ_H]", f"{c.sig_H:.2f}", "MPa", ""])
        self.tbl_gear.add_row(["[σ_F1]", f"{c.sig_F1:.2f}", "MPa", ""])
        self.tbl_gear.add_row(["[σ_F2]", f"{c.sig_F2:.2f}", "MPa", ""])

        self.tbl_gear.add_section_header("Thông số hình học")
        geo_rows = [
            ("Mô đun ngoài m_te",    f"{c.m_te:.2f}",     "mm",   ""),
            ("Số răng z₁ / z₂",      f"{c.z1} / {c.z2}", "",     ""),
            ("Tỉ số truyền u_tt",    f"{c.u_tt:.4f}",     "",     ""),
            ("Sai lệch Δu",          f"{c.delta_u_pct:.2f}", "%",  ""),
            ("R_e côn ngoài",        f"{c.Re_mm:.2f}",    "mm",   ""),
            ("d_e1 vòng chia ngoài", f"{c.de1_mm:.2f}",   "mm",   ""),
            ("Chiều rộng b",         f"{c.b_mm:.2f}",     "mm",   ""),
            ("δ₁ / δ₂",             f"{c.delta1_deg:.3f}° / {c.delta2_deg:.3f}°", "", ""),
        ]
        for row in geo_rows:
            self.tbl_gear.add_row(list(row))

        self.tbl_gear.add_section_header("Kiểm bền")
        ok1 = "ĐẠT" if c.F1_ok else "KHÔNG ĐẠT"
        ok2 = "ĐẠT" if c.F2_ok else "KHÔNG ĐẠT"
        self.tbl_gear.add_row(
            ["σ_F1 thực tế", f"{c.sigma_F1_actual:.2f}", "MPa", ok1], ok_col=3)
        self.tbl_gear.add_row(
            ["σ_F2 thực tế", f"{c.sigma_F2_actual:.2f}", "MPa", ok2], ok_col=3)
        self.tbl_gear.add_row(
            ["Lực vòng F_t / F_r / F_a",
             f"{c.Ft_N:.1f} / {c.Fr_N:.1f} / {c.Fa_N:.1f}", "N", ""])

        # Overall verdict
        ok = s.gearbox.strength_ok
        self.lbl_overall.setVisible(True)
        if ok:
            self.lbl_overall.setText("✓  Toàn bộ kiểm bền ĐẠT — Hệ thống đáp ứng yêu cầu thiết kế")
            self.lbl_overall.setStyleSheet(
                "color:#10AC84; font-weight:bold; font-size:15px;"
                "background:#0D2B1F; border-radius:8px; padding:12px;"
            )
        else:
            self.lbl_overall.setText("✗  Có điều kiện bền KHÔNG ĐẠT — Cần điều chỉnh thông số")
            self.lbl_overall.setStyleSheet(
                "color:#EE5A24; font-weight:bold; font-size:15px;"
                "background:#2B1510; border-radius:8px; padding:12px;"
            )

    def _export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Excel", "Thuyet_minh_thung_tron.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return
        self._run_export(path, "excel")

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu PDF", "Thuyet_minh_thung_tron.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return
        self._run_export(path, "pdf")

    def _run_export(self, path: str, fmt: str):
        self.progress.setVisible(True)
        self.btn_excel.setEnabled(False)
        self.btn_pdf.setEnabled(False)
        self._worker = _ExportWorker(self.session, path, fmt)
        self._worker.done.connect(self._on_export_done)
        self._worker.error.connect(self._on_export_error)
        self._worker.start()

    def _on_export_done(self, path: str):
        self.progress.setVisible(False)
        self.btn_excel.setEnabled(True)
        self.btn_pdf.setEnabled(True)
        QMessageBox.information(
            self, "Xuất thành công",
            f"File đã được lưu tại:\n{path}"
        )

    def _on_export_error(self, msg: str):
        self.progress.setVisible(False)
        self.btn_excel.setEnabled(True)
        self.btn_pdf.setEnabled(True)
        QMessageBox.critical(self, "Lỗi xuất file",
                             f"Không thể tạo file:\n{msg}")
