from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class OPERATIONALTEMPLATE:
    # Placeholder for the OPERATIONALTEMPLATE class
    pass

@dataclass
class TemplateMetaData:
    operationaltemplate: Optional[OPERATIONALTEMPLATE] = None
    created_on: Optional[datetime] = None
    internal_id: Optional[UUID] = None
    error_list: List[str] = field(default_factory=list)

    def add_error(self, error: str):
        """Adds an error message to the list of errors."""
        self.error_list.append(error)


