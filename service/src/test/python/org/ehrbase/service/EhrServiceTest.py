import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
import uuid

from ehrbase.api.dto import EhrStatusDto
from ehrbase.api.exception import ObjectNotFoundException, StateConflictException
from ehrbase.api.service import EhrService
from ehrbase.api.service import SystemService
from ehrbase.api.service import ValidationService
from ehrbase.repository import CompositionRepository, EhrFolderRepository, EhrRepository, ItemTagRepository
from ehrbase.service.maping import EhrStatusMapper
from ehrbase.service import EhrServiceImp
from ehrbase.test.assertions import EhrStatusAssert
from nedap.archie.rm.changecontrol import OriginalVersion
from nedap.archie.rm.datavalues import DvText
from nedap.archie.rm.ehr import EhrStatus
from nedap.archie.rm.generic import PartySelf
from nedap.archie.rm.support.identification import HierObjectId, ObjectVersionId, PartyRef, UIDBasedId


class EhrServiceTest(unittest.TestCase):

    def setUp(self):
        self.system_service = SystemService(lambda: "test-ehr-service")
        self.validation_service = MagicMock(spec=ValidationService)
        self.ehr_folder_repository = MagicMock(spec=EhrFolderRepository)
        self.composition_repository = MagicMock(spec=CompositionRepository)
        self.ehr_repository = MagicMock(spec=EhrRepository)
        self.item_tag_repository = MagicMock(spec=ItemTagRepository)

        self.spy_ehr_service = mock.create_autospec(EhrServiceImp)(
            validation_service=self.validation_service,
            system_service=self.system_service,
            ehr_folder_repository=self.ehr_folder_repository,
            composition_repository=self.composition_repository,
            ehr_repository=self.ehr_repository,
            item_tag_repository=self.item_tag_repository
        )

    def service(self):
        return self.spy_ehr_service

    @staticmethod
    def ehr_status_dto(uid_based_id=None, subject=None):
        return EhrStatusDto(
            uid_based_id,
            "openEHR-EHR-EHR_STATUS.generic.v1",
            DvText("EHR Status"),
            None,
            None,
            subject,
            True,
            True,
            None
        )

    @staticmethod
    def original_version(object_id, data):
        return OriginalVersion(
            ObjectVersionId(str(object_id)),
            None,
            data,
            None,
            None,
            None,
            None,
            None,
            None
        )

    def test_create_defaults(self):
        ehr_id = uuid.UUID("64aa777e-942c-45c0-97c9-835a5371025a")
        result = self.run_create_ehr(self.service(), ehr_id, None)

        self.validation_service.check.assert_not_called()
        self.assertEqual(result.ehr_id, ehr_id)
        EhrStatusAssert.assertThat(result.ehr_status).has_id_root().has_id_extension("test-ehr-service::1").is_equal_to_ignore_id(
            EhrStatusMapper.from_dto(self.ehr_status_dto(None, PartySelf()))
        )

    def test_create_with_ehr_status(self):
        ehr_id = uuid.UUID("ac7979e1-c84b-4a3a-affb-716d8651c37d")
        ehr_status_dto = self.ehr_status_dto(
            HierObjectId("49995d4b-2cff-445c-ae38-579919007a72"),
            PartySelf(PartyRef(HierObjectId("42"), "some:external_id", "my_type"))
        )
        result = self.run_create_ehr(self.service(), ehr_id, ehr_status_dto)

        self.validation_service.check.assert_called_once_with(mock.ANY)

        self.assertEqual(result.ehr_id, ehr_id)
        EhrStatusAssert.assertThat(result.ehr_status).has_id_root().has_id_extension("test-ehr-service::1").is_equal_to_ignore_id(
            EhrStatusMapper.from_dto(ehr_status_dto)
        )

    def test_create_with_ehr_status_id_replaced(self):
        ehr_id = uuid.UUID("64aa777e-942c-45c0-97c9-835a5371025a")
        ehr_status_dto = self.ehr_status_dto(HierObjectId("invalid"), None)
        result = self.run_create_ehr(self.service(), ehr_id, ehr_status_dto)

        self.assertIsNotNone(uuid.UUID(result.ehr_status.uid.root.value))

    def test_create_with_ehr_status_error_conflict(self):
        ehr_id = uuid.UUID("35ac68ba-7147-455c-adbc-c31f1faa675b")
        ehr_status_dto = self.ehr_status_dto(HierObjectId("invalid"), None)
        result = self.run_create_ehr(self.service(), ehr_id, ehr_status_dto)

        self.assertIsNotNone(uuid.UUID(result.ehr_status.uid.root.value))

    def test_create_with_ehr_status_error_party_exist(self):
        ehr_id = uuid.UUID("73d7cf5c-03b3-4b57-b689-d7f6be579049")
        ehr_status_dto = self.ehr_status_dto(
            HierObjectId("20b5cb7a-4431-4524-96ea-56f80bc00496"),
            PartySelf(PartyRef(HierObjectId("42"), "some:namespace", "some_type"))
        )

        service = self.service()
        service.find_by_subject = mock.MagicMock(return_value=uuid.UUID("20b5cb7a-4431-4524-96ea-56f80bc00496"))

        with self.assertRaises(StateConflictException) as context:
            self.run_create_ehr(service, ehr_id, ehr_status_dto)

        self.assertEqual(str(context.exception), "Supplied partyId[42] is used by a different EHR in the same partyNamespace[some:namespace].")

    class CreationResult:
        def __init__(self, ehr_id, ehr_status):
            self.ehr_id = ehr_id
            self.ehr_status = ehr_status

    def run_create_ehr(self, service, ehr_id, ehr_status_dto):
        captor = mock.Mock()
        created_ehr_id = service.create(ehr_id, ehr_status_dto).ehr_id()

        self.ehr_repository.commit.assert_called_once_with(
            created_ehr_id, captor.capture(), None, None
        )
        return self.CreationResult(created_ehr_id, captor.return_value)

    def test_get_ehr_status_error_ehr_not_found(self):
        ehr_id = uuid.UUID("ce3a8b60-cfba-4081-8583-8113d12a6118")

        service = self.service()
        self.ehr_repository.has_ehr.return_value = True

        with self.assertRaises(ObjectNotFoundException) as context:
            service.get_ehr_status(ehr_id)

        self.assertEqual(str(context.exception), "No EHR found with given ID: ce3a8b60-cfba-4081-8583-8113d12a6118")

    def test_get_ehr_status_error_head_not_found(self):
        ehr_id = uuid.UUID("ce3a8b60-cfba-4081-8583-8113d12a6118")

        service = self.service()
        self.ehr_repository.has_ehr.return_value = False
        self.ehr_repository.find_head.return_value = None

        with self.assertRaises(ObjectNotFoundException) as context:
            service.get_ehr_status(ehr_id)

        self.assertEqual(str(context.exception), "EHR with id ce3a8b60-cfba-4081-8583-8113d12a6118 not found")

    def test_get_ehr_status(self):
        ehr_id = uuid.UUID("ce3a8b60-cfba-4081-8583-8113d12a6118")
        ehr_status_dto = self.ehr_status_dto()

        service = self.service()
        self.ehr_repository.has_ehr.return_value = True
        self.ehr_repository.find_head.return_value = EhrStatusMapper.from_dto(ehr_status_dto)

        ehr_status = service.get_ehr_status(ehr_id).status()
        self.assertEqual(ehr_status, ehr_status_dto)

    def test_get_ehr_status_at_version_ehr_not_found(self):
        ehr_id = uuid.UUID("d783d2f0-0686-4dc0-a04e-0c7272687952")
        status_id = uuid.UUID("b08d2dca-f79b-480a-a2fa-f1b1dd997667")

        service = self.service()
        self.ehr_repository.has_ehr.return_value = False

        with self.assertRaises(ObjectNotFoundException) as context:
            service.get_ehr_status_at_version(ehr_id, status_id, 2)

        self.assertEqual(str(context.exception), "No EHR found with given ID: d783d2f0-0686-4dc0-a04e-0c7272687952")

    def test_get_ehr_status_at_version_not_found(self):
        ehr_id = uuid.UUID("d783d2f0-0686-4dc0-a04e-0c7272687952")
        status_id = uuid.UUID("1990b6e5-7d26-4bc6-9f54-0cf7f0b65855")

        service = self.service()
        self.ehr_repository.has_ehr.return_value = True

        self.assertIsNone(service.get_ehr_status_at_version(ehr_id, status_id, 2))

    def test_get_ehr_status_at_version(self):
        ehr_id = uuid.UUID("d783d2f0-0686-4dc0-a04e-0c7272687952")
        status_id = uuid.UUID("af0db626-8f1e-4931-a87e-bd9f641169af")
        expected_dto = self.ehr_status_dto()

        service = self.service()
        self.ehr_repository.has_ehr.return_value = True
        self.ehr_repository.find_head.return_value = EhrStatusMapper.from_dto(expected_dto)

        result = service.get_ehr_status_at_version(ehr_id, status_id, 2)
        self.assertIsNotNone(result)
        self.assertEqual(result.ehr_id, ehr_id)
        self.assertEqual(result.ehr_status, expected_dto)


if __name__ == '__main__':
    unittest.main()
