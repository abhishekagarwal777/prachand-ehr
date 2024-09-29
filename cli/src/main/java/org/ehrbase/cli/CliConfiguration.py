from typing import Any
from dependency_injector import containers, providers

class CliConfiguration(containers.DeclarativeContainer):
    config = providers.Configuration()
    # Add other components here if needed
