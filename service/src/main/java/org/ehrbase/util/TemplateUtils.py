from typing import List, Optional
from openehr.schemas.v1 import OPERATIONALTEMPLATE, OBJECTID  # Assuming appropriate Python bindings for OpenEHR SDK
from ehrbase.openehr.sdk.webtemplate.model import WebTemplate
from ehrbase.openehr.sdk.webtemplate.parser import OPTParser


class TemplateUtils:
    UNSUPPORTED_RM_TYPES: List[str] = ["ITEM_TABLE"]

    @staticmethod
    def is_supported(template: OPERATIONALTEMPLATE) -> bool:
        """
        Check whether the given OPT template is supported.

        :param template: The candidate template.
        :return: True if the template is supported.
        """
        web_template = OPTParser(template).parse()
        return TemplateUtils.is_supported_web_template(web_template)

    @staticmethod
    def is_supported_web_template(template: WebTemplate) -> bool:
        """
        Check whether the given WebTemplate is supported.

        :param template: The candidate template.
        :return: True if the template is supported.
        """
        return not any(node.rm_type in TemplateUtils.UNSUPPORTED_RM_TYPES for node in template.tree.find_matching())

    @staticmethod
    def get_template_id(template: OPERATIONALTEMPLATE) -> str:
        """
        Retrieves the template ID from the given OPT template.

        :param template: The template.
        :return: Template ID.
        :raises ValueError: If the template is None or ID is None.
        """
        if template is None:
            raise ValueError("Template must not be None")
        
        template_id = template.template_id
        if template_id is None:
            raise ValueError("Template ID must not be None for the given template")
        
        return template_id.value
