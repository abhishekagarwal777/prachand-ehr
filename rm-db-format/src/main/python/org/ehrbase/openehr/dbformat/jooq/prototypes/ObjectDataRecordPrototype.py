from enum import Enum
from typing import Dict, Any
from uuid import UUID
from jooq import JSONB, Record3

class FieldPrototype(Enum):
    VO_ID = 1
    NUM = 2
    CITEM_NUM = 3
    PARENT_NUM = 4
    NUM_CAP = 5
    RM_ENTITY = 6
    ENTITY_CONCEPT = 7
    ENTITY_NAME = 8
    ENTITY_ATTRIBUTE = 9
    ENTITY_IDX = 10
    ENTITY_IDX_LEN = 11
    DATA = 12

class ObjectDataRecordPrototype(AbstractRecordPrototype):
    """
    This class represents the ObjectDataRecordPrototype, extending the AbstractRecordPrototype.
    It manages data and field definitions for the object data history.
    """

    COLUMNS: Dict[FieldPrototype, int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(ObjectDataTablePrototype.INSTANCE)
        self.COLUMNS = self.determine_columns(False, True)
    
    def set_vo_id(self, value: UUID) -> None:
        self.set(FieldPrototype.VO_ID, value)

    def get_vo_id(self) -> UUID:
        return self.get(FieldPrototype.VO_ID)

    def set_num(self, value: int) -> None:
        self.set(FieldPrototype.NUM, value)

    def get_num(self) -> int:
        return self.get(FieldPrototype.NUM)

    def set_citem_num(self, value: int) -> None:
        self.set(FieldPrototype.CITEM_NUM, value)

    def get_citem_num(self) -> int:
        return self.get(FieldPrototype.CITEM_NUM)

    def set_parent_num(self, value: int) -> None:
        self.set(FieldPrototype.PARENT_NUM, value)

    def get_parent_num(self) -> int:
        return self.get(FieldPrototype.PARENT_NUM)

    def set_num_cap(self, value: int) -> None:
        self.set(FieldPrototype.NUM_CAP, value)

    def get_num_cap(self) -> int:
        return self.get(FieldPrototype.NUM_CAP)

    def set_rm_entity(self, value: str) -> None:
        self.set(FieldPrototype.RM_ENTITY, value)

    def get_rm_entity(self) -> str:
        return self.get(FieldPrototype.RM_ENTITY)

    def set_entity_concept(self, value: str) -> None:
        self.set(FieldPrototype.ENTITY_CONCEPT, value)

    def get_entity_concept(self) -> str:
        return self.get(FieldPrototype.ENTITY_CONCEPT)

    def set_entity_name(self, value: str) -> None:
        self.set(FieldPrototype.ENTITY_NAME, value)

    def get_entity_name(self) -> str:
        return self.get(FieldPrototype.ENTITY_NAME)

    def set_entity_attribute(self, value: str) -> None:
        self.set(FieldPrototype.ENTITY_ATTRIBUTE, value)

    def get_entity_attribute(self) -> str:
        return self.get(FieldPrototype.ENTITY_ATTRIBUTE)

    def set_entity_idx(self, value: str) -> None:
        self.set(FieldPrototype.ENTITY_IDX, value)

    def get_entity_idx(self) -> str:
        return self.get(FieldPrototype.ENTITY_IDX)

    def set_entity_idx_len(self, value: int) -> None:
        self.set(FieldPrototype.ENTITY_IDX_LEN, value)

    def get_entity_idx_len(self) -> int:
        return self.get(FieldPrototype.ENTITY_IDX_LEN)

    def set_data(self, value: JSONB) -> None:
        self.set(FieldPrototype.DATA, value)

    def get_data(self) -> JSONB:
        return self.get(FieldPrototype.DATA)

    # Primary key information
    def key(self) -> Record3[UUID, int, int]:
        return super().key()

    # Constructor
    def __init__(
        self,
        vo_id: UUID = None,
        num: int = None,
        citem_num: int = None,
        rm_entity: str = None,
        entity_concept: str = None,
        entity_name: str = None,
        entity_attribute: str = None,
        entity_idx: str = None,
        entity_idx_len: int = None,
        data: JSONB = None,
    ):
        super().__init__(
            ObjectDataTablePrototype.INSTANCE,
            vo_id,
            num,
            citem_num,
            rm_entity,
            entity_concept,
            entity_name,
            entity_attribute,
            entity_idx,
            entity_idx_len,
            data,
        )

    # Method to get column index
    def column_index(self, f: FieldPrototype) -> int:
        return self.COLUMNS[f]
