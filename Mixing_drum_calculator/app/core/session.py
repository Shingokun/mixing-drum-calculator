# ============================================================
# session.py — Data Model trung tâm của toàn bộ ứng dụng
# ============================================================
from dataclasses import dataclass, field, asdict
from typing import Optional
import json, os
 
 
@dataclass
class InputParams:
    power_kw: float = 6.5
    rpm_out: float = 75.0
    service_life_year: float = 10.0
    eta_kn: float = 1.00
    eta_ol: float = 0.99
    eta_brc: float = 0.96
    eta_brt: float = 0.97
    eta_x: float = 0.91
    u_h: float = 13.0
    u_x: float = 3.0
    u1: float = 3.45
 
 
@dataclass
class MotorResult:
    selected_motor_id: str = ""
    motor_name: str = ""
    rated_power_kw: float = 0.0
    rated_rpm: float = 0.0
    eta: float = 0.0
    p_ct_kw: float = 0.0
    u_ch_preliminary: float = 0.0
    n_sb_rpm: float = 0.0
    u_ch_actual: float = 0.0
    u_h_actual: float = 0.0
    u2: float = 0.0
    shaft_powers: dict = field(default_factory=dict)
    shaft_rpms: dict = field(default_factory=dict)
    shaft_torques: dict = field(default_factory=dict)
 
 
@dataclass
class BeltResult:
    d1_mm: float = 0.0
    d2_mm: float = 0.0
    belt_velocity_ms: float = 0.0
    center_distance_mm: float = 0.0
    belt_length_mm: float = 0.0
    num_belts: int = 0
    alpha1_deg: float = 0.0
    Ft_N: float = 0.0
    F0_N: float = 0.0
    velocity_ok: bool = True
 
 
@dataclass
class ConeGearResult:
    # Ứng suất cho phép
    sig_H: float = 0.0
    sig_F1: float = 0.0
    sig_F2: float = 0.0
    # Hình học
    Re_mm: float = 0.0
    de1_mm: float = 0.0
    dm1_mm: float = 0.0
    m_te: float = 0.0
    z1: int = 0
    z2: int = 0
    u_tt: float = 0.0
    delta_u_pct: float = 0.0
    b_mm: float = 0.0
    delta1_deg: float = 0.0
    delta2_deg: float = 0.0
    # Kiểm bền
    sigma_F1_actual: float = 0.0
    sigma_F2_actual: float = 0.0
    F1_ok: bool = False
    F2_ok: bool = False
    # Lực tác dụng
    Ft_N: float = 0.0
    Fr_N: float = 0.0
    Fa_N: float = 0.0
 
 
@dataclass
class GearboxResult:
    cone: ConeGearResult = field(default_factory=ConeGearResult)
    strength_ok: bool = False
 
 
@dataclass
class ProjectSession:
    inputs: InputParams = field(default_factory=InputParams)
    motor: MotorResult = field(default_factory=MotorResult)
    belt: BeltResult = field(default_factory=BeltResult)
    gearbox: GearboxResult = field(default_factory=GearboxResult)
    uc02_done: bool = False
    uc03_done: bool = False
    uc04_done: bool = False
    uc05_done: bool = False
    filepath: str = ""
 
    def save(self, filepath: str):
        self.filepath = filepath
        data = asdict(self)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
 
    @classmethod
    def load(cls, filepath: str) -> 'ProjectSession':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        s = cls()
        s.filepath = filepath
        s.inputs = InputParams(**data.get('inputs', {}))
        s.motor = MotorResult(**data.get('motor', {}))
        br = data.get('belt', {})
        s.belt = BeltResult(**br)
        gb = data.get('gearbox', {})
        cone_data = gb.pop('cone', {})
        s.gearbox = GearboxResult(cone=ConeGearResult(**cone_data), **gb)
        s.uc02_done = data.get('uc02_done', False)
        s.uc03_done = data.get('uc03_done', False)
        s.uc04_done = data.get('uc04_done', False)
        s.uc05_done = data.get('uc05_done', False)
        return s
 
    def reset(self):
        self.inputs = InputParams()
        self.motor = MotorResult()
        self.belt = BeltResult()
        self.gearbox = GearboxResult()
        self.uc02_done = False
        self.uc03_done = False
        self.uc04_done = False
        self.uc05_done = False
        self.filepath = ""
