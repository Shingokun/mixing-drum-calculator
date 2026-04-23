# ============================================================
# pdf_exporter.py — Xuất báo cáo ra PDF
# ============================================================
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.core.session import ProjectSession

# ── Màu chủ đạo ──────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1E3A5F")
MID_BLUE   = colors.HexColor("#2C6FAC")
LIGHT_BLUE = colors.HexColor("#EBF3FB")
GREEN      = colors.HexColor("#2ECC71")
RED        = colors.HexColor("#E74C3C")
GREY       = colors.HexColor("#F5F5F5")
WHITE      = colors.white


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle", fontSize=16, textColor=WHITE,
        alignment=TA_CENTER, spaceAfter=4,
        fontName="Helvetica-Bold"
    )
    section = ParagraphStyle(
        "SectionHdr", fontSize=12, textColor=WHITE,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=4,
        fontName="Helvetica-Bold"
    )
    body = ParagraphStyle(
        "Body", fontSize=9, textColor=colors.black,
        alignment=TA_LEFT, fontName="Helvetica"
    )
    return title, section, body


def _param_table(data: list, col_widths=None):
    """2-column table: tên thông số | giá trị"""
    if col_widths is None:
        col_widths = [110*mm, 60*mm]
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND",(0,0), (-1,0), MID_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ALIGN",     (1,1), (1,-1), "RIGHT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_BLUE, WHITE]),
        ("GRID",      (0,0), (-1,-1), 0.5, colors.HexColor("#AAAAAA")),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6),
    ])
    t.setStyle(style)
    return t


