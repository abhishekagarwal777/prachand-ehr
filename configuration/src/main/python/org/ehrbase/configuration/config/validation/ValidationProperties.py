from typing import Dict
from pydantic import BaseModel, Field

class ValidationProperties(BaseModel):
    enabled: bool = False
    authenticate: bool = False
    fail_on_error: bool = False
    provider: Dict[str, 'Provider'] = {}

    class Provider(BaseModel):
        oauth2_client: str = Field(None, alias='oauth2Client')
        type: 'ProviderType'
        url: str

    class ProviderType(str):
        FHIR = 'FHIR'
