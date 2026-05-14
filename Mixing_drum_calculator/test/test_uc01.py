import pytest
import os
from app.core.session import ProjectSession, InputParams

def test_uc01_session_lifecycle(tmp_path):
    # Test khởi tạo session
    session = ProjectSession()
    assert session.uc02_done is False
    
    # Test lưu file
    test_file = tmp_path / "test_project.json"
    session.inputs.power_kw = 9.9
    session.save(str(test_file))
    assert os.path.exists(test_file)
    
    # Test load file
    new_session = ProjectSession.load(str(test_file))
    assert new_session.inputs.power_kw == 9.9
    assert new_session.filepath == str(test_file)

def test_uc01_reset():
    session = ProjectSession()
    session.uc02_done = True
    session.inputs.power_kw = 20.0
    session.reset()
    assert session.uc02_done is False
    assert session.inputs.power_kw == 6.5 # Giá trị mặc định
