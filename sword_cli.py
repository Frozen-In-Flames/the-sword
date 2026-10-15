#!/usr/bin/env python3
"""the-sword CLI: security core for a new nation.

Subcommands:
  defense register --name N --domain D --readiness R [--quantity Q]
                   [--home-unit U]
  defense inventory [--domain D] [--status S]
  defense readiness
  defense import-pairs --json PATH --domain D [--min-score S] [--limit N]
  border log --crosser ID --direction in|out --port P [--flags F,...]
             [--timestamp T]
  border summary [--port P] [--start T] [--end T]
  border flagged --flag F
  justice open --case-id ID --statute S --office O
  justice transition --case-id ID --status S [--note N]
  justice cases [--status S] [--office O]
  justice backlog

Global: --data-dir DIR (default: data/)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from defense import Defense, DOMAINS
from border import Border, FLAG_CATEGORIES
from justice import Justice, STATUSES


def cmd_defense(args):
    d = Defense(os.path.join(args.data_dir, "defense.json"))
    if args.action == "register":
        rec = d.register_capability(args.name, args.domain, args.readiness,
                                    quantity=args.quantity,
                                    home_unit=args.home_unit)
        print(json.dumps(rec, indent=1))
    elif args.action == "inventory":
        for c in d.inventory(domain=args.domain, status=args.status):
            print("%-4d %-28s %-6s r%d x%-4d %-14s %s [%s]" % (
                c["id"], c["name"][:28], c["domain"], c["readiness"],
                c["quantity"], c["home_unit"][:14], c["status"],
                c["source"]))
    elif args.action == "readiness":
        print(json.dumps(d.readiness_summary(), indent=1))
    elif args.action == "import-pairs":
        recs = d.import_acquisition_pairs(args.json, args.domain,
                                          min_score=args.min_score,
                                          limit=args.limit)
        print("imported %d candidate capabilities from %s"
              % (len(recs), args.json))


def cmd_border(args):
    b = Border(os.path.join(args.data_dir, "border.json"))
    if args.action == "log":
        flags = args.flags.split(",") if args.flags else ["none"]
        rec = b.log_crossing(args.crosser, args.direction, args.port,
                             timestamp=args.timestamp, flags=flags)
        print(json.dumps(rec, indent=1))
    elif args.action == "summary":
        for row in b.summary(port=args.port, start=args.start,
                             end=args.end):
            print("%-18s %-3s %d" % (row["port"], row["direction"],
                                     row["crossings"]))
    elif args.action == "flagged":
        for c in b.flagged(args.flag):
            print("%-6d %-12s %-3s %-18s %s" % (
                c["id"], c["crosser_id"][:12], c["direction"], c["port"],
                ",".join(c["flags"])))


def cmd_justice(args):
    j = Justice(os.path.join(args.data_dir, "justice.json"))
    if args.action == "open":
        rec = j.open_case(args.case_id, args.statute, args.office)
        print(json.dumps(rec, indent=1))
    elif args.action == "transition":
        rec = j.transition(args.case_id, args.status, note=args.note)
        print(json.dumps(rec, indent=1))
    elif args.action == "cases":
        for c in j.cases(status=args.status, office=args.office):
            print("%-12s %-20s %-8s %s" % (
                c["case_id"], c["statute"][:20], c["status"], c["office"]))
    elif args.action == "backlog":
        for row in j.backlog():
            print("%-18s %-8s %d" % (row["office"], row["status"],
                                     row["cases"]))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sword_cli.py",
                                 description="the-sword: security core")
    ap.add_argument("--data-dir", default="data",
                    help="data directory (default: data/)")
    sub = ap.add_subparsers(dest="area", required=True)

    # defense
    pd = sub.add_parser("defense")
    da = pd.add_subparsers(dest="action", required=True)
    r = da.add_parser("register")
    r.add_argument("--name", required=True)
    r.add_argument("--domain", required=True, choices=DOMAINS)
    r.add_argument("--readiness", required=True, type=int,
                   choices=[1, 2, 3, 4])
    r.add_argument("--quantity", type=int, default=1)
    r.add_argument("--home-unit", default="")
    da.add_parser("readiness")
    inv = da.add_parser("inventory")
    inv.add_argument("--domain", choices=DOMAINS)
    inv.add_argument("--status")
    imp = da.add_parser("import-pairs")
    imp.add_argument("--json", required=True,
                     help="M&A for Peace --format json output file")
    imp.add_argument("--domain", required=True, choices=DOMAINS,
                     help="domain to assign imported candidates")
    imp.add_argument("--min-score", type=float, default=0.0)
    imp.add_argument("--limit", type=int, default=None)

    # border
    pb = sub.add_parser("border")
    ba = pb.add_subparsers(dest="action", required=True)
    lg = ba.add_parser("log")
    lg.add_argument("--crosser", required=True)
    lg.add_argument("--direction", required=True, choices=("in", "out"))
    lg.add_argument("--port", required=True)
    lg.add_argument("--flags", default="")
    lg.add_argument("--timestamp", default=None)
    sm = ba.add_parser("summary")
    sm.add_argument("--port", default=None)
    sm.add_argument("--start", default=None)
    sm.add_argument("--end", default=None)
    fl = ba.add_parser("flagged")
    fl.add_argument("--flag", required=True, choices=FLAG_CATEGORIES)

    # justice
    pj = sub.add_parser("justice")
    ja = pj.add_subparsers(dest="action", required=True)
    op = ja.add_parser("open")
    op.add_argument("--case-id", required=True)
    op.add_argument("--statute", required=True)
    op.add_argument("--office", required=True)
    tr = ja.add_parser("transition")
    tr.add_argument("--case-id", required=True)
    tr.add_argument("--status", required=True, choices=STATUSES)
    tr.add_argument("--note", default="")
    cs = ja.add_parser("cases")
    cs.add_argument("--status", choices=STATUSES)
    cs.add_argument("--office")
    ja.add_parser("backlog")

    args = ap.parse_args(argv)
    if args.area == "defense":
        cmd_defense(args)
    elif args.area == "border":
        cmd_border(args)
    elif args.area == "justice":
        cmd_justice(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
