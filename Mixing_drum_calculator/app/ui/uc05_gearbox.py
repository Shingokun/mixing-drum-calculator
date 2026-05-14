# ============================================================
# uc05_gearbox.py — Bevel Gearbox Design
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from app.core.session import ProjectSession
from app.core.uc05_calculator import UC05Calculator
from app.ui.widgets.param_input import ResultRow
from app.ui.i18n import _

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

        self.hdr = QLabel(_("uc05_hdr"))
        self.hdr.setProperty("type", "title")
        root.addWidget(self.hdr)
        self.sub = QLabel(_("uc05_sub"))
        self.sub.setProperty("type", "subtitle")
        root.addWidget(self.sub)
        root.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(20)

        # Allowable Stresses
        self.g_stress = QGroupBox(_("g_allow_stress"))
        gsl = QVBoxLayout(self.g_stress)
        self.res_sig_h  = ResultRow("lbl_sig_h", "unit_mpa")
        self.res_sig_f1 = ResultRow("lbl_sig_f1", "unit_mpa")
        self.res_sig_f2 = ResultRow("lbl_sig_f2", "unit_mpa")
        for w in [self.res_sig_h, self.res_sig_f1, self.res_sig_f2]: gsl.addWidget(w)
        cl.addWidget(self.g_stress)

        # Geometry
        self.g_geo = QGroupBox(_("g_gear_geo"))
        ggl = QVBoxLayout(self.g_geo)
        self.res_re    = ResultRow("lbl_re", "unit_mm")
        self.res_mte   = ResultRow("lbl_mte", "")
        self.res_z1z2  = ResultRow("lbl_z1z2", "")
        self.res_u_tt  = ResultRow("lbl_u_gear", "")
        self.res_delta = ResultRow("lbl_delta_u", "%")
        self.res_b     = ResultRow("lbl_b_width", "unit_mm")
        for w in [self.res_re, self.res_mte, self.res_z1z2, self.res_u_tt, self.res_delta, self.res_b]: ggl.addWidget(w)
        cl.addWidget(self.g_geo)

        # Strength Check
        self.g_check = QGroupBox(_("g_strength_check"))
        gcl = QVBoxLayout(self.g_check)
        self.res_check_f1 = ResultRow("lbl_check_f1", "")
        self.res_check_f2 = ResultRow("lbl_check_f2", "")
        for w in [self.res_check_f1, self.res_check_f2]: gcl.addWidget(w)
        cl.addWidget(self.g_check)

        # Forces
        self.g_forces = QGroupBox(_("g_forces"))
        gfl = QVBoxLayout(self.g_forces)
        self.res_ft = ResultRow("lbl_ft", "unit_n")
        self.res_fr = ResultRow("lbl_fr", "unit_n")
        self.res_fa = ResultRow("lbl_fa", "unit_n")
        for w in [self.res_ft, self.res_fr, self.res_fa]: gfl.addWidget(w)
        cl.addWidget(self.g_forces)

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.btn_confirm = QPushButton(_("confirm_next"))
        self.btn_confirm.clicked.connect(self._confirm)
        root.addWidget(self.btn_confirm)

    def retranslate_ui(self):
        self.hdr.setText(_("uc05_hdr"))
        self.sub.setText(_("uc05_sub"))
        self.g_stress.setTitle(_("g_allow_stress"))
        self.g_geo.setTitle(_("g_gear_geo"))
        self.g_check.setTitle(_("g_strength_check"))
        self.g_forces.setTitle(_("g_forces"))
        self.btn_confirm.setText(_("confirm_next"))
        for w in [self.res_sig_h, self.res_sig_f1, self.res_sig_f2, self.res_re,
                  self.res_mte, self.res_z1z2, self.res_u_tt, self.res_delta,
                  self.res_b, self.res_check_f1, self.res_check_f2, self.res_ft,
                  self.res_fr, self.res_fa]:
            w.retranslate_ui()
        self.refresh()

    def refresh(self):
        if not self.session.uc03_done: return
        m = self.session.motor
        res = self.calc.run(m.u_h_actual, m.shaft_rpms['I'], m.shaft_torques['I'])
        self.session.gearbox.cone = res
        self.session.uc05_done = True

        self.res_sig_h.set_value(res.sig_H, 2)
        self.res_sig_f1.set_value(res.sig_F1, 2)
        self.res_sig_f2.set_value(res.sig_F2, 2)

        self.res_re.set_value(res.Re_mm, 2)
        self.res_mte.set_value(res.m_te, 1)
        self.res_z1z2.set_value(f"{res.z1} / {res.z2}")
        self.res_u_tt.set_value(res.u_tt, 4)
        self.res_delta.set_value(res.delta_u_pct, 2)
        self.res_b.set_value(res.b_mm, 2)

        self.res_check_f1.set_value(f"{res.sigma_F1_actual:.2f} <= {res.sig_F1:.2f}")
        self.res_check_f1.set_badge(res.F1_ok)
        self.res_check_f2.set_value(f"{res.sigma_F2_actual:.2f} <= {res.sig_F2:.2f}")
        self.res_check_f2.set_badge(res.F2_ok)

        self.res_ft.set_value(res.Ft_N, 1)
        self.res_fr.set_value(res.Fr_N, 1)
        self.res_fa.set_value(res.Fa_N, 1)

    def _confirm(self):
        self.mw.on_step_completed(4)
