import math
from dataclasses import dataclass
from .session import BeltResult

@dataclass
class BeltInput:
    power_kw: float       # P1 (kW)
    n1_rpm: float         # Số vòng quay trục bánh dẫn (vòng/phút)
    u: float              # Tỉ số truyền đai
    slip_factor: float = 0.015  # Hệ số trượt epsilon (0.01 - 0.02)

class UC04Calculator:
    def calculate_belt(self, inp: BeltInput) -> BeltResult:
        # Đường kính bánh đai nhỏ dựa theo công thức thực nghiệm: (1.2..2)*Cbr(T1)
        # Hoặc lấy công suất định hướng
        # Chọn sơ bộ d1 (mm). Dùng công thức d1 = 5.2 * sqrt[3]{P1 / n1} * 100 (tuỳ chuẩn),
        # Ở đây ta dùng công thức cơ bản d1 = 100...200. Ta lấy d1 theo chuẩn đơn giản:
        d1_suggested = 1.2 * (inp.power_kw * 1000 / inp.n1_rpm) ** 0.33 * 50
        # Chọn d1 theo tiêu chuẩn (ví dụ 140, 160, 180, 200...)
        std_d1 = [100, 112, 125, 140, 160, 180, 200, 224, 250, 280, 315]
        d1 = min((d for d in std_d1 if d >= d1_suggested), default=std_d1[-1])

        # Vận tốc đai (m/s)
        v = (math.pi * d1 * inp.n1_rpm) / 60000

        # Đường kính bánh đai lớn d2
        d2_calc = inp.u * d1 * (1 - inp.slip_factor)
        std_d2 = [400, 450, 500, 560, 630, 710, 800, 900, 1000]
        d2 = min((d for d in std_d2 if d >= d2_calc), default=std_d2[-1])

        # Khoảng cách trục A sơ bộ: 0.55(d1+d2) + h <= A <= 2(d1+d2)
        center_distance_pre = 1.0 * (d1 + d2)

        # Chiều dài đai L sơ bộ
        l_pre = 2 * center_distance_pre + math.pi * (d1 + d2) / 2 + ((d2 - d1) ** 2) / (4 * center_distance_pre)
        
        # Chọn chiều dài đai tiêu chuẩn
        std_L = [1000, 1120, 1250, 1400, 1600, 1800, 2000, 2240, 2500, 2800, 3150]
        l_actual = min((l_ for l_ in std_L if l_ >= l_pre), default=std_L[-1])

        # Tính lại khoảng cách trục A
        k = l_actual - math.pi * (d1 + d2) / 2
        center_distance_actual = (k + math.sqrt(max(0, k**2 - 8 * ((d2 - d1)/2)**2))) / 4

        # Số dây đai (z)
        # Giả định công suất cho phép 1 dây đai [P0] khoảng 2.0 kW (tuỳ đai loại A, B...)
        p0 = 2.0
        c_alpha = 1 - 0.003 * (180 - math.degrees(math.acos((d2 - d1) / center_distance_actual)))  if center_distance_actual > (d2-d1) else 0.8
        c_l = 1.0
        c_u = 1.0
        c_z = 0.95
        
        num_belts_calc = inp.power_kw / (p0 * c_alpha * c_l * c_u * c_z)
        num_belts = math.ceil(num_belts_calc)

        return BeltResult(
            d1_mm=round(d1, 2),
            d2_mm=round(d2, 2),
            belt_velocity=round(v, 2),
            belt_length_mm=round(l_actual, 2),
            num_belts=max(1, num_belts),
            center_distance_mm=round(center_distance_actual, 2)
        )
