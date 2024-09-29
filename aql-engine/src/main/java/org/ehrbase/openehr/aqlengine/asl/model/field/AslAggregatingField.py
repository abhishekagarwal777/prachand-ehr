from typing import Optional
from enum import Enum

class AslQuery:
    pass

class AggregateFunctionName(Enum):
    # Assuming some aggregate function names are defined here
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"

class AslField:
    def get_owner(self) -> Optional[AslQuery]:
        pass

    def get_internal_provider(self) -> Optional[AslQuery]:
        pass

    def get_provider(self) -> Optional[AslQuery]:
        pass

    def aliased_name(self, name: str) -> str:
        pass

class AslVirtualField(AslField):
    def __init__(self, field_type: type, *args, **kwargs):
        super().__init__()

class AslAggregatingField(AslVirtualField):
    def __init__(self, function: AggregateFunctionName, base_field: Optional[AslField], distinct: bool):
        super().__init__(Number)
        self.function = function
        self.base_field = base_field
        self.distinct = distinct

    def get_function(self) -> AggregateFunctionName:
        return self.function

    def get_base_field(self) -> Optional[AslField]:
        return self.base_field

    def get_owner(self) -> Optional[AslQuery]:
        return self.base_field.get_owner() if self.base_field else None

    def get_internal_provider(self) -> Optional[AslQuery]:
        return self.base_field.get_internal_provider() if self.base_field else None

    def get_provider(self) -> Optional[AslQuery]:
        return self.base_field.get_provider() if self.base_field else None

    def aliased_name(self, name: str) -> str:
        if self.base_field:
            return f"agg_{self.base_field.aliased_name(name)}"
        return f"agg_{name}"

    def with_provider(self, provider: AslQuery) -> None:
        raise NotImplementedError("This method is not supported.")

    def copy_with_owner(self, asl_filtering_query: AslQuery) -> None:
        raise NotImplementedError("This method is not supported.")

    def is_distinct(self) -> bool:
        return self.distinct


# Example usage
base_field = AslField()  # Replace with actual implementation
agg_field = AslAggregatingField(AggregateFunctionName.SUM, base_field, distinct=True)
print(agg_field.aliased_name("example_field"))
        