from abc import ABC, abstractmethod
from typing import Any

class AslRootQuery:
    # Define the structure of AslRootQuery based on your requirements
    pass

class SelectQuery:
    def __init__(self, record_type: Any):
        self.record_type = record_type

    # Define methods and attributes of SelectQuery based on your requirements
    pass

class AqlSqlQueryPostProcessor(ABC):
    @abstractmethod
    def after_build_sql_query(self, asl_root_query: AslRootQuery, query: SelectQuery) -> None:
        """
        Method to modify the SelectQuery generated from the given AslRootQuery.

        Args:
            asl_root_query (AslRootQuery): The ASL root query object.
            query (SelectQuery): The select query object to be modified.
        """
        pass
