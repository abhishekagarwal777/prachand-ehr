import pytest
from your_module import AqlQuery, AqlQueryParser, AqlQueryFeatureCheck, AqlFeatureNotImplementedException, IllegalAqlException

class TestAqlQueryFeatureCheck:

    @pytest.mark.parametrize("aql", [
        "SELECT s FROM EHR e CONTAINS EHR_STATUS s",
        "SELECT e/ehr_id/value FROM EHR e CONTAINS COMPOSITION LIMIT 10 OFFSET 20",
        "SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea'] CONTAINS COMPOSITION c",
        "SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea'] CONTAINS COMPOSITION c CONTAINS OBSERVATION",
        """
            SELECT c, it from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c CONTAINS OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]
            CONTAINS ITEM_TREE it""",
        """
            SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c
            CONTAINS OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]""",
        """
           SELECT e/ehr_id/value,
               c/uid/value, c/name/value, c/archetype_node_id, c/archetype_details/template_id/value,
               o/name/value, o/archetype_node_id
           FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION o""",
        """
            SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c
            CONTAINS OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1]""",
        """
            SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c
            CONTAINS OBSERVATION[name/value='Blood pressure (Training sample)']""",
        """
            SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c[openEHR-EHR-COMPOSITION.sample_blood_pressure.v1,'Blood pressure (Training sample)']
            CONTAINS OBSERVATION[openEHR-EHR-OBSERVATION.sample_blood_pressure.v1,'Blood pressure (Training sample)']""",
        """
            SELECT c from EHR [ehr_id/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea' OR ehr_id/value!='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS COMPOSITION c[name/value!='Blood pressure (Training sample)' AND archetype_node_id='openEHR-EHR-COMPOSITION.sample_blood_pressure.v1' OR uid/value='b037bf7c-0ecb-40fb-aada-fc7d559815ea']
            CONTAINS OBSERVATION[name/value!='Blood pressure (Training sample)' AND archetype_node_id='openEHR-EHR-COMPOSITION.sample_blood_pressure.v1' OR name/value!='Blood pressure (Training sample)']""",
        """
           SELECT o
           FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION o
           WHERE e/ehr_id/value MATCHES {'b037bf7c-0ecb-40fb-aada-fc7d559815ea'}
             AND (o/archetype_node_id LIKE 'openEHR-EHR-OBSERVATION.sample_blood_pressure.*'
               OR o/name/value = 'Blood pressure (Training sample)')
             AND c/uid/value != 'b037bf7c-0ecb-40fb-aada-fc7d559815ea'
             AND c/archetype_details/template_id/value = 'some-template.v1'""",
        """
           SELECT e/ehr_id/value, c1, c2, o, ev, a
           FROM EHR e CONTAINS(
           (COMPOSITION c1
             CONTAINS OBSERVATION o
             AND EVALUATION ev)
           AND COMPOSITION c2 CONTAINS ADMIN_ENTRY a)""",
        """
           SELECT e/ehr_id/value, c1/content/name/value, c1/content/data/name/value, o, ev
           FROM EHR e CONTAINS
           COMPOSITION c1
             CONTAINS OBSERVATION o
             CONTAINS EVALUATION ev
             WHERE c1/content/name/value = 'My Observation'""",
        """
            SELECT e/ehr_id/value, c/content/name/value
            FROM EHR e CONTAINS COMPOSITION c
            ORDER BY e/ehr_id/value, c/content/name/value""",
        """
           SELECT c/context/start_time
           FROM COMPOSITION c
           ORDER BY c/context/start_time
        """,
        """
            SELECT ec/start_time/value
            FROM EHR e CONTAINS COMPOSITION c CONTAINS EVENT_CONTEXT ec
            ORDER BY ec/start_time ASC
        """,
        """
            SELECT e/ehr_id/value, c/content
            FROM EHR e CONTAINS COMPOSITION c
        """,
        "SELECT c/setting/defining_code/code_string FROM EVENT_CONTEXT c",
        """
            SELECT
            o/name/mappings,
            o/name/mappings/target,
            o/name/mappings/purpose/mappings,
            o/name/mappings/purpose/mappings/target
            FROM OBSERVATION o
        """,
        "SELECT c/start_time/value, e/value/value, e/value/magnitude FROM EVENT_CONTEXT c CONTAINS ELEMENT e",
        """
           SELECT c
           FROM EVENT_CONTEXT c CONTAINS ELEMENT e
           WHERE e/value = '1' AND c/start_time < '2023-10-13'
        """,
        """
            SELECT l/name/value
            FROM EHR e
            CONTAINS EHR_STATUS
            CONTAINS ELEMENT l
        """,
        """
            SELECT s/subject/external_ref/id/value, s/other_details/items[at0001]/value/id
            FROM EHR e
            CONTAINS EHR_STATUS s
        """,
        """
           SELECT s/other_details/items[at0001]/value/id
           FROM EHR e
           CONTAINS EHR_STATUS s
           WHERE e/ehr_id/value = '10f23be7-fd39-4e71-a0a5-9d1624d662b7'
        """,
        """
           SELECT t FROM ENTRY t
        """,
        """
           SELECT
               e/ehr_id/value,
               COUNT(*),
               COUNT(DISTINCT c/uid/value),
               COUNT(el),
               COUNT(el/name/mappings),
               COUNT(el/value),
               COUNT(el/value/value),
               MAX(el/value/value),
               MIN(el/value/value),
               MAX(el/value),
               MIN(el/value),
               AVG(el/value/value),
               SUM(el/value/value)
           FROM EHR e CONTAINS COMPOSITION c CONTAINS ELEMENT el
        """,
        "SELECT 1 FROM EHR e",
        "SELECT c FROM COMPOSITION c WHERE c/uid/value = 'b037bf7c-0ecb-40fb-aada-fc7d559815ea::node::1'",
        "SELECT c FROM COMPOSITION c WHERE c/uid/value = 'b037bf7c-0ecb-40fb-aada-fc7d559815ea::::1'",
        "SELECT c FROM COMPOSITION c WHERE c/uid/value = 'b037bf7c-0ecb-40fb-aada-fc7d559815ea'",
        "SELECT e/ehr_id/value, e/time_created, e/time_created/value FROM EHR e WHERE e/time_created > '2021-01-02T12:13:14+01:00' ORDER BY e/time_created",
        """
            SELECT
             e/ehr_id/value,
             e/system_id,
             e/system_id/value
            FROM EHR e
            WHERE e/system_id/value = 'abc'
            ORDER BY e/system_id/value
        """
    ])
    def test_ensure_query_supported(self, aql):
        aql_query = AqlQueryParser.parse(aql)
        AqlQueryFeatureCheck(lambda: "node").ensure_query_supported(aql_query)

    @pytest.mark.parametrize("aql", [
        "SELECT e FROM EHR e",
        "SELECT e/ehr_id FROM EHR e",
        """
           SELECT c
           FROM COMPOSITION c
           WHERE c/uid/value = c/name/value
        """,
        """
           SELECT c
           FROM COMPOSITION c
           WHERE c/uid = '1'
        """,
        """
           SELECT c
           FROM COMPOSITION c
           WHERE EXISTS c/uid/value
        """,
        """
           SELECT c
           FROM COMPOSITION c
           ORDER BY c/context/start_time/value
        """,
        """
           SELECT o
           FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION o
           WHERE o/value/value = '1' AND o/value/magnitude = 2
        """,
        """
           SELECT o
           FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION o
           WHERE o/value = '1' AND o/value/magnitude = 2
        """,
        "SELECT e FROM EHR e LIMIT 10 OFFSET 20",
        """
            SELECT c
            FROM EHR e CONTAINS COMPOSITION c
            LIMIT 10 OFFSET 20
        """,
        """
            SELECT c
            FROM EHR e CONTAINS COMPOSITION c
            LIMIT 20
        """,
        """
            SELECT c
            FROM EHR e CONTAINS COMPOSITION c
            ORDER BY c/context/start_time/value
            LIMIT 10 OFFSET 10
        """,
        "SELECT s FROM EHR e CONTAINS EHR_STATUS s WHERE e/ehr_id/value = 'b037bf7c-0ecb-40fb-aada-fc7d559815ea' LIMIT 10 OFFSET 10",
        "SELECT c FROM COMPOSITION c WHERE c/name/value LIKE 'hello%'"
    ])
    def test_ensure_query_not_supported(self, aql):
        aql_query = AqlQueryParser.parse(aql)
        with pytest.raises(AqlFeatureNotImplementedException):
            AqlQueryFeatureCheck(lambda: "node").ensure_query_supported(aql_query)
