"""Justice: the law is enforced.

One job: track every case from open to closed. Each case carries a case
id, the statute it is charged under, a status (open, charged, closed),
the assigned office, and a timestamped history of status transitions.

The backlog answers "what is still open, and where."

This registry records and tracks. It does not try cases.
"""

import datetime
import json
import os

STATUSES = ("open", "charged", "closed")

# Allowed forward transitions. Reopening a closed case starts a new
# case id; history is never rewritten.
TRANSITIONS = {
    "open": ("charged", "closed"),
    "charged": ("closed",),
    "closed": (),
}


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Justice:
    def __init__(self, path):
        self.path = path
        self.records = []
        self._load()

    # -- persistence -------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                doc = json.load(f)
            self.records = doc.get("cases", [])

    def _save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)),
                    exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"cases": self.records}, f, indent=1)

    def _find(self, case_id):
        for c in self.records:
            if c["case_id"] == case_id:
                return c
        raise KeyError("unknown case id: %s" % case_id)

    # -- cases -------------------------------------------------------
    def open_case(self, case_id, statute, office, timestamp=None):
        if not case_id:
            raise ValueError("case_id is required")
        if any(c["case_id"] == case_id for c in self.records):
            raise ValueError("case id already exists: %s" % case_id)
        rec = {
            "case_id": case_id,
            "statute": statute,
            "status": "open",
            "office": office,
            "history": [{"status": "open",
                         "at": timestamp or _now(),
                         "note": "case opened"}],
        }
        self.records.append(rec)
        self._save()
        return rec

    def transition(self, case_id, new_status, note="", timestamp=None):
        if new_status not in STATUSES:
            raise ValueError("status must be one of %s" % (STATUSES,))
        rec = self._find(case_id)
        allowed = TRANSITIONS[rec["status"]]
        if new_status not in allowed:
            raise ValueError("cannot move case %s from %s to %s"
                             % (case_id, rec["status"], new_status))
        rec["status"] = new_status
        rec["history"].append({"status": new_status,
                               "at": timestamp or _now(),
                               "note": note})
        self._save()
        return rec

    def cases(self, status=None, office=None):
        out = self.records
        if status is not None:
            if status not in STATUSES:
                raise ValueError("status must be one of %s" % (STATUSES,))
            out = [c for c in out if c["status"] == status]
        if office is not None:
            out = [c for c in out if c["office"] == office]
        return out

    def backlog(self):
        """Open and charged cases by office. What is still unresolved,
        and where it sits."""
        counts = {}
        for c in self.records:
            if c["status"] == "closed":
                continue
            key = (c["office"], c["status"])
            counts[key] = counts.get(key, 0) + 1
        return [{"office": o, "status": s, "cases": n}
                for (o, s), n in sorted(counts.items())]
