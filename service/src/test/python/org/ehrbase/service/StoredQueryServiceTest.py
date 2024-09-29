import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid
from collections import namedtuple
from EhrServiceTest import StoredQueryService, StateConflictException, QueryDefinitionResultDto, StoredQueryRecord, StoredQueryQualifiedName, SemVer  # Adjust import statements as necessary

StoredQueryRecord = namedtuple('StoredQueryRecord', ['qualified_name', 'id', 'semver', 'query_text', 'type', 'creation_date'])

class TestStoredQueryService(unittest.TestCase):

    def setUp(self):
        self.mock_stored_query_repository = MagicMock()
        self.cache_manager = MagicMock()
        self.cache_manager.get_cache.return_value = MagicMock()
        self.cache_provider = MagicMock()  # Replace with actual CacheProviderImp if needed

    def service(self, *records):
        # Mock responses
        for record in records:
            stored_query_qualified_name = StoredQueryQualifiedName.create(record.qualified_name, SemVer.parse(record.semver))
            self.mock_stored_query_repository.retrieve_qualified.return_value = (stored_query_qualified_name, record)

        return StoredQueryService(self.mock_stored_query_repository, self.cache_provider)

    def test_create_stored_query_new(self):
        record = StoredQueryRecord(
            qualified_name="test::crate", id="id", semver="0.5.0",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        self.mock_stored_query_repository.retrieve_qualified.return_value = (None, None)

        service = self.service()
        result = service.create_stored_query("test::name", "0.5.0", "SELECT es FROM EHR_STATUS es")
        self.assertEqual(result.qualified_name, "test::crate::id")
        self.assertEqual(result.version, "0.5.0")
        self.assertEqual(result.type, "test")
        self.assertEqual(result.query_text, "SELECT es FROM EHR_STATUS es")
        self.assertEqual(result.saved, record.creation_date)

    def test_create_stored_query_fail_version_already_exists(self):
        record = StoredQueryRecord(
            qualified_name="test::crate", id="id", semver="0.5.0",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        self.mock_stored_query_repository.retrieve_qualified.return_value = (record.qualified_name, record)

        service = self.service()
        with self.assertRaises(StateConflictException) as context:
            service.create_stored_query("test::name", "0.5.0", "SELECT es FROM EHR_STATUS es")
        self.assertEqual(str(context.exception), "Version already exists")

    def test_create_stored_query_fail_partial_version(self):
        record = StoredQueryRecord(
            qualified_name="test::crate", id="id", semver="0.5",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        self.mock_stored_query_repository.retrieve_qualified.return_value = (record.qualified_name, record)

        service = self.service()
        with self.assertRaises(IllegalStateException) as context:
            service.create_stored_query("test::name", "0.3.0", "SELECT es FROM EHR_STATUS es")
        self.assertEqual(str(context.exception), "The database contains stored queries with partial versions")

    def test_delete_stored_query(self):
        service = self.service()
        service.delete_stored_query("test::delete", "1.0.0")

        stored_query_qualified_name = StoredQueryQualifiedName.create("test::delete", SemVer.parse("1.0.0"))
        self.mock_stored_query_repository.delete.assert_called_with(stored_query_qualified_name)

    def test_delete_stored_query_evict_cache(self):
        stored_query_qualified_name = StoredQueryQualifiedName.create("test::delete", SemVer.parse("1.0.0"))
        self.cache_manager.get_cache.return_value.put(stored_query_qualified_name.to_qualified_name_string(), object())

        service = self.service()
        service.delete_stored_query("test::delete", "1.0.0")

        self.assertIsNone(self.cache_manager.get_cache.return_value.get(stored_query_qualified_name.to_qualified_name_string()))

    def test_retrieve_stored_query(self):
        record = StoredQueryRecord(
            qualified_name="test::name", id="id", semver="1.0.0",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        service = self.service(record)
        result = service.retrieve_stored_query("test::name", "1.0.0")

        self.assertEqual(result.qualified_name, "test::name::id")
        self.assertEqual(result.version, "1.0.0")
        self.assertEqual(result.type, "test")
        self.assertEqual(result.query_text, "SELECT es FROM EHR_STATUS es")
        self.assertEqual(result.saved, record.creation_date)

    def test_retrieve_stored_query_cached(self):
        record = StoredQueryRecord(
            qualified_name="test::cached", id="id", semver="1.4.2",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        service = self.service(record)
        result = service.retrieve_stored_query("test::cached", "1.4.2")
        result2 = service.retrieve_stored_query("test::cached", "1.4.2")

        self.assertIs(result, result2, "Expected result to be cached")

    def test_retrieve_stored_query_partial(self):
        v05 = StoredQueryQualifiedName.create("test::name", SemVer.parse("0.5"))
        v050 = StoredQueryQualifiedName.create("test::name", SemVer.parse("0.5.0"))
        v051 = StoredQueryQualifiedName.create("test::name", SemVer.parse("0.5.1"))

        record = StoredQueryRecord(
            qualified_name="test::crate", id="id", semver="0.5.0",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        record2 = StoredQueryRecord(
            qualified_name="test::crate", id="id", semver="0.5.1",
            query_text="SELECT es FROM EHR_STATUS es", type="test",
            creation_date=datetime.now()
        )

        service = self.service()

        # Create version 0.5.0
        self.mock_stored_query_repository.retrieve_qualified.return_value = (None, record)

        result = service.create_stored_query("test::name", "0.5.0", "SELECT es FROM EHR_STATUS es")
        self.assertEqual(result.version, "0.5.0")

        # Access using partial version
        self.mock_stored_query_repository.retrieve_qualified.return_value = (record.qualified_name, record)
        result = service.retrieve_stored_query("test::name", "0.5")
        self.assertEqual(result.version, "0.5.0")

        # Create version 0.5.1
        self.mock_stored_query_repository.retrieve_qualified.return_value = (None, record2)
        result = service.create_stored_query("test::name", "0.5.1", "SELECT es FROM EHR_STATUS es")
        self.assertEqual(result.version, "0.5.1")

        self.mock_stored_query_repository.retrieve_qualified.return_value = (record2.qualified_name, record2)
        result = service.retrieve_stored_query("test::name", "0.5")
        self.assertEqual(result.version, "0.5.1")

    def test_retrieve_stored_queries_empty(self):
        self.mock_stored_query_repository.retrieve_qualified_list.return_value = []

        service = self.service()
        self.assertEqual(0, len(service.retrieve_stored_queries("test::query")))

    def test_retrieve_stored_queries(self):
        self.mock_stored_query_repository.retrieve_qualified_list.return_value = [QueryDefinitionResultDto()]

        service = self.service()
        self.assertEqual(1, len(service.retrieve_stored_queries("test::query")))


if __name__ == '__main__':
    unittest.main()
