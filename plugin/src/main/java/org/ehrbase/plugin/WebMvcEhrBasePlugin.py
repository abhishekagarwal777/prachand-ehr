from abc import ABC, abstractmethod
from typing import Optional, Dict

# Mock classes to simulate pf4j and Spring components
class PluginWrapper:
    def get_plugin_manager(self):
        pass

class ApplicationContext:
    def get_parent(self):
        pass

class ConfigurableApplicationContext(ApplicationContext):
    def refresh(self):
        pass

class WebApplicationContext(ApplicationContext):
    pass

class DispatcherServlet:
    def get_web_application_context(self) -> WebApplicationContext:
        pass

class Environment:
    def contains_property(self, key: str) -> bool:
        pass

    def get_property(self, key: str, property_type):
        pass

class PluginDescriptor:
    def get_plugin_id(self) -> str:
        pass

class EhrBasePluginManagerInterface:
    def get_application_context(self) -> ApplicationContext:
        pass

    def load_config(self, plugin_wrapper: PluginWrapper):
        pass

class AuthorizationInfo:
    class AuthorizationEnabled:
        pass

    class AuthorizationDisabled:
        pass

class AbstractApplicationContext(ConfigurableApplicationContext):
    def set_class_loader(self, class_loader):
        pass

    def set_parent(self, parent_context: ApplicationContext):
        pass

class AnnotationConfigRegistry:
    def register(self, cls):
        pass

class ExternalBeanRegistration:
    def external_registration(self, ctx: WebApplicationContext):
        pass

class InternalServerException(Exception):
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

# Python version of WebMvcEhrBasePlugin
class WebMvcEhrBasePlugin(EhrBasePlugin):

    DISABLE_PLUGIN_AUTHORIZATION = "authorization.service.disable.for.%s"
    WARN_PLUGIN_SEC = (
        "Cannot Configure Plugin Security, check that setting Classloader and Registering of Components is Possible"
    )

    def __init__(self, wrapper: PluginWrapper):
        super().__init__(wrapper)
        self.dispatcher_servlet: Optional[DispatcherServlet] = None

    def create_application_context(self) -> ApplicationContext:
        """
        Creates and configures the ApplicationContext from the DispatcherServlet.
        """
        return self.get_dispatcher_servlet().get_web_application_context()

    def get_dispatcher_servlet(self) -> DispatcherServlet:
        """
        Lazily initializes the DispatcherServlet and sets up the plugin context.
        """
        if self.dispatcher_servlet is None:
            self.dispatcher_servlet = self.build_dispatcher_servlet()

            # Retrieve the application context from the dispatcher servlet
            application_context = self.dispatcher_servlet.get_web_application_context()

            # Perform external bean registration and plugin security initialization
            self.external_bean_registration(application_context)
            self.init_plugin_security(application_context)

            # Load plugin properties if applicable
            plugin_manager = self.get_wrapper().get_plugin_manager()
            if isinstance(application_context, ConfigurableApplicationContext):
                self.load_properties(application_context, plugin_manager)

        return self.dispatcher_servlet

    def external_bean_registration(self, ctx: WebApplicationContext):
        """
        Registers external beans in the plugin context.
        """
        plugin_manager = self.get_wrapper().get_plugin_manager()

        parent_context = ctx.get_parent()
        if parent_context is None:
            raise InternalServerException("Plugin context not correctly set")

        # Retrieve and register external beans
        all_external_registrations: Dict[str, ExternalBeanRegistration] = parent_context.get_beans_of_type(ExternalBeanRegistration)
        for ex_reg in all_external_registrations.values():
            if isinstance(ctx, AbstractApplicationContext):
                ctx.set_class_loader(self._wrapper.get_plugin_class_loader())
                ctx.set_parent(plugin_manager.get_application_context())
            else:
                print(self.WARN_PLUGIN_SEC)

            ex_reg.external_registration(ctx)

    def init_plugin_security(self, ctx: WebApplicationContext):
        """
        Initializes plugin security by configuring the application context with necessary security settings.
        """
        plugin_manager = self.get_wrapper().get_plugin_manager()

        if isinstance(ctx, AbstractApplicationContext) and isinstance(ctx, AnnotationConfigRegistry):
            ctx.set_class_loader(self._wrapper.get_plugin_class_loader())
            ctx.register(PluginSecurityConfiguration)
            ctx.register(self.create_authorization_info_of(plugin_manager).__class__)
            ctx.set_parent(plugin_manager.get_application_context())
        else:
            print(self.WARN_PLUGIN_SEC)

    def create_authorization_info_of(self, plugin_manager: EhrBasePluginManagerInterface) -> AuthorizationInfo:
        """
        Creates the appropriate AuthorizationInfo based on plugin-specific configuration.
        """
        descriptor = self.get_wrapper().get_descriptor()
        plugin_id = descriptor.get_plugin_id()

        env = plugin_manager.get_application_context().get_environment()
        auth_prop = self.DISABLE_PLUGIN_AUTHORIZATION % plugin_id

        if not env.contains_property(auth_prop):
            return AuthorizationInfo.AuthorizationEnabled()
        elif env.get_property(auth_prop, bool):
            return AuthorizationInfo.AuthorizationDisabled()
        else:
            return AuthorizationInfo.AuthorizationEnabled()

    @abstractmethod
    def build_dispatcher_servlet(self) -> DispatcherServlet:
        """
        Abstract method for building the DispatcherServlet. To be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_context_path(self) -> str:
        """
        Abstract method to return the context path for the deployed DispatcherServlet.
        """
        pass
