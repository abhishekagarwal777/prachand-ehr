from typing import List, Dict, Set, Type, Optional
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class IdentifiedPath:
    pass

@dataclass
class AslColumnField:
    field_type: Type
    name: str
    source: 'FieldSource'
    is_dv_ordered: bool

@dataclass
class AslDvOrderedColumnField(AslColumnField):
    dv_ordered_types: Set[str]

@dataclass
class FieldSource:
    owner: 'AslPathDataQuery'

    @classmethod
    def with_owner(cls, owner: 'AslPathDataQuery') -> 'FieldSource':
        return cls(owner=owner)

@dataclass
class AqlObjectPath:
    @dataclass
    class PathNode:
        pass

@dataclass
class AslPathFilterJoinCondition:
    pass

class AslDataQuery:
    def __init__(self, alias: str, base: 'AslQuery', base_provider: 'AslQuery'):
        self.alias = alias
        self.base = base
        self.base_provider = base_provider

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        return {}

    def get_select(self) -> List['AslField']:
        return []

class AslPathDataQuery(AslDataQuery):
    DATA_COLUMN_NAME = "data"

    def __init__(self, alias: str, base: 'AslQuery', base_provider: 'AslQuery', 
                 data_path: List[AqlObjectPath.PathNode], multiple_valued: bool, 
                 dv_ordered_types: Optional[Set[str]], field_type: Type):
        super().__init__(alias, base, base_provider)
        
        if not isinstance(base, (AslDataQuery, AslPathDataQuery)):
            raise ValueError(f"{type(base).__name__} is not a valid base for AslPathDataQuery")
        
        self.data_path = data_path
        self.dv_ordered_types = dv_ordered_types or set()
        field_source = FieldSource.with_owner(self)
        
        if not self.dv_ordered_types:
            self.data_field = AslColumnField(field_type, self.DATA_COLUMN_NAME, field_source, False)
        else:
            self.data_field = AslDvOrderedColumnField(field_type, self.DATA_COLUMN_NAME, field_source, self.dv_ordered_types)
        
        self.multiple_valued = multiple_valued

    def get_data_field(self) -> AslColumnField:
        return self.data_field

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        return {}

    def get_select(self) -> List[AslColumnField]:
        return [self.data_field]

    def get_path_nodes(self, field: AslColumnField) -> List[AqlObjectPath.PathNode]:
        if field != self.data_field:
            raise ValueError("Field is not part of this AslPathDataQuery")
        return self.data_path

    def is_multiple_valued(self) -> bool:
        return self.multiple_valued

    def get_dv_ordered_types(self) -> Set[str]:
        return self.dv_ordered_types
