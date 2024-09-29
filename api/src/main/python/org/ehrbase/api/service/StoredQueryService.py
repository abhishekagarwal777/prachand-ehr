from abc import ABC, abstractmethod
from typing import List, Optional

class QueryDefinitionResultDto:
    # Assuming QueryDefinitionResultDto is a data transfer object with relevant attributes.
    def __init__(self, name: str, version: str, query_string: str):
        self.name = name
        self.version = version
        self.query_string = query_string

class StoredQueryService(ABC):

    @abstractmethod
    def retrieve_stored_queries(self, fully_qualified_name: str) -> List[QueryDefinitionResultDto]:
        """
        Retrieves a list of stored queries based on the fully qualified name.
        """
        pass

    @abstractmethod
    def retrieve_stored_query(self, qualified_name: str, version: str) -> Optional[QueryDefinitionResultDto]:
        """
        Retrieves a specific stored query based on the qualified name and version.
        """
        pass

    @abstractmethod
    def create_stored_query(self, qualified_name: str, version: str, query_string: str) -> QueryDefinitionResultDto:
        """
        Creates a new stored query with the given name, version, and query string.
        """
        pass

    @abstractmethod
    def delete_stored_query(self, qualified_name: str, version: str) -> None:
        """
        Deletes a stored query based on the qualified name and version.
        """
        pass
