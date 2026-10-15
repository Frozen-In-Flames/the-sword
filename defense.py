"""Defense: deter, and win if deterrence fails.

One job: know what the nation can field. The capability inventory records
every military capability: name, domain (land, air, sea, space, cyber),
readiness level, quantity, and home unit.

This registry records and tracks. It does not command forces.

Candidate capabilities can be imported from Mergers and Acquisitions For
Peace (https://github.com/Frozen-In-Flames/mergers-and-acquisitions-for-peace):
its ranked acquirer/target pairs carry gap_concepts_top, capabilities the
target holds that the acquirer lacks. Imported records are flagged
source "mafp" and status "candidate": screened, not fielded.
"""

import datetime
import json
import os

DOMAINS = ("land", "air", "sea", "space", "cyber")

READINESS_LEVELS = {
    1: "concept",
    2: "prototype",
    3: "fielded",
    4: "sustained",
}


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Defense:
    def __init__(self, path):
        self.path = path
        self.capabilities = []
        self._next_id = 1
        self._load()

    # -- persistence -------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                doc = json.load(f)
            self.capabilities = doc.get("capabilities", [])
            ids = [c.get("id", 0) for c in self.capabilities]
            self._next_id = max(ids, default=0) + 1

    def _save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)),
                    exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"capabilities": self.capabilities}, f, indent=1)

    # -- inventory ---------------------------------------------------
    def register_capability(self, name, domain, readiness, quantity=1,
                            home_unit="", source="registry",
                            status="fielded"):
        if domain not in DOMAINS:
            raise ValueError("domain must be one of %s" % (DOMAINS,))
        if readiness not in READINESS_LEVELS:
            raise ValueError("readiness must be 1-4")
        if quantity < 1:
            raise ValueError("quantity must be at least 1")
        rec = {
            "id": self._next_id,
            "name": name,
            "domain": domain,
            "readiness": readiness,
            "readiness_label": READINESS_LEVELS[readiness],
            "quantity": int(quantity),
            "home_unit": home_unit,
            "source": source,
            "status": status,
            "registered_at": _now(),
        }
        self._next_id += 1
        self.capabilities.append(rec)
        self._save()
        return rec

    def inventory(self, domain=None, status=None):
        out = self.capabilities
        if domain is not None:
            out = [c for c in out if c["domain"] == domain]
        if status is not None:
            out = [c for c in out if c["status"] == status]
        return out

    def readiness_summary(self):
        """Counts by domain and readiness. Labeled, no estimates."""
        summary = {d: {lbl: 0 for lbl in READINESS_LEVELS.values()}
                   for d in DOMAINS}
        for c in self.capabilities:
            if c["status"] != "fielded":
                continue
            summary[c["domain"]][c["readiness_label"]] += c["quantity"]
        return summary

    # -- M&A for Peace integration -----------------------------------
    def import_acquisition_pairs(self, json_path, domain, min_score=0.0,
                                 limit=None):
        """Import candidate capabilities from a Mergers and Acquisitions
        For Peace --format json output file.

        Each pair's gap_concepts_top becomes a candidate capability record
        (status "candidate", source "mafp:<ACQ>-><TGT>", readiness 2
        "prototype"), linked to the pair and its score. The M&A output
        does not say which domain a concept belongs to, so the operator
        assigns `domain`. Screening input, not fielded inventory.
        """
        if domain not in DOMAINS:
            raise ValueError("domain must be one of %s" % (DOMAINS,))
        with open(json_path) as f:
            doc = json.load(f)
        pairs = doc.get("pairs", [])
        imported = []
        for p in pairs:
            score = p.get("screening_score", p.get("score"))
            if score is None or score < min_score:
                continue
            for concept in p.get("gap_concepts_top", []):
                rec = self.register_capability(
                    name="candidate: %s" % concept,
                    domain=domain,
                    readiness=2,
                    quantity=1,
                    home_unit="",
                    source="mafp:%s->%s" % (p.get("acquirer"),
                                            p.get("target")),
                    status="candidate",
                )
                rec["mafp_score"] = score
                rec["mafp_rationale"] = p.get("rationale", "")
                imported.append(rec)
                if limit is not None and len(imported) >= limit:
                    self._save()
                    return imported
        self._save()
        return imported
