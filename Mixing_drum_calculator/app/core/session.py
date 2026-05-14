# ============================================================
# session.py — Central Data Model
# ============================================================
from pydantic import BaseModel, Field
from typing import Optional, Dict
import json, os


class InputParams(BaseModel):
    power_kw: float = Field(default=6.5, gt=0, description="Output power at work shaft (kW)")
    rpm_out: float = Field(default=75.0, gt=0, description="Output speed at work shaft (rpm)")
    service_life_year: float = Field(default=10.0, gt=0)
    eta_kn: float = Field(default=1.00, ge=0, le=1.0)
    eta_ol: float = Field(default=0.99, ge=0, le=1.0)
    eta_brc: float = Field(default=0.96, ge=0, le=1.0)
    eta_brt: float = Field(default=0.97, ge=0, le=1.0)
    eta_x: float = Field(default=0.91, ge=0, le=1.0)
    u_h: float = Field(default=13.0, gt=0)
    u_x: float = Field(default=3.0, gt=0)
    u1: float = Field(default=3.45, gt=0)


class MotorResult(BaseModel):
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
    shaft_powers: Dict[str, float] = Field(default_factory=dict)
    shaft_rpms: Dict[str, float] = Field(default_factory=dict)
    shaft_torques: Dict[str, float] = Field(default_factory=dict)


class BeltResult(BaseModel):
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


class ConeGearResult(BaseModel):
    # Allowable stress
    sig_H: float = 0.0
    sig_F1: float = 0.0
    sig_F2: float = 0.0
    # Geometry
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
    # Strength check
    sigma_F1_actual: float = 0.0
    sigma_F2_actual: float = 0.0
    F1_ok: bool = False
    F2_ok: bool = False
    # Forces
    Ft_N: float = 0.0
    Fr_N: float = 0.0
    Fa_N: float = 0.0


class GearboxResult(BaseModel):
    cone: ConeGearResult = Field(default_factory=ConeGearResult)
    strength_ok: bool = False


class ProjectSession(BaseModel):
    inputs: InputParams = Field(default_factory=InputParams)
    motor: MotorResult = Field(default_factory=MotorResult)
    belt: BeltResult = Field(default_factory=BeltResult)
    gearbox: GearboxResult = Field(default_factory=GearboxResult)
    uc02_done: bool = False
    uc03_done: bool = False
    uc04_done: bool = False
    uc05_done: bool = False
    filepath: str = ""

    def save(self, filepath: str):
        self.filepath = filepath
        data = self.model_dump()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> 'ProjectSession':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        s = cls(**data)
        s.filepath = filepath
        return s

    def reset(self):
        self.__init__()
        self.filepath = ""
