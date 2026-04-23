# ============================================================
# widgets/result_table.py — Bảng kết quả tổng hợp
# ============================================================
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class ResultTable(QTableWidget):
    """QTableWidget có style đẹp sẵn + các method tiện ích"""

    OK_COLOR   = QColor("#10AC84")
    FAIL_COLOR = QColor("#EE5A24")
    HEAD_COLOR = QColor("#54A0FF")
    ALT_COLOR  = QColor("#1C2B3A")
    BASE_COLOR = QColor("#162130")

    def __init__(self, headers: list, parent=None):
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(False)  # thủ công
        self.setShowGrid(False)

    def add_row(self, values: list, ok_col: int = -1,
                highlight_row: bool = False):
        r = self.rowCount()
        self.insertRow(r)
        bg = self.ALT_COLOR if r % 2 == 0 else self.BASE_COLOR
        for c, v in enumerate(values):
            item = QTableWidgetItem(str(v))
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(bg)
            if c == 0:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            if c == ok_col:
                ok = str(v).upper() in ("ĐẠT", "OK", "TRUE", "✓")
                item.setForeground(self.OK_COLOR if ok else self.FAIL_COLOR)
                f = QFont()
                f.setBold(True)
                item.setFont(f)
            self.setItem(r, c, item)
        self.setRowHeight(r, 36)

    def add_section_header(self, title: str):
        r = self.rowCount()
        self.insertRow(r)
        self.setSpan(r, 0, 1, self.columnCount())
        item = QTableWidgetItem(f"  {title}")
        item.setBackground(QColor("#0A1628"))
        item.setForeground(self.HEAD_COLOR)
        f = QFont()
        f.setBold(True)
        f.setPointSize(10)
        item.setFont(f)
        self.setItem(r, 0, item)
        self.setRowHeight(r, 32)

    def clear_data(self):
        self.setRowCount(0)