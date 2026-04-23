# ============================================================
# style.py — Global Qt stylesheet (Dark industrial theme)
# ============================================================

PALETTE = {
    "bg":          "#0F1923",   # nền chính — xanh đen
    "bg_card":     "#162130",   # nền card/panel
    "bg_input":    "#1C2B3A",   # nền input field
    "bg_hover":    "#1E3A5F",   # hover state
    "accent":      "#2E86DE",   # xanh chính
    "accent_light":"#54A0FF",   # xanh nhạt
    "accent_dim":  "#1B4F8A",   # xanh tối hơn (border active)
    "success":     "#10AC84",   # xanh lá
    "warning":     "#F9CA24",   # vàng
    "danger":      "#EE5A24",   # đỏ cam
    "text":        "#DFE6ED",   # chữ chính
    "text_muted":  "#7F8C8D",   # chữ mờ
    "border":      "#263748",   # border mặc định
    "nav_bg":      "#0A1628",   # sidebar
    "nav_sel":     "#1B4F8A",   # sidebar selected
}

GLOBAL_STYLE = """
/* ─── Base ─────────────────────────────────── */
QWidget {
    background-color: #0F1923;
    color: #DFE6ED;
    font-family: "Segoe UI", "Calibri", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0F1923;
}

/* ─── Navigation Sidebar ────────────────────── */
QListWidget {
    background-color: #0A1628;
    border: none;
    border-right: 2px solid #263748;
    padding: 8px 0px;
    outline: none;
}

QListWidget::item {
    color: #7F8C8D;
    padding: 14px 20px;
    border-left: 3px solid transparent;
    font-size: 13px;
    font-weight: normal;
}

QListWidget::item:selected {
    background-color: #1B4F8A;
    color: #FFFFFF;
    border-left: 3px solid #2E86DE;
    font-weight: bold;
}

QListWidget::item:hover:!selected {
    background-color: #162130;
    color: #DFE6ED;
}

QListWidget::item:disabled {
    color: #3D5166;
}

/* ─── Cards / Group Boxes ───────────────────── */
QGroupBox {
    background-color: #162130;
    border: 1px solid #263748;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px 12px 12px 12px;
    font-size: 13px;
    font-weight: bold;
    color: #54A0FF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    left: 12px;
    background-color: #162130;
}

/* ─── Input Fields ─────────────────────────── */
QLineEdit {
    background-color: #1C2B3A;
    border: 1px solid #263748;
    border-radius: 5px;
    padding: 8px 12px;
    color: #DFE6ED;
    font-size: 13px;
    selection-background-color: #2E86DE;
}

QLineEdit:focus {
    border: 1px solid #2E86DE;
    background-color: #1E3A5F;
}

QLineEdit[valid="false"] {
    border: 1px solid #EE5A24;
    background-color: #2C1810;
}

QLineEdit[valid="true"] {
    border: 1px solid #10AC84;
}

QLineEdit:disabled {
    background-color: #12202E;
    color: #3D5166;
    border-color: #1C2B3A;
}

/* ─── Labels ────────────────────────────────── */
QLabel {
    background: transparent;
    color: #DFE6ED;
}

QLabel[type="title"] {
    font-size: 22px;
    font-weight: bold;
    color: #54A0FF;
}

QLabel[type="subtitle"] {
    font-size: 14px;
    color: #7F8C8D;
}

QLabel[type="section"] {
    font-size: 14px;
    font-weight: bold;
    color: #2E86DE;
    padding-bottom: 4px;
}

QLabel[type="unit"] {
    color: #7F8C8D;
    font-size: 12px;
}

QLabel[type="error"] {
    color: #EE5A24;
    font-size: 11px;
}

QLabel[type="success"] {
    color: #10AC84;
    font-size: 12px;
    font-weight: bold;
}

QLabel[type="result_ok"] {
    color: #10AC84;
    font-weight: bold;
    font-size: 13px;
}

QLabel[type="result_fail"] {
    color: #EE5A24;
    font-weight: bold;
    font-size: 13px;
}

/* ─── Buttons ───────────────────────────────── */
QPushButton {
    background-color: #2E86DE;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: bold;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #54A0FF;
}

QPushButton:pressed {
    background-color: #1B4F8A;
}

QPushButton:disabled {
    background-color: #263748;
    color: #3D5166;
}

QPushButton[variant="secondary"] {
    background-color: transparent;
    border: 1px solid #2E86DE;
    color: #2E86DE;
}

QPushButton[variant="secondary"]:hover {
    background-color: #1E3A5F;
    color: #54A0FF;
}

QPushButton[variant="danger"] {
    background-color: #EE5A24;
}

QPushButton[variant="danger"]:hover {
    background-color: #FF6B35;
}

QPushButton[variant="success"] {
    background-color: #10AC84;
}

QPushButton[variant="success"]:hover {
    background-color: #1DD1A1;
}

/* ─── ComboBox ──────────────────────────────── */
QComboBox {
    background-color: #1C2B3A;
    border: 1px solid #263748;
    border-radius: 5px;
    padding: 8px 12px;
    color: #DFE6ED;
    font-size: 13px;
    min-width: 160px;
}

QComboBox:focus {
    border: 1px solid #2E86DE;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #1C2B3A;
    border: 1px solid #263748;
    selection-background-color: #1B4F8A;
    color: #DFE6ED;
    outline: none;
}

/* ─── Tables ────────────────────────────────── */
QTableWidget {
    background-color: #162130;
    border: 1px solid #263748;
    border-radius: 6px;
    gridline-color: #1C2B3A;
    font-size: 12px;
    color: #DFE6ED;
    selection-background-color: #1B4F8A;
    outline: none;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1C2B3A;
}

QTableWidget::item:selected {
    background-color: #1B4F8A;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #0A1628;
    color: #54A0FF;
    border: none;
    border-bottom: 2px solid #2E86DE;
    padding: 10px 12px;
    font-weight: bold;
    font-size: 12px;
}

QHeaderView::section:vertical {
    border-right: 1px solid #263748;
}

/* ─── ScrollBars ────────────────────────────── */
QScrollBar:vertical {
    background: #0A1628;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #263748;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #2E86DE;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0A1628;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #263748;
    border-radius: 4px;
}

/* ─── Tab Widget ────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #263748;
    background-color: #162130;
    border-radius: 0px 6px 6px 6px;
}

QTabBar::tab {
    background-color: #0A1628;
    color: #7F8C8D;
    border: 1px solid #263748;
    border-bottom: none;
    padding: 8px 18px;
    border-radius: 4px 4px 0px 0px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #162130;
    color: #54A0FF;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    color: #DFE6ED;
    background-color: #162130;
}

/* ─── Splitter ──────────────────────────────── */
QSplitter::handle {
    background-color: #263748;
    width: 2px;
}

/* ─── Tooltip ───────────────────────────────── */
QToolTip {
    background-color: #162130;
    color: #DFE6ED;
    border: 1px solid #2E86DE;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* ─── Message Box ───────────────────────────── */
QMessageBox {
    background-color: #162130;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ─── Frame / Separator ─────────────────────── */
QFrame[frameShape="4"],  /* HLine */
QFrame[frameShape="5"]  /* VLine */ {
    color: #263748;
    background-color: #263748;
    border: none;
    max-height: 1px;
}

/* ─── Spinbox ───────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #1C2B3A;
    border: 1px solid #263748;
    border-radius: 5px;
    padding: 7px 10px;
    color: #DFE6ED;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #2E86DE;
}
"""

# ── Tiện ích màu cho từng trạng thái ─────────────
STATUS_COLORS = {
    "ok":      "#10AC84",
    "fail":    "#EE5A24",
    "warning": "#F9CA24",
    "info":    "#2E86DE",
}