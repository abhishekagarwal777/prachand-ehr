from abc import ABC, abstractmethod
from spring.context import ApplicationContext  # Adjust import based on your project structure

class ExternalBeanRegistration(ABC):
    """
    Interface for external bean registration.
    """

    @abstractmethod
    def external_registration(self, plugin_ctx: ApplicationContext) -> None:
        """
        External registration method for the application context.

        Args:
            plugin_ctx: Application context for plugin registration.
        """
        pass
