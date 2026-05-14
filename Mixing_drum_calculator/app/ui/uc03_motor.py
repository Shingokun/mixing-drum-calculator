# ============================================================
# uc03_motor.py — Motor Selection & Ratio Distribution
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
from app.ui.i18n import _

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
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        path = os.path.normpath(os.path.join(base_dir, "app", "data", "motor_catalog.json"))
        
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
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

        self.hdr = QLabel(_("uc03_hdr"))
        self.hdr.setProperty("type", "title")
        root.addWidget(self.hdr)
        self.sub = QLabel(_("uc03_sub"))
        self.sub.setProperty("type", "subtitle")
        root.addWidget(self.sub)
        root.addSpacing(20)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        # ── Left Panel ────
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 12, 0)
        ll.setSpacing(16)

        self.g_prelim = QGroupBox(_("g_prelim_calc"))
        gpl = QVBoxLayout(self.g_prelim)
        gpl.setSpacing(8)

        self.lbl_eta_row = self._kv_row(gpl, "lbl_total_eta")
        self.lbl_pct_row = self._kv_row(gpl, "lbl_req_power")
        self.lbl_uch_row = self._kv_row(gpl, "lbl_prelim_u")
        self.lbl_nsb_row = self._kv_row(gpl, "lbl_prelim_n")

        self.btn_calc = QPushButton(_("btn_prelim"))
        self.btn_calc.clicked.connect(self._do_prelim)
        gpl.addWidget(self.btn_calc)
        ll.addWidget(self.g_prelim)

        self.g_list = QGroupBox(_("g_motor_list"))
        gll = QVBoxLayout(self.g_list)

        self.motor_table = QTableWidget(0, 6)
        self._init_table_headers()
        self.motor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.motor_table.verticalHeader().setVisible(False)
        self.motor_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.motor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.motor_table.setMinimumHeight(220)
        self.motor_table.itemSelectionChanged.connect(self._on_motor_select)
        gll.addWidget(self.motor_table)
        ll.addWidget(self.g_list, 1)

        splitter.addWidget(left)

        # ── Right Panel ─────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.setSpacing(16)

        self.g_shaft = QGroupBox(_("g_shaft_table"))
        gsl = QVBoxLayout(self.g_shaft)

        self.shaft_table = ResultTable(
            [_("shaft_param"), _("shaft_motor"), _("shaft_1"), _("shaft_2"), _("shaft_3")]
        )
        self.shaft_table.setMinimumHeight(200)
        gsl.addWidget(self.shaft_table)
        rl.addWidget(self.g_shaft)

        self.g_sel = QGroupBox(_("g_selected_motor"))
        gsel = QVBoxLayout(self.g_sel)
        gsel.setSpacing(8)
        self.lbl_motor_name_row = self._kv_row(gsel, "lbl_motor_id")
        self.lbl_u_h_row        = self._kv_row(gsel, "lbl_actual_uh")
        self.lbl_u2_row         = self._kv_row(gsel, "lbl_u2")
        self.lbl_uch_real_row   = self._kv_row(gsel, "lbl_actual_utotal")
        rl.addWidget(self.g_sel)

        self.btn_confirm = QPushButton(_("confirm_next"))
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._confirm)
        rl.addWidget(self.btn_confirm)
        rl.addStretch()

        splitter.addWidget(right)
        splitter.setSizes([480, 520])
        root.addWidget(splitter, 1)

    def _init_table_headers(self):
        self.motor_table.setHorizontalHeaderLabels([
            _("col_id"), _("col_p"), _("col_n"),
            _("col_surplus"), _("col_dn"), _("col_dn_pct")
        ])

    def retranslate_ui(self):
        self.hdr.setText(_("uc03_hdr"))
        self.sub.setText(_("uc03_sub"))
        self.g_prelim.setTitle(_("g_prelim_calc"))
        self.btn_calc.setText(_("btn_prelim"))
        self.g_list.setTitle(_("g_motor_list"))
        self.g_shaft.setTitle(_("g_shaft_table"))
        self.g_sel.setTitle(_("g_selected_motor"))
        self.btn_confirm.setText(_("confirm_next"))
        
        self._init_table_headers()
        self.shaft_table.setHorizontalHeaderLabels([
            _("shaft_param"), _("shaft_motor"), _("shaft_1"), _("shaft_2"), _("shaft_3")
        ])
        
        # Update KV rows (labels)
        self.lbl_eta_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_total_eta") + ":")
        self.lbl_pct_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_req_power") + ":")
        self.lbl_uch_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_prelim_u") + ":")
        self.lbl_nsb_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_prelim_n") + ":")
        self.lbl_motor_name_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_motor_id") + ":")
        self.lbl_u_h_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_actual_uh") + ":")
        self.lbl_u2_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_u2") + ":")
        self.lbl_uch_real_row.parentWidget().layout().itemAt(0).widget().setText(_("lbl_actual_utotal") + ":")

        self.refresh()

    def _kv_row(self, layout, label_key: str) -> QLabel:
        row = QHBoxLayout()
        lbl = QLabel(_(label_key) + ":")
        lbl.setFixedWidth(240)
        lbl.setStyleSheet("color: #7F8C8D;")
        val = QLabel("—")
        val.setStyleSheet("font-weight: bold; color: #54A0FF;")
        row.addWidget(lbl)
        row.addWidget(val)
        row.addStretch()
        container = QWidget()
        container.setLayout(row)
        layout.addWidget(container)
        return val

    def _do_prelim(self):
        if not self.session.uc02_done:
            return
        p = self.session.inputs
        result = self.calc.calc_preliminary(p)
        m = self.session.motor
        m.eta = result.eta
        m.p_ct_kw = result.p_ct_kw
        m.u_ch_preliminary = result.u_ch_preliminary
        m.n_sb_rpm = result.n_sb_rpm

        self.lbl_eta_row.setText(f"{result.eta:.4f}")
        self.lbl_pct_row.setText(f"{result.p_ct_kw:.4f} kW")
        self.lbl_uch_row.setText(f"{result.u_ch_preliminary:.2f}")
        self.lbl_nsb_row.setText(f"{result.n_sb_rpm:.1f} {_('unit_rpm')}")

        self.filtered = self.calc.filter_motors(
            self.catalog, result.p_ct_kw, result.n_sb_rpm, tol_pct=15.0
        )
        self._fill_motor_table()
        if self.filtered:
            self.motor_table.selectRow(0)

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
        p = self.session.inputs
        result = self.session.motor
        result = self.calc.calc_after_motor_selected(p, result, m['rated_rpm'])
        result.motor_name = m['name']
        result.rated_power_kw = m['rated_power_kw']
        result.selected_motor_id = m['id']
        self.session.motor = result

        self.lbl_motor_name_row.setText(m['name'])
        self.lbl_u_h_row.setText(f"{result.u_h_actual:.4f}")
        self.lbl_u2_row.setText(f"{result.u2:.2f}")
        self.lbl_uch_real_row.setText(f"{result.u_ch_actual:.4f}")

        self._update_shaft_table(result)
        self.btn_confirm.setEnabled(True)

    def _update_shaft_table(self, m):
        self.shaft_table.clear_data()
        self.shaft_table.add_row([
            _("shaft_power"),
            f"{m.shaft_powers.get('dc', 0):.4f}",
            f"{m.shaft_powers.get('I', 0):.4f}",
            f"{m.shaft_powers.get('II', 0):.4f}",
            f"{m.shaft_powers.get('III', 0):.4f}",
        ])
        self.shaft_table.add_row([
            _("shaft_speed"),
            f"{m.shaft_rpms.get('dc', 0):.1f}",
            f"{m.shaft_rpms.get('I', 0):.2f}",
            f"{m.shaft_rpms.get('II', 0):.2f}",
            f"{m.shaft_rpms.get('III', 0):.2f}",
        ])
        self.shaft_table.add_row([
            _("shaft_torque"),
            f"{m.shaft_torques.get('dc', 0):.2f}",
            f"{m.shaft_torques.get('I', 0):.2f}",
            f"{m.shaft_torques.get('II', 0):.2f}",
            f"{m.shaft_torques.get('III', 0):.2f}",
        ])

    def _confirm(self):
        if not self._selected_motor:
            return
        self.session.uc03_done = True
        self.mw.on_step_completed(2)

    def refresh(self):
        m = self.session.motor
        if m.eta:
            self.lbl_eta_row.setText(f"{m.eta:.4f}")
            self.lbl_pct_row.setText(f"{m.p_ct_kw:.4f} kW")
            self.lbl_uch_row.setText(f"{m.u_ch_preliminary:.2f}")
            self.lbl_nsb_row.setText(f"{m.n_sb_rpm:.1f} {_('unit_rpm')}")
        if m.motor_name:
            self.lbl_motor_name_row.setText(m.motor_name)
            self.lbl_u_h_row.setText(f"{m.u_h_actual:.4f}")
            self.lbl_u2_row.setText(f"{m.u2:.2f}")
            self.lbl_uch_real_row.setText(f"{m.u_ch_actual:.4f}")
            self._update_shaft_table(m)
            self.btn_confirm.setEnabled(True)
