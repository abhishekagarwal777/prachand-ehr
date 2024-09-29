from typing import Union, List
from abc import ABC, abstractmethod

class AqlFeatureNotImplementedException(Exception):
    pass

class IllegalAqlException(Exception):
    pass

class SystemService:
    def get_system_id(self) -> str:
        pass

class AqlQuery:
    def get_where(self) -> 'WhereCondition':
        pass

class WhereCondition(ABC):
    pass

class ComparisonOperatorCondition(WhereCondition):
    def get_statement(self) -> 'ComparisonLeftOperand':
        pass

    def get_symbol(self) -> 'ComparisonOperatorSymbol':
        pass

class LikeCondition(WhereCondition):
    def get_statement(self) -> 'AqlObjectPath':
        pass

    def get_value(self) -> 'LikeOperand':
        pass

class MatchesCondition(WhereCondition):
    def get_statement(self) -> 'IdentifiedPath':
        pass

    def get_values(self) -> List['LikeOperand']:
        pass

class ExistsCondition(WhereCondition):
    def get_value(self) -> 'IdentifiedPath':
        pass

class ComparisonLeftOperand(ABC):
    pass

class IdentifiedPath(ComparisonLeftOperand):
    def get_path(self) -> 'Path':
        pass

    def get_root(self) -> 'AbstractContainmentExpression':
        pass

class LikeOperand(ABC):
    pass

class Primitive(LikeOperand):
    def get_value(self) -> object:
        pass

class Path(ABC):
    def render(self) -> str:
        pass

class ComparisonOperatorSymbol:
    EQ = 'EQ'
    NEQ = 'NEQ'

class FeatureCheckUtils:
    @staticmethod
    def find_supported_identified_path(path: IdentifiedPath, flag: bool, clause_type: str, system_id: str) -> 'PathDetails':
        pass

    @staticmethod
    def ensure_operand_supported(path_with_type: 'PathDetails', operand: LikeOperand, system_id: str):
        pass

class PathDetails:
    def extracted_column(self) -> 'AslExtractedColumn':
        pass

class AslExtractedColumn:
    ARCHETYPE_NODE_ID = 'ARCHETYPE_NODE_ID'
    TEMPLATE_ID = 'TEMPLATE_ID'
    OV_TIME_COMMITTED = 'OV_TIME_COMMITTED'
    AD_CHANGE_TYPE_VALUE = 'AD_CHANGE_TYPE_VALUE'
    AD_CHANGE_TYPE_CODE_STRING = 'AD_CHANGE_TYPE_CODE_STRING'
    AD_CHANGE_TYPE_PREFERRED_TERM = 'AD_CHANGE_TYPE_PREFERRED_TERM'
    VO_ID = 'VO_ID'

    def get_path(self) -> Path:
        pass

class AqlObjectPath:
    def get_path(self) -> Path:
        pass

class ClauseType:
    WHERE = 'WHERE'

class WhereCheck:
    def __init__(self, system_service: SystemService):
        self.system_service = system_service

    def ensure_supported(self, aql_query: AqlQuery):
        where = aql_query.get_where()
        conditions = AqlQueryUtils.stream_where_conditions(where)
        for condition in conditions:
            if isinstance(condition, ComparisonOperatorCondition):
                self.ensure_where_comparison_condition_supported(condition)
            elif isinstance(condition, LikeCondition):
                self.ensure_like_condition_supported(condition)
            elif isinstance(condition, MatchesCondition):
                self.ensure_matches_condition_supported(condition)
            elif isinstance(condition, ExistsCondition):
                self.ensure_exists_condition_supported(condition)
            else:
                raise IllegalAqlException(f"Unexpected condition type {condition.__class__.__name__}")

    def ensure_where_comparison_condition_supported(self, condition: ComparisonOperatorCondition):
        condition_statement = condition.get_statement()

        if isinstance(condition_statement, IdentifiedPath):
            condition_field = condition_statement
            path_with_type = FeatureCheckUtils.find_supported_identified_path(
                condition_field, False, ClauseType.WHERE, self.system_service.get_system_id()
            )
            if (condition_field.get_path() == AslExtractedColumn.ARCHETYPE_NODE_ID.get_path() and
                condition.get_symbol() not in {ComparisonOperatorSymbol.EQ, ComparisonOperatorSymbol.NEQ}):
                raise AqlFeatureNotImplementedException(
                    "Conditions on 'archetype_node_id' only support =,!=, LIKE and MATCHES"
                )
            if (condition_field.get_path() == AslExtractedColumn.TEMPLATE_ID.get_path() and
                condition.get_symbol() not in {ComparisonOperatorSymbol.EQ, ComparisonOperatorSymbol.NEQ}):
                raise AqlFeatureNotImplementedException(
                    "Conditions on 'archetype_details/template_id/value' only support =,!= and MATCHES"
                )
            if path_with_type.extracted_column() == AslExtractedColumn.OV_TIME_COMMITTED:
                raise AqlFeatureNotImplementedException(f"Conditions on {condition_field.get_path().render()} of VERSION")
            if (path_with_type.extracted_column() in {
                AslExtractedColumn.AD_CHANGE_TYPE_VALUE,
                AslExtractedColumn.AD_CHANGE_TYPE_CODE_STRING,
                AslExtractedColumn.AD_CHANGE_TYPE_PREFERRED_TERM
            } and condition.get_symbol() not in {ComparisonOperatorSymbol.EQ, ComparisonOperatorSymbol.NEQ}):
                raise AqlFeatureNotImplementedException(
                    f"Conditions on {condition_field.get_path().render()} of VERSION only support =,!= and MATCHES"
                )
            FeatureCheckUtils.ensure_operand_supported(path_with_type, condition.get_value(), self.system_service.get_system_id())
        else:
            raise AqlFeatureNotImplementedException("Functions are not supported in WHERE")

    @staticmethod
    def ensure_exists_condition_supported(exists: ExistsCondition):
        raise AqlFeatureNotImplementedException("WHERE: EXISTS operator is not supported")

    def ensure_matches_condition_supported(self, matches: MatchesCondition):
        path_with_type = FeatureCheckUtils.find_supported_identified_path(
            matches.get_statement(), False, ClauseType.WHERE, self.system_service.get_system_id()
        )
        for operand in matches.get_values():
            FeatureCheckUtils.ensure_operand_supported(path_with_type, operand, self.system_service.get_system_id())

    def ensure_like_condition_supported(self, like: LikeCondition):
        path = like.get_statement().get_path()
        FeatureCheckUtils.find_supported_identified_path(
            like.get_statement(), False, ClauseType.WHERE, self.system_service.get_system_id()
        )
        operand = like.get_value()
        if path == AslExtractedColumn.VO_ID.get_path():
            raise AqlFeatureNotImplementedException("LIKE on /uid/value is not supported")
        if not isinstance(operand, Primitive):
            raise AqlFeatureNotImplementedException("Only primitive operands are supported")
        value = operand.get_value()
        if not isinstance(value, str):
            raise AqlFeatureNotImplementedException("LIKE must use String values")
        if (path == AslExtractedColumn.ARCHETYPE_NODE_ID.get_path() and
            not value.startswith("openEHR-EHR-")):
            raise AqlFeatureNotImplementedException(
                "LIKE on archetype_node_id has to start with 'openEHR-EHR-{RM-TYPE}.'"
            )
        if path == AslExtractedColumn.TEMPLATE_ID.get_path():
            raise AqlFeatureNotImplementedException(
                "Conditions on 'archetype_details/template_id/value' only support =,!= and MATCHES"
            )
