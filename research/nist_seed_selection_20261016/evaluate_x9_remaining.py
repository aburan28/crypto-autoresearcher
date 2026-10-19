#!/usr/bin/env python3
"""Complete both X9-reference prime mappings, reusing bound exact counts."""

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
FAMILY_PLAN = ROOT / "raw" / "family_campaign" / "plan.json"
FAMILY_SUMMARY = ROOT / "raw" / "family_campaign" / "family_summary.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_family(target, start, end):
    plan = json.loads(FAMILY_PLAN.read_text())
    summary = json.loads(FAMILY_SUMMARY.read_text())
    if summary["plan_sha256"] != digest(FAMILY_PLAN):
        raise ArithmeticError("family summary does not bind plan")
    retry = ROOT / "raw" / "family_campaign" / "retry_plan.json"
    if summary.get("retry_plan_sha256") != (digest(retry) if retry.exists() else None):
        raise ArithmeticError("family summary does not bind retry plan")
    rows = {}
    shards = {}
    for key, segment in summary["segment_manifest"].items():
        if segment["target"] != target or segment["end"] < start or segment["start"] > end:
            continue
        path = ROOT / key
        file_sha = digest(path)
        if summary["shard_sha256"].get(key) != file_sha:
            raise ArithmeticError(f"family shard hash mismatch: {key}")
        shards[key] = file_sha
        with path.open() as source:
            header = json.loads(next(source))
            if (header["candidate_sha256"] != plan["candidate_sha256"] or
                    header["script_sha256"] != plan["evaluator_sha256"] or
                    header["start"] != segment["start"] or
                    header["end"] != segment["header_end"]):
                raise ArithmeticError(f"family shard header mismatch: {key}")
            for line in source:
                row = json.loads(line)
                if not segment["start"] <= row["index"] <= segment["end"]:
                    raise ArithmeticError(f"family segment row outside bound: {key}")
                if start <= row["index"] <= end:
                    if row["index"] in rows:
                        raise ArithmeticError(f"duplicate family index: {row['index']}")
                    rows[row["index"]] = row
    if set(rows) != set(range(start, end + 1)):
        raise ArithmeticError("family range incomplete")
    return rows, shards


def roots_for(row, p):
    variant = row["variant"]
    roots = [int(value, 16) for value in variant["b_roots"]]
    if len(roots) != 2:
        raise ArithmeticError("expected two seeded roots")
    c = int(variant["c"], 16)
    canonical = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p) if p % 4 == 3 else roots[0]
    if canonical not in roots or p - canonical not in roots:
        raise ArithmeticError("seeded-root assignment failed")
    return canonical, p - canonical


def count_variant(pari, p, variant):
    if variant["reason"] != "nonsingular":
        return {"status": "NO_CURVE_" + variant["reason"].upper(), "c": variant["c"]}
    canonical_b, other_b = roots_for({"variant": variant}, p)
    canonical_order = prime_order_count(pari, p, canonical_b)
    other_order = 2 * (p + 1) - canonical_order if p % 4 == 3 else canonical_order
    return {"status": "COUNTED", "c": variant["c"],
            "canonical_b": hex(canonical_b), "other_b": hex(other_b),
            "canonical": checks(pari, canonical_order, p, 1),
            "other": checks(pari, other_order, p, 1)}


def evaluate(row, family, p, pari):
    result = {"index": row["index"], "seed": row["seed"], "target": row["target"]}
    unmasked = row["variants"]["nist_fips_186_2"]
    strict = row["variants"]["ansi_x9_62_1998"]
    if unmasked["reason"] == "nonsingular" and family["status"] == "COUNTED":
        canonical_b, other_b = roots_for({"variant": unmasked}, p)
        if (int(family["canonical_b"], 16) != canonical_b or
                int(family["other_b"], 16) != other_b):
            raise ArithmeticError("family count root mismatch")
        fips = {"status": "REUSED_FAMILY_COUNT", "c": unmasked["c"],
                "canonical_b": family["canonical_b"], "other_b": family["other_b"],
                "canonical": family["canonical"], "other": family["other"]}
    elif unmasked["reason"] == "nonsingular":
        fips = count_variant(pari, p, unmasked)
    else:
        fips = {"status": "NO_CURVE_" + unmasked["reason"].upper(), "c": unmasked["c"]}
    if strict["c"] == unmasked["c"]:
        if strict["reason"] != unmasked["reason"] or strict["b_roots"] != unmasked["b_roots"]:
            raise ArithmeticError("same coefficient with different curve state")
        x9 = {"status": "REUSED_UNMASKED", "c": strict["c"]}
    else:
        x9 = count_variant(pari, p, strict)
    result.update({"unmasked": fips, "strict_x9": x9,
                   "strict_x9_same_c": strict["c"] == unmasked["c"]})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--stack-mib", type=int, default=512)
    args = parser.parse_args()
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    target = targets[args.target]
    if target["kind"] != "prime" or not 1 <= args.start <= args.end <= target["candidate_index"]:
        raise ValueError("invalid target or range")
    candidate_source = ROOT / "raw" / "candidates.jsonl"
    family, family_shards = load_family(args.target, args.start, args.end)
    p = int(target["p"])
    output_dir = ROOT / "raw" / "x9_evaluations" / args.target
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.start:05d}-{args.end:05d}.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    pari = Pari()
    pari.allocatemem(args.stack_mib * 1024 * 1024)
    count = 0
    with partial.open("w") as sink, candidate_source.open() as source:
        sink.write(json.dumps({"record": "run", "command": sys.argv, "target": args.target,
                               "start": args.start, "end": args.end,
                               "candidate_sha256": digest(candidate_source),
                               "family_plan_sha256": digest(FAMILY_PLAN),
                               "family_summary_sha256": digest(FAMILY_SUMMARY),
                               "family_shard_sha256": family_shards,
                               "script_sha256": digest(Path(__file__)),
                               "stack_mib": args.stack_mib, "python": platform.python_version(),
                               "pid": os.getpid(),
                               "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                              sort_keys=True) + "\n")
        for line in source:
            row = json.loads(line)
            if row["target"] != args.target or not args.start <= row["index"] <= args.end:
                continue
            started = time.monotonic()
            try:
                result = evaluate(row, family[row["index"]], p, pari)
                if row["index"] == target["candidate_index"]:
                    fips = result["unmasked"]
                    if fips["status"] not in ("COUNTED", "REUSED_FAMILY_COUNT"):
                        raise ArithmeticError("published anchor uncounted")
                    side = "canonical" if int(fips["canonical_b"], 16) == int(target["published_b"]) else "other"
                    result["anchor_order_matches"] = (int(fips[f"{side}_b"], 16) == int(target["published_b"]) and
                                                      int(fips[side]["order"]) == int(target["published_subgroup_order"]))
                    if not result["anchor_order_matches"]:
                        raise ArithmeticError("published anchor mismatch")
            except Exception as error:
                result = {"target": args.target, "index": row["index"], "seed": row["seed"],
                          "status": "INDETERMINATE", "error_type": type(error).__name__,
                          "error": str(error)}
            result["elapsed_seconds"] = round(time.monotonic() - started, 6)
            sink.write(json.dumps(result, sort_keys=True) + "\n")
            sink.flush()
            count += 1
    if count != args.end - args.start + 1:
        raise ArithmeticError("incomplete X9 range")
    os.replace(partial, output)
    print(json.dumps({"target": args.target, "start": args.start, "end": args.end,
                      "rows": count, "output": str(output), "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
