import unittest
from unittest.mock import Mock, patch, call
from your_module import CliDataBaseCommand, MigrationStrategy, MigrationStrategyConfig, Flyway, HikariDataSource

class CliDataBaseCommandTest(unittest.TestCase):

    def setUp(self):
        self.dataSource = Mock(HikariDataSource)
        self.flyway = Mock(Flyway)
        self.migrationStrategyConfig = Mock(MigrationStrategyConfig)
        self.strategy = Mock()
        self.cmd = Mock(CliDataBaseCommand(self.dataSource, self.flyway, self.migrationStrategyConfig))

        self.cmd.exit = Mock()
        self.cmd.println = Mock()
        
    def test_command_name_is_help(self):
        self.assertEqual(self.cmd.get_name(), "database")

    def test_run_without_argument_error(self):
        self.cmd.run([])
        self.cmd.print_usage.assert_called_once()
        self.cmd.exit_fail.assert_called_once_with("No argument provided")
        self.cmd.exit.assert_called_once_with(-1)

    def test_run_with_unknown_argument_error(self):
        self.cmd.run(["illegal"])
        self.cmd.print_usage.assert_called_once()
        self.cmd.exit_fail.assert_called_once_with("Unknown argument [illegal]")
        self.cmd.exit.assert_called_once_with(-1)

    def test_run_help(self):
        self.cmd.run(["help"])
        self.cmd.print_usage.assert_called_once()
        self.cmd.exit_fail.assert_not_called()
        self.cmd.exit.assert_not_called()

    def test_run_check_connection(self):
        jdb_url = "jdbc:test//localhost:1234/db"
        self.dataSource.get_jdbc_url.return_value = jdb_url

        connection = Mock()
        meta_data = Mock()
        meta_data.get_url.return_value = jdb_url
        connection.get_meta_data.return_value = meta_data
        self.dataSource.get_connection.return_value = connection

        self.cmd.run(["--check-connection"])
        self.cmd.print_usage.assert_not_called()
        self.cmd.exit.assert_not_called()

    def test_run_migration_verify(self):
        self.run_migration_test("--migration-validate", MigrationStrategy.VALIDATE)

    def test_run_migration_migrate(self):
        self.run_migration_test("--migration-migrate", MigrationStrategy.MIGRATE)

    def run_migration_test(self, arg, migration_strategy):
        self.migrationStrategyConfig.flyway_migration_strategy.return_value = self.strategy

        self.cmd.run([arg])
        self.strategy.migrate.assert_called_once_with(self.flyway)
