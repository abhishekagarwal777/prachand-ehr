from abc import ABC, abstractmethod

class AslQuery(ABC):
    # Abstract method to be implemented by concrete classes
    @abstractmethod
    def get_alias(self) -> str:
        pass

class AslStructureQuery(AslQuery):
    # Additional structure-related methods can be defined here
    pass

class AslJoinCondition(ABC):
    @abstractmethod
    def get_left_owner(self) -> AslQuery:
        pass

    @abstractmethod
    def get_right_owner(self) -> AslQuery:
        pass

class AslAuditDetailsJoinCondition(AslJoinCondition):
    def __init__(self, left_owner: AslQuery, right_owner: AslStructureQuery):
        self.left_owner = left_owner
        self.right_owner = right_owner

    def get_left_owner(self) -> AslQuery:
        return self.left_owner

    def get_right_owner(self) -> AslStructureQuery:
        return self.right_owner
