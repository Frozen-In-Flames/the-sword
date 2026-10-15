# the-sword

Security core for a new nation. Step 4 of the Nation Kit's 17-to-1
reverse-SDG build sequence.

## The idea

Every federal agency is one class with one job. This build centralizes the
three security classes:

- `Defense` — one job: deter, and win if deterrence fails. Capability
  inventory: name, domain (land, air, sea, space, cyber), readiness level
  (1 concept, 2 prototype, 3 fielded, 4 sustained), quantity, home unit.
  Imports candidate capabilities from Mergers and Acquisitions For Peace
  ranked pairs (screened, not fielded).
- `Border` — one job: know who and what crosses. Pseudonymous crossing
  log with direction, port, timestamp, and flag categories; summaries by
  port and period carry counts only, never identities.
- `Justice` — one job: the law is enforced. Case tracker with case id,
  statute, status (open, charged, closed), assigned office, and a
  timestamped transition history. The backlog shows what is still open
  and where it sits.

## SDGs unlocked

This build unlocks **SDG 16 (Peace, Justice and Strong Institutions)**.
Peace comes from deterrence you can inventory, justice from cases that
cannot quietly die in a drawer, and strong institutions from a border log
that counts without surveilling.

It is step 4 of the 17-to-1 sequence because security is a prerequisite,
not an outcome. The ledger (step 1) funds it, the registry (step 2)
records what it protects, the shield (step 3) keeps the population alive
to be worth protecting. You cannot have safety nets, commons, or
prosperity without first answering: what can we field, who crossed, and
which cases are still open.

## Mergers and Acquisitions For Peace integration

`defense import-pairs` reads a `--format json` output file from
[Mergers and Acquisitions For Peace](https://github.com/Frozen-In-Flames/mergers-and-acquisitions-for-peace)
and registers each pair's gap concepts as candidate capabilities
(status `candidate`, source `mafp:<ACQ>-><TGT>`, readiness 2
"prototype"). The M&A output does not say which domain a concept belongs
to, so the operator assigns it with `--domain`. Candidates are screening
input. Nothing becomes fielded inventory except by explicit
registration.

## Usage

```bash
# Defense
python3 sword_cli.py defense register --name "F-35 squadron" --domain air \
  --readiness 3 --quantity 24 --home-unit "1st Wing"
python3 sword_cli.py defense inventory --domain air
python3 sword_cli.py defense readiness
python3 sword_cli.py defense import-pairs --json mafp-pairs.json \
  --domain air --min-score 90 --limit 10

# Border
python3 sword_cli.py border log --crosser P-001 --direction in \
  --port "El Paso" --flags goods
python3 sword_cli.py border summary --port "El Paso"
python3 sword_cli.py border flagged --flag goods

# Justice
python3 sword_cli.py justice open --case-id 2026-001 \
  --statute "18 USC 1343" --office Dallas
python3 sword_cli.py justice transition --case-id 2026-001 \
  --status charged --note indictment
python3 sword_cli.py justice backlog
```

## Honest limits

These registries record and track. They do not command forces, close
borders, or try cases. Readiness levels are the operator's assessment,
not sensor truth. The border log is pseudonymous by design: crosser ids
are opaque tokens, and summaries export counts only. Imported M&A
candidates are 10-patent screening samples from the upstream tool, not
capability audits. TRL 8: tested and demonstrated; operational use is the
gap to 9.

## License

Apache-2.0. Not advice of any kind.
