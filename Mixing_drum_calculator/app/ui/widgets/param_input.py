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
    An input row for parameters:
        [Label]  [QLineEdit]  [Unit]
                 [error_msg]
    """
    value_changed = Signal(float)

    def __init__(self, label_key: str, unit_key: str = "",
                 default: float = 0.0,
                 validator: Callable[[str, str], Tuple[bool, str, float]] = None,
                 tooltip_key: str = "",
                 parent=None):
        super().__init__(parent)
        self._label_key = label_key
        self._unit_key = unit_key
        self._tooltip_key = tooltip_key
        self._validator = validator
        self._valid = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        row = QHBoxLayout()
        row.setSpacing(10)

        # Label
        from app.ui.i18n import _
        self.lbl = QLabel(_(label_key))
        self.lbl.setFixedWidth(260)
        self.lbl.setWordWrap(True)
        row.addWidget(self.lbl)

        # Input
        self.edit = QLineEdit()
        self.edit.setText(str(default))
        self.edit.setFixedWidth(130)
        if tooltip_key:
            self.edit.setToolTip(_(tooltip_key))
        row.addWidget(self.edit)

        # Unit
        self.unit_lbl = QLabel(_(unit_key) if unit_key else "")
        self.unit_lbl.setProperty("type", "unit")
        self.unit_lbl.setFixedWidth(60)
        row.addWidget(self.unit_lbl)

        row.addStretch()
        layout.addLayout(row)

        # Error label
        self.err_lbl = QLabel("")
        self.err_lbl.setProperty("type", "error")
        self.err_lbl.setContentsMargins(270, 0, 0, 0)
        self.err_lbl.setVisible(False)
        layout.addWidget(self.err_lbl)

        self.edit.textChanged.connect(self._on_change)

    def retranslate_ui(self):
        from app.ui.i18n import _
        self.lbl.setText(_(self._label_key))
        if self._unit_key:
            self.unit_lbl.setText(_(self._unit_key))
        if self._tooltip_key:
            self.edit.setToolTip(_(self._tooltip_key))

    def _on_change(self, text: str):
        if self._validator:
            ok, msg, val = self._validator(text, self.lbl.text())
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

    def is_valid(self) -> bool:
        return self._valid

    def get_value(self) -> Tuple[bool, float]:
        text = self.edit.text()
        if self._validator:
            ok, _, val = self._validator(text, self.lbl.text())
            return ok, val
        try:
            val = float(text.replace(',', '.'))
            return True, val
        except ValueError:
            return False, 0.0

    def set_value(self, value: float):
        # Keep the existing validation flow by updating the edit text.
        self.edit.setText(str(value))


class ResultRow(QWidget):
    """A row displaying a result: [Label] [Value] [Unit] [OK/FAIL Badge]"""

    def __init__(self, label_key: str, unit_key: str = "", parent=None):
        super().__init__(parent)
        self._label_key = label_key
        self._unit_key = unit_key
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        from app.ui.i18n import _
        self.lbl = QLabel(_(label_key))
        self.lbl.setFixedWidth(280)
        self.lbl.setWordWrap(True)
        layout.addWidget(self.lbl)

        self.val_lbl = QLabel("—")
        self.val_lbl.setFixedWidth(140)
        self.val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.val_lbl.setStyleSheet("font-weight: bold; color: #DFE6ED;")
        layout.addWidget(self.val_lbl)

        self.u = QLabel(_(unit_key) if unit_key else "")
        self.u.setProperty("type", "unit")
        self.u.setFixedWidth(60)
        layout.addWidget(self.u)

        self.badge = QLabel("")
        self.badge.setFixedWidth(80)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setVisible(False)
        layout.addWidget(self.badge)

        layout.addStretch()

    def retranslate_ui(self):
        from app.ui.i18n import _
        self.lbl.setText(_(self._label_key))
        if self._unit_key:
            self.u.setText(_(self._unit_key))
        if self.badge.isVisible():
            # Current badge logic is internal, might need a refresh flag
            pass

    def set_value(self, v, decimals: int = 4):
        if isinstance(v, float):
            self.val_lbl.setText(f"{v:.{decimals}f}")
        else:
            self.val_lbl.setText(str(v))

    def set_badge(self, ok: bool):
        from app.ui.i18n import _
        self.badge.setVisible(True)
        if ok:
            self.badge.setText(_("badge_ok"))
            self.badge.setStyleSheet(
                "background:#10AC84; color:#fff; border-radius:4px;"
                "padding:3px 8px; font-weight:bold; font-size:11px;"
            )
        else:
            self.badge.setText(_("badge_fail"))
            self.badge.setStyleSheet(
                "background:#EE5A24; color:#fff; border-radius:4px;"
                "padding:3px 8px; font-weight:bold; font-size:11px;"
            )