import uuid
from dataclasses import dataclass, field
from typing import Any
from com.nedap.archie.rm.composition import Composition  # Adjust the import as necessary
from com.nedap.archie.rm.support.identification import ObjectVersionId  # Adjust the import as necessary

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


@dataclass(frozen=True)
class CompositionWithEhrIdAndPreviousVersion(CompositionWithEhrId):
    """
    Wrapper for Composition with ehrId (UUID) and previous version (ObjectVersionId).
    """
    previous_version: ObjectVersionId = field(repr=True)

    def get_previous_version(self) -> ObjectVersionId:
        return self.previous_version

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, CompositionWithEhrIdAndPreviousVersion):
            return False
        if not super().__eq__(other):
            return False
        return self.previous_version == other.previous_version

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.previous_version))

    def __str__(self) -> str:
        return f"CompositionWithEhrIdAndPreviousVersion{{previousVersion={self.previous_version}}} " + super().__str__()
