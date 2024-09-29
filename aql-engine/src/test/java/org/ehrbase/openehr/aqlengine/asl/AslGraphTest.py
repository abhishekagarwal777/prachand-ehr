import unittest
from your_module import (
    AqlQuery, AqlQueryWrapper, AslRootQuery, AslGraph
)

class TestAslGraph(unittest.TestCase):

    def test_print_data_query_graph(self):
        # Sample AQL query string
        aql_query_str = """
        SELECT
          -- c1/content[openEHR-EHR-SECTION.adhoc.v1],
          -- c1/content[openEHR-EHR-SECTION.adhoc.v1]/name,
          c1/content[openEHR-EHR-SECTION.adhoc.v1]/name/value
          -- ,c1/content[openEHR-EHR-SECTION.adhoc.v1,'Diagnostic Results']/name/value
        FROM EHR e
          CONTAINS COMPOSITION c1
        """

        # Parse AQL query
        aql_query = AqlQuery.parse(aql_query_str)

        # Wrap the parsed query
        query_wrapper = AqlQueryWrapper.create(aql_query)

        # Build ASL root query
        root_query = AslRootQuery.create_from_wrapper(query_wrapper)

        # Generate ASL graph and print it
        asl_graph = AslGraph.create_asl_graph(root_query)
        print(asl_graph)

        # Optionally: Assert something about the output
        # For example, you might want to check that the output contains certain expected strings
        self.assertIn("SELECT", asl_graph)
        self.assertIn("FROM", asl_graph)

if __name__ == '__main__':
    unittest.main()
