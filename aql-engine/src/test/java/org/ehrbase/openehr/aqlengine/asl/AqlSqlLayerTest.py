import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from typing import List
from your_module import AslRootQuery, AslGraph, AqlQueryWrapper, AqlSqlLayer
from your_module import AslQuery, AslStructureQuery, AslEncapsulatingQuery, AslPathDataQuery
from your_module import AslField, AslSubqueryField, KnowledgeCacheService
from your_module import AqlQueryParser, AqlQuery

class AqlSqlLayerTest(unittest.TestCase):
    
    def setUp(self):
        self.mock_knowledge_cache_service = MagicMock()
        self.mock_knowledge_cache_service.find_uuid_by_template_id.return_value = uuid4()
        
    def test_data_query_placed_last(self):
        asl_query = self.build_sql_query(
            """
            SELECT
            c/content,
            c/content[at0001],
            c[openEHR-EHR-COMPOSITION.test.v0]/content[at0002],
            c/uid/value,
            c/context/other_context[at0004]/items[at0014]/value
            FROM EHR e CONTAINS COMPOSITION c
            WHERE e/ehr_id/value = 'e6fad8ba-fb4f-46a2-bf82-66edb43f142f'
            """
        )
        queries = [q[0] for q in asl_query.get_children()]

        self.assertEqual(len(queries), 5)

        self.assertIsInstance(queries[0], AslStructureQuery)
        self.assertIsInstance(queries[1], AslStructureQuery)
        self.assertIsInstance(queries[2], AslEncapsulatingQuery)
        self.assertIsInstance(queries[3], AslEncapsulatingQuery)
        self.assertIsInstance(queries[4], AslPathDataQuery)

        # Check select
        content_field1 = asl_query.get_select()[0]
        content_field2 = asl_query.get_select()[1]
        content_field3 = asl_query.get_select()[2]

        self.assertIsInstance(content_field1, AslSubqueryField)
        self.assertEqual(len(content_field1.get_filter_conditions()), 0)
        self.assertIsInstance(content_field2, AslSubqueryField)
        self.assertEqual(len(content_field2.get_filter_conditions()), 1)
        self.assertIsInstance(content_field3, AslSubqueryField)
        self.assertEqual(len(content_field3.get_filter_conditions()), 2)

    def test_cluster_data_single_selection(self):
        asl_query = self.build_sql_query(
            """
            SELECT
                cluster/items[at0001]/value/data
            FROM COMPOSITION CONTAINS CLUSTER cluster[openEHR-EHR-CLUSTER.media_file.v1]
            """
        )
        queries = [q[0] for q in asl_query.get_children()]

        self.assertEqual(len(queries), 4)

        self.assertIsInstance(queries[0], AslStructureQuery)
        self.assertIsInstance(queries[1], AslStructureQuery)
        self.assertIsInstance(queries[2], AslEncapsulatingQuery)
        self.assertIsInstance(queries[3], AslPathDataQuery)
        self.assertFalse(queries[3].is_multiple_valued())
        self.assertEqual(queries[3].get_data_field().get_column_name(), "data")
        self.assertEqual(queries[3].get_data_field().get_type(), 'JSONB')

    def build_sql_query(self, query: str) -> AslRootQuery:
        aql_query = AqlQueryParser.parse(query)
        query_wrapper = AqlQueryWrapper.create(aql_query)
        aql_sql_layer = AqlSqlLayer(self.mock_knowledge_cache_service, lambda: "node")
        return aql_sql_layer.build_asl_root_query(query_wrapper)

if __name__ == '__main__':
    unittest.main()
