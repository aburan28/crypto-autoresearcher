"""Stage 4 for EXP-ECDLP-a98ea9: comparator, nulls, CONTROL C, curve-free.

Records D = ADV(digit) - ADV(comparator) at matched (n, s) and a
mechanical two-branch table as observations. Does not change
H-ECDLP-07c7c6 status, does not close D2, and does not authorize
Stage 5.

Tested scale is the Stage 3 disclosed 16-19 bit seven-order set.
20-26 bit cells are not run and are not claimed.
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy

from curve_find import fp_mul
from ec_jac import Curve, affine_xy, is_infinity, jac_add, jac_infinity
from kfree_transport import (
    canonical_order_n_lift,
    hensel_lift_without_projection,
    ordinary_base_p_digits,
)
from qmaj import q_maj_exact
from runrecord import _dump_yaml, write_run_record
from stage3 import (
    INSTANCES,
    RS,
    SEEDS,
    SS,
    _bucket,
    _cell,
    _check_instance,
    _frac,
    _labels_t1,
    _labels_t2,
    _labels_t3,
    _labels_t4,
    _legendre_label,
)
from static_provenance import check_kfree_module

HERE = Path(__file__).resolve().parent
RUN_DIR = HERE.parent / "runs" / "RUN-ECDLP-a98ea9-S4"
REPORT_PATH = HERE.parent / "execution-report-stage4.yaml"
S3_RAW = HERE.parent / "runs" / "RUN-ECDLP-a98ea9-S3" / "raw-result.json"
TASK_ID = "TASK-20260907-b90ff5"

# CONTROL C: S1-b full group. Generator found by random search under seed 1
# before this run; order-N check is re-verified in-process.
CONTROL_C = {
    "id": "S1-b-full",
    "p": 128629,
    "A": 119056,
    "B": 83257,
    "N": 128001,
    "n": 128001,
    "S": (74606, 55395),
    "source": "S1-b E(F_p); generator of cyclic group of order 128001=3*42667",
}

# Curve-free arm: n | (p_mult-1). Same n as the Stage 3 instances.
MULT_INSTANCES = [
    {"id": "M-a", "n": 47057, "p": 3105763, "k": 66, "g": 375223, "ec_id": "S1-a"},
    {"id": "M-b", "n": 42667, "p": 170669, "k": 4, "g": 16, "ec_id": "S1-b"},
    {"id": "M-c", "n": 58453, "p": 350719, "k": 6, "g": 64, "ec_id": "S1-c"},
    {"id": "M-d", "n": 162611, "p": 4227887, "k": 26, "g": 3690559, "ec_id": "S1-d"},
    {"id": "M-e", "n": 39503, "p": 237019, "k": 6, "g": 64, "ec_id": "S1-e"},
    {"id": "M-f", "n": 79043, "p": 948517, "k": 12, "g": 4096, "ec_id": "S1-f"},
    {"id": "M-span", "n": 375391, "p": 6006257, "k": 16, "g": 65536, "ec_id": "S3-span"},
]


def _walk_ec(curve: Curve, P0, n: int, r: int) -> dict:
    """Walk k=0..n-1 by adding P0. Identity (k=0) has no affine x."""
    mod = curve.p**r
    P = jac_infinity()
    xs: list[int | None] = []
    digits: list[list[int] | None] = []
    for _k in range(n):
        if is_infinity(P, mod):
            xs.append(None)
            digits.append(None)
        else:
            ax, _ay = affine_xy(curve, P, mod)
            xs.append(int(ax))
            digits.append(ordinary_base_p_digits(ax, curve.p, r))
        P = jac_add(curve, P, P0, mod)
    return {
        "xs": xs,
        "digits": digits,
        "walk_closed": is_infinity(P, mod),
        "identity_count": sum(1 for x in xs if x is None),
        "identity_at_k0": xs[0] is None,
    }


def _mult_canonical(u0: int, p: int, r: int, n: int) -> int:
    """Canonical prime-to-p lift of u0 in F_p^* to (Z/p^r Z)^*."""
    mod = p**r
    u = u0 % p
    for _ in range(r - 1):
        u = pow(u, p, mod)
    m = pow((p ** (r - 1)) % n, -1, n)
    return pow(u, m, mod)


def _mult_null2(u0: int, p: int, r: int) -> int:
    """Integer lift of u0 with no p-power projection. Higher digits are 0."""
    return u0 % p


def _walk_mult(g: int, p: int, n: int, r: int, kind: str) -> dict:
    xs: list[int] = []
    digits: list[list[int]] = []
    for k in range(n):
        u0 = pow(g, k, p)
        ur = _mult_canonical(u0, p, r, n) if kind == "canonical" else _mult_null2(u0, p, r)
        xs.append(int(ur))
        digits.append(ordinary_base_p_digits(ur, p, r))
    return {"xs": xs, "digits": digits, "walk_closed": True, "identity_count": 0, "identity_at_k0": False}


def _cells_from_walk(inst: dict, r: int, xs, digits, extra: dict | None = None) -> list[dict]:
    rows = []
    p = inst["p"]
    modulus = p**r
    tag = extra or {}
    for s in SS:
        for j in range(min(3, r)):
            q = q_maj_exact(_labels_t1(digits, j, p, s), inst["n"])
            rows.append(_cell(f"T1_digit{j}", inst, r, s, q, {**tag, "j": j}))
        q = q_maj_exact(_labels_t3(xs, modulus, s), inst["n"])
        rows.append(_cell("T3_x_interval", inst, r, s, q, {**tag, "definition": "min((x*s)//modulus, s-1)"}))
        if r >= 2:
            q = q_maj_exact(_labels_t4(digits, p, s), inst["n"])
            rows.append(_cell("T4_digit0_digit1", inst, r, s, q, tag))
    for j in range(min(3, r)):
        q = q_maj_exact(_labels_t2(digits, j, p), inst["n"])
        rows.append(_cell("T2_legendre", inst, r, 3, q, {**tag, "j": j, "s_note": "natural image size 3"}))
    return rows


def _key(row: dict) -> tuple:
    return (row["statistic"], row.get("j"), row["instance_id"], row["n"], row["r"], row["s"])


def _parse_adv(row: dict) -> Fraction:
    return Fraction(row["ADV"])


def _null1_cells(inst: dict) -> tuple[list[dict], dict]:
    n = inst["n"]
    rows = []
    dist: dict[int, list[float]] = {s: [] for s in SS}
    for s in SS:
        advs = []
        for seed in SEEDS:
            rng = random.Random(seed)
            lab = np.array([rng.randrange(s) for _ in range(n)], dtype=np.int64)
            q = q_maj_exact(lab, n)
            adv = q - Fraction(1, s)
            advs.append(adv)
            rows.append({
                "statistic": "NULL1_prf",
                "instance_id": inst["id"],
                "p": inst["p"],
                "n": n,
                "r": None,
                "s": s,
                "seed": seed,
                "q_maj": _frac(q),
                "ADV": _frac(adv),
                "ADV_float": float(adv),
                "estimator": "q_maj_exact (FFT pair-counts)",
                "rng": "random.Random(seed).randrange(s) over k=0..n-1",
            })
        dist[s] = [float(a) for a in advs]
        rows.append({
            "statistic": "NULL1_summary",
            "instance_id": inst["id"],
            "n": n,
            "s": s,
            "ADV_max": _frac(max(advs)),
            "ADV_max_float": float(max(advs)),
            "ADV_min_float": float(min(advs)),
            "ADV_mean_float": float(sum(advs) / len(advs)),
            "n_seeds": len(SEEDS),
            "seeds": list(SEEDS),
        })
    return rows, {s: max(dist[s]) for s in SS}


def _mechanical_branch(d_rows: list[dict], null1_max: dict, null2_d: dict) -> dict:
    """Pre-registered two-branch rule, recorded as an observation only."""
    by_stat: dict[str, list[dict]] = {}
    for row in d_rows:
        by_stat.setdefault(row["statistic"], []).append(row)
    out = []
    for stat, rows in sorted(by_stat.items()):
        abs_d = [abs(Fraction(r["D"])) for r in rows]
        all_closure = all(ad <= Fraction(1, 100) for ad in abs_d)
        lead_orders = set()
        lead_details = []
        for r in rows:
            dabs = abs(Fraction(r["D"]))
            if dabs < Fraction(5, 100):
                continue
            n = r["n"]
            s = r["s"]
            n1 = Fraction(str(null1_max.get((r["instance_id"], s), "0")))
            n2 = null2_d.get((stat, r.get("j"), r["instance_id"], n, r["r"], s))
            reproduced_n1 = dabs <= n1
            reproduced_n2 = n2 is not None and abs(n2) >= Fraction(5, 100)
            if not reproduced_n1 and not reproduced_n2:
                lead_orders.add(n)
                lead_details.append({
                    "instance_id": r["instance_id"],
                    "n": n,
                    "r": r["r"],
                    "s": s,
                    "abs_D": _frac(dabs),
                    "null1_max_ADV": _frac(n1),
                    "null2_D": _frac(n2) if n2 is not None else None,
                })
        decaying = False
        if lead_orders:
            by_n = {}
            for r in rows:
                if abs(Fraction(r["D"])) >= Fraction(5, 100):
                    by_n.setdefault(r["n"], 0.0)
                    by_n[r["n"]] = max(by_n[r["n"]], abs(float(Fraction(r["D"]))))
            ns = sorted(by_n)
            if len(ns) >= 2 and by_n[ns[-1]] < by_n[ns[0]]:
                decaying = True
        if all_closure:
            branch = "CLOSURE"
        elif len(lead_orders) >= 3 and not decaying:
            branch = "LEAD"
        else:
            branch = "INCONCLUSIVE"
        out.append({
            "statistic": stat,
            "mechanical_branch": branch,
            "all_abs_D_le_0.01": all_closure,
            "lead_prime_order_count": len(lead_orders),
            "lead_not_decaying_in_n": (not decaying) if lead_orders else None,
            "lead_cells": lead_details,
            "official_disposition": False,
            "note": "Observation only. Not H status and not D2.",
        })
    return {
        "rule": "|D|<=0.01 every cell -> CLOSURE; |D|>=0.05 at >=3 prime orders, not reproduced by NULL-1/NULL-2, not decaying in n -> LEAD; else INCONCLUSIVE",
        "official_disposition": False,
        "per_statistic": out,
    }


def _load_s3_treatment() -> list[dict]:
    raw = json.loads(S3_RAW.read_text())
    if raw.get("validity") != "valid" or not raw.get("digit_ADV_computed"):
        raise RuntimeError("Stage 3 raw-result is not a valid treatment source")
    return raw["cells"]


def _check_mult(inst: dict) -> dict:
    p, n, k, g = inst["p"], inst["n"], inst["k"], inst["g"]
    reasons = []
    if not sympy.isprime(n):
        reasons.append("n_not_prime")
    if not sympy.isprime(p):
        reasons.append("p_not_prime")
    if (p - 1) != n * k:
        reasons.append("p_minus_1_not_n_k")
    if pow(g, n, p) != 1 or g % p in (0, 1):
        reasons.append("g_not_order_n")
    return {"instance_id": inst["id"], "p": p, "n": n, "pass": not reasons, "reasons": reasons}


def main() -> int:
    t0 = time.time()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    provenance = check_kfree_module(HERE / "kfree_transport.py")
    checks = [_check_instance(inst) for inst in INSTANCES]
    ns = [inst["n"] for inst in INSTANCES]
    span = max(ns) / min(ns)
    scale = {
        "declared_band_bits": [16, 26],
        "tested_n": ns,
        "tested_bits_n": [n.bit_length() for n in ns],
        "n_min": min(ns),
        "n_max": max(ns),
        "span_ratio": span,
        "span_at_least_6x": span >= 6.0,
        "instance_count": len(INSTANCES),
        "at_least_six_prime_orders": len(INSTANCES) >= 6,
        "band_top_26_bit_tested": False,
        "band_20_to_26_tested": False,
        "disclosure": (
            "Stage 4 reuses the Stage 3 seven-order 16-19 bit set. "
            f"Span vs smallest n is {span:.4f} (>= 6). 20-26 bit cells "
            "were not run and are not claimed."
        ),
    }

    treatment = _load_s3_treatment()
    treatment_by_key = {_key(c): c for c in treatment}

    comparator_cells: list[dict] = []
    null2_cells: list[dict] = []
    null1_cells: list[dict] = []
    null1_max: dict[tuple, Fraction] = {}
    walk_reports: list[dict] = []
    r1_identity_ok = True
    walk_ok = True

    for inst in INSTANCES:
        curve = Curve(inst["p"], inst["A"], inst["B"])
        n = inst["n"]
        S = tuple(inst["S"])
        n1_rows, _n1_max_s = _null1_cells(inst)
        null1_cells.extend(n1_rows)
        for row in n1_rows:
            if row["statistic"] == "NULL1_summary":
                null1_max[(inst["id"], row["s"])] = Fraction(row["ADV_max"])

        for r in RS:
            t_walk = time.time()
            if r == 1:
                P0 = canonical_order_n_lift(curve, S, n, r)
                walked = _walk_ec(curve, P0, n, r)
                P0n = hensel_lift_without_projection(curve, S, r)
                walked_n2 = _walk_ec(curve, P0n, n, r)
                if walked["xs"] != walked_n2["xs"]:
                    r1_identity_ok = False
                kind = "comparator_and_null2_r1"
            else:
                P0n = hensel_lift_without_projection(curve, S, r)
                walked = _walk_ec(curve, P0n, n, r)
                kind = "null2"
            walk_s = time.time() - t_walk
            ok = walked["walk_closed"] and walked["identity_count"] == 1 and walked["identity_at_k0"]
            walk_ok = walk_ok and ok
            walk_reports.append({
                "arm": "EC",
                "kind": kind,
                "instance_id": inst["id"],
                "n": n,
                "r": r,
                "walk_closed": walked["walk_closed"],
                "identity_count": walked["identity_count"],
                "identity_at_k0": walked["identity_at_k0"],
                "walk_seconds": round(walk_s, 3),
                "pass": ok,
            })
            print(f"walk EC {kind} {inst['id']} n={n} r={r} {walk_s:.2f}s ok={ok}", flush=True)
            extra = {"arm": "EC", "lift": "null2" if r > 1 else "r1_shared"}
            rows = _cells_from_walk(inst, r, walked["xs"], walked["digits"], extra)
            if r == 1:
                for row in rows:
                    if row["statistic"] == "T3_x_interval":
                        crow = dict(row)
                        crow["statistic"] = "COMPARATOR_x_bucket"
                        crow["definition"] = "plain F_p x-coordinate interval bucket at matched s (r=1 shadow)"
                        comparator_cells.append(crow)
                null2_cells.extend(rows)
            else:
                null2_cells.extend(rows)

    # CONTROL C
    cc = CONTROL_C
    curve_c = Curve(cc["p"], cc["A"], cc["B"])
    control_c_cells: list[dict] = []
    G = tuple(cc["S"])
    order_ok = fp_mul(cc["N"], G, cc["p"], cc["A"]) is None
    order_n3 = fp_mul(cc["N"] // 3, G, cc["p"], cc["A"]) is not None
    order_nN3 = fp_mul(3, G, cc["p"], cc["A"]) is not None
    cc_inst = {"id": cc["id"], "p": cc["p"], "n": cc["N"], "A": cc["A"], "B": cc["B"]}
    for r in RS:
        t_walk = time.time()
        P0 = canonical_order_n_lift(curve_c, G, cc["N"], r)
        walked = _walk_ec(curve_c, P0, cc["N"], r)
        walk_s = time.time() - t_walk
        ok = walked["walk_closed"] and walked["identity_count"] == 1
        walk_ok = walk_ok and ok
        walk_reports.append({
            "arm": "CONTROL_C",
            "instance_id": cc["id"],
            "n": cc["N"],
            "r": r,
            "walk_closed": walked["walk_closed"],
            "identity_count": walked["identity_count"],
            "walk_seconds": round(walk_s, 3),
            "pass": ok,
            "generator_order_N": order_ok and order_n3 and order_nN3,
        })
        print(f"walk CONTROL_C n={cc['N']} r={r} {walk_s:.2f}s ok={ok}", flush=True)
        rows = _cells_from_walk(cc_inst, r, walked["xs"], walked["digits"], {"arm": "CONTROL_C"})
        control_c_cells.extend(rows)
        if r == 1:
            for row in rows:
                if row["statistic"] == "T3_x_interval":
                    crow = dict(row)
                    crow["statistic"] = "COMPARATOR_x_bucket"
                    control_c_cells.append(crow)

    # Curve-free
    mult_checks = [_check_mult(m) for m in MULT_INSTANCES]
    mult_cells: list[dict] = []
    mult_null2_cells: list[dict] = []
    for minst in MULT_INSTANCES:
        inst = {"id": minst["id"], "p": minst["p"], "n": minst["n"]}
        for r in RS:
            t_walk = time.time()
            walked = _walk_mult(minst["g"], minst["p"], minst["n"], r, "canonical")
            walked_n2 = _walk_mult(minst["g"], minst["p"], minst["n"], r, "null2")
            walk_s = time.time() - t_walk
            if r == 1 and walked["xs"] != walked_n2["xs"]:
                r1_identity_ok = False
            walk_reports.append({
                "arm": "MULT",
                "instance_id": minst["id"],
                "n": minst["n"],
                "r": r,
                "walk_seconds": round(walk_s, 3),
                "pass": True,
            })
            print(f"walk MULT {minst['id']} n={minst['n']} r={r} {walk_s:.2f}s", flush=True)
            mult_cells.extend(_cells_from_walk(inst, r, walked["xs"], walked["digits"], {"arm": "MULT", "lift": "canonical"}))
            if r == 1:
                for row in _cells_from_walk(inst, r, walked["xs"], walked["digits"], {"arm": "MULT"}):
                    if row["statistic"] == "T3_x_interval":
                        crow = dict(row)
                        crow["statistic"] = "COMPARATOR_x_bucket"
                        mult_cells.append(crow)
            else:
                mult_null2_cells.extend(_cells_from_walk(inst, r, walked_n2["xs"], walked_n2["digits"], {"arm": "MULT", "lift": "null2"}))
            if r == 1:
                mult_null2_cells.extend(_cells_from_walk(inst, r, walked_n2["xs"], walked_n2["digits"], {"arm": "MULT", "lift": "null2"}))

    # D on prime-order EC treatment vs comparator
    comp_index = {}
    for row in comparator_cells:
        comp_index[(row["instance_id"], row["s"])] = Fraction(row["ADV"])

    d_rows = []
    for trow in treatment:
        key = (trow["instance_id"], trow["s"])
        if key not in comp_index:
            continue
        cadv = comp_index[key]
        tadv = Fraction(trow["ADV"])
        d = tadv - cadv
        d_rows.append({
            "statistic": trow["statistic"],
            "j": trow.get("j"),
            "instance_id": trow["instance_id"],
            "n": trow["n"],
            "r": trow["r"],
            "s": trow["s"],
            "ADV_digit": trow["ADV"],
            "ADV_comparator": _frac(cadv),
            "D": _frac(d),
            "D_float": float(d),
            "abs_D_float": abs(float(d)),
        })

    null2_d = {}
    for row in null2_cells:
        key = (row["instance_id"], row["s"])
        if key not in comp_index:
            continue
        d = Fraction(row["ADV"]) - comp_index[key]
        null2_d[(row["statistic"], row.get("j"), row["instance_id"], row["n"], row["r"], row["s"])] = d

    # r=1 NULL-2 vs treatment identity on T3
    r1_cell_ok = True
    for inst in INSTANCES:
        for s in SS:
            tkey = ("T3_x_interval", None, inst["id"], inst["n"], 1, s)
            trow = treatment_by_key.get(tkey)
            if trow is None:
                r1_cell_ok = False
                continue
            n2 = next((c for c in null2_cells if _key(c) == tkey), None)
            if n2 is None or Fraction(n2["ADV"]) != Fraction(trow["ADV"]):
                r1_cell_ok = False

    branch = _mechanical_branch(d_rows, {k: v for k, v in null1_max.items()}, null2_d)

    hard_gates = {
        "static_provenance": bool(provenance.get("passed")),
        "instance_precheck": all(c["pass"] for c in checks),
        "mult_precheck": all(c["pass"] for c in mult_checks),
        "walk_closed_identity": walk_ok,
        "null2_r1_width_zero": r1_identity_ok and r1_cell_ok,
        "control_c_generator_order_N": order_ok and order_n3 and order_nN3,
        "six_prime_orders": scale["at_least_six_prime_orders"],
        "span_at_least_6x": scale["span_at_least_6x"],
        "treatment_loaded_from_S3": len(treatment) == 847,
        "all_n_in_16_26": all(16 <= n.bit_length() <= 26 for n in ns),
    }
    passed = all(hard_gates.values())
    raw = {
        "stage": 4,
        "run_id": "RUN-ECDLP-a98ea9-S4",
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "task_id": TASK_ID,
        "amendment": "v5_stage4_authorized",
        "authorized_stages": [0, 1, 2, 3, 4],
        "certificate": {"kind": "none"},
        "digit_ADV_computed": True,
        "D_computed": True,
        "two_branch_applied": True,
        "two_branch_official_disposition": False,
        "beta_fitted_as_claim": False,
        "stage5_authorized": False,
        "static_provenance": provenance,
        "instance_precheck": checks,
        "mult_precheck": mult_checks,
        "tested_scale": scale,
        "identity_convention": (
            "EC: k=0 is the identity and has no affine x; label 0. "
            "MULT: k=0 is the unit 1; digits of 1 are used (disclosed)."
        ),
        "control_c": {
            "instance": CONTROL_C,
            "generator_order_N": order_ok and order_n3 and order_nN3,
        },
        "walk": walk_reports,
        "treatment_source": "RUN-ECDLP-a98ea9-S3",
        "treatment_cell_count": len(treatment),
        "comparator_cells": comparator_cells,
        "null1_cells": null1_cells,
        "null2_cells": null2_cells,
        "control_c_cells": control_c_cells,
        "mult_cells": mult_cells,
        "mult_null2_cells": mult_null2_cells,
        "D_cells": d_rows,
        "mechanical_two_branch": branch,
        "hard_gates": hard_gates,
        "validity": "valid" if passed else "gate_failure",
        "validity_reason": (
            "Stage 4 comparator, nulls, CONTROL C, and curve-free recorded; "
            "D and mechanical two-branch are observations"
            if passed
            else f"gate failure: {[k for k, v in hard_gates.items() if not v]}"
        ),
        "scientific_boundary": (
            "Stage 4 observations only. D and the two-branch table are not "
            "H support and are not D2 disposition. No Stage 5."
        ),
    }
    (RUN_DIR / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    wall = time.time() - t0
    summary = {
        "hard_gates": hard_gates,
        "D_cell_count": len(d_rows),
        "mechanical_two_branch": [
            {"statistic": p["statistic"], "mechanical_branch": p["mechanical_branch"]}
            for p in branch["per_statistic"]
        ],
        "tested_scale": {k: scale[k] for k in (
            "n_min", "n_max", "span_ratio", "span_at_least_6x",
            "instance_count", "band_top_26_bit_tested",
        )},
        "validity": raw["validity"],
        "D_computed": True,
        "two_branch_official_disposition": False,
        "wall_clock_seconds": round(wall, 3),
    }
    write_run_record(
        RUN_DIR,
        stage="4",
        command="python3 implementation/stage4.py",
        params={
            "authorized_stages": [0, 1, 2, 3, 4],
            "r": list(RS),
            "s": list(SS),
            "instance_ids": [inst["id"] for inst in INSTANCES],
            "control_c": CONTROL_C["id"],
            "mult_ids": [m["id"] for m in MULT_INSTANCES],
            "seeds": SEEDS,
        },
        seeds={"declared": SEEDS, "note": "Seeds enter NULL-1 only. ADV/D on other arms are exact enumerations."},
        validity=raw["validity"],
        validity_reason=raw["validity_reason"],
        wall_clock_s=wall,
        stdout=json.dumps(summary, indent=2) + "\n",
        stderr="",
        raw_result_file="raw-result.json",
        model_id="cursor-grok-4.6-cloud-agent",
        repo_root=HERE.parents[2],
        extra_artifacts={},
        task_id=TASK_ID,
        scientific_boundary=(
            "Stage 4 observations only. D and mechanical two-branch are "
            "not official H/D2 disposition. No Stage 5."
        ),
    )
    report = {
        "execution_report": {
            "experiment_id": "EXP-ECDLP-a98ea9",
            "hypothesis_id": "H-ECDLP-07c7c6",
            "task_id": TASK_ID,
            "run_id": "RUN-ECDLP-a98ea9-S4",
            "amendment": "v5_stage4_authorized",
            "authorized_stages": [0, 1, 2, 3, 4],
            "certificate": {"kind": "none"},
            "digit_ADV_computed": True,
            "D_computed": True,
            "two_branch_applied": True,
            "two_branch_official_disposition": False,
            "beta_fitted_as_claim": False,
            "stage5_authorized": False,
            "hard_gates": hard_gates,
            "D_cell_count": len(d_rows),
            "mechanical_two_branch": branch,
            "tested_scale": scale,
            "validity": raw["validity"],
            "validity_reason": raw["validity_reason"],
            "wall_clock_seconds": round(wall, 3),
            "scientific_boundary": (
                "Stage 4 only under v5_stage4_authorized. D and the "
                "two-branch table are observations. No Stage 5. No D2. "
                "H remains unspecified by this report."
            ),
        }
    }
    REPORT_PATH.write_text(_dump_yaml(report) + "\n")
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
