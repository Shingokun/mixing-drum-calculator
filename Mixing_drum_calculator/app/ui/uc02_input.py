# ============================================================
# uc02_input.py — Input parameters
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from app.core.session import ProjectSession
from app.core.validators import validate_positive, validate_efficiency, validate_ratio
from app.ui.widgets.param_input import ParamInput
from app.ui.i18n import _


class UC02InputPage(QWidget):
    completed = Signal()

    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        # Header
        self.hdr = QLabel(_("uc02_hdr"))
        self.hdr.setProperty("type", "title")
        root.addWidget(self.hdr)

        self.sub = QLabel(_("uc02_sub"))
        self.sub.setProperty("type", "subtitle")
        root.addWidget(self.sub)
        root.addSpacing(20)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(20)
        cl.setContentsMargins(0, 0, 0, 0)

        # ── Group 1: Kinematics ────────────────
        self.g1 = QGroupBox(_("g_kinematics"))
        g1l = QVBoxLayout(self.g1)
        g1l.setSpacing(12)

        self.inp_power = ParamInput("p_power", "kW", 6.5, validate_positive)
        self.inp_rpm = ParamInput("p_rpm", "unit_rpm", 75.0, validate_positive)
        self.inp_life = ParamInput("p_life", "unit_year", 10.0, validate_positive)
        
        for w in [self.inp_power, self.inp_rpm, self.inp_life]:
            g1l.addWidget(w)
        cl.addWidget(self.g1)

        # ── Group 2: Efficiency ─────────────────
        self.g2 = QGroupBox(_("g_efficiency"))
        g2l = QVBoxLayout(self.g2)
        g2l.setSpacing(12)

        self.inp_eta_kn  = ParamInput("p_eta_kn",  "", 1.00, validate_efficiency)
        self.inp_eta_ol  = ParamInput("p_eta_ol",  "", 0.99, validate_efficiency)
        self.inp_eta_brc = ParamInput("p_eta_brc", "", 0.96, validate_efficiency)
        self.inp_eta_brt = ParamInput("p_eta_brt", "", 0.97, validate_efficiency)
        self.inp_eta_x   = ParamInput("p_eta_x",   "", 0.91, validate_efficiency)
        for w in [self.inp_eta_kn, self.inp_eta_ol, self.inp_eta_brc,
                  self.inp_eta_brt, self.inp_eta_x]:
            g2l.addWidget(w)
        cl.addWidget(self.g2)

        # ── Group 3: Ratios ──────────────
        self.g3 = QGroupBox(_("g_prelim_ratio"))
        g3l = QVBoxLayout(self.g3)
        g3l.setSpacing(12)

        self.inp_u_h  = ParamInput("p_u_h",  "", 13.0, lambda v, n: validate_ratio(v, n, 5, 60))
        self.inp_u_x  = ParamInput("p_u_x",  "", 3.0,  lambda v, n: validate_ratio(v, n, 1, 10))
        self.inp_u1   = ParamInput("p_u1",   "", 3.45, lambda v, n: validate_ratio(v, n, 1, 10))
        for w in [self.inp_u_h, self.inp_u_x, self.inp_u1]:
            g3l.addWidget(w)
        cl.addWidget(self.g3)

        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Footer ──────────────────────
        root.addSpacing(16)
        footer = QHBoxLayout()
        footer.addStretch()

        self.err_summary = QLabel("")
        self.err_summary.setProperty("type", "error")
        footer.addWidget(self.err_summary)

        self.btn_confirm = QPushButton(_("confirm_next"))
        self.btn_confirm.setFixedHeight(42)
        self.btn_confirm.clicked.connect(self._confirm)
        footer.addWidget(self.btn_confirm)
        root.addLayout(footer)

    def retranslate_ui(self):
        self.hdr.setText(_("uc02_hdr"))
        self.sub.setText(_("uc02_sub"))
        self.g1.setTitle(_("g_kinematics"))
        self.g2.setTitle(_("g_efficiency"))
        self.g3.setTitle(_("g_prelim_ratio"))
        self.btn_confirm.setText(_("confirm_next"))
        for w in self._all_inputs():
            w.retranslate_ui()

    def _all_inputs(self):
        return [
            self.inp_power, self.inp_rpm, self.inp_life,
            self.inp_eta_kn, self.inp_eta_ol, self.inp_eta_brc,
            self.inp_eta_brt, self.inp_eta_x,
            self.inp_u_h, self.inp_u_x, self.inp_u1
        ]

    def _confirm(self):
        invalid = [w for w in self._all_inputs() if not w.is_valid()]
        if invalid:
            self.err_summary.setText(_("invalid_inputs", count=len(invalid)))
            for w in invalid:
                w._on_change(w.edit.text())
            return
        self.err_summary.setText("")

        inp = self.session.inputs
        inp.power_kw           = self.inp_power.get_value()[1]
        inp.rpm_out            = self.inp_rpm.get_value()[1]
        inp.service_life_year  = self.inp_life.get_value()[1]
        inp.eta_kn             = self.inp_eta_kn.get_value()[1]
        inp.eta_ol             = self.inp_eta_ol.get_value()[1]
        inp.eta_brc            = self.inp_eta_brc.get_value()[1]
        inp.eta_brt            = self.inp_eta_brt.get_value()[1]
        inp.eta_x              = self.inp_eta_x.get_value()[1]
        inp.u_h                = self.inp_u_h.get_value()[1]
        inp.u_x                = self.inp_u_x.get_value()[1]
        inp.u1                 = self.inp_u1.get_value()[1]

        self.session.uc02_done = True
        self.mw.on_step_completed(1)

    def refresh(self):
        inp = self.session.inputs
        self.inp_power.set_value(inp.power_kw)
        self.inp_rpm.set_value(inp.rpm_out)
        self.inp_life.set_value(inp.service_life_year)
        self.inp_eta_kn.set_value(inp.eta_kn)
        self.inp_eta_ol.set_value(inp.eta_ol)
        self.inp_eta_brc.set_value(inp.eta_brc)
        self.inp_eta_brt.set_value(inp.eta_brt)
        self.inp_eta_x.set_value(inp.eta_x)
        self.inp_u_h.set_value(inp.u_h)
        self.inp_u_x.set_value(inp.u_x)
        self.inp_u1.set_value(inp.u1)
