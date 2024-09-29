from typing import List

class LogicalOperatorConditionWrapper(ConditionWrapper):
    def __init__(self, operator: LogicalConditionOperator, logical_operands: List[ConditionWrapper]):
        self._operator = operator
        self._logical_operands = tuple(logical_operands)  # Immutable list (tuple) in Python

    @property
    def operator(self) -> LogicalConditionOperator:
        return self._operator

    @property
    def logical_operands(self) -> List[ConditionWrapper]:
        return self._logical_operands

    def __str__(self) -> str:
        return f"LogicalOperatorConditionWrapper[operator={self._operator}, logicalOperands={self._logical_operands}]"
