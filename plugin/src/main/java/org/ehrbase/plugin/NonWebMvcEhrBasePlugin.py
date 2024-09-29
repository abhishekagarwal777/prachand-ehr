from abc import ABC, abstractmethod

# Mock classes to simulate pf4j and Spring components
class PluginWrapper:
    def get_plugin_manager(self):
        pass

class ApplicationContext:
    pass

class ConfigurableApplicationContext(ApplicationContext):
    def is_active(self) -> bool:
        pass

    def refresh(self):
        pass

class EhrBasePluginManagerInterface:
    def load_config(self, plugin_wrapper: PluginWrapper):
        pass

# Base class EhrBasePlugin in Python
class EhrBasePlugin(ABC):
    def __init__(self, wrapper: PluginWrapper):
        self._wrapper = wrapper

    def get_wrapper(self) -> PluginWrapper:
        return self._wrapper

    def load_properties(self, application_context: ConfigurableApplicationContext, plugin_manager: EhrBasePluginManagerInterface):
        properties = plugin_manager.load_config(self.get_wrapper())
        for prop in properties:
            application_context.get_environment().get_property_sources().add_last(prop)

    @abstractmethod
    def create_application_context(self) -> ApplicationContext:
        pass

# Python version of NonWebMvcEhrBasePlugin
class NonWebMvcEhrBasePlugin(EhrBasePlugin):

    def __init__(self, wrapper: PluginWrapper):
        super().__init__(wrapper)

    @abstractmethod
    def build_application_context(self) -> ApplicationContext:
        """
        Build the ApplicationContext of the plugin. Will only be called once by EHRbase.
        The ApplicationContext will be refreshed by EHRbase.
        """
        pass

    def create_application_context(self) -> ApplicationContext:
        """
        Creates and configures the plugin's ApplicationContext.
        """
        application_context = self.build_application_context()

        # Ensure applicationContext is an instance of ConfigurableApplicationContext and is not active
        if isinstance(application_context, ConfigurableApplicationContext) and not application_context.is_active():

            # Retrieve the plugin manager from the plugin wrapper
            plugin_manager = self.get_wrapper().get_plugin_manager()

            # Cast plugin manager to EhrBasePluginManagerInterface
            plugin_manager = EhrBasePluginManagerInterface()

            # Load properties and refresh the context
            self.load_properties(application_context, plugin_manager)
            application_context.refresh()

        return application_context
