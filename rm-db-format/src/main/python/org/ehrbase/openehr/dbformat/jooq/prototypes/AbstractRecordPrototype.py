from enum import Enum
from typing import Any, Dict, List, TypeVar, Union


P = TypeVar('P', bound='AbstractRecordPrototype')


class FieldPrototype(Enum):
    # Define the actual values based on your application needs
    # Example fields
    FIELD_ONE = 1
    FIELD_TWO = 2

    def is_available(self, version: bool, head: bool) -> bool:
        # Implement availability logic based on version and head
        # Placeholder implementation
        return True


class UpdatableRecordImpl:
    def __init__(self, table: 'Table', *values: Any):
        self.table = table
        self.values = list(values)
        self.changed = [False] * len(values)

    def set(self, index: int, value: Any):
        if index < len(self.values):
            self.values[index] = value
            self.changed[index] = True

    def get(self, index: int) -> Any:
        return self.values[index]

    def reset_changed_on_not_null(self):
        for i in range(len(self.values)):
            if self.values[i] is not None:
                self.changed[i] = False


class Table:
    # Placeholder for Table class as per jOOQ's Table implementation
    pass


class AbstractRecordPrototype(UpdatableRecordImpl[P]):
    def __init__(self, table: Table, *values: Any):
        super().__init__(table, *values)
        for i, value in enumerate(values):
            self.set(i, value)
        self.reset_changed_on_not_null()

    def set(self, f: FieldPrototype, value: Any):
        super().set(self.column_index(f), value)

    def get(self, f: FieldPrototype) -> Any:
        return super().get(self.column_index(f))

    def column_index(self, f: FieldPrototype) -> int:
        raise NotImplementedError("Subclasses must implement this method")

    @staticmethod
    def determine_columns(version: bool, head: bool) -> Dict[FieldPrototype, int]:
        columns = {}
        pos = 0
        for f in FieldPrototype:
            if f.is_available(version, head):
                columns[f] = pos
                pos += 1
        return columns
