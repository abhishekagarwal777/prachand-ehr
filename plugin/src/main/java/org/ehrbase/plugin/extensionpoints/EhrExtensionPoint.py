from abc import ABC, abstractmethod
from typing import Callable, Optional, TypeVar
import uuid

# Define type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class OriginalVersion:
    pass  # Placeholder for the OriginalVersion class from the original Java code

class EhrStatus:
    pass  # Placeholder for the EhrStatus class

class EhrStatusWithEhrId:
    pass  # Placeholder for the EhrStatusWithEhrId class

class EhrStatusVersionRequestParameters:
    pass  # Placeholder for the EhrStatusVersionRequestParameters class

class EhrExtensionPoint(ABC):
    """
    Extension Point for Ehr handling.
    """

    @abstractmethod
    def around_creation(self, input: EhrStatusWithEhrId, 
                        chain: Callable[[EhrStatusWithEhrId], uuid.UUID]) -> uuid.UUID:
        """
        Intercept Ehr create.

        Args:
            input: Ehr with ehrStatus to be created and optional ehrId.
            chain: Next Extension Point.

        Returns:
            UUID of the created ehr.
        """
        return chain(input)

    @abstractmethod
    def around_update(self, input: EhrStatusWithEhrId, 
                      chain: Callable[[EhrStatusWithEhrId], uuid.UUID]) -> uuid.UUID:
        """
        Intercept EhrStatus update.

        Args:
            input: Update ehrStatus in ehrId.
            chain: Next Extension Point.

        Returns:
            UUID of the updated EhrStatus.
        """
        return chain(input)

    @abstractmethod
    def around_retrieve_at_version(self, input: EhrStatusVersionRequestParameters, 
                                    chain: Callable[[EhrStatusVersionRequestParameters, Optional[OriginalVersion[EhrStatus]]]]) -> Optional[OriginalVersion[EhrStatus]]:
        """
        Intercept EhrStatus retrieve.

        Args:
            input: Get ehrStatus in ehrId.
            chain: Next Extension Point.

        Returns:
            OriginalVersion of EhrStatus.
        """
        return chain(input)
