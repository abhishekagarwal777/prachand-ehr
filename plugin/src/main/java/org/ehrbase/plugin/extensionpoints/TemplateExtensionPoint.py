from typing import Callable
from openehr.schemas.v1 import OPERATIONALTEMPLATE  # Adjust import based on your project structure
from pf4j import ExtensionPoint  # Adjust import based on your project structure

class TemplateExtensionPoint(ExtensionPoint):
    """
    Extension Point for Template handling.
    """

    def around_creation(self, input: OPERATIONALTEMPLATE, 
                        chain: Callable[[OPERATIONALTEMPLATE], str]) -> str:
        """
        Intercept Template create.

        Args:
            input: OPERATIONALTEMPLATE to be created.
            chain: Next Extension Point function.

        Returns:
            str: templateId of the created template.
        """
        return chain(input)
