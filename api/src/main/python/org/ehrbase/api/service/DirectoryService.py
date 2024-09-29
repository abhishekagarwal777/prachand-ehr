from abc import ABC, abstractmethod
from typing import Optional
import uuid
from datetime import datetime

class Folder:
    # Placeholder for the Folder class definition.
    pass

class ObjectVersionId:
    # Placeholder for the ObjectVersionId class definition.
    pass

class DirectoryService(ABC):

    EHR_DIRECTORY_FOLDER_IDX = 1

    @abstractmethod
    def get(self, ehr_id: uuid.UUID, folder_id: Optional[ObjectVersionId], path: Optional[str]) -> Optional[Folder]:
        """
        Get the Folder for EHR with id equal `ehr_id`.
        If `folder_id` is None, the latest version will be returned.
        Optionally return folder at `path`.
        """
        pass

    @abstractmethod
    def get_by_time(self, ehr_id: uuid.UUID, time: datetime, path: Optional[str]) -> Optional[Folder]:
        """
        Get the Folder for EHR with id equal `ehr_id` for a specific point in time.
        Optionally return folder at `path`.
        """
        pass

    @abstractmethod
    def create(self, ehr_id: uuid.UUID, folder: Folder) -> Folder:
        """
        Create a new folder for EHR with id equal `ehr_id`.
        """
        pass

    @abstractmethod
    def update(self, ehr_id: uuid.UUID, folder: Folder, if_matches: ObjectVersionId) -> Folder:
        """
        Update the folder for EHR with id equal `ehr_id`.
        Use `if_matches` for optimistic locking.
        """
        pass

    @abstractmethod
    def delete(self, ehr_id: uuid.UUID, if_matches: ObjectVersionId) -> None:
        """
        Delete the folder for EHR with id equal `ehr_id`.
        Use `if_matches` for optimistic locking.
        """
        pass

    @abstractmethod
    def admin_delete_folder(self, ehr_id: uuid.UUID, folder_id: uuid.UUID) -> None:
        """
        Physically delete a folder with all its history.
        """
        pass
