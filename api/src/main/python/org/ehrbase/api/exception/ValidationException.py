class ValidationException(RuntimeError):
    def __init__(self, message, cause=None):
        super().__init__(message)
        self.cause = cause

try:
    raise ValidationException("Invalid input provided.", "Additional context.")
except ValidationException as e:
    print(f"Exception: {e}")
    if e.cause:
        print(f"Cause: {e.cause}")
