from typing import List, Set, TypeVar
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class AslDvOrderedValueQueryCondition:
    types_to_compare: Set[str] = field(repr=True)
    field: 'AslDvOrderedColumnField'
    operator: 'AslConditionOperator'
    values: List[T] = field(default_factory=list)

    def __post_init__(self):
        if not self.types_to_compare:
            raise ValueError("Affected DV_ORDERED types not specified")

    def get_types_to_compare(self) -> Set[str]:
        return self.types_to_compare

# Placeholder classes for type hints
class AslDvOrderedColumnField:
    pass

class AslConditionOperator:
    pass

# Example usage
if __name__ == "__main__":
    # Example instantiation assuming actual implementations of AslDvOrderedColumnField and AslConditionOperator
    types_to_compare = {"type1", "type2"}
    field = AslDvOrderedColumnField()  # Placeholder for actual implementation
    operator = AslConditionOperator()  # Placeholder for actual implementation
    values = ["value1", "value2"]

    condition = AslDvOrderedValueQueryCondition(
        types_to_compare=types_to_compare,
        field=field,
        operator=operator,
        values=values
    )

    # Print attributes
    print(condition.get_types_to_compare())
