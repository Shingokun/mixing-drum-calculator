import pytest
from app.core.uc05_calculator import UC05Calculator

def test_uc05_geometry():
    calc = UC05Calculator()
    # u1=3.45, T1=50000, sig_H=500
    geo = calc.calc_geometry(u1=3.45, T1_Nmm=50000.0, sig_H=500.0)
    
    assert geo["Re"] > 0
    assert geo["z1"] >= 16
    assert geo["z2"] > geo["z1"]
    assert geo["m_te"] in [1.5, 2.0, 2.5, 3.0, 4.0, 5.0] # một vài module chuẩn

def test_uc05_full_run():
    calc = UC05Calculator()
    res = calc.run(u1=3.45, n1=1450.0, T1_Nmm=50000.0)
    
    assert res.m_te > 0
    assert res.u_tt > 0
    assert res.Ft_N > 0
