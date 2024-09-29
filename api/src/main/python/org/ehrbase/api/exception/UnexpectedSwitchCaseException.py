class UnexpectedSwitchCaseException(RuntimeError):
    def __init__(self, value, additional_message=None):
        if isinstance(value, Enum):
            message = self._format_message(value.__class__.__name__, value.name, additional_message)
        elif isinstance(value, int):
            message = self._format_message(value, additional_message)
        elif isinstance(value, str):
            message = self._format_message(value, additional_message)
        else:
            message = self._format_message(type(value).__name__, value, additional_message)
        super().__init__(message)

    @staticmethod
    def _format_message(type, value, additional_message):
        message = f"Unexpected value of {type}: '{value}'"
        if additional_message:
            message += f"; {additional_message}"
        return message


from enum import Enum

class MyEnum(Enum):
    CASE1 = 1
    CASE2 = 2

try:
    raise UnexpectedSwitchCaseException(MyEnum.CASE1, "Additional context here.")
except UnexpectedSwitchCaseException as e:
    print(f"Exception: {e}")
