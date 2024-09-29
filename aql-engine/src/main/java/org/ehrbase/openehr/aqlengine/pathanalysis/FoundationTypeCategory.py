from enum import Enum, auto

class FoundationTypeCategory(Enum):
    ANY = auto()
    BOOLEAN = auto()
    BYTEA = auto()
    NUMERIC = auto()
    TEXT = auto()

# Example usage:
category = FoundationTypeCategory.BOOLEAN
print(f'The category is {category.name}')
