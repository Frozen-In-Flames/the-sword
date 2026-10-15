import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from defense import Defense, DOMAINS


class TestDefense(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "defense.json")
        self.d = Defense(self.path)

    def test_register_and_inventory(self):
        rec = self.d.register_capability("F-35 squadron", "air", 3,
                                         quantity=24,
                                         home_unit="1st Wing")
        self.assertEqual(rec["id"], 1)
        self.assertEqual(rec["readiness_label"], "fielded")
        inv = self.d.inventory()
        self.assertEqual(len(inv), 1)
        self.assertEqual(len(self.d.inventory(domain="sea")), 0)

    def test_bad_domain_rejected(self):
        with self.assertRaises(ValueError):
            self.d.register_capability("x", "orbit", 3)

    def test_bad_readiness_rejected(self):
        with self.assertRaises(ValueError):
            self.d.register_capability("x", "air", 9)

    def test_persistence(self):
        self.d.register_capability("Patriot battery", "land", 4,
                                   quantity=6, home_unit="2nd ADA")
        d2 = Defense(self.path)
        self.assertEqual(len(d2.inventory()), 1)
        self.assertEqual(d2.inventory()[0]["name"], "Patriot battery")

    def test_readiness_summary_counts_fielded_only(self):
        self.d.register_capability("a", "air", 3, quantity=2)
        self.d.register_capability("b", "air", 2, quantity=5,
                                   status="candidate")
        s = self.d.readiness_summary()
        self.assertEqual(s["air"]["fielded"], 2)
        self.assertEqual(s["air"]["prototype"], 0)

    def test_import_acquisition_pairs(self):
        doc = {"pairs": [
            {"acquirer": "TDG", "target": "BA", "screening_score": 95.8,
             "gap_concepts_top": ["actuator", "accessory port"],
             "rationale": "shares 15 concepts"},
            {"acquirer": "TXT", "target": "BA", "screening_score": 10.0,
             "gap_concepts_top": ["air"],
             "rationale": "low"},
        ]}
        jf = os.path.join(self.tmp, "pairs.json")
        with open(jf, "w") as f:
            json.dump(doc, f)
        recs = self.d.import_acquisition_pairs(jf, "air", min_score=50.0)
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(r["status"] == "candidate" for r in recs))
        self.assertTrue(all(r["source"].startswith("mafp:") for r in recs))
        self.assertEqual(recs[0]["mafp_score"], 95.8)
        self.assertEqual(recs[0]["readiness_label"], "prototype")

    def test_import_bad_domain_rejected(self):
        jf = os.path.join(self.tmp, "pairs.json")
        with open(jf, "w") as f:
            json.dump({"pairs": []}, f)
        with self.assertRaises(ValueError):
            self.d.import_acquisition_pairs(jf, "orbit")


if __name__ == "__main__":
    unittest.main()
