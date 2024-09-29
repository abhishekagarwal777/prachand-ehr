from enum import Enum

class ClauseType(Enum):
    SELECT = 'SELECT'
    WHERE = 'WHERE'
    FROM_PREDICATE = 'FROM_PREDICATE'
    ORDER_BY = 'ORDER_BY'
