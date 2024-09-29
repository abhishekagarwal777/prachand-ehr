from typing import TypeVar
from pydantic import BaseModel, Field
from uuid import UUID

T = TypeVar('T')

class HierObjectId(BaseModel):
    value: UUID

class ObjectId(BaseModel):
    value: UUID

class ObjectRef(BaseModel):
    value: T  # Generic reference to either HierObjectId or ObjectId

class VersionedEhrStatusDto(BaseModel):
    uid: HierObjectId
    owner_id: ObjectRef[ObjectId] = Field(..., alias='owner_id')
    time_created: str = Field(..., alias='time_created')

    @property
    def type(self) -> str:
        return "VERSIONED_EHR_STATUS"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            UUID: str,  # Custom serialization for UUID if needed
        }


from uuid import uuid4

# Example instantiation
versioned_ehr_status_dto = VersionedEhrStatusDto(
    uid=HierObjectId(value=uuid4()),
    owner_id=ObjectRef(value=ObjectId(value=uuid4())),
    time_created="2024-09-17T12:00:00Z"
)

print(versioned_ehr_status_dto.json())
