from enum import Enum
from jooq import DataType, Name, DSL


class FieldPrototype(Enum):
    # All fields
    VO_ID = ("UUID", False, True, True, True)
    EHR_ID = ("UUID", False, True, False, False)
    CONTRIBUTION_ID = ("UUID", False, True, False, False)
    AUDIT_ID = ("UUID", False, True, False, False)
    SYS_PERIOD_LOWER = ("TIMESTAMPWITHTIMEZONE(6)", False, True, False, False)
    SYS_VERSION = ("INTEGER", False, True, False, True)
    SYS_PERIOD_UPPER = ("TIMESTAMPWITHTIMEZONE(6)", True, True, False, False)
    SYS_DELETED = ("BOOLEAN", False, True, False, False)

    # DATA
    NUM = ("INTEGER", False, False, True, True)
    NUM_CAP = ("INTEGER", False, False, True, True)
    PARENT_NUM = ("INTEGER", False, False, True, True)
    CITEM_NUM = ("INTEGER", True, False, True, True)
    RM_ENTITY = ("CLOB", False, False, True, True)
    ENTITY_CONCEPT = ("CLOB", True, False, True, True)
    ENTITY_NAME = ("CLOB", True, False, True, True)
    ENTITY_ATTRIBUTE = ("CLOB", True, False, True, True)
    ENTITY_IDX = ("CLOB", False, True, True, True)
    ENTITY_IDX_LEN = ("INTEGER", False, True, True, True)
    DATA = ("JSONB", False, True, True, True)

    def __init__(self, data_type: str, version_head: bool, version_history: bool, data_head: bool, data_history: bool):
        self.available_in = [[version_head, version_history], [data_head, data_history]]
        self.field_name = DSL.name(self.name.lower())
        self.type = self._get_data_type(data_type)

    def _get_data_type(self, data_type: str) -> DataType:
        # Logic to convert string type to actual DataType object
        if data_type == "UUID":
            return DataType.UUID.nullable(False)
        elif data_type == "INTEGER":
            return DataType.INTEGER.nullable(False)
        elif data_type == "BOOLEAN":
            return DataType.BOOLEAN.nullable(False)
        elif "TIMESTAMPWITHTIMEZONE" in data_type:
            precision = int(data_type.split("(")[1][:-1])  # Extract precision
            return DataType.TIMESTAMPWITHTIMEZONE(precision).nullable(False)
        elif data_type == "CLOB":
            return DataType.CLOB.nullable(False)
        elif data_type == "JSONB":
            return DataType.JSONB.nullable(False)
        # Add more types as necessary
        raise ValueError(f"Unknown data type: {data_type}")

    def is_available(self, version: bool, head: bool) -> bool:
        return self.available_in[0 if version else 1][0 if head else 1]

    def field_name(self) -> Name:
        return self.field_name

    def type(self) -> DataType:
        return self.type
