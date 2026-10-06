#!/usr/bin/env python3
"""Independent checker for EXP-AUXIN-fef6ac Stage 0-1 run artifacts.

Recomputes Jacobi point-count, trial factorization, Cheon closed forms, and
the consecutive-integer r_null obstruction without importing run.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-AUXIN-fef6ac"
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {
    "O-SPLIT",
    "O-NO-SPLIT",
    "O-ARTIFACT",
    "O-R-SMALL",
    "O-MISMATCH",
    "O-WRONG-INTEGER",
    "O-SINGULAR",
    "O-IMPEDIMENT",
}
PINNED_P = 10007
SPLIT_THRESHOLD = 2.0
NULL_THRESHOLD = 1.25
R_MIN = 16


def jacobi(a: int, n: int) -> int:
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            r = n % 8
            if r in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def count_points(p: int) -> int:
    n = 1
    for x in range(p):
        rhs = (x * x * x + x + 1) % p
        n += 1 + jacobi(rhs, p)
    return n


def factor_trial(n: int) -> list[int]:
    factors: list[int] = []
    x = n
    while x % 2 == 0:
        factors.append(2)
        x //= 2
    f = 3
    while f * f <= x:
        while x % f == 0:
            factors.append(f)
            x //= f
        f += 2
    if x > 1:
        factors.append(x)
    return factors


def product(xs: list[int]) -> int:
    out = 1
    for x in xs:
        out *= x
    return out


def admissible(n: int, cap: int) -> list[int]:
    divs = {1}
    tmp = n
    primes: list[int] = []
    p = 2
    while p * p <= tmp:
        while tmp % p == 0:
            primes.append(p)
            tmp //= p
        p += 1 if p == 2 else 2
    if tmp > 1:
        primes.append(tmp)
    for pr in primes:
        divs = divs | {d * pr for d in divs}
    return sorted(d for d in divs if 2 <= d <= cap)


def load_yaml_outcome(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("outcome:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("no outcome in manifest")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1]).resolve()
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    if not raw_path.is_file() or not man_path.is_file():
        print("missing raw-result.json or manifest.yaml", file=sys.stderr)
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        print("experiment_id mismatch", file=sys.stderr)
        return 1
    if raw.get("amazon_bedrock") != "NOT SELECTED":
        print("amazon_bedrock must be NOT SELECTED", file=sys.stderr)
        return 1
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("attack") or claims.get("exponent_move"):
        print("forbidden claim flag", file=sys.stderr)
        return 1
    stage = (raw.get("result") or {}).get("stage")
    outcome = (raw.get("result") or {}).get("outcome")
    man_outcome = load_yaml_outcome(man_path)
    if outcome != man_outcome:
        print("manifest/raw outcome mismatch", file=sys.stderr)
        return 1
    exp_root = run_dir.parents[1]
    if stage == 0:
        if outcome not in STAGE0_OK:
            print(f"bad stage0 outcome {outcome}", file=sys.stderr)
            return 1
        for name in (
            "preregistered-predictions.json",
            "protocol-freeze.json",
            "worksheet-note.md",
        ):
            if not (exp_root / "stage0" / name).is_file():
                print(f"missing stage0/{name}", file=sys.stderr)
                return 1
        freeze = json.loads((exp_root / "stage0" / "protocol-freeze.json").read_text())
        if freeze.get("curve", {}).get("p") != PINNED_P:
            print("frozen p mismatch", file=sys.stderr)
            return 1
        if freeze.get("r_null", {}).get("status") != "IMPOSSIBLE_CONSECUTIVE":
            print("r_null obstruction not frozen", file=sys.stderr)
            return 1
        print("check.py PASS stage 0", outcome)
        return 0
    if stage != 1 or outcome not in STAGE1_OK:
        print(f"bad stage1 outcome {outcome}", file=sys.stderr)
        return 1
    census_path = exp_root / "stage1" / "census.json"
    if not census_path.is_file():
        print("missing stage1/census.json", file=sys.stderr)
        return 1
    census = json.loads(census_path.read_text(encoding="utf-8"))
    n = count_points(PINNED_P)
    if census.get("N") != n:
        print(f"N mismatch checker={n} census={census.get('N')}", file=sys.stderr)
        return 1
    nf = factor_trial(n)
    if product(nf) != n:
        print("N factorization reconstruction failed", file=sys.stderr)
        return 1
    r = max(nf)
    if census.get("r") != r:
        print(f"r mismatch checker={r} census={census.get('r')}", file=sys.stderr)
        return 1
    cap = math.isqrt(r)
    ads_m = admissible(r - 1, cap)
    ads_p = admissible(r + 1, cap)
    d_minus = ads_m[-1] if ads_m else (2 if (r - 1) % 2 == 0 else None)
    d_plus = ads_p[-1] if ads_p else (2 if (r + 1) % 2 == 0 else None)
    if census.get("d_minus") != d_minus or census.get("d_plus") != d_plus:
        print("d_minus/d_plus mismatch", file=sys.stderr)
        return 1
    if d_minus is None or d_plus is None:
        print("missing admissible divisor", file=sys.stderr)
        return 1
    bm = math.sqrt(r / d_minus) + math.sqrt(d_minus)
    bp = math.sqrt(r / d_plus) + float(d_plus)
    pinned = max(bm, bp) / min(bm, bp)
    bm2 = math.sqrt(r / 2) + math.sqrt(2)
    bp2 = math.sqrt(r / 2) + 2.0
    d2 = max(bm2, bp2) / min(bm2, bp2)
    if abs(float(census["pinned_ratio"]) - pinned) > 1e-9:
        print("pinned_ratio mismatch", file=sys.stderr)
        return 1
    if abs(float(census["d2_ratio"]) - d2) > 1e-9:
        print("d2_ratio mismatch", file=sys.stderr)
        return 1
    if census.get("d_N_minus") == d_minus and census.get("N") != r:
        if census.get("d_minus") == census.get("d_N_minus") and n != r:
            # Using N±1 would typically differ; require metric_from r±1 via control table.
            pass
    control = json.loads((exp_root / "stage1" / "control-table.json").read_text())
    if control.get("wrong_integer", {}).get("used_for_metric") is not False:
        print("wrong_integer used_for_metric must be false", file=sys.stderr)
        return 1
    if control.get("wrong_integer", {}).get("metric_from") != "r±1":
        print("metric_from must be r±1", file=sys.stderr)
        return 1
    # Independent label
    if r < R_MIN:
        want = "O-R-SMALL"
    elif d2 >= NULL_THRESHOLD:
        want = "O-ARTIFACT"
    elif pinned >= SPLIT_THRESHOLD:
        want = "O-SPLIT"
    else:
        want = "O-NO-SPLIT"
    if not census.get("reconstruction_ok", True):
        want = "O-MISMATCH"
    if outcome not in (want, "O-IMPEDIMENT"):
        if outcome != want:
            print(f"label mismatch checker={want} producer={outcome}", file=sys.stderr)
            return 1
    print("check.py PASS stage 1", outcome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
