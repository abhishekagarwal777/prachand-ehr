import json
import logging
import re
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import RequestException

from aql_query_repository import AqlQueryRepository
from external_terminology_validation import ExternalTerminologyValidation
from aql_sql_layer import AqlSqlLayer
from aql_query_feature_check import AqlQueryFeatureCheck
from aql_query_context import AqlQueryContext
from aql_query_request import AqlQueryRequest
from aql_query import AqlQuery
from aql_query_parser import AqlQueryParser
from aql_renderer import AqlRenderer
from result_holder import ResultHolder
from query_result_dto import QueryResultDto
from containment_expression import ContainmentClassExpression, ContainmentSetOperator, ContainmentSetOperatorSymbol
from aql_util import AqlUtil
from aql_query_wrapper import AqlQueryWrapper, SelectWrapper, SelectType

logger = logging.getLogger(__name__)

class AqlQueryServiceImp:

    def __init__(self, 
                 aql_query_repository: AqlQueryRepository,
                 ts_adapter: ExternalTerminologyValidation,
                 aql_sql_layer: AqlSqlLayer,
                 aql_query_feature_check: AqlQueryFeatureCheck,
                 object_mapper: json.JSONDecoder,
                 aql_query_context: AqlQueryContext,
                 default_limit: Optional[int] = None,
                 max_limit: Optional[int] = None,
                 max_fetch: Optional[int] = None,
                 fetch_precedence: str = 'REJECT'):
        self.aql_query_repository = aql_query_repository
        self.ts_adapter = ts_adapter
        self.aql_sql_layer = aql_sql_layer
        self.aql_query_feature_check = aql_query_feature_check
        self.object_mapper = object_mapper
        self.aql_query_context = aql_query_context
        self.default_limit = default_limit
        self.max_limit = max_limit
        self.max_fetch = max_fetch
        self.fetch_precedence = fetch_precedence

    def query(self, aql_query_request: AqlQueryRequest) -> QueryResultDto:
        return self.query_aql(aql_query_request)

    def query_aql(self, aql_query_request: AqlQueryRequest) -> QueryResultDto:
        if self.default_limit is not None:
            self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_DEFAULT_LIMIT, self.default_limit)
        if self.max_limit is not None:
            self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_MAX_LIMIT, self.max_limit)
        if self.max_fetch is not None:
            self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_MAX_FETCH, self.max_fetch)

        try:
            aql_query = self.build_aql_query(aql_query_request)

            self.aql_query_feature_check.ensure_query_supported(aql_query)

            if logger.isEnabledFor(logging.TRACE):
                logger.trace(self.object_mapper.dumps(aql_query))

            query_wrapper = AqlQueryWrapper.create(aql_query)
            asl_query = self.aql_sql_layer.build_asl_root_query(query_wrapper)
            non_primitive_selects = query_wrapper.non_primitive_selects()

            prepared_query = self.aql_query_repository.prepare_query(asl_query, non_primitive_selects)

            if self.aql_query_context.show_executed_sql():
                self.aql_query_context.set_meta_property(
                    AqlQueryContext.EHRBASE_META_PROPERTY_EXECUTED_SQL,
                    self.aql_query_repository.get_query_sql(prepared_query)
                )
            if self.aql_query_context.show_query_plan():
                analyze = not self.aql_query_context.is_dry_run()
                explained_query = self.aql_query_repository.explain_query(analyze, prepared_query)
                self.aql_query_context.set_meta_property(
                    AqlQueryContext.EHRBASE_META_PROPERTY_QUERY_PLAN,
                    self.object_mapper.loads(explained_query)
                )

            if self.aql_query_context.show_executed_aql():
                self.aql_query_context.set_executed_aql(AqlRenderer.render(aql_query))

            limit = query_wrapper.limit()
            if limit is not None:
                self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_FETCH, limit)
                offset = query_wrapper.offset() or 0
                self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_OFFSET, offset)

            if self.aql_query_context.is_dry_run():
                result_data = []
            else:
                result_data = self.execute_query(prepared_query, query_wrapper, non_primitive_selects)
                self.aql_query_context.set_meta_property(AqlQueryContext.EHRBASE_META_PROPERTY_RESULT_SIZE, len(result_data))

            return self.format_result(query_wrapper.selects(), result_data)

        except (ValueError, json.JSONDecodeError) as e:
            raise InternalServerError(str(e)) from e
        except RequestException as e:
            raise BadGatewayError(f"Bad gateway: {str(e)}") from e
        except SQLAlchemyError as e:
            raise InternalServerError(f"Data Access Error: {str(e)}") from e
        except AqlParseException as e:
            raise IllegalAqlException(f"Could not parse AQL query: {str(e)}") from e

    def build_aql_query(self, aql_query_request: AqlQueryRequest) -> AqlQuery:
        aql_query = AqlQueryParser.parse(aql_query_request.query_string())

        fetch_param = aql_query_request.fetch
        offset_param = aql_query_request.offset

        query_limit = aql_query.limit
        query_offset = aql_query.offset

        if query_limit and self.max_limit and query_limit > self.max_limit:
            raise UnprocessableEntityException(f"Query LIMIT {query_limit} exceeds maximum limit {self.max_limit}")

        if fetch_param and self.max_fetch and fetch_param > self.max_fetch:
            raise UnprocessableEntityException(f"Fetch parameter {fetch_param} exceeds maximum fetch {self.max_fetch}")

        limit = self.apply_fetch_precedence(query_limit, query_offset, fetch_param, offset_param)

        aql_query.limit = limit or self.default_limit
        aql_query.offset = offset_param or query_offset

        AqlParameterReplacement.replace_parameters(aql_query, aql_query_request.parameters)
        self.replace_ehr_paths(aql_query)

        return aql_query

    def apply_fetch_precedence(self, query_limit: Optional[int], query_offset: Optional[int], fetch_param: Optional[int], offset_param: Optional[int]) -> Optional[int]:
        if fetch_param is None:
            if offset_param is not None:
                raise UnprocessableEntityException("Query parameter for offset provided, but no fetch parameter")
            return query_limit
        elif query_limit is None:
            assert offset_param is None
            return fetch_param

        if self.fetch_precedence == 'REJECT':
            raise UnprocessableEntityException(f"Query contains a LIMIT clause, fetch and offset parameters must not be used (with fetch precedence {self.fetch_precedence})")
        elif self.fetch_precedence == 'MIN_FETCH':
            if query_offset is not None:
                raise UnprocessableEntityException(f"Query contains an OFFSET clause, fetch parameter must not be used (with fetch precedence {self.fetch_precedence})")
            return min(query_limit, fetch_param)

    def execute_query(self, prepared_query, query_wrapper, non_primitive_selects: List[SelectWrapper]) -> List[List[object]]:
        result_data = self.aql_query_repository.execute_query(prepared_query)

        if not non_primitive_selects:
            result_data = [[None] * len(result_data[0])] * int(result_data[0][0])

        selects = query_wrapper.selects()
        for i, sd in enumerate(selects):
            if sd.type == SelectType.PRIMITIVE:
                value = sd.primitive.value
                for row in result_data:
                    row.insert(i, value)
        return result_data

    def format_result(self, select_fields: List[SelectWrapper], result_data: List[List[object]]) -> QueryResultDto:
        columns = {sf.select_alias or f"#{i}": sf.select_path or None for i, sf in enumerate(select_fields)}

        dto = QueryResultDto()
        dto.variables = columns

        result_list = [ResultHolder({sf.select_alias or f"#{i}": row[i] for i, sf in enumerate(select_fields)})
                       for row in result_data]

        dto.result_set = result_list
        return dto

    def replace_ehr_paths(self, aql_query: AqlQuery):
        self.replace_ehr_path(aql_query, "compositions", "COMPOSITION", "c")
        self.replace_ehr_path(aql_query, "ehr_status", "EHR_STATUS", "s")

    def replace_ehr_path(self, aql_query: AqlQuery, ehr_path: str, type: str, alias_prefix: str):
        ehr_paths = [
            ip for ip in AqlQueryUtils.all_identified_paths(aql_query)
            if isinstance(ip.root, ContainmentClassExpression) and ip.root.type == RmConstants.EHR
            and ip.path.path_nodes[0].attribute == ehr_path
        ]

        if not ehr_paths:
            return

        if len(set(ip.root.identifier for ip in ehr_paths)) > 1:
            raise InternalServerError(f"More than one type of EHR paths found")

        path_nodes = ehr_paths[0].path.path_nodes

        root = path_nodes[0]
        if root.attribute == ehr_path:
            replacement_path = f"{alias_prefix}/{path_nodes[1].attribute}"
            aql_query.replace_path(ehr_paths[0], replacement_path)
            aql_query.add_criteria(
                ContainmentClassExpression(
                    RmConstants.EHR, alias_prefix, ContainmentSetOperatorSymbol.EQ, ContainmentSetOperator.EQUAL
                )
            )

