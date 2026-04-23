# ============================================================
# uc05_calculator.py — Tính bánh răng côn cấp nhanh
# ============================================================
import math
from app.core.session import ConeGearResult
from app.data.constants import STANDARD_MODULES


class UC05Calculator:

    def _pick_std_module(self, m_calc: float) -> float:
        for m in sorted(STANDARD_MODULES):
            if m >= m_calc:
                return float(m)
        return float(STANDARD_MODULES[-1])

    # ------------------------------------------------------------------ #
    #  Ứng suất cho phép
    # ------------------------------------------------------------------ #
    def calc_allowable_stress(self, HB1: float, HB2: float,
                               S_H: float, S_F: float,
                               K_FC: float = 1.0) -> dict:
        sig_Hlim1 = 2 * HB1 + 70
        sig_Hlim2 = 2 * HB2 + 70
        sig_Flim1 = 1.8 * HB1
        sig_Flim2 = 1.8 * HB2
        K_HL = K_FL = 1.0          # tuổi thọ lớn → K=1
        sig_H1 = sig_Hlim1 * K_HL / S_H
        sig_H2 = sig_Hlim2 * K_HL / S_H
        sig_H  = min(sig_H1, sig_H2)
        sig_F1 = sig_Flim1 * K_FL * K_FC / S_F
        sig_F2 = sig_Flim2 * K_FL * K_FC / S_F
        return {
            "sig_H1": round(sig_H1, 2), "sig_H2": round(sig_H2, 2),
            "sig_H":  round(sig_H,  2),
            "sig_F1": round(sig_F1, 2), "sig_F2": round(sig_F2, 2),
        }

    # ------------------------------------------------------------------ #
    #  Hình học
    # ------------------------------------------------------------------ #
    def calc_geometry(self, u1: float, T1_Nmm: float, sig_H: float,
                       K_d: float = 100, psi_R: float = 0.255,
                       K_m: float = 1.13, z1_sb: int = 16) -> dict:
        K_R = 0.5 * K_d
        Re = K_R * math.sqrt(u1**2 + 1) * (
            (T1_Nmm * K_m) / ((1 - psi_R) * psi_R * u1 * sig_H**2)
        ) ** (1/3)

        de1 = 2 * Re / math.sqrt(u1**2 + 1)
        dm1 = (1 - 0.5 * psi_R) * de1

        z1 = math.floor(1.6 * z1_sb)
        z2 = round(z1 * u1)
        u_tt = z2 / z1
        delta_u = abs(u_tt - u1) / u1

        m_te_calc = dm1 / z1
        m_te = self._pick_std_module(m_te_calc)

        Re2 = 0.5 * m_te * math.sqrt(z1**2 + z2**2)
        b   = psi_R * Re2
        Rm  = Re2 - 0.5 * b

        delta1 = math.atan(z1 / z2)
        delta2 = math.pi / 2 - delta1

        h_e  = 2.2 * m_te
        h_ae = m_te
        h_fe = h_e - h_ae
        de2  = m_te * z2

        return {
            "Re": round(Re2, 2), "de1": round(de1, 2), "de2": round(de2, 2),
            "dm1": round(dm1, 2), "m_te": m_te, "m_te_calc": round(m_te_calc, 3),
            "z1": z1, "z2": z2, "u_tt": round(u_tt, 4),
            "delta_u_pct": round(delta_u * 100, 2),
            "b": round(b, 2), "Rm": round(Rm, 2),
            "h_e": round(h_e, 3), "h_fe": round(h_fe, 3), "h_ae": h_ae,
            "delta1_deg": round(math.degrees(delta1), 3),
            "delta2_deg": round(math.degrees(delta2), 3),
        }

    # ------------------------------------------------------------------ #
    #  Kiểm bền uốn
    # ------------------------------------------------------------------ #
    def check_bending(self, T1_Nmm: float, geo: dict,
                       sig_F1_allow: float, sig_F2_allow: float) -> dict:
        z1, z2 = geo["z1"], geo["z2"]
        d1r = math.radians(geo["delta1_deg"])
        d2r = math.radians(geo["delta2_deg"])
        b   = geo["b"]
        m_te= geo["m_te"]
        h_fe= geo["h_fe"]

        K_Fa = 1.0; K_Fb = 1.25; K_Fv = 1.0
        K_F  = K_Fa * K_Fb * K_Fv

        Y_eps = 1 / (1.88 - 3.2 * (1/z1 + 1/z2))
        zv1 = z1 / math.cos(d1r)
        zv2 = z2 / math.cos(d2r)
        Y_F1 = 3.47 + 13.2 / zv1
        Y_F2 = 3.47 + 13.2 / zv2

        de1 = geo["de1"]
        d_f1 = de1 - 2 * h_fe * math.cos(d1r)

        Y_C = 1.0
        sig_F1 = (2 * T1_Nmm * K_F * Y_eps * Y_C * Y_F1) / (0.85 * b * h_fe * d_f1)
        sig_F2 = sig_F1 * Y_F2 / Y_F1

        return {
            "sig_F1": round(sig_F1, 2), "sig_F2": round(sig_F2, 2),
            "allow_F1": sig_F1_allow,   "allow_F2": sig_F2_allow,
            "F1_ok": sig_F1 <= sig_F1_allow,
            "F2_ok": sig_F2 <= sig_F2_allow,
            "K_F": K_F, "Y_eps": round(Y_eps, 4),
            "Y_F1": round(Y_F1, 3), "Y_F2": round(Y_F2, 3),
            "d_f1": round(d_f1, 2),
        }

    # ------------------------------------------------------------------ #
    #  Lực tác dụng
    # ------------------------------------------------------------------ #
    def calc_forces(self, T1_Nmm: float, geo: dict) -> dict:
        d_m1 = geo["dm1"]
        d1r  = math.radians(geo["delta1_deg"])
        Ft = 2 * T1_Nmm / d_m1
        Fr = Ft * math.tan(math.radians(20)) * math.cos(d1r)
        Fa = Ft * math.tan(math.radians(20)) * math.sin(d1r)
        return {
            "Ft": round(Ft, 1),
            "Fr": round(Fr, 1),
            "Fa": round(Fa, 1),
        }

    # ------------------------------------------------------------------ #
    #  Hàm tổng hợp
    # ------------------------------------------------------------------ #
    def run(self, u1: float, n1: float, T1_Nmm: float,
            HB1: float = 250, HB2: float = 230,
            S_H: float = 1.1, S_F: float = 1.75,
            K_FC: float = 1.0) -> ConeGearResult:
        stress = self.calc_allowable_stress(HB1, HB2, S_H, S_F, K_FC)
        geo    = self.calc_geometry(u1, T1_Nmm, stress["sig_H"])
        bend   = self.check_bending(T1_Nmm, geo, stress["sig_F1"], stress["sig_F2"])
        forces = self.calc_forces(T1_Nmm, geo)

        r = ConeGearResult()
        r.sig_H  = stress["sig_H"]
        r.sig_F1 = stress["sig_F1"]
        r.sig_F2 = stress["sig_F2"]
        r.Re_mm  = geo["Re"]
        r.de1_mm = geo["de1"]
        r.dm1_mm = geo["dm1"]
        r.m_te   = geo["m_te"]
        r.z1 = geo["z1"]; r.z2 = geo["z2"]
        r.u_tt = geo["u_tt"]
        r.delta_u_pct = geo["delta_u_pct"]
        r.b_mm   = geo["b"]
        r.delta1_deg = geo["delta1_deg"]
        r.delta2_deg = geo["delta2_deg"]
        r.sigma_F1_actual = bend["sig_F1"]
        r.sigma_F2_actual = bend["sig_F2"]
        r.F1_ok = bend["F1_ok"]
        r.F2_ok = bend["F2_ok"]
        r.Ft_N = forces["Ft"]
        r.Fr_N = forces["Fr"]
        r.Fa_N = forces["Fa"]
        return r