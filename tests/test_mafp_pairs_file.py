"""The shipped demo pairs file must load through the real importer."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from defense import Defense

PAIRS = os.path.join(os.path.dirname(__file__), "..", "demo", "mafp-pairs.json")
CAVEAT = ("Screening sample only: patent portfolios are capped per run "
          "(--limit, default 10 recent patents per company). Scores are "
          "screening scores from 0 to 100, not valuations and not "
          "advice. Candidates imported from this file are screening "
          "input, not fielded inventory.")

class TestMafpPairsFile(unittest.TestCase):
    def test_file_carries_screening_caveat(self):
        import json
        with open(PAIRS) as f: doc = json.load(f)
        self.assertEqual(doc.get("screening_caveat"), CAVEAT)
        self.assertEqual(doc["tool"], "Mergers and Acquisitions For Peace")
        self.assertGreater(len(doc["pairs"]), 0)
    def test_importer_loads_generated_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Defense(os.path.join(td, "defense.json"))
            recs = d.import_acquisition_pairs(PAIRS, "air")
            self.assertGreater(len(recs), 0)
            for r in recs:
                self.assertEqual(r["status"], "candidate")
                self.assertEqual(r["readiness"], 2)
                self.assertTrue(r["source"].startswith("mafp:"))
if __name__ == "__main__": unittest.main()
