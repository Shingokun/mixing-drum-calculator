# ============================================================
# i18n.py — Internationalization (Localization)
# ============================================================

TRANSLATIONS = {
    "en": {
        # General & Nav
        "app_title": "Mixing Drum Drive System Calculator",
        "nav_uc01": "Project Management",
        "nav_uc02": "Input Parameters",
        "nav_uc03": "Motor Selection",
        "nav_uc04": "Belt Drive",
        "nav_uc05": "Gearbox Design",
        "nav_uc06": "Export Report",
        "incomplete_step": "Incomplete Step",
        "incomplete_msg": "Please complete the previous step before continuing.",
        "save_project": "Save Project",
        "exit_app": "Exit Application",
        "exit_save_msg": "Do you want to save your project before exiting?",
        "saved_success": "Saved!",
        "lang_toggle": "Tiếng Việt",
        "brand": "  ⚙ Drive Calculator ",
        "new_project": "New Project",
        "open_project": "Open Project",
        "project_status": "Current Project Status",
        "no_project": "No project opened.",
        "step_completed": "Completed {done}/4 steps.",
        "new_project_msg": "Creating a new project will clear all current data. Continue?",
        "confirm": "Confirm",
        "confirm_next": "Confirm and Continue  →",
        "success": "Success",
        "error": "Error",
        "load_success": "Project loaded successfully!",
        "invalid_file": "Invalid file format:",
        "no_data": "No data to save.",
        "hcmut": "HCMUT - CO3111",
        "group_info": "CO3111 Multidisciplinary Project · HCMUT\nAdvisor: Truong Vinh Lan",
        "step_badges": ["UC02\nInput", "UC03\nMotor", "UC04\nBelt", "UC05\nGearbox"],
        
        # UC02: Input
        "uc02_hdr": "Step 1 · Input Parameters",
        "uc02_sub": "Enter basic parameters and efficiency coefficients of the drive system.",
        "g_kinematics": "📊  Basic Kinematic Parameters",
        "g_efficiency": "⚙️  Transmission Efficiency Coefficients",
        "g_prelim_ratio": "🔢  Preliminary Transmission Ratios",
        "p_power": "Mixing drum power  P",
        "p_rpm": "Output speed  n",
        "p_life": "Service life  L",
        "p_eta_kn": "Coupling efficiency  η_kn",
        "p_eta_ol": "Bearing efficiency (1 pair)  η_ol",
        "p_eta_brc": "Bevel gear efficiency  η_brc",
        "p_eta_brt": "Spur gear efficiency  η_brt",
        "p_eta_x": "Belt/Chain efficiency  η_x",
        "p_u_h": "Gearbox ratio  u_h",
        "p_u_x": "Belt/Chain ratio  u_x",
        "p_u1": "High-speed stage ratio  u₁",
        "unit_year": "years",
        "unit_rpm": "rpm",
        "invalid_inputs": "⚠  {count} invalid fields. Please check again.",
        
        # UC03: Motor
        "uc03_hdr": "Step 2 · Motor Selection & Ratio Distribution",
        "uc03_sub": "Filter suitable motors from database and calculate kinematic table.",
        "g_prelim_calc": "📐  Preliminary Calculations",
        "lbl_total_eta": "Total efficiency η",
        "lbl_req_power": "Required power P_ct",
        "lbl_prelim_u": "Prelim. total ratio",
        "lbl_prelim_n": "Prelim. speed n_sb",
        "btn_prelim": "🔄  Calculate Preliminary",
        "g_motor_list": "📋  Suitable Motors (Top Recommendations)",
        "g_shaft_table": "📊  Shaft Parameters Table",
        "g_selected_motor": "✅  Selected Motor",
        "lbl_motor_id": "Motor designation",
        "lbl_actual_uh": "Actual Gearbox u_h",
        "lbl_u2": "Low-speed stage u₂",
        "lbl_actual_utotal": "Actual total ratio",
        "col_id": "ID",
        "col_p": "P_dc (kW)",
        "col_n": "n_dc (rpm)",
        "col_surplus": "Surplus (kW)",
        "col_dn": "Δn (rpm)",
        "col_dn_pct": "Δn%",
        "shaft_param": "Parameter",
        "shaft_power": "Power (kW)",
        "shaft_speed": "Speed (rpm)",
        "shaft_torque": "Torque (N·mm)",
        "shaft_motor": "Motor",
        "shaft_1": "Shaft I",
        "shaft_2": "Shaft II",
        "shaft_3": "Shaft III",
        "badge_ok": "✓ PASS",
        "badge_fail": "✗ FAIL"
    },
    "vi": {
        # General & Nav
        "app_title": "Hệ thống Dẫn động Thùng trộn",
        "nav_uc01": "Quản lý Dự án",
        "nav_uc02": "Nhập Thông số",
        "nav_uc03": "Chọn Động cơ",
        "nav_uc04": "Bộ truyền Đai",
        "nav_uc05": "Hộp Giảm tốc",
        "nav_uc06": "Xuất Báo cáo",
        "incomplete_step": "Chưa hoàn thành",
        "incomplete_msg": "Vui lòng hoàn thành bước trước đó trước khi tiếp tục.",
        "save_project": "Lưu Dự án",
        "exit_app": "Thoát ứng dụng",
        "exit_save_msg": "Bạn có muốn lưu dự án trước khi thoát không?",
        "saved_success": "Đã lưu!",
        "lang_toggle": "English",
        "brand": "  ⚙ HTDĐ Thùng trộn ",
        "new_project": "Dự án Mới",
        "open_project": "Mở Dự án",
        "project_status": "Trạng thái dự án hiện tại",
        "no_project": "Chưa có dự án nào được mở.",
        "step_completed": "Đã hoàn thành {done}/4 bước tính toán.",
        "new_project_msg": "Tạo dự án mới sẽ xóa toàn bộ dữ liệu hiện tại. Tiếp tục?",
        "confirm": "Xác nhận",
        "confirm_next": "Xác nhận và Tiếp tục  →",
        "success": "Thành công",
        "error": "Lỗi",
        "load_success": "Đã tải dự án thành công!",
        "invalid_file": "File không hợp lệ:",
        "no_data": "Chưa có dữ liệu nào để lưu.",
        "hcmut": "Trường ĐH Bách Khoa - CO3111",
        "group_info": "Đồ án môn học Đa ngành CO3111 · Trường ĐH Bách Khoa TP.HCM\nGV hướng dẫn: Trương Vĩnh Lân",
        "step_badges": ["UC02\nNhập liệu", "UC03\nĐộng cơ", "UC04\nBộ đai", "UC05\nHộp giảm tốc"],
        
        # UC02: Input
        "uc02_hdr": "Bước 1 · Nhập Thông Số Đầu Vào",
        "uc02_sub": "Điền các thông số cơ bản và hệ số hiệu suất của hệ thống dẫn động.",
        "g_kinematics": "📊  Thông số động học cơ bản",
        "g_efficiency": "⚙️  Hệ số hiệu suất các bộ truyền",
        "g_prelim_ratio": "🔢  Tỉ số truyền sơ bộ",
        "p_power": "Công suất thùng trộn  P",
        "p_rpm": "Số vòng quay đầu ra  n",
        "p_life": "Thời gian phục vụ  L",
        "p_eta_kn": "Hiệu suất khớp nối  η_kn",
        "p_eta_ol": "Hiệu suất ổ lăn (1 cặp)  η_ol",
        "p_eta_brc": "Hiệu suất bánh răng côn  η_brc",
        "p_eta_brt": "Hiệu suất bánh răng trụ  η_brt",
        "p_eta_x": "Hiệu suất bộ truyền xích/đai  η_x",
        "p_u_h": "Tỉ số truyền hộp giảm tốc  u_h",
        "p_u_x": "Tỉ số truyền bộ truyền xích/đai  u_x",
        "p_u1": "Tỉ số truyền cấp nhanh  u₁",
        "unit_year": "năm",
        "unit_rpm": "vg/ph",
        "invalid_inputs": "⚠  {count} trường chưa hợp lệ. Vui lòng kiểm tra lại.",
        
        # UC03: Motor
        "uc03_hdr": "Bước 2 · Chọn Động Cơ & Phân bổ Tỉ số Truyền",
        "uc03_sub": "Hệ thống lọc động cơ phù hợp từ CSDL và tính bảng động học trên các trục.",
        "g_prelim_calc": "📐  Tính toán sơ bộ",
        "lbl_total_eta": "Hiệu suất toàn hệ thống η",
        "lbl_req_power": "Công suất cần thiết P_ct",
        "lbl_prelim_u": "Tỉ số truyền chung sơ bộ",
        "lbl_prelim_n": "Số vòng quay sơ bộ n_sb",
        "btn_prelim": "🔄  Tính toán sơ bộ",
        "g_motor_list": "📋  Danh sách động cơ phù hợp (Top gợi ý)",
        "g_shaft_table": "📊  Bảng thông số các trục",
        "g_selected_motor": "✅  Động cơ đã chọn",
        "lbl_motor_id": "Ký hiệu động cơ",
        "lbl_actual_uh": "Tỉ số truyền HGT u_h",
        "lbl_u2": "Tỉ số truyền cấp chậm u₂",
        "lbl_actual_utotal": "Tỉ số truyền chung thực tế",
        "col_id": "Ký hiệu",
        "col_p": "P_đc (kW)",
        "col_n": "n_đc (vg/ph)",
        "col_surplus": "Dư CS (kW)",
        "col_dn": "Δn (vg/ph)",
        "col_dn_pct": "Δn%",
        "shaft_param": "Thông số",
        "shaft_power": "Công suất (kW)",
        "shaft_speed": "Số vòng quay (vg/ph)",
        "shaft_torque": "Momen xoắn (N·mm)",
        "shaft_motor": "Trục ĐC",
        "shaft_1": "Trục I",
        "shaft_2": "Trục II",
        "shaft_3": "Trục III",
        "badge_ok": "✓ ĐẠT",
        "badge_fail": "✗ KHÔNG ĐẠT"
    }
}

class Translator:
    _instance = None
    _lang = "en"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
        return cls._instance

    def set_lang(self, lang):
        self._lang = lang

    def get_lang(self):
        return self._lang

    def translate(self, key, **kwargs):
        text = TRANSLATIONS.get(self._lang, TRANSLATIONS["en"]).get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

# Global singleton
tr = Translator()
def _(key, **kwargs):
    return tr.translate(key, **kwargs)
