from abc import ABC, abstractmethod
from typing import Optional
import uuid

class ContributionDto:
    # Placeholder for the ContributionDto class definition.
    pass

class AuditDetails:
    # Placeholder for the AuditDetails class definition.
    def get_change_type(self):
        pass

class DvCodedText:
    # Placeholder for the DvCodedText class definition.
    def get_defining_code(self):
        pass

class ContributionService(ABC):
    
    class ContributionChangeType:
        CREATION = 249
        AMENDMENT = 250
        MODIFICATION = 251
        SYNTHESIS = 252
        UNKNOWN = 253
        DELETED = 523
        
        _codes = {
            CREATION: "CREATION",
            AMENDMENT: "AMENDMENT",
            MODIFICATION: "MODIFICATION",
            SYNTHESIS: "SYNTHESIS",
            UNKNOWN: "UNKNOWN",
            DELETED: "DELETED"
        }
        
        @staticmethod
        def from_audit_details(commit_audit: AuditDetails) -> str:
            change_type = commit_audit.get_change_type()
            if change_type.get_defining_code().get_terminology_id() != "openehr":
                raise ValidationException(f"Unsupported change type terminology: {change_type.get_defining_code().get_terminology_id()}")
            
            code_string = change_type.get_defining_code().get_code_string()
            try:
                code = int(code_string)
            except ValueError:
                raise ValidationException(f"Unknown change type code {code_string}")
            
            if code in ContributionService.ContributionChangeType._codes:
                if ContributionService.ContributionChangeType._codes[code] == change_type.get_value():
                    return ContributionService.ContributionChangeType._codes[code]
                else:
                    raise ValidationException(f"Inconsistent change type: {change_type.get_value()} for code {code_string}")
            else:
                raise ValidationException(f"Unknown change type code {code_string}")

    @abstractmethod
    def get_contribution(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> ContributionDto:
        """
        Return the Contribution with given id in given EHR.
        """
        pass

    @abstractmethod
    def commit_contribution(self, ehr_id: uuid.UUID, content: str) -> uuid.UUID:
        """
        Commit a CONTRIBUTION containing serialized VERSION<Type> objects.
        """
        pass

    @abstractmethod
    def admin_delete(self, ehr_id: uuid.UUID, contribution_id: uuid.UUID) -> None:
        """
        Admin method to delete a Contribution from the DB.
        """
        pass

class ValidationException(Exception):
    pass
