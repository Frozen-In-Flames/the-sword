"""Border: know who and what crosses.

One job: record every crossing. The crossing log stores a pseudonymous
crosser id (never a real identity in this registry), direction
(in/out), port, timestamp, and flag categories.

Summaries by port and period answer "how much crossed, where, when"
without identifying anyone.

This registry records and tracks. It does not close borders.
"""

import datetime
import json
import os

DIRECTIONS = ("in", "out")

FLAG_CATEGORIES = ("none", "goods", "vehicle", "livestock", "secondary")


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class Border:
    def __init__(self, path):
        self.path = path
        self.crossings = []
        self._next_id = 1
        self._load()

    # -- persistence -------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                doc = json.load(f)
            self.crossings = doc.get("crossings", [])
            ids = [c.get("id", 0) for c in self.crossings]
            self._next_id = max(ids, default=0) + 1

    def _save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)),
                    exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"crossings": self.crossings}, f, indent=1)

    # -- log ---------------------------------------------------------
    def log_crossing(self, crosser_id, direction, port,
                     timestamp=None, flags=("none",)):
        if direction not in DIRECTIONS:
            raise ValueError("direction must be in or out")
        if not port:
            raise ValueError("port is required")
        flags = list(flags)
        for fl in flags:
            if fl not in FLAG_CATEGORIES:
                raise ValueError("flag must be one of %s"
                                 % (FLAG_CATEGORIES,))
        rec = {
            "id": self._next_id,
            "crosser_id": crosser_id,
            "direction": direction,
            "port": port,
            "timestamp": timestamp or _now(),
            "flags": flags,
        }
        self._next_id += 1
        self.crossings.append(rec)
        self._save()
        return rec

    # -- summaries ---------------------------------------------------
    def summary(self, port=None, start=None, end=None):
        """Crossing counts by port and direction. Pseudonymous: no
        crosser_id leaves this function, only counts."""
        counts = {}
        for c in self.crossings:
            if port is not None and c["port"] != port:
                continue
            ts = c["timestamp"]
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue
            key = (c["port"], c["direction"])
            counts[key] = counts.get(key, 0) + 1
        return [{"port": p, "direction": d, "crossings": n}
                for (p, d), n in sorted(counts.items())]

    def flagged(self, flag):
        if flag not in FLAG_CATEGORIES:
            raise ValueError("flag must be one of %s" % (FLAG_CATEGORIES,))
        return [c for c in self.crossings if flag in c["flags"]]
