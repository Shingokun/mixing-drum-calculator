# ============================================================
# excel_exporter.py — Xuất báo cáo ra Excel
# ============================================================
import os
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from app.core.session import ProjectSession


# ── Màu sắc chủ đạo ──────────────────────────────────────
C_HEADER_BG  = "1E3A5F"   # Xanh đậm
C_HEADER_FG  = "FFFFFF"   # Trắng
C_SUB_BG     = "2C6FAC"   # Xanh vừa
C_SUB_FG     = "FFFFFF"
C_ROW_ALT    = "EBF3FB"   # Xanh nhạt xen kẽ
C_OK         = "2ECC71"   # Xanh lá
C_FAIL       = "E74C3C"   # Đỏ
C_LABEL_BG   = "D6E4F0"   # Xám xanh nhạt

# ── Tiện ích ─────────────────────────────────────────────
def _side(style="thin"):
    return Side(style=style, color="AAAAAA")

def _border():
    s = _side()
    return Border(left=s, right=s, top=s, bottom=s)

def _hdr_font(bold=True, size=11):
    return Font(name="Calibri", bold=bold, size=size, color=C_HEADER_FG)

def _body_font(bold=False, size=10):
    return Font(name="Calibri", bold=bold, size=size)

def _fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def _center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def _left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)

def _right():
    return Alignment(horizontal="right", vertical="center")


def _write_section_header(ws, row: int, title: str, num_cols: int = 5):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
    cell = ws.cell(row=row, column=1, value=title)
    cell.font = _hdr_font(bold=True, size=12)
    cell.fill = _fill(C_HEADER_BG)
    cell.alignment = _center()
    cell.border = _border()


def _write_sub_header(ws, row: int, cols: list):
    for c, label in enumerate(cols, start=1):
        cell = ws.cell(row=row, column=c, value=label)
        cell.font = _hdr_font(bold=True, size=10)
        cell.fill = _fill(C_SUB_BG)
        cell.alignment = _center()
        cell.border = _border()


def _write_row(ws, row: int, values: list, alt=False):
    bg = C_ROW_ALT if alt else "FFFFFF"
    for c, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=c, value=val)
        cell.font = _body_font(bold=False, size=10)
        cell.fill = _fill(bg)
        cell.alignment = _right() if isinstance(val, (int, float)) else _left()
        cell.border = _border()


def export_excel(session: ProjectSession, filepath: str):
    wb = Workbook()
    _sheet_summary(wb, session)
    _sheet_uc03(wb, session)
    _sheet_uc04(wb, session)
    _sheet_uc05(wb, session)
    wb.save(filepath)


