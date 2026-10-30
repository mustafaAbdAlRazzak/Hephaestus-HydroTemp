from .. import config
from .reading import DeviceReading

COIL_RUN = 0
COIL_MANUAL_MODE = 1

HREG_SETPOINT = 0
HREG_KP = 1
HREG_KI = 2
HREG_KD = 3
HREG_MANUAL_OUTPUT = 4

IREG_TEMPERATURE = 0
IREG_HEATER_OUTPUT = 1
IREG_SYSTEM_STATE = 2
IREG_FAULT_CODE = 3
IREG_SAFE_LIMIT = 4
IREG_SETPOINT_MIN = 5
IREG_SETPOINT_MAX = 6
IREG_GAIN_MAX = 7

COIL_COUNT = 2
HREG_COUNT = 5
IREG_COUNT = 8


def to_raw(value, scale):
    return max(0, min(65535, int(round(value * scale))))


def to_raw_signed(value, scale):
    return int(round(value * scale)) & 0xFFFF


def _signed(raw):
    return raw - 65536 if raw >= 32768 else raw


def decode_reading(coils, holding, inputs):
    return DeviceReading(
        running=bool(coils[COIL_RUN]),
        manual_mode=bool(coils[COIL_MANUAL_MODE]),
        setpoint=holding[HREG_SETPOINT] / config.SETPOINT_SCALE,
        kp=holding[HREG_KP] / config.GAIN_SCALE,
        ki=holding[HREG_KI] / config.GAIN_SCALE,
        kd=holding[HREG_KD] / config.GAIN_SCALE,
        manual_output=holding[HREG_MANUAL_OUTPUT] / config.OUTPUT_SCALE,
        temperature=_signed(inputs[IREG_TEMPERATURE]) / config.TEMPERATURE_SCALE,
        heater_output=inputs[IREG_HEATER_OUTPUT] / config.OUTPUT_SCALE,
        system_state=int(inputs[IREG_SYSTEM_STATE]),
        fault_code=int(inputs[IREG_FAULT_CODE]),
        safe_limit=inputs[IREG_SAFE_LIMIT] / config.LIMIT_SCALE,
        setpoint_min=inputs[IREG_SETPOINT_MIN] / config.LIMIT_SCALE,
        setpoint_max=inputs[IREG_SETPOINT_MAX] / config.LIMIT_SCALE,
        gain_max=inputs[IREG_GAIN_MAX] / config.GAIN_SCALE,
    )


def describe_state(code):
    return config.SYSTEM_STATES.get(code, f"CODE {code}")


def describe_fault(code):
    return config.FAULT_CODES.get(code, f"UNKNOWN FAULT {code}")
