class InvalidVersionFormatException(ValueError):
    def __init__(self, sem_ver_str):
        super().__init__(f"Invalid version format: {sem_ver_str}")
