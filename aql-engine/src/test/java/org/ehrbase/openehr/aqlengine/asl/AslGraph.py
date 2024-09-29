import itertools
from typing import List, Optional, Callable
from your_module import (
    org.ehrbase.openehr.aqlengine.asl.model.join.AslJoin,AslRootQuery, AslField, AslQuery, AslStructureQuery, AslEncapsulatingQuery, AslDataQuery,
    AslPathDataQuery, AslFieldValueQueryCondition, AslNotQueryCondition, AslFalseQueryCondition,
    AslTrueQueryCondition, AslOrQueryCondition, AslAndQueryCondition, AslNotNullQueryCondition,
    AslEntityIdxOffsetCondition, AslDescendantCondition, AslPathChildCondition, AslJoinCondition,
    AslPathFilterJoinCondition, AslDelegatingJoinCondition, AslAuditDetailsJoinCondition, AslColumnField,
    AslComplexExtractedColumnField, AslAggregatingField, AslSubqueryField, AslConstantField, AslOrderByField
)

def create_asl_graph(query: AslRootQuery) -> str:
    return '\n'.join([
        indented(0, "AslRootQuery"),
        select_graph(1, query.select),
        indented(1, "FROM"),
        ''.join(sq_to_graph(2, s[0], s[1]) for s in query.children),
        section(1, query.condition, lambda x: x is not None, lambda: "WHERE", condition_to_graph),
        section(1, query.group_by_fields, bool, lambda: "GROUP BY", lambda l, fs: ''.join(indented(l, field_to_graph(l, f)) for f in fs)),
        section(1, query.order_by_fields, bool, lambda: "ORDER BY", lambda l, fs: ''.join(order_by_to_graph(l, f) for f in fs)),
        section(1, query.limit, lambda x: x is not None, lambda v: f"LIMIT {v}", lambda l, v: ""),
        section(1, query.offset, lambda x: x is not None, lambda v: f"OFFSET {v}", lambda l, v: "")
    ])

def select_graph(level: int, select: List[AslField]) -> str:
    return indented(level, "SELECT") + indented(level + 1, (field_to_graph(level + 1, s) for s in select))

def sq_to_graph(level: int, subquery: AslQuery, join: Optional[AslJoin]) -> str:
    from_structure = section(
        level + 1, subquery, lambda x: isinstance(x, AslStructureQuery),
        lambda sq: f"FROM {sq.type.name}",
        lambda l, sq: ""
    )
    
    from_encapsulating = section(
        level + 2, subquery, lambda x: isinstance(x, AslEncapsulatingQuery),
        lambda _: "FROM",
        lambda l, sq: indented(l, ''.join(sq_to_graph(l + 1, c[0], c[1]) for c in sq.children))
    )

    base = section(
        level + 1, subquery, lambda x: isinstance(x, AslDataQuery),
        lambda sq: f"BASE {sq.base.alias}",
        lambda l, sq: ""
    )

    join_str = (indented(level + 1, f"{join.join_type} {join.left.alias} -> {join.right.alias}")
                + section(level + 2, join.on, lambda x: bool(x), lambda _: "on", conditions_to_graph)
                if join else "")

    query_comment = ""
    if isinstance(subquery, AslPathDataQuery):
        query_comment = ''.join(p.attribute + p.predicate_or_operands for p in subquery.path_nodes(subquery.data_field))
        query_comment = f" -- {query_comment}"

    return (indented(level if level == 2 else 0, f"{subquery.alias}: {type_name(subquery)}{query_comment}")
            + select_graph(level + 1, subquery.select)
            + base
            + section(level + 1, subquery.condition, lambda x: x is not None, lambda _: "WHERE", condition_to_graph)
            + from_structure
            + from_encapsulating
            + section(level + 1, subquery.structure_conditions, bool, lambda _: "STRUCTURE CONDITIONS", lambda l, cs: ''.join(condition_to_graph(l + 2, c) for c in cs))
            + join_str)

def section(level: int, t, condition: Callable[[Optional[object]], bool], header: Callable[[], str], body: Callable[[int, object], str]) -> str:
    if not condition(t):
        return ""
    heading = header()
    heading_str = indented(level, heading) if heading else ""
    return heading_str + body(level + (1 if heading_str else 0), t)

