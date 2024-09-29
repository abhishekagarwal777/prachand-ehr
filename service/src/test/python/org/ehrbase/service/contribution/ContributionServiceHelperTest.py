import unittest
from unittest import mock
from collections import namedtuple
from typing import List, Callable
import json

# Mocked classes and enums
class RMObject:
    pass

class OriginalVersion:
    def __init__(self, change_type, data, commit_audit):
        self.change_type = change_type
        self.data = data
        self.commit_audit = commit_audit

class ContributionChangeType:
    CREATION = 'creation'
    MODIFICATION = 'modification'

    @classmethod
    def get_code(cls, change_type):
        return 0 if change_type == cls.CREATION else 1

class Audit:
    def __init__(self, system_id):
        self.system_id = system_id

class ContributionCreateDto:
    def __init__(self, audit, versions):
        self.audit = audit
        self.versions = versions

    def get_audit(self):
        return self.audit

    def get_versions(self):
        return self.versions

class ContributionWrapper:
    def __init__(self, contribution_create_dto):
        self.contribution_create_dto = contribution_create_dto

    def get_contribution_create_dto(self):
        return self.contribution_create_dto

class ContributionTestDataCanonicalJson:
    ONE_ENTRY_COMPOSITION = "one_entry_composition"
    TWO_ENTRIES_COMPOSITION = "two_entries_composition"
    ONE_ENTRY_COMPOSITION_MODIFICATION_LATEST = "one_entry_composition_modification_latest"

    @staticmethod
    def get_stream(name):
        # Mocking a data stream for test data
        return open(f"{name}.json", 'r')

class ContributionServiceHelper:
    @staticmethod
    def unmarshal_contribution(data_string):
        data = json.loads(data_string)
        audit = Audit(data['audit']['systemId'])
        versions = [OriginalVersion(v['changeType'], v['data'], v['commitAudit']) for v in data['versions']]
        return ContributionWrapper(ContributionCreateDto(audit, versions))


class ContributionServiceHelperTest(unittest.TestCase):
    def unmarshal_contribution(self, contribution_data):
        try:
            contribution_wrapper = ContributionServiceHelper.unmarshal_contribution(
                load_contribution_string(contribution_data)
            )
            contribution_create_dto = contribution_wrapper.get_contribution_create_dto()
            self.assertIsNotNone(contribution_create_dto)
            return contribution_create_dto
        except IOError as e:
            raise RuntimeError(f"Failed to load contribution: {e}")

    def test_unmarshal_contribution_one_composition(self):
        c = self.unmarshal_contribution(ContributionTestDataCanonicalJson.ONE_ENTRY_COMPOSITION)

        self.assertEqual(c.get_audit().system_id, "test-system-id")

        self.assert_versions(
            c,
            lambda v: self.assert_original_version(v, ContributionChangeType.CREATION, Composition, 
                                                    lambda d: self.assertEqual(d['archetypeNodeId'], "openEHR-EHR-COMPOSITION.minimal.v1"))
        )

    def test_unmarshal_contribution_two_compositions(self):
        c = self.unmarshal_contribution(ContributionTestDataCanonicalJson.TWO_ENTRIES_COMPOSITION)

        self.assertEqual(c.get_audit().system_id, "test-system-id")

        self.assert_versions(
            c,
            lambda v: self.assert_original_version(v, ContributionChangeType.CREATION, Composition,
                                                    lambda d: self.assertEqual(d['archetypeNodeId'], "openEHR-EHR-COMPOSITION.minimal.v1")),
            lambda v: self.assert_original_version(v, ContributionChangeType.CREATION, Composition,
                                                    lambda d: self.assertEqual(d['archetypeNodeId'], "openEHR-EHR-COMPOSITION.minimal.v1"))
        )

    def test_unmarshal_contribution_one_entry_composition_modification(self):
        c = self.unmarshal_contribution(ContributionTestDataCanonicalJson.ONE_ENTRY_COMPOSITION_MODIFICATION_LATEST)

        self.assertEqual(c.get_audit().system_id, "test-system-id")

        self.assert_versions(
            c,
            lambda v: self.assert_original_version(v, ContributionChangeType.MODIFICATION, Composition,
                                                    lambda d: self.assertEqual(d['archetypeNodeId'], "openEHR-EHR-COMPOSITION.minimal.v1"))
        )

    def assert_versions(self, contribution, *version_assertions: Callable[[OriginalVersion], None]):
        versions = contribution.get_versions()
        self.assertEqual(len(versions), len(version_assertions))
        for i in range(len(versions)):
            version_assertions[i](versions[i])

    def assert_original_version(self, v: OriginalVersion, change_type: ContributionChangeType, 
                                data_type: type, data_assertions: Callable[[dict], None]):
        self.assertEqual(v.commit_audit['changeType']['definingCode']['codeString'], str(ContributionChangeType.get_code(change_type)))
        self.assertIsInstance(v.data, data_type)
        data_assertions(v.data)

def load_contribution_string(contribution_data):
    with ContributionTestDataCanonicalJson.get_stream(contribution_data) as infile:
        return infile.read()


if __name__ == "__main__":
    unittest.main()
