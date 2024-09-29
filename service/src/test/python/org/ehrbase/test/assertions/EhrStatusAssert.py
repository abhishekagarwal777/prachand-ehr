import uuid
from assertpy import assert_that
from EHR import EhrStatus, PartySelf  # Adjust this import based on your actual module structure

class EhrStatusAssert:
    def __init__(self, actual: EhrStatus):
        self.actual = actual

    @staticmethod
    def assert_that(actual: EhrStatus):
        return EhrStatusAssert(actual)

    def is_equal_to_ignore_id(self, expected: EhrStatus):
        assert_that(self.actual.archetype_node_id).described_as("archetype_node_id").is_equal_to(expected.archetype_node_id)
        assert_that(self.actual.name).described_as("name").is_equal_to(expected.name)
        assert_that(self.actual.subject).described_as("subject").is_instance_of(PartySelf).is_equal_to(expected.subject)
        assert_that(self.actual.is_queryable).described_as("is_queryable").is_equal_to(expected.is_queryable)
        assert_that(self.actual.is_modifiable).described_as("is_modifiable").is_equal_to(expected.is_modifiable)
        assert_that(self.actual.other_details).described_as("other_details").is_equal_to(expected.other_details)
        assert_that(self.actual.archetype_details).described_as("archetype_details").is_equal_to(expected.archetype_details)
        assert_that(self.actual.feeder_audit).described_as("feeder_audit").is_equal_to(expected.feeder_audit)
        assert_that(self.actual.links).described_as("links").is_none()
        assert_that(self.actual.parent).described_as("parent").is_equal_to(expected.parent)
        return self

    def has_id_root(self):
        assert_that(self.actual.uid.root).described_as("uid::root").is_not_none()
        return self

    def has_id_root_value(self, id_value: uuid.UUID):
        self.has_id_root()
        assert_that(self.actual.uid.root.value).described_as("uid::root").is_equal_to(str(id_value))
        return self

    def has_id_extension(self, id_extension: str):
        assert_that(self.actual.uid.extension).described_as("uid::extension").is_equal_to(id_extension)
        return self

# Example usage:
# actual_ehr_status = ...  # Your instance of EhrStatus
# expected_ehr_status = ...  # Your expected instance of EhrStatus
# EhrStatusAssert.assert_that(actual_ehr_status).is_equal_to_ignore_id(expected_ehr_status)
