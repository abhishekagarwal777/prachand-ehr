from typing import Callable

class CliOverwriteConfig:
    @staticmethod
    def flyway_migration_strategy() -> Callable:
        def no_op_strategy(flyway):
            # Nop - prevent any flyway interaction
            pass
        return no_op_strategy

    @staticmethod
    def external_terminology_validator() -> ExternalTerminologyValidation:
        return ValidationConfiguration.nop_terminology_validation()
