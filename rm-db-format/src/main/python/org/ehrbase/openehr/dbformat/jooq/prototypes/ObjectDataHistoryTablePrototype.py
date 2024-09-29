from jooq import DSL, TableField, Name, JSONB

class ObjectDataHistoryTablePrototype(AbstractTablePrototype):
    """
    This class represents the ObjectDataHistoryTablePrototype, extending the AbstractTablePrototype.
    It contains the table definition and fields for the Object Data History.
    """

    # Singleton instance
    INSTANCE = None

    # Table fields
    VO_ID: TableField = None
    NUM: TableField = None
    CITEM_NUM: TableField = None
    PARENT_NUM: TableField = None
    NUM_CAP: TableField = None
    RM_ENTITY: TableField = None
    ENTITY_CONCEPT: TableField = None
    ENTITY_NAME: TableField = None
    ENTITY_ATTRIBUTE: TableField = None
    ENTITY_IDX: TableField = None
    ENTITY_IDX_LEN: TableField = None
    DATA: TableField = None
    SYS_VERSION: TableField = None

    def __init__(self):
        if ObjectDataHistoryTablePrototype.INSTANCE is None:
            ObjectDataHistoryTablePrototype.INSTANCE = self
        else:
            raise Exception("This class is a singleton!")

        # Create fields in correct order
        for field in ObjectDataHistoryRecordPrototype.COLUMNS.keys():
            self.create_field(field)

        self.VO_ID = self.get_field(FieldPrototype.VO_ID)
        self.NUM = self.get_field(FieldPrototype.NUM)
        self.CITEM_NUM = self.get_field(FieldPrototype.CITEM_NUM)
        self.PARENT_NUM = self.get_field(FieldPrototype.PARENT_NUM)
        self.NUM_CAP = self.get_field(FieldPrototype.NUM_CAP)
        self.RM_ENTITY = self.get_field(FieldPrototype.RM_ENTITY)
        self.ENTITY_CONCEPT = self.get_field(FieldPrototype.ENTITY_CONCEPT)
        self.ENTITY_NAME = self.get_field(FieldPrototype.ENTITY_NAME)
        self.ENTITY_ATTRIBUTE = self.get_field(FieldPrototype.ENTITY_ATTRIBUTE)
        self.ENTITY_IDX = self.get_field(FieldPrototype.ENTITY_IDX)
        self.ENTITY_IDX_LEN = self.get_field(FieldPrototype.ENTITY_IDX_LEN)
        self.DATA = self.get_field(FieldPrototype.DATA)
        self.SYS_VERSION = self.get_field(FieldPrototype.SYS_VERSION)

    def __init__(self, alias: Name = None, aliased: 'Table' = None):
        super().__init__(alias or DSL.name("object_data_history_prototype"), aliased)

    def instance(self, alias: Name, aliased: 'ObjectDataHistoryTablePrototype') -> 'ObjectDataHistoryTablePrototype':
        return ObjectDataHistoryTablePrototype(alias, aliased)

    def get_record_type(self) -> type:
        return ObjectDataHistoryRecordPrototype
