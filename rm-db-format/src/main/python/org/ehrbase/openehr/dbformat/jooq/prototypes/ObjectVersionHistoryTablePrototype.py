from uuid import UUID
from datetime import datetime
from jooq import TableField, Name, Table
from jooq.impl import DSL

class ObjectVersionHistoryTablePrototype(AbstractTablePrototype):
    """
    This class represents the ObjectVersionHistoryTablePrototype,
    extending the AbstractTablePrototype. It defines the structure
    for version history tables with associated fields.
    """

    serial_version_uid = 1  # Equivalent to the Java serialVersionUID

    # Singleton instance of the table prototype
    INSTANCE = None

    def __init__(self):
        if ObjectVersionHistoryTablePrototype.INSTANCE is None:
            ObjectVersionHistoryTablePrototype.INSTANCE = self
            # Create fields in correct order
            for field in ObjectVersionHistoryRecordPrototype.COLUMNS.keys():
                self.create_field(field)

        # Define table fields
        self.VO_ID = self.get_field(FieldPrototype.VO_ID)
        self.EHR_ID = self.get_field(FieldPrototype.EHR_ID)
        self.CONTRIBUTION_ID = self.get_field(FieldPrototype.CONTRIBUTION_ID)
        self.AUDIT_ID = self.get_field(FieldPrototype.AUDIT_ID)
        self.SYS_VERSION = self.get_field(FieldPrototype.SYS_VERSION)
        self.SYS_PERIOD_LOWER = self.get_field(FieldPrototype.SYS_PERIOD_LOWER)
        self.SYS_PERIOD_UPPER = self.get_field(FieldPrototype.SYS_PERIOD_UPPER)
        self.SYS_DELETED = self.get_field(FieldPrototype.SYS_DELETED)

    def __init__(self, alias: Name = None, aliased: Table = None):
        super().__init__(alias, aliased)

    def instance(self, alias: Name, aliased: 'ObjectVersionHistoryTablePrototype') -> 'ObjectVersionHistoryTablePrototype':
        return ObjectVersionHistoryTablePrototype(alias, aliased)

    def get_record_type(self) -> type:
        return ObjectVersionHistoryRecordPrototype

# Instantiate the prototype
ObjectVersionHistoryTablePrototype()
