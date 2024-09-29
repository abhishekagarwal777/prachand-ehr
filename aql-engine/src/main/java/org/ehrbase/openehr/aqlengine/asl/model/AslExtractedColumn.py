from typing import List, Optional, Set, Union
from enum import Enum
from dataclasses import dataclass
from aql_object_path import AqlObjectPath, PathNode  # Adjust import as needed
from jooq_tables import Tables  # Adjust import as needed

@dataclass
class AslExtractedColumn(Enum):
    NAME_VALUE = (
        AqlObjectPathUtil.NAME_VALUE,
        [Tables.COMP_DATA.ENTITY_NAME],
        str,
        False,
        *[s.name for s in StructureRmType] + [s.name for s in AncestorStructureRmType]
    )
    VO_ID = (
        AqlObjectPath.parse("uid/value"),
        [Tables.COMP_DATA.VO_ID, Tables.COMP_VERSION.SYS_VERSION],
        str,
        True,
        StructureRmType.COMPOSITION.name,
        StructureRmType.EHR_STATUS.name,
        RmConstants.ORIGINAL_VERSION
    )
    ROOT_CONCEPT = (
        AqlObjectPathUtil.ARCHETYPE_NODE_ID,
        [Tables.COMP_VERSION.ROOT_CONCEPT],
        str,
        True,
        StructureRmType.COMPOSITION.name
    )
    ARCHETYPE_NODE_ID = (
        AqlObjectPathUtil.ARCHETYPE_NODE_ID,
        [Tables.COMP_DATA.RM_ENTITY, Tables.COMP_DATA.ENTITY_CONCEPT],
        str,
        False,
        *[s.name for s in StructureRmType if s != StructureRmType.COMPOSITION] +
        [s.name for s in AncestorStructureRmType]
    )
    TEMPLATE_ID = (
        AqlObjectPath.parse("archetype_details/template_id/value"),
        [Tables.COMP_VERSION.TEMPLATE_ID],
        str,
        True,
        StructureRmType.COMPOSITION.name
    )

    # EHR
    EHR_ID = (
        AqlObjectPath.parse("ehr_id/value"),
        [Tables.EHR_.ID],
        UUID,
        False,
        RmConstants.EHR
    )
    EHR_SYSTEM_ID = (
        AqlObjectPath.parse("system_id/value"),
        [],
        str,
        False,
        RmConstants.EHR
    )
    EHR_SYSTEM_ID_DV = (
        AqlObjectPath.parse("system_id"),
        [],
        str,
        False,
        RmConstants.EHR
    )
    EHR_TIME_CREATED_DV = (
        AqlObjectPath.parse("time_created"),
        [Tables.EHR_.CREATION_DATE],
        str,
        False,
        RmConstants.EHR
    )
    EHR_TIME_CREATED = (
        AqlObjectPath.parse("time_created/value"),
        [Tables.EHR_.CREATION_DATE],
        str,
        False,
        RmConstants.EHR
    )

    # ORIGINAL_VERSION
    OV_CONTRIBUTION_ID = (
        AqlObjectPath.parse("contribution/id/value"),
        [Tables.COMP_VERSION.CONTRIBUTION_ID],
        str,
        True,
        RmConstants.ORIGINAL_VERSION
    )
    OV_TIME_COMMITTED_DV = (
        AqlObjectPath.parse("commit_audit/time_committed"),
        [Tables.COMP_VERSION.SYS_PERIOD_LOWER],
        str,
        True,
        RmConstants.ORIGINAL_VERSION
    )
    OV_TIME_COMMITTED = (
        AqlObjectPath.parse("commit_audit/time_committed/value"),
        [Tables.COMP_VERSION.SYS_PERIOD_LOWER],
        str,
        True,
        RmConstants.ORIGINAL_VERSION
    )

    # AUDIT_DETAILS
    AD_SYSTEM_ID = (
        AqlObjectPath.parse("system_id"),
        [],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_DESCRIPTION_DV = (
        AqlObjectPath.parse("description"),
        [Tables.AUDIT_DETAILS.DESCRIPTION],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_DESCRIPTION_VALUE = (
        AqlObjectPath.parse("description/value"),
        [Tables.AUDIT_DETAILS.DESCRIPTION],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_CHANGE_TYPE_DV = (
        AqlObjectPath.parse("change_type"),
        [Tables.AUDIT_DETAILS.CHANGE_TYPE],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_CHANGE_TYPE_VALUE = (
        AqlObjectPath.parse("change_type/value"),
        [Tables.AUDIT_DETAILS.CHANGE_TYPE],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_CHANGE_TYPE_CODE_STRING = (
        AqlObjectPath.parse("change_type/defining_code/code_string"),
        [Tables.AUDIT_DETAILS.CHANGE_TYPE],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_CHANGE_TYPE_PREFERRED_TERM = (
        AqlObjectPath.parse("change_type/defining_code/preferred_term"),
        [Tables.AUDIT_DETAILS.CHANGE_TYPE],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )
    AD_CHANGE_TYPE_TERMINOLOGY_ID_VALUE = (
        AqlObjectPath.parse("change_type/defining_code/terminology_id/value"),
        [],
        str,
        True,
        RmConstants.AUDIT_DETAILS
    )

    def __init__(self, path, columns, column_type, requires_version_table, *allowed_rm_types):
        self.path = path
        self.columns = columns
        self.column_type = column_type
        self.requires_version_table = requires_version_table
        self.allowed_rm_types = set(allowed_rm_types)

    def get_path(self) -> AqlObjectPath:
        return self.path

    def get_allowed_rm_types(self) -> Set[str]:
        return self.allowed_rm_types

    def requires_version_table(self) -> bool:
        return self.requires_version_table

    @staticmethod
    def find(contains, to_match: AqlObjectPath) -> Optional['AslExtractedColumn']:
        return AslExtractedColumn.find(contains.get_rm_type(), to_match)

    @staticmethod
    def find(containment_type: str, to_match: AqlObjectPath) -> Optional['AslExtractedColumn']:
        return next((ep for ep in AslExtractedColumn if ep.matches(containment_type, to_match)), None)

    @staticmethod
    def find_with_skip(containment_type: str, to_match: AqlObjectPath, skip: int) -> Optional['AslExtractedColumn']:
        path_nodes = to_match.get_path_nodes()[skip:] if to_match else []
        return AslExtractedColumn.find(containment_type, AqlObjectPath(path_nodes))

    def matches(self, containment_type: str, to_match: AqlObjectPath) -> bool:
        return containment_type in self.allowed_rm_types and self.path == to_match

    def get_column_type(self) -> type:
        return self.column_type

    def get_columns(self) -> List[str]:
        return self.columns
