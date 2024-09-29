class InternalServerException(RuntimeError):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause is not None:
            message = message or str(cause)
        super().__init__(message)
        self.__cause__ = cause

def process_request():
    try:
        # Simulating an internal error
        raise ValueError("An unexpected error occurred")
    except ValueError as e:
        raise InternalServerException("Internal server error occurred", cause=e)

try:
    process_request()
except InternalServerException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
