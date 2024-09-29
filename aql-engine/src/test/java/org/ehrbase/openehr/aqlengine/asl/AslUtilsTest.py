import unittest
from your_module import AslUtils  # Replace with the actual module name

class TestAslUtils(unittest.TestCase):

    def test_translate_aql_like_pattern_to_sql(self):
        # Test cases from the Java test class
        self.assertEqual(AslUtils.translate_aql_like_pattern_to_sql("abc"), "abc")
        self.assertEqual(AslUtils.translate_aql_like_pattern_to_sql("X\\\\\\?\\*%_*?X"), "X\\\\?*\\%\\_%_X")
        self.assertEqual(AslUtils.translate_aql_like_pattern_to_sql("\\\\\\?\\*%_*?X"), "\\\\?*\\%\\_%_X")
        self.assertEqual(AslUtils.translate_aql_like_pattern_to_sql("X%_*?X\\\\\\?\\*"), "X\\%\\_%_X\\\\?*")

if __name__ == '__main__':
    unittest.main()
