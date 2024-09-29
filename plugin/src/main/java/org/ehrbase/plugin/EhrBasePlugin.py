from abc import ABC, abstractmethod
from typing import List

# Mock classes to simulate behavior of pf4j and Spring components
class PluginWrapper:
    pass

class SpringPlugin(ABC):
    def __init__(self, wrapper: PluginWrapper):
        self.wrapper = wrapper

    @abstractmethod
    def get_wrapper(self):
        pass

class ConfigurableApplicationContext:
    def __init__(self):
        self.environment = Environment()

class Environment:
    def __init__(self):
        self.property_sources = PropertySources()

class PropertySources:
    def __init__(self):
        self.sources = []

    def add_last(self, p):
        self.sources.append(p)

class EhrBasePluginManagerInterface(ABC):
    @abstractmethod
    def load_config(self, wrapper: PluginWrapper) -> List:
        pass

# Python version of EhrBasePlugin
class EhrBasePlugin(SpringPlugin):
    def __init__(self, wrapper: PluginWrapper):
        super().__init__(wrapper)

    def load_properties(self, application_context: ConfigurableApplicationContext, plugin_manager: EhrBasePluginManagerInterface):
        """
        Load properties into the Spring-like environment from the plugin manager.
        """
        for p in plugin_manager.load_config(self.get_wrapper()):
            application_context.environment.property_sources.add_last(p)

    def get_wrapper(self):
        """
        Get the plugin wrapper. 
        """
        return self.wrapper
