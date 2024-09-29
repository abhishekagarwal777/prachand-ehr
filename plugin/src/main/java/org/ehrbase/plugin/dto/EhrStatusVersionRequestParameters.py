import uuid
from dataclasses import dataclass, field
from typing import Any
from com.nedap.archie.rm.ehr import EhrStatus  # Adjust the import as necessary

@dataclass(frozen=True)
class EhrStatusVersionRequestParameters:
    """
    Wrapper for an Ehr with ehrId (UUID) and ehrStatus (EhrStatus).
    """
    ehr_id: uuid.UUID = field(repr=True)
    ehr_status_id: uuid.UUID = field(repr=True)
    ehr_status_version: int = field(repr=True)

    def __init__(self, ehr_id: uuid.UUID, ehr_status_id: uuid.UUID, ehr_status_version: int) -> None:
        object.__setattr__(self, 'ehr_id', ehr_id)
        object.__setattr__(self, 'ehr_status_id', ehr_status_id)
        object.__setattr__(self, 'ehr_status_version', ehr_status_version)

    def get_ehr_id(self) -> uuid.UUID:
        return self.ehr_id

    def get_ehr_status_id(self) -> uuid.UUID:
        return self.ehr_status_id

    def get_ehr_status_version(self) -> int:
        return self.ehr_status_version

    def __str__(self) -> str:
        return (f"EhrStatusVersionRequestParameters{{ehrStatusId={self.ehr_status_id}, "
                f"version={self.ehr_status_version}, ehrId={self.ehr_id}}}")

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, EhrStatusVersionRequestParameters):
            return False
        return (self.ehr_status_id == other.ehr_status_id and
                self.ehr_status_version == other.ehr_status_version and
                self.ehr_id == other.ehr_id)

    def __hash__(self) -> int:
        return hash((self.ehr_status_id, self.ehr_status_version, self.ehr_id))
