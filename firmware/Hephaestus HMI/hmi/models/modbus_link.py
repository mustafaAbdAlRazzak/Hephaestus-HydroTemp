import inspect

from pymodbus.client import ModbusTcpClient

from . import registers as reg
from .link import LinkError


class ModbusLink:
    def __init__(self, host, port, unit_id, timeout):
        self._unit_id = unit_id
        try:
            self._client = ModbusTcpClient(host, port=port, timeout=timeout, retries=1)
        except TypeError:
            self._client = ModbusTcpClient(host, port=port, timeout=timeout)
        self._unit_kwargs = self._detect_unit_kwargs()

    def _detect_unit_kwargs(self):
        try:
            params = inspect.signature(self._client.read_coils).parameters
        except (TypeError, ValueError):
            return {}
        for name in ("device_id", "slave", "unit"):
            if name in params:
                return {name: self._unit_id}
        return {}

    @property
    def is_open(self):
        return bool(getattr(self._client, "connected", False))

    def open(self):
        try:
            return bool(self._client.connect())
        except Exception:
            return False

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass

    def _call(self, function, address, **kwargs):
        try:
            response = function(address, **kwargs, **self._unit_kwargs)
        except Exception as exc:
            raise LinkError(str(exc) or exc.__class__.__name__) from exc
        if response is None or response.isError():
            raise LinkError(str(response) if response is not None else "No response")
        return response

    def read_raw(self):
        coils = self._call(self._client.read_coils, 0, count=reg.COIL_COUNT).bits
        holding = self._call(self._client.read_holding_registers, 0, count=reg.HREG_COUNT).registers
        inputs = self._call(self._client.read_input_registers, 0, count=reg.IREG_COUNT).registers
        if len(coils) < reg.COIL_COUNT or len(holding) < reg.HREG_COUNT or len(inputs) < reg.IREG_COUNT:
            raise LinkError("Incomplete response")
        return list(coils[: reg.COIL_COUNT]), list(holding), list(inputs)

    def write_coil(self, address, value):
        self._call(self._client.write_coil, address, value=bool(value))

    def write_register(self, address, value):
        self._call(self._client.write_register, address, value=int(value))
