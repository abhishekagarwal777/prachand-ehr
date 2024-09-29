from typing import List, Dict, Collection, Set
from dataclasses import dataclass, field
from enum import Enum
from .asl_query import AslQuery
from .asl_field import AslField, AslColumnField
from .asl_condition import AslFieldValueQueryCondition, AslConditionOperator
from .asl_join_condition import AslPathFilterJoinCondition
from .ident_path import IdentifiedPath
from .structure_rm_type import StructureRmType, StructureRoot
from .asl_utils import AslUtils
from .rm_attribute_alias import RmAttributeAlias
from jooq_tables import Tables  # Adjust import as needed

class AslSourceRelation(Enum):
    EHR = (StructureRoot.EHR, None, Tables.EHR_)
    EHR_STATUS = (StructureRoot.EHR_STATUS, Tables.EHR_STATUS_VERSION, Tables.EHR_STATUS_DATA)
    COMPOSITION = (StructureRoot.COMPOSITION, Tables.COMP_VERSION, Tables.COMP_DATA)
    FOLDER = (StructureRoot.FOLDER, Tables.EHR_FOLDER_VERSION, Tables.EHR_FOLDER_DATA)
    AUDIT_DETAILS = (None, None, Tables.AUDIT_DETAILS)

    def __init__(self, structure_root, version_table, data_table):
        self.structure_root = structure_root
        self.version_table = version_table
        self.data_table = data_table
        self.pkey_fields = (version_table or data_table).get_primary_key().get_fields_array()

    @property
    def structure_root(self):
        return self._structure_root

    @property
    def version_table(self):
        return self._version_table

    @property
    def data_table(self):
        return self._data_table

    @property
    def pkey_fields(self):
        return self._pkey_fields

    _BY_STRUCTURE_ROOT = {v.structure_root: v for v in AslSourceRelation}

    @staticmethod
    def get(structure_root):
        return AslSourceRelation._BY_STRUCTURE_ROOT.get(structure_root)

@dataclass
class AslStructureQuery(AslQuery):
    ENTITY_ATTRIBUTE: str = "entity_attribute"

    type: AslSourceRelation
    rm_types: Collection[str]
    alias: str
    requires_version_table_join: bool
    represents_original_version_expression: bool = False

    join_conditions_for_filtering: Dict[IdentifiedPath, AslPathFilterJoinCondition] = field(default_factory=dict)
    fields: List[AslField] = field(default_factory=list)

    NON_LOCATABLE_STRUCTURE_RM_TYPES: Set[str] = set(
        [s.get_alias() for s in StructureRmType if s.is_structure_entry() and not issubclass(s.type, Locatable)]
    )

    def __post_init__(self):
        super().__post_init__()

        if self.type not in [AslSourceRelation.EHR, AslSourceRelation.AUDIT_DETAILS]:
            if self.rm_types:
                aliased_rm_types = [StructureRmType.get_alias_or_type_name(rt) for rt in self.rm_types]
                if self.NON_LOCATABLE_STRUCTURE_RM_TYPES.issubset(aliased_rm_types):
                    self.structure_conditions.append(AslFieldValueQueryCondition(
                        AslUtils.find_field_for_owner(AslStructureColumn.ENTITY_CONCEPT, self.get_select(), self),
                        AslConditionOperator.IS_NULL,
                        []
                    ))

            if self.rm_types_constraint:
                aliased_rm_types = [StructureRmType.get_alias_or_type_name(rt) for rt in self.rm_types_constraint]
                self.structure_conditions.append(AslFieldValueQueryCondition(
                    AslUtils.find_field_for_owner(AslStructureColumn.RM_ENTITY, self.get_select(), self),
                    AslConditionOperator.IN,
                    aliased_rm_types
                ))

            if self.attribute:
                self.structure_conditions.append(AslFieldValueQueryCondition(
                    AslColumnField(str, self.ENTITY_ATTRIBUTE, FieldSource.with_owner(self), False),
                    AslConditionOperator.EQ,
                    [RmAttributeAlias.get_alias(self.attribute)]
                ))

    def add_join_condition_for_filtering(self, ip: IdentifiedPath, condition: AslQueryCondition):
        self.join_conditions_for_filtering[ip] = AslPathFilterJoinCondition(self, condition)

    def join_conditions_for_filtering(self) -> Dict[IdentifiedPath, List[AslPathFilterJoinCondition]]:
        return {k: [v] for k, v in self.join_conditions_for_filtering.items()}

    def get_select(self) -> List[AslField]:
        return self.fields

    def get_alias(self) -> str:
        return self.alias

    def get_type(self) -> AslSourceRelation:
        return self.type
