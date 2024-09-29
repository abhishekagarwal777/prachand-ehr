from enum import Enum
from typing import List, Union

class JoinType(Enum):
    # Placeholder for the actual JoinType logic. You can extend it based on the SQL join types (INNER, LEFT, RIGHT, etc.).
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class AslJoinCondition:
    # This class should be defined based on the structure of join conditions in your system.
    pass

class AslQuery:
    # Placeholder for the AslQuery class.
    pass

class AslJoin:
    def __init__(self, left: AslQuery, join_type: JoinType, right: AslQuery, on: Union[List[AslJoinCondition], AslJoinCondition]):
        self.left = left
        self.join_type = join_type
        self.right = right
        # Handling both single AslJoinCondition and a list of them
        if isinstance(on, AslJoinCondition):
            self.on = [on]
        else:
            self.on = on

    def get_left(self) -> AslQuery:
        return self.left

    def get_join_type(self) -> JoinType:
        return self.join_type

    def get_right(self) -> AslQuery:
        return self.right

    def get_on(self) -> List[AslJoinCondition]:
        return self.on
