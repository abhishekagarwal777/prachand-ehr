from abc import ABC, abstractmethod
from typing import List

# Mock classes to simulate pf4j and Spring components
class PluginWrapper:
    pass

class ApplicationContext:
    pass

class PropertySource:
    pass

# Python version of EhrBasePluginManagerInterface
class EhrBasePluginManagerInterface(ABC):
    @abstractmethod
    def get_application_context(self) -> ApplicationContext:
        """
        Return the application context associated with the plugin.
        """
        pass

    @abstractmethod
    def load_config(self, plugin_wrapper: PluginWrapper) -> List[PropertySource]:
        """
        Load configuration properties for the given plugin.
        :param plugin_wrapper: PluginWrapper representing the plugin instance
        :return: List of PropertySource objects loaded for the plugin
        """
        pass
