from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .asl_encapsulating_query import AslEncapsulatingQuery
from .asl_field import AslField, AslDvOrderedColumnField, AslOrderByField
from .asl_join_condition import AslPathFilterJoinCondition
from .ident_path import IdentifiedPath
from enum import Enum

class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class AslRootQuery(AslEncapsulatingQuery):
    fields: List[AslField] = field(default_factory=list)
    order_by_fields: List[AslOrderByField] = field(default_factory=list)
    group_by_fields: List[AslField] = field(default_factory=list)
    group_by_dv_ordered_magnitude_fields: List[AslDvOrderedColumnField] = field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()

    def get_select(self) -> List[AslField]:
        return self.fields

    def get_available_fields(self) -> List[AslField]:
        return super().get_select()

    def get_limit(self) -> Optional[int]:
        return self.limit

    def set_limit(self, limit: Optional[int]):
        self.limit = limit

    def get_offset(self) -> Optional[int]:
        return self.offset

    def set_offset(self, offset: Optional[int]):
        self.offset = offset

    def get_order_by_fields(self) -> List[AslOrderByField]:
        return self.order_by_fields

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        raise NotImplementedError("join_conditions_for_filtering() is not supported in AslRootQuery")

    def get_group_by_fields(self) -> List[AslField]:
        return self.group_by_fields

    def get_group_by_dv_ordered_magnitude_fields(self) -> List[AslDvOrderedColumnField]:
        return self.group_by_dv_ordered_magnitude_fields

    def add_order_by(self, field: AslField, sort_order: SortOrder, uses_aggregate_function_or_distinct: bool):
        self.order_by_fields.append(AslOrderByField(field=field, sort_order=sort_order))

        for f in field.fields_for_aggregation(self):
            if uses_aggregate_function_or_distinct and f not in self.group_by_fields:
                if isinstance(field, AslDvOrderedColumnField):
                    self.group_by_dv_ordered_magnitude_fields.append(field)
                else:
                    self.group_by_fields.append(f)
