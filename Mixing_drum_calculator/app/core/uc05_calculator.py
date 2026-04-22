import math
from dataclasses import dataclass

@dataclass
class ConeGearInput:
    u1: float          # Tỉ số truyền cấp nhanh
    n1_rpm: float      # Tốc độ trục I
    T1_Nmm: float      # Momen xoắn trục I
    HB1: float = 250   # Độ cứng bánh nhỏ
    HB2: float = 230   # Độ cứng bánh lớn
    S_H: float = 1.1
    S_F: float = 1.75
    K_d: float = 100
    psi_R: float = 0.255
    K_m: float = 1.13
    z1_sb: int = 16
    K_FC: float = 1.0
    L_h: float = 87600  # Giờ làm việc (10 năm * 365 * 24)

class UC05Calculator:
    def calc_allowable_stress(self, inp: ConeGearInput) -> dict:
        NHO1 = 30 * (inp.HB1 ** 2.4)
        NHO2 = 30 * (inp.HB2 ** 2.4)
        c = 1  # số lần ăn khớp mỗi vòng
        n2 = inp.n1_rpm / inp.u1
        NHE1 = NHE2 = 60 * inp.n1_rpm * c * inp.L_h  # simplified (=1)
        K_HL1 = K_HL2 = 1.0
        K_FL1 = K_FL2 = 1.0
        sig_Hlim1 = 2 * inp.HB1 + 70
        sig_Hlim2 = 2 * inp.HB2 + 70
        sig_Flim1 = 1.8 * inp.HB1
        sig_Flim2 = 1.8 * inp.HB2
        sig_H1 = sig_Hlim1 * K_HL1 / inp.S_H
        sig_H2 = sig_Hlim2 * K_HL2 / inp.S_H
        sig_H  = min(sig_H1, sig_H2)
        sig_F1 = sig_Flim1 * K_FL1 * inp.K_FC / inp.S_F
        sig_F2 = sig_Flim2 * K_FL2 * inp.K_FC / inp.S_F
        return {
            "sig_H1": round(sig_H1, 2), "sig_H2": round(sig_H2, 2),
            "sig_H": round(sig_H, 2),
            "sig_F1": round(sig_F1, 2), "sig_F2": round(sig_F2, 2)
        }

    def calc_geometry(self, inp: ConeGearInput, stress: dict) -> dict:
        K_R = 0.5 * inp.K_d
        u, T1, pR, Km = inp.u1, inp.T1_Nmm, inp.psi_R, inp.K_m
        sig_H = stress["sig_H"]

        # Chiều dài côn ngoài
        Re = K_R * math.sqrt(u**2 + 1) * ((T1 * Km) / ((1 - pR) * pR * u * sig_H**2)) ** (1/3)
        de1 = 2 * Re / math.sqrt(u**2 + 1)
        dm1 = (1 - 0.5 * pR) * de1

        # Chọn z1, z2
        z1 = math.floor(1.6 * inp.z1_sb)
        z2 = round(z1 * u)
        u_tt = z2 / z1
        delta_u = abs(u_tt - u) / u

        m_te_calc = dm1 / z1
        # Chọn mô đun tiêu chuẩn (bảng chuẩn VN)
        std_modules = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
        m_te = min((m for m in std_modules if m >= m_te_calc), default=std_modules[-1])

        Re2 = 0.5 * m_te * math.sqrt(z1**2 + z2**2)
        b   = round(pR * Re2, 2)
        Rm  = round(Re2 - 0.5 * b, 2)
        delta1 = math.atan(z1 / z2)
        delta2 = math.pi/2 - delta1

        return {
            "Re": round(Re2, 2), "de1": round(de1, 2),
            "dm1": round(dm1, 2), "m_te": m_te,
            "z1": z1, "z2": z2, "u_tt": round(u_tt, 4),
            "delta_u_pct": round(delta_u * 100, 2),
            "b": b, "Rm": Rm,
            "delta1_deg": round(math.degrees(delta1), 3),
            "delta2_deg": round(math.degrees(delta2), 3),
        }

    def check_bending_strength(self, inp: ConeGearInput,
                                geo: dict, stress: dict) -> dict:
        z1, z2 = geo["z1"], geo["z2"]
        d1, d2 = geo["delta1_deg"], geo["delta2_deg"]
        d1_r, d2_r = math.radians(d1), math.radians(d2)

        K_Fa, K_Fb, K_Fv = 1.0, 1.25, 1.0  # simplified
        K_F = K_Fa * K_Fb * K_Fv

        Y_eps = 1 / (1.88 - 3.2 * (1/z1 + 1/z2))
        zv1 = z1 / math.cos(d1_r)
        zv2 = z2 / math.cos(d2_r)
        Y_F1 = 3.47 + 13.2 / zv1
        Y_F2 = 3.47 + 13.2 / zv2

        b = geo["b"]
        m_te = geo["m_te"]
        h_e = 2.2 * m_te
        h_fe = h_e - m_te  # h_fe = h_e - h_ae; h_ae = m_te
        d_f1 = geo["de1"] - 2 * h_fe * math.cos(d1_r)

        Y_C = 1.0
        sig_F1 = (2 * inp.T1_Nmm * K_F * Y_eps * Y_C * Y_F1) / (0.85 * b * h_fe * d_f1)
        sig_F2 = sig_F1 * Y_F2 / Y_F1

        F_t = 2 * inp.T1_Nmm / d_f1
        F_r = F_t * math.tan(math.radians(20)) * math.cos(d1_r)
        F_a = F_t * math.tan(math.radians(20)) * math.sin(d1_r)

        return {
            "sig_F1": round(sig_F1, 2),
            "sig_F2": round(sig_F2, 2),
            "F_t": round(F_t, 2),
            "F_r": round(F_r, 2),
            "F_a": round(F_a, 2),
            "pass": sig_F1 <= stress["sig_F1"] and sig_F2 <= stress["sig_F2"]
        }

        Y_C = 1.0
        sig_F1 = (2 * inp.T1_Nmm * K_F * Y_eps * Y_C * Y_F1) / (0.85 * b * h_fe * d_f1)
        sig_F2 = sig_F1 * Y_F2 / Y_F1

        return {
            "sig_F1": round(sig_F1, 2),
            "sig_F2": round(sig_F2, 2),
            "allow_F1": stress["sig_F1"],
            "allow_F2": stress["sig_F2"],
            "F1_ok": sig_F1 <= stress["sig_F1"],
            "F2_ok": sig_F2 <= stress["sig_F2"],
        }