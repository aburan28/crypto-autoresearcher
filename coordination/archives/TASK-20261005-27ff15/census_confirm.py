#!/usr/bin/env python3
"""Report-only census confirmation for TASK-20261005-27ff15 (T-1 CENSUS).

For each id in DEC-20261005-138b51 and DEC-20261005-98a823
withheld_contracts.ids, state whether it appears in
coordination/archives/TASK-20261005-2af213/template-census.json with status
`approved` and empty run_dirs. Reads only; edits no record.

    python3 coordination/archives/TASK-20261005-27ff15/census_confirm.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CENSUS = "coordination/archives/TASK-20261005-2af213/template-census.json"
DECISIONS = ("DEC-20261005-138b51", "DEC-20261005-98a823")


def main() -> int:
    census = json.loads((REPO / CENSUS).read_text())
    rows = {r["experiment_id"]: r for r in census["rows"]}
    table = []
    for did in DECISIONS:
        cd = yaml.safe_load((REPO / f"ledger/decisions/{did}.yaml").read_text())["coordinator_decision"]
        for eid in cd["withheld_contracts"]["ids"]:
            row = rows.get(eid)
            entry = {"id": eid, "decision_id": did, "in_census": row is not None,
                     "status": row.get("status") if row else None,
                     "run_dirs": row.get("run_dirs") if row else None}
            entry["confirmed"] = bool(row and entry["status"] == "approved" and entry["run_dirs"] == [])
            table.append(entry)
    unconfirmed = [e["id"] for e in table if not e["confirmed"]]
    summary = {"census": CENSUS, "census_schema": census.get("schema"),
               "census_rows_total": census.get("rows_total"),
               "ids_checked": len(table), "distinct_ids": len({e["id"] for e in table}),
               "by_decision": {did: {"ids": sum(e["decision_id"] == did for e in table),
                                     "confirmed": sum(e["decision_id"] == did and e["confirmed"]
                                                      for e in table)}
                               for did in DECISIONS},
               "confirmed": len(table) - len(unconfirmed), "unconfirmed": unconfirmed,
               "rows": table}
    (HERE / "census-confirmation.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
