"""Bounded, source-bound twist-order factorization comparison.

The fixed 20-second cap applies independently to each residual. A timeout is
unknown factorization, never evidence that a curve's twist lacks large primes.
Input rows are the 21 original seed classes, not duplicate P-224 sign models.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016"
TIMEOUT_SECONDS = 20
OUT = HERE / "twist_factor_probe.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factor_residual(n: int) -> tuple[str, list[list[int]], str, float]:
    code = (f"F=factor({n});"
            "for(i=1,matsize(F)[1],if(!isprime(F[i,1]),error(\"nonprime factor\"));"
            "print(F[i,1],\" \",F[i,2]))\n")
    start = time.monotonic()
    try:
        p = subprocess.run(["gp", "-q"], input=code, capture_output=True,
                           text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return "timeout", [], "", time.monotonic() - start
    elapsed = time.monotonic() - start
    if p.returncode != 0:
        return "gp_error", [], p.stderr[:1000], elapsed
    try:
        pairs = [[int(v) for v in line.split()] for line in p.stdout.splitlines()]
        assert pairs and all(len(pair) == 2 for pair in pairs)
        product = 1
        for prime, exponent in pairs:
            product *= prime ** exponent
        assert product == n
    except (ValueError, AssertionError) as exc:
        return "parse_or_product_error", [], repr(exc) + ": " + p.stdout[:1000], elapsed
    return "complete", pairs, "", elapsed


def main() -> None:
    traits_path = SOURCE / "traits.json"
    assessed_path = SOURCE / "assessed.json"
    traits = json.loads(traits_path.read_text())
    assessed = json.loads(assessed_path.read_text())
    rows = [(name, row, "published") for name, row in traits["published_controls"].items()]
    rows += [(f"{row['timestamp']}:{row['seed_ordinal_one_based']}", row, "passed_over")
             for row in assessed["candidate_rows"]]
    assert len(rows) == 21
    gp_version = subprocess.run(["gp", "--version"], check=True, capture_output=True,
                                text=True).stdout.strip()
    results = []
    for name, row, label in rows:
        residual = int(row["twist_unfactored_rest_hex"], 16)
        status, factors, error, elapsed = factor_residual(residual)
        small = [[int(p), int(e)] for p, e in row["twist_small_factors_to_10000"]]
        full = small + factors if status == "complete" else None
        twist_order = int(row["twist_order_hex"], 16)
        if full is not None:
            product = 1
            for prime, exponent in full:
                product *= prime ** exponent
            assert product == twist_order
        result = {
            "name": name,
            "label": label,
            "field_bits": int(row["p_hex"], 16).bit_length(),
            "timestamp": int(row["timestamp"]),
            "ordinal": int(row["seed_ordinal_one_based"]),
            "twist_order_hex": row["twist_order_hex"],
            "residual_hex": row["twist_unfactored_rest_hex"],
            "status": status,
            "elapsed_seconds": round(elapsed, 3),
            "prime_factors_if_complete": full,
            "largest_prime_factor_bits_if_complete": max(p.bit_length() for p, _ in full)
            if full else None,
            "error": error or None,
        }
        results.append(result)
        OUT.write_text(json.dumps({
            "method": "PARI/GP factor and isprime on residual after source trial division <=10000",
            "per_residual_timeout_seconds": TIMEOUT_SECONDS,
            "gp_version": gp_version,
            "source_sha256": {"traits.json": digest(traits_path),
                              "assessed.json": digest(assessed_path)},
            "rows_completed_or_censored": results,
        }, indent=2, sort_keys=True) + "\n")
        print(f"{name:20s} {status:8s} largest_bits="
              f"{result['largest_prime_factor_bits_if_complete']}", flush=True)


if __name__ == "__main__":
    main()
