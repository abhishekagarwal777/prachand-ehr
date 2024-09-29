from typing import List, Union
from abc import ABC, abstractmethod

class AqlFeatureNotImplementedException(Exception):
    pass

class IllegalAqlException(Exception):
    pass

class SystemService:
    def get_system_id(self) -> str:
        pass

class AqlQuery:
    def get_select(self) -> 'SelectExpression':
        pass

class SelectExpression:
    def get_statement(self) -> List['SelectExpressionItem']:
        pass

class SelectExpressionItem(ABC):
    @abstractmethod
    def get_column_expression(self) -> Union['IdentifiedPath', 'AggregateFunction', 'Primitive']:
        pass

class IdentifiedPath:
    def get_root(self) -> 'AbstractContainmentExpression':
        pass

    def get_path(self) -> 'Path':
        pass

class Path:
    def render(self) -> str:
        pass

class AggregateFunction(ABC):
    class AggregateFunctionName:
        COUNT = 'COUNT'
        AVG = 'AVG'
        SUM = 'SUM'
        MAX = 'MAX'
        MIN = 'MIN'

    def get_function_name(self) -> str:
        pass

    def get_identified_path(self) -> Optional[IdentifiedPath]:
        pass

class CountDistinctAggregateFunction(AggregateFunction):
    pass

class Primitive:
    pass

class AbstractContainmentExpression:
    def get_identifier(self) -> str:
        pass

class FeatureCheckUtils:
    @staticmethod
    def find_supported_identified_path(path: IdentifiedPath, flag: bool, clause_type: str, system_id: str) -> 'PathDetails':
        pass

class PathDetails:
    def extracted_column(self) -> 'AslExtractedColumn':
        pass

    def targets_dv_ordered(self) -> bool:
        pass

    def targets_primitive(self) -> bool:
        pass

class AslExtractedColumn:
    OV_TIME_COMMITTED = 'OV_TIME_COMMITTED'
    OV_TIME_COMMITTED_DV = 'OV_TIME_COMMITTED_DV'
    EHR_TIME_CREATED = 'EHR_TIME_CREATED'
    EHR_TIME_CREATED_DV = 'EHR_TIME_CREATED_DV'

class ClauseType:
    SELECT = 'SELECT'

class SelectCheck:
    def __init__(self, system_service: SystemService):
        self.system_service = system_service

    def ensure_supported(self, aql_query: AqlQuery):
        select = aql_query.get_select()
        for select_exp in select.get_statement():
            column_expr = select_exp.get_column_expression()
            if isinstance(column_expr, IdentifiedPath):
                self.ensure_select_path_supported(column_expr)
            elif isinstance(column_expr, AggregateFunction):
                self.ensure_aggregate_function_supported(column_expr)
            elif isinstance(column_expr, Primitive):
                # Primitives are allowed
                pass
            else:
                raise AqlFeatureNotImplementedException(
                    f"{select_exp.__class__.__name__} is not supported in SELECT"
                )

    def ensure_aggregate_function_supported(self, af: AggregateFunction):
        func = af.get_function_name()
        ip = af.get_identified_path()
        
        if ip is None:
            if func != AggregateFunction.AggregateFunctionName.COUNT:
                raise IllegalAqlException(
                    f"Aggregate function {func} requires an identified path argument."
                )
            elif isinstance(af, CountDistinctAggregateFunction):
                raise IllegalAqlException("COUNT(DISTINCT) requires an identified path argument")
        else:
            containment = ip.get_root()
            path_with_type = FeatureCheckUtils.find_supported_identified_path(
                ip, True, ClauseType.SELECT, self.system_service.get_system_id()
            )
            
            if func != AggregateFunction.AggregateFunctionName.COUNT:
                if path_with_type.extracted_column() and path_with_type.extracted_column() in {
                    AslExtractedColumn.OV_TIME_COMMITTED,
                    AslExtractedColumn.OV_TIME_COMMITTED_DV,
                    AslExtractedColumn.EHR_TIME_CREATED,
                    AslExtractedColumn.EHR_TIME_CREATED_DV
                }:
                    raise AqlFeatureNotImplementedException(
                        f"SELECT: Aggregate function {func} is not supported for path {containment.get_identifier()}/{ip.get_path().render()} (COUNT only)"
                    )
                
                if func in {AggregateFunction.AggregateFunctionName.AVG, AggregateFunction.AggregateFunctionName.SUM}:
                    if path_with_type.extracted_column() in {
                        AslExtractedColumn.OV_TIME_COMMITTED,
                        AslExtractedColumn.OV_TIME_COMMITTED_DV,
                        AslExtractedColumn.EHR_TIME_CREATED,
                        AslExtractedColumn.EHR_TIME_CREATED_DV
                    }:
                        raise AqlFeatureNotImplementedException(
                            f"SELECT: Aggregate function {func}({containment.get_identifier()}/{ip.get_path().render()}) not applicable to the given path"
                        )
                    if path_with_type.targets_dv_ordered():
                        raise AqlFeatureNotImplementedException(
                            f"SELECT: Aggregate function {func}({containment.get_identifier()}/{ip.get_path().render()}) not applicable to paths targeting subtypes of DV_ORDERED"
                        )
                    if not path_with_type.targets_primitive():
                        raise AqlFeatureNotImplementedException(
                            f"SELECT: Aggregate function {func}({containment.get_identifier()}/{ip.get_path().render()}) only applicable to paths targeting primitive types"
                        )
                elif func in {AggregateFunction.AggregateFunctionName.MAX, AggregateFunction.AggregateFunctionName.MIN}:
                    if not (path_with_type.targets_primitive() or path_with_type.targets_dv_ordered()):
                        raise AqlFeatureNotImplementedException(
                            f"SELECT: Aggregate function {func}({containment.get_identifier()}/{ip.get_path().render()}) only applicable to paths targeting primitive types or subtypes of DV_ORDERED"
                        )

    def ensure_select_path_supported(self, ip: IdentifiedPath):
        FeatureCheckUtils.find_supported_identified_path(ip, True, ClauseType.SELECT, self.system_service.get_system_id())
