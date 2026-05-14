import pytest
from pydantic import ValidationError
from app.core.session import InputParams

def test_uc02_validation_success():
    # Nhập đúng thông số
    p = InputParams(power_kw=5.0, rpm_out=100.0, eta_ol=0.98)
    assert p.power_kw == 5.0
    assert p.eta_ol == 0.98

def test_uc02_validation_error():
    # Test công suất âm
    with pytest.raises(ValidationError):
        InputParams(power_kw=-1.0)
    
    # Test hiệu suất > 1
    with pytest.raises(ValidationError):
        InputParams(eta_kn=1.5)

def test_uc02_default_values():
    p = InputParams()
    assert p.u_h == 13.0
    assert p.u_x == 3.0
