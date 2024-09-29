from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class IsoDateTimeConverter(BaseModel):
    date_time: Optional[datetime]

    @validator('date_time', pre=True, always=True)
    def parse_iso_date_time(cls, value):
        if not value:
            return None
        return datetime.fromisoformat(value.replace('Z', '+00:00'))

# Example usage
def convert_iso_date_time(iso_string: str) -> Optional[datetime]:
    try:
        return IsoDateTimeConverter(date_time=iso_string).date_time
    except ValueError:
        return None

# Example usage
iso_string = "2024-09-19T12:34:56Z"
converted_date_time = convert_iso_date_time(iso_string)
print(converted_date_time)
