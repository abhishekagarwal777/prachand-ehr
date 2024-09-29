from typing import List, Optional, Callable, Union

class CliArgument:
    def __init__(self, arg: str, key: str, value: Optional[str]):
        self.arg = arg
        self.key = key
        self.value = value

class Result:
    class OK:
        pass

    class Unknown:
        pass

    OK = OK()
    Unknown = Unknown()

class CliCommand:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def run(self, args: List[str]) -> None:
        raise NotImplementedError

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
        raise NotImplementedError

    def consume_args(self, args: List[str], consumer: Callable[[CliArgument], Result]) -> None:
        if not args:
            self.exit_fail("No argument provided")
            return

        for arg_str in args:
            if arg_str == "help":
                self.print_usage()
                return

            split = arg_str.split("=")
            arg = CliArgument(arg_str, split[0].replace("--", ""), split[1] if len(split) > 1 else None)
            result = consumer(arg)
            if isinstance(result, Result.Unknown):
                self.exit_fail(f"Unknown argument [{arg.arg}]")

class CliDataBaseCommand(CliCommand):
    def __init__(self, data_source, flyway, migration_strategy_config):
        super().__init__("database")
        self.data_source = data_source
        self.flyway = flyway
        self.migration_strategy_config = migration_strategy_config

    def run(self, args: List[str]) -> None:
        self.consume_args(args, lambda arg: {
            "check-connection": self.execute_check_connection,
            "migration-validate": lambda: self.execute_migration(MigrationStrategy.VALIDATE),
            "migration-migrate": lambda: self.execute_migration(MigrationStrategy.MIGRATE)
        }.get(arg.key, lambda: Result.Unknown)())

    def execute_check_connection(self) -> Result:
        self.print_step(f"executing Database connection check: {self.jdb_url()}")

        try:
            with self.data_source.get_connection() as connection:
                url = connection.get_meta_data().get_url()
                self.println(f"Connection established to {url}")
                return Result.OK
        except Exception as e:
            self.exit_fail(f"Failed to open connection {self.jdb_url()}")
            return Result.Unknown

    def execute_migration(self, migration_strategy) -> Result:
        self.print_step(f"executing Flyway with strategy: {migration_strategy}")

        strategy = self.migration_strategy_config.flyway_migration_strategy(migration_strategy, migration_strategy)
        strategy.migrate(self.flyway)
        return Result.OK

    def jdb_url(self) -> str:
        return self.data_source.get_jdbc_url()

    def print_usage(self) -> None:
        self.println(
            """Database related operation like connection verification or migration.

            Arguments:
              --check-connection    verifies database access by open/close a connection
              --migration-validate  validate flyway migration
              --migration-migrate   executes flyway migration

            Example:

            database --check-connection --migration-validate
            """
        )
