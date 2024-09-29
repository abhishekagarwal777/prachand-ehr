from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from uuid import UUID

# Define type variables
T = TypeVar('T')  # Represents Locatable or its subtype
U = TypeVar('U')  # Represents the return type of create and update methods

class VersionedObjectService(ABC, Generic[T, U]):

    @abstractmethod
    def create(self, ehr_id: UUID, obj_data: T, contribution: Optional[UUID] = None, audit: Optional[UUID] = None) -> Optional[U]:
        """
        Creation with given audit meta-data or default. Will create a new ad-hoc contribution if necessary.

        :param ehr_id: EHR ID of context
        :param obj_data: Payload object data
        :param contribution: Optional contribution for the operation
        :param audit: Optional audit ID
        :return: Response wrapped in Optional
        """
        pass

    @abstractmethod
    def update(self, ehr_id: UUID, target_obj_id: UUID, obj_data: T, contribution: Optional[UUID] = None, audit: Optional[UUID] = None) -> Optional[U]:
        """
        Update with given audit meta-data or default. Will create a new ad-hoc contribution if necessary.

        :param ehr_id: EHR ID of context
        :param target_obj_id: ID of target object
        :param obj_data: Payload object data
        :param contribution: Optional contribution for the operation
        :param audit: Optional audit ID
        :return: Response wrapped in Optional
        """
        pass

    @abstractmethod
    def delete(self, ehr_id: UUID, target_obj_id: UUID, contribution: Optional[UUID] = None, audit: Optional[UUID] = None) -> None:
        """
        Deletion with given audit meta-data or default. Will create a new ad-hoc contribution if necessary.

        :param ehr_id: EHR ID of context
        :param target_obj_id: ID of target object
        :param contribution: Optional contribution for the operation
        :param audit: Optional audit ID
        """
        pass
