import threading

from PySide6.QtCore import QMetaObject, QObject, QThread, Qt, Signal

from .. import config
from ..models import registers as reg
from ..models.excel_exporter import export_to_excel
from ..services.device_worker import WriteBatch, WriteOp
from .view_state import PLACEHOLDER, ViewState

FORM_KEYS = ("setpoint", "kp", "ki", "kd", "manual_output")


class MainViewModel(QObject):
    state_changed = Signal(object)
    history_changed = Signal()
    form_changed = Signal(object)
    message = Signal(str, str)
    export_progress = Signal(int)
    export_finished = Signal(bool, str)
    _submit = Signal(object)

    def __init__(self, worker, store, endpoint_text, parent=None):
        super().__init__(parent)
        self._worker = worker
        self._store = store
        self._endpoint = endpoint_text
        self._reading = None
        self._last_good = None
        self._polled_once = False
        self._busy = False
        self._dirty = False
        self._form = {key: PLACEHOLDER for key in FORM_KEYS}
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.start)
        self._worker.polled.connect(self._on_polled)
        self._worker.batch_done.connect(self._on_batch_done)
        self._submit.connect(self._worker.execute)

    def start(self):
        self.state_changed.emit(self._build_state())
        self.form_changed.emit(dict(self._form))
        self._thread.start()

    def shutdown(self):
        if self._thread.isRunning():
            QMetaObject.invokeMethod(self._worker, "stop", Qt.ConnectionType.BlockingQueuedConnection)
            self._thread.quit()
            self._thread.wait(3000)

    def history(self):
        return self._store.times(), self._store.column("temperature"), self._store.column("setpoint")

    def current_state(self):
        return self._build_state()

    def data_range(self):
        return self._store.time_range()

    def form_edited(self, key, text):
        self._form[key] = text
        self._dirty = True

    def reload_form(self):
        self._dirty = False
        self._form = {key: PLACEHOLDER for key in FORM_KEYS}
        self._sync_form(force=True)

    def request_mode(self, manual):
        reading = self._reading
        if reading is None:
            self.message.emit("No connection to controller", "error")
            return
        if reading.running:
            self.message.emit("Stop the system before changing the control mode", "error")
            return
        if reading.manual_mode == manual:
            return
        label = "MANUAL" if manual else "AUTO (PID)"
        self._send(WriteBatch(f"Control mode set to {label}", (WriteOp("coil", reg.COIL_MANUAL_MODE, int(manual)),)))

    def request_toggle_run(self):
        reading = self._reading
        if reading is None:
            self.message.emit("No connection to controller", "error")
            return
        if reading.running:
            self._send(WriteBatch("System stopped", (WriteOp("coil", reg.COIL_RUN, 0),)))
            return
        try:
            ops = self._value_ops(reading.manual_mode)
        except ValueError as exc:
            self.message.emit(str(exc), "error")
            return
        ops.append(WriteOp("coil", reg.COIL_RUN, 1))
        self._send(WriteBatch("System started", tuple(ops), clears_form=True))

    def request_apply(self):
        reading = self._reading
        if reading is None:
            self.message.emit("No connection to controller", "error")
            return
        if reading.running:
            self.message.emit("Values are locked while the system is running", "error")
            return
        try:
            ops = self._value_ops(reading.manual_mode)
        except ValueError as exc:
            self.message.emit(str(exc), "error")
            return
        self._send(WriteBatch("Values applied", tuple(ops), clears_form=True))

    def start_export(self, path, start, end):
        range_ = self._store.time_range()
        if range_ is None:
            self.export_finished.emit(False, "There is no data to export yet")
            return
        start = max(start, range_[0])
        end = min(end, range_[1])
        snapshot = self._store.snapshot(start, end)
        if len(snapshot) == 0 or end < start:
            self.export_finished.emit(False, "There is no data in the selected time range")
            return

        def job():
            try:
                rows, missing = export_to_excel(path, snapshot, start, end, self.export_progress.emit)
            except Exception as exc:
                self.export_finished.emit(False, f"Export failed: {exc}")
                return
            self.export_finished.emit(True, f"Exported {rows} rows ({missing} seconds without data)\n{path}")

        threading.Thread(target=job, daemon=True).start()

    def _send(self, batch):
        self._busy = True
        self.state_changed.emit(self._build_state())
        self._submit.emit(batch)

    def _on_batch_done(self, batch, ok, error):
        self._busy = False
        if ok:
            if batch.clears_form:
                self._dirty = False
            self.message.emit(batch.label, "ok")
        else:
            self.message.emit(f"Write failed: {error}", "error")
        self.state_changed.emit(self._build_state())

    def _on_polled(self, timestamp, reading):
        self._polled_once = True
        self._reading = reading
        if reading is not None:
            self._last_good = reading
        self._store.append(timestamp, reading)
        self._sync_form()
        self.history_changed.emit()
        self.state_changed.emit(self._build_state())

    def _sync_form(self, force=False):
        if self._dirty and not force:
            return
        reading = self._reading
        if reading is None:
            target = {key: PLACEHOLDER for key in FORM_KEYS}
        else:
            target = {
                "setpoint": f"{reading.setpoint:.1f}",
                "kp": f"{reading.kp:.2f}",
                "ki": f"{reading.ki:.2f}",
                "kd": f"{reading.kd:.2f}",
                "manual_output": f"{reading.manual_output:.1f}",
            }
        if target != self._form or force:
            self._form = target
            self.form_changed.emit(dict(target))

    def _parse(self, key, label, low, high, unit):
        text = self._form[key].strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            raise ValueError(f"{label}: enter a valid number") from None
        if not low <= value <= high:
            raise ValueError(f"{label} must be between {low:g} and {high:g} {unit}".strip())
        return value

    def _value_ops(self, manual):
        limits = self._last_good
        if limits is None:
            raise ValueError("No connection to controller")
        if manual:
            output = self._parse("manual_output", "Manual output", 0.0, 100.0, "%")
            return [WriteOp("register", reg.HREG_MANUAL_OUTPUT, reg.to_raw(output, config.OUTPUT_SCALE))]
        setpoint = self._parse("setpoint", "Setpoint", limits.setpoint_min, limits.setpoint_max, "°C")
        kp = self._parse("kp", "Kp", 0.0, limits.gain_max, "")
        ki = self._parse("ki", "Ki", 0.0, limits.gain_max, "")
        kd = self._parse("kd", "Kd", 0.0, limits.gain_max, "")
        return [
            WriteOp("register", reg.HREG_SETPOINT, reg.to_raw(setpoint, config.SETPOINT_SCALE)),
            WriteOp("register", reg.HREG_KP, reg.to_raw(kp, config.GAIN_SCALE)),
            WriteOp("register", reg.HREG_KI, reg.to_raw(ki, config.GAIN_SCALE)),
            WriteOp("register", reg.HREG_KD, reg.to_raw(kd, config.GAIN_SCALE)),
        ]

    def _build_state(self):
        reading = self._reading
        known = reading or self._last_good
        connected = reading is not None
        running = bool(reading and reading.running)
        manual = bool(known.manual_mode) if known else False
        fault_active = bool(reading and reading.fault_code != 0)

        state = ViewState(connected=connected, running=running, manual_mode=manual, busy=self._busy)
        state.fault_active = fault_active
        state.safe_limit = known.safe_limit if known else None

        if connected:
            state.temperature_text = f"{reading.temperature:.1f} °C"
            state.setpoint_text = f"{reading.setpoint:.1f} °C"
            state.output_text = f"{reading.heater_output:.1f} %"
            state.link_text = "ONLINE"
            state.link_level = "ok"
            mode_text = "MANUAL" if manual else "AUTO (PID)"
            if fault_active:
                state.banner_text = f"FAULT {reading.fault_code}: {reg.describe_fault(reading.fault_code)}"
                state.banner_level = "error"
            elif running:
                state.banner_text = f"RUNNING - {mode_text}"
                state.banner_level = "ok"
            else:
                state.banner_text = f"STOPPED - {mode_text}"
                state.banner_level = "idle"
        else:
            state.banner_text = "NO CONNECTION" if self._polled_once else "CONNECTING..."
            state.banner_level = "warn"

        state.mode_switch_enabled = connected and not running and not self._busy
        state.fields_enabled = connected and not running and not self._busy
        state.apply_enabled = state.fields_enabled
        state.locked_note_visible = connected and running
        state.run_button_enabled = connected and not self._busy
        state.run_button_text = "STOP SYSTEM" if running else "START SYSTEM"
        state.run_button_level = "stop" if running else "start"

        rows = {
            "link": f"{state.link_text}  ({self._endpoint})",
            "system_state": PLACEHOLDER,
            "fault": PLACEHOLDER,
            "mode": PLACEHOLDER,
            "safe_limit": PLACEHOLDER,
            "sp_range": PLACEHOLDER,
            "gain_max": PLACEHOLDER,
        }
        if connected:
            rows["system_state"] = f"{reading.system_state} - {reg.describe_state(reading.system_state)}"
            rows["fault"] = f"{reading.fault_code} - {reg.describe_fault(reading.fault_code)}"
            rows["mode"] = "MANUAL" if manual else "AUTO (PID)"
            rows["safe_limit"] = f"{reading.safe_limit:.1f} °C"
            rows["sp_range"] = f"{reading.setpoint_min:.1f} to {reading.setpoint_max:.1f} °C"
            rows["gain_max"] = f"{reading.gain_max:g}"
        state.status_rows = rows

        hints = {key: "" for key in FORM_KEYS}
        if known:
            hints["setpoint"] = f"{known.setpoint_min:.1f} - {known.setpoint_max:.1f} °C"
            for key in ("kp", "ki", "kd"):
                hints[key] = f"0 - {known.gain_max:g}"
            hints["manual_output"] = "0 - 100 %"
        state.hints = hints
        return state
