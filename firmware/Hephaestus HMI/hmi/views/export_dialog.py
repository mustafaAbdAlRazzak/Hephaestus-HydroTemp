from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

DISPLAY_FORMAT = "yyyy-MM-dd HH:mm:ss"


class ExportDialog(QDialog):
    PRESETS = (("Last 5 min", 300), ("Last 30 min", 1800), ("Last 1 hour", 3600), ("Last 6 hours", 21600))

    def __init__(self, first, last, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export to Excel")
        self.setModal(True)
        self._first = int(first)
        self._last = int(last)

        first_time = QDateTime.fromSecsSinceEpoch(self._first)
        last_time = QDateTime.fromSecsSinceEpoch(self._last)

        self._start = QDateTimeEdit()
        self._end = QDateTimeEdit()
        for editor in (self._start, self._end):
            editor.setDisplayFormat(DISPLAY_FORMAT)
            editor.setCalendarPopup(True)
            editor.setMinimumDateTime(first_time)
            editor.setMaximumDateTime(last_time)
        self._start.setDateTime(first_time)
        self._end.setDateTime(last_time)

        available = QLabel(
            f"Available data: {first_time.toString(DISPLAY_FORMAT)}  to  {last_time.toString(DISPLAY_FORMAT)}"
        )
        available.setObjectName("hint")

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        grid.addWidget(QLabel("From"), 0, 0)
        grid.addWidget(self._start, 0, 1)
        grid.addWidget(QLabel("To"), 1, 0)
        grid.addWidget(self._end, 1, 1)

        presets = QHBoxLayout()
        for title, seconds in self.PRESETS:
            button = QPushButton(title)
            button.clicked.connect(lambda _checked=False, s=seconds: self._apply_preset(s))
            presets.addWidget(button)
        all_button = QPushButton("All data")
        all_button.clicked.connect(lambda _checked=False: self._apply_preset(None))
        presets.addWidget(all_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("CHOOSE FILE...")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.addWidget(available)
        layout.addLayout(grid)
        layout.addLayout(presets)
        layout.addWidget(buttons)
        self.setMinimumWidth(560)

    def _apply_preset(self, seconds):
        end = self._last
        start = self._first if seconds is None else max(self._first, end - seconds)
        self._start.setDateTime(QDateTime.fromSecsSinceEpoch(start))
        self._end.setDateTime(QDateTime.fromSecsSinceEpoch(end))

    def _on_accept(self):
        if self._start.dateTime() >= self._end.dateTime():
            QMessageBox.warning(self, "Export to Excel", "The start time must be earlier than the end time.")
            return
        self.accept()

    def selected_range(self):
        return float(self._start.dateTime().toSecsSinceEpoch()), float(self._end.dateTime().toSecsSinceEpoch())
