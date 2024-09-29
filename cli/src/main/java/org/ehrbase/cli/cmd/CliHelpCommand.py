from typing import List

class CliHelpCommand(CliCommand):
    def __init__(self):
        super().__init__("help")

    def run(self, args: List[str]) -> None:
        if args:
            self.exit_fail(f"illegal arguments {args}")

        self.print_step("Help")
        self.print_usage()

    def print_usage(self) -> None:
        self.println(
            """Run with subcommand

            cli [sub-command] [arguments]

            Sub-commands:
                database  database related operation
                help      print this help message

            Examples:

            # show this help message
            cli help

            # show help message of a sub-command
            cli database
            cli database help

            # execute sub-command with arguments
            cli database --check-connection
            """
        )
