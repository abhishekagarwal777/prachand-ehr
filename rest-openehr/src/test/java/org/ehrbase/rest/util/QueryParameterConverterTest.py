import unittest

class QueryParameterConverter:
    def convert(self, query_string):
        if not query_string:
            return {}
        
        params = {}
        pairs = query_string.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value
            else:
                params[pair] = ''
        return params


class QueryParameterConverterTest(unittest.TestCase):

    def converter(self):
        return QueryParameterConverter()

    def test_convert_empty(self):
        result = self.converter().convert("")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_convert_single_parameter(self):
        result = self.converter().convert("param=foo")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result["param"], "foo")

    def test_convert_single_parameter_empty(self):
        result = self.converter().convert("param=")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result["param"], "")

    def test_convert_single_parameter_only(self):
        result = self.converter().convert("invalid")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertIn("invalid", result)
        self.assertEqual(result["invalid"], "")

    def test_convert_multiple_parameter(self):
        result = self.converter().convert("param=foo&other=")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result["param"], "foo")
        self.assertEqual(result["other"], "")


if __name__ == "__main__":
    unittest.main()
