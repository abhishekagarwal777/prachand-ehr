from abc import ABC, abstractmethod

# Placeholder for the WebTemplate class
class WebTemplate:
    def __init__(self, template_id: str, metadata: dict):
        self.template_id = template_id
        self.metadata = metadata

class IntrospectService(ABC):
    
    @abstractmethod
    def get_query_opt_metadata(self, template_id: str) -> WebTemplate:
        """Fetches metadata for a given template ID.

        Args:
            template_id (str): The ID of the template to introspect.

        Returns:
            WebTemplate: The metadata for the given template.
        """
        pass
