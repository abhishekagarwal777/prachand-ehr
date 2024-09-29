from typing import Callable, Optional, TypeVar
from abc import ABC, abstractmethod
import uuid

# Define type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

class Composition:
    pass  # Placeholder for the Composition class from the original Java code

class CompositionWithEhrId:
    pass  # Placeholder for the CompositionWithEhrId class

class CompositionWithEhrIdAndPreviousVersion:
    pass  # Placeholder for the CompositionWithEhrIdAndPreviousVersion class

class CompositionVersionIdWithEhrId:
    pass  # Placeholder for the CompositionVersionIdWithEhrId class

class CompositionIdWithVersionAndEhrId:
    pass  # Placeholder for the CompositionIdWithVersionAndEhrId class

class CompositionExtensionPoint(ABC):
    """
    Extension Point for Composition handling.
    """

    @abstractmethod
    def around_creation(self, input: CompositionWithEhrId, chain: Callable[[CompositionWithEhrId], uuid.UUID]) -> uuid.UUID:
        """
        Intercept Composition create.

        Args:
            input: Composition to be created in ehr with ehrId.
            chain: Next Extension Point.

        Returns:
            UUID of the created Composition.
        """
        return chain(input)

    @abstractmethod
    def around_update(self, input: CompositionWithEhrIdAndPreviousVersion, 
                      chain: Callable[[CompositionWithEhrIdAndPreviousVersion], uuid.UUID]) -> uuid.UUID:
        """
        Intercept Composition update.

        Args:
            input: Composition to update previous version in ehr with ehrId.
            chain: Next Extension Point.

        Returns:
            UUID of the updated Composition.
        """
        return chain(input)

    @abstractmethod
    def around_delete(self, input: CompositionVersionIdWithEhrId, 
                      chain: Callable[[CompositionVersionIdWithEhrId], None]) -> None:
        """
        Intercept Composition delete.

        Args:
            input: Composition version in ehr with ehrId to be deleted.
            chain: Next Extension Point.
        """
        return chain(input)

    @abstractmethod
    def around_retrieve(self, input: CompositionIdWithVersionAndEhrId, 
                         chain: Callable[[CompositionIdWithVersionAndEhrId], Optional[Composition]]) -> Optional[Composition]:
        """
        Intercept Composition retrieve.

        Args:
            input: Composition id with version in ehr with ehrId to be retrieved.
            chain: Next Extension Point.

        Returns:
            Composition object if found.
        """
        return chain(input)
