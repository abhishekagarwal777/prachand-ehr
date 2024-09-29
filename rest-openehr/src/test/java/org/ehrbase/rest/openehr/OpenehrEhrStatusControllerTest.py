import unittest
from unittest.mock import Mock, patch, call
from datetime import datetime
from collections import namedtuple

# Assuming these classes exist and are imported
from your_module import OpenehrEhrStatusController, EhrStatusDto, InvalidApiParameterException, ObjectNotFoundException

# Mock classes to simulate Java classes
class ObjectVersionId:
    def __init__(self, uid, system, version):
        self.uid = uid
        self.system = system
        self.version = version

    def __str__(self):
        return f"{self.uid}::{self.system}::{self.version}"


class DvText:
    def __init__(self, text):
        self.text = text


class AuditDetails:
    def __init__(self, time_committed):
        self.time_committed = time_committed


class OriginalVersion:
    def __init__(self, uid, preceding_version_uid, data, commit_audit):
        self.uid = uid
        self.preceding_version_uid = preceding_version_uid
        self.data = data
        self.commit_audit = commit_audit


class EhrService:
    class EhrResult:
        def __init__(self, ehr_id, next_version_id, ehr_status):
            self.ehr_id = ehr_id
            self.next_version_id = next_version_id
            self.ehr_status = ehr_status

# Test class
class TestOpenehrEhrStatusController(unittest.TestCase):

    CONTEXT_PATH = "https://test.ehr-status.controller/ehrbase/rest"

    def setUp(self):
        self.mock_ehr_service = Mock()
        self.controller = OpenehrEhrStatusController(self.mock_ehr_service)
        self.controller.get_context_path = Mock(return_value=self.CONTEXT_PATH)

    def tearDown(self):
        pass  # Reset or clean up if needed

    def ehr_status_dto(self, version_id, is_queryable, is_modifiable):
        return EhrStatusDto(
            version_id,
            "openEHR-EHR-EHR_STATUS.generic.v1",
            DvText("EHR Status"),
            None,
            None,
            None,
            is_queryable,
            is_modifiable,
            None
        )

    def original_version(self, next_version_id, current_version_id, last_modified, ehr_status):
        commit_audit = AuditDetails(last_modified)
        return OriginalVersion(next_version_id, current_version_id, ehr_status, commit_audit)

    def test_get_ehr_status_by_version_not_found(self):
        ehr_id = "d83a16ae-2644-4706-8911-282772c10137"
        with self.assertRaises(ObjectNotFoundException) as context:
            self.controller.get_ehr_status_by_version_id(ehr_id, "13a82993-a489-421a-ac88-5cec001bd58c::local-system::42")
        self.assertEqual(str(context.exception), "Could not find EhrStatus[id=13a82993-a489-421a-ac88-5cec001bd58c, version=42]")

    def test_get_ehr_status_version_by_time_latest(self):
        ehr_id = "7c927831-726e-4ad7-8b62-b078d80eb59a"
        ehr_status_dto = self.ehr_status_dto(ObjectVersionId("some-id", "some-system", "12"), False, False)

        self.mock_ehr_service.get_latest_version_uid_of_status.return_value = ehr_status_dto.uid
        response = self.controller.get_ehr_status_version_by_time(ehr_id, None)

        self.assertIsNotNone(response)

    def test_get_ehr_status_version_by_time_by_timestamp(self):
        ehr_id = "7c927831-726e-4ad7-8b62-b078d80eb59a"
        ehr_status_dto = self.ehr_status_dto(ObjectVersionId("some-id", "some-system", "12"), False, False)

        self.mock_ehr_service.get_ehr_status_version_by_timestamp.return_value = ehr_status_dto.uid
        response = self.controller.get_ehr_status_version_by_time(ehr_id, "2024-07-16T08:30:00Z")

        self.assertIsNotNone(response)

    def test_get_ehr_status_by_version_id_invalid(self):
        ehr_id = "d83a16ae-2644-4706-8911-282772c10137"
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller.get_ehr_status_by_version_id(ehr_id, "13a82993-a489-421a-ac88-5cec001bd58c")
        self.assertEqual(str(context.exception), "VERSION UID parameter does not contain a version")

    def test_get_ehr_status_by_version_id(self):
        ehr_id = "d83a16ae-2644-4706-8911-282772c10137"
        ehr_status_id = "13a82993-a489-421a-ac88-5cec001bd58c"
        version_id = ObjectVersionId(ehr_status_id, "some-system", "42")
        last_modified = datetime.fromisoformat("2024-07-16T13:15:00")

        ehr_status = self.ehr_status_dto(version_id, True, False)

        self.mock_ehr_service.get_ehr_status_at_version.return_value = \
            OriginalVersion(version_id, None, ehr_status, AuditDetails(last_modified))

        response = self.controller.get_ehr_status_by_version_id(ehr_id, str(version_id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Location'], f"{self.CONTEXT_PATH}/ehr/{ehr_id}/ehr_status/{version_id}")
        self.assertEqual(response.headers['ETag'], f'"{version_id}"')
        self.assertEqual(response.headers['Last-Modified'], last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def test_update_ehr_status(self):
        prefer = ""
        ehr_id = "d83a16ae-2644-4706-8911-282772c10137"
        ehr_status_id = "305eb2fd-c228-445c-ada7-5429d852fbb2"
        current_version_id = ObjectVersionId(ehr_status_id, "test.ehr.controller", "2")
        next_version_id = ObjectVersionId(ehr_status_id, "test.ehr.controller", "3")
        last_modified = datetime.fromisoformat("2024-07-16T12:00:00")

        ehr_status = self.ehr_status_dto(current_version_id, True, True)

        self.mock_ehr_service.update_status.return_value = EhrService.EhrResult(ehr_id, next_version_id, ehr_status)
        self.mock_ehr_service.get_ehr_status_at_version.return_value = \
            OriginalVersion(next_version_id, current_version_id, ehr_status, AuditDetails(last_modified))

        response = self.controller.update_ehr_status(ehr_id, str(current_version_id), prefer, ehr_status)

        if prefer == "return=representation":
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Location'], f"{self.CONTEXT_PATH}/ehr/{ehr_id}/ehr_status/{next_version_id}")
        else:
            self.assertEqual(response.status_code, 204)
            self.assertIsNone(response.data)

    def run_test_with_mock_result(self, consumer):
        ehr_id = "7c927831-726e-4ad7-8b62-b078d80eb59a"
        ehr_status_id = "8c2152e8-10f7-4b9f-bc28-27421b8937e7"
        version_id = ObjectVersionId(ehr_status_id, "some-system", "12")
        last_modified = datetime.fromisoformat("2024-07-16T13:20:00")

        ehr_status = self.ehr_status_dto(version_id, False, False)

        self.mock_ehr_service.get_ehr_status_at_version.return_value = \
            OriginalVersion(version_id, None, ehr_status, AuditDetails(last_modified))

        response = consumer(ehr_id, ehr_status)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Location'], f"{self.CONTEXT_PATH}/ehr/{ehr_id}/ehr_status/{version_id}")
        self.assertEqual(response.headers['Last-Modified'], last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"))

# Entry point for running tests
if __name__ == '__main__':
    unittest.main()
