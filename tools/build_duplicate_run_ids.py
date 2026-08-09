#!/usr/bin/env python3
"""Freeze the map of run IDs that occur under more than one experiment.

Run IDs are not globally unique in this repository. `RUN_ID` is the one open
identifier pattern (`^RUN-[A-Za-z0-9._-]+$`), runs are physically namespaced
under their experiment directory, and several experiment packages named their
runs after the parameters rather than the experiment -- so
`RUN-FCP-fixed-b16-s1-t0` exists under three different experiments, holding
three different manifests.

Renumbering them would rewrite committed run artifacts, which
`tools/check_run_immutability.py` refuses by design. So the collisions stay,
and this map is the compensating control: it states exactly which IDs collide,
where, and whether the colliding manifests disagree about anything that
changes how a citation to them is read.

Why that matters, precisely (`tools/validate_ledger.py`):

    ctx.run_params[str(rec_id)] = ...   # line 265, unconditional
    ctx.register(str(rec_id), ...)      # line 266, keeps the FIRST only

For a colliding ID, `ctx.ids` therefore points at the FIRST manifest globbed
while `ctx.run_params` holds the LAST. Scale metadata and run provenance are
evaluated against those last-written parameters. If two same-named runs
disagree on `field_bits`, the report marks the ambiguity rather than silently
using one manifest for a claim the citing record never meant.
`tier_divergent: true` below marks every ID where that is not hypothetical.

Usage:
    python3 tools/build_duplicate_run_ids.py            # write the map
    python3 tools/build_duplicate_run_ids.py --check    # fail if it drifted

No manifest is read for anything but its own content, and none is modified.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

import yaml


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(REPO, "tools", "duplicate_run_ids.yaml")
SCHEMA = "duplicate-run-ids-v1"

# Mirrors tier_of_run() in tools/validate_ledger.py. Kept as a local copy
# rather than an import so this map records what the boundaries were when it
# was frozen, and a later change to the validator shows up as drift here.
def _tier(params: dict) -> str | None:
    bits = params.get("field_bits") or params.get("field_bit_size")
    if bits is None:
        return None
    bits = int(bits)
    if bits <= 32:
        return "toy"
    return "medium" if bits <= 96 else "crypto"


def collisions() -> dict:
    seen: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(REPO, "experiments", "*", "runs",
                                              "*", "manifest.yaml"))):
        try:
            body = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("run")
        except yaml.YAMLError:
            continue                      # unparseable manifests are their own error
        if not isinstance(body, dict):
            continue
        rec_id = body.get("id")
        if not rec_id:
            continue
        seen.setdefault(str(rec_id), []).append(os.path.relpath(path, REPO))

    records = {}
    for rec_id, paths in sorted(seen.items()):
        if len(paths) < 2:
            continue
        entries, tiers = [], set()
        for rel in sorted(paths):
            body = (yaml.safe_load(open(os.path.join(REPO, rel),
                                        encoding="utf-8")) or {}).get("run") or {}
            params = (body.get("inputs") or {}).get("parameters") or {}
            tier = _tier(params)
            tiers.add(tier)
            entries.append({
                "path": rel,
                "experiment_id": body.get("experiment_id"),
                "field_bits": params.get("field_bits")
                              or params.get("field_bit_size"),
                "tier": tier,
            })
        records[rec_id] = {
            "occurrences": entries,
            # True when the colliding manifests would not agree about the
            # scale metadata. These are the ones where an arbitrary pick
            # changes the answer rather than merely the provenance.
            "tier_divergent": len({t for t in tiers if t is not None}) > 1,
        }
    return records


def document() -> dict:
    records = collisions()
    divergent = sorted(k for k, v in records.items() if v["tier_divergent"])
    return {
        "schema": SCHEMA,
        "generated_by": "tools/build_duplicate_run_ids.py",
        "note": (
            "Frozen inventory of run IDs occurring under more than one "
            "experiment. This file records a defect; it does not bless it. "
            "It may SHRINK as collisions are retired by superseding run "
            "records. It must never GROW: a new collision is a new defect, "
            "not something to absorb here."
        ),
        "collision_count": len(records),
        "tier_divergent_count": len(divergent),
        "tier_divergent_ids": divergent,
        "records": records,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed map does not match the tree")
    args = ap.parse_args()

    current = document()
    if not args.check:
        with open(MAP_PATH, "w", encoding="utf-8") as handle:
            yaml.safe_dump(current, handle, sort_keys=False, width=100)
        print(f"wrote {current['collision_count']} colliding run id(s) "
              f"({current['tier_divergent_count']} tier-divergent) to "
              f"{os.path.relpath(MAP_PATH, REPO)}")
        return 0

    if not os.path.exists(MAP_PATH):
        print(f"FAIL: {os.path.relpath(MAP_PATH, REPO)} is missing",
              file=sys.stderr)
        return 1
    frozen = yaml.safe_load(open(MAP_PATH, encoding="utf-8")) or {}
    frozen_ids = set(frozen.get("records") or {})
    current_ids = set(current["records"])
    added = sorted(current_ids - frozen_ids)
    if added:
        print(f"FAIL: {len(added)} run id collision(s) not in the frozen map. "
              f"A new collision is a new defect; give the run a distinct id "
              f"rather than adding it here:", file=sys.stderr)
        for rec_id in added:
            print(f"  - {rec_id}", file=sys.stderr)
        return 1
    removed = sorted(frozen_ids - current_ids)
    if removed:
        print(f"note: {len(removed)} collision(s) no longer occur; regenerate "
              f"to prune")
    print(f"PASS: no new run id collisions ({len(current_ids)} known)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
