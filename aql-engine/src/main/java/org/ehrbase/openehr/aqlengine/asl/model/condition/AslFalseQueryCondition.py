from typing import TypeVar
from dataclasses import dataclass

# Define placeholder classes for type hints
class AslQuery:
    pass

@dataclass(frozen=True)
class AslFalseQueryCondition:
    def with_provider(self, provider: AslQuery) -> 'AslFalseQueryCondition':
        return AslFalseQueryCondition()
