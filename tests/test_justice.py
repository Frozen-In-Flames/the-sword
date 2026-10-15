import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from justice import Justice


class TestJustice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.j = Justice(os.path.join(self.tmp, "justice.json"))

    def test_open_and_transition(self):
        rec = self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        self.assertEqual(rec["status"], "open")
        self.assertEqual(len(rec["history"]), 1)
        rec = self.j.transition("2026-001", "charged", note="indictment")
        self.assertEqual(rec["status"], "charged")
        self.assertEqual(len(rec["history"]), 2)
        rec = self.j.transition("2026-001", "closed", note="convicted")
        self.assertEqual(rec["status"], "closed")

    def test_illegal_transition_rejected(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        self.j.transition("2026-001", "closed")
        with self.assertRaises(ValueError):
            self.j.transition("2026-001", "charged")

    def test_backward_transition_rejected(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        self.j.transition("2026-001", "charged")
        with self.assertRaises(ValueError):
            self.j.transition("2026-001", "open")

    def test_duplicate_case_rejected(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        with self.assertRaises(ValueError):
            self.j.open_case("2026-001", "18 USC 1343", "Dallas")

    def test_backlog(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        self.j.open_case("2026-002", "18 USC 1956", "Dallas")
        self.j.open_case("2026-003", "18 USC 1343", "Houston")
        self.j.transition("2026-003", "charged")
        self.j.transition("2026-002", "closed")
        bl = self.j.backlog()
        dallas = [r for r in bl if r["office"] == "Dallas"]
        self.assertEqual(dallas[0]["cases"], 1)
        self.assertFalse(any(r["office"] == "Houston" and
                             r["status"] == "open" for r in bl))

    def test_cases_filter(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        self.j.open_case("2026-002", "18 USC 1956", "Houston")
        self.assertEqual(len(self.j.cases(status="open")), 2)
        self.assertEqual(len(self.j.cases(office="Houston")), 1)

    def test_persistence(self):
        self.j.open_case("2026-001", "18 USC 1343", "Dallas")
        j2 = Justice(os.path.join(self.tmp, "justice.json"))
        self.assertEqual(len(j2.cases()), 1)


if __name__ == "__main__":
    unittest.main()
