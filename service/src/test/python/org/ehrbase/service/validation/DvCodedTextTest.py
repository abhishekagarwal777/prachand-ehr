import json
import unittest
from unittest import mock
from unittest.mock import Mock
from my_package import DvCodedTextValidator, FhirTerminologyValidation, DvCodedText, CodePhrase, TerminologyId, ConstraintViolation, ConstraintViolationException, ExternalTerminologyValidationException, TerminologyParam


import my_package

# Example usage
my_package.DvCodedTextValidator()



class DvCodedTextTest(unittest.TestCase):

    def setUp(self):
        self.object_mapper = Mock()
        self.fhir_terminology_validation_mock = mock.Mock(spec=FhirTerminologyValidation)

    def parse_node(self, file):
        with open(file, 'r') as f:
            return json.load(f)

    def test_validate(self):
        validator = DvCodedTextValidator()

        node = self.parse_node('webtemplate_nodes/dv_codedtext.json')
        dv_coded_text = DvCodedText("First", CodePhrase(TerminologyId("local"), "at0028"))

        result = validator.validate(dv_coded_text, node)
        self.assertTrue(len(result) == 0)

        dv_coded_text = DvCodedText("Test", CodePhrase(TerminologyId("local"), "at0028"))
        result = validator.validate(dv_coded_text, node)
        self.assertEqual(len(result), 1)

        dv_coded_text = DvCodedText("First", CodePhrase(TerminologyId("local"), "at0029"))
        result = validator.validate(dv_coded_text, node)
        self.assertEqual(len(result), 1)

    def test_validate_unsupported_external_terminology(self):
        self.fhir_terminology_validation_mock.supports.return_value = False

        node = self.parse_node('webtemplate_nodes/dv_codedtext_unsupported.json')
        dv_coded_text = DvCodedText(
            "Iodine-deficiency related thyroid disorders and allied conditions",
            CodePhrase(TerminologyId("ICD10"), "E01")
        )

        result = DvCodedTextValidator(self.fhir_terminology_validation_mock).validate(dv_coded_text, node)
        self.assertTrue(len(result) == 0)

    def test_validate_fhir_code_system(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "final")

        self.fhir_terminology_validation_mock.supports.return_value = True
        tp = TerminologyParam.of_fhir("//fhir.hl7.org/CodeSystem?url=http://hl7.org/fhir/observation-status")
        tp.set_code_phrase(code_phrase)
        self.fhir_terminology_validation_mock.validate.return_value = (True, None)

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_codesystem.json')

        result = validator.validate(DvCodedText("Final", code_phrase), node)
        self.assertTrue(len(result) == 0)

    def test_validate_fhir_code_system_wrong_terminology_id(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/name-use"), "usual")

        tp = TerminologyParam.of_fhir("//fhir.hl7.org/CodeSystem?url=http://hl7.org/fhir/observation-status")
        tp.set_code_phrase(code_phrase)
        self.fhir_terminology_validation_mock.supports.return_value = True

        self.fhir_terminology_validation_mock.validate.side_effect = ConstraintViolationException(
            [ConstraintViolation("/test/dv_coded_text_fhir_value_set",
                                 "The terminology http://hl7.org/fhir/name-use must be http://hl7.org/fhir/observation-status")]
        )

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_codesystem.json')

        result = validator.validate(DvCodedText("Usual", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_code_system_wrong_code(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "casual")

        tp = TerminologyParam.of_fhir("//fhir.hl7.org/CodeSystem?url=http://hl7.org/fhir/observation-status")
        tp.set_code_phrase(code_phrase)

        self.fhir_terminology_validation_mock.supports.return_value = True
        self.fhir_terminology_validation_mock.validate.side_effect = ConstraintViolationException(
            [ConstraintViolation("/test/dv_coded_text_fhir_code_system",
                                 "The specified code 'casual' is not known to belong to the specified code system 'http://hl7.org/fhir/observation-status'")]
        )

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_codesystem.json')

        result = validator.validate(DvCodedText("Casual", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_value_set(self):
        code_phrase = CodePhrase(TerminologyId("http://terminology.hl7.org/CodeSystem/v3-EntityNameUseR2"), "UKN")

        tp = TerminologyParam.of_fhir(
            "//fhir.hl7.org/ValueSet/$expand?url=http://terminology.hl7.org/ValueSet/v3-EntityNameUseR2"
        )
        tp.set_code_phrase(code_phrase)

        self.fhir_terminology_validation_mock.supports.return_value = True
        self.fhir_terminology_validation_mock.validate.return_value = (True, None)

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_valueset.json')

        result = validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(len(result) == 0)

    def test_validate_fhir_value_set_wrong_terminology_id(self):
        code_phrase = CodePhrase(TerminologyId("http://snomed.info/sct"), "ANON")

        tp = TerminologyParam.of_fhir(
            "//fhir.hl7.org/ValueSet/$expand?url=http://terminology.hl7.org/ValueSet/v3-EntityNameUseR2"
        )
        tp.set_code_phrase(code_phrase)

        self.fhir_terminology_validation_mock.supports.return_value = True
        self.fhir_terminology_validation_mock.validate.side_effect = ConstraintViolationException(
            [ConstraintViolation("/test/dv_coded_text_fhir_value_set",
                                 "The terminology http://snomed.info/sct must be http://terminology.hl7.org/CodeSystem/v3-EntityNameUseR2")]
        )

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_valueset.json')

        result = validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_value_set_wrong_code(self):
        code_phrase = CodePhrase(TerminologyId("http://terminology.hl7.org/CodeSystem/v3-EntityNameUseR2"), "UKN")

        tp = TerminologyParam.of_fhir(
            "//fhir.hl7.org/ValueSet/$expand?url=http://terminology.hl7.org/ValueSet/v3-EntityNameUseR2"
        )
        tp.set_code_phrase(code_phrase)

        self.fhir_terminology_validation_mock.supports.return_value = True
        self.fhir_terminology_validation_mock.validate.side_effect = ConstraintViolationException(
            [ConstraintViolation("/test/dv_coded_text_fhir_value_set",
                                 "The value UKN does not match any option from value set http://terminology.hl7.org/ValueSet/v3-EntityNameUseR2")]
        )

        validator = DvCodedTextValidator(self.fhir_terminology_validation_mock)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_valueset.json')

        result = validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_fail_on_error_enabled(self):
        validation_support = FhirTerminologyValidation("https://wrong.terminology.server/fhir")
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "B")
        dv_coded_text = DvCodedText("Buccal", code_phrase)

        validator = DvCodedTextValidator(validation_support)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_valueset.json')

        with self.assertRaises(ExternalTerminologyValidationException):
            validator.validate(dv_coded_text, node)

    def test_fail_on_error_disabled(self):
        validation_support = FhirTerminologyValidation("https://wrong.terminology.server/fhir")
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "B")
        dv_coded_text = DvCodedText("Buccal", code_phrase)

        validator = DvCodedTextValidator(validation_support)
        node = self.parse_node('webtemplate_nodes/dv_codedtext_fhir_valueset.json')

        with self.assertRaises(ExternalTerminologyValidationException):
            validator.validate(dv_coded_text, node)

if __name__ == '__main__':
    unittest.main()
