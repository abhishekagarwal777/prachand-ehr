class PluginHelper:
    """Utility class for Plugin Management."""

    PLUGIN_MANAGER_PREFIX = "plugin-manager"

    def __init__(self):
        """Private constructor to prevent instantiation."""
        raise NotImplementedError("This is a utility class and cannot be instantiated.")

# Example usage
if __name__ == "__main__":
    print(f"Plugin Manager Prefix: {PluginHelper.PLUGIN_MANAGER_PREFIX}")
