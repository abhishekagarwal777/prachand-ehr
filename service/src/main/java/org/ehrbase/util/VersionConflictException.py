class VersionConflictException(Exception):
    """Exception raised for version conflict errors."""

    def __init__(self, sem_ver_str: str):
        """Initialize the exception with a version string.

        Args:
            sem_ver_str (str): The semantic version string that caused the conflict.
        """
        super().__init__(sem_ver_str)  # Call the base class constructor with the error message
