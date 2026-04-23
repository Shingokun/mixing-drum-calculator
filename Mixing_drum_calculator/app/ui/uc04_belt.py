# ============================================================
# uc04_belt.py — Tính bộ truyền đai thang
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt
from app.core.session import ProjectSession
from app.core.uc04_calculator import UC04Calculator
from app.ui.widgets.param_input import ResultRow


class UC04BeltPage(QWidget):
    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self.calc = UC04Calculator()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        hdr = QLabel("Bước 3 · Tính Bộ Truyền Đai Thang")
        hdr.setProperty("type", "title")
        root.addWidget(hdr)
        sub = QLabel("Tính toán thông số bộ truyền đai loại B từ dữ liệu trục I.")
        sub.setProperty("type", "subtitle")
        root.addWidget(sub)
        root.addSpacing(24)

        splitter = QSplitter(Qt.Horizontal)

        # ── Panel trái: Thông tin đầu vào & sơ đồ ─────
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 12, 0)
        ll.setSpacing(16)

        g_in = QGroupBox("📥  Thông số đầu vào (từ UC03)")
        gl = QVBoxLayout(g_in)
        gl.setSpacing(10)
        self.lbl_n1   = self._kv(gl, "Tốc độ trục I  n₁",       "vg/ph")
        self.lbl_u_x  = self._kv(gl, "Tỉ số truyền đai  u_x",   "")
        self.lbl_P1   = self._kv(gl, "Công suất trục I  P₁",     "kW")
        self.lbl_T1   = self._kv(gl, "Momen xoắn trục I  T₁",   "N·mm")
        ll.addWidget(g_in)

        # Sơ đồ đai ASCII đơn giản
        g_diag = QGroupBox("🔄  Sơ đồ bộ truyền đai")
        gdl = QVBoxLayout(g_diag)
        diag = QLabel(
            "   Trục ĐC                    Trục I\n"
            "  ┌──────┐        đai        ┌──────┐\n"
            "  │  d₁  │═══════════════════│  d₂  │\n"
            "  └──────┘                   └──────┘\n"
            "  n₁ (rpm)    ←── a ───→    n₂ (rpm)\n"
        )
        diag.setStyleSheet(
            "font-family: 'Consolas','Courier New',monospace;"
            "font-size: 12px; color:#54A0FF; background:#0A1628;"
            "padding:12px; border-radius:6px;"
        )
        gdl.addWidget(diag)
        ll.addWidget(g_diag)
        ll.addStretch()
        splitter.addWidget(left)

        # ── Panel phải: Kết quả ────────────────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.setSpacing(16)

        g_res = QGroupBox("📐  Kết quả tính toán")
        grl = QVBoxLayout(g_res)
        grl.setSpacing(6)

        self.r_d1   = ResultRow("Đường kính bánh đai nhỏ  d₁",   "mm")
        self.r_d2   = ResultRow("Đường kính bánh đai lớn  d₂",   "mm")
        self.r_v    = ResultRow("Vận tốc đai  v",                 "m/s")
        self.r_L    = ResultRow("Chiều dài đai tiêu chuẩn  L",   "mm")
        self.r_a    = ResultRow("Khoảng cách trục  a",            "mm")
        self.r_a1   = ResultRow("Góc ôm bánh nhỏ  α₁",           "°")
        self.r_z    = ResultRow("Số dây đai  z",                  "dây")
        self.r_Ft   = ResultRow("Lực vòng  F_t",                  "N")
        self.r_F0   = ResultRow("Lực căng ban đầu  F₀",          "N")

        for w in [self.r_d1, self.r_d2, self.r_v, self.r_L,
                  self.r_a, self.r_a1, self.r_z, self.r_Ft, self.r_F0]:
            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            grl.addWidget(sep)
            grl.addWidget(w)

        # Kiểm tra vận tốc
        self.lbl_v_check = QLabel("")
        self.lbl_v_check.setAlignment(Qt.AlignCenter)
        self.lbl_v_check.setVisible(False)
        grl.addWidget(self.lbl_v_check)
        rl.addWidget(g_res, 1)

        # Nút tính & xác nhận
        btn_row = QHBoxLayout()
        self.btn_calc = QPushButton("🔄  Tính toán")
        self.btn_calc.clicked.connect(self._calculate)
        btn_row.addWidget(self.btn_calc)

        self.btn_confirm = QPushButton("Xác nhận và Tiếp tục →")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._confirm)
        btn_row.addWidget(self.btn_confirm)
        rl.addLayout(btn_row)

        splitter.addWidget(right)
        splitter.setSizes([380, 600])
        root.addWidget(splitter, 1)

    def _kv(self, layout, label: str, unit: str) -> QLabel:
        row = QHBoxLayout()
        l = QLabel(label + ":")
        l.setFixedWidth(240)
        l.setStyleSheet("color:#7F8C8D;")
        v = QLabel("—")
        v.setStyleSheet("font-weight:bold; color:#54A0FF;")
        u = QLabel(unit)
        u.setStyleSheet("color:#3D5166; font-size:11px;")
        row.addWidget(l); row.addWidget(v); row.addWidget(u)
        row.addStretch()
        layout.addLayout(row)
        return v

    def _calculate(self):
        m = self.session.motor
        p = self.session.inputs
        n1  = m.shaft_rpms.get('I', 0)
        P1  = m.shaft_powers.get('I', 0)
        T1  = m.shaft_torques.get('I', 0)
        u_x = p.u_x

        self.lbl_n1.setText(f"{n1:.2f}")
        self.lbl_u_x.setText(f"{u_x:.2f}")
        self.lbl_P1.setText(f"{P1:.4f}")
        self.lbl_T1.setText(f"{T1:.2f}")

        belt = self.calc.calc(n1, u_x, P1, T1)
        self.session.belt = belt

        self.r_d1.set_value(belt.d1_mm, 1)
        self.r_d2.set_value(belt.d2_mm, 1)
        self.r_v.set_value(belt.belt_velocity_ms, 3)
        self.r_L.set_value(belt.belt_length_mm, 0)
        self.r_a.set_value(belt.center_distance_mm, 1)
        self.r_a1.set_value(belt.alpha1_deg, 2)
        self.r_z.set_value(belt.num_belts, 0)
        self.r_Ft.set_value(belt.Ft_N, 1)
        self.r_F0.set_value(belt.F0_N, 1)

        self.lbl_v_check.setVisible(True)
        if belt.velocity_ok:
            self.lbl_v_check.setText("✓  Vận tốc đai hợp lệ (v ≤ 25 m/s)")
            self.lbl_v_check.setStyleSheet(
                "color:#10AC84; font-weight:bold; font-size:13px;"
                "background:#0D2B1F; border-radius:6px; padding:8px;"
            )
            self.btn_confirm.setEnabled(True)
        else:
            self.lbl_v_check.setText(
                f"✗  Vận tốc đai {belt.belt_velocity_ms:.2f} m/s vượt giới hạn 25 m/s!\n"
                "→ Quay lại UC03 để điều chỉnh tỉ số truyền."
            )
            self.lbl_v_check.setStyleSheet(
                "color:#EE5A24; font-weight:bold; font-size:13px;"
                "background:#2B1510; border-radius:6px; padding:8px;"
            )
            self.btn_confirm.setEnabled(False)

    def _confirm(self):
        self.session.uc04_done = True
        self.mw.on_step_completed(3)

    def refresh(self):
        b = self.session.belt
        if b.d1_mm:
            self.r_d1.set_value(b.d1_mm, 1)
            self.r_d2.set_value(b.d2_mm, 1)
            self.r_v.set_value(b.belt_velocity_ms, 3)
            self.r_L.set_value(b.belt_length_mm, 0)
            self.r_a.set_value(b.center_distance_mm, 1)
            self.r_a1.set_value(b.alpha1_deg, 2)
            self.r_z.set_value(b.num_belts, 0)
            self.r_Ft.set_value(b.Ft_N, 1)
            self.r_F0.set_value(b.F0_N, 1)
            self.btn_confirm.setEnabled(b.velocity_ok)