from pathlib import Path
from typing import List, Optional, Dict, Type
import json
import yaml
import logging

# Define custom exceptions
class InternalServerException(Exception):
    pass

# Define the property source loaders
class PropertySourceLoader:
    def get_file_extensions(self) -> List[str]:
        raise NotImplementedError
    
    def load(self, file_name: str, path: Path) -> dict:
        raise NotImplementedError

class YamlPropertySourceLoader(PropertySourceLoader):
    def get_file_extensions(self) -> List[str]:
        return ['yml', 'yaml']
    
    def load(self, file_name: str, path: Path) -> dict:
        with open(path, 'r') as file:
            return yaml.safe_load(file)

class PropertiesPropertySourceLoader(PropertySourceLoader):
    def get_file_extensions(self) -> List[str]:
        return ['properties']
    
    def load(self, file_name: str, path: Path) -> dict:
        # Implement properties file loading here
        raise NotImplementedError

class JsonPropertySourceLoader(PropertySourceLoader):
    def get_file_extensions(self) -> List[str]:
        return ['json']
    
    def load(self, file_name: str, path: Path) -> dict:
        with open(path, 'r') as file:
            return json.load(file)

# Map file extensions to loaders
PROPERTY_SOURCE_LOADER_MAP: Dict[str, PropertySourceLoader] = {
    ext: loader
    for loader in [YamlPropertySourceLoader(), PropertiesPropertySourceLoader(), JsonPropertySourceLoader()]
    for ext in loader.get_file_extensions()
}

# Plugin manager properties placeholder
class PluginManagerProperties:
    def __init__(self, plugin_dir: Path, plugin_config_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugin_config_dir = plugin_config_dir

# Main plugin manager class
class EhrBasePluginManager:
    def __init__(self, properties: PluginManagerProperties):
        self.properties = properties
        self.init = False

    def init_plugins(self):
        if not self.init:
            self.start_plugins()
            # Simulate ExtensionsInjector and injection logic
            self.inject_extensions()
            self.init = True

    def start_plugins(self):
        # Implement plugin start logic here
        pass

    def inject_extensions(self):
        # Simulate extensions injection
        pass

    def get_config(self, file_name: str, plugin_id: str) -> dict:
        total_path = Path(self.properties.plugin_config_dir, plugin_id, file_name)
        ext = file_name.split('.')[-1]
        loader = PROPERTY_SOURCE_LOADER_MAP.get(ext)

        if not loader:
            raise InternalServerException(f"No Property Source Loader found for {file_name}")

        try:
            return loader.load(file_name, total_path)
        except Exception as e:
            raise InternalServerException(str(e))

    def load_config(self, plugin_id: str) -> List[dict]:
        total_path = Path(self.properties.plugin_config_dir, plugin_id)

        if total_path.exists():
            configs = []
            for file_path in total_path.rglob('*'):
                ext = file_path.suffix[1:]
                if ext in PROPERTY_SOURCE_LOADER_MAP:
                    configs.append(self.get_config(file_path.name, plugin_id))
            return configs

        return []

# Example usage
plugin_manager_properties = PluginManagerProperties(Path('/path/to/plugins'), Path('/path/to/plugin/configs'))
plugin_manager = EhrBasePluginManager(plugin_manager_properties)
plugin_manager.init_plugins()
