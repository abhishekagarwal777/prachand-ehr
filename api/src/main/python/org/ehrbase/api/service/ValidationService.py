from abc import ABC, abstractmethod
from typing import Protocol
from your_module_definitions import Composition, EhrStatusDto, ContributionCreateDto

class ValidationService(ABC):

    @abstractmethod
    def check_composition(self, composition: Composition) -> None:
        """
        Initially check if the `composition` is valid for further processing.

        :param composition: The composition to validate
        :raises ValueError: If the given `composition` is invalid
        """
        pass

    @abstractmethod
    def check_ehr_status(self, ehr_status: EhrStatusDto) -> None:
        """
        Initially check if `ehrStatus` is valid for further processing.

        :param ehr_status: The EHR status to validate
        :raises ValueError: If the given `ehrStatus` is invalid
        """
        pass

    @abstractmethod
    def check_contribution(self, contribution: ContributionCreateDto) -> None:
        """
        Initially check if `contribution` is valid for further processing.

        :param contribution: The contribution to validate
        :raises ValueError: If the given `contribution` is invalid
        """
        pass
