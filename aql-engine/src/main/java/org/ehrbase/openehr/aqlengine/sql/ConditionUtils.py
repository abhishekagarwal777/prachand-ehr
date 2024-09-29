import json
from typing import List, Optional, Union, Any
from sqlalchemy import and_, or_, not_, false, true, Table, Column, select

class ConditionUtils:
    @staticmethod
    def build_join_condition(asl_join, asl_query_to_table):
        sql_left = asl_query_to_table.get_data_table(asl_join.left)
        sql_right = asl_query_to_table.get_data_table(asl_join.right)

        conditions = []
        for jc in asl_join.on:
            if isinstance(jc, AslDelegatingJoinCondition):
                ConditionUtils.add_delegating_join_conditions(jc, conditions, sql_left, sql_right)
            elif isinstance(jc, AslPathFilterJoinCondition):
                conditions.append(ConditionUtils.build_condition(jc.condition, asl_query_to_table, True))
            elif isinstance(jc, AslAuditDetailsJoinCondition):
                conditions.append(
                    FieldUtils.field(sql_left, asl_join.left, jc.left_owner, 'audit_id', UUID, True)
                    .eq(FieldUtils.field(sql_right, asl_join.right, jc.right_owner, 'audit_id', UUID, True))
                )

        return and_(*conditions)

    @staticmethod
    def add_delegating_join_conditions(join_condition, conditions, sql_left, sql_right):
        if isinstance(join_condition.delegate, AslEntityIdxOffsetCondition):
            conditions.extend(ConditionUtils.entity_idx_offset_conditions(join_condition.delegate, sql_left, sql_right, True))
        elif isinstance(join_condition.delegate, AslDescendantCondition):
            conditions.extend(ConditionUtils.descendant_conditions(join_condition.delegate, sql_left, sql_right, True))
        elif isinstance(join_condition.delegate, AslPathChildCondition):
            conditions.extend(ConditionUtils.path_child_conditions(join_condition.delegate, sql_left, sql_right, True))

    @staticmethod
    def path_child_conditions(dc, sql_left, sql_right, is_join_condition):
        parent_relation = dc.parent_relation
        if parent_relation not in {AslSourceRelation.COMPOSITION, AslSourceRelation.EHR_STATUS}:
            raise ValueError(f"unexpected parent relation type {parent_relation}")
        if dc.child_relation not in {AslSourceRelation.COMPOSITION, AslSourceRelation.EHR_STATUS}:
            raise ValueError(f"unexpected descendant relation type {dc.child_relation}")

        p_key_field = 'vo_id' if parent_relation == AslSourceRelation.COMPOSITION else 'ehr_id'
        
        return [
            FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, p_key_field, UUID, True)
            .eq(FieldUtils.field(sql_right, dc.right_provider, dc.right_owner, p_key_field, UUID, is_join_condition)),
            FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, 'num', int, True)
            .eq(FieldUtils.field(sql_right, dc.right_provider, dc.right_owner, 'parent_num', int, is_join_condition))
        ]

    @staticmethod
    def entity_idx_offset_conditions(ic, sql_left, sql_right, is_join_condition):
        return [
            FieldUtils.field(sql_left, ic.left_provider, ic.left_owner, 'entity_idx_len', int, True)
            .add(ic.offset)
            .eq(FieldUtils.field(sql_right, ic.right_provider, ic.right_owner, 'entity_idx_len', int, is_join_condition))
        ]

    @staticmethod
    def descendant_conditions(dc, sql_left, sql_right, is_join_condition):
        parent_relation = dc.parent_relation
        if parent_relation not in {AslSourceRelation.COMPOSITION, AslSourceRelation.EHR_STATUS, AslSourceRelation.EHR}:
            raise ValueError(f"unexpected parent relation type {parent_relation}")
        if dc.descendant_relation not in {AslSourceRelation.COMPOSITION, AslSourceRelation.EHR_STATUS}:
            raise ValueError(f"unexpected descendant relation type {dc.descendant_relation}")

        if parent_relation == AslSourceRelation.EHR:
            return [
                FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, 'id', UUID, True)
                .eq(FieldUtils.field(sql_right, dc.right_provider, dc.right_owner, 'ehr_id', UUID, is_join_condition))
            ]
        else:
            p_key_field = 'vo_id' if parent_relation == AslSourceRelation.COMPOSITION else 'ehr_id'
            return [
                FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, p_key_field, UUID, True)
                .eq(FieldUtils.field(sql_right, dc.right_provider, dc.right_owner, p_key_field, UUID, is_join_condition)),
                FieldUtils.field(sql_right, dc.right_provider, dc.right_owner, 'num', int, True)
                .between(
                    FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, 'num', int, is_join_condition).add(1),
                    FieldUtils.field(sql_left, dc.left_provider, dc.left_owner, 'num_cap', int, is_join_condition)
                )
            ]

    @staticmethod
    def build_condition(condition, tables, use_aliases):
        if condition is None:
            return false()
        elif isinstance(condition, AslAndQueryCondition):
            return and_(*(ConditionUtils.build_condition(op, tables, use_aliases) for op in condition.operands))
        elif isinstance(condition, AslOrQueryCondition):
            return or_(*(ConditionUtils.build_condition(op, tables, use_aliases) for op in condition.operands))
        elif isinstance(condition, AslNotQueryCondition):
            return not_(ConditionUtils.build_condition(condition.condition, tables, use_aliases))
        elif isinstance(condition, AslFalseQueryCondition):
            return false()
        elif isinstance(condition, AslTrueQueryCondition):
            return true()
        elif isinstance(condition, AslNotNullQueryCondition):
            return ConditionUtils.not_null_condition(tables, use_aliases, condition)
        elif isinstance(condition, AslFieldValueQueryCondition):
            return ConditionUtils.build_field_value_condition(tables, use_aliases, condition)
        elif isinstance(condition, AslEntityIdxOffsetCondition):
            return and_(*ConditionUtils.entity_idx_offset_conditions(condition, tables.get_data_table(condition.left_provider), tables.get_data_table(condition.right_provider), False))
        elif isinstance(condition, AslDescendantCondition):
            return and_(*ConditionUtils.descendant_conditions(condition, tables.get_data_table(condition.left_provider), tables.get_version_table(condition.right_provider) if condition.parent_relation == AslSourceRelation.EHR else tables.get_data_table(condition.right_provider), False))
        elif isinstance(condition, AslPathChildCondition):
            return and_(*ConditionUtils.path_child_conditions(condition, tables.get_data_table(condition.left_provider), tables.get_version_table(condition.right_provider) if condition.parent_relation == AslSourceRelation.EHR else tables.get_data_table(condition.right_provider), False))

    @staticmethod
    def not_null_condition(tables, use_aliases, nn):
        field = nn.field
        if field.extracted_column is not None:
            return true()
        elif isinstance(field, AslColumnField):
            return tables.get_version_table(field.provider).field(field.name(use_aliases)).is_not_null() if field.is_version_table_field() else tables.get_data_table(field.provider).field(field.name(use_aliases)).is_not_null()
        else:
            raise ValueError(f"Unsupported field type: {type(field).__name__}")

    @staticmethod
    def build_field_value_condition(tables, use_aliases, fv):
        field = fv.field
        internal_provider = field.internal_provider
        if isinstance(fv, AslDvOrderedValueQueryCondition):
            sql_dv_ordered_field = FieldUtils.field(tables.get_data_table(internal_provider), field, JSONB, use_aliases)
            sql_magnitude_field = AdditionalSQLFunctions.jsonb_dv_ordered_magnitude(sql_dv_ordered_field)
            sql_type_field = select([sql_dv_ordered_field['type']])  # Adjust as needed
            types = [RmTypeAlias.get_alias(t) for t in fv.types_to_compare]
            return ConditionUtils.apply_operator(AslConditionOperator.IN, sql_type_field, types).and_(ConditionUtils.apply_operator(fv.operator, sql_magnitude_field, fv.values))

        if isinstance(field, AslComplexExtractedColumnField):
            return ConditionUtils.complex_extracted_column_condition(use_aliases, fv, field, tables.get_data_table(internal_provider), tables.get_version_table(internal_provider))
        elif isinstance(field, AslColumnField):
            return ConditionUtils.apply_operator(fv.operator, FieldUtils.field(tables.get_version_table(internal_provider) if field.is_version_table_field() else tables.get_data_table(internal_provider), field, use_aliases), fv.values)
        elif isinstance(field, AslConstantField):
            return ConditionUtils.apply_operator(fv.operator, json.dumps(fv.value), fv.values)
        elif isinstance(field, AslAggregatingField):
            raise ValueError("AslAggregatingField cannot be used in WHERE")
        elif isinstance(field, AslSubqueryField):
            raise ValueError("AslSubqueryField cannot be used in WHERE")

    @staticmethod
    def complex_extracted_column_condition(use_aliases, fv, ecf, data_table, version_table):
        if ecf.extracted_column == 'vo_id':
            op = AslConditionOperator.EQ if fv.operator == AslConditionOperator.IN else fv.operator
            return or_(*[ConditionUtils.vo_id_condition(version_table, use_aliases, id, op, ecf) for id in fv.values])
        elif ecf.extracted_column == 'archetype_node_id':
            op = AslConditionOperator.EQ if fv.operator == AslConditionOperator.IN else fv.operator
            return or_(*[ConditionUtils.archetype_node_id_condition(data_table, use_aliases, ecf, p, op) for p in fv.values])
        else:
            raise ValueError(f"Extracted column {ecf.extracted_column} is not complex")

    @staticmethod
    def archetype_node_id_condition(src, aliased_names, ecf, rm_type_and_concept, op):
        return and_(*[
            ConditionUtils.apply_operator(op, FieldUtils.field(src, ecf, 'rm_entity', aliased_names), [rm_type_and_concept.aliased_rm_type]),
            ConditionUtils.apply_operator(op, FieldUtils.field(src, ecf, 'entity_concept', aliased_names), [rm_type_and_concept.concept])
        ])

    @staticmethod
    def vo_id_condition(version_table, aliased_names, id, op, field):
        split = id.split("::")
        uuid_field = FieldUtils.field(version_table, field, 'vo_id', aliased_names)
        version_field = FieldUtils.field(version_table, field, 'sys_version', aliased_names)
        uuid = split[0]
        version = int(split[2]) if len(split) > 2 else None
        left = select([uuid_field, version_field]) if version is not None else uuid_field
        right = uuid if version is None else select([uuid, version])
        return {
            AslConditionOperator.IN: left.eq(right),
            AslConditionOperator.EQ: left.eq(right),
            AslConditionOperator.NEQ: left.ne(right),
            AslConditionOperator.LT: left.lt(right),
            AslConditionOperator.GT: left.gt(right),
            AslConditionOperator.GT_EQ: left.ge(right),
            AslConditionOperator.LT_EQ: left.le(right),
            AslConditionOperator.IS_NULL: uuid_field.is_null(),
            AslConditionOperator.IS_NOT_NULL: uuid_field.is_not_null(),
        }.get(op)

    @staticmethod
    def apply_operator(operator, field, values):
        if operator == AslConditionOperator.LIKE:
            like_pattern = values[0]
            return field.like(like_pattern)
        elif operator == AslConditionOperator.IS_NULL:
            return field.is_null()
        elif operator == AslConditionOperator.IS_NOT_NULL:
            return field.is_not_null()

        # Handle other operators...
        filtered_values = [v for v in values if v is not None]
        if len(filtered_values) == 0:
            return false() if operator in {AslConditionOperator.IN, AslConditionOperator.EQ} else true()
        elif len(filtered_values) == 1:
            val = filtered_values[0]
            return field.eq(val)  # Adjust for other operators as needed

        # Handle multiple values for IN, NEQ, etc.
        return field.in_(filtered_values)

# Note: This code is a simplified adaptation and may require additional context to function correctly.
