# ============================================================
# uc06_report.py — Report & Export
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame, QMessageBox, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt
from app.core.session import ProjectSession
from app.ui.widgets.param_input import ResultRow
from app.ui.i18n import _, tr
from app.export.pdf_exporter import export_pdf
from app.export.excel_exporter import export_excel

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
        self.lbl_output_name = QLabel(_("lbl_output_name"))
        self.inp_output_name = QLineEdit()
        self.inp_output_name.setPlaceholderText(_("ph_output_name"))
        self.res_motor = ResultRow("lbl_motor_sel", "")
        self.res_eta = ResultRow("lbl_total_efficiency", "")
        gsl.addWidget(self.res_name)
        gsl.addWidget(self.lbl_output_name)
        gsl.addWidget(self.inp_output_name)
        for w in [self.res_motor, self.res_eta]:
            gsl.addWidget(w)
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
        self.lbl_output_name.setText(_("lbl_output_name"))
        self.inp_output_name.setPlaceholderText(_("ph_output_name"))
        self.btn_pdf.setText(_("btn_export_pdf"))
        self.btn_excel.setText(_("btn_export_excel"))
        for w in [self.res_name, self.res_motor, self.res_eta]:
            w.retranslate_ui()
        self.refresh()

    def refresh(self):
        import os

        if self.session.filepath:
            base_name = os.path.basename(self.session.filepath)
            self.res_name.set_value(base_name)
            if not self.inp_output_name.text().strip():
                self.inp_output_name.setText(os.path.splitext(base_name)[0])
        else:
            self.res_name.set_value("—")
        self.res_motor.set_value(self.session.motor.motor_name or "—")
        self.res_eta.set_value(self.session.motor.eta, 4)

    def _build_default_name(self, extension: str) -> str:
        base = self.inp_output_name.text().strip()
        if not base:
            base = "Design_Report" if extension == "pdf" else "Calculation_Data"
        ext = f".{extension}"
        if not base.lower().endswith(ext):
            base += ext
        return base

    def _export_pdf(self):
        default_name = self._build_default_name("pdf")
        path, _selected_filter = QFileDialog.getSaveFileName(
            self, _("btn_export_pdf"), default_name, "PDF Files (*.pdf)"
        )
        if not path:
            return
        try:
            export_pdf(self.session, path, lang=tr.get_lang())
            QMessageBox.information(self, _("success"), _("export_success") + f"\n{path}")
        except Exception as e:
            import traceback, os
            tb = traceback.format_exc()
            # write to log so user can attach it
            try:
                logpath = os.path.join(os.getcwd(), 'pdf_export_error.log')
                with open(logpath, 'a', encoding='utf-8') as f:
                    f.write(tb + '\n')
            except Exception:
                pass
            QMessageBox.critical(self, _("error"), f"Failed to export PDF:\n{e}\n\nFull traceback was written to: {logpath if 'logpath' in locals() else 'N/A'}\n\n{tb}")

    def _export_excel(self):
        default_name = self._build_default_name("xlsx")
        path, _selected_filter = QFileDialog.getSaveFileName(
            self, _("btn_export_excel"), default_name, "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            export_excel(self.session, path)
            QMessageBox.information(self, _("success"), _("export_success") + f"\n{path}")
        except Exception as e:
            import traceback, os
            tb = traceback.format_exc()
            try:
                logpath = os.path.join(os.getcwd(), 'excel_export_error.log')
                with open(logpath, 'a', encoding='utf-8') as f:
                    f.write(tb + '\n')
            except Exception:
                pass
            QMessageBox.critical(self, _("error"), f"Failed to export Excel:\n{e}\n\nFull traceback was written to: {logpath if 'logpath' in locals() else 'N/A'}\n\n{tb}")
