from typing import Dict, Optional, Any
from dataclasses import dataclass, field

@dataclass(frozen=True)
class QueryWithParameters:
    """
    Wrapper for an Aql String `query` with optional `parameters`.
    """
    query: str = field(repr=True)
    parameters: Optional[Dict[str, Any]] = field(default=None, repr=True)

    def __init__(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        object.__setattr__(self, 'query', query)
        object.__setattr__(self, 'parameters', parameters)

    def get_query(self) -> str:
        return self.query

    def get_parameters(self) -> Optional[Dict[str, Any]]:
        return self.parameters

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, QueryWithParameters):
            return False
        return (self.query == other.query and
                self.parameters == other.parameters)

    def __hash__(self) -> int:
        return hash((self.query, frozenset(self.parameters.items()) if self.parameters else None))

    def __str__(self) -> str:
        return f"QueryWithParameters{{query='{self.query}', parameters={self.parameters}}}"
