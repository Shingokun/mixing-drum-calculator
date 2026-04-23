# ============================================================
# uc04_calculator.py — Tính bộ truyền đai thang loại B
# ============================================================
import math
from app.core.session import BeltResult
from app.data.constants import (
    STANDARD_PULLEY_DIAMETERS, STANDARD_BELT_LENGTHS,
    BELT_B_PARAMS, MAX_BELT_VELOCITY
)


class UC04Calculator:

    def _next_std(self, val: float, lst: list) -> float:
        """Chọn giá trị tiêu chuẩn nhỏ nhất >= val"""
        for v in sorted(lst):
            if v >= val:
                return float(v)
        return float(lst[-1])

    def calc(self, n1: float, u_dai: float, P1_kw: float, T1_Nmm: float) -> BeltResult:
        """
        n1      : Tốc độ trục dẫn (vg/ph)
        u_dai   : Tỉ số truyền đai (thường = u_x)
        P1_kw   : Công suất trục I (kW)
        T1_Nmm  : Momen trục I (N.mm)
        """
        r = BeltResult()
        bp = BELT_B_PARAMS

        # Bước 1: Chọn d1 (đường kính bánh đai nhỏ)
        d1_min = bp['d1_min']
        d1 = self._next_std(d1_min, STANDARD_PULLEY_DIAMETERS)
        r.d1_mm = d1

        # Bước 2: Tính d2
        eps = 0.01  # hệ số trượt
        d2_calc = d1 * u_dai * (1 - eps)
        d2 = self._next_std(d2_calc, STANDARD_PULLEY_DIAMETERS)
        r.d2_mm = d2

        # Vận tốc đai
        v = math.pi * d1 * n1 / 60000  # m/s
        r.belt_velocity_ms = round(v, 3)
        r.velocity_ok = v <= MAX_BELT_VELOCITY

        # Khoảng cách trục sơ bộ
        a_min = 0.55 * (d1 + d2) + bp['h']
        a_max = 2 * (d1 + d2)
        a = max(a_min, min(a_max, d1 + d2))  # chọn trung bình

        # Chiều dài đai
        L_calc = 2 * a + math.pi * (d1 + d2) / 2 + (d2 - d1) ** 2 / (4 * a)
        L = self._next_std(L_calc, STANDARD_BELT_LENGTHS)
        r.belt_length_mm = L

        # Tính lại khoảng cách trục theo L chuẩn
        k = (d2 - d1) / 2
        discriminant = (L - math.pi * (d1 + d2) / 2) ** 2 / 4 - 2 * k ** 2
        if discriminant < 0:
            discriminant = 0
        a_real = (L - math.pi * (d1 + d2) / 2 + math.sqrt(discriminant)) / 4
        # Công thức chính xác hơn:
        tmp = L - math.pi * (d1 + d2) / 2
        a_real = (tmp + math.sqrt(tmp ** 2 - 8 * (d2 - d1) ** 2)) / 8
        r.center_distance_mm = round(a_real, 1)

        # Góc ôm trên bánh nhỏ
        alpha1 = 180 - 57.3 * (d2 - d1) / a_real
        r.alpha1_deg = round(alpha1, 2)

        # Số dây đai
        # Hệ số ảnh hưởng:
        C_alpha = 1 - 0.003 * (180 - alpha1)   # hệ số ảnh hưởng góc ôm
        C_L     = (L / 1700) ** 0.09            # hệ số chiều dài (ref 1700 mm)
        C_u     = 1.14 if u_dai >= 3 else 1.0  # hệ số tỉ số truyền
        C_z     = 0.95                          # hệ số số dây (giả định trước)

        # Công suất cho phép của 1 dây đai P0 (kW) – tra bảng hoặc công thức
        # Đơn giản hóa: P0 dựa theo v
        P0 = 1.0 + 0.12 * v - 0.001 * v**2  # ước lượng cho đai B tại d1=125mm

        # Số dây đai
        K_d = 1.1  # hệ số tải – tải vừa
        z_calc = (P1_kw * K_d) / (P0 * C_alpha * C_L * C_u * C_z)
        z = math.ceil(z_calc)
        if z < 1:
            z = 1
        r.num_belts = z

        # Lực vòng và lực căng
        Ft = P1_kw * 1000 / v  # N
        F0 = 780 * Ft / (z * v) + bp['A'] * v ** 2 / 1000
        r.Ft_N = round(Ft, 1)
        r.F0_N = round(F0, 1)

        return r
