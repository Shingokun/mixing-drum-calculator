# ============================================================
# pdf_exporter.py — Xuất báo cáo ra PDF
# ============================================================
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.core.session import ProjectSession
from app.ui.i18n import _, tr

import os
try:
    # Đăng ký font hỗ trợ tiếng Việt (Arial)
    if os.name == 'nt':
        font_dir = "C:\\Windows\\Fonts"
    else:
        font_dir = "/Library/Fonts" # macOS fallback
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(font_dir, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(font_dir, 'arialbd.ttf')))
    FONT_REGULAR = 'Arial'
    FONT_BOLD = 'Arial-Bold'
except Exception:
    FONT_REGULAR = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

# ── Màu chủ đạo ──────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1E3A5F")
MID_BLUE   = colors.HexColor("#2C6FAC")
LIGHT_BLUE = colors.HexColor("#EBF3FB")
GREEN      = colors.HexColor("#2ECC71")
RED        = colors.HexColor("#E74C3C")
GREY       = colors.HexColor("#F5F5F5")
WHITE      = colors.white


def _pdf_safe_text(value) -> str:
    """Normalize symbols that often miss glyphs in PDFs across Windows font setups."""
    text = str(value)
    # Rút gọn danh sách thay thế vì font Arial đã hỗ trợ tốt các ký tự Hy Lạp và chỉ số
    replacements = {
        "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
        "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
        "✗": "FAIL", "✓": "PASS",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def _pdf_safe_table(data: list):
    return [[_pdf_safe_text(cell) for cell in row] for row in data]


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle", fontSize=16, textColor=WHITE,
        alignment=TA_CENTER, spaceAfter=4,
        fontName=FONT_BOLD
    )
    section = ParagraphStyle(
        "SectionHdr", fontSize=12, textColor=WHITE,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=4,
        fontName=FONT_BOLD
    )
    body = ParagraphStyle(
        "Body", fontSize=9, textColor=colors.black,
        alignment=TA_LEFT, fontName=FONT_REGULAR
    )
    return title, section, body


def _param_table(data: list, col_widths=None):
    """2-column table: tên thông số | giá trị"""
    if col_widths is None:
        col_widths = [110*mm, 60*mm]
    t = Table(_pdf_safe_table(data), colWidths=col_widths)
    style = TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), FONT_REGULAR),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("FONTNAME",  (0,0), (0,-1), FONT_BOLD),
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


