def validate_positive_number(value_str: str, field_name: str) -> tuple[bool, str]:
    try:
        val = float(str(value_str).replace(',', '.'))
        if val <= 0:
            return False, f'Vui lòng nhập {field_name} dương hợp lệ.'
        return True, ''
    except ValueError:
        return False, f'Lỗi: {field_name} phải là số (không chứa chữ cái, ký tự đặc biệt).'

def validate_inputs(power_str: str, rpm_str: str, life_str: str) -> tuple[bool, dict]:
    errors = {}
    valid_p, msg_p = validate_positive_number(power_str, 'công suất')
    if not valid_p: errors['power_kw'] = msg_p
    
    valid_n, msg_n = validate_positive_number(rpm_str, 'số vòng quay')
    if not valid_n: errors['rpm_out'] = msg_n
    
    valid_l, msg_l = validate_positive_number(life_str, 'thời gian phục vụ')
    if not valid_l: errors['service_life_year'] = msg_l
    
    return len(errors) == 0, errors