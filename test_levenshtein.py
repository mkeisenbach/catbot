import unittest
from levenshtein_distance import levenshtein

class LevenshteinTests(unittest.TestCase):
    def test_empty_strings(self):
        self.assertEquals(levenshtein("", ""), 0)

    def test_compare_against_empty(self):
        self.assertEquals(levenshtein("aaa", ""), 3)
        self.assertEquals(levenshtein("", "bbb"), 3)

    def test_equal_strings(self):
        self.assertEquals(levenshtein("a", "a"), 0)
        self.assertEquals(levenshtein("Hello", "Hello"), 0)

    def test_single_character_replacement(self):
        self.assertEquals(levenshtein("a", "b"), 1)
        self.assertEquals(levenshtein("H_llo", "Hello"), 1)

    def test_multople_character_replacement(self):
        self.assertEquals(levenshtein("aa", "bb"), 2)
        self.assertEquals(levenshtein("World", "Wires"), 3)

    def test_truncated_string_length(self):
        self.assertEquals(levenshtein("aaa", "a"), 2)
        self.assertEquals(levenshtein("b", "bbb"), 2)
        self.assertEquals(levenshtein("Hello World", "Hello"), 6)

# TODO(andre): Check if case-insensitive comparisons should work or not
#    def test_equal_strings_case_insensitive(self):
#       self.assertEquals(levenshtein("a", "A"), 0)
#       self.assertEquals(levenshtein("Hello", "hElLo"), 0)

if __name__ == '__main__':
    unittest.main()
