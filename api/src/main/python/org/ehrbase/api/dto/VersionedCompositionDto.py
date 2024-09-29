from typing import TypeVar
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

T = TypeVar('T')

class HierObjectId(BaseModel):
    value: UUID

class ObjectId(BaseModel):
    value: UUID

class ObjectRef(BaseModel):
    value: T  # Generic reference to either HierObjectId or ObjectId

class VersionedCompositionDto(BaseModel):
    uid: HierObjectId
    owner_id: ObjectRef[ObjectId] = Field(..., alias='owner_id')
    time_created: str = Field(..., alias='time_created')

    @property
    def type(self) -> str:
        return "VERSIONED_COMPOSITION"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            UUID: str,  # Custom serialization for UUID if needed
        }


from uuid import uuid4

# Example instantiation
versioned_composition_dto = VersionedCompositionDto(
    uid=HierObjectId(value=uuid4()),
    owner_id=ObjectRef(value=ObjectId(value=uuid4())),
    time_created="2024-09-17T12:00:00Z"
)

print(versioned_composition_dto.json())
