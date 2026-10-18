"""Add an independent planted-positive contradiction check to the frozen checker.

This is an additive successor: archived check.py and execute.py stay byte-for-byte
unchanged. The approved trial plan must bind this file and use it as check_argv.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent /
                       "icperf_prime63_inflight_admission_20261017"))
import check  # noqa: E402  # the archived independent checker
import execute  # noqa: E402  # the archived, hash-bound schedule and input reader


def verify(run_dir: Path, plan: Path, owner: str, epoch: int, trial_id: str,
           *, root: Path = execute.ROOT, rows: list[dict] | None = None) -> dict:
    result = check.verify(run_dir, plan, owner, epoch, trial_id, root=root, rows=rows)
    scheduled = execute.schedule() if rows is None else rows
    panel_dir = run_dir / "panel"
    receipt = execute.read(panel_dir / "receipt.json")
    archived = check.verify_archive(panel_dir, receipt)
    witnesses = {entry["cell"]: entry["root"] for entry in
                 execute.read(execute.OLD / "planted_witnesses.json")["witnesses"]}
    records = {entry["cell"]: entry for entry in receipt["cells"]}
    for row in scheduled:
        if row["kind"] != "positive":
            continue
        cell = row["id"]
        if cell not in witnesses:
            raise ValueError(f"missing independently archived positive witness: {cell}")
        # Re-evaluate the exact encoded polynomials, base, signed lifts and
        # target point before interpreting a solver's unit-ideal assertion.
        check.verify_root(row["request"], {"variables": witnesses[cell]})
        record = records[cell]
        if not record["attempted"] or not record.get("response_sha256"):
            continue
        response = json.loads(archived[cell + "/response.json"])
        if response.get("status") == "certified_no_solution":
            raise ValueError(
                f"planted positive contradiction in {cell}: independently "
                "satisfying witness and certified_no_solution response")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--epoch", required=True, type=int)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.run_dir, args.plan, args.owner, args.epoch,
                            args.trial_id), sort_keys=True))


if __name__ == "__main__":
    main()
