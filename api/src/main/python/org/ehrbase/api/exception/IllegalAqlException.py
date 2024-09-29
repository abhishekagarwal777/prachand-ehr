class IllegalAqlException(RuntimeError):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause is not None:
            message = message or str(cause)
        super().__init__(message)
        self.__cause__ = cause

def process_aql_query(query):
    if not is_valid_aql(query):
        raise IllegalAqlException("Invalid AQL query", cause=Exception("Syntax error"))

try:
    process_aql_query("invalid query")
except IllegalAqlException as e:
    print(f"Exception: {e}, Cause: {e.__cause__}")
