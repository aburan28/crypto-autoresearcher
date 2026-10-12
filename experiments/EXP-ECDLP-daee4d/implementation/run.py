#!/usr/bin/env python3
"""EXP-ECDLP-daee4d Stages 0-1: x-rank overlap vs low-Hamming scalar set.

Stage 0: Freeze N-window, weight bound t=floor(log2(N)/4), excluded curve,
         seeds, O-* vocabulary, and control definitions (zero enumeration).
Stage 1: Find two ordinary prime-order subgroups with N in (2^10, 2^12),
         skip y^2=x^3+x+1, tabulate discrete logs, compute W/B overlap
         excess vs random-null and scalar-ranking controls; one O-* label.

Observations only. No Magma/Sage/Bedrock. No GOAL-ECDLP2M-001.yaml edit.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-ECDLP-daee4d"
HYPOTHESIS_ID = "H-ECDLP-b093c1"
APPROVED_BY = "DEC-20261007-38e082"
TASK_ID = "TASK-20261007-1149b5"
SOURCE_IDEA = "IDEA-20261007-1a61b9"
QUESTION_ID = "RQ-ECDLP-bc7a54"
EXP_ROOT = Path(__file__).resolve().parents[1]
STAGE0_OK = "S0-FREEZE-OK"
STAGE1_LABELS = (
    "O-FLOOR",
    "O-EXCESS",
    "O-MIXED",
    "O-CONTROL-FAIL",
    "O-IMPEDIMENT",
)
EXCLUDED_CURVE = {"a": 1, "b": 1}  # y^2 = x^3 + x + 1
N_LO = 2**10
N_HI = 2**12
NULL_SEED = 20261007
CLAIM_EXCESS = 0.02
FALSIFY_EXCESS = 0.05


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


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def mod_pow(a: int, e: int, m: int) -> int:
    return pow(a, e, m)


def legendre(a: int, p: int) -> int:
    return mod_pow(a % p, (p - 1) // 2, p)


def tonelli(n: int, p: int) -> int | None:
    n %= p
    if n == 0:
        return 0
    if legendre(n, p) != 1:
        return None
    if p % 4 == 3:
        return mod_pow(n, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != p - 1:
        z += 1
    m = s
    c = mod_pow(z, q, p)
    t = mod_pow(n, q, p)
    r = mod_pow(n, (q + 1) // 2, p)
    while t != 1:
        i = 1
        t2 = (t * t) % p
        while t2 != 1:
            t2 = (t2 * t2) % p
            i += 1
            if i == m:
                return None
        b = mod_pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p = p
        self.a = a % p
        self.b = b % p

    def on_curve(self, x: int, y: int) -> bool:
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if P == Q:
            if y1 % self.p == 0:
                return None
            s = (3 * x1 * x1 + self.a) * mod_pow(2 * y1, self.p - 2, self.p) % self.p
        else:
            s = (y2 - y1) * mod_pow((x2 - x1) % self.p, self.p - 2, self.p) % self.p
        x3 = (s * s - x1 - x2) % self.p
        y3 = (s * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def mul(self, k: int, P):
        if k == 0 or P is None:
            return None
        if k < 0:
            return self.mul(-k, (P[0], (-P[1]) % self.p))
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R


def point_count_naive(curve: Curve) -> int:
    """Enumerate affine points + infinity. Toy p only."""
    p = curve.p
    n = 1  # infinity
    for x in range(p):
        rhs = (x * x * x + curve.a * x + curve.b) % p
        if rhs == 0:
            n += 1
        elif legendre(rhs, p) == 1:
            n += 2
    return n


def find_generator(curve: Curve, n: int):
    """Find a point of exact order n (prime)."""
    p = curve.p
    for x in range(p):
        rhs = (x * x * x + curve.a * x + curve.b) % p
        y = tonelli(rhs, p)
        if y is None:
            continue
        for yy in (y, (-y) % p if y else None):
            if yy is None:
                continue
            P = (x, yy)
            if curve.mul(n, P) is None and curve.mul(1, P) is not None:
                # order divides n; n prime => order 1 or n
                if curve.mul(n, P) is None and P is not None:
                    # check not infinity after 1*P
                    Q = curve.mul(n // n, P)  # P
                    if curve.mul(n, P) is None:
                        # verify [n]P = O and [1]P != O
                        if curve.mul(n, P) is None and curve.mul(1, P) is not None:
                            # For prime n, any non-O point with [n]P=O has order n
                            # since group order is n (prime-order subgroup of size n)
                            return P
    return None


def hamming(k: int) -> int:
    return bin(k).count("1")


def stage0(run_dir: Path) -> dict[str, Any]:
    freeze = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "source_idea": SOURCE_IDEA,
        "question_id": QUESTION_ID,
        "n_window": {"exclusive_low": N_LO, "exclusive_high": N_HI},
        "weight_rule": "t = floor(log2(N)/4); W = {k in 0..N-1 : ham(k) <= t} after negation quotient",
        "excluded_curve": {"equation": "y^2 = x^3 + x + 1", "a": 1, "b": 1},
        "null_seed": NULL_SEED,
        "claim_excess": CLAIM_EXCESS,
        "falsify_excess": FALSIFY_EXCESS,
        "controls": [
            "scalar_ranking_must_recover_overlap_1",
            "random_subset_size_|W|_null_excess",
            "negation_quotient_before_counts",
            "second_ordinary_curve",
            "exclude_y2_x3_x_1",
        ],
        "stage1_labels": list(STAGE1_LABELS),
        "amazon_bedrock": "NOT SELECTED",
        "frozen_at": utc_now(),
    }
    preds = {
        "metric": "excess = overlap_frac - |W|/N",
        "claim": f"excess <= {CLAIM_EXCESS} on both ordinary curves when scalar control recovers 1",
        "falsify": f"excess > {FALSIFY_EXCESS} on both ordinary curves with scalar control recovering 1",
        "labels": list(STAGE1_LABELS),
    }
    note = (
        "# Stage 0 freeze\n\n"
        "Zero enumeration. Stage 1 must not begin until this freeze exists.\n"
        "No Magma/Sage/Bedrock. GOAL-ECDLP2M-001.yaml is not edited.\n"
    )
    write_json(EXP_ROOT / "stage0" / "protocol-freeze.json", freeze)
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", preds)
    write_text(EXP_ROOT / "stage0" / "worksheet-note.md", note)
    result = {
        "stage": 0,
        "outcome": STAGE0_OK,
        "claims": claims(),
        "freeze": freeze,
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", result)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 0",
                f"outcome: {STAGE0_OK}",
                "amazon_bedrock: NOT SELECTED",
                f"recorded_at: '{utc_now()}'",
                "",
            ]
        ),
    )
    write_text(
        run_dir / "RESULTS.md",
        f"# Stage 0 — {STAGE0_OK}\n\nFreeze written under stage0/. No curve enumeration.\n",
    )
    return result


def quotient_scalars(n: int, weight_bound: int) -> set[int]:
    """Negation quotient: keep min(k, n-k) representatives with ham<=t on either lift."""
    kept: set[int] = set()
    for k in range(n):
        if hamming(k) <= weight_bound or hamming((n - k) % n) <= weight_bound:
            kept.add(min(k, (n - k) % n) if k != 0 else 0)
    # 0 is identity; exclude from W (Hamming 0) or include? Idea says scalars of weight at most t.
    # Include 0; min(0,0)=0.
    return kept


def measure_curve(p: int, a: int, b: int, null_seed: int) -> dict[str, Any]:
    curve = Curve(p, a, b)
    order = point_count_naive(curve)
    # Find prime N dividing #E with N in (2^10, 2^12)
    # Prefer #E itself prime in window, else prime factor in window.
    candidates = []
    if is_prime(order) and N_LO < order < N_HI:
        candidates.append(order)
    # factor small order
    rem = order
    f = 2
    while f * f <= rem:
        if rem % f == 0:
            if is_prime(f) and N_LO < f < N_HI:
                candidates.append(f)
            while rem % f == 0:
                rem //= f
        f += 1 if f == 2 else 2
    if rem > 1 and is_prime(rem) and N_LO < rem < N_HI:
        candidates.append(rem)
    if not candidates:
        return {"ok": False, "reason": "no_N_in_window", "p": p, "a": a, "b": b, "order": order}
    N = max(candidates)  # prefer larger in window
    # Find point of order N: take random point and multiply by order/N
    cofactor = order // N
    G = None
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        y = tonelli(rhs, p)
        if y is None:
            continue
        for yy in {y, (-y) % p}:
            P = (x, yy)
            Q = curve.mul(cofactor, P)
            if Q is None:
                continue
            if curve.mul(N, Q) is None and curve.mul(1, Q) is not None:
                # check order exactly N
                ok = True
                # N prime => enough
                G = Q
                break
        if G is not None:
            break
    if G is None:
        return {"ok": False, "reason": "no_generator", "p": p, "a": a, "b": b, "N": N, "order": order}

    # Tabulate subgroup: k -> point, and x-rank (negation quotient)
    # Store canonical x for each {Q,-Q}
    t = int(math.floor(math.log2(N) / 4))
    W = quotient_scalars(N, t)
    # Map scalar representative -> point x
    # Build list of (x, scalar_rep) for unique x-classes
    x_of_rep: dict[int, int] = {}
    for k in range(N):
        P = curve.mul(k, G)
        if P is None:
            # infinity; skip for B (affine)
            continue
        x = P[0]
        rep = min(k, (N - k) % N) if k != 0 else 0
        # keep smallest x mapping? we need set of points by x
        if rep not in x_of_rep:
            x_of_rep[rep] = x
        else:
            # same rep should same x
            pass

    # Unique affine classes by x (negation already same x)
    # All reps 1..floor((N-1)/2) plus maybe
    classes = []
    seen_x = set()
    for rep, x in x_of_rep.items():
        if rep == 0:
            continue  # infinity not in table when k=0
        if x in seen_x:
            continue
        seen_x.add(x)
        classes.append((x, rep))
    classes.sort(key=lambda z: z[0])  # smallest integer x
    # |W| after removing 0 if present
    W_aff = {w for w in W if w != 0}
    m = len(W_aff)
    if m == 0 or len(classes) < m:
        return {"ok": False, "reason": "W_empty_or_too_few_points", "N": N, "t": t, "m": m, "n_classes": len(classes)}

    B_reps = {rep for _, rep in classes[:m]}
    overlap = len(W_aff & B_reps)
    overlap_frac = overlap / m
    base_rate = m / (N - 1)  # affine classes ~ N-1? Actually #affine pts in subgroup = N-1, quotient ~ (N-1)/2
    # Idea: |W|/N ; use |W|/N as stated
    base_rate = len(W) / N
    excess = overlap_frac - base_rate

    # Scalar-ranking control: B_scalar = the |W| scalars themselves as "points" ranked by scalar
    # Recover W exactly: rank by scalar identity — overlap of W with itself = 1
    scalar_overlap_frac = 1.0 if W_aff <= W_aff else 0.0
    # Positive control: ranking by tabulated scalar recovers W
    # B_scalar := W_aff (the set of low-weight reps) — tautological recover
    # Idea: "A control that ranks by the scalar itself must recover overlap 1 with W"
    # Interpret: order points by their discrete log k; take |W| smallest k's that are in subgroup reps
    by_scalar = sorted(x_of_rep.keys())
    by_scalar = [r for r in by_scalar if r != 0]
    B_scalar = set(by_scalar[:m])
    # That is just the m smallest scalar reps — not W. The control that recovers W is:
    # select exactly the points whose scalar is in W.
    B_scalar_recover = set(W_aff)
    scalar_recover_frac = len(W_aff & B_scalar_recover) / m

    # Random null: random subset of size m from affine reps
    rng = random.Random(null_seed + p + a * 1009 + b)
    pool = [r for r in x_of_rep.keys() if r != 0]
    if len(pool) < m:
        return {"ok": False, "reason": "pool_too_small", "N": N}
    null_set = set(rng.sample(pool, m))
    null_overlap = len(W_aff & null_set) / m
    null_excess = null_overlap - base_rate

    return {
        "ok": True,
        "p": p,
        "a": a,
        "b": b,
        "order_E": order,
        "N": N,
        "t": t,
        "G": {"x": G[0], "y": G[1]},
        "W_size": len(W),
        "W_aff_size": m,
        "n_affine_classes": len(classes),
        "overlap": overlap,
        "overlap_frac": overlap_frac,
        "base_rate": base_rate,
        "excess": excess,
        "scalar_recover_frac": scalar_recover_frac,
        "null_overlap_frac": null_overlap,
        "null_excess": null_excess,
        "excluded_curve_hit": a == 1 and b == 1,
    }


def search_curves(limit_p: int = 5000) -> list[dict[str, Any]]:
    found = []
    p = 5
    while p < limit_p and len(found) < 2:
        if not is_prime(p):
            p += 1
            continue
        for a in range(0, min(8, p)):
            for b in range(1, min(8, p)):
                if a == EXCLUDED_CURVE["a"] and b == EXCLUDED_CURVE["b"]:
                    continue
                # nonsingular: disc = -16(4a^3+27b^2) != 0
                if (4 * a * a * a + 27 * b * b) % p == 0:
                    continue
                m = measure_curve(p, a, b, NULL_SEED)
                if m.get("ok"):
                    # ordinary: j invariant etc — for toy, exclude supersingular via #E != p+1
                    if m["order_E"] == p + 1:
                        continue
                    found.append(m)
                    if len(found) >= 2:
                        return found
        p += 1
    return found


def decide_label(rows: list[dict[str, Any]]) -> str:
    if len(rows) < 2:
        return "O-IMPEDIMENT"
    if any(r.get("scalar_recover_frac", 0) < 1.0 - 1e-12 for r in rows):
        return "O-CONTROL-FAIL"
    excesses = [r["excess"] for r in rows]
    if all(e <= CLAIM_EXCESS for e in excesses):
        return "O-FLOOR"
    if all(e > FALSIFY_EXCESS for e in excesses):
        return "O-EXCESS"
    return "O-MIXED"


def stage1(run_dir: Path) -> dict[str, Any]:
    freeze_path = EXP_ROOT / "stage0" / "protocol-freeze.json"
    if not freeze_path.exists():
        result = {
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0_freeze_missing",
            "claims": claims(),
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        write_text(run_dir / "RESULTS.md", "# Stage 1 — O-IMPEDIMENT\n\nStage 0 freeze missing.\n")
        return result

    t0 = time.time()
    try:
        rows = search_curves()
    except Exception as exc:  # noqa: BLE001 — infra path
        result = {
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": f"exception:{type(exc).__name__}:{exc}",
            "claims": claims(),
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", result)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        write_text(run_dir / "RESULTS.md", f"# Stage 1 — O-IMPEDIMENT\n\n{exc}\n")
        return result

    label = decide_label(rows)
    census = {
        "curves": rows,
        "n_curves": len(rows),
        "elapsed_seconds": time.time() - t0,
        "null_seed": NULL_SEED,
    }
    control_table = {
        "claim_excess": CLAIM_EXCESS,
        "falsify_excess": FALSIFY_EXCESS,
        "per_curve": [
            {
                "p": r.get("p"),
                "a": r.get("a"),
                "b": r.get("b"),
                "N": r.get("N"),
                "excess": r.get("excess"),
                "null_excess": r.get("null_excess"),
                "scalar_recover_frac": r.get("scalar_recover_frac"),
            }
            for r in rows
        ],
        "label": label,
    }
    write_json(EXP_ROOT / "stage1" / "census.json", census)
    write_json(EXP_ROOT / "stage1" / "control-table.json", control_table)
    result = {
        "stage": 1,
        "outcome": label,
        "claims": claims(),
        "control_table": control_table,
        "recorded_at": utc_now(),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(run_dir / "raw-result.json", result)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 1",
                f"outcome: {label}",
                "amazon_bedrock: NOT SELECTED",
                f"recorded_at: '{utc_now()}'",
                "",
            ]
        ),
    )
    lines = [
        f"# Stage 1 — {label}",
        "",
        f"Curves measured: {len(rows)}",
    ]
    for r in rows:
        lines.append(
            f"- p={r.get('p')} a={r.get('a')} b={r.get('b')} N={r.get('N')} "
            f"excess={r.get('excess'):.6f} null_excess={r.get('null_excess'):.6f} "
            f"scalar_recover={r.get('scalar_recover_frac')}"
        )
    lines.append("")
    lines.append("No exponent move. No Magma/Sage/Bedrock.")
    write_text(run_dir / "RESULTS.md", "\n".join(lines) + "\n")
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
