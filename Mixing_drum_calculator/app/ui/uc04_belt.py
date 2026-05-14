# ============================================================
# uc04_belt.py — V-Belt Drive Design
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from app.core.session import ProjectSession
from app.core.uc04_calculator import UC04Calculator
from app.ui.widgets.param_input import ResultRow
from app.ui.i18n import _

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

        self.hdr = QLabel(_("uc04_hdr"))
        self.hdr.setProperty("type", "title")
        root.addWidget(self.hdr)
        self.sub = QLabel(_("uc04_sub"))
        self.sub.setProperty("type", "subtitle")
        root.addWidget(self.sub)
        root.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(20)

        # ── Input Summary ──
        self.g_in = QGroupBox(_("g_input_summary"))
        ginl = QVBoxLayout(self.g_in)
        self.res_p1 = ResultRow("lbl_p1", "kW")
        self.res_n1 = ResultRow("lbl_n1", "unit_rpm")
        self.res_u  = ResultRow("lbl_u_belt", "")
        for w in [self.res_p1, self.res_n1, self.res_u]: ginl.addWidget(w)
        
        self.btn_calc = QPushButton(_("btn_calc_belt"))
        self.btn_calc.clicked.connect(self._do_calc)
        ginl.addWidget(self.btn_calc)
        cl.addWidget(self.g_in)

        # ── Results ──
        self.g_res = QGroupBox(_("g_belt_results"))
        gresl = QVBoxLayout(self.g_res)
        self.res_d1     = ResultRow("lbl_d1", "unit_mm")
        self.res_d2     = ResultRow("lbl_d2", "unit_mm")
        self.res_v      = ResultRow("lbl_v_belt", "unit_ms")
        self.res_a      = ResultRow("lbl_a_belt", "unit_mm")
        self.res_L      = ResultRow("lbl_l_belt", "unit_mm")
        self.res_z      = ResultRow("lbl_z_belt", "")
        self.res_alpha1 = ResultRow("lbl_alpha1", "unit_deg")
        self.res_ft     = ResultRow("lbl_ft", "unit_n")
        self.res_f0     = ResultRow("lbl_f0", "unit_n")

        for w in [self.res_d1, self.res_d2, self.res_v, self.res_a,
                  self.res_L, self.res_z, self.res_alpha1, self.res_ft, self.res_f0]:
            gresl.addWidget(w)
        
        self.g_res.setVisible(False)
        cl.addWidget(self.g_res)
        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.btn_confirm = QPushButton(_("confirm_next"))
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._confirm)
        root.addWidget(self.btn_confirm)

    def retranslate_ui(self):
        self.hdr.setText(_("uc04_hdr"))
        self.sub.setText(_("uc04_sub"))
        self.g_in.setTitle(_("g_input_summary"))
        self.btn_calc.setText(_("btn_calc_belt"))
        self.g_res.setTitle(_("g_belt_results"))
        self.btn_confirm.setText(_("confirm_next"))
        for w in [self.res_p1, self.res_n1, self.res_u, self.res_d1, self.res_d2,
                  self.res_v, self.res_a, self.res_L, self.res_z, self.res_alpha1,
                  self.res_ft, self.res_f0]:
            w.retranslate_ui()
        self.refresh()

    def _do_calc(self):
        if not self.session.uc03_done: return
        m = self.session.motor
        p = self.session.inputs
        res = self.calc.calc(m.shaft_rpms['dc'], p.u_x, m.shaft_powers['dc'], m.shaft_torques['dc'])
        self.session.belt = res
        self.session.uc04_done = True
        self.refresh()

    def refresh(self):
        m = self.session.motor
        p = self.session.inputs
        self.res_p1.set_value(m.shaft_powers.get('dc', 0))
        self.res_n1.set_value(m.shaft_rpms.get('dc', 0), 1)
        self.res_u.set_value(p.u_x)

        b = self.session.belt
        if b.d1_mm > 0:
            self.g_res.setVisible(True)
            self.res_d1.set_value(b.d1_mm, 1)
            self.res_d2.set_value(b.d2_mm, 1)
            self.res_v.set_value(b.belt_velocity_ms, 2)
            self.res_v.set_badge(b.velocity_ok)
            self.res_a.set_value(b.center_distance_mm, 1)
            self.res_L.set_value(b.belt_length_mm, 0)
            self.res_z.set_value(b.num_belts, 0)
            self.res_alpha1.set_value(b.alpha1_deg, 2)
            self.res_ft.set_value(b.Ft_N, 1)
            self.res_f0.set_value(b.F0_N, 1)
            self.btn_confirm.setEnabled(True)

    def _confirm(self):
        self.mw.on_step_completed(3)
