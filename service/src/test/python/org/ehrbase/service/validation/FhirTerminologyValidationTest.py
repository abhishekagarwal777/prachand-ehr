import unittest
from unittest.mock import Mock
from my_package import FhirTerminologyValidation, ValueSetConverter
from ca.uhn.fhir.context import FhirContext
from jsonpath_ng import jsonpath, parse
from com.nedap.archie.rm.datavalues import DvCodedText
from hl7.fhir.r4.model import ValueSet, ValueSetExpansionComponent, ValueSetExpansionContainsComponent
import random
import string


class FhirTerminologyValidationTest(unittest.TestCase):

    def test_guarantee_prefix(self):
        self.assertEqual("url=ABC", FhirTerminologyValidation.guarantee_prefix("url=", "url=ABC"))
        self.assertEqual("url=ABC", FhirTerminologyValidation.guarantee_prefix("url=", "ABC"))
        self.assertIsNone(FhirTerminologyValidation.guarantee_prefix("url=", ""))
        self.assertEqual("xyz=XYZ&url=ABC", FhirTerminologyValidation.guarantee_prefix("url=", "xyz=XYZ&url=ABC"))

    def test_render_templ(self):
        ref = FhirTerminologyValidation.SUPPORTS_CODE_SYS_TEMPL.format("abc", "123")
        render1 = FhirTerminologyValidation.render_templ(FhirTerminologyValidation.SUPPORTS_CODE_SYS_TEMPL, "abc", "123")
        self.assertEqual(ref, render1)

        render2 = FhirTerminologyValidation.render_templ(FhirTerminologyValidation.SUPPORTS_CODE_SYS_TEMPL, "abc", "123", "xyz")
        self.assertEqual(ref, render2)

        with self.assertRaises(ValueError):
            FhirTerminologyValidation.render_templ(FhirTerminologyValidation.SUPPORTS_CODE_SYS_TEMPL, "abc")

    def test_value_set_converter(self):
        values = self.any_value_set()
        json = FhirContext.for_r4().new_json_parser().encode_resource_to_string(values)
        ctx = parse(json)

        dv = ValueSetConverter.convert(ctx)
        self.assertEqual(len(values.get_expansion().get_contains()), len(dv))

    def test_string_join(self):
        params = []
        req_param = "&".join(params)
        self.assertEqual("", req_param)

        params = ["a"]
        req_param = "&".join(params)
        self.assertEqual("a", req_param)

        params = ["a", "b"]
        req_param = "&".join(params)
        self.assertEqual("a&b", req_param)

    @staticmethod
    def any_value_set():
        values = [FhirTerminologyValidationTest.any_value_set_expansion_contains_component() for _ in range(16)]
        ext = ValueSetExpansionComponent()
        ext.set_id(FhirTerminologyValidationTest.any_string())
        ext.set_contains(values)

        value_set = ValueSet()
        value_set.set_id(FhirTerminologyValidationTest.any_string())
        value_set.set_expansion(ext)

        return value_set

    @staticmethod
    def any_value_set_expansion_contains_component():
        cmp = ValueSetExpansionContainsComponent()
        cmp.set_id(FhirTerminologyValidationTest.any_string())
        cmp.set_code(FhirTerminologyValidationTest.any_string())
        cmp.set_system(FhirTerminologyValidationTest.any_string())
        cmp.set_display(FhirTerminologyValidationTest.any_string())
        return cmp

    @staticmethod
    def any_string():
        return ''.join(random.choices(string.ascii_letters, k=random.randint(1, 16)))


if __name__ == '__main__':
    unittest.main()





# #MAVEN
# <dependency>
#     <groupId>com.nedap.archie</groupId>
#     <artifactId>archie</artifactId>
#     <version>VERSION_NUMBER</version> <!-- Specify the version you need -->
# </dependency>

# #GRADLE
# implementation 'com.nedap.archie:archie:VERSION_NUMBER' // Specify the version you need
