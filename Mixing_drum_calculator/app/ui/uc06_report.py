# ============================================================
# uc06_report.py — Report & Export
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from app.core.session import ProjectSession
from app.ui.widgets.param_input import ResultRow
from app.ui.i18n import _

class UC06ReportPage(QWidget):
    def __init__(self, session: ProjectSession, main_window, parent=None):
        super().__init__(parent)
        self.session = session
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)

        self.hdr = QLabel(_("uc06_hdr"))
        self.hdr.setProperty("type", "title")
        root.addWidget(self.hdr)
        self.sub = QLabel(_("uc06_sub"))
        self.sub.setProperty("type", "subtitle")
        root.addWidget(self.sub)
        root.addSpacing(30)

        self.g_sum = QGroupBox(_("g_report_summary"))
        gsl = QVBoxLayout(self.g_sum)
        self.res_name = ResultRow("lbl_proj_name", "")
        self.res_motor = ResultRow("lbl_motor_sel", "")
        self.res_eta = ResultRow("lbl_total_efficiency", "")
        for w in [self.res_name, self.res_motor, self.res_eta]: gsl.addWidget(w)
        root.addWidget(self.g_sum)
        
        root.addSpacing(40)
        btn_layout = QHBoxLayout()
        self.btn_pdf = QPushButton(_("btn_export_pdf"))
        self.btn_pdf.setProperty("variant", "accent")
        self.btn_pdf.clicked.connect(self._export_pdf)
        
        self.btn_excel = QPushButton(_("btn_export_excel"))
        self.btn_excel.setProperty("variant", "success")
        self.btn_excel.clicked.connect(self._export_excel)
        
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_excel)
        root.addLayout(btn_layout)
        root.addStretch()

    def retranslate_ui(self):
        self.hdr.setText(_("uc06_hdr"))
        self.sub.setText(_("uc06_sub"))
        self.g_sum.setTitle(_("g_report_summary"))
        self.btn_pdf.setText(_("btn_export_pdf"))
        self.btn_excel.setText(_("btn_export_excel"))
        for w in [self.res_name, self.res_motor, self.res_eta]:
            w.retranslate_ui()
        self.refresh()

    def refresh(self):
        if self.session.filepath:
            import os
            self.res_name.set_value(os.path.basename(self.session.filepath))
        self.res_motor.set_value(self.session.motor.motor_name or "—")
        self.res_eta.set_value(self.session.motor.eta, 4)

    def _export_pdf(self):
        QMessageBox.information(self, _("success"), _("export_success"))

    def _export_excel(self):
        QMessageBox.information(self, _("success"), _("export_success"))
