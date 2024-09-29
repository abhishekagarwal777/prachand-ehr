import json
import unittest
from unittest import mock
from jsonschema import validate, ValidationError
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.codesystem import CodeSystem
from fhirclient.models.valueset import ValueSet
from ehrbase.openehr.sdk.validation.webtemplate import DvCodedTextValidator
from ehrbase.openehr.sdk.webtemplate.model import WebTemplateNode


class DvCodedTextIT(unittest.TestCase):

    def setUp(self):
        self.fhir_terminology_validator = FhirTerminologyValidation("https://r4.ontoserver.csiro.au/fhir")
        self.validator = DvCodedTextValidator(self.fhir_terminology_validator)

    def parse_node(self, file):
        with open(file, 'r') as f:
            return WebTemplateNode(**json.load(f))

    def test_validate_unsupported_external_terminology(self):
        node = self.parse_node("webtemplate_nodes/dv_codedtext_unsupported.json")
        dv_coded_text = DvCodedText(
            "Iodine-deficiency related thyroid disorders and allied conditions",
            CodePhrase(TerminologyId("ICD10"), "E01")
        )

        result = self.validator.validate(dv_coded_text, node)
        self.assertTrue(not result)

    def test_validate_fhir_code_system(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "final")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_codesystem.json")

        result = self.validator.validate(DvCodedText("Final", code_phrase), node)
        self.assertTrue(not result)

    def test_validate_fhir_code_system_wrong_terminology_id(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/name-use"), "usual")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_codesystem.json")

        result = self.validator.validate(DvCodedText("Usual", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_code_system_wrong_code(self):
        code_phrase = CodePhrase(TerminologyId("http://hl7.org/fhir/observation-status"), "casual")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_codesystem.json")

        result = self.validator.validate(DvCodedText("Casual", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_value_set(self):
        code_phrase = CodePhrase(TerminologyId("http://terminology.hl7.org/CodeSystem/v3-EntityNameUseR2"), "ANON")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_valueset.json")

        result = self.validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(not result)

    def test_validate_fhir_value_set_wrong_terminology_id(self):
        code_phrase = CodePhrase(TerminologyId("http://snomed.info/sct"), "ANON")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_valueset.json")

        result = self.validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(len(result) > 0)

    def test_validate_fhir_value_set_wrong_code(self):
        code_phrase = CodePhrase(TerminologyId("http://terminology.hl7.org/CodeSystem/v3-EntityNameUseR2"), "UKN")
        node = self.parse_node("webtemplate_nodes/dv_codedtext_fhir_valueset.json")

        result = self.validator.validate(DvCodedText("Anonymous", code_phrase), node)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()
