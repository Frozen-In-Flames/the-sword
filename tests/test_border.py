import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from border import Border


class TestBorder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.b = Border(os.path.join(self.tmp, "border.json"))

    def test_log_and_summary(self):
        self.b.log_crossing("P-001", "in", "El Paso",
                            timestamp="2026-10-01T08:00:00+00:00")
        self.b.log_crossing("P-002", "in", "El Paso",
                            timestamp="2026-10-01T09:00:00+00:00")
        self.b.log_crossing("P-003", "out", "San Diego",
                            timestamp="2026-10-01T10:00:00+00:00")
        s = self.b.summary()
        self.assertEqual(len(s), 2)
        elp = [r for r in s if r["port"] == "El Paso"][0]
        self.assertEqual(elp["crossings"], 2)

    def test_summary_filters(self):
        self.b.log_crossing("P-001", "in", "El Paso",
                            timestamp="2026-10-01T08:00:00+00:00")
        self.b.log_crossing("P-002", "in", "El Paso",
                            timestamp="2026-11-01T08:00:00+00:00")
        s = self.b.summary(port="El Paso", end="2026-10-15T00:00:00+00:00")
        self.assertEqual(s[0]["crossings"], 1)

    def test_summary_is_pseudonymous(self):
        self.b.log_crossing("P-SECRET", "in", "El Paso")
        for row in self.b.summary():
            self.assertNotIn("crosser_id", row)
            self.assertNotIn("P-SECRET", str(row))

    def test_flags(self):
        self.b.log_crossing("P-001", "in", "El Paso", flags=["goods"])
        self.b.log_crossing("P-002", "in", "El Paso")
        self.assertEqual(len(self.b.flagged("goods")), 1)

    def test_bad_direction_rejected(self):
        with self.assertRaises(ValueError):
            self.b.log_crossing("P-001", "sideways", "El Paso")

    def test_bad_flag_rejected(self):
        with self.assertRaises(ValueError):
            self.b.log_crossing("P-001", "in", "El Paso",
                                flags=["explosives"])

    def test_persistence(self):
        self.b.log_crossing("P-001", "in", "El Paso")
        b2 = Border(os.path.join(self.tmp, "border.json"))
        self.assertEqual(len(b2.summary()), 1)


if __name__ == "__main__":
    unittest.main()
