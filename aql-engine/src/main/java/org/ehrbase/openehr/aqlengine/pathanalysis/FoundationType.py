from enum import Enum, auto
from typing import Optional

class FoundationTypeCategory(Enum):
    BOOLEAN = auto()
    BYTEA = auto()
    NUMERIC = auto()
    TEXT = auto()
    ANY = auto()

class FoundationType(Enum):
    BOOLEAN = FoundationTypeCategory.BOOLEAN
    BYTE = FoundationTypeCategory.BYTEA
    DOUBLE = FoundationTypeCategory.NUMERIC
    INTEGER = FoundationTypeCategory.NUMERIC
    LONG = FoundationTypeCategory.NUMERIC
    STRING = FoundationTypeCategory.TEXT
    URI = FoundationTypeCategory.TEXT
    TEMPORAL = FoundationTypeCategory.TEXT
    TEMPORAL_ACCESSOR = FoundationTypeCategory.TEXT
    TEMPORAL_AMOUNT = FoundationTypeCategory.TEXT
    CHAR = FoundationTypeCategory.TEXT
    OBJECT = FoundationTypeCategory.ANY

    _BY_TYPE_NAME = {ft.name: ft for ft in list(FoundationType)}

    def __init__(self, category: FoundationTypeCategory):
        self.category = category

    @staticmethod
    def by_type_name(type_name: str) -> Optional['FoundationType']:
        return FoundationType._BY_TYPE_NAME.get(type_name)

# Example usage:
type_name = 'STRING'
foundation_type = FoundationType.by_type_name(type_name)
if foundation_type:
    print(f'Category of {type_name}: {foundation_type.category.name}')
else:
    print(f'{type_name} not found')
