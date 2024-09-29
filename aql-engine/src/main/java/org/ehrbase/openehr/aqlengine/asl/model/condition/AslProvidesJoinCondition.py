from typing import Protocol

class AslQuery:
    pass

class AslDelegatingJoinCondition:
    def __init__(self, condition: 'AslProvidesJoinCondition'):
        self.condition = condition

class AslProvidesJoinCondition(Protocol):
    def get_left_owner(self) -> AslQuery:
        ...

    def get_right_owner(self) -> AslQuery:
        ...

    def provide_join_condition(self) -> AslDelegatingJoinCondition:
        return AslDelegatingJoinCondition(self)

    def with_provider(self, provider: AslQuery) -> None:
        raise NotImplementedError("Operation not supported")
