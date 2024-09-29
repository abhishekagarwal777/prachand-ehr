from dataclasses import dataclass
from typing import Protocol

# Define placeholder classes for type hints
class AslQuery:
    pass

class AslSourceRelation:
    pass

class AslProvidesJoinCondition(Protocol):
    def get_left_owner(self) -> AslQuery:
        pass

    def get_right_owner(self) -> AslQuery:
        pass

@dataclass(frozen=True)
class AslPathChildCondition(AslProvidesJoinCondition):
    parent_relation: AslSourceRelation
    child_relation: AslSourceRelation
    left_provider: AslQuery
    left_owner: AslQuery
    right_provider: AslQuery
    right_owner: AslQuery

    def get_parent_relation(self) -> AslSourceRelation:
        return self.parent_relation

    def get_child_relation(self) -> AslSourceRelation:
        return self.child_relation

    def get_left_owner(self) -> AslQuery:
        return self.left_owner

    def get_right_owner(self) -> AslQuery:
        return self.right_owner

    def get_left_provider(self) -> AslQuery:
        return self.left_provider

    def get_right_provider(self) -> AslQuery:
        return self.right_provider
