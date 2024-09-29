from typing import Protocol, Union

class AslQuery:
    pass

class AslQueryCondition(Protocol):
    class AslConditionOperator:
        LIKE = 'LIKE'
        IN = 'IN'
        EQ = 'EQ'
        NEQ = 'NEQ'
        GT_EQ = 'GT_EQ'
        GT = 'GT'
        LT_EQ = 'LT_EQ'
        LT = 'LT'
        IS_NULL = 'IS_NULL'
        IS_NOT_NULL = 'IS_NOT_NULL'

    def with_provider(self, provider: AslQuery) -> 'AslQueryCondition':
        ...


class AslAndQueryCondition:
    def with_provider(self, provider: AslQuery) -> 'AslAndQueryCondition':
        # Implement method logic
        return self

# Example usage
condition = AslAndQueryCondition()
new_condition = condition.with_provider(AslQuery())
