import sys
from typing import Callable, List, Optional, Union

class CliArgument:
    def __init__(self, arg: str, key: str, value: Optional[str]):
        self.arg = arg
        self.key = key
        self.value = value

class Result:
    OK = "OK"
    UNKNOWN = "UNKNOWN"

class CliCommand:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def run(self, args: List[str]) -> None:
        raise NotImplementedError("Subclasses should implement this method")

    def println(self, line: str) -> None:
        print(line)

    def print_step(self, line: str) -> None:
        self.println("---------------------------------------------------------------------------")
        self.println(line)
        self.println("---------------------------------------------------------------------------")

    def exit_fail(self, reason: str) -> None:
        print(reason, file=sys.stderr)
        self.print_usage()
        self.exit(-1)

    def exit(self, code: int) -> None:
        sys.exit(code)

    def print_usage(self) -> None:
        raise NotImplementedError("Subclasses should implement this method")

    def consume_args(self, args: List[str], consumer: Callable[[CliArgument], str]) -> None:
        if not args:
            self.exit_fail("No argument provided")
            return

        for next_arg in args:
            if next_arg == "help":
                self.print_usage()
                return

            split = next_arg.split("=", 1)
            key = split[0].lstrip("--")
            value = split[1] if len(split) > 1 else None
            arg = CliArgument(next_arg, key, value)

            result = consumer(arg)
            if result == Result.UNKNOWN:
                self.exit_fail(f"Unknown argument [{arg.arg}]")

# Example subclass implementation
class MyCliCommand(CliCommand):
    def run(self, args: List[str]) -> None:
        # Implement the command execution logic here
        pass

    def print_usage(self) -> None:
        self.println("Usage: [options]")
