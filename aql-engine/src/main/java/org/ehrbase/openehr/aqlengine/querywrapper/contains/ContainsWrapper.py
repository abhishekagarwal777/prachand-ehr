from abc import ABC, abstractmethod

class ContainsWrapper(ABC):
    @abstractmethod
    def get_rm_type(self) -> str:
        """
        Should return the RM type as a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def alias(self) -> str:
        """
        Should return the alias as a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")
