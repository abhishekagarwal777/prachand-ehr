import pytest
from your_module import AqlQueryServiceImp, AqlQueryParser, AqlQueryRequest, UnprocessableEntityException
from typing import Optional, Dict

def replace_ehr_paths(aql_query):
    # Replace with actual implementation of replaceEhrPaths
    AqlQueryServiceImp.replace_ehr_paths(aql_query)

def build_aql_query(request: AqlQueryRequest, fetch_precedence, default_limit: Optional[int], max_limit: Optional[int], max_fetch: Optional[int]):
    # Replace with actual implementation of buildAqlQuery
    AqlQueryServiceImp.build_aql_query(request, fetch_precedence, default_limit, max_limit, max_fetch)

def parse_long(long_str: str) -> Optional[int]:
    return int(long_str) if long_str and long_str.strip() else None

@pytest.mark.parametrize("src_aql, expected_aql", [
    ("SELECT e/ehr_status AS s FROM EHR e", "SELECT s AS s FROM EHR e CONTAINS EHR_STATUS s"),
    ("SELECT s/uid/value, e/ehr_status/subject/external_ref/id FROM EHR e CONTAINS COMPOSITION s WHERE e/ehr_status/is_modifiable = true", "SELECT s/uid/value, s1/subject/external_ref/id FROM EHR e CONTAINS (EHR_STATUS s1 AND COMPOSITION s) WHERE s1/is_modifiable = true"),
])
def test_resolve_ehr_status(src_aql, expected_aql):
    aql_query = AqlQueryParser.parse(src_aql)
    replace_ehr_paths(aql_query)
    assert aql_query.render().replace('  ', ' ') == expected_aql.replace('  ', ' ')

@pytest.mark.parametrize("src_aql, expected_aql", [
    ("SELECT e/compositions AS c FROM EHR e", "SELECT c AS c FROM EHR e CONTAINS COMPOSITION c"),
    ("SELECT c/uid/value, e/compositions/uid/value FROM EHR e CONTAINS COMPOSITION c WHERE e/compositions/archetype_details/template_id/value = 'tpl.v0'", "SELECT c/uid/value, c1/uid/value FROM EHR e CONTAINS (COMPOSITION c1 AND COMPOSITION c) WHERE c1/archetype_details/template_id/value = 'tpl.v0'"),
])
def test_resolve_ehr_compositions(src_aql, expected_aql):
    aql_query = AqlQueryParser.parse(src_aql)
    replace_ehr_paths(aql_query)
    assert aql_query.render().replace('  ', ' ') == expected_aql.replace('  ', ' ')

@pytest.mark.parametrize("aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch, message", [
    ("5", "", "10", "", "REJECT", "", "", "Query contains a LIMIT clause, fetch and offset parameters must not be used (with fetch precedence REJECT)"),
    ("5", "20", "40", "", "REJECT", "", "", "Query parameter for offset provided, but no fetch parameter"),
    ("5", "20", "40", "", "MIN_FETCH", "", "", "Query parameter for offset provided, but no fetch parameter"),
    ("5", "", "30", "", "REJECT", "", "", "Query parameter for offset provided, but no fetch parameter"),
    ("", "", "42", "", "REJECT", "", "", "Query parameter for offset provided, but no fetch parameter"),
    ("20", "", "", "", "REJECT", "19", "", "Query LIMIT 20 exceeds maximum limit 19"),
    ("20", "", "", "", "MIN_FETCH", "19", "", "Query LIMIT 20 exceeds maximum limit 19"),
    ("", "20", "", "", "REJECT", "", "19", "Fetch parameter 20 exceeds maximum fetch 19"),
    ("", "20", "", "", "MIN_FETCH", "", "19", "Fetch parameter 20 exceeds maximum fetch 19"),
    ("20", "5", "30", "", "MIN_FETCH", "", "", "Query contains an OFFSET clause, fetch parameter must not be used (with fetch precedence MIN_FETCH)"),
])
def test_query_offset_limit_rejected(aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch, message):
    with pytest.raises(UnprocessableEntityException, match=message):
        run_query_test(aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch)

@pytest.mark.parametrize("aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch", [
    ("", "", "", "", "REJECT", "", "", ""),
    ("5", "", "", "", "REJECT", "", "", ""),
    ("5", "15", "", "", "REJECT", "", "", ""),
    ("", "20", "", "", "REJECT", "", "", ""),
    ("", "20", "25", "", "REJECT", "", "", ""),
    ("", "", "", "REJECT", "", "20", "10", "10"),
    ("20", "30", "", "", "REJECT", "20", "20", "20"),
    ("", "20", "50", "", "REJECT", "20", "20", "20"),
    ("30", "", "20", "50", "MIN_FETCH", "30", "30", "20"),
    ("10", "", "20", "50", "MIN_FETCH", "30", "30", "20"),
])
def test_query_offset_limit_accepted(aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch):
    run_query_test(aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch)

def run_query_test(aql_limit, aql_offset, param_limit, param_offset, fetch_precedence, default_limit, max_limit, max_fetch):
    query = f"SELECT s FROM EHR_STATUS s {'LIMIT ' + aql_limit if aql_limit else ''} {'OFFSET ' + aql_offset if aql_offset else ''}".strip()

    build_aql_query(
        AqlQueryRequest(
            query,
            {},
            parse_long(param_limit),
            parse_long(param_offset)
        ),
        fetch_precedence,
        parse_long(default_limit),
        parse_long(max_limit),
        parse_long(max_fetch)
    )
