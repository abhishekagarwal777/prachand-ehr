class GeneralRequestProcessingException(RuntimeError):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause is not None:
            message = message or str(cause)
        super().__init__(message)
        self.__cause__ = cause

def process_request(data):
    if not validate_data(data):
        raise GeneralRequestProcessingException("Invalid data provided", cause=Exception("Data validation failed"))

try:
    process_request({"invalid": "data"})
except GeneralRequestProcessingException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
