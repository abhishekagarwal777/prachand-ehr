from abc import ABC, abstractmethod

class ServerConfig(ABC):
    
    @abstractmethod
    def get_port(self) -> int:
        """Return the port number the server is running on"""
        pass

    @abstractmethod
    def is_disable_strict_validation(self) -> bool:
        """Return whether strict validation is disabled"""
        pass


class MyServerConfig(ServerConfig):
    
    def __init__(self, port, disable_strict_validation):
        self.port = port
        self.disable_strict_validation = disable_strict_validation

    def get_port(self) -> int:
        return self.port

    def is_disable_strict_validation(self) -> bool:
        return self.disable_strict_validation


config = MyServerConfig(port=8080, disable_strict_validation=True)

print("Server Port:", config.get_port())
print("Is strict validation disabled?", config.is_disable_strict_validation())
