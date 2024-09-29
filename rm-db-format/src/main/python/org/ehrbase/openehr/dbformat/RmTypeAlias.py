from typing import List, Dict, Optional

class StructureRmType:
    COMPOSITION = "COMPOSITION"
    FOLDER = "FOLDER"
    EHR_STATUS = "EHR_STATUS"
    FEEDER_AUDIT = "FEEDER_AUDIT"
    FEEDER_AUDIT_DETAILS = "FEEDER_AUDIT_DETAILS"
    EVENT_CONTEXT = "EVENT_CONTEXT"
    SECTION = "SECTION"
    GENERIC_ENTRY = "GENERIC_ENTRY"
    ADMIN_ENTRY = "ADMIN_ENTRY"
    OBSERVATION = "OBSERVATION"
    INSTRUCTION = "INSTRUCTION"
    ACTION = "ACTION"
    EVALUATION = "EVALUATION"
    INSTRUCTION_DETAILS = "INSTRUCTION_DETAILS"
    ACTIVITY = "ACTIVITY"
    HISTORY = "HISTORY"
    POINT_EVENT = "POINT_EVENT"
    INTERVAL_EVENT = "INTERVAL_EVENT"
    ITEM_LIST = "ITEM_LIST"
    ITEM_SINGLE = "ITEM_SINGLE"
    ITEM_TABLE = "ITEM_TABLE"
    ITEM_TREE = "ITEM_TREE"
    CLUSTER = "CLUSTER"
    ELEMENT = "ELEMENT"

