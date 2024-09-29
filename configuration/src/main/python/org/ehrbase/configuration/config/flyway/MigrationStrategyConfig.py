import logging
from typing import Dict
from flyway import Flyway, FluentConfiguration  # Adjust imports based on actual Flyway Python implementation

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class MigrationStrategyConfig:
    def __init__(self, ehr_schema: str, ext_schema: str, ehr_location: str, ext_location: str,
                 ext_strategy: 'MigrationStrategy', ehr_strategy: 'MigrationStrategy'):
        self.ehr_schema = ehr_schema
        self.ext_schema = ext_schema
        self.ehr_location = ehr_location
        self.ext_location = ext_location
        self.ext_strategy = ext_strategy
        self.ehr_strategy = ehr_strategy

    def flyway_migration_strategy(self):
        return lambda flyway: self._apply_strategy(flyway)

    def _apply_strategy(self, flyway: Flyway):
        if self.ext_strategy != MigrationStrategy.DISABLED:
            self.ext_strategy.apply_strategy(
                self._set_schema(flyway, self.ext_schema)
                .locations(self.ext_location)
                .baseline_on_migrate(True)
                .baseline_version("1")
                .placeholders({"extSchema": self.ext_schema})
                .load()
            )
        else:
            log.info("Flyway migration for schema 'ext' is disabled")

        if self.ehr_strategy != MigrationStrategy.DISABLED:
            self.ehr_strategy.apply_strategy(
                self._set_schema(flyway, self.ehr_schema)
                .placeholders({"ehrSchema": self.ehr_schema})
                .locations(self.ehr_location)
                .load()
            )
        else:
            log.info("Flyway migration for schema 'ehr' is disabled")

    def _set_schema(self, flyway: Flyway, schema: str) -> FluentConfiguration:
        return Flyway.configure() \
            .data_source(flyway.configuration.get_data_source()) \
            .schemas(schema)
