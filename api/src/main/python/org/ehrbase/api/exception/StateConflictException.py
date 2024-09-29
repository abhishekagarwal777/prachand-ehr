class StateConflictException(RuntimeError):
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self._cause = cause

    @property
    def cause(self):
        return self._cause

try:
    raise StateConflictException("Conflict with current state")
except StateConflictException as e:
    print(f"Exception: {e}, Cause: {e.cause}")
