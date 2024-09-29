from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field

@dataclass
class AslField:
    pass

@dataclass
class AslPathFilterJoinCondition:
    pass

@dataclass
class IdentifiedPath:
    pass

@dataclass
class AslQueryCondition:
    pass

@dataclass
class AslAndQueryCondition(AslQueryCondition):
    operands: List[AslQueryCondition]

@dataclass
class AslOrQueryCondition(AslQueryCondition):
    operands: List[AslQueryCondition]

class AslQuery:
    def __init__(self, alias: str, structure_conditions: List[AslQueryCondition]):
        self.alias = alias
        self.structure_conditions = structure_conditions
        self.condition: Optional[AslQueryCondition] = None

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        raise NotImplementedError("Subclasses should implement this method")

    def get_select(self) -> List[AslField]:
        raise NotImplementedError("Subclasses should implement this method")

    def get_alias(self) -> str:
        return self.alias

    def get_condition(self) -> Optional[AslQueryCondition]:
        return self.condition

    def set_condition(self, condition: AslQueryCondition) -> None:
        self.condition = condition

    def add_condition_and(self, to_add: AslQueryCondition) -> 'AslQuery':
        if self.condition is None:
            self.condition = to_add
        elif isinstance(self.condition, AslAndQueryCondition):
            self.condition.operands.append(to_add)
        else:
            self.condition = AslAndQueryCondition(operands=[self.condition, to_add])
        return self

    def add_condition_or(self, to_add: AslQueryCondition) -> 'AslQuery':
        if self.condition is None:
            self.condition = to_add
        elif isinstance(self.condition, AslOrQueryCondition):
            self.condition.operands.append(to_add)
        else:
            self.condition = AslOrQueryCondition(operands=[self.condition, to_add])
        return self

    def get_structure_conditions(self) -> List[AslQueryCondition]:
        return self.structure_conditions.copy()
