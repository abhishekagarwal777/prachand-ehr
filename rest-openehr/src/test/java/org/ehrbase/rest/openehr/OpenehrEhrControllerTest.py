import unittest
from unittest.mock import Mock, patch
from uuid import UUID
from your_module import OpenehrEhrController, EhrService, InvalidApiParameterException, ObjectNotFoundException, EhrDto, EhrStatusDto, PartySelf, DvText, HttpStatus, ResponseEntity

class OpenehrEhrControllerTest(unittest.TestCase):

    CONTEXT_PATH = "https://test.ehr.controller/ehrbase/rest"

    def setUp(self):
        self.mock_ehr_service = Mock(spec=EhrService)
        self.controller = OpenehrEhrController(self.mock_ehr_service, lambda: "test.ehr.controller")
        self.controller.getContextPath = Mock(return_value=self.CONTEXT_PATH)

    def tearDown(self):
        pass  # Clean up if necessary

    def create_result(self, ehr_id):
        return EhrService.EhrResult(ehr_id, None, self.ehr_status_dto())

    def ehr_status_dto(self):
        return EhrStatusDto(
            None,
            "openEHR-EHR-EHR_STATUS.generic.v1",
            DvText("EHR Status"),
            None,
            None,
            PartySelf(),
            True,
            True,
            None
        )

    def run_create_test(self, ehr_id, ehr_status, prefer, creation):
        self.mock_ehr_service.getEhrStatus.return_value = self.create_result(ehr_id)

        response = creation()
        self.assertEqual(response.status_code, HttpStatus.CREATED)
        self.assertIn('Location', response.headers)
        self.assertEqual(response.headers['Location'], f"{self.CONTEXT_PATH}/ehr/{ehr_id}")

        if prefer == "return=representation":
            self.assert_response_data_body(response, ehr_id, ehr_status)
        else:
            self.assertIsNone(response.data)

    def assert_response_data_body(self, response, ehr_id, ehr_status):
        body = response.data
        self.assertIsNotNone(body)
        self.assertEqual(body.ehrId.value, str(ehr_id))
        self.assertIs(body.ehrStatus, ehr_status)

    def test_create_ehr(self):
        prefer_options = ["", "return=minimal", "return=representation"]
        for prefer in prefer_options:
            ehr_id = UUID("a6ddec4c-a68a-49ef-963e-3e0bc1970a28")
            self.run_create_test(ehr_id, self.ehr_status_dto(), prefer, lambda: self.controller.createEhr("1.0.3", None, prefer, None))

    def test_create_ehr_with_status(self):
        prefer_options = ["", "return=minimal", "return=representation"]
        for prefer in prefer_options:
            ehr_status = self.ehr_status_dto()
            ehr_id = UUID("a6ddec4c-a68a-49ef-963e-3e0bc1970a28")
            self.run_create_test(ehr_id, ehr_status, prefer, lambda: self.controller.createEhr("1.0.3", None, prefer, ehr_status))

    def test_create_ehr_with_id(self):
        prefer_options = ["", "return=minimal", "return=representation"]
        for prefer in prefer_options:
            ehr_id = UUID("a6ddec4c-a68a-49ef-963e-3e0bc1970a28")
            self.run_create_test(ehr_id, self.ehr_status_dto(), prefer, lambda: self.controller.createEhrWithId("1.0.3", None, prefer, str(ehr_id), None))

    def test_create_ehr_with_id_and_status(self):
        prefer_options = ["", "return=minimal", "return=representation"]
        for prefer in prefer_options:
            ehr_id = UUID("2eee20ea-67cc-449f-95bc-1dbdf6d3d0c1")
            ehr_status = self.ehr_status_dto()
            self.run_create_test(ehr_id, ehr_status, prefer, lambda: self.controller.createEhrWithId("1.0.3", None, prefer, str(ehr_id), ehr_status))

    def test_create_ehr_with_id_invalid_uuid(self):
        with self.assertRaises(InvalidApiParameterException) as context:
            self.controller.createEhrWithId("1.0.3", None, None, "invalid", None)
        self.assertEqual(str(context.exception), "EHR ID format not a UUID")

    def test_get_ehr_by_id_invalid_uuid(self):
        with self.assertRaises(ObjectNotFoundException) as context:
            self.controller.getEhrById("not a uuid")
        self.assertEqual(str(context.exception), "EHR not found, in fact, only UUID-type IDs are supported")

    def test_get_ehr_by_id_not_exist(self):
        self.mock_ehr_service.getEhrStatus.side_effect = ObjectNotFoundException("ehr", "No EHR found with given ID: 46e8518f-e9b7-45de-b214-1588466d71d6")
        
        with self.assertRaises(ObjectNotFoundException) as context:
            self.controller.getEhrById("46e8518f-e9b7-45de-b214-1588466d71d6")
        self.assertEqual(str(context.exception), "No EHR found with given ID: 46e8518f-e9b7-45de-b214-1588466d71d6")

    def test_get_ehr_by(self):
        ehr_id = UUID("0c1f9fce-05bd-4f6f-a558-fc27a2140795")
        ehr_status = self.ehr_status_dto()
        
        self.mock_ehr_service.getEhrStatus.return_value = self.create_result(ehr_id)
        
        response = self.controller.getEhrById(str(ehr_id))
        self.assert_ehr_response_data(response, ehr_id, ehr_status)

    def test_get_ehr_by_subject_not_found(self):
        self.mock_ehr_service.findBySubject.return_value = None
        
        with self.assertRaises(ObjectNotFoundException) as context:
            self.controller.getEhrBySubject("test_subject", "some:external:id")
        self.assertEqual(str(context.exception), "No EHR with supplied subject parameters found")

    def test_get_ehr_by_subject(self):
        ehr_id = UUID("d2c04bbd-fbd5-4a39-ade3-848a336037ed")
        ehr_status = self.ehr_status_dto()

        self.mock_ehr_service.findBySubject.return_value = ehr_id
        self.mock_ehr_service.getEhrStatus.return_value = self.create_result(ehr_id)

        response = self.controller.getEhrBySubject("test_subject", "some:external:id")
        self.assert_ehr_response_data(response, ehr_id, ehr_status)

    def assert_ehr_response_data(self, response, ehr_id, ehr_status):
        self.assertEqual(response.status_code, HttpStatus.OK)
        self.assertIn('Location', response.headers)
        self.assertEqual(response.headers['Location'], f"{self.CONTEXT_PATH}/ehr/{ehr_id}")

        self.assert_response_data_body(response, ehr_id, ehr_status)

if __name__ == '__main__':
    unittest.main()
