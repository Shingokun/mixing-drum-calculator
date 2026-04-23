# ============================================================
# constants.py — Hằng số cơ học dùng trong toàn hệ thống
# ============================================================

# Mô đun tiêu chuẩn (mm) – dãy ưu tiên theo TCVN
STANDARD_MODULES = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20]

# Đường kính bánh đai tiêu chuẩn (mm)
STANDARD_PULLEY_DIAMETERS = [
    63, 71, 80, 90, 100, 112, 125, 140, 160, 180,
    200, 224, 250, 280, 315, 355, 400, 450, 500,
    560, 630, 710, 800, 900, 1000
]

# Chiều dài đai thang tiêu chuẩn (mm) – loại B
STANDARD_BELT_LENGTHS = [
    800, 900, 1000, 1120, 1250, 1400, 1600, 1800, 2000,
    2240, 2500, 2800, 3150, 3550, 4000, 4500, 5000, 5600, 6300
]

# Hệ số dạng răng Y_F (tra theo số răng tương đương z_v)
# (z_v, Y_F)
YF_TABLE = [
    (17, 4.25), (19, 4.07), (20, 4.01), (21, 3.96),
    (22, 3.92), (24, 3.85), (25, 3.83), (26, 3.80),
    (28, 3.76), (30, 3.73), (32, 3.70), (35, 3.67),
    (37, 3.66), (40, 3.63), (42, 3.61), (45, 3.61),
    (50, 3.58), (60, 3.55), (70, 3.53), (80, 3.52),
    (90, 3.51), (100, 3.50),
]

# Vận tốc đai cho phép tối đa (m/s)
MAX_BELT_VELOCITY = 25.0

# Hệ số chiều rộng vành răng mặc định
DEFAULT_PSI_R = 0.255

# Góc áp lực tiêu chuẩn (độ)
PRESSURE_ANGLE_DEG = 20.0

# Số giờ/năm làm việc (mặc định 1 ca/ngày)
HOURS_PER_YEAR = 8760  # 365 * 24 (full); hoặc 2000 (1 ca)

# Loại đai thang B – thông số tiết diện
BELT_B_PARAMS = {
    "type": "B",
    "bp": 14.0,   # chiều rộng trên (mm)
    "b":  10.0,   # chiều rộng đáy (mm)
    "h":  10.5,   # chiều cao (mm)
    "y0": 4.0,    # khoảng cách từ đáy đến trọng tâm (mm)
    "A":  138.0,  # diện tích tiết diện (mm²)
    "d1_min": 125, # đường kính bánh đai nhỏ tối thiểu (mm)
}

# ============================================================
# Bảng lựa chọn tiết diện đai theo công suất và tốc độ
# (P_ct, n_sb) → loại đai
# Simplified: mọi trường hợp đồ án này dùng đai loại B
# ============================================================
BELT_SECTION = "B"