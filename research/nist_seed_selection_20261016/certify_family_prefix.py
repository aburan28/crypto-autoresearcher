#!/usr/bin/env python3
"""Independently certify accepted curves in the frozen pre-retry snapshot."""

import hashlib
import json
import os
from pathlib import Path

from cypari2 import Pari

from certify_prime_orders import certify


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "raw" / "family_campaign" / "retry_plan.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "family_campaign" / "prefix_certificates.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    plan = json.loads(PLAN.read_text())
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    pari = Pari()
    source_hashes = {}
    accepted = []
    for segment in plan["source_segments"]:
        path = ROOT / segment["path"]
        if digest(path) != segment["sha256"]:
            raise ArithmeticError(f"frozen source changed: {path}")
        source_hashes[segment["path"]] = segment["sha256"]
        with path.open() as source:
            header = json.loads(next(source))
            if (header["candidate_sha256"] != plan["candidate_sha256"] or
                    header["script_sha256"] != plan["evaluator_sha256"]):
                raise ArithmeticError(f"source header changed: {path}")
            for line in source:
                row = json.loads(line)
                for side in ("canonical", "other"):
                    if row.get(f"family_accept_{side}"):
                        accepted.append((segment["path"], row, side))
    accepted.sort(key=lambda item: (item[1]["target"], item[1]["index"], item[2]))
    with partial.open("x") as sink:
        sink.write(json.dumps({"record": "certificate_run", "retry_plan_sha256": digest(PLAN),
                               "candidate_sha256": plan["candidate_sha256"],
                               "source_sha256": source_hashes, "expected_branches": len(accepted),
                               "method": "independent affine scalar multiplication and Hasse uniqueness"},
                              sort_keys=True) + "\n")
        for source, row, side in accepted:
            target = row["target"]
            p = int(targets[target]["p"])
            b = int(row[f"{side}_b"], 16)
            n = int(row[side]["order"])
            result = certify(f"{target}:{row['index']}:{side}", p, b, n, pari)
            result.update({"target": target, "index": row["index"], "seed": row["seed"],
                           "side": side, "source": source,
                           "strict_x9_same_c": row["strict_x9_same_c"]})
            sink.write(json.dumps(result, sort_keys=True) + "\n")
            sink.flush()
            if not result["order_certified"]:
                raise ArithmeticError(f"independent order certificate failed: {result['name']}")
    os.replace(partial, output)
    print(json.dumps({"certified_branches": len(accepted), "sha256": digest(output)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
