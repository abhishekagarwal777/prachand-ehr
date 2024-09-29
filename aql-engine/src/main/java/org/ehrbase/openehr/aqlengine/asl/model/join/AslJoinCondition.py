from abc import ABC, abstractmethod

class AslQuery:
    # Placeholder for AslQuery class.
    pass

class AslJoinCondition(ABC):
    @abstractmethod
    def get_left_owner(self) -> AslQuery:
        pass

    @abstractmethod
    def get_right_owner(self) -> AslQuery:
        pass
