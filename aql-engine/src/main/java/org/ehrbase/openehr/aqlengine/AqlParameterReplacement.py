# Copyright (c) 2024 vitasystems GmbH.
#
# This file is part of project EHRbase
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import List, Dict, Optional, Callable
from collections import defaultdict
from itertools import chain

# Mocks of some EHRbase specific classes - these would be implemented similarly to the Java DTOs
class AslRmTypeAndConcept:
    pass

class AqlQuery:
    pass

class ComparisonOperatorCondition:
    pass

class ExistsCondition:
    pass

class LikeCondition:
    pass

class LogicalOperatorCondition:
    pass

class MatchesCondition:
    pass

class NotCondition:
    pass

class WhereCondition:
    pass

class AbstractContainmentExpression:
    pass

class Containment:
    pass

class ContainmentClassExpression:
    pass

class ContainmentNotOperator:
    pass

class ContainmentSetOperator:
    pass

class ContainmentVersionExpression:
    pass

class AggregateFunction:
    pass

class BooleanPrimitive:
    pass

class ComparisonLeftOperand:
    pass

class DoublePrimitive:
    pass

class IdentifiedPath:
    pass

class LikeOperand:
    pass

class LongPrimitive:
    pass

class MatchesOperand:
    pass

class Operand:
    pass

class PathPredicateOperand:
    pass

class Primitive:
    pass

class QueryParameter:
    pass

class SingleRowFunction:
    pass

class StringPrimitive:
    pass

class TemporalPrimitive:
    pass

class TerminologyFunction:
    pass

class OrderByExpression:
    pass

class AndOperatorPredicate:
    pass

class AqlObjectPath:
    pass

class AqlObjectPathUtil:
    pass

class ComparisonOperatorPredicate:
    pass

class SelectClause:
    pass

class SelectExpression:
    pass

class AqlParseException(Exception):
    pass


# Utility functions (mapping some of the Java functional constructs to Python's functional tools)

def map_utils_is_empty(map_obj: Dict) -> bool:
    """Replicates the functionality of MapUtils.isEmpty in Python."""
    return len(map_obj) == 0

def stream_collect(stream: Callable, collector: Callable):
    """Simulates Java's stream.collect in Python."""
    return collector(stream())

def int_stream_range(start: int, end: int):
    """Simulates Java's IntStream.range."""
    return range(start, end)

def stream_filter(predicate: Callable, collection: List):
    """Simulates Java's stream.filter."""
    return list(filter(predicate, collection))

def stream_map(function: Callable, collection: List):
    """Simulates Java's stream.map."""
    return list(map(function, collection))

def pattern_compile(regex: str):
    """Wrapper around Python's regex compile function."""
    return re.compile(regex)
import re
from typing import List, Optional, Dict, Union

class AqlParameterReplacement:

    @staticmethod
    def replace_parameters(aql_query, parameter_map: Dict[str, Union[int, float, str, bool]]):
        if parameter_map:
            # SELECT
            SelectParams.replace_parameters(aql_query.select, parameter_map)
            # FROM
            ContainmentParams.replace_parameters(aql_query.from_, parameter_map)
            # WHERE
            WhereParams.replace_parameters(aql_query.where, parameter_map)
            # ORDER BY
            OrderByParams.replace_parameters(parameter_map, aql_query.order_by)

    @staticmethod
    def replace_identified_path_parameters(identified_path, parameter_map: Dict[str, Union[int, float, str, bool]]):
        # Modify root predicates in place
        if identified_path.root_predicate:
            for operand in identified_path.root_predicate.operands:
                ObjectPathParams.replace_comparison_operator_parameters(operand, True, parameter_map)

        ObjectPathParams.replace_parameters(identified_path.path, parameter_map).if_present(
            lambda path: identified_path.set_path(path)
        )


class SelectParams:

    @staticmethod
    def replace_parameters(select_clause, parameter_map: Dict[str, Union[int, float, str, bool]]):
        for statement in select_clause.statements:
            column_expression = statement.column_expression
            if isinstance(column_expression, SingleRowFunction):
                AqlParameterReplacement.replace_function_parameters(column_expression, parameter_map)
            elif isinstance(column_expression, AggregateFunction):
                AqlParameterReplacement.replace_identified_path_parameters(column_expression.identified_path, parameter_map)
            elif isinstance(column_expression, IdentifiedPath):
                AqlParameterReplacement.replace_identified_path_parameters(column_expression, parameter_map)


class OrderByParams:

    @staticmethod
    def replace_parameters(parameter_map: Dict[str, Union[int, float, str, bool]], order_by: List):
        if order_by:
            for expression in order_by:
                AqlParameterReplacement.replace_identified_path_parameters(expression.statement, parameter_map)


class WhereParams:

    @staticmethod
    def replace_parameters(where_condition, parameter_map: Dict[str, Union[int, float, str, bool]]):
        if where_condition is None:
            return
        elif isinstance(where_condition, ComparisonOperatorCondition):
            WhereParams.replace_comparison_left_operand_parameters(where_condition.statement, parameter_map)
            AqlParameterReplacement.replace_operand_parameters(where_condition.value, parameter_map).if_present(
                lambda value: where_condition.set_value(value)
            )
        elif isinstance(where_condition, NotCondition):
            WhereParams.replace_parameters(where_condition.condition_dto, parameter_map)
        elif isinstance(where_condition, MatchesCondition):
            for i, operand in enumerate(where_condition.values):
                WhereParams.replace_matches_parameters(operand, parameter_map)
        elif isinstance(where_condition, LikeCondition):
            WhereParams.replace_like_operand_parameters(where_condition.value, parameter_map).if_present(
                lambda value: where_condition.set_value(value)
            )
        elif isinstance(where_condition, LogicalOperatorCondition):
            for condition in where_condition.values:
                WhereParams.replace_parameters(condition, parameter_map)


class Utils:

    @staticmethod
    def revise_list(lst: List, replacement_func):
        for i in range(len(lst)):
            replacement = replacement_func(lst[i])
            if replacement:
                lst[i] = replacement

    @staticmethod
    def string_to_primitive(s: str):
        if TemporalPrimitivePattern.matches(s):
            return TemporalPrimitive(s)
        return StringPrimitive(s)

    @staticmethod
    def replace_child_parameters(children: List, replacement_func, parameter_map):
        modified = False
        new_children = []
        for child in children:
            replacement = replacement_func(child, parameter_map)
            if replacement:
                new_children.append(replacement)
                modified = True
            else:
                new_children.append(child)
        return new_children if modified else None


class TemporalPrimitivePattern:

    TEMPORAL_PATTERN = None

    @staticmethod
    def initialize():
        if TemporalPrimitivePattern.TEMPORAL_PATTERN is None:
            # Regular expressions for temporal pattern matching
            TemporalPrimitivePattern.TEMPORAL_PATTERN = re.compile(
                r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[-+]\d{2}:\d{2}))"
            )

    @staticmethod
    def matches(s: str) -> bool:
        TemporalPrimitivePattern.initialize()
        return bool(TemporalPrimitivePattern.TEMPORAL_PATTERN.match(s))
