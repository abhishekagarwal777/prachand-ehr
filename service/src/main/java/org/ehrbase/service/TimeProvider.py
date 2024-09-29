from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta

class TimeProvider(ABC):
    @abstractmethod
    def get_now(self) -> datetime:
        pass

class DefaultTimeProvider(TimeProvider):
    def get_now(self) -> datetime:
        return datetime.now(timezone.utc)
