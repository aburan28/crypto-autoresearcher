#!/usr/bin/env python3
"""Exact cheap rejection for cofactor-one prime candidates.

A rational root of x^3-3x+b gives a point of order two, so neither b root
can define a prime-order group.  This screen does not decide X9.62 near-prime
acceptance, which may allow a small even cofactor.
"""

import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

from cypari2 import Pari


ROOT = Path(__file__).resolve().parent


def main():
    source = ROOT / "raw" / "candidates.jsonl"
    output = ROOT / "raw" / "prime_2torsion_screen.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    pari = Pari()
    variable = pari("x")
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    cache = {}
    counts = Counter()
    started = time.monotonic()
    with partial.open("w") as sink, source.open() as stream:
        sink.write(json.dumps({"record": "run", "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                               "method": "PARI_polrootsmod_cubic", "pid": os.getpid()}, sort_keys=True) + "\n")
        for line in stream:
            row = json.loads(line)
            if row["kind"] != "prime":
                continue
            method = row["variants"]["nist_fips_186_2"]
            status = "NO_SEEDED_CURVE" if method["reason"] == "no_b_root" else "SINGULAR" if method["reason"] == "singular" else "C_ZERO" if method["reason"] == "c_zero_mod_p" else None
            roots = []
            if status is None:
                p = int(targets[row["target"]]["p"])
                b = int(method["b_roots"][0], 16)
                key = (p, b)
                if key not in cache:
                    cache[key] = [int(root) for root in pari.polrootsmod(variable**3 - 3 * variable + b, p)]
                roots = cache[key]
                status = "EVEN_ORDER" if roots else "ODD_ORDER_PENDING_COUNT"
            counts[status] += 1
            sink.write(json.dumps({"target": row["target"], "index": row["index"], "seed": row["seed"],
                                   "status": status, "rational_2torsion_x": [hex(x) for x in roots]}, sort_keys=True) + "\n")
        sink.write(json.dumps({"record": "finish", "counts": dict(counts),
                               "elapsed_seconds": round(time.monotonic() - started, 6)}, sort_keys=True) + "\n")
    os.replace(partial, output)
    print(json.dumps({"counts": dict(counts), "output": str(output),
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
