import unittest
from unittest.mock import Mock, patch
from your_module import CliHelpCommand

class CliHelpCommandTest(unittest.TestCase):

    def setUp(self):
        self.cmd = Mock(CliHelpCommand())
        self.cmd.exit = Mock()
        self.cmd.println = Mock()

    def test_command_name_is_help(self):
        self.assertEqual(self.cmd.get_name(), "help")

    def test_run_with_argument_error(self):
        self.cmd.run(["invalid"])
        self.cmd.exit_fail.assert_called_once_with("illegal arguments [invalid]")
        self.cmd.exit.assert_called_once_with(-1)

    def test_run_without_argument(self):
        self.cmd.run([])
        self.cmd.print_usage.assert_called_once()
        self.cmd.exit.assert_not_called()
