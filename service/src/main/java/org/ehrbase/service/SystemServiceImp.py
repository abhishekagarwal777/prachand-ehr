import os


class SystemService:
    """
    Python equivalent of the SystemService interface in Java.
    Provides an interface for system-related services.
    """

    def get_system_id(self):
        """
        Abstract method to be implemented in the implementing class.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class SystemServiceImp(SystemService):
    """
    Python equivalent of the SystemServiceImp class in Java.
    Implements the SystemService interface and retrieves the system's node name.
    """

    def __init__(self):
        # Retrieve system ID from environment variables or default to 'local.ehrbase.org'
        self.system_id = os.getenv("SERVER_NODENAME", "local.ehrbase.org")

    def get_system_id(self):
        """
        Returns the system ID.
        """
        return self.system_id


# Example usage of the SystemServiceImp class
if __name__ == "__main__":
    system_service = SystemServiceImp()
    print(f"System ID: {system_service.get_system_id()}")
