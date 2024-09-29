from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
import io

class OPERATIONALTEMPLATE:
    # Placeholder for the OPERATIONALTEMPLATE class
    pass

class TemplateMetaData:
    # Placeholder for the TemplateMetaData class
    pass

class KnowledgeCacheService(ABC):

    @abstractmethod
    def add_operational_template(self, content: io.InputStream) -> str:
        """
        Adds an operational template to the system and current cache.
        :param content: Operational template input
        :return: Resulting template ID
        :raises InvalidApiParameterException: When input can't be parsed to OPT instance
        :raises StateConflictException: When template with the same template ID is already in the system
        :raises InternalServerException: When an unspecified problem occurs
        """
        pass

    @abstractmethod
    def add_operational_template(self, template: OPERATIONALTEMPLATE) -> str:
        """
        Adds an operational template directly.
        :param template: OPERATIONALTEMPLATE instance
        :return: Resulting template ID
        """
        pass

    @abstractmethod
    def list_all_operational_templates(self) -> List[TemplateMetaData]:
        """
        Lists all operational templates.
        :return: List of TemplateMetaData
        """
        pass

    @abstractmethod
    def retrieve_operational_template(self, key: str) -> Optional[OPERATIONALTEMPLATE]:
        """
        Retrieves an operational template by its name.
        :param key: Name of the operational template
        :return: An OPERATIONALTEMPLATE instance or None
        """
        pass

    @abstractmethod
    def retrieve_operational_template(self, uuid: UUID) -> Optional[OPERATIONALTEMPLATE]:
        """
        Retrieves a cached operational template by its unique ID.
        :param uuid: UUID of the operational template
        :return: An OPERATIONALTEMPLATE instance or None
        """
        pass

    @abstractmethod
    def delete_operational_template(self, template: OPERATIONALTEMPLATE) -> bool:
        """
        Deletes an operational template from cache and storage.
        :param template: The template instance to delete
        :return: True if the template has been deleted
        """
        pass

    @abstractmethod
    def find_template_id_by_uuid(self, uuid: UUID) -> Optional[str]:
        """
        Finds a template ID by its UUID.
        :param uuid: UUID of the template
        :return: Template ID or None
        """
        pass

    @abstractmethod
    def find_uuid_by_template_id(self, template_id: str) -> Optional[UUID]:
        """
        Finds a UUID by its template ID.
        :param template_id: Template ID
        :return: UUID or None
        """
        pass
