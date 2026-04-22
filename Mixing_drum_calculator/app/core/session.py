from dataclasses import dataclass, field, asdict
from typing import Optional
import json

@dataclass
class InputParams:
    power_kw: float = 0.0        # P - Công suất yêu cầu
    rpm_out: float = 0.0          # n - Số vòng quay đầu ra
    service_life_year: float = 0.0  # L - Thời gian phục vụ
    # Hiệu suất
    eta_kn: float = 1.00          # Khớp nối
    eta_ol: float = 0.99          # Ổ lăn
    eta_brc: float = 0.96         # Bánh răng côn
    eta_brt: float = 0.97         # Bánh răng trụ
    eta_x: float = 0.91           # Xích (hoặc đai)
    # Tỉ số truyền sơ bộ
    u_h: float = 13.0             # Hộp giảm tốc
    u_x: float = 3.0              # Bộ truyền xích
    u1: float = 3.45              # Cấp nhanh

@dataclass
class MotorResult:
    selected_motor_id: Optional[str] = None
    motor_name: str = ""
    rated_power_kw: float = 0.0
    rated_rpm: float = 0.0
    # Kết quả phân bổ tỉ số truyền
    eta: float = 0.0
    p_ct: float = 0.0
    u_ch_actual: float = 0.0
    u2: float = 0.0
    # Bảng thông số trục
    shaft_powers: dict = field(default_factory=dict)
    shaft_rpms: dict = field(default_factory=dict)
    shaft_torques: dict = field(default_factory=dict)

@dataclass
class BeltResult:
    d1_mm: float = 0.0
    d2_mm: float = 0.0
    belt_velocity: float = 0.0
    belt_length_mm: float = 0.0
    num_belts: int = 0
    center_distance_mm: float = 0.0

@dataclass
class GearboxResult:
    # Bánh răng côn cấp nhanh
    re_mm: float = 0.0
    de1_mm: float = 0.0
    b_mm: float = 0.0
    m_te: float = 0.0
    z1: int = 0
    z2: int = 0
    sigma_h: float = 0.0
    sigma_f1: float = 0.0
    sigma_f2: float = 0.0
    strength_ok: bool = False

@dataclass
class ProjectSession:
    """Object duy nhất lưu toàn bộ trạng thái phiên làm việc"""
    inputs: InputParams = field(default_factory=InputParams)
    motor: MotorResult = field(default_factory=MotorResult)
    belt: BeltResult = field(default_factory=BeltResult)
    gearbox: GearboxResult = field(default_factory=GearboxResult)
    # Trạng thái wizard
    uc02_done: bool = False
    uc03_done: bool = False
    uc04_done: bool = False
    uc05_done: bool = False

    def save(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> 'ProjectSession':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Tái tạo nested dataclasses
        session = cls()
        session.inputs = InputParams(**data['inputs'])
        session.motor = MotorResult(**data['motor'])
        session.belt = BeltResult(**data['belt'])
        session.gearbox = GearboxResult(**data['gearbox'])
        session.uc02_done = data['uc02_done']
        session.uc03_done = data['uc03_done']
        session.uc04_done = data['uc04_done']
        session.uc05_done = data['uc05_done']
        return session