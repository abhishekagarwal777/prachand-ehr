from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Any

T = TypeVar('T')  # Concept type
ID = TypeVar('ID')  # Identifier type
U = TypeVar('U')  # Custom operation parameters type

class TerminologyServer(ABC, Generic[T, ID, U]):

    @abstractmethod
    def expand(self, value_set_id: ID) -> List[T]:
        """
        Expands the value set identified by the provided ID.

        :param value_set_id: The ID of the value set to expand
        :return: List of concepts of type T that conform the expansion of the value set
        """
        pass

    @abstractmethod
    def expand_with_parameters(self, value_set_id: ID, *operation_params: U) -> List[T]:
        """
        Expands the value set identified by the provided ID with additional parameters.

        :param value_set_id: The ID of the value set to expand
        :param operation_params: Additional parameters for the operation
        :return: List of concepts of type T that conform the expansion of the value set
        """
        pass

    @abstractmethod
    def look_up(self, concept_id: ID) -> T:
        """
        Searches all the attributes associated with the concept that corresponds to the provided ID.

        :param concept_id: The ID of the concept to look up
        :return: A complex object of type T that contains all the attributes associated with the concept
        """
        pass

    @abstractmethod
    def validate(self, concept: T, value_set_id: ID) -> bool:
        """
        Evaluates if the concept belongs to the value set identified by the provided ID.

        :param concept: The concept to evaluate
        :param value_set_id: The ID of the value set
        :return: True if the concept belongs to the specified value set, otherwise False
        """
        pass

    @abstractmethod
    def validate_with_params(self, *operation_params: U) -> bool:
        """
        Evaluates if the concept provided in the operation parameters belongs to the value set provided.

        :param operation_params: Dynamic list of parameters to perform the operation
        :return: True if the concept belongs to the specified value set, otherwise False
        """
        pass

    @abstractmethod
    def subsumes(self, concept_a: T, concept_b: T) -> 'SubsumptionResult':
        """
        Evaluates if concept B subsumes concept A.

        :param concept_a: Concept that is subsumed by the concept in the second parameter
        :param concept_b: Concept that subsumes the concept in the first parameter
        :return: Result of the subsumption evaluation
        """
        pass

    class SubsumptionResult:
        EQUIVALENT = 'EQUIVALENT'
        SUBSUMES = 'SUBSUMES'
        SUBSUMED_BY = 'SUBSUMED_BY'
        NOT_SUBSUMED = 'NOT_SUBSUMED'

    class TerminologyAdapter:
        FHIR = "hl7.org/fhir/R4"
        OCEAN = "OTS.OCEANHEALTHSYSTEMS.COM"
        BETTER = "bts.better.care"
        DTS4 = "dts4.apelon.com"
        INDIZEN = "cts2.indizen.com"

        supported_adapters = {FHIR}

        def __init__(self, adapter_id: str):
            self.adapter_id = adapter_id

        def get_adapter_id(self) -> str:
            return self.adapter_id

        @classmethod
        def is_adapter_supported(cls, adapter_to_check: str) -> bool:
            return adapter_to_check in cls.__dict__.values()
