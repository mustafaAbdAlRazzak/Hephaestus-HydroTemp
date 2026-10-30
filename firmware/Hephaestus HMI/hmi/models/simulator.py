import random
import time

from .. import config
from . import registers as reg
from .link import LinkError


class SimulatedLink:
    def __init__(self, speed=1.0):
        self.link_up = True
        self._speed = speed
        self._open = False
        self._coils = [False, False]
        self._hold = [
            reg.to_raw(40.0, config.SETPOINT_SCALE),
            reg.to_raw(10.0, config.GAIN_SCALE),
            reg.to_raw(0.1, config.GAIN_SCALE),
            reg.to_raw(0.0, config.GAIN_SCALE),
            reg.to_raw(0.0, config.OUTPUT_SCALE),
        ]
        self._temperature = 24.0
        self._ambient = 24.0
        self._output = 0.0
        self._integral = 0.0
        self._previous_error = 0.0
        self._fault = 0
        self._safe_limit = 50.0
        self._last = time.monotonic()

    @property
    def is_open(self):
        return self._open and self.link_up

    def open(self):
        self._open = self.link_up
        return self._open

    def close(self):
        self._open = False

    def _require_link(self):
        if not self.link_up:
            raise LinkError("Simulated link is down")

    def _step(self):
        now = time.monotonic()
        dt = min(now - self._last, 5.0) * self._speed
        self._last = now
        running, manual = self._coils
        if running:
            if manual:
                self._output = self._hold[reg.HREG_MANUAL_OUTPUT] / config.OUTPUT_SCALE
            else:
                setpoint = self._hold[reg.HREG_SETPOINT] / config.SETPOINT_SCALE
                kp = self._hold[reg.HREG_KP] / config.GAIN_SCALE
                ki = self._hold[reg.HREG_KI] / config.GAIN_SCALE
                kd = self._hold[reg.HREG_KD] / config.GAIN_SCALE
                error = setpoint - self._temperature
                self._integral = max(0.0, min(100.0, self._integral + ki * error * dt))
                derivative = (error - self._previous_error) / dt if dt > 0 else 0.0
                self._previous_error = error
                self._output = max(0.0, min(100.0, kp * error + self._integral + kd * derivative))
        else:
            self._output = 0.0
            self._integral = 0.0
        power = 800.0 * self._output / 100.0
        loss = 2.0 * (self._temperature - self._ambient)
        self._temperature += dt * (power - loss) / 3000.0
        if self._temperature >= self._safe_limit:
            self._coils[0] = False
            self._fault = 2
            self._output = 0.0

    def read_raw(self):
        self._require_link()
        self._step()
        measured = self._temperature + random.uniform(-0.03, 0.03)
        state = 2 if self._fault else (1 if self._coils[0] else 0)
        inputs = [
            reg.to_raw_signed(measured, config.TEMPERATURE_SCALE),
            reg.to_raw(self._output, config.OUTPUT_SCALE),
            state,
            self._fault,
            reg.to_raw(self._safe_limit, config.LIMIT_SCALE),
            reg.to_raw(20.0, config.LIMIT_SCALE),
            reg.to_raw(45.0, config.LIMIT_SCALE),
            reg.to_raw(50.0, config.GAIN_SCALE),
        ]
        return list(self._coils), list(self._hold), inputs

    def write_coil(self, address, value):
        self._require_link()
        if address == reg.COIL_RUN and value and self._fault:
            if self._temperature < self._safe_limit - 2.0:
                self._fault = 0
                self._coils[0] = True
            return
        self._coils[address] = bool(value)

    def write_register(self, address, value):
        self._require_link()
        self._hold[address] = int(value)
