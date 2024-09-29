from dataclasses import dataclass
from typing import Protocol

# Define placeholder classes for type hints
class AslQuery:
    pass

class AslQueryCondition(Protocol):
    def with_provider(self, provider: AslQuery) -> 'AslQueryCondition':
        pass  # Method to be implemented in subclasses

@dataclass(frozen=True)
class AslNotQueryCondition:
    condition: AslQueryCondition

    def with_provider(self, provider: AslQuery) -> 'AslNotQueryCondition':
        return AslNotQueryCondition(condition=self.condition.with_provider(provider))