def export_pdf(session: ProjectSession, filepath: str, lang: str | None = None):
    original_lang = tr.get_lang()
    if lang in ("en", "vi"):
        tr.set_lang(lang)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=18*mm, bottomMargin=18*mm,
        leftMargin=18*mm, rightMargin=18*mm
    )
    _title_style, _sec_style, body_style = _styles()
    story = []

    # ── Tiêu đề ──────────────────────────────────────────
    title_tbl = Table(
        [[_pdf_safe_text(_("rpt_title"))]],
        colWidths=[174*mm]
    )
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
        ("FONTNAME",   (0,0), (-1,-1), FONT_BOLD),
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
    story.append(_section_hdr(_("rpt_sec_input")))
    data = [[_("shaft_param"), _("rpt_result")],
            [_("p_power") + " P",       f"{s.inputs.power_kw:.2f} kW"],
            [_("p_rpm") + " n",         f"{s.inputs.rpm_out:.1f} " + _("unit_rpm")],
            [_("p_life") + " L",           f"{s.inputs.service_life_year:.1f} " + _("unit_year")],
            [_("lbl_total_eta"),         f"{s.motor.eta:.4f}"],
            [_("lbl_req_power"),      f"{s.motor.p_ct_kw:.3f} kW"],
            ]
    story.append(_param_table(data))
    story.append(Spacer(1, 5*mm))

    # ── II. Động cơ ──────────────────────────────────────
    story.append(_section_hdr(_("rpt_sec_motor")))
    m = s.motor
    data = [[_("shaft_param"), _("rpt_result")],
            [_("lbl_motor_sel"),              m.motor_name or "—"],
            [_("col_p"),             f"{m.rated_power_kw:.1f} kW"],
            [_("col_n"),          f"{m.rated_rpm:.0f} " + _("unit_rpm")],
            [_("lbl_actual_utotal"),    f"{m.u_ch_actual:.4f}"],
            [_("lbl_actual_uh"),    f"{m.u_h_actual:.4f}"],
            [_("p_u1") + " u₁",    f"{s.inputs.u1:.2f}"],
            [_("lbl_u2"),     f"{m.u2:.2f}"],
            ]
    story.append(_param_table(data))

    # Bảng trục
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(_pdf_safe_text(_("rpt_shaft_table")), body_style))
    
    shaft_data = [
        [_("shaft_param"), _("shaft_power"), _("shaft_speed"), _("shaft_torque")],
        [_("shaft_motor"),
         f"{m.shaft_powers.get('dc', 0):.4f}",
         f"{m.shaft_rpms.get('dc', 0):.0f}",
         f"{m.shaft_torques.get('dc', 0):.2f}"],
        [_("shaft_1"),
         f"{m.shaft_powers.get('I', 0):.4f}",
         f"{m.shaft_rpms.get('I', 0):.2f}",
         f"{m.shaft_torques.get('I', 0):.2f}"],
        [_("shaft_2"),
         f"{m.shaft_powers.get('II', 0):.4f}",
         f"{m.shaft_rpms.get('II', 0):.2f}",
         f"{m.shaft_torques.get('II', 0):.2f}"],
        [_("shaft_3"),
         f"{m.shaft_powers.get('III', 0):.4f}",
         f"{m.shaft_rpms.get('III', 0):.2f}",
         f"{m.shaft_torques.get('III', 0):.2f}"],
    ]
    story.append(_param_table(shaft_data, col_widths=[43*mm, 43*mm, 43*mm, 45*mm]))
    story.append(Spacer(1, 5*mm))

    # ── III. Bộ truyền đai ───────────────────────────────
    story.append(_section_hdr(_("rpt_sec_belt")))
    b = s.belt
    data = [[_("shaft_param"), _("rpt_result")],
            [_("lbl_d1"),  f"{b.d1_mm:.1f} mm"],
            [_("lbl_d2"),   f"{b.d2_mm:.1f} mm"],
            [_("lbl_v_belt"),                f"{b.belt_velocity_ms:.3f} " + _("unit_ms")],
            [_("lbl_l_belt"),              f"{b.belt_length_mm:.0f} mm"],
            [_("lbl_a_belt"),           f"{b.center_distance_mm:.1f} mm"],
            [_("lbl_alpha1"),          f"{b.alpha1_deg:.2f}°"],
            [_("lbl_z_belt"),                 str(b.num_belts)],
            [_("lbl_ft"),                 f"{b.Ft_N:.1f} N"],
            ]
    story.append(_param_table(data))
    story.append(Spacer(1, 5*mm))

    # ── IV. Hộp giảm tốc ────────────────────────────────
    story.append(_section_hdr(_("rpt_sec_gear")))
    c = s.gearbox.cone
    ok_str = _("rpt_pass") if s.gearbox.strength_ok else _("rpt_fail")
    data = [[_("shaft_param"), _("rpt_result")],
            [_("lbl_mte"),  f"{c.m_te:.2f} mm"],
            [_("lbl_z1z2"),              f"{c.z1} / {c.z2}"],
            [_("lbl_u_gear"),     f"{c.u_tt:.4f}"],
            [_("lbl_delta_u"),                  f"{c.delta_u_pct:.2f}%"],
            [_("lbl_re"),       f"{c.Re_mm:.2f} mm"],
            ["d_e1",     f"{c.de1_mm:.2f} mm"],
            [_("lbl_b_width"),        f"{c.b_mm:.2f} mm"],
            ["δ₁ / δ₂",         f"{c.delta1_deg:.3f}° / {c.delta2_deg:.3f}°"],
            [_("lbl_sig_h"),       f"{c.sig_H:.2f} MPa"],
            ["σ_F1",       f"{c.sigma_F1_actual:.2f} / {c.sig_F1:.2f} MPa"],
            ["σ_F2",       f"{c.sigma_F2_actual:.2f} / {c.sig_F2:.2f} MPa"],
            ["F_t / F_r / F_a", f"{c.Ft_N:.1f} / {c.Fr_N:.1f} / {c.Fa_N:.1f} N"],
            [_("rpt_result"),              ok_str],
            ]
    t = _param_table(data)
    # Tô màu kết quả kiểm bền
    row_idx = len(data) - 1
    color = GREEN if s.gearbox.strength_ok else RED
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (1, row_idx), (1, row_idx), color),
        ("FONTNAME",  (1, row_idx), (1, row_idx), FONT_BOLD),
    ]))
    story.append(t)

    try:
        doc.build(story)
    finally:
        tr.set_lang(original_lang)


def _section_hdr(text: str):
    tbl = Table([[_pdf_safe_text(text)]], colWidths=[174*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), MID_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
        ("FONTNAME",   (0,0), (-1,-1), FONT_BOLD),
        ("FONTSIZE",   (0,0), (-1,-1), 11),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
    ]))
    return tbl
