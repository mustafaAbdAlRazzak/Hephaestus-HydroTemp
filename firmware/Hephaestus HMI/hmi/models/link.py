from typing import Protocol


class LinkError(Exception):
    pass


class DeviceLink(Protocol):
    @property
    def is_open(self) -> bool: ...

    def open(self) -> bool: ...

    def close(self) -> None: ...

    def read_raw(self): ...

    def write_coil(self, address: int, value: bool) -> None: ...

    def write_register(self, address: int, value: int) -> None: ...
