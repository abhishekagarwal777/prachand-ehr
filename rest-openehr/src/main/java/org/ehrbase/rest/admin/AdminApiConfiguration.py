import os
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class AdminApiConfiguration:
    active: bool = False
    allow_delete_all: bool = False

    def __post_init__(self):
        # Load configuration from environment variables
        self.active = self.get_env_var("ADMIN_API_ACTIVE", self.active)
        self.allow_delete_all = self.get_env_var("ADMIN_API_ALLOW_DELETE_ALL", self.allow_delete_all)

    @staticmethod
    def get_env_var(var_name: str, default: Any) -> Any:
        """Retrieve environment variable, return default if not found."""
        return os.getenv(var_name, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "active": self.active,
            "allow_delete_all": self.allow_delete_all
        }

# Example usage
if __name__ == "__main__":
    config = AdminApiConfiguration()
    print(config.to_dict())
