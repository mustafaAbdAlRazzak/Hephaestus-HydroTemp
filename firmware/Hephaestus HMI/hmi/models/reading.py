from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceReading:
    running: bool
    manual_mode: bool
    setpoint: float
    kp: float
    ki: float
    kd: float
    manual_output: float
    temperature: float
    heater_output: float
    system_state: int
    fault_code: int
    safe_limit: float
    setpoint_min: float
    setpoint_max: float
    gain_max: float
