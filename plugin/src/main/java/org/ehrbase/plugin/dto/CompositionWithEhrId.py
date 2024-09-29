import uuid
from dataclasses import dataclass, field
from typing import Any

# Assuming Composition is a class you need to implement or import.
# If it comes from an external library, make sure to replace the following line accordingly.
class Composition:
    # Placeholder for the actual implementation of Composition
    pass

@dataclass(frozen=True)
class CompositionWithEhrId:
    """
    Wrapper for Composition with ehrId (UUID).
    """
    composition: Composition = field(repr=True)
    ehr_id: uuid.UUID = field(repr=True)

    def get_composition(self) -> Composition:
        return self.composition

    def get_ehr_id(self) -> uuid.UUID:
        return self.ehr_id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CompositionWithEhrId):
            return False
        return self.composition == other.composition and self.ehr_id == other.ehr_id

    def __hash__(self) -> int:
        return hash((self.composition, self.ehr_id))

    def __str__(self) -> str:
        return f"CompositionWithEhrId{{composition={self.composition}, ehrId={self.ehr_id}}}"
