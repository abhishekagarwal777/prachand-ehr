class UnprocessableEntityException(RuntimeError):
    def __init__(self, message, cause=None):
        super().__init__(message)
        self.cause = cause


try:
    raise UnprocessableEntityException("The request contains semantic errors.", "Additional context.")
except UnprocessableEntityException as e:
    print(f"Exception: {e}")
    if e.cause:
        print(f"Cause: {e.cause}")
