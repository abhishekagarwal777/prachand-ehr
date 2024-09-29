from typing import Optional, List, Union, Generator


class AqlQueryUtils:
    @staticmethod
    def all_identified_paths(query):
        return (
            path
            for sublist in (
                AqlQueryUtils._all_identified_paths_from_select(query.select.statement),
                AqlQueryUtils.stream_where_conditions(query.where),
                (order_by.statement for order_by in (query.order_by or []))
            )
            for path in sublist
        )

    @staticmethod
    def _all_identified_paths_from_select(select_expressions):
        for select_expression in select_expressions:
            yield from AqlQueryUtils.all_identified_paths_select(select_expression)

    @staticmethod
    def all_identified_paths_where(w):
        if isinstance(w, ComparisonOperatorCondition):
            yield from AqlQueryUtils.all_identified_paths(w.statement)
            yield from AqlQueryUtils.all_identified_paths(w.value)
        elif isinstance(w, MatchesCondition):
            yield w.statement
        elif isinstance(w, LikeCondition):
            yield w.statement
        elif isinstance(w, ExistsCondition):
            # XXX Should this be included in the analysis?
            yield w.value
        else:
            raise ValueError(f"Unsupported type of {w}")

    @staticmethod
    def all_identified_paths_select(select_expression):
        column_expression = select_expression.column_expression
        if isinstance(column_expression, Primitive):
            return
        elif isinstance(column_expression, AggregateFunction):
            yield from (column_expression.identified_path,)
        elif isinstance(column_expression, IdentifiedPath):
            yield column_expression
        elif isinstance(column_expression, SingleRowFunction):
            for operand in column_expression.operand_list:
                yield from AqlQueryUtils.all_identified_paths(operand)
        else:
            raise ValueError(f"Unsupported type of {column_expression}")

    @staticmethod
    def all_identified_paths_operand(operand):
        if isinstance(operand, Primitive) or isinstance(operand, QueryParameter):
            return
        elif isinstance(operand, IdentifiedPath):
            yield operand
        elif isinstance(operand, SingleRowFunction):
            for sub_operand in operand.operand_list:
                yield from AqlQueryUtils.all_identified_paths(sub_operand)
        else:
            raise ValueError(f"Unsupported type of {operand}")

    @staticmethod
    def all_identified_paths_comparison_left_operand(operand):
        if isinstance(operand, IdentifiedPath):
            yield operand
        elif isinstance(operand, SingleRowFunction):
            for sub_operand in operand.operand_list:
                yield from AqlQueryUtils.all_identified_paths(sub_operand)
        else:
            raise ValueError(f"Unsupported type of {operand}")

    @staticmethod
    def stream_where_conditions(condition: Optional[WhereCondition]) -> Generator[WhereCondition, None, None]:
        if condition is None:
            return
        if isinstance(condition, (ComparisonOperatorCondition, MatchesCondition, LikeCondition, ExistsCondition)):
            yield condition
        elif isinstance(condition, LogicalOperatorCondition):
            for value in condition.values:
                yield from AqlQueryUtils.stream_where_conditions(value)
        elif isinstance(condition, NotCondition):
            yield from AqlQueryUtils.stream_where_conditions(condition.condition_dto)
        else:
            raise ValueError(f"Unsupported condition type {condition.__class__.__name__}")
