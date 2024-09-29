from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class PluginManagerProperties:
    plugin_dir: Path
    enable: bool
    plugin_context_path: str
    plugin_config_dir: Path

    @staticmethod
    def from_dict(config: dict) -> 'PluginManagerProperties':
        """
        Create an instance of PluginManagerProperties from a dictionary.
        """
        return PluginManagerProperties(
            plugin_dir=Path(config.get('plugin_dir', '.')),
            enable=config.get('enable', False),
            plugin_context_path=config.get('plugin_context_path', ''),
            plugin_config_dir=Path(config.get('plugin_config_dir', '.'))
        )



# Example dictionary to simulate configuration loading
config_dict = {
    'plugin_dir': '/path/to/plugins',
    'enable': True,
    'plugin_context_path': '/plugins',
    'plugin_config_dir': '/path/to/plugin/configs'
}

# Create PluginManagerProperties instance from dictionary
plugin_manager_properties = PluginManagerProperties.from_dict(config_dict)

print(plugin_manager_properties)
