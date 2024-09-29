from typing import Optional
from urllib.parse import urlparse

class CliAqlQueryContext(AqlQueryContext):
    UNSUPPORTED_MSG = "AQL is not supported on CLI"

    def create_meta_data(self, location: URI) -> MetaData:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def is_dry_run(self) -> bool:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def show_executed_aql(self) -> bool:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def show_executed_sql(self) -> bool:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def show_query_plan(self) -> bool:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def set_executed_aql(self, executed_aql: str) -> None:
        raise NotImplementedError(self.UNSUPPORTED_MSG)

    def set_meta_property(self, property: MetaProperty, value: Optional[object]) -> None:
        raise NotImplementedError(self.UNSUPPORTED_MSG)
