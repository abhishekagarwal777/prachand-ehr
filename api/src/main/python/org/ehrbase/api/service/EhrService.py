from abc import ABC, abstractmethod
from typing import Optional
import uuid
from datetime import datetime

class EhrStatusDto:
    # Placeholder for the EhrStatusDto class definition.
    pass

class ObjectVersionId:
    # Placeholder for the ObjectVersionId class definition.
    pass

class DvDateTime:
    # Placeholder for the DvDateTime class definition.
    pass

class EhrResult:
    def __init__(self, ehr_id: uuid.UUID, status_version_id: ObjectVersionId, status: EhrStatusDto):
        self.ehr_id = ehr_id
        self.status_version_id = status_version_id
        self.status = status

class EhrService(ABC):

    @abstractmethod
    def create(self, ehr_id: Optional[uuid.UUID], status: Optional[EhrStatusDto]) -> EhrResult:
        """
        Creates a new EHR instance, with default settings and values when no status or ID is supplied.
        """
        pass

    @abstractmethod
    def update_status(self, ehr_id: uuid.UUID, status: EhrStatusDto, target_obj_id: ObjectVersionId, contribution: Optional[uuid.UUID], audit: uuid.UUID) -> EhrResult:
        """
        Updates the EHR_STATUS linked to the given EHR.
        """
        pass

    @abstractmethod
    def get_ehr_status(self, ehr_uuid: uuid.UUID) -> EhrResult:
        """
        Gets latest EHR_STATUS of the given EHR.
        """
        pass

    @abstractmethod
    def get_ehr_status_at_version(self, ehr_uuid: uuid.UUID, versioned_object_uid: uuid.UUID, version: int) -> Optional[OriginalVersion[EhrStatusDto]]:
        """
        Gets particular EHR_STATUS matching the given version UID.
        """
        pass

    @abstractmethod
    def find_by_subject(self, subject_id: str, name_space: str) -> Optional[uuid.UUID]:
        """
        Searches for an EHR_STATUS based on the given subject ID and namespace.
        """
        pass

    @abstractmethod
    def get_latest_version_uid_of_status(self, ehr_id: uuid.UUID) -> ObjectVersionId:
        """
        Gets latest version UID of an EHR_STATUS by given associated EHR UID.
        """
        pass

    @abstractmethod
    def get_ehr_status_version_by_timestamp(self, ehr_uid: uuid.UUID, timestamp: datetime) -> ObjectVersionId:
        """
        Gets version number of EHR_STATUS associated with given EHR UID at given timestamp.
        """
        pass

    @abstractmethod
    def get_creation_time(self, ehr_id: uuid.UUID) -> DvDateTime:
        """
        Provides the creation time of the given EHR ID.
        """
        pass

    @abstractmethod
    def has_ehr(self, ehr_id: uuid.UUID) -> bool:
        """
        Returns True if an EHR with identifier `ehr_id` exists.
        """
        pass

    @abstractmethod
    def get_versioned_ehr_status(self, ehr_id: uuid.UUID) -> VersionedObject[EhrStatusDto]:
        """
        Gets version container EhrStatus associated with given EHR.
        """
        pass

    @abstractmethod
    def get_revision_history_of_versioned_ehr_status(self, ehr_id: uuid.UUID) -> RevisionHistory:
        """
        Gets revision history of EhrStatus associated with given EHR.
        """
        pass

    @abstractmethod
    def admin_delete_ehr(self, ehr_id: uuid.UUID) -> None:
        """
        Admin method to delete an EHR from the DB.
        """
        pass

    @abstractmethod
    def get_subject_ext_ref(self, ehr_id: uuid.UUID) -> Optional[str]:
        """
        Helper to directly get the external subject reference form the linked subject to given EHR.
        """
        pass

    @abstractmethod
    def check_ehr_exists(self, ehr_id: uuid.UUID) -> None:
        """
        Checks if an EHR with the given UUID exists.
        """
        pass

    @abstractmethod
    def check_ehr_exists_and_is_modifiable(self, ehr_id: uuid.UUID) -> None:
        """
        Checks if the EHR with the given UUID is modifiable.
        """
        pass