def export_pdf(session: ProjectSession, filepath: str):
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=18*mm, bottomMargin=18*mm,
        leftMargin=18*mm, rightMargin=18*mm
    )
    title_style, section_style, body_style = _styles()
    story = []

    # ── Tiêu đề ──────────────────────────────────────────
    title_tbl = Table(
        [["BÁO CÁO THIẾT KẾ\nHỆ THỐNG DẪN ĐỘNG THÙNG TRỘN"]],
        colWidths=[174*mm]
    )
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 15),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [DARK_BLUE]),
    ]))
    story.append(title_tbl)
    story.append(Spacer(1, 8*mm))

    s = session

    # ── I. Thông số đầu vào ──────────────────────────────
    story.append(_section_hdr("I. THÔNG SỐ ĐẦU VÀO"))
    data = [["Thông số", "Giá trị"],
            ["Công suất thùng trộn P",       f"{s.inputs.power_kw:.2f} kW"],
            ["Số vòng quay đầu ra n",         f"{s.inputs.rpm_out:.1f} vg/ph"],
            ["Thời gian phục vụ L",           f"{s.inputs.service_life_year:.1f} năm"],
            ["Hiệu suất hệ thống η",         f"{s.motor.eta:.4f}"],
            ["Công suất cần thiết P_ct",      f"{s.motor.p_ct_kw:.3f} kW"],
            ]
    story.append(_param_table(data))
    story.append(Spacer(1, 5*mm))

    # ── II. Động cơ ──────────────────────────────────────
    story.append(_section_hdr("II. CHỌN ĐỘNG CƠ & PHÂN BỔ TỶ SỐ TRUYỀN"))
    m = s.motor
    data = [["Thông số", "Giá trị"],
            ["Động cơ đã chọn",              m.motor_name or "—"],
            ["Công suất động cơ",             f"{m.rated_power_kw:.1f} kW"],
            ["Số vòng quay động cơ",          f"{m.rated_rpm:.0f} vg/ph"],
            ["Tỉ số truyền chung thực tế",    f"{m.u_ch_actual:.4f}"],
            ["Tỉ số truyền hộp giảm tốc",    f"{m.u_h_actual:.4f}"],
            ["Tỉ số truyền cấp nhanh u₁",    f"{s.inputs.u1:.2f}"],
            ["Tỉ số truyền cấp chậm u₂",     f"{m.u2:.2f}"],
            ]
    story.append(_param_table(data))

    # Bảng trục
    story.append(Spacer(1, 4*mm))
    shaft_data = [
        ["Trục", "Công suất (kW)", "Tốc độ (vg/ph)", "Momen (N·mm)"],
        ["Động cơ",
         f"{m.shaft_powers.get('dc', 0):.4f}",
         f"{m.shaft_rpms.get('dc', 0):.0f}",
         f"{m.shaft_torques.get('dc', 0):.2f}"],
        ["Trục I",
         f"{m.shaft_powers.get('I', 0):.4f}",
         f"{m.shaft_rpms.get('I', 0):.2f}",
         f"{m.shaft_torques.get('I', 0):.2f}"],
        ["Trục II",
         f"{m.shaft_powers.get('II', 0):.4f}",
         f"{m.shaft_rpms.get('II', 0):.2f}",
         f"{m.shaft_torques.get('II', 0):.2f}"],
        ["Trục III",
         f"{m.shaft_powers.get('III', 0):.4f}",
         f"{m.shaft_rpms.get('III', 0):.2f}",
         f"{m.shaft_torques.get('III', 0):.2f}"],
    ]
    story.append(_param_table(shaft_data, col_widths=[43*mm, 43*mm, 43*mm, 45*mm]))
    story.append(Spacer(1, 5*mm))

    # ── III. Bộ truyền đai ───────────────────────────────
    story.append(_section_hdr("III. BỘ TRUYỀN ĐAI THANG"))
    b = s.belt
    data = [["Thông số", "Giá trị"],
            ["Đường kính bánh đai nhỏ d₁",  f"{b.d1_mm:.1f} mm"],
            ["Đường kính bánh đai lớn d₂",   f"{b.d2_mm:.1f} mm"],
            ["Vận tốc đai v",                f"{b.belt_velocity_ms:.3f} m/s"],
            ["Chiều dài đai L",              f"{b.belt_length_mm:.0f} mm"],
            ["Khoảng cách trục a",           f"{b.center_distance_mm:.1f} mm"],
            ["Góc ôm bánh nhỏ α₁",          f"{b.alpha1_deg:.2f}°"],
            ["Số dây đai z",                 str(b.num_belts)],
            ["Lực vòng F_t",                 f"{b.Ft_N:.1f} N"],
            ]
    story.append(_param_table(data))
    story.append(Spacer(1, 5*mm))

    # ── IV. Hộp giảm tốc ────────────────────────────────
    story.append(_section_hdr("IV. BÁNH RĂNG CÔN CẤP NHANH"))
    c = s.gearbox.cone
    ok_str = "ĐẠT" if s.gearbox.strength_ok else "KHÔNG ĐẠT"
    data = [["Thông số", "Giá trị"],
            ["Mô đun ngoài tiêu chuẩn m_te",  f"{c.m_te:.2f} mm"],
            ["Số răng z₁ / z₂",              f"{c.z1} / {c.z2}"],
            ["Tỉ số truyền thực tế u_tt",     f"{c.u_tt:.4f}"],
            ["Sai lệch Δu",                  f"{c.delta_u_pct:.2f}%"],
            ["Chiều dài côn ngoài R_e",       f"{c.Re_mm:.2f} mm"],
            ["Đường kính vòng chia d_e1",     f"{c.de1_mm:.2f} mm"],
            ["Chiều rộng vành răng b",        f"{c.b_mm:.2f} mm"],
            ["Góc côn chia δ₁ / δ₂",         f"{c.delta1_deg:.3f}° / {c.delta2_deg:.3f}°"],
            ["Ứng suất cho phép [σ_H]",       f"{c.sig_H:.2f} MPa"],
            ["σ_F1 thực tế / cho phép",       f"{c.sigma_F1_actual:.2f} / {c.sig_F1:.2f} MPa"],
            ["σ_F2 thực tế / cho phép",       f"{c.sigma_F2_actual:.2f} / {c.sig_F2:.2f} MPa"],
            ["Lực vòng / hướng tâm / dọc trục", f"{c.Ft_N:.1f} / {c.Fr_N:.1f} / {c.Fa_N:.1f} N"],
            ["Kết quả kiểm bền",              ok_str],
            ]
    t = _param_table(data)
    # Tô màu kết quả kiểm bền
    row_idx = len(data) - 1
    color = GREEN if s.gearbox.strength_ok else RED
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (1, row_idx), (1, row_idx), color),
        ("FONTNAME",  (1, row_idx), (1, row_idx), "Helvetica-Bold"),
    ]))
    story.append(t)

    doc.build(story)


def _section_hdr(text: str):
    tbl = Table([[text]], colWidths=[174*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), MID_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 11),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
    ]))
    return tbl