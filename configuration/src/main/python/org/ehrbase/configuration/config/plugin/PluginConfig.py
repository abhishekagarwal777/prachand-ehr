import logging
from pathlib import Path
from typing import Dict, List
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_injector import FlaskInjector
from injector import inject, Binder
import yaml

# Custom exceptions
class InternalServerException(Exception):
    pass

# Define plugin manager properties
class PluginManagerProperties:
    def __init__(self, plugin_dir: Path, plugin_config_dir: Path, plugin_context_path: str):
        self.plugin_dir = plugin_dir
        self.plugin_config_dir = plugin_config_dir
        self.plugin_context_path = plugin_context_path

# Define the plugin manager
class EhrBasePluginManager:
    def __init__(self, properties: PluginManagerProperties):
        self.properties = properties
        self.plugins = []
    
    def load_plugins(self):
        # Implement plugin loading logic here
        pass
    
    def get_plugins(self):
        return self.plugins
    
    def init_plugins(self):
        # Implement plugin initialization logic here
        pass

# Define a plugin interface
class WebMvcEhrBasePlugin:
    def get_context_path(self) -> str:
        raise NotImplementedError

    def get_dispatcher_servlet(self):
        raise NotImplementedError

    def get_wrapper(self):
        raise NotImplementedError

# Define the PluginConfig class
class PluginConfig:
    def __init__(self, app: Flask, plugin_manager: EhrBasePluginManager, properties: PluginManagerProperties):
        self.app = app
        self.plugin_manager = plugin_manager
        self.properties = properties

        self.register_plugins()
        self.initialize_plugins_listener()

    def register_plugins(self):
        self.plugin_manager.load_plugins()

        registered_url: Dict[str, str] = {}

        for plugin in self.plugin_manager.get_plugins():
            if isinstance(plugin, WebMvcEhrBasePlugin):
                self.register(self.app, self.properties, registered_url, plugin)

    def register(self, app: Flask, properties: PluginManagerProperties, registered_url: Dict[str, str], plugin: WebMvcEhrBasePlugin):
        plugin_id = plugin.get_wrapper().get_plugin_id()
        uri = f"{properties.plugin_context_path}{plugin.get_context_path()}/*"

        # Check for duplicate plugin URI
        if uri in registered_url.values():
            existing_plugin = [k for k, v in registered_url.items() if v == uri]
            if existing_plugin:
                raise InternalServerException(f"URI {uri} for plugin {plugin_id} already registered by plugin {existing_plugin[0]}")

        registered_url[plugin_id] = uri
        app.add_url_rule(uri, plugin_id, plugin.get_dispatcher_servlet())

    def initialize_plugins_listener(self):
        @self.app.before_first_request
        def on_startup():
            self.plugin_manager.init_plugins()

# Example Flask app and configuration
app = Flask(__name__)
app.config['PLUGIN_DIR'] = Path('/path/to/plugins')
app.config['PLUGIN_CONFIG_DIR'] = Path('/path/to/plugin/configs')
app.config['PLUGIN_CONTEXT_PATH'] = '/plugins'

properties = PluginManagerProperties(
    plugin_dir=app.config['PLUGIN_DIR'],
    plugin_config_dir=app.config['PLUGIN_CONFIG_DIR'],
    plugin_context_path=app.config['PLUGIN_CONTEXT_PATH']
)

plugin_manager = EhrBasePluginManager(properties)
plugin_config = PluginConfig(app, plugin_manager, properties)

if __name__ == '__main__':
    app.run()
