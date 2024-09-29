from typing import List, Dict
from dataclasses import dataclass, field
from .asl_query import AslDataQuery
from .asl_field import AslField, AslColumnField
from .asl_join_condition import AslPathFilterJoinCondition
from .ident_path import IdentifiedPath

@dataclass
class AslRmObjectDataQuery(AslDataQuery):
    field: AslColumnField = field(init=False)

    def __post_init__(self):
        super().__init__(alias=self.alias, base=self.base, base_provider=self.base_provider)
        self.field = AslColumnField(field_type=object, column_name="data", field_source=FieldSource.with_owner(self), multiple_valued=False)

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        return {}

    def get_select(self) -> List[AslField]:
        return [self.field]
