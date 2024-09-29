class InvalidApiParameterException(RuntimeError):
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.__cause__ = cause

def validate_parameters(params):
    if not isinstance(params, dict):
        raise InvalidApiParameterException("Parameters must be a dictionary")

try:
    validate_parameters("invalid_params")
except InvalidApiParameterException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
