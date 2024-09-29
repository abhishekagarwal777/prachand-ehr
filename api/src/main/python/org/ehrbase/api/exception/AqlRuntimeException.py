class AqlRuntimeException(RuntimeError):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause is not None:
            message = message or str(cause)
        super().__init__(message)
        self.__cause__ = cause


def some_aql_function():
    raise AqlRuntimeException("An error occurred", cause=Exception("Root cause"))

try:
    some_aql_function()
except AqlRuntimeException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
