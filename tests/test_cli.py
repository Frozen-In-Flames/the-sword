import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sword_cli


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def run_cli(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sword_cli.main(["--data-dir", self.tmp] + argv)
        self.assertEqual(rc, 0)
        return buf.getvalue()

    def test_defense_flow(self):
        out = self.run_cli(["defense", "register", "--name", "F-35 squadron",
                        "--domain", "air", "--readiness", "3",
                        "--quantity", "24", "--home-unit", "1st Wing"])
        rec = json.loads(out)
        self.assertEqual(rec["name"], "F-35 squadron")
        out = self.run_cli(["defense", "inventory"])
        self.assertIn("F-35 squadron", out)
        out = self.run_cli(["defense", "readiness"])
        self.assertIn("fielded", out)

    def test_defense_import_pairs(self):
        jf = os.path.join(self.tmp, "pairs.json")
        with open(jf, "w") as f:
            json.dump({"pairs": [
                {"acquirer": "TDG", "target": "BA", "screening_score": 95.8,
                 "gap_concepts_top": ["actuator"],
                 "rationale": "shares 15 concepts"}]}, f)
        out = self.run_cli(["defense", "import-pairs", "--json", jf,
                        "--domain", "air"])
        self.assertIn("imported 1 candidate", out)
        out = self.run_cli(["defense", "inventory", "--status", "candidate"])
        self.assertIn("candidate: actuator", out)

    def test_border_flow(self):
        out = self.run_cli(["border", "log", "--crosser", "P-001",
                        "--direction", "in", "--port", "El Paso"])
        rec = json.loads(out)
        self.assertEqual(rec["direction"], "in")
        out = self.run_cli(["border", "summary"])
        self.assertIn("El Paso", out)

    def test_justice_flow(self):
        out = self.run_cli(["justice", "open", "--case-id", "2026-001",
                        "--statute", "18 USC 1343", "--office", "Dallas"])
        rec = json.loads(out)
        self.assertEqual(rec["status"], "open")
        out = self.run_cli(["justice", "transition", "--case-id", "2026-001",
                        "--status", "charged"])
        rec = json.loads(out)
        self.assertEqual(rec["status"], "charged")
        out = self.run_cli(["justice", "backlog"])
        self.assertIn("Dallas", out)


if __name__ == "__main__":
    unittest.main()
