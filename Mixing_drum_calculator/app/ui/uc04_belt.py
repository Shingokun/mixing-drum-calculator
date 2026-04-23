from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QMessageBox, QFrame
from app.core import UC04Calculator

class UC04BeltPage(QWidget):
    def __init__(self, session, mw):
        super().__init__()
        self.session = session
        self.mw = mw
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(15)
        hdr = QLabel('Bước 3 · Tính toán Bộ Truyền Đai (UC-04)')
        hdr.setStyleSheet('font-size: 24px; font-weight: bold;')
        root.addWidget(hdr)

        desc = QLabel('Tính toán đường kính bánh đai, số lượng đai và khoảng cách trục.')
        desc.setStyleSheet('margin-bottom: 20px;')
        root.addWidget(desc)
        
        g_in = QGroupBox('📌 Thông số đầu vào')
        g_in_ly = QFormLayout(g_in)
        self.lbl_p1 = QLabel('-')
        self.lbl_n1 = QLabel('-')
        self.lbl_u = QLabel('-')
        g_in_ly.addRow('Công suất truyền (P_ct):', self.lbl_p1)
        g_in_ly.addRow('Tốc độ trục dẫn (n1_dc):', self.lbl_n1)
        g_in_ly.addRow('Tỉ số truyền đai (u_x):', self.lbl_u)
        root.addWidget(g_in)
        
        btn_calc = QPushButton('⚙️ Thực hiện Tính toán')
        btn_calc.setMinimumHeight(45)
        btn_calc.clicked.connect(self.calculate)
        root.addWidget(btn_calc)

        self.g_out = QGroupBox('📊 Kết quả Tính toán')
        self.g_out.setVisible(False)
        out_ly = QFormLayout(self.g_out)
        self.lbl_d1 = QLabel()
        self.lbl_d2 = QLabel()
        self.lbl_v = QLabel()
        self.lbl_L = QLabel()
        self.lbl_A = QLabel()
        self.lbl_z = QLabel()
        
        out_ly.addRow('Đường kính bánh dẫn (d1):', self.lbl_d1)
        out_ly.addRow('Đường kính bánh bị dẫn (d2):', self.lbl_d2)
        out_ly.addRow('Vận tốc đai (v):', self.lbl_v)
        out_ly.addRow('Chiều dài đai (L):', self.lbl_L)
        out_ly.addRow('Khoảng cách trục (A):', self.lbl_A)
        out_ly.addRow('Số lượng dây đai (z):', self.lbl_z)
        root.addWidget(self.g_out)

        root.addStretch()
        btn_next = QPushButton('Xác nhận && Tiếp tục →')
        btn_next.setMinimumHeight(45)
        btn_next.clicked.connect(self.on_verify)
        root.addWidget(btn_next)

    def showEvent(self, event):
        super().showEvent(event)
        motor = self.session.motor
        inp = self.session.inputs
        if motor.shaft_powers:
            p1 = motor.shaft_powers.get('dc', 0)
            n1 = motor.shaft_rpms.get('dc', 0)
            self.lbl_p1.setText(f"{p1} kW")
            self.lbl_n1.setText(f"{n1} vg/ph")
            self.lbl_u.setText(f"{inp.u_x}")
        else:
            self.lbl_p1.setText('-')

    def calculate(self):
        motor = self.session.motor
        inp = self.session.inputs
        if not motor.shaft_powers:
            QMessageBox.warning(self, 'Lỗi', 'Chưa có thông số từ động cơ. Xin vui lòng quay lại Bước 2 (UC-03).')
            return
            
        p1 = motor.shaft_powers.get('dc', 0)
        n1 = motor.shaft_rpms.get('dc', 0)
        u_x = inp.u_x
        
        res = UC04Calculator().calc(n1=n1, u_dai=u_x, P1_kw=p1, T1_Nmm=0)
        self.session.belt = res
        
        self.lbl_d1.setText(f"{res.d1_mm} mm")
        self.lbl_d2.setText(f"{res.d2_mm} mm")
        self.lbl_v.setText(f"{res.belt_velocity} m/s")
        self.lbl_L.setText(f"{res.belt_length_mm} mm")
        self.lbl_A.setText(f"{res.center_distance_mm} mm")
        self.lbl_z.setText(f"{res.num_belts} đai")
        
        self.g_out.setVisible(True)
        self.session.uc04_done = True
        
    def on_verify(self):
        if not self.g_out.isVisible():
            QMessageBox.warning(self, 'Cảnh báo', 'Vui lòng thực hiện tính toán...')
            return
        self.mw.on_step_completed(4)