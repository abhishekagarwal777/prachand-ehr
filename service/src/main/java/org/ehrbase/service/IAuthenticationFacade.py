# Import necessary libraries for authentication
from abc import ABC, abstractmethod
from typing import Any

# Assuming a security library is available for authentication
class Authentication:
    # This is a placeholder for whatever the Authentication class should contain
    def __init__(self, principal: Any, credentials: Any, authorities: Any):
        self.principal = principal
        self.credentials = credentials
        self.authorities = authorities

class IAuthenticationFacade(ABC):
    @abstractmethod
    def get_authentication(self) -> Authentication:
        """Retrieve the current authentication object.

        Returns:
            Authentication: The current authentication object containing user details.
        """
        pass
