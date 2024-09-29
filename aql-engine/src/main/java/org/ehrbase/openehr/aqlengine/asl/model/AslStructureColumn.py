from enum import Enum
from typing import Optional, Type
from dataclasses import dataclass
import uuid
from datetime import datetime

# Placeholder implementations
class AslExtractedColumn:
    NAME_VALUE = 'name_value'
    TEMPLATE_ID = 'template_id'
    # Define other constants as needed

@dataclass
class AslColumnField:
    clazz: Type
    field_name: str
    extracted_column: Optional[str]
    from_version_table: Optional[bool]

@dataclass
class AslStructureColumn(Enum):
    VO_ID = ('vo_id', uuid.UUID, None)
    NUM = ('num', int, False)
    NUM_CAP = ('num_cap', int, False)
    PARENT_NUM = ('parent_num', int, False)
    EHR_ID = ('ehr_id', uuid.UUID, True)
    ENTITY_IDX = ('entity_idx', str, False)
    ENTITY_IDX_LEN = ('entity_idx_len', int, False)
    ENTITY_CONCEPT = ('entity_concept', str, False)
    ENTITY_NAME = ('entity_name', str, AslExtractedColumn.NAME_VALUE, False)
    RM_ENTITY = ('rm_entity', str, False)
    TEMPLATE_ID = ('template_id', uuid.UUID, AslExtractedColumn.TEMPLATE_ID, True)
    SYS_VERSION = ('sys_version', int, True)
    
    # Columns for VERSION querying
    AUDIT_ID = ('audit_id', uuid.UUID, True)
    CONTRIBUTION_ID = ('contribution_id', uuid.UUID, None, True)
    SYS_PERIOD_LOWER = ('sys_period_lower', datetime, None, True)

    def __init__(self, field_name: str, clazz: Type, extracted_column: Optional[str] = None, from_version_table: Optional[bool] = None):
        self.field_name = field_name
        self.clazz = clazz
        self.extracted_column = extracted_column
        self.from_version_table = from_version_table

    def field(self) -> AslColumnField:
        return AslColumnField(
            clazz=self.clazz,
            field_name=self.field_name,
            extracted_column=self.extracted_column,
            from_version_table=self.from_version_table
        )

    @property
    def is_from_version_table(self) -> bool:
        return self.from_version_table is not False

    @property
    def is_from_data_table(self) -> bool:
        return self.from_version_table is not True
