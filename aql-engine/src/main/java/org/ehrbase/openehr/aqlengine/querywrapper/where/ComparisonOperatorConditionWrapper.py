from typing import List, Optional, Union

class ComparisonConditionOperator:
    # Placeholder for the ComparisonConditionOperator class
    pass

class IdentifiedPath:
    # Placeholder for the IdentifiedPath class
    pass

class Primitive:
    # Placeholder for the Primitive class
    pass

class ContainsWrapper:
    # Placeholder for the ContainsWrapper class
    pass

class IdentifiedPathWrapper:
    def __init__(self, root: ContainsWrapper, path: IdentifiedPath):
        self._root = root
        self._path = path

    def get_root(self) -> ContainsWrapper:
        return self._root

    def get_path(self) -> IdentifiedPath:
        return self._path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IdentifiedPathWrapper):
            return False
        return self is other

    def __hash__(self) -> int:
        return id(self)

class ComparisonOperatorConditionWrapper:
    def __init__(self,
                 left_comparison_operand: IdentifiedPathWrapper,
                 operator: ComparisonConditionOperator,
                 right_comparison_operands: List[Primitive]):
        self._left_comparison_operand = left_comparison_operand
        self._operator = operator
        self._right_comparison_operands = tuple(right_comparison_operands)

    def __init__(self,
                 left_comparison_operand: IdentifiedPathWrapper,
                 operator: ComparisonConditionOperator,
                 right_comparison_operand: Primitive):
        self.__init__(left_comparison_operand, operator, [right_comparison_operand])

    def get_left_comparison_operand(self) -> IdentifiedPathWrapper:
        return self._left_comparison_operand

    def get_operator(self) -> ComparisonConditionOperator:
        return self._operator

    def get_right_comparison_operands(self) -> List[Primitive]:
        return list(self._right_comparison_operands)

    def __str__(self) -> str:
        return (f"ComparisonOperatorConditionWrapper[leftComparisonOperand={self._left_comparison_operand}, "
                f"operator={self._operator}, rightComparisonOperands={self._right_comparison_operands}]")

# Example of usage
left_operand = IdentifiedPathWrapper(ContainsWrapper(), IdentifiedPath())
operator = ComparisonConditionOperator()
right_operand = Primitive()

condition_wrapper = ComparisonOperatorConditionWrapper(
    left_comparison_operand=left_operand,
    operator=operator,
    right_comparison_operands=[right_operand]
)
print(condition_wrapper)