def type_name(subquery: AslQuery) -> str:
    return subquery.__class__.__name__.lstrip('Asl')

def condition_to_graph(level: int, condition) -> str:
    if isinstance(condition, AslNotQueryCondition):
        return indented(level, "NOT") + condition_to_graph(level + 1, condition.condition)
    elif isinstance(condition, AslFieldValueQueryCondition):
        return indented(level, f"{field_to_graph(level + 1, condition.field)} {condition.operator} {condition.values}")
    elif isinstance(condition, AslFalseQueryCondition):
        return indented(level, "false")
    elif isinstance(condition, AslTrueQueryCondition):
        return indented(level, "true")
    elif isinstance(condition, AslOrQueryCondition):
        return indented(level, "OR") + ''.join(condition_to_graph(level + 1, op) for op in condition.operands)
    elif isinstance(condition, AslAndQueryCondition):
        return indented(level, "AND") + ''.join(condition_to_graph(level + 1, op) for op in condition.operands)
    elif isinstance(condition, AslNotNullQueryCondition):
        return indented(level, f"NOT_NULL {field_to_graph(level + 1, condition.field)}")
    elif isinstance(condition, AslEntityIdxOffsetCondition):
        return indented(level, f"EntityIdxOffset {condition.left_owner.alias} -{condition.offset}-> {condition.right_owner.alias}")
    elif isinstance(condition, AslDescendantCondition):
        return indented(level, f"DescendantCondition {condition.parent_relation} {condition.left_owner.alias} -> {condition.descendant_relation} {condition.right_owner.alias}")
    elif isinstance(condition, AslPathChildCondition):
        return indented(level, f"PathChildCondition {condition.parent_relation} {condition.left_owner.alias} -> {condition.child_relation} {condition.right_owner.alias}")
    else:
        return ""

def conditions_to_graph(level: int, join_conditions: List[AslJoinCondition]) -> str:
    return ''.join(
        (f"PathFilterJoinCondition {jc.left_owner.alias} ->\n{condition_to_graph(level + 2, jc.condition}"
         if isinstance(jc, AslPathFilterJoinCondition)
         else f"DelegatingJoinCondition {jc.left_owner.alias} ->\n{condition_to_graph(level + 2, jc.delegate}"
         if isinstance(jc, AslDelegatingJoinCondition)
         else f"AuditDetailsJoinCondition {jc.left_owner.alias} -> {jc.right_owner.alias}")
        for jc in join_conditions
    )

def order_by_to_graph(level: int, sort_order_pair: AslOrderByField) -> str:
    return f"{field_to_graph(level, sort_order_pair.field)} {sort_order_pair.direction}"

def field_to_graph(level: int, field: AslField) -> str:
    provider_alias = f"{field.internal_provider.alias}." if field.internal_provider else ""
    if isinstance(field, AslColumnField):
        return (f"{provider_alias}{field.aliased_name}"
                + (f" -- {field.extracted_column.path.render()}" if field.extracted_column else ""))
    elif isinstance(field, AslComplexExtractedColumnField):
        return (f"{provider_alias}??"
                + (f" -- COMPLEX {field.extracted_column.name} {field.extracted_column.path.render()}"
                   if field.extracted_column else ""))
    elif isinstance(field, AslAggregatingField):
        return f"{field.function}({('DISTINCT ' if field.is_distinct else '')}{field_to_graph(level, field.base_field) if field.base_field else '*'})"
    elif isinstance(field, AslSubqueryField):
        return (sq_to_graph(level + 1, field.base_query, None)
                + (f"Filter:\n{''.join(condition_to_graph(level + 2, c) for c in field.filter_conditions)}"
                   if field.filter_conditions else ""))
    elif isinstance(field, AslConstantField):
        return f"CONSTANT ({field.type.__name__}): {field.value}"
    else:
        return ""

def indented(level: int, string: str) -> str:
    prefix = '  ' * level
    return f"{prefix}{string}\n"

def indented(level: int, entries: iter, to_string: Callable[[object], str]) -> str:
    prefix = '  ' * level
    return ''.join(f"{prefix}{to_string(entry)}\n" for entry in entries)
