import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt
from app.core import ProjectSession

class UC06ReportPage(QWidget):
    def __init__(self, session: ProjectSession, mw):
        super().__init__()
        self.session = session
        self.mw = mw
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(15)

        hdr = QLabel('Bước 5 · Tổng hợp & Báo cáo (UC-06)')
        hdr.setStyleSheet('font-size: 24px; font-weight: bold;')
        root.addWidget(hdr)

        desc = QLabel('Xem lại bảng động học, in kết quả ra màn hình.')
        root.addWidget(desc)

        # Table hiển thị
        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(['Trục Động Cơ', 'Trục I', 'Trục II', 'Trục III'])
        self.table.setVerticalHeaderLabels(['Tỉ số truyền (u)', 'Công suất P (kW)', 'Tốc độ n (vg/ph)', 'Momen xoắn T (N.mm)'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        root.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_refresh = QPushButton('🔄 Tải Lại Bảng')
        btn_refresh.clicked.connect(self.load_data)
        
        btn_pdf = QPushButton('📄 Xuất PDF Thuyết Minh')
        btn_pdf.clicked.connect(self.export_pdf)
        btn_pdf.setStyleSheet('background-color: #c0392b; color: white;')

        btn_row.addWidget(btn_refresh)
        btn_row.addWidget(btn_pdf)
        root.addLayout(btn_row)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def load_data(self):
        motor = self.session.motor
        inp = self.session.inputs

        if not motor.shaft_powers:
            return

        def _set(row, col, val):
            item = QTableWidgetItem(f"{val}")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, item)

        idx_map = {'dc': 0, 'I': 1, 'II': 2, 'III': 3}
        
        # Tỉ số truyền
        u = [motor.u_ch_actual, 1.0, inp.u1, motor.u2]
        for i, v in enumerate(u): _set(0, i, round(v, 4))
        
        # Công suất
        for k, v in motor.shaft_powers.items(): _set(1, idx_map[k], round(v, 4))
        # Tốc độ
        for k, v in motor.shaft_rpms.items(): _set(2, idx_map[k], round(v, 4))
        # Momen xoắn
        for k, v in motor.shaft_torques.items(): _set(3, idx_map[k], round(v, 4))

    def export_pdf(self):
        QMessageBox.information(self, 'Thông báo', 'Tính năng xuất PDF đang được phát triển.')
