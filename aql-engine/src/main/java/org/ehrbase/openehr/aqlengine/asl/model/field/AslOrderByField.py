from dataclasses import dataclass
from enum import Enum
from typing import Type

class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass(frozen=True)
class AslOrderByField:
    field: 'AslField'
    direction: SortOrder


# Example usage
field = AslField(...)  # Replace with actual AslField instance
order_by_field = AslOrderByField(field=field, direction=SortOrder.ASC)

print(order_by_field)
