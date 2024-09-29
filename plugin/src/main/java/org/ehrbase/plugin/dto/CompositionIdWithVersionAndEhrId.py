import uuid
from typing import Optional

class CompositionIdWithVersionAndEhrId:
    """
    Wrapper to identify a composition by compositionId (UUID), in version
    version (int), None means latest, containing ehr with ehrId (UUID).
    """

    def __init__(self, ehr_id: uuid.UUID, composition_id: uuid.UUID, version: Optional[int] = None):
        self.ehr_id = ehr_id
        self.composition_id = composition_id
        self.version = version

    def get_ehr_id(self) -> uuid.UUID:
        return self.ehr_id

    def get_composition_id(self) -> uuid.UUID:
        return self.composition_id

    def get_version(self) -> Optional[int]:
        return self.version

    def is_latest_version(self) -> bool:
        return self.version is None

    def __eq__(self, other):
        if not isinstance(other, CompositionIdWithVersionAndEhrId):
            return False
        return (self.ehr_id == other.ehr_id and
                self.composition_id == other.composition_id and
                self.version == other.version)

    def __hash__(self):
        return hash((self.ehr_id, self.composition_id, self.version))
