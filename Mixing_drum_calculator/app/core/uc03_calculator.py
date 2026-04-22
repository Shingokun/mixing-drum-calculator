import math
from dataclasses import dataclass
from .session import InputParams, MotorResult

@dataclass
class UC03Result:
    eta: float
    p_ct_kw: float
    u_ch_preliminary: float
    n_sb_rpm: float
    # Sau khi chốt động cơ:
    u_ch_actual: float = 0.0
    u_h_actual: float = 0.0
    u2: float = 0.0
    shaft_powers: dict = None
    shaft_rpms: dict = None
    shaft_torques: dict = None

class UC03Calculator:
    def calc_efficiency(self, p: InputParams) -> float:
        """η = η_kn × η_ol^4 × η_brc × η_brt × η_x"""
        return round(
            p.eta_kn * (p.eta_ol ** 4) * p.eta_brc * p.eta_brt * p.eta_x,
            3
        )

    def calc_required_power(self, power_kw: float, eta: float) -> float:
        """P_ct = P / η"""
        return round(power_kw / eta, 3)

    def calc_preliminary(self, p: InputParams) -> UC03Result:
        eta = self.calc_efficiency(p)
        p_ct = self.calc_required_power(p.power_kw, eta)
        u_ch = p.u_h * p.u_x
        n_sb = round(p.rpm_out * u_ch, 2)
        return UC03Result(eta=eta, p_ct_kw=p_ct,
                          u_ch_preliminary=u_ch, n_sb_rpm=n_sb)

    def calc_after_motor_selected(self, p: InputParams, result: UC03Result,
                                   n_dc: float, p_dc_kw: float) -> UC03Result:
        """Tính lại sau khi người dùng chọn động cơ"""
        u_ch_actual = round(n_dc / p.rpm_out, 4)
        u_h_actual = round(u_ch_actual / p.u_x, 4)
        u2 = round(u_h_actual / p.u1, 2)

        # Bảng thông số trục
        p_out = p.power_kw
        p_x   = round(p_out / (p.eta_x * p.eta_ol), 4)
        p_brt = round(p_x   / (p.eta_brt * p.eta_ol), 4)
        p_brc = round(p_brt / (p.eta_brc * p.eta_ol), 4)
        p_ct  = round(p_brc / p.eta_ol, 4)

        n1 = n_dc  # u_kn = 1
        n2 = round(n1 / p.u1, 4)
        n3 = round(n2 / u2, 4)

        T_dc  = round(9.55e6 * (p_ct  / n_dc), 2)
        T_brc = round(9.55e6 * (p_brc / n_dc), 2)
        T_brt = round(9.55e6 * (p_brt / n2),   2)
        T_x   = round(9.55e6 * (p_x   / n3),   2)
        T_out = round(9.55e6 * (p_out  / p.rpm_out), 4)

        result.u_ch_actual = u_ch_actual
        result.u_h_actual  = u_h_actual
        result.u2          = u2
        result.shaft_powers  = {"dc": p_ct, "I": p_brc, "II": p_brt, "III": p_x}
        result.shaft_rpms    = {"dc": n_dc,  "I": n1,   "II": n2,    "III": n3}
        result.shaft_torques = {"dc": T_dc,  "I": T_brc,"II": T_brt, "III": T_x}
        return result

    def suggest_motors(self, catalog: list[dict], p_ct_kw: float, n_sb_rpm: float, tolerance: float = 0.1) -> list[dict]:
        """
        Lọc và gợi ý Top 3 động cơ từ catalog dựa trên thuật toán UC-06:
        1. P_dm >= P_ct
        2. Sai lệch tốc độ δ_n <= tolerance (VD: 10%)
        3. Ưu tiên (P_dm - P_ct) min -> Δn min
        """
        valid_motors = []
        for motor in catalog:
            if motor['rated_power_kw'] >= p_ct_kw:
                delta_rpm = abs(motor['rated_rpm'] - n_sb_rpm)
                delta_rpm_ratio = delta_rpm / n_sb_rpm
                if delta_rpm_ratio <= tolerance:
                    valid_motors.append({
                        **motor,
                        'surplus_power': motor['rated_power_kw'] - p_ct_kw,
                        'delta_rpm': delta_rpm,
                        'delta_rpm_ratio': delta_rpm_ratio
                    })
        
        # Sort by surplus_power (ascending), then delta_rpm (ascending)
        valid_motors.sort(key=lambda x: (x['surplus_power'], x['delta_rpm']))
        return valid_motors[:3]