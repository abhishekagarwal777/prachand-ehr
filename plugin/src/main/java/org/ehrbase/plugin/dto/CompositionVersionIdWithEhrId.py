import uuid
from typing import Any
from dataclasses import dataclass, field

# Assuming ObjectVersionId is a class you need to implement or import.
# If it comes from an external library, make sure to replace the following line accordingly.
class ObjectVersionId:
    # Placeholder for the actual implementation of ObjectVersionId
    pass

@dataclass(frozen=True)
class CompositionVersionIdWithEhrId:
    """
    Wrapper for composition version ObjectVersionId and ehrId (UUID).
    """
    ehr_id: uuid.UUID
    version_id: ObjectVersionId = field(repr=True)

    def get_ehr_id(self) -> uuid.UUID:
        return self.ehr_id

    def get_version_id(self) -> ObjectVersionId:
        return self.version_id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CompositionVersionIdWithEhrId):
            return False
        return self.ehr_id == other.ehr_id and self.version_id == other.version_id

    def __hash__(self) -> int:
        return hash((self.ehr_id, self.version_id))

    def __str__(self) -> str:
        return f"CompositionVersionIdWithEhrId{{ehrId={self.ehr_id}, versionId={self.version_id}}}"
