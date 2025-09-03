import unittest
from parser import ProgressParser


class ParserTest(unittest.TestCase):
    def test_unknown_time(self):
        p = ProgressParser()
        (pr, t) = p.parse("[download]   9.5% of ~ 195.84MiB at  604.34KiB/s ETA Unknown (frag 2/32)")
        self.assertEqual(pr, 10)
        self.assertIsNone(t)

    def test_two_digits(self):
        p = ProgressParser()
        (pr, t) = p.parse("[download]   12.1% of ~ 195.84MiB at  604.34KiB/s ETA 2:33 (frag 2/32)")
        self.assertEqual(pr, 12)
        self.assertEqual(t, "2:33")


if __name__ == "__main__":
    unittest.main()
