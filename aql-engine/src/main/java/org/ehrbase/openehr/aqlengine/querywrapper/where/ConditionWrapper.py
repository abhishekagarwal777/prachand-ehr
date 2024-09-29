from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Type, Union
from enum import Enum

# Abstract base class for ConditionWrapper
class ConditionWrapper(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

# Enum for LogicalConditionOperator
class LogicalConditionOperator(Enum):
    AND = ("AslAndQueryCondition", "AslTrueQueryCondition", "AslFalseQueryCondition")
    OR = ("AslOrQueryCondition", "AslFalseQueryCondition", "AslTrueQueryCondition")
    NOT = (lambda l: l[0] if l else None, None, None)

    def __init__(self, set_operator: Union[str, Callable[[List['AslQueryCondition']], 'AslQueryCondition']], 
                 noop_condition: Type, 
                 short_circuit_condition: Type):
        self.set_operator = set_operator
        self.noop_condition = noop_condition
        self.short_circuit_condition = short_circuit_condition

    def build(self, params: List['AslQueryCondition']) -> 'AslQueryCondition':
        if callable(self.set_operator):
            return self.set_operator(params)
        return self.set_operator

    def filter_not_noop(self, condition: 'AslQueryCondition') -> bool:
        return not isinstance(condition, self.noop_condition)

    def filter_short_circuit(self, condition: 'AslQueryCondition') -> bool:
        return isinstance(condition, self.short_circuit_condition)

# Enum for ComparisonConditionOperator
class ComparisonConditionOperator(Enum):
    EXISTS = "IS_NOT_NULL"
    LIKE = "LIKE"
    MATCHES = "IN"
    EQ = "EQ"
    NEQ = "NEQ"
    GT_EQ = "GT_EQ"
    GT = "GT"
    LT_EQ = "LT_EQ"
    LT = "LT"

    def __init__(self, asl_operator: str):
        self.asl_operator = asl_operator

    def get_asl_operator(self) -> str:
        return self.asl_operator

    def negate(self) -> 'ComparisonConditionOperator':
        negations = {
            ComparisonConditionOperator.EQ: ComparisonConditionOperator.NEQ,
            ComparisonConditionOperator.NEQ: ComparisonConditionOperator.EQ,
            ComparisonConditionOperator.GT_EQ: ComparisonConditionOperator.LT,
            ComparisonConditionOperator.GT: ComparisonConditionOperator.LT_EQ,
            ComparisonConditionOperator.LT_EQ: ComparisonConditionOperator.GT,
            ComparisonConditionOperator.LT: ComparisonConditionOperator.GT_EQ
        }
        if self in negations:
            return negations[self]
        raise NotImplementedError(f"No operator known to represent negated {self}")

    @staticmethod
    def value_of(name: str, negated: bool) -> 'ComparisonConditionOperator':
        try:
            operator = ComparisonConditionOperator[name]
        except KeyError:
            raise ValueError(f"Unknown operator: {name}")
        return operator.negate() if negated else operator
