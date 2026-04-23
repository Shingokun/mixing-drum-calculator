# ============================================================
# widgets/param_input.py — Input field với validation tích hợp
# ============================================================
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit
)
from PySide6.QtCore import Signal, Qt
from typing import Callable, Tuple


class ParamInput(QWidget):
    """
    Một hàng nhập thông số:
        [Label]  [QLineEdit]  [Unit]
                 [error_msg]
    """
    value_changed = Signal(float)

    def __init__(self, label: str, unit: str = "",
                 default: float = 0.0,
                 validator: Callable[[str, str], Tuple[bool, str, float]] = None,
                 tooltip: str = "",
                 parent=None):
        super().__init__(parent)
        self._label_text = label
        self._unit = unit
        self._validator = validator
        self._valid = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        row = QHBoxLayout()
        row.setSpacing(10)

        # Label
        lbl = QLabel(label)
        lbl.setFixedWidth(260)
        lbl.setWordWrap(True)
        row.addWidget(lbl)

        # Input
        self.edit = QLineEdit()
        self.edit.setText(str(default))
        self.edit.setFixedWidth(130)
        if tooltip:
            self.edit.setToolTip(tooltip)
        row.addWidget(self.edit)

        # Unit
        if unit:
            unit_lbl = QLabel(unit)
            unit_lbl.setProperty("type", "unit")
            unit_lbl.setFixedWidth(60)
            row.addWidget(unit_lbl)

        row.addStretch()
        layout.addLayout(row)

        # Error label
        self.err_lbl = QLabel("")
        self.err_lbl.setProperty("type", "error")
        self.err_lbl.setContentsMargins(270, 0, 0, 0)
        self.err_lbl.setVisible(False)
        layout.addWidget(self.err_lbl)

        self.edit.textChanged.connect(self._on_change)

    def _on_change(self, text: str):
        if self._validator:
            ok, msg, val = self._validator(text, self._label_text)
            self._valid = ok
            self.edit.setProperty("valid", "true" if ok else "false")
            self.edit.style().unpolish(self.edit)
            self.edit.style().polish(self.edit)
            if ok:
                self.err_lbl.setVisible(False)
                self.value_changed.emit(val)
            else:
                self.err_lbl.setText(msg)
                self.err_lbl.setVisible(True)
        else:
            try:
                val = float(text.replace(',', '.'))
                self._valid = True
                self.value_changed.emit(val)
            except ValueError:
                self._valid = False

    def get_value(self) -> Tuple[bool, float]:
        if self._validator:
            ok, _, val = self._validator(self.edit.text(), self._label_text)
            return ok, val
        try:
            return True, float(self.edit.text().replace(',', '.'))
        except ValueError:
            return False, 0.0

    def set_value(self, v: float):
        self.edit.setText(f"{v:.4g}")

    def is_valid(self) -> bool:
        if self._validator:
            ok, _, _ = self._validator(self.edit.text(), self._label_text)
            return ok
        try:
            float(self.edit.text())
            return True
        except ValueError:
            return False

    def set_enabled(self, en: bool):
        self.edit.setEnabled(en)


class ResultRow(QWidget):
    """Một hàng hiển thị kết quả: [Label] [Giá trị] [Unit] [Badge OK/FAIL]"""

    def __init__(self, label: str, unit: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        lbl = QLabel(label)
        lbl.setFixedWidth(280)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        self.val_lbl = QLabel("—")
        self.val_lbl.setFixedWidth(140)
        self.val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.val_lbl.setStyleSheet("font-weight: bold; color: #DFE6ED;")
        layout.addWidget(self.val_lbl)

        if unit:
            u = QLabel(unit)
            u.setProperty("type", "unit")
            u.setFixedWidth(60)
            layout.addWidget(u)

        self.badge = QLabel("")
        self.badge.setFixedWidth(80)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setVisible(False)
        layout.addWidget(self.badge)

        layout.addStretch()

    def set_value(self, v, decimals: int = 4):
        if isinstance(v, float):
            self.val_lbl.setText(f"{v:.{decimals}f}")
        else:
            self.val_lbl.setText(str(v))

    def set_badge(self, ok: bool):
        self.badge.setVisible(True)
        if ok:
            self.badge.setText("✓ ĐẠT")
            self.badge.setStyleSheet(
                "background:#10AC84; color:#fff; border-radius:4px;"
                "padding:3px 8px; font-weight:bold; font-size:11px;"
            )
        else:
            self.badge.setText("✗ KHÔNG ĐẠT")
            self.badge.setStyleSheet(
                "background:#EE5A24; color:#fff; border-radius:4px;"
                "padding:3px 8px; font-weight:bold; font-size:11px;"
            )