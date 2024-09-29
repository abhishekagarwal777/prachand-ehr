from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class HierObjectId(BaseModel):
    value: UUID

class EhrStatusDto(BaseModel):
    # Define fields for EhrStatusDto based on its Java counterpart
    pass

class CompositionDto(BaseModel):
    # Define fields for CompositionDto based on its Java counterpart
    pass

class ContributionDto(BaseModel):
    # Define fields for ContributionDto based on its Java counterpart
    pass

class EhrDto(BaseModel):
    system_id: HierObjectId = Field(..., alias='system_id')
    ehr_id: HierObjectId = Field(..., alias='ehr_id')
    ehr_status: EhrStatusDto = Field(..., alias='ehr_status')
    time_created: datetime = Field(..., alias='time_created')
    compositions: List[CompositionDto] = Field(..., alias='compositions')
    contributions: List[ContributionDto] = Field(..., alias='contributions')

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {
            # Customize JSON serialization for specific types if needed
        }


from uuid import uuid4
from datetime import datetime

# Example instantiation
ehr_dto = EhrDto(
    system_id=HierObjectId(value=uuid4()),
    ehr_id=HierObjectId(value=uuid4()),
    ehr_status=EhrStatusDto(),
    time_created=datetime.now(),
    compositions=[CompositionDto()],
    contributions=[ContributionDto()]
)

print(ehr_dto.json())
