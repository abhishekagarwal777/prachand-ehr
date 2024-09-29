from collections import defaultdict
import uuid
from jooq import JSONB, Record4
from sqlalchemy.dialects.postgresql import JSONB


class ObjectDataHistoryRecordPrototype(AbstractRecordPrototype):
    """
    This class represents the ObjectDataHistoryRecordPrototype, extending the AbstractRecordPrototype.
    """

    # Static variables
    COLUMNS = defaultdict(int)

    @staticmethod
    def determine_columns():
        # Logic to determine columns based on specific requirements (similar to the Java method)
        return {field: index for index, field in enumerate(FieldPrototype)}

    # Initialize COLUMNS
    COLUMNS.update(determine_columns())

    def set_vo_id(self, value: uuid.UUID):
        self.set(FieldPrototype.VO_ID, value)

    def get_vo_id(self) -> uuid.UUID:
        return self.get(FieldPrototype.VO_ID)

    def set_num(self, value: int):
        self.set(FieldPrototype.NUM, value)

    def get_num(self) -> int:
        return self.get(FieldPrototype.NUM)

    def set_citem_num(self, value: int):
        self.set(FieldPrototype.CITEM_NUM, value)

    def get_citem_num(self) -> int:
        return self.get(FieldPrototype.CITEM_NUM)

    def set_parent_num(self, value: int):
        self.set(FieldPrototype.PARENT_NUM, value)

    def get_parent_num(self) -> int:
        return self.get(FieldPrototype.PARENT_NUM)

    def set_num_cap(self, value: int):
        self.set(FieldPrototype.NUM_CAP, value)

    def get_num_cap(self) -> int:
        return self.get(FieldPrototype.NUM_CAP)

    def set_rm_entity(self, value: str):
        self.set(FieldPrototype.RM_ENTITY, value)

    def get_rm_entity(self) -> str:
        return self.get(FieldPrototype.RM_ENTITY)

    def set_entity_concept(self, value: str):
        self.set(FieldPrototype.ENTITY_CONCEPT, value)

    def get_entity_concept(self) -> str:
        return self.get(FieldPrototype.ENTITY_CONCEPT)

    def set_entity_name(self, value: str):
        self.set(FieldPrototype.ENTITY_NAME, value)

    def get_entity_name(self) -> str:
        return self.get(FieldPrototype.ENTITY_NAME)

    def set_entity_attribute(self, value: str):
        self.set(FieldPrototype.ENTITY_ATTRIBUTE, value)

    def get_entity_attribute(self) -> str:
        return self.get(FieldPrototype.ENTITY_ATTRIBUTE)

    def set_entity_idx(self, value: str):
        self.set(FieldPrototype.ENTITY_IDX, value)

    def get_entity_idx(self) -> str:
        return self.get(FieldPrototype.ENTITY_IDX)

    def set_entity_idx_len(self, value: int):
        self.set(FieldPrototype.ENTITY_IDX_LEN, value)

    def get_entity_idx_len(self) -> int:
        return self.get(FieldPrototype.ENTITY_IDX_LEN)

    def set_data(self, value: JSONB):
        self.set(FieldPrototype.DATA, value)

    def get_data(self) -> JSONB:
        return self.get(FieldPrototype.DATA)

    def set_sys_version(self, value: int):
        self.set(FieldPrototype.SYS_VERSION, value)

    def get_sys_version(self) -> int:
        return self.get(FieldPrototype.SYS_VERSION)

    # -------------------------------------------------------------------------
    # Primary key information
    # -------------------------------------------------------------------------

    def key(self) -> Record4:
        return super().key()

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    def __init__(self, vo_id=None, num=None, citem_num=None, rm_entity=None,
                 entity_concept=None, entity_name=None, entity_attribute=None,
                 entity_idx=None, entity_idx_len=None, data=None, sys_version=None):
        super().__init__(ObjectDataHistoryTablePrototype.INSTANCE)

        if all(arg is not None for arg in [vo_id, num, citem_num, rm_entity,
                                            entity_concept, entity_name,
                                            entity_attribute, entity_idx,
                                            entity_idx_len, data, sys_version]):
            super().__init__(
                ObjectDataHistoryTablePrototype.INSTANCE,
                vo_id, num, citem_num, rm_entity,
                entity_concept, entity_name, entity_attribute,
                entity_idx, entity_idx_len, data, sys_version
            )

    def column_index(self, f: FieldPrototype) -> int:
        return self.COLUMNS[f]