# ─────────────────────────────────────────────────────────
def _sheet_summary(wb: Workbook, s: ProjectSession):
    ws = wb.active
    ws.title = "Tổng hợp"
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 22
    ws.column_dimensions['C'].width = 22
    ws.column_dimensions['D'].width = 22
    ws.column_dimensions['E'].width = 22
    ws.row_dimensions[1].height = 40

    # Tiêu đề lớn
    ws.merge_cells("A1:E1")
    t = ws["A1"]
    t.value = "BÁO CÁO THIẾT KẾ HỆ THỐNG DẪN ĐỘNG THÙNG TRỘN"
    t.font = Font(name="Calibri", bold=True, size=16, color=C_HEADER_FG)
    t.fill = _fill(C_HEADER_BG)
    t.alignment = _center()
    t.border = _border()

    row = 3
    _write_section_header(ws, row, "I. THÔNG SỐ ĐẦU VÀO"); row += 1
    pairs = [
        ("Công suất thùng trộn P",       f"{s.inputs.power_kw:.2f} kW"),
        ("Số vòng quay đầu ra n",         f"{s.inputs.rpm_out:.1f} vg/ph"),
        ("Thời gian phục vụ L",           f"{s.inputs.service_life_year:.1f} năm"),
        ("Hiệu suất khớp nối η_kn",       f"{s.inputs.eta_kn:.3f}"),
        ("Hiệu suất ổ lăn η_ol",          f"{s.inputs.eta_ol:.3f}"),
        ("Hiệu suất BR côn η_brc",        f"{s.inputs.eta_brc:.3f}"),
        ("Hiệu suất BR trụ η_brt",        f"{s.inputs.eta_brt:.3f}"),
        ("Hiệu suất xích/đai η_x",        f"{s.inputs.eta_x:.3f}"),
    ]
    for i, (k, v) in enumerate(pairs):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=5)
        lbl = ws.cell(row=row, column=1, value=k)
        val = ws.cell(row=row, column=4, value=v)
        lbl.font = _body_font(bold=True); lbl.fill = _fill(C_LABEL_BG if i%2==0 else "FFFFFF")
        val.font = _body_font(); val.fill = _fill(C_ROW_ALT if i%2==0 else "FFFFFF")
        lbl.alignment = _left(); val.alignment = _right()
        lbl.border = _border(); val.border = _border()
        row += 1

    row += 1
    _write_section_header(ws, row, "II. KẾT QUẢ TỔNG HỢP"); row += 1
    m = s.motor
    summary = [
        ("Hiệu suất toàn hệ thống η",         f"{m.eta:.4f}"),
        ("Công suất cần thiết P_ct",           f"{m.p_ct_kw:.4f} kW"),
        ("Động cơ đã chọn",                    m.motor_name or "—"),
        ("Công suất động cơ P_đc",             f"{m.rated_power_kw:.1f} kW"),
        ("Số vòng quay động cơ n_đc",          f"{m.rated_rpm:.0f} vg/ph"),
        ("Tỉ số truyền chung u_ch",            f"{m.u_ch_actual:.4f}"),
        ("Tỉ số truyền hộp giảm tốc u_h",     f"{m.u_h_actual:.4f}"),
        ("Tỉ số truyền cấp nhanh u_1",        f"{s.inputs.u1:.2f}"),
        ("Tỉ số truyền cấp chậm u_2",         f"{m.u2:.2f}"),
        ("Số dây đai z",                       f"{s.belt.num_belts}"),
        ("Vận tốc đai v",                      f"{s.belt.belt_velocity_ms:.3f} m/s"),
        ("Mô đun ngoài tiêu chuẩn m_te",      f"{s.gearbox.cone.m_te:.2f} mm"),
        ("Số răng bánh nhỏ z1",               f"{s.gearbox.cone.z1}"),
        ("Số răng bánh lớn z2",               f"{s.gearbox.cone.z2}"),
        ("Chiều dài côn ngoài R_e",           f"{s.gearbox.cone.Re_mm:.2f} mm"),
        ("Chiều rộng vành răng b",            f"{s.gearbox.cone.b_mm:.2f} mm"),
        ("KBền tiếp xúc [σ_H]",              f"{s.gearbox.cone.sig_H:.2f} MPa"),
        ("σ_F1 thực tế / cho phép",           f"{s.gearbox.cone.sigma_F1_actual:.2f} / {s.gearbox.cone.sig_F1:.2f} MPa"),
        ("σ_F2 thực tế / cho phép",           f"{s.gearbox.cone.sigma_F2_actual:.2f} / {s.gearbox.cone.sig_F2:.2f} MPa"),
        ("Kiểm bền uốn",                       "ĐẠT ✓" if s.gearbox.strength_ok else "KHÔNG ĐẠT ✗"),
    ]
    for i, (k, v) in enumerate(summary):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=5)
        lbl = ws.cell(row=row, column=1, value=k)
        val = ws.cell(row=row, column=4, value=v)
        bg = C_ROW_ALT if i % 2 == 0 else "FFFFFF"
        lbl.fill = val.fill = _fill(bg)
        lbl.font = _body_font(bold=True)
        if "ĐẠT" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_OK)
        elif "KHÔNG" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_FAIL)
        else: val.font = _body_font()
        lbl.alignment = _left(); val.alignment = _right()
        lbl.border = val.border = _border()
        row += 1


def _sheet_uc03(wb: Workbook, s: ProjectSession):
    ws = wb.create_sheet("UC03 - Động cơ & Trục")
    for col, w in zip("ABCDE", [30, 18, 18, 18, 18]):
        ws.column_dimensions[col].width = w

    row = 1
    _write_section_header(ws, row, "BẢNG THÔNG SỐ ĐỘNG HỌC TRÊN CÁC TRỤC"); row += 1
    _write_sub_header(ws, row, ["Thông số", "Trục ĐC", "Trục I", "Trục II", "Trục III"]); row += 1

    m = s.motor
    shaft_rows = [
        ("Công suất (kW)",
         m.shaft_powers.get('dc','—'), m.shaft_powers.get('I','—'),
         m.shaft_powers.get('II','—'), m.shaft_powers.get('III','—')),
        ("Số vòng quay (vg/ph)",
         m.shaft_rpms.get('dc','—'), m.shaft_rpms.get('I','—'),
         m.shaft_rpms.get('II','—'), m.shaft_rpms.get('III','—')),
        ("Momen xoắn (N·mm)",
         m.shaft_torques.get('dc','—'), m.shaft_torques.get('I','—'),
         m.shaft_torques.get('II','—'), m.shaft_torques.get('III','—')),
    ]
    for i, row_data in enumerate(shaft_rows):
        _write_row(ws, row, list(row_data), alt=(i%2==0)); row += 1


