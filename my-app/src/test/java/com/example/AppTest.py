import unittest

class AppTest(unittest.TestCase):
    """
    Unit test for simple App.
    """

    def __init__(self, test_name):
        super().__init__(test_name)

    @classmethod
    def suite(cls):
        return unittest.TestLoader().loadTestsFromTestCase(cls)

    def test_app(self):
        # Rigorous Test :-)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
