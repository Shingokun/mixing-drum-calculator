# ============================================================
# uc03_calculator.py — Tính động cơ & phân bổ tỉ số truyền
# ============================================================
import math
from app.core.session import InputParams, MotorResult


class UC03Calculator:

    def calc_efficiency(self, p: InputParams) -> float:
        return round(
            p.eta_kn * (p.eta_ol ** 4) * p.eta_brc * p.eta_brt * p.eta_x, 3
        )

    def calc_preliminary(self, p: InputParams) -> MotorResult:
        eta = self.calc_efficiency(p)
        p_ct = round(p.power_kw / eta, 3)
        u_ch = p.u_h * p.u_x
        n_sb = round(p.rpm_out * u_ch, 2)
        r = MotorResult()
        r.eta = eta
        r.p_ct_kw = p_ct
        r.u_ch_preliminary = u_ch
        r.n_sb_rpm = n_sb
        return r

    def calc_after_motor_selected(self, p: InputParams, r: MotorResult,
                                   n_dc: float) -> MotorResult:
        r.rated_rpm = n_dc
        u_ch_actual = round(n_dc / p.rpm_out, 4)
        u_h_actual  = round(u_ch_actual / p.u_x, 4)
        u2          = round(u_h_actual / p.u1, 2)
        r.u_ch_actual = u_ch_actual
        r.u_h_actual  = u_h_actual
        r.u2          = u2

        p_out  = p.power_kw
        p_x    = round(p_out  / (p.eta_x   * p.eta_ol), 4)
        p_brt  = round(p_x    / (p.eta_brt * p.eta_ol), 4)
        p_brc  = round(p_brt  / (p.eta_brc * p.eta_ol), 4)
        p_ct   = round(p_brc  / p.eta_ol, 4)

        n1 = n_dc
        n2 = round(n1 / p.u1, 4)
        n3 = round(n2 / u2, 4)

        T_dc  = round(9.55e6 * (p_ct  / n_dc), 2)
        T_brc = round(9.55e6 * (p_brc / n1),   2)
        T_brt = round(9.55e6 * (p_brt / n2),   2)
        T_x   = round(9.55e6 * (p_x   / n3),   2)

        r.shaft_powers  = {"dc": p_ct,  "I": p_brc, "II": p_brt, "III": p_x}
        r.shaft_rpms    = {"dc": n_dc,  "I": n1,    "II": n2,    "III": n3}
        r.shaft_torques = {"dc": T_dc,  "I": T_brc, "II": T_brt, "III": T_x}
        return r

    def filter_motors(self, catalog: list, p_ct: float, n_sb: float,
                      tol_pct: float = 10.0) -> list:
        results = []
        for m in catalog:
            if m['rated_power_kw'] < p_ct:
                continue
            delta = abs(m['rated_rpm'] - n_sb)
            ratio = delta / n_sb * 100
            if ratio > tol_pct:
                continue
            m = dict(m)
            m['surplus_power'] = round(m['rated_power_kw'] - p_ct, 3)
            m['delta_rpm'] = round(delta, 1)
            m['delta_rpm_pct'] = round(ratio, 2)
            results.append(m)
        results.sort(key=lambda x: (x['surplus_power'], x['delta_rpm']))
        return results