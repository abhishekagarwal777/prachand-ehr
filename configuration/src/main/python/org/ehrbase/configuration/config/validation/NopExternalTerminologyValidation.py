from typing import List, Optional
from pydantic import BaseModel
from pydantic.error_wrappers import ErrorWrapper
from functools import partial

class ConstraintViolation(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ConstraintViolationException(Exception):
    def __init__(self, violations: List[ConstraintViolation]):
        super().__init__("Constraint Violation(s)")
        self.violations = violations

class TerminologyParam(BaseModel):
    # Define fields as needed
    pass

class DvCodedText(BaseModel):
    # Define fields as needed
    pass

class NopExternalTerminologyValidation:
    def __init__(self, error_message: str):
        self.err = ConstraintViolation(error_message)

    def validate(self, param: TerminologyParam) -> 'Try[bool, ConstraintViolationException]':
        return Try.failure(ConstraintViolationException([self.err]))

    def supports(self, param: TerminologyParam) -> bool:
        return False

    def expand(self, param: TerminologyParam) -> List[DvCodedText]:
        return []

class Try:
    @staticmethod
    def failure(exception: Exception):
        return {'status': 'failure', 'exception': exception}

    @staticmethod
    def success(value):
        return {'status': 'success', 'value': value}
