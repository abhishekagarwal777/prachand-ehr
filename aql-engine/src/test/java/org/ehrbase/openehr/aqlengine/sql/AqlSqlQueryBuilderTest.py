import pytest
from unittest.mock import Mock, patch
from your_module import (
    AqlQueryServiceImp, AqlQueryParser, AqlQueryWrapper, AqlSqlLayer, AqlSqlQueryBuilder,
    AslRootQuery, PathInfo, KnowledgeCacheService, UnprocessableEntityException
)
from sqlalchemy.sql import text
from sqlalchemy import create_engine, MetaData

@pytest.fixture
def mock_knowledge_cache_service():
    service = Mock(spec=KnowledgeCacheService)
    service.find_uuid_by_template_id.return_value = UUID('12345678-1234-5678-1234-567812345678')  # Example UUID
    return service

def test_print_sql_query(mock_knowledge_cache_service):
    aql_query = AqlQueryParser.parse("""
    SELECT
    c/content,
    c/content[at0001],
    c/content[at0002],
    c/uid/value,
    c/context/other_context[at0004]/items[at0014]/value
    FROM EHR e CONTAINS COMPOSITION c
    WHERE e/ehr_id/value = 'e6fad8ba-fb4f-46a2-bf82-66edb43f142f'
    """)

    print("/*")
    print(aql_query.render())
    print("*/")

    query_wrapper = AqlQueryWrapper.create(aql_query)
    aql_sql_layer = AqlSqlLayer(mock_knowledge_cache_service, lambda: "node")
    asl_query = aql_sql_layer.build_asl_root_query(query_wrapper)

    print("/*")
    print(AslGraph.create_asl_graph(asl_query))
    print("*/")
    print()

    sql_query_builder = AqlSqlQueryBuilder(create_engine('postgresql://user:pass@localhost/db'), mock_knowledge_cache_service, None)
    sql_query = sql_query_builder.build_sql_query(asl_query)
    print(sql_query)

@pytest.mark.parametrize("aql", [
    """
    SELECT o/data/events/data/items/value/magnitude
    FROM OBSERVATION o [openEHR-EHR-OBSERVATION.conformance_observation.v0]
    WHERE o/data[at0001]/events[at0002]/data[at0003]/items[at0008]/value = 82.0
    """
])
def test_can_build_sql_query(aql, mock_knowledge_cache_service):
    aql_query = AqlQueryParser.parse(aql)
    query_wrapper = AqlQueryWrapper.create(aql_query)
    aql_sql_layer = AqlSqlLayer(mock_knowledge_cache_service, lambda: "node")
    asl_query = aql_sql_layer.build_asl_root_query(query_wrapper)
    sql_query_builder = AqlSqlQueryBuilder(create_engine('postgresql://user:pass@localhost/db'), mock_knowledge_cache_service, None)

    assert sql_query_builder.build_sql_query(asl_query) is not None

def test_data_query(mock_knowledge_cache_service):
    aql_query = AqlQueryParser.parse("""
    SELECT
    c/content,
    c/content[at0001],
    c/content[at0002],
    c/uid/value,
    c/context/other_context[at0004]/items[at0014]/value
    FROM EHR e CONTAINS COMPOSITION c
    WHERE e/ehr_id/value = 'e6fad8ba-fb4f-46a2-bf82-66edb43f142f'
    """)
    query_wrapper = AqlQueryWrapper.create(aql_query)

    assert build_sql_query(query_wrapper) is not None

def test_cluster_with_data_multiplicity_select_single(mock_knowledge_cache_service):
    aql_query = AqlQueryParser.parse("""
    SELECT
        cluster/items[at0001]/value/data
    FROM COMPOSITION CONTAINS CLUSTER cluster[openEHR-EHR-CLUSTER.media_file.v1]
    """)
    query_wrapper = AqlQueryWrapper.create(aql_query)

    assert len(query_wrapper.path_infos()) == 1
    path_info = next(iter(query_wrapper.path_infos().values()), None)
    assert path_info is not None

    cohesion_tree_root = path_info.get_cohesion_tree_root()
    assert not path_info.is_multiple_valued(cohesion_tree_root)

    # Ensure generated query does not try to perform jsonb array selection
    select_query = build_sql_query(query_wrapper)
    assert "select jsonb_array_elements(" not in str(select_query)

def build_sql_query(query_wrapper):
    aql_sql_layer = AqlSqlLayer(Mock(spec=KnowledgeCacheService), lambda: "node")
    asl_query = aql_sql_layer.build_asl_root_query(query_wrapper)
    sql_query_builder = AqlSqlQueryBuilder(create_engine('postgresql://user:pass@localhost/db'), Mock(spec=KnowledgeCacheService), None)
    return sql_query_builder.build_sql_query(asl_query)
