from abc import ABC, abstractmethod

class AuthorizationInfo(ABC):
    """
    Interface to represent authorization information.
    """

    @abstractmethod
    def is_disabled(self) -> bool:
        """
        Abstract method to determine if authorization is disabled.
        """
        pass

class AuthorizationDisabled(AuthorizationInfo):
    """
    Class representing a disabled authorization state.
    """

    def is_disabled(self) -> bool:
        """
        Indicates that the authorization is disabled.
        """
        return True

class AuthorizationEnabled(AuthorizationInfo):
    """
    Class representing an enabled authorization state.
    """

    def is_disabled(self) -> bool:
        """
        Indicates that the authorization is enabled.
        """
        return False
