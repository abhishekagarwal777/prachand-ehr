from typing import Protocol

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

class AslTrueQueryCondition(AslQueryCondition):
    def with_provider(self, provider: AslQuery) -> 'AslTrueQueryCondition':
        return AslTrueQueryCondition()


# Example usage
condition = AslTrueQueryCondition()
new_condition = condition.with_provider(AslQuery())
