from uuid import UUID
from datetime import datetime
from jooq import Name, Table, TableField, DSL

class ObjectVersionTablePrototype(AbstractTablePrototype):
    """
    The ObjectVersionTablePrototype class represents the table structure for object versions.
    It is a singleton and provides access to the table fields.
    """

    serial_version_uid = 1  # Equivalent to the Java serialVersionUID
    INSTANCE = None

    def __new__(cls):
        """Implement singleton pattern to ensure a single instance."""
        if cls.INSTANCE is None:
            cls.INSTANCE = super(ObjectVersionTablePrototype, cls).__new__(cls)
            cls.INSTANCE.__init_fields()  # Initialize fields on first creation
        return cls.INSTANCE

    def __init_fields(self):
        """Create fields in correct order."""
        for field in ObjectVersionRecordPrototype.COLUMNS.keys():
            self.create_field(field)

    def __init__(self):
        """Private constructor for the singleton instance."""
        super().__init__(DSL.name("object_version_prototype"), None)

    def __init__(self, alias: Name, aliased: Table) -> None:
        """Private constructor for creating an aliased instance."""
        super().__init__(alias, aliased)

    # Define table fields
    VO_ID: TableField = get_field(FieldPrototype.VO_ID)
    EHR_ID: TableField = get_field(FieldPrototype.EHR_ID)
    CONTRIBUTION_ID: TableField = get_field(FieldPrototype.CONTRIBUTION_ID)
    AUDIT_ID: TableField = get_field(FieldPrototype.AUDIT_ID)
    SYS_VERSION: TableField = get_field(FieldPrototype.SYS_VERSION)
    SYS_PERIOD_LOWER: TableField = get_field(FieldPrototype.SYS_PERIOD_LOWER)

    def instance(self, alias: Name, aliased: 'ObjectVersionTablePrototype') -> 'ObjectVersionTablePrototype':
        """Create a new instance of ObjectVersionTablePrototype with alias."""
        return ObjectVersionTablePrototype(alias, aliased)

    def get_record_type(self) -> type:
        """Return the record type associated with this table."""
        return ObjectVersionRecordPrototype
