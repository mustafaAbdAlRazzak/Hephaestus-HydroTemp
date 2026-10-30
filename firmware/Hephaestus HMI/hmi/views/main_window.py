import os
from datetime import datetime

from PySide6.QtCore import QDateTime, QRegularExpression, Qt, QTimer
from PySide6.QtGui import QKeySequence, QRegularExpressionValidator, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..viewmodels.main_viewmodel import MainViewModel
from . import theme
from .export_dialog import ExportDialog
from .trend_panel import TrendPanel

AUTO_FIELDS = (
    ("setpoint", "Setpoint (SP)", "°C"),
    ("kp", "Kp", ""),
    ("ki", "Ki", ""),
    ("kd", "Kd", ""),
)
MANUAL_FIELDS = (("manual_output", "Manual output", "%"),)
STATUS_ROWS = (
    ("link", "Connection"),
    ("system_state", "System state"),
    ("fault", "Fault code"),
    ("mode", "Control mode"),
    ("safe_limit", "Safe temp. limit"),
    ("sp_range", "Setpoint range"),
    ("gain_max", "Max gain"),
)


def set_level(widget, level):
    if widget.property("level") != level:
        widget.setProperty("level", level)
        widget.style().unpolish(widget)
        widget.style().polish(widget)


def make_card(title=None):
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 10, 14, 12)
    layout.setSpacing(8)
    if title:
        label = QLabel(title)
        label.setObjectName("cardTitle")
        layout.addWidget(label)
    return frame, layout


