import unittest
from unittest.mock import Mock, call
from your_module import CliRunner, CliHelpCommand, CliCommand

class TestCliCommand(CliCommand):
    
    def __init__(self, name):
        super().__init__(name)
        self.args = None
        self.did_run = False
        self.did_print_usage = False

    def run(self, args):
        self.did_run = True
        self.args = args

    def print_usage(self):
        self.did_print_usage = True

class CliRunnerTest(unittest.TestCase):

    def setUp(self):
        self.mock_help_command = Mock(CliHelpCommand)
        self.cli_runner = lambda *commands: CliRunner(list(commands), self.mock_help_command)

    def test_duplicate_command_error(self):
        cmd1 = TestCliCommand("duplicate-cmd")
        cmd2 = TestCliCommand("duplicate-cmd")
        with self.assertRaises(IllegalStateException) as cm:
            self.cli_runner(cmd1, cmd2).run()
        self.assertEqual(str(cm.exception), f"Duplicate command for name duplicate-cmd (attempted merging values {cmd1} and {cmd2})")

    def test_run_error_without_arguments(self):
        self.cli_runner().run()
        self.mock_help_command.exit_fail.assert_called_once_with("No command specified")

    def test_run_error_without_cli_arguments(self):
        self.cli_runner().run("--some --other=true --command")
        self.mock_help_command.exit_fail.assert_called_once_with("No command specified")

    def test_run_error_command_not_exist(self):
        self.cli_runner().run("cli", "does-not-exist")
        self.mock_help_command.exit_fail.assert_called_once_with("Unknown command does-not-exist")

    def test_run_command(self):
        cmd = TestCliCommand("capture-the-flag")
        self.cli_runner(cmd).run(CliRunner.CLI, "capture-the-flag")
        self.assertTrue(cmd.did_run, "command did not run")
        self.assertIsNotNone(cmd.args)

    def test_run_command_help(self):
        cmd = TestCliCommand("capture-the-flag")
        self.cli_runner(cmd).run(CliRunner.CLI, "capture-the-flag", "help")
        self.assertTrue(cmd.did_run, "command did not run")
        self.assertIsNotNone(cmd.args)

    def test_run_command_with_argument(self):
        cmd = TestCliCommand("capture-the-flag")
        self.cli_runner(cmd).run(CliRunner.CLI, "capture-the-flag", "--flag=true")
        self.assertTrue(cmd.did_run, "command did not run")
        self.assertEqual(len(cmd.args), 1)
        self.assertEqual(cmd.args[0], "--flag=true")

if __name__ == '__main__':
    unittest.main()
