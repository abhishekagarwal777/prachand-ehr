from abc import ABC, abstractmethod
from typing import List, Optional
from your_module_definitions import OperationalTemplateFormat  # Import your format enum or class
from your_module_dtos import TemplateMetaDataDto  # Import your DTO class

class TemplateService(ABC):

    @abstractmethod
    def get_all_templates(self) -> List[TemplateMetaDataDto]:
        """
        Retrieves all templates.
        """
        pass

    @abstractmethod
    def build_example(self, template_id: str) -> Composition:
        """
        Builds an example composition from the given template ID.
        """
        pass

    @abstractmethod
    def find_template(self, template_id: str) -> WebTemplate:
        """
        Finds and returns the template corresponding to the given template ID.
        """
        pass

    @abstractmethod
    def find_operational_template(self, template_id: str, format: OperationalTemplateFormat) -> str:
        """
        Finds and returns the operational template as a string in the requested format.

        :param template_id: Unique name of the operational template
        :param format: The format to return
        :return: Template as a string in the requested format
        :raises RuntimeError: If the template couldn't be found, format isn't supported, or another error occurs
        """
        pass

    @abstractmethod
    def create(self, content: OPERATIONALTEMPLATE) -> str:
        """
        Creates a new template with the provided operational template content.

        :param content: Operational template content
        :return: The ID of the newly created template
        """
        pass

    @abstractmethod
    def admin_delete_template(self, template_id: str) -> bool:
        """
        Deletes a given template from storage.

        :param template_id: ID of the template to delete
        :return: Whether the template could be removed or not
        """
        pass

    @abstractmethod
    def admin_update_template(self, template_id: str, content: str) -> str:
        """
        Replaces a given template in the storage with new content.

        :param template_id: ID of the template to update
        :param content: New content to overwrite the template
        :return: New template ID
        """
        pass

    @abstractmethod
    def admin_delete_all_templates(self) -> int:
        """
        Deletes all templates from storage.

        :return: Number of deleted templates
        """
        pass
