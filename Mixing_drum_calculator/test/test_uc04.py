import pytest
from app.core.uc04_calculator import UC04Calculator

def test_uc04_calc_basic():
    calc = UC04Calculator()
    # Giả định n1=1450, u=3, P1=5.0, T1=33000
    res = calc.calc(n1=1450.0, u_dai=3.0, P1_kw=5.0, T1_Nmm=33000.0)
    
    assert res.d1_mm >= 125 # d1_min cho đai B là 125
    assert res.d2_mm > res.d1_mm
    assert res.belt_velocity_ms > 0
    assert res.num_belts >= 1
    assert res.velocity_ok is True
