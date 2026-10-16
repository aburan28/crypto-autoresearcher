#!/usr/bin/env python3
"""Exhaustively decide the published cofactor-one profile on a prime stream.

Exact 2- and 3-torsion detects definite composite group orders before SEA.
Every remaining candidate gets an exact PARI point count; the other b root
is derived by the twist order formula or same-order isomorphism.  X9.62
near-prime status on torsion-rejected curves remains unassessed.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

from cypari2 import Pari

from evaluate_candidates import checks, prime_order_count


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--stack-mib", type=int, default=512)
    args = parser.parse_args()
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    target = targets[args.target]
    if target["kind"] != "prime" or not 1 <= args.start <= args.end <= target["candidate_index"]:
        raise ValueError("invalid prime target or range")
    candidate_source = ROOT / "raw" / "candidates.jsonl"
    torsion_source = ROOT / "raw" / "prime_3torsion_screen.jsonl"
    torsion = {}
    with torsion_source.open() as source:
        source.readline()
        for line in source:
            row = json.loads(line)
            if row.get("target") == args.target and args.start <= row["index"] <= args.end:
                torsion[row["index"]] = row
    output_dir = ROOT / "raw" / "family_evaluations" / args.target
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.start:05d}-{args.end:05d}.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    pari = Pari()
    pari.allocatemem(args.stack_mib * 1024 * 1024)
    p = int(target["p"])
    records = 0
    with candidate_source.open() as source, partial.open("w") as sink:
        sink.write(json.dumps({"record": "run", "command": sys.argv, "target": args.target,
                               "start": args.start, "end": args.end,
                               "candidate_sha256": digest(candidate_source),
                               "torsion_sha256": digest(torsion_source),
                               "script_sha256": digest(Path(__file__)),
                               "stack_mib": args.stack_mib, "python": platform.python_version(),
                               "pid": os.getpid(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                              sort_keys=True) + "\n")
        for line in source:
            row = json.loads(line)
            if row["target"] != args.target or not args.start <= row["index"] <= args.end:
                continue
            prior = torsion.get(row["index"])
            if prior is None or prior["target"] != args.target:
                raise ArithmeticError("missing 3-torsion screen")
            started = time.monotonic()
            result = {"target": args.target, "index": row["index"], "seed": row["seed"],
                      "prior_status": prior["prior_status"], "strict_x9_same_c":
                      row["variants"]["nist_fips_186_2"]["c"] == row["variants"]["ansi_x9_62_1998"]["c"]}
            try:
                if prior["prior_status"] != "ODD_ORDER_PENDING_COUNT":
                    result["status"] = "REJECT_" + prior["prior_status"]
                    result["family_accept_canonical"] = False
                    result["family_accept_other"] = False
                else:
                    variant = row["variants"]["nist_fips_186_2"]
                    roots = [int(value, 16) for value in variant["b_roots"]]
                    if len(roots) != 2:
                        raise ArithmeticError("expected two b roots")
                    candidate_states = {roots[0]: prior["root_low"], roots[1]: prior["root_high"]}
                    c = int(variant["c"], 16)
                    canonical_b = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p) if p % 4 == 3 else roots[0]
                    other_b = p - canonical_b
                    if canonical_b not in candidate_states or other_b not in candidate_states:
                        raise ArithmeticError("root assignment failed")
                    result.update({"canonical_b": hex(canonical_b), "other_b": hex(other_b),
                                   "canonical_3torsion": candidate_states[canonical_b],
                                   "other_3torsion": candidate_states[other_b]})
                    if candidate_states[canonical_b] == candidate_states[other_b] == "DIVISIBLE_BY_3":
                        result["status"] = "REJECT_THREE_TORSION"
                        result["family_accept_canonical"] = False
                        result["family_accept_other"] = False
                    else:
                        count_b = canonical_b if candidate_states[canonical_b] == "PENDING_COUNT" else other_b
                        counted = prime_order_count(pari, p, count_b)
                        if count_b == canonical_b:
                            canonical_order = counted
                            other_order = 2 * (p + 1) - counted if p % 4 == 3 else counted
                        else:
                            other_order = counted
                            canonical_order = 2 * (p + 1) - counted if p % 4 == 3 else counted
                        canonical = checks(pari, canonical_order, p, 1)
                        other = checks(pari, other_order, p, 1)
                        if candidate_states[canonical_b] == "DIVISIBLE_BY_3" and canonical["family_accept"]:
                            raise ArithmeticError("3-torsion contradicts canonical prime order")
                        if candidate_states[other_b] == "DIVISIBLE_BY_3" and other["family_accept"]:
                            raise ArithmeticError("3-torsion contradicts other prime order")
                        result.update({"status": "COUNTED", "counted_b": hex(count_b),
                                       "canonical": canonical, "other": other,
                                       "family_accept_canonical": canonical["family_accept"],
                                       "family_accept_other": other["family_accept"]})
                if row["index"] == target["candidate_index"]:
                    if result["status"] != "COUNTED":
                        raise ArithmeticError("published anchor rejected")
                    published_b = int(target["published_b"])
                    published = result["canonical"] if published_b == int(result["canonical_b"], 16) else result["other"]
                    result["anchor_matches"] = int(published["order"]) == int(target["published_subgroup_order"]) and published["family_accept"]
                    if not result["anchor_matches"]:
                        raise ArithmeticError("published anchor count or criteria mismatch")
            except Exception as error:
                result = {"target": args.target, "index": row["index"], "seed": row["seed"],
                          "status": "INDETERMINATE", "error_type": type(error).__name__, "error": str(error)}
            result["elapsed_seconds"] = round(time.monotonic() - started, 6)
            sink.write(json.dumps(result, sort_keys=True) + "\n")
            sink.flush()
            records += 1
    if records != args.end - args.start + 1:
        raise ArithmeticError(f"incomplete shard: {records} rows")
    os.replace(partial, output)
    print(json.dumps({"target": args.target, "start": args.start, "end": args.end,
                      "rows": records, "output": str(output), "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