class RmTypeAlias:
    def __init__(self, type_: str, alias: str, structure_alias: bool):
        self.type = type_
        self.alias = alias
        self.structure_alias = structure_alias

    @staticmethod
    def values() -> List['RmTypeAlias']:
        return [
            RmTypeAlias.structure_alias(StructureRmType.COMPOSITION),
            RmTypeAlias.structure_alias(StructureRmType.FOLDER),
            RmTypeAlias.structure_alias(StructureRmType.EHR_STATUS),
            RmTypeAlias.structure_alias(StructureRmType.FEEDER_AUDIT),
            RmTypeAlias.structure_alias(StructureRmType.FEEDER_AUDIT_DETAILS),
            RmTypeAlias.structure_alias(StructureRmType.EVENT_CONTEXT),
            RmTypeAlias.structure_alias(StructureRmType.SECTION),
            RmTypeAlias.structure_alias(StructureRmType.GENERIC_ENTRY),
            RmTypeAlias.structure_alias(StructureRmType.ADMIN_ENTRY),
            RmTypeAlias.structure_alias(StructureRmType.OBSERVATION),
            RmTypeAlias.structure_alias(StructureRmType.INSTRUCTION),
            RmTypeAlias.structure_alias(StructureRmType.ACTION),
            RmTypeAlias.structure_alias(StructureRmType.EVALUATION),
            RmTypeAlias.structure_alias(StructureRmType.INSTRUCTION_DETAILS),
            RmTypeAlias.structure_alias(StructureRmType.ACTIVITY),
            RmTypeAlias.structure_alias(StructureRmType.HISTORY),
            RmTypeAlias.structure_alias(StructureRmType.POINT_EVENT),
            RmTypeAlias.structure_alias(StructureRmType.INTERVAL_EVENT),
            RmTypeAlias.structure_alias(StructureRmType.ITEM_LIST),
            RmTypeAlias.structure_alias(StructureRmType.ITEM_SINGLE),
            RmTypeAlias.structure_alias(StructureRmType.ITEM_TABLE),
            RmTypeAlias.structure_alias(StructureRmType.ITEM_TREE),
            RmTypeAlias.structure_alias(StructureRmType.CLUSTER),
            RmTypeAlias.structure_alias(StructureRmType.ELEMENT),
            RmTypeAlias.alias("ARCHETYPED", "AR"),
            RmTypeAlias.alias("ARCHETYPE_ID", "AX"),
            RmTypeAlias.alias("ATTESTATION", "AT"),
            RmTypeAlias.alias("AUDIT_DETAILS", "AD"),
            RmTypeAlias.alias("CODE_PHRASE", "C"),
            RmTypeAlias.alias("DV_BOOLEAN", "b"),
            RmTypeAlias.alias("DV_CODED_TEXT", "c"),
            RmTypeAlias.alias("DV_COUNT", "co"),
            RmTypeAlias.alias("DV_DATE", "d"),
            RmTypeAlias.alias("DV_DATE_TIME", "dt"),
            RmTypeAlias.alias("DV_DURATION", "du"),
            RmTypeAlias.alias("DV_EHR_URI", "eu"),
            RmTypeAlias.alias("DV_IDENTIFIER", "id"),
            RmTypeAlias.alias("DV_INTERVAL", "iv"),
            RmTypeAlias.alias("DV_MULTIMEDIA", "mu"),
            RmTypeAlias.alias("DV_ORDINAL", "o"),
            RmTypeAlias.alias("DV_PARAGRAPH", "p"),
            RmTypeAlias.alias("DV_PARSABLE", "pa"),
            RmTypeAlias.alias("DV_PROPORTION", "pr"),
            RmTypeAlias.alias("DV_QUANTITY", "q"),
            RmTypeAlias.alias("DV_SCALE", "sc"),
            RmTypeAlias.alias("DV_STATE", "st"),
            RmTypeAlias.alias("DV_TEXT", "x"),
            RmTypeAlias.alias("DV_TIME", "t"),
            RmTypeAlias.alias("DV_URI", "u"),
            RmTypeAlias.alias("GENERIC_ID", "GX"),
            RmTypeAlias.alias("HIER_OBJECT_ID", "HX"),
            RmTypeAlias.alias("INTERNET_ID", "IX"),
            RmTypeAlias.alias("INTERVAL", "IV"),
            RmTypeAlias.alias("ISM_TRANSITION", "IT"),
            RmTypeAlias.alias("LINK", "LK"),
            RmTypeAlias.alias("LOCATABLE_REF", "LR"),
            RmTypeAlias.alias("OBJECT_REF", "OR"),
            RmTypeAlias.alias("OBJECT_VERSION_ID", "OV"),
            RmTypeAlias.alias("PARTICIPATION", "PA"),
            RmTypeAlias.alias("PARTY_IDENTIFIED", "PI"),
            RmTypeAlias.alias("PARTY_REF", "PF"),
            RmTypeAlias.alias("PARTY_RELATED", "PR"),
            RmTypeAlias.alias("PARTY_SELF", "PS"),
            RmTypeAlias.alias("REFERENCE_RANGE", "RR"),
            RmTypeAlias.alias("TEMPLATE_ID", "TP"),
            RmTypeAlias.alias("TERMINOLOGY_ID", "T"),
            RmTypeAlias.alias("TERM_MAPPING", "TM"),
            RmTypeAlias.alias("UUID", "U"),
        ]

    @staticmethod
    def structure_alias(s_type: str) -> 'RmTypeAlias':
        return RmTypeAlias(s_type, s_type, True)

    @staticmethod
    def alias(type_: str, alias: str) -> 'RmTypeAlias':
        return RmTypeAlias(type_, alias, False)

    type2alias: Dict[str, str] = {value.type: value.alias for value in values()}
    alias2type: Dict[str, str] = {value.alias: value.type for value in values()}

    @staticmethod
    def get_alias(type_: str) -> str:
        alias = RmTypeAlias.type2alias.get(type_)
        if alias is None:
            raise ValueError(f"Missing alias for type {type_}")
        return alias

    @staticmethod
    def optional_alias(type_: str) -> Optional[str]:
        return RmTypeAlias.type2alias.get(type_)

    @staticmethod
    def get_rm_type(alias: str) -> str:
        type_ = RmTypeAlias.alias2type.get(alias)
        if type_ is None:
            raise ValueError(f"Missing type for alias {alias}")
        return type_
