from typing import List, Dict, Optional, Union
from collections import defaultdict
from enum import Enum

# Assuming necessary imports are made from your Aql-related module

class SelectType(Enum):
    PATH = "PATH"
    AGGREGATE_FUNCTION = "AGGREGATE_FUNCTION"
    PRIMITIVE = "PRIMITIVE"

class ComparisonConditionOperator(Enum):
    EQ = "EQ"
    NEQ = "NEQ"
    LIKE = "LIKE"
    MATCHES = "MATCHES"
    EXISTS = "EXISTS"

class LogicalConditionOperator(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class SelectWrapper:
    def __init__(self, expression, select_type: SelectType, containment_wrapper):
        self.expression = expression
        self.select_type = select_type
        self.containment_wrapper = containment_wrapper

class ConditionWrapper:
    pass

class ComparisonOperatorConditionWrapper(ConditionWrapper):
    def __init__(self, path_wrapper, operator: ComparisonConditionOperator, value):
        self.path_wrapper = path_wrapper
        self.operator = operator
        self.value = value

class LogicalOperatorConditionWrapper(ConditionWrapper):
    def __init__(self, operator: LogicalConditionOperator, conditions: List[ConditionWrapper]):
        self.operator = operator
        self.conditions = conditions

class OrderByWrapper:
    def __init__(self, statement, symbol, containment_wrapper):
        self.statement = statement
        self.symbol = symbol
        self.containment_wrapper = containment_wrapper

class ContainsWrapper:
    pass

class ContainsChain:
    def __init__(self, chain: List[ContainsWrapper], set_operator):
        self.chain = chain
        self.set_operator = set_operator

class AqlQueryWrapper:
    def __init__(self, distinct: bool, selects: List[SelectWrapper], contains_chain: ContainsChain,
                 where: Optional[ConditionWrapper], order_by: List[OrderByWrapper],
                 limit: Optional[int], offset: Optional[int], path_infos: Dict[ContainsWrapper, 'PathInfo']):
        self.distinct = distinct
        self.selects = selects
        self.contains_chain = contains_chain
        self.where = where
        self.order_by = order_by
        self.limit = limit
        self.offset = offset
        self.path_infos = path_infos

    def non_primitive_selects(self):
        return (select for select in self.selects if select.select_type != SelectType.PRIMITIVE)

    @staticmethod
    def create(aql_query: 'AqlQuery') -> 'AqlQueryWrapper':
        contains_descs = {}
        from_root = aql_query.get_from()

        for containment in AqlUtil.stream_containments(from_root):
            if isinstance(containment, ContainmentClassExpression):
                contains_descs[containment] = RmContainsWrapper(containment)
        
        for containment in AqlUtil.stream_containments(from_root):
            if isinstance(containment, ContainmentVersionExpression):
                contains_descs[containment] = VersionContainsWrapper(containment.get_identifier(),
                    contains_descs[containment.get_contains()])

        from_clause = AqlQueryWrapper.build_contains_chain(from_root, contains_descs)

        selects = [
            AqlQueryWrapper.build_select_descriptor(contains_descs, s)
            for s in aql_query.get_select().get_statement()
        ]

        where = AqlQueryWrapper.build_where_descriptor(aql_query.get_where(), contains_descs, False) if aql_query.get_where() else None

        order_by = [
            AqlQueryWrapper.build_order_by_descriptor(o, contains_descs)
            for o in (aql_query.get_order_by() or [])
        ]

        path_infos = PathInfo.create_path_infos(aql_query, contains_descs)

        return AqlQueryWrapper(
            aql_query.get_select().is_distinct(),
            selects,
            from_clause,
            where,
            order_by,
            aql_query.get_limit(),
            aql_query.get_offset(),
            path_infos
        )

    @staticmethod
    def build_order_by_descriptor(expression, contains_descs) -> OrderByWrapper:
        return OrderByWrapper(
            expression.get_statement(),
            expression.get_symbol(),
            contains_descs.get(expression.get_statement().get_root())
        )

    @staticmethod
    def build_contains_chain(root, contains_descs) -> ContainsChain:
        chain = []
        set_operator = None

        next_containment = root
        while isinstance(next_containment, AbstractContainmentExpression):
            chain.append(contains_descs[next_containment])
            if isinstance(next_containment, ContainmentVersionExpression):
                next_containment = next_containment.get_contains().get_contains()
            else:
                next_containment = next_containment.get_contains()

        if isinstance(next_containment, ContainmentSetOperator):
            set_operator = ContainsSetOperationWrapper(
                next_containment.get_symbol(),
                [AqlQueryWrapper.build_contains_chain(c, contains_descs) for c in next_containment.get_values()]
            )

        return ContainsChain(chain, set_operator)

    @staticmethod
    def build_select_descriptor(contains_descs, s) -> SelectWrapper:
        column_expr = s.get_column_expression()
        if isinstance(column_expr, IdentifiedPath):
            select_type = SelectType.PATH
            path = column_expr
        elif isinstance(column_expr, AggregateFunction):
            select_type = SelectType.AGGREGATE_FUNCTION
            path = column_expr.get_identified_path()
        elif isinstance(column_expr, Primitive):
            select_type = SelectType.PRIMITIVE
            path = None
        else:
            raise ValueError("Unknown ColumnExpression type in SELECT")

        return SelectWrapper(
            s,
            select_type,
            contains_descs.get(path.get_root()) if path else None
        )

    @staticmethod
    def build_where_descriptor(where, contains_descs, negate) -> ConditionWrapper:
        if isinstance(where, ComparisonOperatorCondition):
            return ComparisonOperatorConditionWrapper(
                ComparisonOperatorConditionWrapper.IdentifiedPathWrapper(
                    contains_descs.get(where.get_statement().get_root()),
                    where.get_statement()
                ),
                ComparisonConditionOperator[where.get_symbol().name()],
                where.get_value()
            )
        elif isinstance(where, MatchesCondition):
            if negate:
                return LogicalOperatorConditionWrapper(
                    LogicalConditionOperator.OR,
                    [
                        ComparisonOperatorConditionWrapper(
                            ComparisonOperatorConditionWrapper.IdentifiedPathWrapper(
                                contains_descs.get(where.get_statement().get_root()),
                                where.get_statement()
                            ),
                            ComparisonConditionOperator.NEQ,
                            v
                        )
                        for v in where.get_values()
                    ]
                )
            else:
                return ComparisonOperatorConditionWrapper(
                    ComparisonOperatorConditionWrapper.IdentifiedPathWrapper(
                        contains_descs.get(where.get_statement().get_root()),
                        where.get_statement()
                    ),
                    ComparisonConditionOperator.MATCHES,
                    where.get_values()
                )
        elif isinstance(where, LikeCondition):
            condition = ComparisonOperatorConditionWrapper(
                ComparisonOperatorConditionWrapper.IdentifiedPathWrapper(
                    contains_descs.get(where.get_statement().get_root()),
                    where.get_statement()
                ),
                ComparisonConditionOperator.LIKE,
                where.get_value()
            )
            return LogicalOperatorConditionWrapper(
                LogicalConditionOperator.NOT,
                [condition]
            ) if negate else condition
        elif isinstance(where, ExistsCondition):
            comparison_condition = ComparisonOperatorConditionWrapper(
                ComparisonOperatorConditionWrapper.IdentifiedPathWrapper(
                    contains_descs.get(where.get_value().get_root()),
                    where.get_value()
                ),
                ComparisonConditionOperator.EXISTS,
                []
            )
            return LogicalOperatorConditionWrapper(
                LogicalConditionOperator.NOT,
                [comparison_condition]
            ) if negate else comparison_condition
        elif isinstance(where, LogicalOperatorCondition):
            return LogicalOperatorConditionWrapper(
                LogicalConditionOperator.AND if (where.get_symbol() == "AND" and negate) or
                                                 (where.get_symbol() == "OR" and not negate) else
                LogicalConditionOperator.OR,
                [
                    AqlQueryWrapper.build_where_descriptor(w, contains_descs, negate)
                    for w in where.get_values()
                ]
            )
        elif isinstance(where, NotCondition):
            return AqlQueryWrapper.build_where_descriptor(where.get_condition_dto(), contains_descs, not negate)
        else:
            raise ValueError(f"Unknown WhereCondition class: {type(where)}")

    def __str__(self):
        return (f"AqlQueryWrapper[distinct={self.distinct}, selects={self.selects}, "
                f"contains_chain={self.contains_chain}, where={self.where}, order_by={self.order_by}, "
                f"limit={self.limit}, offset={self.offset}, path_infos={self.path_infos}]")
