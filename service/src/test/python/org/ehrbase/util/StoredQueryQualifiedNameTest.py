# test_stored_query_qualified_name.py

import pytest
from semver import SemVer
from stored_query_qualified_name import StoredQueryQualifiedName
from assertpy import assert_that

# Test class to replace the original StoredQueryQualifiedNameTest
class TestStoredQueryQualifiedName:

    def test_with_full_name(self):
        name = "org.example.departmentx.test::diabetes-patient-overview"
        version = SemVer.parse("1.0.2")

        # Creating a StoredQueryQualifiedName instance
        stored_query_qualified_name = StoredQueryQualifiedName.create(name, version)

        # Asserting the values are correctly set
        assert stored_query_qualified_name is not None
        assert stored_query_qualified_name.semVer() == version

        assert stored_query_qualified_name.reverse_domain_name() == "org.example.departmentx.test"
        assert stored_query_qualified_name.semantic_id() == "diabetes-patient-overview"
        assert stored_query_qualified_name.semVer().to_version_string() == "1.0.2"
        assert stored_query_qualified_name.to_name() == "org.example.departmentx.test::diabetes-patient-overview"
        assert stored_query_qualified_name.to_qualified_name_string() == "org.example.departmentx.test::diabetes-patient-overview/1.0.2"
        assert str(stored_query_qualified_name) == "org.example.departmentx.test::diabetes-patient-overview/1.0.2"

    def test_with_incomplete_name(self):
        name = "org.example.departmentx.test::diabetes-patient-overview"

        # Creating a StoredQueryQualifiedName instance with SemVer.NO_VERSION
        stored_query_qualified_name = StoredQueryQualifiedName.create(name, SemVer.NO_VERSION)

        # Asserting the values are correctly set
        assert stored_query_qualified_name is not None
        assert stored_query_qualified_name.semVer() == SemVer.NO_VERSION

        assert stored_query_qualified_name.reverse_domain_name() == "org.example.departmentx.test"
        assert stored_query_qualified_name.semantic_id() == "diabetes-patient-overview"
        assert stored_query_qualified_name.semVer().to_version_string() == ""
        assert stored_query_qualified_name.to_name() == "org.example.departmentx.test::diabetes-patient-overview"
        assert stored_query_qualified_name.to_qualified_name_string() == "org.example.departmentx.test::diabetes-patient-overview"
        assert str(stored_query_qualified_name) == "org.example.departmentx.test::diabetes-patient-overview"

    def test_with_badly_formed_name(self):
        name = "org.example.departmentx.test"
        version = SemVer.parse("")

        # Expecting an IllegalArgumentException to be raised
        with pytest.raises(ValueError):
            StoredQueryQualifiedName.create(name, version)

    def test_to_string(self):
        # Testing the string representation with SemVer.NO_VERSION
        assert_that(StoredQueryQualifiedName.create(
            "org.example.departmentx.test::diabetes-patient-overview", SemVer.NO_VERSION)).has_to_string("org.example.departmentx.test::diabetes-patient-overview")

        # Testing the string representation with a specific SemVer version
        assert_that(StoredQueryQualifiedName.create(
            "org.example.departmentx.test::diabetes-patient-overview", SemVer.parse("1.2"))).has_to_string("org.example.departmentx.test::diabetes-patient-overview/1.2")
