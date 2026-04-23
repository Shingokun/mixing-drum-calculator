# ============================================================
# uc03_motor.py — Chọn động cơ & phân bổ tỉ số truyền
# ============================================================
import json, os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from app.core.session import ProjectSession
from app.core.uc03_calculator import UC03Calculator
from app.ui.widgets.result_table import ResultTable

CATALOG_PATH = os.path.join(os.path.dirname(__file__),
                             "../../app/data/motor_catalog.json")


class UC03MotorPage(QWidget):
    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self.calc = UC03Calculator()
        self.catalog = self._load_catalog()
        self.filtered = []
        self._selected_motor = None
        self._build_ui()

    def _load_catalog(self):
        path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "data", "motor_catalog.json")
        )
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            # Deduplicate on 'id'
            seen = set()
            result = []
            for m in data:
                if m['id'] not in seen:
                    seen.add(m['id'])
                    result.append(m)
            return result
        except Exception:
            return []

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        hdr = QLabel("Bước 2 · Chọn Động Cơ & Phân bổ Tỉ số Truyền")
        hdr.setProperty("type", "title")
        root.addWidget(hdr)
        sub = QLabel("Hệ thống lọc động cơ phù hợp từ CSDL và tính bảng động học trên các trục.")
        sub.setProperty("type", "subtitle")
        root.addWidget(sub)
        root.addSpacing(20)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        # ── Panel trái: Kết quả sơ bộ + Danh sách ────
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 12, 0)
        ll.setSpacing(16)

        # Kết quả sơ bộ
        g_prelim = QGroupBox("📐  Tính toán sơ bộ")
        gpl = QVBoxLayout(g_prelim)
        gpl.setSpacing(8)

        self.lbl_eta    = self._kv_row(gpl, "Hiệu suất toàn hệ thống η")
        self.lbl_pct    = self._kv_row(gpl, "Công suất cần thiết P_ct")
        self.lbl_uch    = self._kv_row(gpl, "Tỉ số truyền chung sơ bộ")
        self.lbl_nsb    = self._kv_row(gpl, "Số vòng quay sơ bộ n_sb")

        self.btn_calc = QPushButton("🔄  Tính toán sơ bộ")
        self.btn_calc.clicked.connect(self._do_prelim)
        gpl.addWidget(self.btn_calc)
        ll.addWidget(g_prelim)

        # Danh sách động cơ
        g_list = QGroupBox("📋  Danh sách động cơ phù hợp (Top gợi ý)")
        gll = QVBoxLayout(g_list)

        self.motor_table = QTableWidget(0, 6)
        self.motor_table.setHorizontalHeaderLabels([
            "Ký hiệu", "P_đc (kW)", "n_đc (vg/ph)",
            "Dư CS (kW)", "Δn (vg/ph)", "Δn%"
        ])
        self.motor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.motor_table.verticalHeader().setVisible(False)
        self.motor_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.motor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.motor_table.setMinimumHeight(220)
        self.motor_table.itemSelectionChanged.connect(self._on_motor_select)
        gll.addWidget(self.motor_table)
        ll.addWidget(g_list, 1)

        splitter.addWidget(left)

        # ── Panel phải: Bảng kết quả trục ─────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.setSpacing(16)

        g_shaft = QGroupBox("📊  Bảng thông số các trục")
        gsl = QVBoxLayout(g_shaft)

        self.shaft_table = ResultTable(
            ["Thông số", "Trục ĐC", "Trục I", "Trục II", "Trục III"]
        )
        self.shaft_table.setMinimumHeight(200)
        gsl.addWidget(self.shaft_table)
        rl.addWidget(g_shaft)

        # Thông tin động cơ đã chọn
        g_sel = QGroupBox("✅  Động cơ đã chọn")
        gsel = QVBoxLayout(g_sel)
        gsel.setSpacing(8)
        self.lbl_motor_name = self._kv_row(gsel, "Ký hiệu động cơ")
        self.lbl_u_h        = self._kv_row(gsel, "Tỉ số truyền HGT u_h")
        self.lbl_u2         = self._kv_row(gsel, "Tỉ số truyền cấp chậm u₂")
        self.lbl_uch_real   = self._kv_row(gsel, "Tỉ số truyền chung thực tế")
        rl.addWidget(g_sel)

        self.btn_confirm = QPushButton("✓  Chốt động cơ & Tiếp theo →")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._confirm)
        rl.addWidget(self.btn_confirm)
        rl.addStretch()

        splitter.addWidget(right)
        splitter.setSizes([480, 520])
        root.addWidget(splitter, 1)

    def _kv_row(self, layout, label: str) -> QLabel:
        row = QHBoxLayout()
        lbl = QLabel(label + ":")
        lbl.setFixedWidth(240)
        lbl.setStyleSheet("color: #7F8C8D;")
        val = QLabel("—")
        val.setStyleSheet("font-weight: bold; color: #54A0FF;")
        row.addWidget(lbl)
        row.addWidget(val)
        row.addStretch()
        layout.addLayout(row)
        return val

    def _do_prelim(self):
        if not self.session.uc02_done:
            return
        p = self.session.inputs
        result = self.calc.calc_preliminary(p)
        # Copy vào session tạm
        m = self.session.motor
        m.eta = result.eta
        m.p_ct_kw = result.p_ct_kw
        m.u_ch_preliminary = result.u_ch_preliminary
        m.n_sb_rpm = result.n_sb_rpm

        self.lbl_eta.setText(f"{result.eta:.4f}")
        self.lbl_pct.setText(f"{result.p_ct_kw:.4f} kW")
        self.lbl_uch.setText(f"{result.u_ch_preliminary:.2f}")
        self.lbl_nsb.setText(f"{result.n_sb_rpm:.1f} vg/ph")

        # Lọc động cơ
        self.filtered = self.calc.filter_motors(
            self.catalog, result.p_ct_kw, result.n_sb_rpm, tol_pct=15.0
        )
        self._fill_motor_table()

    def _fill_motor_table(self):
        self.motor_table.setRowCount(0)
        alt_bg = QColor("#1C2B3A")
        base_bg = QColor("#162130")
        for i, m in enumerate(self.filtered):
            r = self.motor_table.rowCount()
            self.motor_table.insertRow(r)
            values = [
                m['name'], f"{m['rated_power_kw']:.1f}",
                f"{m['rated_rpm']:.0f}", f"{m['surplus_power']:.3f}",
                f"{m['delta_rpm']:.0f}", f"{m['delta_rpm_pct']:.1f}"
            ]
            bg = alt_bg if i % 2 == 0 else base_bg
            for c, v in enumerate(values):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(bg)
                self.motor_table.setItem(r, c, item)
            self.motor_table.setRowHeight(r, 34)

    def _on_motor_select(self):
        rows = self.motor_table.selectedItems()
        if not rows:
            return
        row = self.motor_table.currentRow()
        if row < 0 or row >= len(self.filtered):
            return
        self._selected_motor = self.filtered[row]
        m = self._selected_motor
        # Tính lại
        p = self.session.inputs
        result = self.session.motor
        result = self.calc.calc_after_motor_selected(p, result, m['rated_rpm'])
        result.motor_name = m['name']
        result.rated_power_kw = m['rated_power_kw']
        result.selected_motor_id = m['id']
        self.session.motor = result

        # Cập nhật UI
        self.lbl_motor_name.setText(m['name'])
        self.lbl_u_h.setText(f"{result.u_h_actual:.4f}")
        self.lbl_u2.setText(f"{result.u2:.2f}")
        self.lbl_uch_real.setText(f"{result.u_ch_actual:.4f}")

        # Bảng trục
        self._update_shaft_table(result)
        self.btn_confirm.setEnabled(True)

    def _update_shaft_table(self, m):
        self.shaft_table.clear_data()
        self.shaft_table.add_row([
            "Công suất (kW)",
            f"{m.shaft_powers.get('dc', 0):.4f}",
            f"{m.shaft_powers.get('I', 0):.4f}",
            f"{m.shaft_powers.get('II', 0):.4f}",
            f"{m.shaft_powers.get('III', 0):.4f}",
        ])
        self.shaft_table.add_row([
            "Số vòng quay (vg/ph)",
            f"{m.shaft_rpms.get('dc', 0):.1f}",
            f"{m.shaft_rpms.get('I', 0):.2f}",
            f"{m.shaft_rpms.get('II', 0):.2f}",
            f"{m.shaft_rpms.get('III', 0):.2f}",
        ])
        self.shaft_table.add_row([
            "Momen xoắn (N·mm)",
            f"{m.shaft_torques.get('dc', 0):.2f}",
            f"{m.shaft_torques.get('I', 0):.2f}",
            f"{m.shaft_torques.get('II', 0):.2f}",
            f"{m.shaft_torques.get('III', 0):.2f}",
        ])

    def _confirm(self):
        if not self._selected_motor:
            return
        self.session.uc03_done = True
        self.mw.on_step_completed(3)

    def refresh(self):
        m = self.session.motor
        if m.eta:
            self.lbl_eta.setText(f"{m.eta:.4f}")
            self.lbl_pct.setText(f"{m.p_ct_kw:.4f} kW")
            self.lbl_uch.setText(f"{m.u_ch_preliminary:.2f}")
            self.lbl_nsb.setText(f"{m.n_sb_rpm:.1f} vg/ph")
        if m.motor_name:
            self.lbl_motor_name.setText(m.motor_name)
            self.lbl_u_h.setText(f"{m.u_h_actual:.4f}")
            self.lbl_u2.setText(f"{m.u2:.2f}")
            self.lbl_uch_real.setText(f"{m.u_ch_actual:.4f}")
            self._update_shaft_table(m)
            self.btn_confirm.setEnabled(True)