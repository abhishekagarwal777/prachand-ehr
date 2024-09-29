from typing import Protocol

class ServerConfig(Protocol):
    def get_port(self) -> int:
        ...
    def is_disable_strict_validation(self) -> bool:
        ...

class NopServerConfig(ServerConfig):
    def __init__(self) -> None:
        self._disable_strict_validation = False

    def get_port(self) -> int:
        return -1

    def set_port(self, port: int) -> None:
        # ignored
        pass

    def set_disable_strict_validation(self, disable_strict_validation: bool) -> None:
        self._disable_strict_validation = disable_strict_validation

    def is_disable_strict_validation(self) -> bool:
        return self._disable_strict_validation
