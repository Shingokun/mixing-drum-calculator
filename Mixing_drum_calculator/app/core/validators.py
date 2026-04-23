# ============================================================
# validators.py
# ============================================================
from typing import Tuple


def validate_positive(value: str, field_name: str) -> Tuple[bool, str, float]:
    """Trả về (ok, message, parsed_value)"""
    try:
        v = float(value.replace(',', '.'))
        if v <= 0:
            return False, f"{field_name} phải > 0", 0.0
        return True, "", v
    except ValueError:
        return False, f"{field_name}: giá trị không hợp lệ", 0.0


def validate_efficiency(value: str, field_name: str) -> Tuple[bool, str, float]:
    ok, msg, v = validate_positive(value, field_name)
    if not ok:
        return ok, msg, v
    if not (0 < v <= 1):
        return False, f"{field_name} phải trong khoảng (0, 1]", 0.0
    return True, "", v


def validate_ratio(value: str, field_name: str, lo=1.0, hi=50.0) -> Tuple[bool, str, float]:
    ok, msg, v = validate_positive(value, field_name)
    if not ok:
        return ok, msg, v
    if not (lo <= v <= hi):
        return False, f"{field_name} phải trong khoảng [{lo}, {hi}]", 0.0
    return True, "", v