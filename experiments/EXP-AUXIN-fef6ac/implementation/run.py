#!/usr/bin/env python3
"""EXP-AUXIN-fef6ac Stages 0-1 launcher (F_10007 Cheon r±1 divisor split).

Stage 0: Zero-compute freeze of the curve pin, closed forms, thresholds,
         dual-factor methods, r_null obstruction, and d=2 nearby-object
         control into stage0/.
Stage 1: Count #E(F_10007), factor N, take r, factor r±1 by two independent
         implementations, compute B_minus/B_plus/B_rho and the pinned ratio,
         record the d=2 formula null, and emit exactly one O-* label.

Observations only. Do not run Cheon's algorithm. Do not ingest auxiliary
points. No Magma/Sage/AUXIN walks/Bedrock. No ECDLP solve. Amazon Bedrock
is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-AUXIN-fef6ac"
HYPOTHESIS_ID = "H-AUXIN-9d9ee0"
APPROVED_BY = "DEC-20261004-927012"
TASK_ID = "TASK-20261004-f88f65"
SOURCE_IDEA = "IDEA-20261005-447d82"
QUESTION_ID = "RQ-AUXIN-f8d8c0"
MASTER_SEED = "20261004fef6ac"
EXP_ROOT = Path(__file__).resolve().parents[1]

PINNED_P = 10007
PINNED_A = 1
PINNED_B = 1
SPLIT_THRESHOLD = 2.0
NULL_THRESHOLD = 1.25
R_MIN = 16
R_NULL_LOWER = 2**16
STAGE0_OK = "S0-FREEZE-OK"
STAGE1_LABELS = (
    "O-SPLIT",
    "O-NO-SPLIT",
    "O-ARTIFACT",
    "O-R-SMALL",
    "O-MISMATCH",
    "O-WRONG-INTEGER",
    "O-SINGULAR",
    "O-IMPEDIMENT",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def claims() -> dict[str, bool]:
    return {"attack": False, "break": False, "exponent_move": False}


def load_plan(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    f = 5
    while f * f <= n:
        if n % f == 0 or n % (f + 2) == 0:
            return False
        f += 6
    return True


def powmod(base: int, exp: int, mod: int) -> int:
    return pow(base, exp, mod)


def jacobi(a: int, n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("jacobi n must be odd positive")
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


def euler_legendre(a: int, p: int) -> int:
    if a % p == 0:
        return 0
    return 1 if powmod(a, (p - 1) // 2, p) == 1 else -1


def factor_trial_up(n: int) -> list[int]:
    if n <= 0:
        raise ValueError("factor non-positive")
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


def _pollard_rho_split(n: int) -> int:
    if n % 2 == 0:
        return 2
    if is_prime(n):
        return n
    c = 1
    while c < 64:
        x = 2
        y = 2
        d = 1
        f = lambda v: (v * v + c) % n
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d
        c += 1
    # Fallback: trial from the top of the sqrt window (independent order).
    f = int(math.isqrt(n))
    if f % 2 == 0:
        f -= 1
    while f >= 3:
        if n % f == 0:
            return f
        f -= 2
    return n


def factor_pollard(n: int) -> list[int]:
    if n <= 0:
        raise ValueError("factor non-positive")
    if n == 1:
        return []
    factors: list[int] = []
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if is_prime(m):
            factors.append(m)
            continue
        d = _pollard_rho_split(m)
        if d in (1, m):
            factors.extend(factor_trial_up(m))
            continue
        stack.append(d)
        stack.append(m // d)
    return sorted(factors)


def product(xs: list[int]) -> int:
    out = 1
    for x in xs:
        out *= x
    return out


def admissible_divisors(n: int, cap: int) -> list[int]:
    if n <= 0:
        return []
    divs = {1}
    x = n
    p = 2
    tmp = x
    primes: list[int] = []
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


def largest_admissible(n: int, cap: int) -> int | None:
    ads = admissible_divisors(n, cap)
    return ads[-1] if ads else None


def b_minus(r: int, d: int) -> float:
    return math.sqrt(r / d) + math.sqrt(d)


def b_plus(r: int, d: int) -> float:
    return math.sqrt(r / d) + float(d)


def b_rho(r: int) -> float:
    return math.sqrt(r)


def ratio_of(a: float, b: float) -> float:
    lo, hi = (a, b) if a <= b else (b, a)
    if lo <= 0:
        raise ValueError("non-positive Cheon shape")
    return hi / lo


def count_points_jacobi(p: int, a: int, b: int) -> int:
    n = 1
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        n += 1 + jacobi(rhs, p)
    return n


def count_points_euler(p: int, a: int, b: int) -> int:
    n = 1
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        n += 1 + euler_legendre(rhs, p)
    return n


def discriminant(a: int, b: int, p: int) -> int:
    # -16(4a^3 + 27b^2) mod p
    return (-16 * (4 * pow(a, 3, p) + 27 * pow(b, 2, p))) % p


def r_null_obstruction() -> dict[str, Any]:
    return {
        "definition": (
            "smallest prime r_null > 2^16 such that (r_null-1)/2 and "
            "(r_null+1)/2 are both prime"
        ),
        "status": "IMPOSSIBLE_CONSECUTIVE",
        "argument": (
            "For odd r, (r-1)/2 and (r+1)/2 are consecutive integers. The only "
            "consecutive primes are (2,3), giving r=5, which is not > 2^16. "
            "Therefore the idea's r_null search has empty range. This is a "
            "defect of the null construction, not a Cheon-split observation."
        ),
        "nearby_object_control": (
            "Evaluate the two closed forms at d_minus=d_plus=2 on the pinned "
            "r (the claim's 'same ratio with d=2 on both sides')."
        ),
        "r_null": None,
        "lower_bound": R_NULL_LOWER,
    }


def freeze_payload() -> dict[str, Any]:
    return {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "curve": {
            "model": "short Weierstrass y^2 = x^3 + a x + b",
            "p": PINNED_P,
            "a": PINNED_A,
            "b": PINNED_B,
            "field": "F_10007",
        },
        "formulas": {
            "B_minus": "sqrt(r/d_minus)+sqrt(d_minus)",
            "B_plus": "sqrt(r/d_plus)+d_plus",
            "B_rho": "sqrt(r)",
            "pinned_ratio": "max(B_minus,B_plus)/min(B_minus,B_plus)",
            "log_factor": "omitted; common to both branches and cancels in the ratio",
            "source": "KN-LIT-90e34c / IDEA-20261005-447d82",
        },
        "thresholds": {
            "split_ratio": SPLIT_THRESHOLD,
            "null_ratio": NULL_THRESHOLD,
            "r_min": R_MIN,
            "admissible_window": "[2, floor(sqrt(r))]",
        },
        "dual_factor_methods": {
            "route_A": "trial division from 2 upward",
            "route_B": "Pollard rho then trial of remaining cofactors",
        },
        "dual_point_count": {
            "route_A": "Jacobi symbol of x^3+x+1",
            "route_B": "Euler criterion (x^3+x+1)^((p-1)/2) mod p",
        },
        "r_null": r_null_obstruction(),
        "d2_null_control": {
            "d_minus": 2,
            "d_plus": 2,
            "note": (
                "Constructible nearby-object control. If this ratio is >= 1.25, "
                "the factor-2 gap is an artifact of the two formulas at small d."
            ),
        },
        "wrong_integer_control": (
            "Also record largest admissible divisors of N-1 and N+1. Those "
            "values are not the metric. Using them in place of r±1 is "
            "O-WRONG-INTEGER."
        ),
        "labels": {
            "stage0": [STAGE0_OK],
            "stage1": list(STAGE1_LABELS),
        },
        "not_claimed": [
            "ordinary ECDLP improvement",
            "protocol supply of auxiliary powers",
            "transfer to NIST P-256 / secp256k1 / Curve25519 / BN254 / BLS12-381",
            "Cheon algorithm execution",
        ],
        "source_idea": SOURCE_IDEA,
        "hypothesis_id": HYPOTHESIS_ID,
        "experiment_id": EXPERIMENT_ID,
        "master_seed": MASTER_SEED,
    }


def stage0(run_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    freeze = freeze_payload()
    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", {
        "amazon_bedrock": "NOT SELECTED",
        "decision_rules": {
            "O-SPLIT": "pinned_ratio >= 2 and d2_ratio < 1.25 and r >= 16 and reconstruction ok",
            "O-NO-SPLIT": "pinned_ratio < 2 and reconstruction ok and r >= 16 and d2_ratio < 1.25",
            "O-ARTIFACT": "d2_ratio >= 1.25 (formulas already split at d=2)",
            "O-R-SMALL": "r < 16",
            "O-MISMATCH": "route A/B factorizations or point counts disagree, or product fails",
            "O-WRONG-INTEGER": "reported d_minus/d_plus taken from N±1 rather than r±1",
            "O-SINGULAR": "curve discriminant 0 mod p",
            "O-IMPEDIMENT": "timeout/crash/infra; never mathematical negative",
        },
        "numeric_ratio_not_preregistered": True,
        "numeric_ratio_note": (
            "The pinned ratio is the measurement. Stage 0 freezes rules, not "
            "the integer factorization of this order."
        ),
        "split_threshold": SPLIT_THRESHOLD,
        "null_threshold": NULL_THRESHOLD,
        "r_min": R_MIN,
        "source_idea": SOURCE_IDEA,
    })
    write_json(stage0_dir / "protocol-freeze.json", freeze)
    write_text(stage0_dir / "worksheet-note.md", (
        "# Stage 0 freeze — EXP-AUXIN-fef6ac\n\n"
        "Pinned curve: y^2 = x^3 + x + 1 over F_10007.\n\n"
        "Cheon shapes (log factor omitted): "
        "B_minus = sqrt(r/d_minus)+sqrt(d_minus), "
        "B_plus = sqrt(r/d_plus)+d_plus, B_rho = sqrt(r).\n\n"
        "r_null as written in IDEA-20261005-447d82 is IMPOSSIBLE_CONSECUTIVE "
        "(documented in protocol-freeze.json). The nearby-object control is "
        "the d=2 formula ratio on the measured r.\n\n"
        "No point count and no factorization in this stage.\n"
        "Amazon Bedrock is NOT SELECTED.\n"
    ))
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": claims(),
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "result": {
            "artifacts": [
                "stage0/preregistered-predictions.json",
                "stage0/protocol-freeze.json",
                "stage0/worksheet-note.md",
            ],
            "note": "Zero-compute freeze. Stage 1 performs the census.",
            "outcome": STAGE0_OK,
            "stage": 0,
            "stage1_admitted": True,
        },
        "source_idea": SOURCE_IDEA,
        "task_id": TASK_ID,
        "trial_plan_approved_by": plan.get("approved_by"),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(run_dir / "manifest.yaml", (
        f"amazon_bedrock: NOT SELECTED\n"
        f"experiment_id: {EXPERIMENT_ID}\n"
        f"hypothesis_id: {HYPOTHESIS_ID}\n"
        f"approved_by: {APPROVED_BY}\n"
        f"outcome: {STAGE0_OK}\n"
        f"stage: 0\n"
        f"wrap_note: 'Nested run: wrapped flat manifest for validate_ledger'\n"
    ))
    write_text(run_dir / "RESULTS.md", (
        f"# RUN Stage 0 — {EXPERIMENT_ID}\n\n"
        f"Outcome: **{STAGE0_OK}**\n\n"
        "Protocol freeze only. No factorization.\n"
    ))
    return raw


def decide_label(payload: dict[str, Any]) -> str:
    if payload.get("singular"):
        return "O-SINGULAR"
    if payload.get("mismatch"):
        return "O-MISMATCH"
    if payload.get("wrong_integer"):
        return "O-WRONG-INTEGER"
    if payload["r"] < R_MIN:
        return "O-R-SMALL"
    if payload["d2_ratio"] >= NULL_THRESHOLD:
        return "O-ARTIFACT"
    if payload["pinned_ratio"] >= SPLIT_THRESHOLD:
        return "O-SPLIT"
    return "O-NO-SPLIT"


def stage1(run_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    freeze_path = EXP_ROOT / "stage0" / "protocol-freeze.json"
    if not freeze_path.exists():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 1")
    p, a, b = PINNED_P, PINNED_A, PINNED_B
    disc = discriminant(a, b, p)
    singular = disc == 0
    n_jac = count_points_jacobi(p, a, b)
    n_eul = count_points_euler(p, a, b)
    mismatch = n_jac != n_eul
    n = n_jac
    n_factors_a = factor_trial_up(n)
    n_factors_b = factor_pollard(n)
    mismatch = mismatch or sorted(n_factors_a) != sorted(n_factors_b)
    mismatch = mismatch or product(n_factors_a) != n
    r = max(n_factors_a) if n_factors_a else n
    cap = math.isqrt(r)
    rm1_a = factor_trial_up(r - 1)
    rm1_b = factor_pollard(r - 1)
    rp1_a = factor_trial_up(r + 1)
    rp1_b = factor_pollard(r + 1)
    mismatch = mismatch or sorted(rm1_a) != sorted(rm1_b) or product(rm1_a) != (r - 1)
    mismatch = mismatch or sorted(rp1_a) != sorted(rp1_b) or product(rp1_a) != (r + 1)
    d_minus = largest_admissible(r - 1, cap)
    d_plus = largest_admissible(r + 1, cap)
    d_n_minus = largest_admissible(n - 1, math.isqrt(n) if n > 0 else 0)
    d_n_plus = largest_admissible(n + 1, math.isqrt(n) if n > 0 else 0)
    wrong_integer = False
    if d_minus is None or d_plus is None:
        # No admissible divisor: treat as d=2 if 2 divides, else mismatch-scale fail.
        if (r - 1) % 2 == 0:
            d_minus = 2
        if (r + 1) % 2 == 0:
            d_plus = 2
        if d_minus is None or d_plus is None:
            mismatch = True
            d_minus = d_minus or 2
            d_plus = d_plus or 2
    bm = b_minus(r, d_minus)
    bp = b_plus(r, d_plus)
    br = b_rho(r)
    pinned = ratio_of(bm, bp)
    bm2 = b_minus(r, 2)
    bp2 = b_plus(r, 2)
    d2_ratio = ratio_of(bm2, bp2)
    payload = {
        "N": n,
        "r": r,
        "cofactor": n // r if r else None,
        "singular": singular,
        "mismatch": mismatch,
        "wrong_integer": wrong_integer,
        "d_minus": d_minus,
        "d_plus": d_plus,
        "d_N_minus": d_n_minus,
        "d_N_plus": d_n_plus,
        "B_minus": bm,
        "B_plus": bp,
        "B_rho": br,
        "pinned_ratio": pinned,
        "d2_ratio": d2_ratio,
        "N_jacobi": n_jac,
        "N_euler": n_eul,
        "N_factors_trial": n_factors_a,
        "N_factors_pollard": sorted(n_factors_b),
        "r_minus_1_trial": rm1_a,
        "r_minus_1_pollard": sorted(rm1_b),
        "r_plus_1_trial": rp1_a,
        "r_plus_1_pollard": sorted(rp1_b),
        "sqrt_r_floor": cap,
        "r_null": r_null_obstruction(),
    }
    label = decide_label(payload)
    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "census.json", {
        "amazon_bedrock": "NOT SELECTED",
        "curve": {"p": p, "a": a, "b": b},
        "discriminant_mod_p": disc,
        **{k: payload[k] for k in (
            "N", "r", "cofactor", "d_minus", "d_plus", "d_N_minus", "d_N_plus",
            "B_minus", "B_plus", "B_rho", "pinned_ratio", "d2_ratio",
            "N_factors_trial", "N_factors_pollard",
            "r_minus_1_trial", "r_minus_1_pollard",
            "r_plus_1_trial", "r_plus_1_pollard", "sqrt_r_floor",
        )},
        "reconstruction_ok": not mismatch,
        "point_count_agree": n_jac == n_eul,
    })
    write_json(stage1_dir / "control-table.json", {
        "amazon_bedrock": "NOT SELECTED",
        "d2_null": {"d_minus": 2, "d_plus": 2, "ratio": d2_ratio, "threshold": NULL_THRESHOLD},
        "wrong_integer": {
            "d_N_minus": d_n_minus,
            "d_N_plus": d_n_plus,
            "used_for_metric": False,
            "metric_from": "r±1",
        },
        "r_null": r_null_obstruction(),
        "twin_point_count_ok": n_jac == n_eul,
        "twin_factor_ok": not mismatch,
    })
    write_text(stage1_dir / "r-null-obstruction.md", (
        "# r_null construction is empty\n\n"
        + r_null_obstruction()["argument"]
        + "\n\nNearby-object control used: d=2 formula ratio = "
        + f"{d2_ratio}.\n"
    ))
    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Task: {TASK_ID}\n"
        f"Source: {SOURCE_IDEA}\n\n"
        f"Stage-1 package outcome: **{label}**\n\n"
        f"| Quantity | Value |\n| --- | --- |\n"
        f"| N = #E(F_10007) | {n} |\n"
        f"| r (largest prime factor) | {r} |\n"
        f"| cofactor N/r | {n // r if r else 'NA'} |\n"
        f"| d_minus | {d_minus} |\n"
        f"| d_plus | {d_plus} |\n"
        f"| B_minus | {bm} |\n"
        f"| B_plus | {bp} |\n"
        f"| B_rho | {br} |\n"
        f"| pinned_ratio | {pinned} |\n"
        f"| d2_ratio (null) | {d2_ratio} |\n"
        f"| r_null | IMPOSSIBLE_CONSECUTIVE |\n\n"
        "This is a necessary-condition integer measurement. It is not a break, "
        "not a protocol finding, and not an ordinary-ECDLP improvement. "
        "No transfer to deployed curves. Cheon's algorithm was not run. "
        "Amazon Bedrock is NOT SELECTED.\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    write_text(run_dir / "RESULTS.md", results)
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": claims(),
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "result": {
            "N": n,
            "r": r,
            "artifacts": [
                "stage1/census.json",
                "stage1/control-table.json",
                "stage1/r-null-obstruction.md",
            ],
            "d2_ratio": d2_ratio,
            "d_minus": d_minus,
            "d_plus": d_plus,
            "note": (
                "Exact integer census. Cheon not executed. r_null empty by "
                "consecutive-prime obstruction; d=2 formula is the null."
            ),
            "outcome": label,
            "pinned_ratio": pinned,
            "reconstruction_ok": not mismatch,
            "stage": 1,
        },
        "source_idea": SOURCE_IDEA,
        "task_id": TASK_ID,
        "trial_plan_approved_by": plan.get("approved_by"),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(run_dir / "manifest.yaml", (
        f"amazon_bedrock: NOT SELECTED\n"
        f"experiment_id: {EXPERIMENT_ID}\n"
        f"hypothesis_id: {HYPOTHESIS_ID}\n"
        f"approved_by: {APPROVED_BY}\n"
        f"outcome: {label}\n"
        f"stage: 1\n"
        f"wrap_note: 'Nested run: wrapped flat manifest for validate_ledger'\n"
    ))
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = load_plan(Path(args.trial_plan))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("experiment_id mismatch", file=sys.stderr)
        return 2
    started = time.time()
    try:
        if args.stage == 0:
            stage0(run_dir, plan)
        else:
            stage1(run_dir, plan)
    except FileExistsError as exc:
        print(f"O-IMPEDIMENT overwrite-refuse: {exc}", file=sys.stderr)
        return 3
    elapsed = time.time() - started
    print(f"stage {args.stage} complete in {elapsed:.3f}s amazon_bedrock=NOT_SELECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