class MainWindow(QMainWindow):
    def __init__(self, viewmodel: MainViewModel):
        super().__init__()
        self._vm = viewmodel
        self._state = None
        self._edits = {}
        self._hint_labels = {}
        self._status_values = {}
        self._progress = None

        self.setWindowTitle("Water Heater PID - HMI")
        self.setStyleSheet(theme.STYLESHEET)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(10)

        layout.addWidget(self._build_top_bar())

        body = QHBoxLayout()
        body.setSpacing(12)
        self._trend = TrendPanel()
        trend_card, trend_layout = make_card()
        trend_layout.addWidget(self._trend)
        body.addWidget(trend_card, 1)
        body.addWidget(self._build_side_panel(), 0)
        layout.addLayout(body, 1)

        self._message = QLabel("")
        self._message.setObjectName("messageBar")
        self._message.setMinimumHeight(30)
        layout.addWidget(self._message)

        self._message_timer = QTimer(self)
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_message)

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(500)
        self._update_clock()

        QShortcut(QKeySequence("F11"), self, activated=self._toggle_fullscreen)

        self._vm.state_changed.connect(self._render)
        self._vm.form_changed.connect(self._load_form)
        self._vm.history_changed.connect(self._refresh_history)
        self._vm.message.connect(self._show_message)
        self._vm.export_progress.connect(self._on_export_progress)
        self._vm.export_finished.connect(self._on_export_finished)
        self._vm.start()

    def _build_top_bar(self):
        bar = QFrame()
        bar.setObjectName("topBar")
        row = QHBoxLayout(bar)
        row.setContentsMargins(16, 8, 12, 8)
        title = QLabel("WATER HEATER PID CONTROL")
        title.setObjectName("appTitle")
        self._link_indicator = QLabel("● OFFLINE")
        self._link_indicator.setObjectName("linkIndicator")
        self._clock = QLabel("")
        self._clock.setObjectName("clock")
        exit_button = QPushButton("EXIT")
        exit_button.setObjectName("exitButton")
        exit_button.setToolTip("Close the HMI (the controller keeps running)")
        exit_button.clicked.connect(self.close)
        row.addWidget(title)
        row.addStretch(1)
        row.addWidget(self._link_indicator)
        row.addSpacing(18)
        row.addWidget(self._clock)
        row.addSpacing(18)
        row.addWidget(exit_button)
        return bar

    def _build_side_panel(self):
        content = QWidget()
        column = QVBoxLayout(content)
        column.setContentsMargins(0, 0, 6, 0)
        column.setSpacing(10)

        self._banner = QLabel("CONNECTING...")
        self._banner.setObjectName("banner")
        self._banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(self._banner)

        column.addWidget(self._build_readouts())
        column.addWidget(self._build_control())
        column.addWidget(self._build_parameters())
        column.addWidget(self._build_status())

        export_button = QPushButton("EXPORT TO EXCEL")
        export_button.setMinimumHeight(46)
        export_button.clicked.connect(self._on_export)
        column.addWidget(export_button)
        column.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        scroll.setFixedWidth(440)
        return scroll

    def _build_readouts(self):
        card, layout = make_card("TEMPERATURE")
        self._pv_label = QLabel("----")
        self._pv_label.setObjectName("bigValue")
        layout.addWidget(self._pv_label)

        row = QHBoxLayout()
        sp_box = QVBoxLayout()
        sp_title = QLabel("TARGET")
        sp_title.setObjectName("cardTitle")
        self._sp_label = QLabel("----")
        self._sp_label.setObjectName("spValue")
        sp_box.addWidget(sp_title)
        sp_box.addWidget(self._sp_label)
        out_box = QVBoxLayout()
        out_title = QLabel("HEATER OUTPUT")
        out_title.setObjectName("cardTitle")
        self._out_label = QLabel("----")
        self._out_label.setObjectName("midValue")
        out_box.addWidget(out_title)
        out_box.addWidget(self._out_label)
        row.addLayout(sp_box, 1)
        row.addLayout(out_box, 1)
        layout.addLayout(row)
        return card

    def _build_control(self):
        card, layout = make_card("CONTROL")
        mode_row = QHBoxLayout()
        mode_row.setSpacing(0)
        self._auto_button = QPushButton("AUTO (PID)")
        self._manual_button = QPushButton("MANUAL")
        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)
        for button in (self._auto_button, self._manual_button):
            button.setObjectName("modeButton")
            button.setCheckable(True)
            self._mode_group.addButton(button)
            mode_row.addWidget(button, 1)
        self._auto_button.setChecked(True)
        self._auto_button.clicked.connect(lambda: self._on_mode_clicked(False))
        self._manual_button.clicked.connect(lambda: self._on_mode_clicked(True))
        layout.addLayout(mode_row)

        self._run_button = QPushButton("START SYSTEM")
        self._run_button.setObjectName("runButton")
        self._run_button.setProperty("level", "start")
        self._run_button.clicked.connect(self._vm.request_toggle_run)
        layout.addWidget(self._run_button)
        return card

    def _build_parameters(self):
        card, layout = make_card("PARAMETERS")
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_field_page(AUTO_FIELDS))
        self._stack.addWidget(self._build_field_page(MANUAL_FIELDS))
        layout.addWidget(self._stack)

        self._lock_note = QLabel("Locked while the system is running")
        self._lock_note.setObjectName("lockNote")
        self._lock_note.setVisible(False)
        layout.addWidget(self._lock_note)

        buttons = QHBoxLayout()
        self._apply_button = QPushButton("APPLY VALUES")
        self._apply_button.clicked.connect(self._vm.request_apply)
        self._reload_button = QPushButton("RELOAD")
        self._reload_button.setToolTip("Discard typed values and read them again from the controller")
        self._reload_button.clicked.connect(self._vm.reload_form)
        buttons.addWidget(self._apply_button, 2)
        buttons.addWidget(self._reload_button, 1)
        layout.addLayout(buttons)
        return card

    def _build_field_page(self, fields):
        page = QWidget()
        grid = QGridLayout(page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(1, 1)
        validator = QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]*$"))
        for row, (key, title, unit) in enumerate(fields):
            label = QLabel(f"{title} [{unit}]" if unit else title)
            edit = QLineEdit("----")
            edit.setAlignment(Qt.AlignmentFlag.AlignRight)
            edit.setValidator(validator)
            edit.setMinimumWidth(130)
            edit.textEdited.connect(lambda text, k=key: self._vm.form_edited(k, text))
            edit.returnPressed.connect(self._vm.request_apply)
            hint = QLabel("")
            hint.setObjectName("hint")
            hint.setMinimumWidth(110)
            grid.addWidget(label, row, 0)
            grid.addWidget(edit, row, 1)
            grid.addWidget(hint, row, 2)
            self._edits[key] = edit
            self._hint_labels[key] = hint
        return page

    def _build_status(self):
        card, layout = make_card("SYSTEM STATUS")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)
        for row, (key, title) in enumerate(STATUS_ROWS):
            name = QLabel(title)
            name.setObjectName("statusName")
            value = QLabel("----")
            value.setObjectName("statusValue")
            value.setWordWrap(True)
            grid.addWidget(name, row, 0)
            grid.addWidget(value, row, 1)
            self._status_values[key] = value
        layout.addLayout(grid)
        return card

    def _render(self, state):
        self._state = state
        self._pv_label.setText(state.temperature_text)
        self._sp_label.setText(state.setpoint_text)
        self._out_label.setText(state.output_text)

        self._banner.setText(state.banner_text)
        set_level(self._banner, state.banner_level)
        self._link_indicator.setText(f"● {state.link_text}")
        set_level(self._link_indicator, state.link_level)

        self._auto_button.setChecked(not state.manual_mode)
        self._manual_button.setChecked(state.manual_mode)
        self._auto_button.setEnabled(state.mode_switch_enabled)
        self._manual_button.setEnabled(state.mode_switch_enabled)
        self._stack.setCurrentIndex(1 if state.manual_mode else 0)

        for edit in self._edits.values():
            edit.setEnabled(state.fields_enabled)
        for key, hint in self._hint_labels.items():
            hint.setText(state.hints.get(key, ""))
        self._apply_button.setEnabled(state.apply_enabled)
        self._reload_button.setEnabled(state.apply_enabled)
        self._lock_note.setVisible(state.locked_note_visible)

        self._run_button.setText(state.run_button_text)
        self._run_button.setEnabled(state.run_button_enabled)
        set_level(self._run_button, state.run_button_level)

        for key, value_label in self._status_values.items():
            value_label.setText(state.status_rows.get(key, "----"))
        set_level(self._status_values["fault"], "error" if state.fault_active else "")

        self._trend.set_safe_limit(state.safe_limit)

    def _load_form(self, values):
        for key, text in values.items():
            edit = self._edits.get(key)
            if edit is not None and edit.text() != text:
                edit.setText(text)

    def _refresh_history(self):
        times, temperature, setpoint = self._vm.history()
        self._trend.set_history(times, temperature, setpoint)

    def _on_mode_clicked(self, manual):
        self._vm.request_mode(manual)
        if self._state is not None:
            self._render(self._state)

    def _show_message(self, text, level):
        stamp = datetime.now().strftime("%H:%M:%S")
        self._message.setText(f"[{stamp}]  {text}")
        set_level(self._message, level)
        self._message_timer.start(9000)

    def _clear_message(self):
        self._message.setText("")
        set_level(self._message, "")

    def _update_clock(self):
        self._clock.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd  HH:mm:ss"))

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def _on_export(self):
        data_range = self._vm.data_range()
        if data_range is None:
            self._show_message("There is no data to export yet", "error")
            return
        dialog = ExportDialog(data_range[0], data_range[1], self)
        if dialog.exec() != ExportDialog.DialogCode.Accepted:
            return
        start, end = dialog.selected_range()
        default_name = datetime.now().strftime("water_heater_%Y%m%d_%H%M%S.xlsx")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel file", os.path.join(os.path.expanduser("~"), default_name), "Excel workbook (*.xlsx)"
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        self._progress = QProgressDialog("Exporting data...", "", 0, 100, self)
        self._progress.setCancelButton(None)
        self._progress.setWindowTitle("Export to Excel")
        self._progress.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress.setMinimumDuration(0)
        self._progress.setAutoClose(False)
        self._progress.setAutoReset(False)
        self._progress.setValue(0)
        self._vm.start_export(path, start, end)

    def _on_export_progress(self, value):
        if self._progress is not None:
            self._progress.setValue(value)

    def _on_export_finished(self, ok, text):
        if self._progress is not None:
            self._progress.close()
            self._progress = None
        if ok:
            QMessageBox.information(self, "Export to Excel", text)
            self._show_message("Excel export finished", "ok")
        else:
            QMessageBox.warning(self, "Export to Excel", text)
            self._show_message(text, "error")

    def closeEvent(self, event):
        running = self._state is not None and self._state.running
        if running:
            answer = QMessageBox.question(
                self,
                "Exit HMI",
                "The system is running.\nClosing the HMI does not stop the controller.\n\nExit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self._vm.shutdown()
        event.accept()
