class NotAcceptableException(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)

def check_acceptable(value):
    if value not in acceptable_values:
        raise NotAcceptableException("The value is not acceptable")

acceptable_values = [1, 2, 3]

try:
    check_acceptable(4)
except NotAcceptableException as e:
    print(f"Exception: {e}")
