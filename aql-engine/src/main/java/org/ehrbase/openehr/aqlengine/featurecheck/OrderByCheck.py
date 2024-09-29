from typing import List, Optional
from abc import ABC, abstractmethod

class AqlFeatureNotImplementedException(Exception):
    pass

class SystemService:
    def get_system_id(self) -> str:
        pass

class AqlQuery:
    def get_order_by(self) -> Optional[List['OrderByExpression']]:
        pass

    def get_select(self) -> 'SelectExpression':
        pass

class OrderByExpression:
    def get_statement(self) -> 'IdentifiedPath':
        pass

class IdentifiedPath:
    def get_root(self) -> 'Root':
        pass

    def get_root_predicate(self) -> Optional['Predicate']:
        pass

    def get_path(self) -> 'Path':
        pass

class SelectExpression:
    def get_column_expression(self) -> IdentifiedPath:
        pass

class Root:
    def get_identifier(self) -> str:
        pass

class Path:
    def render(self) -> str:
        pass

class Predicate:
    pass

class FeatureCheckUtils:
    @staticmethod
    def starts_with(path: IdentifiedPath, other_path: IdentifiedPath) -> bool:
        pass

    @staticmethod
    def find_supported_identified_path(path: IdentifiedPath, flag: bool, clause_type: str, system_id: str) -> 'PathDetails':
        pass

class PathDetails:
    def extracted_column(self) -> 'AslExtractedColumn':
        pass

class AslExtractedColumn:
    OV_TIME_COMMITTED = 'OV_TIME_COMMITTED'
    AD_SYSTEM_ID = 'AD_SYSTEM_ID'
    AD_CHANGE_TYPE_TERMINOLOGY_ID_VALUE = 'AD_CHANGE_TYPE_TERMINOLOGY_ID_VALUE'

class OrderByCheck:
    def __init__(self, system_service: SystemService):
        self.system_service = system_service

    def ensure_supported(self, aql_query: AqlQuery):
        order_by_expressions = aql_query.get_order_by() or []
        for order_by in order_by_expressions:
            path = order_by.get_statement()
            self.ensure_order_by_statement_supported(aql_query, path)

    def ensure_order_by_statement_supported(self, aql_query: AqlQuery, ip: IdentifiedPath):
        select_expressions = aql_query.get_select().get_statement()
        if not any(
            isinstance(selected, IdentifiedPath) and FeatureCheckUtils.starts_with(selected, ip)
            for selected in select_expressions
        ):
            root_id = ip.get_root().get_identifier()
            root_predicate = ip.get_root_predicate()
            root_predicate_str = '' if root_predicate is None else self.render_predicate(root_predicate)
            path_str = ip.get_path().render()
            raise AqlFeatureNotImplementedException(
                f"ORDER BY: Path: {root_id}{root_predicate_str}/{path_str} is not present in SELECT statement"
            )

        path_details = FeatureCheckUtils.find_supported_identified_path(
            ip, False, 'ORDER_BY', self.system_service.get_system_id()
        )

        if path_details.extracted_column() in {
            AslExtractedColumn.OV_TIME_COMMITTED,
            AslExtractedColumn.AD_SYSTEM_ID,
            AslExtractedColumn.AD_CHANGE_TYPE_TERMINOLOGY_ID_VALUE
        }:
            raise AqlFeatureNotImplementedException(
                f"ORDER BY: Path: {ip.get_path().render()} on VERSION"
            )

    def render_predicate(self, predicate: Predicate) -> str:
        # Implement the method to convert Predicate to its string representation
        pass
