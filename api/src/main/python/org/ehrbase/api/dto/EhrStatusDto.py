from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class UIDBasedId(BaseModel):
    value: UUID

class DvText(BaseModel):
    value: str

class Archetyped(BaseModel):
    # Define fields for Archetyped based on its Java counterpart
    pass

class FeederAudit(BaseModel):
    # Define fields for FeederAudit based on its Java counterpart
    pass

class PartySelf(BaseModel):
    # Define fields for PartySelf based on its Java counterpart
    pass

class ItemStructure(BaseModel):
    # Define fields for ItemStructure based on its Java counterpart
    pass

class EhrStatusDto(BaseModel):
    uid: UIDBasedId
    archetype_node_id: str = Field(..., alias='archetype_node_id')
    name: DvText
    archetype_details: Optional[Archetyped] = Field(None, alias='archetype_details')
    feeder_audit: Optional[FeederAudit] = Field(None, alias='feeder_audit')
    subject: PartySelf
    is_queryable: Optional[bool] = Field(None, alias='is_queryable')
    is_modifiable: Optional[bool] = Field(None, alias='is_modifiable')
    other_details: Optional[ItemStructure] = Field(None, alias='other_details')

    @property
    def type(self) -> str:
        return "EHR_STATUS"

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {
            UUID: str,  # Custom serialization for UUID if needed
        }


from uuid import uuid4

# Example instantiation
ehr_status_dto = EhrStatusDto(
    uid=UIDBasedId(value=uuid4()),
    archetype_node_id="some_id",
    name=DvText(value="EHR Status Name"),
    subject=PartySelf(),
    is_queryable=True,
    is_modifiable=False
)

print(ehr_status_dto.json())
