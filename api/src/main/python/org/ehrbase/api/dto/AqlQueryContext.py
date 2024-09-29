from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

class MetaProperty(ABC):
    @abstractmethod
    def property_name(self) -> str:
        pass

class EhrbaseMetaProperty(Enum):
    OFFSET = "offset"
    FETCH = "fetch"
    DEFAULT_LIMIT = "default-limit"
    MAX_LIMIT = "max-limit"
    MAX_FETCH = "max-fetch"
    RESULT_SIZE = "resultsize"
    DRY_RUN = "dry_run"
    EXECUTED_SQL = "executed_sql"
    QUERY_PLAN = "query_plan"

    def property_name(self) -> str:
        return self.value

class AqlQueryContext(ABC):
    BEAN_NAME = "scopedAqlQueryContext"
    OPENEHR_REST_API_VERSION = "1.0.3"

    @abstractmethod
    def create_meta_data(self, location: str) -> Any:
        pass

    @abstractmethod
    def show_executed_aql(self) -> bool:
        pass

    @abstractmethod
    def is_dry_run(self) -> bool:
        pass

    @abstractmethod
    def show_executed_sql(self) -> bool:
        pass

    @abstractmethod
    def show_query_plan(self) -> bool:
        pass

    @abstractmethod
    def set_executed_aql(self, executed_aql: str) -> None:
        pass

    @abstractmethod
    def set_meta_property(self, property: MetaProperty, value: Any) -> None:
        pass




class AqlQueryContextImpl(AqlQueryContext):
    def create_meta_data(self, location: str) -> Any:
        return urlparse(location)

    def show_executed_aql(self) -> bool:
        return True

    def is_dry_run(self) -> bool:
        return False

    def show_executed_sql(self) -> bool:
        return True

    def show_query_plan(self) -> bool:
        return True

    def set_executed_aql(self, executed_aql: str) -> None:
        self.executed_aql = executed_aql

    def set_meta_property(self, property: MetaProperty, value: Any) -> None:
        setattr(self, property.property_name(), value)

# Example usage
context = AqlQueryContextImpl()
context.set_meta_property(EhrbaseMetaProperty.OFFSET, 10)
print(context.create_meta_data("http://example.com"))