def _sheet_uc04(wb: Workbook, s: ProjectSession):
    ws = wb.create_sheet("UC04 - Bộ truyền đai")
    ws.column_dimensions['A'].width = 38
    ws.column_dimensions['B'].width = 25

    row = 1
    _write_section_header(ws, row, "BỘ TRUYỀN ĐAI THANG LOẠI B", num_cols=2); row += 1
    b = s.belt
    params = [
        ("Đường kính bánh đai nhỏ d₁",     f"{b.d1_mm:.1f} mm"),
        ("Đường kính bánh đai lớn d₂",      f"{b.d2_mm:.1f} mm"),
        ("Vận tốc đai v",                   f"{b.belt_velocity_ms:.3f} m/s"),
        ("Chiều dài đai L",                 f"{b.belt_length_mm:.0f} mm"),
        ("Khoảng cách trục a",              f"{b.center_distance_mm:.1f} mm"),
        ("Góc ôm trên bánh nhỏ α₁",        f"{b.alpha1_deg:.2f}°"),
        ("Số dây đai z",                    str(b.num_belts)),
        ("Lực vòng F_t",                    f"{b.Ft_N:.1f} N"),
        ("Lực căng ban đầu F₀",            f"{b.F0_N:.1f} N"),
        ("Vận tốc đai hợp lệ",             "ĐẠT ✓" if b.velocity_ok else "VƯỢT GIỚI HẠN ✗"),
    ]
    for i, (k, v) in enumerate(params):
        lbl = ws.cell(row=row, column=1, value=k)
        val = ws.cell(row=row, column=2, value=v)
        bg = C_ROW_ALT if i%2==0 else "FFFFFF"
        lbl.fill = val.fill = _fill(bg)
        lbl.font = _body_font(bold=True)
        if "ĐẠT" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_OK)
        elif "VƯỢT" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_FAIL)
        else: val.font = _body_font()
        lbl.alignment = _left(); val.alignment = _right()
        lbl.border = val.border = _border()
        row += 1


def _sheet_uc05(wb: Workbook, s: ProjectSession):
    ws = wb.create_sheet("UC05 - Hộp giảm tốc")
    ws.column_dimensions['A'].width = 38
    ws.column_dimensions['B'].width = 25

    row = 1
    _write_section_header(ws, row, "BÁNH RĂNG CÔN CẤP NHANH", num_cols=2); row += 1
    c = s.gearbox.cone
    params = [
        ("Tỉ số truyền thực tế u_tt",       f"{c.u_tt:.4f}"),
        ("Sai lệch tỉ số truyền Δu",         f"{c.delta_u_pct:.2f}%"),
        ("Mô đun ngoài tiêu chuẩn m_te",     f"{c.m_te:.2f} mm"),
        ("Số răng bánh nhỏ z₁",             str(c.z1)),
        ("Số răng bánh lớn z₂",             str(c.z2)),
        ("Chiều dài côn ngoài R_e",          f"{c.Re_mm:.2f} mm"),
        ("Đường kính vòng chia ngoài d_e1", f"{c.de1_mm:.2f} mm"),
        ("Chiều rộng vành răng b",           f"{c.b_mm:.2f} mm"),
        ("Góc mặt côn chia δ₁",             f"{c.delta1_deg:.3f}°"),
        ("Góc mặt côn chia δ₂",             f"{c.delta2_deg:.3f}°"),
        ("Ứng suất cho phép [σ_H]",          f"{c.sig_H:.2f} MPa"),
        ("σ_F1 cho phép / thực tế",          f"{c.sig_F1:.2f} / {c.sigma_F1_actual:.2f} MPa"),
        ("σ_F2 cho phép / thực tế",          f"{c.sig_F2:.2f} / {c.sigma_F2_actual:.2f} MPa"),
        ("Lực vòng F_t",                     f"{c.Ft_N:.1f} N"),
        ("Lực hướng tâm F_r",               f"{c.Fr_N:.1f} N"),
        ("Lực dọc trục F_a",                f"{c.Fa_N:.1f} N"),
        ("Kiểm bền uốn",                     "ĐẠT ✓" if s.gearbox.strength_ok else "KHÔNG ĐẠT ✗"),
    ]
    for i, (k, v) in enumerate(params):
        lbl = ws.cell(row=row, column=1, value=k)
        val = ws.cell(row=row, column=2, value=v)
        bg = C_ROW_ALT if i%2==0 else "FFFFFF"
        lbl.fill = val.fill = _fill(bg)
        lbl.font = _body_font(bold=True)
        if "ĐẠT ✓" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_OK)
        elif "KHÔNG" in str(v): val.font = Font(name="Calibri", bold=True, size=10, color=C_FAIL)
        else: val.font = _body_font()
        lbl.alignment = _left(); val.alignment = _right()
        lbl.border = val.border = _border()
        row += 1