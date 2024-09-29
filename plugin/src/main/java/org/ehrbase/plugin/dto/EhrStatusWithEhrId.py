import uuid
from dataclasses import dataclass, field
from typing import Any
from com.nedap.archie.rm.ehr import EhrStatus  # Adjust the import as necessary

@dataclass(frozen=True)
class EhrStatusWithEhrId:
    """
    Wrapper for an Ehr with ehrId (UUID) and ehrStatus (EhrStatus).
    """
    ehr_status: EhrStatus = field(repr=True)
    ehr_id: uuid.UUID = field(repr=True)

    def __init__(self, ehr_status: EhrStatus, ehr_id: uuid.UUID) -> None:
        object.__setattr__(self, 'ehr_status', ehr_status)
        object.__setattr__(self, 'ehr_id', ehr_id)

    def get_ehr_status(self) -> EhrStatus:
        return self.ehr_status

    def get_ehr_id(self) -> uuid.UUID:
        return self.ehr_id

    def __str__(self) -> str:
        return f"EhrStatusWithEhrId{{ehrStatus={self.ehr_status}, ehrId={self.ehr_id}}}"

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, EhrStatusWithEhrId):
            return False
        return (self.ehr_status == other.ehr_status and
                self.ehr_id == other.ehr_id)

    def __hash__(self) -> int:
        return hash((self.ehr_status, self.ehr_id))
