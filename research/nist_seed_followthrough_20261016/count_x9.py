#!/usr/bin/env python3
"""Exact point counts for one immutable slice of the six prime seed streams."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = REPO / "research/nist_seed_selection_20261016"
CENSUS = REPO / "research/nist_seed_provenance_20261016/census"
REPRESENTATIVES = {
    "prime239v3": 863711343,
    "prime192v2": 863966734,
    "P-521": 871002724,
    "P-256": 871696354,
    "P-384": 872952608,
    "P-224": 891607927,
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_candidates(target, start, end):
    rows = {}
    with (PREVIOUS / "raw/candidates.jsonl").open() as source:
        for line in source:
            row = json.loads(line)
            if row["target"] == target and start <= row["index"] <= end:
                rows[row["index"]] = row
    if set(rows) != set(range(start, end + 1)):
        raise AssertionError("candidate range missing or duplicated")
    return rows


def census_orders(target):
    rows = {}
    path = CENSUS / f"orders_{REPRESENTATIVES[target]}.txt"
    with path.open() as source:
        for line in source:
            i, n, nt = map(int, line.split())
            if i in rows:
                raise AssertionError("duplicate census index")
            rows[i] = (n, nt)
    return rows, path


def canonical_root(variant, p):
    roots = [int(value, 16) for value in variant["b_roots"]]
    if len(roots) != 2 or (roots[0] + roots[1]) % p:
        raise AssertionError("invalid seeded root pair")
    if p % 4 == 3:
        c = int(variant["c"], 16)
        root = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p)
        if root not in roots:
            raise AssertionError("published-style root missing")
        return root
    return roots[0]


def gp_order(p, b, stack_mib):
    # All interpolated values are integers parsed from frozen source records.
    program = (f"default(parisizemax,{stack_mib * 1048576})\n"
               f"print(ellcard(ellinit([-3,{b}],{p})))\nquit\n")
    started = time.monotonic()
    result = subprocess.run(["gp", "-q", "-f"], input=program,
                            capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError(f"gp exited {result.returncode}: {result.stderr[-1000:]}")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].isdigit():
        raise RuntimeError(f"unexpected gp result: {result.stdout[-1000:]}")
    n = int(lines[0])
    if (n - p - 1) ** 2 > 4 * p:
        raise ArithmeticError("point count outside Hasse interval")
    return n, time.monotonic() - started, result.stdout, result.stderr


def evaluate_variant(variant, p, imported, stack_mib):
    if variant["reason"] != "nonsingular":
        return {"status": "NO_CURVE", "reason": variant["reason"], "c": variant["c"]}
    b = canonical_root(variant, p)
    source = "pari_ellcard"
    elapsed = 0.0
    gp_stdout = None
    gp_stderr = None
    n = None
    if imported is not None:
        old, twist = imported
        if old:
            n, source = old, "bound_prior_ellsea_curve"
        elif p % 4 == 3 and twist:
            n, source = 2 * (p + 1) - twist, "bound_prior_ellsea_twist_identity"
    if n is None:
        n, elapsed, gp_stdout, gp_stderr = gp_order(p, b, stack_mib)
    if (n - p - 1) ** 2 > 4 * p:
        raise ArithmeticError("reused count outside Hasse interval")
    if p % 4 == 3:
        other = 2 * (p + 1) - n
    else:
        other = n  # b and -b are isomorphic when p is 1 mod 4.
    return {"status": "COUNTED", "c": variant["c"], "canonical_b": str(b),
            "canonical_order": str(n), "other_order": str(other),
            "source": source, "count_seconds": round(elapsed, 6),
            "gp_stdout": gp_stdout, "gp_stderr": gp_stderr}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=tuple(REPRESENTATIVES), required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--stack-mib", type=int, default=512)
    parser.add_argument("--attempt", default="", help="suffix for immutable retry")
    args = parser.parse_args()
    targets_path = PREVIOUS / "targets.json"
    target = next(x for x in json.loads(targets_path.read_text())
                  if x["name"] == args.target)
    if not 1 <= args.start <= args.end <= target["candidate_index"]:
        parser.error("range outside stream")
    p = int(target["p"])
    candidate_path = PREVIOUS / "raw/candidates.jsonl"
    candidates = load_candidates(args.target, args.start, args.end)
    census, census_path = census_orders(args.target)
    output_dir = HERE / "raw/x9" / args.target
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"-{args.attempt}" if args.attempt else ""
    output = output_dir / f"{args.start:05d}-{args.end:05d}{suffix}.jsonl"
    partial = output.with_suffix(".jsonl.partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    gp_version = subprocess.run(["gp", "--version-short"], capture_output=True,
                                text=True, check=True).stdout.strip()
    header = {"record": "run", "command": sys.argv, "target": args.target,
              "start": args.start, "end": args.end, "gp_version": gp_version,
              "python": platform.python_version(), "pid": os.getpid(),
              "stack_mib": args.stack_mib, "watchdog_seconds_per_count": 600,
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "script_sha256": digest(Path(__file__)),
              "targets_sha256": digest(targets_path),
              "candidates_sha256": digest(candidate_path),
              "census_sha256": digest(census_path)}
    with partial.open("w") as sink:
        sink.write(json.dumps(header, sort_keys=True) + "\n")
        sink.flush()
        for i in range(args.start, args.end + 1):
            row = candidates[i]
            first = row["variants"]["nist_fips_186_2"]
            second = row["variants"]["ansi_x9_62_1998"]
            started = time.monotonic()
            result = {"target": args.target, "index": i, "seed": row["seed"],
                      "same_c": first["c"] == second["c"]}
            try:
                old = census.get(i)
                if first["reason"] == "nonsingular" and old is None:
                    raise AssertionError("valid published mapping absent from census")
                result["unmasked"] = evaluate_variant(first, p, old, args.stack_mib)
                if first["c"] == second["c"]:
                    if first["reason"] != second["reason"] or first["b_roots"] != second["b_roots"]:
                        raise AssertionError("equal coefficients have different roots")
                    result["strict_x9"] = {"status": "REUSED_UNMASKED"}
                else:
                    result["strict_x9"] = evaluate_variant(second, p, None, args.stack_mib)
                result["status"] = "COMPLETE"
                if i == target["candidate_index"]:
                    published_b = int(target["published_b"])
                    item = result["unmasked"]
                    if item["status"] != "COUNTED":
                        raise AssertionError("published curve uncounted")
                    order = (int(item["canonical_order"]) if published_b == int(item["canonical_b"])
                             else int(item["other_order"]))
                    if order != int(target["published_subgroup_order"]):
                        raise AssertionError("published order mismatch")
                    result["anchor_order_matches"] = True
            except Exception as exc:
                result["status"] = "INDETERMINATE"
                result["error_type"] = type(exc).__name__
                result["error"] = str(exc)
            result["elapsed_seconds"] = round(time.monotonic() - started, 6)
            sink.write(json.dumps(result, sort_keys=True) + "\n")
            sink.flush()
    os.replace(partial, output)
    print(json.dumps({"path": str(output), "sha256": digest(output),
                      "rows": args.end - args.start + 1}, sort_keys=True))


if __name__ == "__main__":
    main()
