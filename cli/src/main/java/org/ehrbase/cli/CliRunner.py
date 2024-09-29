import sys
from typing import Callable, List, Optional
from functools import reduce

class CliRunner:

    CLI = "cli"

    def __init__(self, commands: List['CliCommand'], help_command: 'CliHelpCommand'):
        self.help_command = help_command
        self.commands = sorted(commands, key=lambda cmd: cmd.get_name())

    def run(self, *args: str) -> None:
        self.run_with_handler(lambda t, t2: 
                              raise ValueError(f"Duplicate command for name {t.get_name()} (attempted merging values {t} and {t2})"),
                              *args)

    def run_with_handler(self, on_duplicated_cmd: Callable[['CliCommand', 'CliCommand'], None], *args: str) -> None:
        arg_list = list(args)
        arg_iter = iter(arg_list)
        command_name = self.extract_cmd(arg_iter)

        named_commands = {cmd.get_name(): cmd for cmd in self.commands}

        if command_name:
            command = named_commands.get(command_name)
            if command:
                self.run_command(command, list(arg_iter))
            else:
                self.help_command.exit_fail(f"Unknown command {command_name}")
        else:
            self.help_command.exit_fail("No command specified")

    def extract_cmd(self, arg_iter: iter) -> Optional[str]:
        for next in arg_iter:
            if next == self.CLI:
                break

        try:
            return next(arg_iter)
        except StopIteration:
            return None

    def run_command(self, command: 'CliCommand', args: List[str]) -> None:
        try:
            command.run(args)
        except Exception as e:
            logger.error(f"Failed to execute [{command.get_name()}]", exc_info=e)
            self.help_command.exit_fail(str(e))
