import pytest
from app.core.uc03_calculator import UC03Calculator
from app.core.session import InputParams, MotorResult

def test_calc_efficiency():
    calc = UC03Calculator()
    p = InputParams()
    # Mặc định: eta_kn=1.0, eta_ol=0.99, eta_brc=0.96, eta_brt=0.97, eta_x=0.91
    # Efficiency = 1.0 * (0.99^4) * 0.96 * 0.97 * 0.91 = 0.8126...
    expected = round(1.0 * (0.99**4) * 0.96 * 0.97 * 0.91, 3)
    assert calc.calc_efficiency(p) == expected

def test_calc_preliminary():
    calc = UC03Calculator()
    p = InputParams(power_kw=10.0, rpm_out=50.0, u_h=10.0, u_x=3.0)
    res = calc.calc_preliminary(p)
    
    # eta ~ 0.813
    # p_ct = 10.0 / 0.813 = 12.3
    assert res.p_ct_kw > 12.0
    assert res.u_ch_preliminary == 30.0
    assert res.n_sb_rpm == 1500.0

def test_filter_motors():
    calc = UC03Calculator()
    catalog = [
        {"id": "M1", "name": "Motor 1", "rated_power_kw": 11.0, "rated_rpm": 1450},
        {"id": "M2", "name": "Motor 2", "rated_power_kw": 15.0, "rated_rpm": 1460},
        {"id": "M3", "name": "Motor 3", "rated_power_kw": 7.5,  "rated_rpm": 1440},
    ]
    # Yêu cầu p_ct = 12.0, n_sb = 1500
    filtered = calc.filter_motors(catalog, p_ct=12.0, n_sb=1500.0, tol_pct=10.0)
    
    assert len(filtered) == 1
    assert filtered[0]['id'] == "M2" # Chỉ M2 có power >= 12.0 và rpm trong dải [1350, 1650]
