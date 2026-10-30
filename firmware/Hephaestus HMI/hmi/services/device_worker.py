import time
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from ..models import registers
from ..models.link import LinkError


@dataclass(frozen=True)
class WriteOp:
    kind: str
    address: int
    value: int


@dataclass(frozen=True)
class WriteBatch:
    label: str
    ops: tuple = field(default_factory=tuple)
    clears_form: bool = False


class DeviceWorker(QObject):
    polled = Signal(float, object)
    batch_done = Signal(object, bool, str)

    def __init__(self, link, interval_ms):
        super().__init__()
        self._link = link
        self._interval_ms = interval_ms
        self._timer = None

    @Slot()
    def start(self):
        self._timer = QTimer(self)
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._poll)
        self._timer.start()
        self._poll()

    @Slot()
    def stop(self):
        if self._timer is not None:
            self._timer.stop()
        self._link.close()

    def _ensure_open(self):
        if not self._link.is_open and not self._link.open():
            raise LinkError("No connection to controller")

    def _poll(self):
        reading = None
        try:
            self._ensure_open()
            coils, holding, inputs = self._link.read_raw()
            reading = registers.decode_reading(coils, holding, inputs)
        except (LinkError, IndexError):
            self._link.close()
        self.polled.emit(time.time(), reading)

    @Slot(object)
    def execute(self, batch):
        ok = True
        message = ""
        try:
            self._ensure_open()
            for op in batch.ops:
                if op.kind == "coil":
                    self._link.write_coil(op.address, bool(op.value))
                else:
                    self._link.write_register(op.address, op.value)
        except LinkError as exc:
            ok = False
            message = str(exc)
            self._link.close()
        self.batch_done.emit(batch, ok, message)
        self._poll()
