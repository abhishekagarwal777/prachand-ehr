from typing import Dict, Callable
from dataclasses import dataclass
import sqlalchemy as sa

@dataclass
class PreparedQuery:
    select_query: sa.sql.Select
    post_processors: Dict[int, Callable[[sa.engine.base.Row], object]]

    def __str__(self) -> str:
        return str(self.select_query)
