import numpy as np

FIELDS = (
    "connected",
    "running",
    "manual_mode",
    "temperature",
    "setpoint",
    "heater_output",
    "manual_output",
    "kp",
    "ki",
    "kd",
    "system_state",
    "fault_code",
)
INDEX = {name: position for position, name in enumerate(FIELDS)}


class Snapshot:
    def __init__(self, times, data):
        self.times = times
        self.data = data

    def __len__(self):
        return len(self.times)

    def column(self, name):
        return self.data[:, INDEX[name]]


class SampleStore:
    def __init__(self, max_samples, initial_capacity=4096):
        self._max = max_samples
        self._times = np.empty(initial_capacity, dtype=np.float64)
        self._data = np.full((initial_capacity, len(FIELDS)), np.nan, dtype=np.float64)
        self._count = 0

    @property
    def count(self):
        return self._count

    def _make_room(self):
        capacity = len(self._times)
        if capacity < self._max:
            new_capacity = min(self._max, capacity * 2)
            times = np.empty(new_capacity, dtype=np.float64)
            data = np.full((new_capacity, len(FIELDS)), np.nan, dtype=np.float64)
            times[: self._count] = self._times[: self._count]
            data[: self._count] = self._data[: self._count]
            self._times, self._data = times, data
            return
        drop = max(1, self._max // 10)
        keep = self._count - drop
        self._times[:keep] = self._times[drop : self._count]
        self._data[:keep] = self._data[drop : self._count]
        self._count = keep

    def append(self, timestamp, reading):
        if self._count >= len(self._times):
            self._make_room()
        i = self._count
        self._times[i] = timestamp
        row = self._data[i]
        if reading is None:
            row[:] = np.nan
            row[INDEX["connected"]] = 0.0
        else:
            row[:] = (
                1.0,
                float(reading.running),
                float(reading.manual_mode),
                reading.temperature,
                reading.setpoint,
                reading.heater_output,
                reading.manual_output,
                reading.kp,
                reading.ki,
                reading.kd,
                float(reading.system_state),
                float(reading.fault_code),
            )
        self._count += 1

    def times(self):
        return self._times[: self._count]

    def column(self, name):
        return self._data[: self._count, INDEX[name]]

    def time_range(self):
        if self._count == 0:
            return None
        return float(self._times[0]), float(self._times[self._count - 1])

    def snapshot(self, start, end):
        times = self._times[: self._count]
        low = int(np.searchsorted(times, start, side="left"))
        high = int(np.searchsorted(times, end, side="right"))
        return Snapshot(times[low:high].copy(), self._data[low:high].copy())
