from dataclasses import dataclass
from typing import Optional

# Define placeholder classes for type hints
class AslField:
    def with_provider(self, provider: 'AslQuery') -> 'AslField':
        pass  # Implement according to actual logic

class AslQuery:
    pass

@dataclass(frozen=True)
class AslNotNullQueryCondition:
    field: AslField

    def with_provider(self, provider: AslQuery) -> 'AslNotNullQueryCondition':
        return AslNotNullQueryCondition(field=self.field.with_provider(provider))
