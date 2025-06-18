
import unittest
from normalize.normalizer import normalize_text

class TestNormalizer(unittest.TestCase):
    def test_typical_case(self):
        self.assertEqual(normalize_text("luv u 4ever"), "love you forever")

    def test_repeated_chars(self):
        self.assertIn("great", normalize_text("gr8!!!"))

    def test_spell_correction(self):
        self.assertIn("love", normalize_text("luvv"))

if __name__ == '__main__':
    unittest.main()
