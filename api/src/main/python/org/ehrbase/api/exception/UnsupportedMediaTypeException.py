class UnsupportedMediaTypeException(RuntimeError):
    def __init__(self, message, cause=None):
        super().__init__(message)
        self.cause = cause


try:
    raise UnsupportedMediaTypeException("The requested media type is not supported.", "Additional context.")
except UnsupportedMediaTypeException as e:
    print(f"Exception: {e}")
    if e.cause:
        print(f"Cause: {e.cause}")
