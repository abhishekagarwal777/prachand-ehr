from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Placeholder classes for OPERATIONALTEMPLATE and TemplateMetaData
class OPERATIONALTEMPLATE:
    def __init__(self, template_id=None):
        self.template_id = template_id

class TemplateMetaData:
    def __init__(self):
        self.created_on = None
        self.operationaltemplate = None


class TemplateStorage(ABC):
    """
    Interface for TemplateStorage, which provides methods for storing, reading, and managing templates in the store.
    """

    @abstractmethod
    def list_all_operational_templates(self) -> List[TemplateMetaData]:
        """
        List all Templates in the store.

        :return: List of TemplateMetaData
        """
        pass

    @abstractmethod
    def store_template(self, template: OPERATIONALTEMPLATE) -> None:
        """
        Save a template in the store.

        :param template: An OPERATIONALTEMPLATE object to be stored.
        :raises RuntimeError: If the template ID or UUID is not unique.
        """
        pass

    @abstractmethod
    def read_operationaltemplate(self, template_id: str) -> Optional[OPERATIONALTEMPLATE]:
        """
        Find and return a saved Template by templateId.

        :param template_id: The ID of the template to read.
        :return: The OPERATIONALTEMPLATE object or None if not found.
        """
        pass

    @abstractmethod
    def delete_template(self, template_id: str) -> bool:
        """
        Deletes an operational template from the storage. The template will be removed physically,
        so ensure that no compositions reference the template.

        :param template_id: The ID of the template to delete from storage (e.g., "IDCR Allergies List.v0").
        :return: True if deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    def find_template_id_by_uuid(self, uuid: UUID) -> Optional[str]:
        """
        Find the template ID by its UUID.

        :param uuid: The UUID of the template.
        :return: The template ID as a string or None if not found.
        """
        pass

    @abstractmethod
    def find_uuid_by_template_id(self, template_id: str) -> Optional[UUID]:
        """
        Find the UUID of a template by its template ID.

        :param template_id: The ID of the template.
        :return: The UUID of the template or None if not found.
        """
        pass
