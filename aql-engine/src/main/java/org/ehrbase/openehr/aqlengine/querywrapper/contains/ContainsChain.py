from typing import List, Optional
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ContainsWrapper:
    # Placeholder for the actual implementation
    pass

@dataclass(frozen=True)
class ContainsSetOperationWrapper:
    # Placeholder for the actual implementation
    pass

@dataclass(frozen=True)
class ContainsChain:
    chain: List[ContainsWrapper] = field(default_factory=list)
    trailing_set_operation: Optional[ContainsSetOperationWrapper] = None

    def has_trailing_set_operation(self) -> bool:
        return self.trailing_set_operation is not None

    def size(self) -> int:
        return len(self.chain) + (1 if self.has_trailing_set_operation() else 0)

    def __str__(self) -> str:
        return (f"ContainsChain[chain={self.chain}, "
                f"trailing_set_operation={self.trailing_set_operation}]")

# Example usage
if __name__ == "__main__":
    # Example instances; replace with actual implementations
    wrapper = ContainsWrapper()
    set_operation = ContainsSetOperationWrapper()
    chain = ContainsChain(
        chain=[wrapper, wrapper],
        trailing_set_operation=set_operation
    )
    print(chain)
    print(f"Size: {chain.size()}")
    print(f"Has trailing set operation: {chain.has_trailing_set_operation()}")
