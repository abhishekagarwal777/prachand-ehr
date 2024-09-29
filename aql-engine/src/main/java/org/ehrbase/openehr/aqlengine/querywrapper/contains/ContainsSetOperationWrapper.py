from typing import List
from dataclasses import dataclass, field

# Assuming ContainmentSetOperatorSymbol and ContainsChain are defined elsewhere
@dataclass(frozen=True)
class ContainsSetOperationWrapper:
    operator: 'ContainmentSetOperatorSymbol'
    operands: List['ContainsChain'] = field(default_factory=list)

    def __post_init__(self):
        # Ensure immutability of the list of operands
        object.__setattr__(self, 'operands', tuple(self.operands))

    def __str__(self) -> str:
        return f"ContainsSetOperationWrapper(operator={self.operator}, operands={self.operands})"

# Example usage
if __name__ == "__main__":
    # Replace 'ContainmentSetOperatorSymbol' and 'ContainsChain' with actual implementations
    operator = None  # Example placeholder
    operands = []  # Example placeholder
    wrapper = ContainsSetOperationWrapper(operator, operands)
    print(wrapper)
