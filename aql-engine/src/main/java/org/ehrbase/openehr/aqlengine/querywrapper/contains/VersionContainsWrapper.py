from typing import Optional

class VersionContainsWrapper(ContainsWrapper):
    def __init__(self, alias: str, child: RmContainsWrapper):
        self._alias = alias
        self._child = child

    def get_rm_type(self) -> str:
        return RmConstants.ORIGINAL_VERSION

    def alias(self) -> str:
        return self._alias

    def child(self) -> RmContainsWrapper:
        return self._child

    def __str__(self) -> str:
        return f"VersionContainsWrapper[alias={self._alias}, child={self._child}]"

# Define RmConstants and other dependent classes

class RmConstants:
    ORIGINAL_VERSION = "original_version"

# Assuming RmContainsWrapper class is already defined as per the previous code
