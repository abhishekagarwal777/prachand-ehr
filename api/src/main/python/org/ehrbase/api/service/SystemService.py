from abc import ABC, abstractmethod

class SystemService(ABC):

    @abstractmethod
    def get_system_id(self) -> str:
        """
        Retrieves the system identifier.
        """
        pass
