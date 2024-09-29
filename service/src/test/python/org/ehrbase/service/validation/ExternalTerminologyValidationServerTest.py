import unittest
from unittest import mock
from unittest.mock import Mock
from my_package import FhirTerminologyValidation, TerminologyParam
from com.nedap.archie.rm.datavalues import DvCodedText



import com.nedap.archie.rm.datavalues.*;

// Example usage


class ExternalTerminologyValidationServerTest(unittest.TestCase):

    @mock.patch('my_package.FhirTerminologyValidation')
    def test_should_retrieve_value_set(self, mock_fhir_terminology_validation):
        # Mock the FhirTerminologyValidation initialization and method behavior
        mock_fhir_terminology_validation.return_value.expand.return_value = [
            DvCodedText("Buccal", "B"),
            DvCodedText("Distal", "D"),
            DvCodedText("Distoclusal", "DO"),
            DvCodedText("Distoincisal", "DI"),
            # Add additional mock DvCodedText objects as needed
        ]

        try:
            tsserver = FhirTerminologyValidation("https://r4.ontoserver.csiro.au/fhir/", True)
        except Exception as e:
            self.fail()

        tp = TerminologyParam.of_service_api("//hl7.org/fhir/R4")
        tp.set_operation("expand")
        tp.set_parameter("http://hl7.org/fhir/ValueSet/surface")

        result = tsserver.expand(tp)
        for e in result:
            print(e.get_value())

        self.assertEqual(result[0].get_defining_code().get_code_string(), "B")
        self.assertEqual(result[0].get_value(), "Buccal")
        self.assertEqual(result[1].get_defining_code().get_code_string(), "D")
        self.assertEqual(result[1].get_value(), "Distal")
        self.assertEqual(result[2].get_defining_code().get_code_string(), "DO")
        self.assertEqual(result[2].get_value(), "Distoclusal")
        self.assertEqual(result[3].get_defining_code().get_code_string(), "DI")
        self.assertEqual(result[3].get_value(), "Distoincisal")

        self.assertEqual(len(result), 11)


if __name__ == '__main__':
    unittest.main()
