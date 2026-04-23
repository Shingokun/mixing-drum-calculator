from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QMessageBox, QFrame, QScrollArea
from app.core import UC05Calculator, GearboxResult

class UC05GearboxPage(QWidget):
    def __init__(self, session, mw):
        super().__init__()
        self.session = session
        self.mw = mw
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(15)

        hdr = QLabel('Bước 4 · Tính toán Hộp Giảm Tốc (Bánh răng Côn) UC-05')
        hdr.setStyleSheet('font-size: 24px; font-weight: bold;')
        root.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(15)

        # Đầu vào
        g_in = QGroupBox('📌 Thông số đầu vào (Từ Trục I)')
        g_in_ly = QFormLayout(g_in)
        self.lbl_n1 = QLabel('-')
        self.lbl_T1 = QLabel('-')
        self.lbl_u1 = QLabel('-')
        g_in_ly.addRow('Tốc độ N1 (vg/ph):', self.lbl_n1)
        g_in_ly.addRow('Momen T1 (N.mm):', self.lbl_T1)
        g_in_ly.addRow('Tỉ số truyền U1:', self.lbl_u1)
        cl.addWidget(g_in)

        btn_calc = QPushButton('⚙️ Thực hiện Tính toán Cấp Nhanh')
        btn_calc.setMinimumHeight(45)
        btn_calc.clicked.connect(self.calculate)
        cl.addWidget(btn_calc)

        # Kết quả
        self.g_out = QGroupBox('📊 Kết quả Hình học & Kiểm bền Uốn')
        self.g_out.setVisible(False)
        out_ly = QFormLayout(self.g_out)
        self.lbl_re = QLabel()
        self.lbl_de1 = QLabel()
        self.lbl_mte = QLabel()
        self.lbl_z1 = QLabel()
        self.lbl_z2 = QLabel()
        self.lbl_fail = QLabel()
        self.lbl_fail.setStyleSheet('color: red; font-weight: bold;')
        
        out_ly.addRow('Chiều dài côn ngoài (Re):', self.lbl_re)
        out_ly.addRow('Mô đun vòng ngoài (m_te):', self.lbl_mte)
        out_ly.addRow('Đường kính vành chia ngoài (de1):', self.lbl_de1)
        out_ly.addRow('Số răng bánh nhỏ (z1):', self.lbl_z1)
        out_ly.addRow('Số răng bánh lớn (z2):', self.lbl_z2)
        out_ly.addRow('', self.lbl_fail)
        cl.addWidget(self.g_out)
        
        scroll.setWidget(content)
        root.addWidget(scroll)

        btn_next = QPushButton('Hoàn thành && Lưu →')
        btn_next.setMinimumHeight(45)
        btn_next.clicked.connect(self.on_verify)
        root.addWidget(btn_next)

    def showEvent(self, event):
        super().showEvent(event)
        motor = self.session.motor
        inp = self.session.inputs
        if motor.shaft_torques:
            self.lbl_n1.setText(f"{motor.shaft_rpms.get('I', 0):.2f}")
            self.lbl_T1.setText(f"{motor.shaft_torques.get('I', 0):.2f}")
            self.lbl_u1.setText(f"{inp.u1}")

    def calculate(self):
        motor = self.session.motor
        inp = self.session.inputs
        if not motor.shaft_torques:
            QMessageBox.warning(self, 'Lỗi', 'Chưa có thông số Momen trục I.')
            return
            
        n1 = motor.shaft_rpms.get('I', 0)
        T1 = motor.shaft_torques.get('I', 0)
        u1 = inp.u1

        calc = UC05Calculator()
        res = calc.run(u1=u1, n1_rpm=n1, T1_Nmm=T1, L_h=inp.L_h)
        
        self.session.gearbox = res
        
        self.lbl_re.setText(f"{res.Re:.1f} mm")
        self.lbl_de1.setText(f"{res.de1:.1f} mm")
        self.lbl_mte.setText(f"{res.m_te}")
        self.lbl_z1.setText(f"{res.z1}")
        self.lbl_z2.setText(f"{res.z2}")
        
        if res.pass_strength:
            self.lbl_fail.setText(f"✓ Thỏa mãn điều kiện bền (σ_F1={res.sig_F1:.2f} <= {res.allowable_sig_F1:.2f})")
            self.lbl_fail.setStyleSheet('color: #27ae60; font-weight: bold;')
            self.session.uc05_done = True
        else:
            self.lbl_fail.setText(f"✕ KHÔNG thỏa mãn điều kiện bền (σ_F1={res.sig_F1:.2f} > {res.allowable_sig_F1:.2f})")
            self.lbl_fail.setStyleSheet('color: #c0392b; font-weight: bold;')
            self.session.uc05_done = False
            
        self.g_out.setVisible(True)

    def on_verify(self):
        if not self.g_out.isVisible():
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng thực hiện tính toán...')
            return
        if not self.session.uc05_done:
            msg = QMessageBox.question(self, 'Xác nhận Bỏ qua', 'Hộp giảm tốc chưa thỏa mãn điều kiện bền. Vẫn tiếp tục?', QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No: return
        self.mw.on_step_completed(5)
