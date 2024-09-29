from uuid import UUID
from jooq import JSONB, Name, Table, TableField, DSL

class ObjectDataTablePrototype(AbstractTablePrototype):
    """
    This class represents the ObjectDataTablePrototype, extending the AbstractTablePrototype.
    It defines the table structure for object data with associated fields.
    """

    INSTANCE = None
    serial_version_uid = 1  # Equivalent to the Java serialVersionUID

    def __init__(self):
        if ObjectDataTablePrototype.INSTANCE is None:
            ObjectDataTablePrototype.INSTANCE = self
            # Create fields in correct order
            for field in ObjectDataRecordPrototype.COLUMNS.keys():
                self.create_field(field)

        # Define fields
        self.VO_ID = self.get_field(FieldPrototype.VO_ID)
        self.NUM = self.get_field(FieldPrototype.NUM)
        self.PARENT_NUM = self.get_field(FieldPrototype.PARENT_NUM)
        self.NUM_CAP = self.get_field(FieldPrototype.NUM_CAP)
        self.CITEM_NUM = self.get_field(FieldPrototype.CITEM_NUM)
        self.RM_ENTITY = self.get_field(FieldPrototype.RM_ENTITY)
        self.ENTITY_CONCEPT = self.get_field(FieldPrototype.ENTITY_CONCEPT)
        self.ENTITY_NAME = self.get_field(FieldPrototype.ENTITY_NAME)
        self.ENTITY_ATTRIBUTE = self.get_field(FieldPrototype.ENTITY_ATTRIBUTE)
        self.ENTITY_IDX = self.get_field(FieldPrototype.ENTITY_IDX)
        self.ENTITY_IDX_LEN = self.get_field(FieldPrototype.ENTITY_IDX_LEN)
        self.DATA = self.get_field(FieldPrototype.DATA)

    def __init__(self, alias: Name = None, aliased: Table = None):
        super().__init__(alias, aliased)

    @classmethod
    def instance(cls, alias: Name, aliased: 'ObjectDataTablePrototype') -> 'ObjectDataTablePrototype':
        return ObjectDataTablePrototype(alias, aliased)

    def get_record_type(self) -> type:
        return ObjectDataRecordPrototype

# Initialize the INSTANCE variable
ObjectDataTablePrototype.INSTANCE = ObjectDataTablePrototype()
