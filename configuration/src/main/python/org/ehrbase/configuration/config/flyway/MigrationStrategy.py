from enum import Enum
from typing import Callable
from flyway import Flyway  # Assuming Flyway is a Python class or interface you need to define or import

class MigrationStrategy(Enum):
    DISABLED = lambda flyway: None
    MIGRATE = lambda flyway: flyway.migrate()
    VALIDATE = lambda flyway: flyway.validate()

    def __init__(self, strategy: Callable[[Flyway], None]):
        self._strategy = strategy

    def apply_strategy(self, flyway: Flyway):
        self._strategy(flyway)
