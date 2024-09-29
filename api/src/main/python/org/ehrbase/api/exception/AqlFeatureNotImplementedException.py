class AqlRuntimeException(Exception):
    """Base class for all AQL runtime exceptions."""
    pass

class AqlFeatureNotImplementedException(AqlRuntimeException):
    def __init__(self, message: str):
        super().__init__(f"Not implemented: {message}")

def some_aql_function():
    raise AqlFeatureNotImplementedException("Feature XYZ")

try:
    some_aql_function()
except AqlFeatureNotImplementedException as e:
    print(e)
