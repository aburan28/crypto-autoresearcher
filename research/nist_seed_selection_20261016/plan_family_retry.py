#!/usr/bin/env python3
"""Freeze a disjoint retry of the interrupted family point-count campaign."""

import hashlib
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PLAN = RAW / "family_campaign" / "plan.json"
OUTPUT = RAW / "family_campaign" / "retry_plan.json"
WIDTH = {"P-521": 10, "P-384": 25, "P-224": 250, "P-256": 100,
         "prime239v3": 150, "prime192v2": 250}
ORDER = {name: i for i, name in enumerate(
    ("P-256", "prime192v2", "P-224", "prime239v3", "P-384", "P-521"))}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    plan = json.loads(PLAN.read_text())
    required = {"candidate_sha256": RAW / "candidates.jsonl",
                "torsion_screen_sha256": RAW / "prime_3torsion_screen.jsonl",
                "evaluator_sha256": ROOT / "evaluate_family_fast.py",
                "fast_controls_sha256": RAW / "fast_evaluator_controls.json"}
    if any(plan[key] != digest(path) for key, path in required.items()):
        raise ArithmeticError("original plan input changed")
    seeds = {}
    with (RAW / "candidates.jsonl").open() as source:
        for line in source:
            row = json.loads(line)
            if row["kind"] == "prime":
                seeds[(row["target"], row["index"])] = row["seed"]
    sources, retries = [], []
    for parent in plan["shards"]:
        target, start, end = parent["target"], parent["start"], parent["end"]
        path = RAW / "family_evaluations" / target / f"{start:05d}-{end:05d}.jsonl"
        partial = path.with_suffix(path.suffix + ".partial")
        if path.exists() and partial.exists():
            raise ArithmeticError(f"both complete and partial: {path}")
        present = path if path.exists() else partial if partial.exists() else None
        rows = 0
        if present:
            with present.open() as source:
                header = json.loads(next(source))
                if (header.get("record") != "run" or header.get("target") != target or
                        header.get("start") != start or header.get("end") != end or
                        header.get("candidate_sha256") != plan["candidate_sha256"] or
                        header.get("torsion_sha256") != plan["torsion_screen_sha256"] or
                        header.get("script_sha256") != plan["evaluator_sha256"]):
                    raise ArithmeticError(f"source header mismatch: {present}")
                for line in source:
                    row = json.loads(line)
                    index = start + rows
                    if (row.get("target") != target or row.get("index") != index or
                            row.get("seed") != seeds[(target, index)] or
                            row.get("status") == "INDETERMINATE"):
                        raise ArithmeticError(f"source row mismatch: {present}:{index}")
                    rows += 1
            if rows > end - start + 1 or (path.exists() and rows != end - start + 1):
                raise ArithmeticError(f"source length mismatch: {present}")
            sources.append({"path": str(present.relative_to(ROOT)),
                            "sha256": digest(present), "target": target,
                            "start": start, "end": start + rows - 1,
                            "original_end": end, "rows": rows,
                            "kind": "complete" if path.exists() else "partial_prefix"})
        first = start + rows
        for a in range(first, end + 1, WIDTH[target]):
            b = min(a + WIDTH[target] - 1, end)
            candidate = RAW / "family_evaluations" / target / f"{a:05d}-{b:05d}.jsonl"
            if candidate.exists() or candidate.with_suffix(candidate.suffix + ".partial").exists():
                raise FileExistsError(candidate)
            retries.append({"target": target, "start": a, "end": b,
                            "stack_mib": parent["stack_mib"],
                            "original_start": start, "original_end": end})
    retries.sort(key=lambda row: (ORDER[row["target"]], row["start"]))
    result = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "original_plan_sha256": digest(PLAN), "candidate_sha256": plan["candidate_sha256"],
              "torsion_screen_sha256": plan["torsion_screen_sha256"],
              "evaluator_sha256": plan["evaluator_sha256"],
              "fast_controls_sha256": plan["fast_controls_sha256"],
              "max_workers": 1, "per_shard_watchdog_seconds": 7200,
              "source_segments": sources, "retry_shards": retries}
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"retry_shards": len(retries), "source_segments": len(sources),
                      "sha256": digest(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
