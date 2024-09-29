from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import uuid

class ItemTagRMType(Enum):
    EHR_STATUS = "EHR_STATUS"
    COMPOSITION = "COMPOSITION"

@dataclass
class ItemTagDto:
    id: Optional[uuid.UUID] = field(default=None)
    owner_id: Optional[uuid.UUID] = field(default=None)
    target: Optional[uuid.UUID] = field(default=None)
    target_type: Optional[ItemTagRMType] = field(default=None)
    target_path: Optional[str] = field(default=None)
    key: str = field(default="")
    value: Optional[str] = field(default=None)

    def __post_init__(self):
        if not self.key or self.key.isspace():
            raise ValueError("Key cannot be empty or contain only whitespace.")


import uuid

item_tag = ItemTagDto(
    id=uuid.uuid4(),
    owner_id=uuid.uuid4(),
    target=uuid.uuid4(),
    target_type=ItemTagRMType.EHR_STATUS,
    target_path="/ehr/composition",
    key="exampleKey",
    value="exampleValue"
)

print(item_tag)
