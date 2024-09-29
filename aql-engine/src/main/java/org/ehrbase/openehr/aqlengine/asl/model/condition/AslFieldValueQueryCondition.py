from typing import List, TypeVar
from dataclasses import dataclass

# Define placeholder classes for type hints
class AslField:
    def with_provider(self, provider: 'AslQuery') -> 'AslField':
        pass  # Implement according to actual logic

class AslConditionOperator:
    pass

class AslQuery:
    pass

T = TypeVar('T')

@dataclass(frozen=True)
class AslFieldValueQueryCondition:
    field: AslField
    operator: AslConditionOperator
    values: List[T]

    def with_provider(self, provider: AslQuery) -> 'AslFieldValueQueryCondition':
        return AslFieldValueQueryCondition(
            field=self.field.with_provider(provider),
            operator=self.operator,
            values=list(self.values)
        )
