import unittest
from unittest.mock import MagicMock, patch
from your_module import OpenehrQueryController, AqlQueryRequest, InvalidApiParameterException, MetaData, QueryResponseData

class TestOpenehrQueryController(unittest.TestCase):

    SAMPLE_QUERY = "SELECT s FROM EHR_STATUS s"
    SAMPLE_PARAMETER_MAP = {"key": "value"}
    SAMPLE_META_DATA = MetaData()

    def setUp(self):
        self.mock_aql_query_service = MagicMock()
        self.mock_stored_query_service = MagicMock()
        self.mock_query_context = MagicMock()
        self.controller = OpenehrQueryController(
            self.mock_aql_query_service,
            self.mock_stored_query_service,
            self.mock_query_context
        )
        self.controller.get_context_path = MagicMock(return_value="https://openehr.test.query.controller.com/rest")

    def tearDown(self):
        # Reset the mock calls after each test if needed
        pass

    def controller_setup(self):
        self.mock_query_context.create_meta_data.return_value = self.SAMPLE_META_DATA
        self.mock_aql_query_service.query.return_value = QueryResponseData()
        return self.controller

    def controller_stored_query_setup(self):
        query_definition_result_dto = {
            "query_text": self.SAMPLE_QUERY,
            "qualified_name": "test_query"
        }
        self.mock_stored_query_service.retrieve_stored_query.return_value = query_definition_result_dto
        return self.controller_setup()

    def to_long(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, int):
            return float(obj)
        elif isinstance(obj, str):
            return float(obj)
        else:
            raise ValueError(f"unexpected type {type(obj).__name__}")

    def test_GETexecuteAddHocQuery(self):
        for fetch, offset in [(None, None), (10, 0), (0, 25)]:
            response = self.controller_setup().execute_ad_hoc_query(
                self.SAMPLE_QUERY,
                offset,
                fetch,
                self.SAMPLE_PARAMETER_MAP,
                "application/json"
            )
            self.assert_meta_data(response)
            self.assert_aql_query_request(AqlQueryRequest(self.SAMPLE_QUERY, self.SAMPLE_PARAMETER_MAP, self.to_long(fetch), self.to_long(offset)))

    def test_POSTexecuteAddHocQuery(self):
        for fetch, offset in [(None, None), (10, 0), (0, 25), ('1', '2')]:
            response = self.controller_setup().execute_ad_hoc_query(
                self.sample_aql_query(fetch, offset),
                "application/json",
                "application/x-www-form-urlencoded"
            )
            self.assert_meta_data(response)
            self.assert_aql_query_request(AqlQueryRequest(self.SAMPLE_QUERY, self.SAMPLE_PARAMETER_MAP, self.to_long(fetch), self.to_long(offset)))

    def sample_aql_query(self, fetch, offset):
        map_ = self.sample_aql_json(fetch, offset)
        map_["q"] = self.SAMPLE_QUERY
        return map_

    def sample_aql_json(self, fetch, offset):
        map_ = {"query_parameters": self.SAMPLE_PARAMETER_MAP}
        if fetch is not None:
            map_["fetch"] = fetch
        if offset is not None:
            map_["offset"] = offset
        return map_

    def test_POSTexecuteAddHocQueryWithFetchInvalid(self):
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller_setup().execute_ad_hoc_query(
                self.sample_aql_query("invalid", None),
                "application/json",
                "application/x-www-form-urlencoded"
            )
        self.assertEqual("invalid 'fetch' value 'invalid'", str(context.exception))

    def test_POSTexecuteAddHocQueryWithOffsetInvalid(self):
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller_setup().execute_ad_hoc_query(
                self.sample_aql_query(None, "invalid"),
                "application/json",
                "application/x-www-form-urlencoded"
            )
        self.assertEqual("invalid 'offset' value 'invalid'", str(context.exception))

    def test_GETexecuteStoredQuery(self):
        for fetch, offset in [(None, None), (10, 0), (0, 25)]:
            response = self.controller_stored_query_setup().execute_stored_query(
                "my_qualified_query",
                "v1.0.0",
                offset,
                fetch,
                self.SAMPLE_PARAMETER_MAP,
                "application/json"
            )
            self.assert_meta_data(response)
            self.assert_aql_query_request(AqlQueryRequest(self.SAMPLE_QUERY, self.SAMPLE_PARAMETER_MAP, self.to_long(fetch), self.to_long(offset)))

    def test_POSTexecuteStoredQuery(self):
        for fetch, offset in [(None, None), (10, 0), (0, 25), ('1', '2')]:
            response = self.controller_stored_query_setup().execute_stored_query(
                "my_qualified_query",
                "v1.0.0",
                "application/json",
                "application/json",
                self.sample_aql_json(fetch, offset)
            )
            self.assert_meta_data(response)
            self.assert_aql_query_request(AqlQueryRequest(self.SAMPLE_QUERY, self.SAMPLE_PARAMETER_MAP, self.to_long(fetch), self.to_long(offset)))

    def test_POSTexecuteStoredQueryWithFetchInvalid(self):
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller_stored_query_setup().execute_stored_query(
                "my_qualified_query",
                "v1.0.0",
                "application/json",
                "application/json",
                self.sample_aql_json("invalid", None)
            )
        self.assertEqual("invalid 'fetch' value 'invalid'", str(context.exception))

    def test_POSTexecuteStoredQueryWithOffsetInvalid(self):
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller_stored_query_setup().execute_stored_query(
                "my_qualified_query",
                "v1.0.0",
                "application/json",
                "application/json",
                self.sample_aql_json(None, "invalid")
            )
        self.assertEqual("invalid 'offset' value 'invalid'", str(context.exception))

    def assert_aql_query_request(self, aql_query_request):
        self.mock_aql_query_service.query.assert_called_once_with(aql_query_request)

    def assert_meta_data(self, response):
        body = response.body
        self.assertIsNotNone(body)
        self.assertIs(self.SAMPLE_META_DATA, body.meta)
        self.mock_query_context.create_meta_data.assert_called_once_with(any())

if __name__ == '__main__':
    unittest.main()
