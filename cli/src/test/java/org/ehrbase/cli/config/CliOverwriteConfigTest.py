import unittest
from unittest.mock import Mock
from your_module import CliOverwriteConfig
from your_module import NopExternalTerminologyValidation

class CliOverwriteConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = CliOverwriteConfig()

    def test_nop_flyway_migration_strategy(self):
        flyway = Mock()
        self.config.flyway_migration_strategy()(flyway)
        flyway.migrate.assert_not_called()

    def test_nop_external_terminology_validator(self):
        self.assertIsInstance(self.config.external_terminology_validator(), NopExternalTerminologyValidation)
