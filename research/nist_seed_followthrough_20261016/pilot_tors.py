#!/usr/bin/env python3
"""Compare PARI's acceptance-specific SEA path with three exact counts."""

import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = HERE / "raw/x9/P-256/00001-00020-retry1.jsonl"
TARGET = REPO / "research/nist_seed_selection_20261016/targets.json"
OUTPUT = HERE / "raw/ellsea_tors_pilot.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes(limit):
    return [n for n in range(2, limit + 1)
            if all(n % d for d in range(2, math.isqrt(n) + 1))]


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    rows = {r["index"]: r for r in [json.loads(line) for line in SOURCE.read_text().splitlines()[1:]]}
    p = int(next(t["p"] for t in json.loads(TARGET.read_text()) if t["name"] == "P-256"))
    tors = math.prod(primes(255))
    gp_version = subprocess.run(["gp", "--version-short"], text=True,
                                capture_output=True, check=True).stdout.strip()
    outcomes = []
    for i in (3, 8, 12):
        source = rows[i]["unmasked"]
        if rows[i]["status"] != "COMPLETE" or source["status"] != "COUNTED":
            raise AssertionError("exact source row missing")
        b = int(source["canonical_b"])
        program = ("default(parisizemax,536870912)\n"
                   f"print(ellsea(ellinit([-3,{b}],{p}),{tors}))\nquit\n")
        started = time.monotonic()
        result = subprocess.run(["gp", "-q", "-f"], input=program,
                                text=True, capture_output=True, timeout=600)
        elapsed = time.monotonic() - started
        lines = [x.strip() for x in result.stdout.splitlines() if x.strip()]
        if result.returncode or len(lines) != 1 or not lines[0].isdigit():
            raise RuntimeError(f"GP pilot failed at {i}: {result.returncode}, {result.stderr[-200:]}")
        n = int(lines[0])
        exact = int(source["canonical_order"])
        if n and n != exact:
            raise AssertionError("nonzero SEA order differs from ellcard")
        outcomes.append({"index": i, "b": str(b), "ellcard_order": str(exact),
                         "ellsea_result": str(n), "nonzero_agrees": bool(n and n == exact),
                         "early_abort": n == 0, "elapsed_seconds": round(elapsed, 6),
                         "gp_program_sha256": hashlib.sha256(program.encode()).hexdigest(),
                         "gp_stdout": result.stdout, "gp_stderr": result.stderr})
    OUTPUT.write_text(json.dumps({"status": "complete", "command": sys.argv,
                                  "python": platform.python_version(),
                                  "gp_version": gp_version,
                                  "script_sha256": digest(Path(__file__)),
                                  "inputs_sha256": {str(path.relative_to(REPO)): digest(path)
                                                    for path in (SOURCE, TARGET, HERE / "AMENDMENT_1.md")},
                                  "tors_primorial_255": str(tors),
                                  "outcomes": outcomes}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(OUTPUT), "sha256": digest(OUTPUT),
                      "elapsed_seconds": sum(x["elapsed_seconds"] for x in outcomes),
                      "early_abort_count": sum(x["early_abort"] for x in outcomes)}))


if __name__ == "__main__":
    main()
