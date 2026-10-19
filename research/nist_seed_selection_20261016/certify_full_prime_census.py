#!/usr/bin/env python3
"""Certify every prime-order seeded branch in the six-stream census."""

import datetime as dt
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

from cypari2 import Pari

from certify_prime_orders import certify


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RAW = ROOT / "raw"
CENSUS = REPO / "research" / "nist_seed_provenance_20261016" / "census"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = RAW / "full_prime_order_certificates.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    cross_path = RAW / "full_census_crosscheck_v4.json"
    cross = json.loads(cross_path.read_text())
    if cross["status"] != "validated" or cross["totals"]["broad_family_both_seeded_roots"] != 69:
        raise ArithmeticError("full census cross-check is not validated")
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    candidates = {rep: {} for rep in cross["streams"]}
    with (RAW / "candidates.jsonl").open() as source:
        for line in source:
            row = json.loads(line)
            if row["target"] in candidates:
                candidates[row["target"]][row["index"]] = row
    inputs = {str(cross_path.relative_to(REPO)): sha(cross_path),
              str((RAW / "candidates.jsonl").relative_to(REPO)): sha(RAW / "candidates.jsonl")}
    cases = []
    pari = Pari()
    for rep, stream in sorted(cross["streams"].items()):
        run = stream["run"]
        p = int(targets[rep]["p"])
        orders_path = CENSUS / f"orders_{run}.txt"
        inputs[str(orders_path.relative_to(REPO))] = sha(orders_path)
        orders = {i: (n, nt) for i, n, nt in
                  (map(int, line.split()) for line in orders_path.read_text().splitlines())}
        for i in stream["broad_family_both_seeded_roots"]:
            candidate = candidates[rep][i]
            variant = candidate["variants"]["nist_fips_186_2"]
            roots = [int(x, 16) for x in variant["b_roots"]]
            if len(roots) != 2 or variant["reason"] != "nonsingular":
                raise ArithmeticError(f"missing seeded roots: {rep}/{i}")
            if p % 4 == 3:
                c = int(variant["c"], 16)
                b0 = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p)
            else:
                b0 = roots[0]
            if {b0, p-b0} != set(roots):
                raise ArithmeticError(f"candidate root mismatch: {rep}/{i}")
            n0, nt = orders[i]
            branch_orders = (("canonical", b0, n0),
                             ("other", p-b0, nt if p % 4 == 3 else n0))
            for side, b, n in branch_orders:
                if n and bool(pari.isprime(n)) and n > 2**160 and n*n > 16*p and n != p and all(pow(p,k,n)!=1 for k in range(1,21)):
                    cases.append((rep, run, i, candidate["seed"], side, p, b, n))
    if len(cases) != 82:
        raise ArithmeticError(f"expected 82 accepted root branches; found {len(cases)}")
    started = dt.datetime.now(dt.timezone.utc)
    start_monotonic = time.monotonic()
    with partial.open("x") as sink:
        sink.write(json.dumps({"record": "certificate_run", "status": "running",
                               "command": sys.argv, "started_utc": started.isoformat(),
                               "python": platform.python_version(),
                               "pari_version": str(pari("version()")),
                               "method": "independent affine scalar multiplication and Hasse uniqueness",
                               "expected_branches": len(cases),
                               "script_sha256": sha(Path(__file__)),
                               "input_sha256": inputs}, sort_keys=True) + "\n")
        sink.flush()
        for rep, run, i, seed, side, p, b, n in cases:
            result = certify(f"{rep}:{i}:{side}", p, b, n, pari)
            result.update({"record": "certificate", "target": rep, "run": run,
                           "index": i, "seed": seed, "side": side})
            sink.write(json.dumps(result, sort_keys=True) + "\n")
            sink.flush()
            if not result["order_certified"]:
                raise ArithmeticError(f"order certificate failed: {rep}/{i}/{side}")
        sink.write(json.dumps({"record": "completed", "status": "validated",
                               "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                               "elapsed_seconds": round(time.monotonic() - start_monotonic, 3),
                               "certified_branches": len(cases)}, sort_keys=True) + "\n")
        sink.flush()
    os.replace(partial, output)
    print(json.dumps({"certified_branches": len(cases), "output": str(output),
                      "sha256": sha(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
