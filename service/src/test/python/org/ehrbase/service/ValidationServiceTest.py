import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from EHR import (ValidationService, ValidationException, ConstraintViolationException,
                          KnowledgeCacheServiceImp, ExternalTerminologyValidation, EhrStatusDto,
                          Composition, DvCodedText, DvText, PartySelf, PartyRef, GenericId,
                          OriginalVersion, Archetyped, TemplateId, FeederAudit, CodePhrase,
                          TerminologyParam, ContributionCreateDto, AuditDetails)

class NopTerminologyValidation(ExternalTerminologyValidation):
    def validate(self, param: TerminologyParam):
        return Exception("Terminology validation is disabled")

    def supports(self, param: TerminologyParam) -> bool:
        return False

    def expand(self, param: TerminologyParam):
        return []

class ValidationServiceTest(unittest.TestCase):
    
    def setUp(self):
        self.knowledge_cache_service = mock.create_autospec(KnowledgeCacheServiceImp)
        self.server_config = mock.create_autospec(ServerConfig)
        self.object_provider = mock.create_autospec(ObjectProvider)

        self.spy_service = mock.create_autospec(ValidationService)
        self.object_provider.getIfAvailable.return_value = NopTerminologyValidation()
        
        self.service = self.spy_service

    @staticmethod
    def valid_audit_details():
        audit = AuditDetails()
        audit.set_system_id("local")
        audit.set_change_type(DvCodedText("creation", CodePhrase("openehr", "249")))
        audit.set_description(DvText("lorem ipsum"))
        audit.set_committer(PartySelf(PartyRef(GenericId("123-abc", "test"), "de.vitagroup", "PERSON")))
        return audit

    @staticmethod
    def test_versions():
        version = OriginalVersion()
        version.set_lifecycle_state(DvCodedText("complete", CodePhrase("openehr", "532")))
        version.set_commit_audit(ValidationServiceTest.valid_audit_details())
        return [version]

    def run_check_composition(self, consumer):
        composition = Composition()
        composition.set_name(DvText("Name"))
        composition.set_archetype_node_id("archetype-node-id")
        composition.set_language("DE-de")
        composition.set_category(DvCodedText("cat", "42"))
        composition.set_composer(PartySelf())
        composition.set_archetype_details(
            Archetyped("openEHR-EHR-COMPOSITION.test.v1", TemplateId(), "1.0.3")
        )
        consumer(composition)
        self.service.check(composition)

    def test_check_composition_invalid_without_name(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_name(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: name")

    def test_check_composition_invalid_without_archetype_node_id(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_archetype_node_id(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: archetype_node_id")

    def test_check_composition_invalid_without_language(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_language(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: language")

    def test_check_composition_invalid_without_category(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_category(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: category")

    def test_check_composition_invalid_without_composer(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_composer(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: composer")

    def test_check_composition_invalid_without_archetype(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_archetype_details(None))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: archetype details")

    def test_check_composition_invalid_without_archetype_template_id(self):
        with self.assertRaises(ValidationException) as context:
            self.run_check_composition(lambda composition: composition.set_archetype_details(Archetyped()))
        self.assertEqual(str(context.exception), "Composition missing mandatory attribute: archetype details/template_id")

    def test_check_composition_invalid_constraints(self):
        with self.assertRaises(ConstraintViolationException) as context:
            self.run_check_composition(lambda composition: None)
        self.assertIn("Invariant Category_validity failed", str(context.exception))

    # Parameterized test examples
    @patch('your_module.loadComposition')
    def test_check_composition_valid_fixtures(self, mock_load):
        # This should contain logic to load valid compositions
        pass

    @patch('your_module.loadComposition')
    def test_check_composition_invalid_fixtures(self, mock_load):
        # This should contain logic to load invalid compositions
        pass

    def run_check_ehr_status(self, ehr_status_dto):
        self.service.check(ehr_status_dto)

    def test_check_ehr_status_invalid_subject_missing(self):
        ehr_status_dto = EhrStatusDto(subject=None)
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertEqual(str(context.exception), "Message at /subject (/subject):  Attribute subject of class EHR_STATUS does not match existence 1..1")

    def test_check_ehr_status_invalid_is_queryable_missing(self):
        ehr_status_dto = EhrStatusDto(is_queryable=None)
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertEqual(str(context.exception), "Message at /is_queryable (/is_queryable):  Attribute is_queryable of class EHR_STATUS does not match existence 1..1")

    def test_check_ehr_status_invalid_is_modifiable_missing(self):
        ehr_status_dto = EhrStatusDto(is_modifiable=None)
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertEqual(str(context.exception), "Message at /is_modifiable (/is_modifiable):  Attribute is_modifiable of class EHR_STATUS does not match existence 1..1")

    def test_check_ehr_status_invalid_uid(self):
        ehr_status_dto = EhrStatusDto(uid=HierObjectId())
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertEqual(str(context.exception), "Message at /value (/uid/value):  Attribute value of class HIER_OBJECT_ID does not match existence 1..1")

    def test_check_ehr_status_invalid_name(self):
        ehr_status_dto = EhrStatusDto(name=DvText())
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertEqual(str(context.exception), "Message at /value (/name/value):  Attribute value of class DV_TEXT does not match existence 1..1")

    def test_check_ehr_status_invalid_subject_party_ref(self):
        ehr_status_dto = EhrStatusDto(subject=PartySelf(PartyRef()))
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertIn("Message at /namespace (/subject/external_ref/namespace):  Attribute namespace of class PARTY_REF does not match existence 1..1", str(context.exception))

    def test_check_ehr_status_invalid_archetype_details(self):
        ehr_status_dto = EhrStatusDto(archetype_details=Archetyped())
        with self.assertRaises(ValidationException) as context:
            self.run_check_ehr_status(ehr_status_dto)
        self.assertIn("Message at /rm_version (/archetype_details/rm_version):  Attribute rm_version of class ARCHETYPED does not match existence 1..1", str(context.exception))

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()















# import pytest
# from unittest.mock import MagicMock, patch
# from my_project.service import ValidationService
# from my_project.exceptions import ValidationException
# from my_project.models import Composition, EhrStatusDto, ContributionCreateDto
# from my_project.utils import load_composition, load_ehr_status


# class TestValidationService:
#     def setup_method(self):
#         self.knowledge_cache_service = MagicMock()
#         self.server_config = MagicMock()
#         self.object_provider = MagicMock()
#         self.validation_service = ValidationService(
#             self.knowledge_cache_service, self.server_config, self.object_provider
#         )

#     def valid_audit_details(self):
#         return {
#             "system_id": "local",
#             "change_type": {"value": "creation", "code": "249"},
#             "description": "lorem ipsum",
#             "committer": {"id": "123-abc", "namespace": "de.vitagroup", "type": "PERSON"}
#         }

#     def test_check_composition_invalid_without_name(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: name"):
#             composition = Composition(name=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_archetype_node_id(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: archetype_node_id"):
#             composition = Composition(archetype_node_id=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_language(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: language"):
#             composition = Composition(language=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_category(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: category"):
#             composition = Composition(category=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_composer(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: composer"):
#             composition = Composition(composer=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_archetype_details(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: archetype details"):
#             composition = Composition(archetype_details=None)
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_without_archetype_template_id(self):
#         with pytest.raises(ValidationException, match="Composition missing mandatory attribute: archetype details/template_id"):
#             composition = Composition(archetype_details={"template_id": None})
#             self.validation_service.check(composition)

#     def test_check_composition_invalid_constraints(self):
#         with pytest.raises(ValidationException) as exc_info:
#             composition = Composition()
#             self.validation_service.check(composition)
#         assert "Invariant Category_validity failed" in str(exc_info.value)

#     def test_check_ehr_status_invalid_subject_missing(self):
#         ehr_status = EhrStatusDto(subject=None)
#         with pytest.raises(ValidationException, match="Message at /subject (/subject):  Attribute subject of class EHR_STATUS does not match existence 1..1"):
#             self.validation_service.check(ehr_status)

#     def test_check_ehr_status_invalid_is_queryable_missing(self):
#         ehr_status = EhrStatusDto(is_queryable=None)
#         with pytest.raises(ValidationException, match="Message at /is_queryable (/is_queryable):  Attribute is_queryable of class EHR_STATUS does not match existence 1..1"):
#             self.validation_service.check(ehr_status)

#     def test_check_ehr_status_invalid_is_modifiable_missing(self):
#         ehr_status = EhrStatusDto(is_modifiable=None)
#         with pytest.raises(ValidationException, match="Message at /is_modifiable (/is_modifiable):  Attribute is_modifiable of class EHR_STATUS does not match existence 1..1"):
#             self.validation_service.check(ehr_status)

#     def test_contribution_invalid_missing_versions(self):
#         contribution = ContributionCreateDto(versions=None)
#         with pytest.raises(ValidationException, match="Message at /versions (/versions):  Versions must not be empty"):
#             self.validation_service.check(contribution)

#         contribution = ContributionCreateDto(versions=[])
#         with pytest.raises(ValidationException, match="Message at /versions (/versions):  Versions must not be empty"):
#             self.validation_service.check(contribution)

#     def test_contribution_valid(self):
#         contribution = ContributionCreateDto(versions=[{"state": "complete"}], audit=self.valid_audit_details())
#         self.validation_service.check(contribution)

#     @pytest.mark.parametrize("composition_data", load_composition)
#     def test_check_composition_valid_fixtures(self, composition_data):
#         composition = load_composition(composition_data)
#         self.validation_service.check(composition)

#     @pytest.mark.parametrize("ehr_data", load_ehr_status)
#     def test_check_ehr_status_valid_fixtures(self, ehr_data):
#         ehr_status = load_ehr_status(ehr_data)
#         self.validation_service.check(ehr_status)
