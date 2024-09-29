import unittest

from ehrbase.openehr.sdk.terminology.openehr import TerminologyService
from ehrbase.service import TerminologyServiceImp


class TerminologyServiceTest(unittest.TestCase):

    def setUp(self):
        self.terminology_service = TerminologyServiceImp()

    def test_terminology(self):
        self.assertIsNotNone(self.terminology_service.terminology("openehr"))
        self.assertIsNotNone(self.terminology_service.terminology("openehr", "ja"))

    def test_code_set(self):
        self.assertIsNotNone(self.terminology_service.codeSet("openehr_integrity_check_algorithms"))
        self.assertIsNotNone(self.terminology_service.codeSet("openehr_integrity_check_algorithms", "ja"))

    def test_code_set_for_id(self):
        self.assertIsNotNone(self.terminology_service.codeSetForId("INTEGRITY_CHECK_ALGORITHMS"))
        self.assertIsNotNone(self.terminology_service.codeSetForId("INTEGRITY_CHECK_ALGORITHMS", "pt"))

    def test_has_terminology(self):
        self.assertTrue(self.terminology_service.hasTerminology("openehr"))
        self.assertTrue(self.terminology_service.hasTerminology("openehr", "ja"))

    def test_has_code_set(self):
        self.assertTrue(self.terminology_service.hasCodeSet("integrity check algorithms"))
        self.assertTrue(self.terminology_service.hasCodeSet("integrity check algorithms", "pt"))

    def test_terminology_identifiers(self):
        self.assertGreater(len(self.terminology_service.terminologyIdentifiers()), 0)
        self.assertGreater(len(self.terminology_service.terminologyIdentifiers("ja")), 0)

    def test_openehr_code_sets(self):
        self.assertGreater(len(self.terminology_service.openehrCodeSets()), 0)
        self.assertGreater(len(self.terminology_service.openehrCodeSets("pt")), 0)

    def test_code_set_identifiers(self):
        self.assertGreater(len(self.terminology_service.codeSetIdentifiers()), 0)
        self.assertGreater(len(self.terminology_service.codeSetIdentifiers("ja")), 0)


if __name__ == '__main__':
    unittest.main()
