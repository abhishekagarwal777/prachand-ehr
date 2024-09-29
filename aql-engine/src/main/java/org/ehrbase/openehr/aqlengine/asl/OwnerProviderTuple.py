from dataclasses import dataclass
from some_module import AslQuery  # Adjust this import according to your codebase

@dataclass(frozen=True)
class OwnerProviderTuple:
    owner: AslQuery
    provider: AslQuery

