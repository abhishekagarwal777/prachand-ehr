class BadGatewayException(RuntimeError):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause is not None:
            message = message or str(cause)
        super().__init__(message)
        self.__cause__ = cause


def some_service_call():
    raise BadGatewayException("Failed to connect to the backend service", cause=Exception("Connection timeout"))

try:
    some_service_call()
except BadGatewayException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
