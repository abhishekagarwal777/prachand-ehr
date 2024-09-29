from abc import ABC, abstractmethod

class AslQuery(ABC):
    # Define necessary attributes and methods
    @abstractmethod
    def get_alias(self) -> str:
        pass

class AslJoinCondition(ABC):
    @abstractmethod
    def get_left_owner(self) -> 'AslQuery':
        pass

    @abstractmethod
    def get_right_owner(self) -> 'AslQuery':
        pass

class AslAbstractJoinCondition(AslJoinCondition):
    def __init__(self, left_owner: AslQuery, right_owner: AslQuery):
        self.left_owner = left_owner
        self.right_owner = right_owner

    def get_left_owner(self) -> AslQuery:
        return self.left_owner

    def get_right_owner(self) -> AslQuery:
        return self.right_owner
