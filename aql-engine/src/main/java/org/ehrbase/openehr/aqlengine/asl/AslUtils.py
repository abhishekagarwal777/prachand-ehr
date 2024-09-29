from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Union, Set
import re
import uuid
from enum import Enum

class AslConditionOperator(Enum):
    IN = "IN"
    EQ = "EQ"
    LIKE = "LIKE"
    NEQ = "NEQ"
    # Add other operators as needed

class AslField:
    pass

class AslQuery:
    pass

class AslStructureColumn:
    ENTITY_NAME = "entity_name"
    TEMPLATE_ID = "template_id"
    # Add other structure fields as needed

class AslExtractedColumn:
    @staticmethod
    def find(rm_type, path):
        # Implement logic to find extracted column
        pass

class AslQueryCondition:
    pass

class AslFieldValueQueryCondition(AslQueryCondition):
    def __init__(self, field, operator, values):
        self.field = field
        self.operator = operator
        self.values = values

class AslFalseQueryCondition(AslQueryCondition):
    pass

class AslTrueQueryCondition(AslQueryCondition):
    pass

class AliasProvider:
    def __init__(self):
        self.alias_counters = {}

    def unique_alias(self, alias: str) -> str:
        count = self.alias_counters.get(alias, 0) + 1
        self.alias_counters[alias] = count
        return f"{alias}_{count}"

class AslUtils:
    @staticmethod
    def stream_condition_fields(condition: AslQueryCondition):
        if isinstance(condition, AslAndQueryCondition):
            return (field for operand in condition.operands for field in AslUtils.stream_condition_fields(operand))
        elif isinstance(condition, AslOrQueryCondition):
            return (field for operand in condition.operands for field in AslUtils.stream_condition_fields(operand))
        elif isinstance(condition, AslNotQueryCondition):
            return AslUtils.stream_condition_fields(condition.condition)
        elif isinstance(condition, AslNotNullQueryCondition):
            return [condition.field]
        elif isinstance(condition, AslFieldValueQueryCondition):
            return [condition.field]
        elif isinstance(condition, (AslFalseQueryCondition, AslTrueQueryCondition)):
            return []
        else:
            raise ValueError("Unsupported condition type")

    @staticmethod
    def translate_aql_like_pattern_to_sql(aql_like: str) -> str:
        escaped = re.escape(aql_like)
        return escaped.replace(r'\%', r'\\%').replace(r'\_', r'\\_').replace('?', '_').replace('*', '%')

    @staticmethod
    def parse_date_time_or_time_with_higher_precision(val: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return None

    @staticmethod
    def find_field_for_owner(field_name: str, fields: List[AslField], owner: AslQuery) -> AslField:
        for field in fields:
            if field.owner == owner and field.column_name == field_name:
                return field
        raise ValueError(f"Field '{field_name}' does not exist for owner '{owner.alias}'")

    @staticmethod
    def structure_predicate_condition(predicate, query: AslStructureQuery, template_uuid_lookup_func: Callable) -> AslQueryCondition:
        # Implement logic based on the structure of predicate and query
        pass

    @staticmethod
    def condition_value(values: List[Union[str, uuid.UUID]], operator: AslConditionOperator, type_: type) -> List:
        # Implement logic to handle condition values
        pass

# Example usage
alias_provider = AliasProvider()
unique_alias = alias_provider.unique_alias("example")
print(unique_alias)  # Outputs: example_1
