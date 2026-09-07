"""Stage 2 for EXP-ECDLP-a98ea9: instrument gates. No digit ADV.

Hard gate. Known-answer valuation, POSITIVE CONTROL B, planted-advantage
ladder, r=1 fixture versus IDEA-20260815-f558e4. Failure STOPS before
any T1-T4 number is recorded. This file does not compute those numbers.
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

from ec_jac import Curve, affine_xy, jac_add, jac_infinity, valuation
from kfree_transport import canonical_order_n_lift
from qmaj import (
    interval_partition,
    q_maj_brute_group,
    q_maj_exact,
    q_strict_exact,
    x_bucket_labels,
)
from runrecord import _dump_yaml, write_run_record
from static_provenance import check_kfree_module

HERE = Path(__file__).resolve().parent
RUN_DIR = HERE.parent / "runs" / "RUN-ECDLP-a98ea9-S2c"
REPORT_PATH = HERE.parent / "execution-report-stage2c.yaml"
TASK_ID = "TASK-20260907-6e2d36"
SEEDS = [3, 5, 7, 11, 13, 17, 19, 23]
WEIGHTS = [1.0, 0.2, 0.06, 0.02]
SIBLING_XBUCKET = {2: 0.530, 3: 0.394, 4: 0.342, 5: 0.282}
SIBLING_INTERVAL = {
    "n": 23,
    "s": 3,
    "q_maj": Fraction(284, 529),
    "q_strict": Fraction(0, 1),
}
# Stage 1 instance with smallest n (DEV-2 band). Known-answer only.
KA_INSTANCE = {
    "p": 949423,
    "A": 610648,
    "B": 188380,
    "n": 39503,
    "S": (377953, 722598),
}
POSB_NS = [23, 211, 809]
LADDER_N = 809
LADDER_S = 3
SMOKE = [(101, 115), (103, 118), (107, 105)]


def _legendre(a: int, p: int) -> int:
    return pow(a % p, (p - 1) // 2, p)


def _tonelli(n: int, p: int) -> int:
    if _legendre(n, p) != 1:
        raise ValueError("not a square")
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    z = 2
    while _legendre(z, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    while t != 1:
        i = 1
        tt = (t * t) % p
        while tt != 1:
            tt = (tt * tt) % p
            i += 1
            if i == m:
                raise ValueError("tonelli failed")
        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        c = (b * b) % p
        t = (t * c) % p
        m = i
    return r


def _point_count(p: int, b: int) -> int:
    count = 1
    for x in range(p):
        rhs = (x * x * x + x + b) % p
        if rhs == 0:
            count += 1
        elif _legendre(rhs, p) == 1:
            count += 2
    return count


def _find_smoke_curves() -> list[dict]:
    curves = []
    for p, n_target in SMOKE:
        found = None
        for b in range(1, 200):
            if _point_count(p, b) == n_target:
                found = {"p": p, "A": 1, "B": b, "N": n_target}
                break
        if found is None:
            raise ValueError(f"no y^2=x^3+x+b with #E={n_target} over F_{p}")
        curves.append(found)
    return curves


def _enumerate_full_group(p: int, b: int) -> list[tuple | None]:
    points: list[tuple | None] = [None]
    for x in range(p):
        rhs = (x * x * x + x + b) % p
        if rhs == 0:
            points.append((x, 0))
        elif _legendre(rhs, p) == 1:
            y = _tonelli(rhs, p)
            points.append((x, y))
            points.append((x, (p - y) % p))
    return points


def _add_fp(p: int, b: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + 1) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def interval_fixture() -> dict:
    n, s = SIBLING_INTERVAL["n"], SIBLING_INTERVAL["s"]
    v = interval_partition(n, s)
    qm = q_maj_exact(v, n)
    qs = q_strict_exact(v, n)
    return {
        "n": n,
        "s": s,
        "q_maj": f"{qm.numerator}/{qm.denominator}",
        "q_maj_expected": "284/529",
        "q_strict": f"{qs.numerator}/{qs.denominator}",
        "q_strict_expected": "0",
        "pass": qm == SIBLING_INTERVAL["q_maj"] and qs == SIBLING_INTERVAL["q_strict"],
        "source": "IDEA-20260815-f558e4 proof_search_map.baseline_embedding",
        "note": "Exact rational fixture of the interval partition, not an x-bucket cell.",
    }


def xbucket_fixture() -> dict:
    curves = _find_smoke_curves()
    results = []
    all_ok = True
    for curve in curves:
        p, b, n = curve["p"], curve["B"], curve["N"]
        points = _enumerate_full_group(p, b)
        if len(points) != n:
            raise RuntimeError(f"point count {len(points)} != {n}")
        index = {pt: i for i, pt in enumerate(points)}
        add = np.zeros((n, n), dtype=np.int32)
        for i, P in enumerate(points):
            for j, Q in enumerate(points):
                add[i, j] = index[_add_fp(p, b, P, Q)]
        xs = [0 if pt is None else pt[0] for pt in points]
        for s in (2, 3, 4, 5):
            labels = [int(x) for x in x_bucket_labels(xs, p, s)]
            qm = q_maj_brute_group(labels, add)
            expected = SIBLING_XBUCKET[s]
            rounded = round(float(qm), 3)
            ok = rounded == expected
            all_ok = all_ok and ok
            results.append({
                "p": p,
                "N": n,
                "s": s,
                "q_maj": f"{qm.numerator}/{qm.denominator}",
                "q_maj_float": float(qm),
                "q_maj_rounded_3dp": rounded,
                "sibling_committed_3dp": expected,
                "match_3dp": ok,
            })
    return {
        "curves": curves,
        "results": results,
        "role": "diagnostic",
        "hard_gate": False,
        "match_3dp_all": all_ok,
        "pass": True,
        "source": "IDEA-20260815-f558e4 section (G)",
        "amendment": "v3_xbucket_diagnostic",
        "caveat": (
            "Diagnostic only under DEC-20260907-933a06. Those curves "
            "were used at full COMPOSITE group order (N=115,118,105). "
            "The sibling published three-decimal smoke values, not "
            "exact rationals. match_3dp is recorded and is not a "
            "hard gate. Nearby is not a pass."
        ),
    }


def known_answer() -> dict:
    inst = KA_INSTANCE
    curve = Curve(inst["p"], inst["A"], inst["B"])
    n = inst["n"]
    S = inst["S"]
    r = 4
    mod = curve.p**r
    Shat = canonical_order_n_lift(curve, S, n, r)
    x_ref, _ = affine_xy(curve, Shat, mod)
    values = []
    P = jac_infinity()
    on_fibre = []
    off_vals: set[int] = set()
    off_large = 0
    for k in range(n):
        if k == 0:
            values.append(None)
            P = jac_add(curve, P, Shat, mod)
            continue
        ax, _ = affine_xy(curve, P, mod)
        val = valuation((ax - x_ref) % mod, curve.p, r, mod)
        values.append(val)
        on = k in (1, n - 1)
        if on:
            on_fibre.append({"k": k, "valuation": val})
        else:
            off_vals.add(val)
            if val >= r:
                off_large += 1
        P = jac_add(curve, P, Shat, mod)
    finite = [v for v in values if v is not None]
    image = sorted(set(finite))
    on_vals = {c["valuation"] for c in on_fibre}
    two_valued = len(image) == 2
    large = max(image) if image else None
    large_on_pm = on_vals == {large} and large not in off_vals
    return {
        "p": inst["p"],
        "n": n,
        "r": r,
        "S": list(S),
        "value_set": image,
        "on_plus_minus_fibre": on_fibre,
        "off_fibre_value_set": sorted(off_vals),
        "off_fibre_at_cap_count": off_large,
        "two_valued": two_valued,
        "large_value_exactly_on_plus_minus_fibre": bool(large_on_pm),
        "pass": two_valued and bool(large_on_pm) and off_large == 0,
        "statistic": "T5 v_p(x([k]S-hat) - x(S-hat)) truncated at r=4",
        "k0_skipped": "k=0 is the identity; no affine x.",
    }


def positive_control_b() -> dict:
    cells = []
    all_ok = True
    for n in POSB_NS:
        v = interval_partition(n, 3)
        qm = q_maj_exact(v, n)
        ok = Fraction(45, 100) <= qm <= Fraction(65, 100)
        all_ok = all_ok and ok
        cells.append({
            "n": n,
            "s": 3,
            "q_maj": f"{qm.numerator}/{qm.denominator}",
            "q_maj_float": float(qm),
            "near_one_half": ok,
        })
    return {
        "cells": cells,
        "pass": all_ok,
        "criterion": "interval-partition q_maj in [0.45, 0.65] at each tested prime n",
        "note": "The sibling states interval q_maj is flat near 1/2, independent of s.",
    }


def planted_ladder() -> dict:
    n, s = LADDER_N, LADDER_S
    interval = interval_partition(n, s)
    qm_int = q_maj_exact(interval, n)
    adv_int = qm_int - Fraction(1, s)
    rungs = []
    smallest_recovered = True
    all_recovered = True
    for w in WEIGHTS:
        planted = Fraction(int(round(w * 10_000)), 10_000) * adv_int
        recovered_by_seed = []
        for seed in SEEDS:
            rng = random.Random(seed)
            labels = np.empty(n, dtype=np.int64)
            for k in range(n):
                if rng.random() < w:
                    labels[k] = int(interval[k])
                else:
                    labels[k] = rng.randrange(s)
            qm = q_maj_exact(labels, n)
            adv = qm - Fraction(1, s)
            recovered_by_seed.append({
                "seed": seed,
                "q_maj": f"{qm.numerator}/{qm.denominator}",
                "ADV": float(adv),
            })
        official = next(x for x in recovered_by_seed if x["seed"] == 3)
        advs = [x["ADV"] for x in recovered_by_seed]
        lo, hi = min(advs), max(advs)
        planted_f = float(planted)
        recovered = official["ADV"]
        # Seed-interval is the declared bootstrap stand-in for a fixed mix.
        in_interval = lo - 1e-12 <= planted_f <= hi + 1e-12
        close = abs(recovered - planted_f) <= 0.025
        recovered_ok = in_interval or close
        if w == 0.02:
            smallest_recovered = recovered_ok
        all_recovered = all_recovered and recovered_ok
        rungs.append({
            "w": w,
            "planted_ADV": planted_f,
            "planted_ADV_exact": f"{planted.numerator}/{planted.denominator}",
            "official_seed": 3,
            "recovered_ADV": recovered,
            "seed_interval": [lo, hi],
            "recovered": recovered_ok,
            "per_seed": recovered_by_seed,
        })
    stage2b = not smallest_recovered
    return {
        "n": n,
        "s": s,
        "interval_q_maj": f"{qm_int.numerator}/{qm_int.denominator}",
        "interval_ADV": float(adv_int),
        "rungs": rungs,
        "all_rungs_recovered": all_recovered,
        "smallest_rung_recovered": smallest_recovered,
        "stage2b_threshold_raise_required": stage2b,
        "pass": all_recovered or stage2b,
        "note": (
            "Planted ADV = w * (q_maj(interval) - 1/s). Mix is per-k: "
            "interval label with probability w, else uniform in 0..s-1. "
            "Eight declared seeds; official cell is seed 3. No T1-T4 ADV."
        ),
    }


def main() -> int:
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    provenance = check_kfree_module(HERE / "kfree_transport.py")
    fx_interval = interval_fixture()
    fx_xbucket = xbucket_fixture()
    ka = known_answer()
    posb = positive_control_b()
    ladder = planted_ladder()
    hard_gates = {
        "interval_fixture": fx_interval["pass"],
        "known_answer": ka["pass"],
        "positive_control_b": posb["pass"],
        "planted_ladder": ladder["pass"],
        "static_provenance": bool(provenance.get("passed")),
    }
    diagnostic = {
        "xbucket_3dp": {
            "role": "diagnostic",
            "hard_gate": False,
            "match_3dp_all": fx_xbucket.get("match_3dp_all"),
        }
    }
    passed = all(hard_gates.values())
    raw = {
        "stage": 2,
        "run_id": "RUN-ECDLP-a98ea9-S2c",
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "task_id": TASK_ID,
        "amendment": "v3_xbucket_diagnostic",
        "authorized_stages": [0, 1, 2],
        "certificate": {"kind": "none"},
        "digit_ADV_computed": False,
        "static_provenance": provenance,
        "interval_fixture": fx_interval,
        "xbucket_diagnostic": fx_xbucket,
        "known_answer": ka,
        "positive_control_b": posb,
        "planted_ladder": ladder,
        "hard_gates": hard_gates,
        "diagnostic": diagnostic,
        "validity": "valid" if passed else "gate_failure",
        "validity_reason": (
            "all Stage 2 hard gates passed under v3_xbucket_diagnostic"
            if passed
            else f"gate failure: {[k for k, v in hard_gates.items() if not v]}"
        ),
    }
    raw_path = RUN_DIR / "raw-result.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    wall = time.time() - t0
    write_run_record(
        RUN_DIR,
        stage="2",
        command="python3 implementation/stage2.py",
        params={"authorized_stages": [0, 1, 2], "seeds": SEEDS},
        seeds={"declared": SEEDS},
        validity=raw["validity"],
        validity_reason=raw["validity_reason"],
        wall_clock_s=wall,
        stdout=json.dumps({
            "hard_gates": hard_gates,
            "diagnostic": diagnostic,
            "validity": raw["validity"],
        }, indent=2) + "\n",
        stderr="",
        raw_result_file="raw-result.json",
        model_id="cursor-grok-4.6-cloud-agent",
        repo_root=HERE.parents[2],
        extra_artifacts={},
        task_id=TASK_ID,
        scientific_boundary=(
            "Stage 2 instrument gates only. No T1-T4 ADV, no D2 disposition."
        ),
    )
    report = {
        "execution_report": {
            "experiment_id": "EXP-ECDLP-a98ea9",
            "hypothesis_id": "H-ECDLP-07c7c6",
            "task_id": TASK_ID,
            "run_id": "RUN-ECDLP-a98ea9-S2c",
            "amendment": "v3_xbucket_diagnostic",
            "authorized_stages": [0, 1, 2],
            "certificate": {"kind": "none"},
            "digit_ADV_computed": False,
            "hard_gates": hard_gates,
            "diagnostic": diagnostic,
            "validity": raw["validity"],
            "validity_reason": raw["validity_reason"],
            "wall_clock_seconds": round(wall, 3),
            "scientific_boundary": (
                "Stage 2 instrument gates only under "
                "v3_xbucket_diagnostic. No T1-T4 ADV, no D2."
            ),
        }
    }
    REPORT_PATH.write_text(_dump_yaml(report) + "\n")
    print(json.dumps({
        "hard_gates": hard_gates,
        "diagnostic": diagnostic,
        "validity": raw["validity"],
    }, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    # Write a real YAML report after the run body so a failure still records.
    sys.exit(main())
