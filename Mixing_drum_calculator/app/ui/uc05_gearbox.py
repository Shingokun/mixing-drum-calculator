# ============================================================
# uc05_gearbox.py — Tính hộp giảm tốc bánh răng côn cấp nhanh
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QFrame, QSplitter, QScrollArea,
    QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt
from app.core.session import ProjectSession, GearboxResult
from app.core.uc05_calculator import UC05Calculator
from app.ui.widgets.param_input import ResultRow


# Vật liệu mặc định
MATERIALS = {
    "Thép 45 (tôi cải thiện) — HB 180–230": (205, 190, 1.1, 1.75),
    "Thép 40X (tôi cải thiện) — HB 235–262": (248, 235, 1.1, 1.75),
    "Thép 40XH (tôi cải thiện) — HB 260–280": (270, 255, 1.1, 1.75),
    "Thép 40X (tôi bề mặt) — HB 45–50 HRC":  (320, 300, 1.2, 1.75),
    "Nhập thủ công": None,
}


class UC05GearboxPage(QWidget):
    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self.calc = UC05Calculator()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        hdr = QLabel("Bước 4 · Tính Hộp Giảm Tốc (Bánh răng Côn)")
        hdr.setProperty("type", "title")
        root.addWidget(hdr)
        sub = QLabel("Tính thông số hình học và kiểm bền uốn, tiếp xúc cho bánh răng côn cấp nhanh.")
        sub.setProperty("type", "subtitle")
        root.addWidget(sub)
        root.addSpacing(20)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        # ── Panel trái: Chọn vật liệu & thông số ──────
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 12, 0)
        ll.setSpacing(14)

        # Thông số đầu vào
        g_in = QGroupBox("📥  Dữ liệu đầu vào (từ UC03)")
        gl = QVBoxLayout(g_in)
        gl.setSpacing(8)
        self.lbl_u1 = self._kv(gl, "Tỉ số truyền cấp nhanh  u₁")
        self.lbl_n1 = self._kv(gl, "Tốc độ trục I  n₁", "vg/ph")
        self.lbl_T1 = self._kv(gl, "Momen trục I  T₁",  "N·mm")
        ll.addWidget(g_in)

        # Chọn vật liệu
        g_mat = QGroupBox("🔩  Chọn vật liệu bánh răng")
        gml = QVBoxLayout(g_mat)
        gml.setSpacing(10)

        mat_lbl = QLabel("Vật liệu bánh răng:")
        mat_lbl.setStyleSheet("color:#7F8C8D;")
        self.combo_mat = QComboBox()
        self.combo_mat.addItems(list(MATERIALS.keys()))
        self.combo_mat.currentIndexChanged.connect(self._on_material_changed)
        gml.addWidget(mat_lbl)
        gml.addWidget(self.combo_mat)

        # HB thủ công
        self.manual_frame = QFrame()
        mfl = QHBoxLayout(self.manual_frame)
        mfl.setContentsMargins(0, 0, 0, 0)
        mfl.setSpacing(12)

        mfl.addWidget(QLabel("HB₁:"))
        self.spin_HB1 = QDoubleSpinBox()
        self.spin_HB1.setRange(150, 400); self.spin_HB1.setValue(250)
        mfl.addWidget(self.spin_HB1)

        mfl.addWidget(QLabel("HB₂:"))
        self.spin_HB2 = QDoubleSpinBox()
        self.spin_HB2.setRange(150, 400); self.spin_HB2.setValue(230)
        mfl.addWidget(self.spin_HB2)
        mfl.addStretch()
        self.manual_frame.setVisible(False)
        gml.addWidget(self.manual_frame)

        # Thêm hệ số
        row_sf = QHBoxLayout()
        row_sf.addWidget(QLabel("S_H:"))
        self.spin_SH = QDoubleSpinBox()
        self.spin_SH.setRange(0.5, 3.0); self.spin_SH.setSingleStep(0.05)
        self.spin_SH.setValue(1.1)
        row_sf.addWidget(self.spin_SH)
        row_sf.addWidget(QLabel("S_F:"))
        self.spin_SF = QDoubleSpinBox()
        self.spin_SF.setRange(0.5, 3.0); self.spin_SF.setSingleStep(0.05)
        self.spin_SF.setValue(1.75)
        row_sf.addWidget(self.spin_SF)
        row_sf.addStretch()
        gml.addLayout(row_sf)

        row_z1 = QHBoxLayout()
        row_z1.addWidget(QLabel("Số răng sơ bộ z₁_sb:"))
        self.spin_z1sb = QSpinBox()
        self.spin_z1sb.setRange(10, 30); self.spin_z1sb.setValue(16)
        row_z1.addWidget(self.spin_z1sb)
        row_z1.addStretch()
        gml.addLayout(row_z1)

        ll.addWidget(g_mat)

        self.btn_calc = QPushButton("🔄  Tính toán kiểm bền")
        self.btn_calc.clicked.connect(self._calculate)
        ll.addWidget(self.btn_calc)
        ll.addStretch()
        splitter.addWidget(left)

        # ── Panel phải: Kết quả ────────────────────────
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.setSpacing(14)

        # Ứng suất cho phép
        g_stress = QGroupBox("⚡  Ứng suất cho phép")
        gsl = QVBoxLayout(g_stress)
        gsl.setSpacing(6)
        self.r_sigH  = ResultRow("[σ_H] tiếp xúc cho phép",  "MPa")
        self.r_sigF1 = ResultRow("[σ_F1] uốn cho phép bánh nhỏ", "MPa")
        self.r_sigF2 = ResultRow("[σ_F2] uốn cho phép bánh lớn", "MPa")
        for w in [self.r_sigH, self.r_sigF1, self.r_sigF2]:
            gsl.addWidget(w)
        rl.addWidget(g_stress)

        # Thông số hình học
        g_geo = QGroupBox("📐  Thông số hình học")
        ggl = QVBoxLayout(g_geo)
        ggl.setSpacing(6)
        self.r_Re   = ResultRow("Chiều dài côn ngoài  R_e",   "mm")
        self.r_de1  = ResultRow("Đường kính vòng chia ngoài d_e1", "mm")
        self.r_mte  = ResultRow("Mô đun ngoài tiêu chuẩn  m_te",   "mm")
        self.r_z1   = ResultRow("Số răng bánh nhỏ  z₁",       "")
        self.r_z2   = ResultRow("Số răng bánh lớn  z₂",       "")
        self.r_utt  = ResultRow("Tỉ số truyền thực tế  u_tt", "")
        self.r_du   = ResultRow("Sai lệch tỉ số truyền  Δu",  "%")
        self.r_b    = ResultRow("Chiều rộng vành răng  b",    "mm")
        self.r_d1   = ResultRow("Góc côn chia  δ₁ / δ₂",     "°")
        for w in [self.r_Re, self.r_de1, self.r_mte, self.r_z1, self.r_z2,
                  self.r_utt, self.r_du, self.r_b, self.r_d1]:
            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            ggl.addWidget(sep); ggl.addWidget(w)
        rl.addWidget(g_geo)

        # Kiểm bền
        g_check = QGroupBox("🔍  Kiểm tra độ bền")
        gck = QVBoxLayout(g_check)
        gck.setSpacing(8)
        self.r_sF1_act = ResultRow("σ_F1 thực tế / cho phép",   "MPa")
        self.r_sF2_act = ResultRow("σ_F2 thực tế / cho phép",   "MPa")
        self.r_Ft      = ResultRow("Lực vòng  F_t",              "N")
        self.r_Fr      = ResultRow("Lực hướng tâm  F_r",         "N")
        self.r_Fa      = ResultRow("Lực dọc trục  F_a",          "N")
        for w in [self.r_sF1_act, self.r_sF2_act, self.r_Ft, self.r_Fr, self.r_Fa]:
            gck.addWidget(w)

        self.lbl_verdict = QLabel("")
        self.lbl_verdict.setAlignment(Qt.AlignCenter)
        self.lbl_verdict.setVisible(False)
        gck.addWidget(self.lbl_verdict)
        rl.addWidget(g_check)

        self.btn_confirm = QPushButton("Xác nhận và Tiếp tục →")
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._confirm)
        rl.addWidget(self.btn_confirm)
        rl.addStretch()

        right_scroll.setWidget(right)
        splitter.addWidget(right_scroll)
        splitter.setSizes([360, 620])
        root.addWidget(splitter, 1)

    def _kv(self, layout, label: str, unit: str = "") -> QLabel:
        row = QHBoxLayout()
        l = QLabel(label + ":"); l.setFixedWidth(220); l.setStyleSheet("color:#7F8C8D;")
        v = QLabel("—"); v.setStyleSheet("font-weight:bold; color:#54A0FF;")
        u = QLabel(unit); u.setStyleSheet("color:#3D5166; font-size:11px;")
        row.addWidget(l); row.addWidget(v); row.addWidget(u); row.addStretch()
        layout.addLayout(row)
        return v

    def _on_material_changed(self, idx: int):
        mat_name = self.combo_mat.currentText()
        is_manual = (mat_name == "Nhập thủ công")
        self.manual_frame.setVisible(is_manual)
        if not is_manual:
            val = MATERIALS[mat_name]
            if val:
                HB1, HB2, SH, SF = val
                self.spin_HB1.setValue(HB1)
                self.spin_HB2.setValue(HB2)
                self.spin_SH.setValue(SH)
                self.spin_SF.setValue(SF)

    def _get_HB(self):
        return self.spin_HB1.value(), self.spin_HB2.value()

    def _calculate(self):
        m = self.session.motor
        p = self.session.inputs
        u1 = p.u1
        n1 = m.shaft_rpms.get('I', 0)
        T1 = m.shaft_torques.get('I', 0)

        self.lbl_u1.setText(f"{u1:.2f}")
        self.lbl_n1.setText(f"{n1:.2f}")
        self.lbl_T1.setText(f"{T1:.2f}")

        HB1, HB2 = self._get_HB()
        S_H = self.spin_SH.value()
        S_F = self.spin_SF.value()
        z1_sb = self.spin_z1sb.value()

        cone = self.calc.run(u1, n1, T1, HB1, HB2, S_H, S_F, z1_sb=z1_sb)
        gb = GearboxResult()
        gb.cone = cone
        gb.strength_ok = cone.F1_ok and cone.F2_ok
        self.session.gearbox = gb

        # Ứng suất cho phép
        self.r_sigH.set_value(cone.sig_H, 2)
        self.r_sigF1.set_value(cone.sig_F1, 2)
        self.r_sigF2.set_value(cone.sig_F2, 2)

        # Hình học
        self.r_Re.set_value(cone.Re_mm, 2)
        self.r_de1.set_value(cone.de1_mm, 2)
        self.r_mte.set_value(cone.m_te, 2)
        self.r_z1.set_value(cone.z1, 0)
        self.r_z2.set_value(cone.z2, 0)
        self.r_utt.set_value(cone.u_tt, 4)
        self.r_du.set_value(cone.delta_u_pct, 2)
        self.r_b.set_value(cone.b_mm, 2)
        self.r_d1.set_value(f"{cone.delta1_deg:.3f}° / {cone.delta2_deg:.3f}°")

        # Kiểm bền
        self.r_sF1_act.set_value(
            f"{cone.sigma_F1_actual:.2f} / {cone.sig_F1:.2f}"
        )
        self.r_sF1_act.set_badge(cone.F1_ok)
        self.r_sF2_act.set_value(
            f"{cone.sigma_F2_actual:.2f} / {cone.sig_F2:.2f}"
        )
        self.r_sF2_act.set_badge(cone.F2_ok)

        self.r_Ft.set_value(cone.Ft_N, 1)
        self.r_Fr.set_value(cone.Fr_N, 1)
        self.r_Fa.set_value(cone.Fa_N, 1)

        # Verdict
        self.lbl_verdict.setVisible(True)
        if gb.strength_ok:
            self.lbl_verdict.setText("✓  Bánh răng đủ bền — Kiểm bền uốn ĐẠT")
            self.lbl_verdict.setStyleSheet(
                "color:#10AC84; font-weight:bold; font-size:14px;"
                "background:#0D2B1F; border-radius:6px; padding:10px;"
            )
            self.btn_confirm.setEnabled(True)
        else:
            msgs = []
            if not cone.F1_ok:
                msgs.append(f"σ_F1 = {cone.sigma_F1_actual:.2f} > [{cone.sig_F1:.2f}]")
            if not cone.F2_ok:
                msgs.append(f"σ_F2 = {cone.sigma_F2_actual:.2f} > [{cone.sig_F2:.2f}]")
            self.lbl_verdict.setText(
                "✗  KHÔNG ĐẠT — " + "  |  ".join(msgs) +
                "\n→ Điều chỉnh vật liệu hoặc hệ số chiều rộng vành răng"
            )
            self.lbl_verdict.setStyleSheet(
                "color:#EE5A24; font-weight:bold; font-size:13px;"
                "background:#2B1510; border-radius:6px; padding:10px;"
            )
            self.btn_confirm.setEnabled(False)

    def _confirm(self):
        self.session.uc05_done = True
        self.mw.on_step_completed(4)

    def refresh(self):
        gb = self.session.gearbox
        c = gb.cone
        if c.Re_mm:
            self.r_Re.set_value(c.Re_mm, 2)
            self.r_de1.set_value(c.de1_mm, 2)
            self.r_mte.set_value(c.m_te, 2)
            self.r_z1.set_value(c.z1, 0)
            self.r_z2.set_value(c.z2, 0)
            self.r_utt.set_value(c.u_tt, 4)
            self.r_du.set_value(c.delta_u_pct, 2)
            self.r_b.set_value(c.b_mm, 2)
            self.r_d1.set_value(f"{c.delta1_deg:.3f}° / {c.delta2_deg:.3f}°")
            self.r_sigH.set_value(c.sig_H, 2)
            self.r_sigF1.set_value(c.sig_F1, 2)
            self.r_sigF2.set_value(c.sig_F2, 2)
            self.r_sF1_act.set_value(f"{c.sigma_F1_actual:.2f} / {c.sig_F1:.2f}")
            self.r_sF1_act.set_badge(c.F1_ok)
            self.r_sF2_act.set_value(f"{c.sigma_F2_actual:.2f} / {c.sig_F2:.2f}")
            self.r_sF2_act.set_badge(c.F2_ok)
            self.r_Ft.set_value(c.Ft_N, 1)
            self.r_Fr.set_value(c.Fr_N, 1)
            self.r_Fa.set_value(c.Fa_N, 1)
            self.btn_confirm.setEnabled(gb.strength_ok)
