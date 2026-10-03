#!/usr/bin/env python3
"""TASK-20261001-b2c916 -- PROVES-TOO-MUCH control of REVIEW-SEMBIN-20261001-04ec3c-v2,
run on the v2 accounting (AMD-20261001-e61f2b), construction charge included.

Objects where the conclusion "no index-calculus cell beats rho" is KNOWN FALSE:
  A. genus-g hyperelliptic Jacobian over F_q, q = 2^b, N = g*b
     (g >= 5 at n ~ 160; g >= 4 at n ~ 256; g = 2, 3 shown as contrast);
  B. F_q^*, q a safe prime of n bits, N = n - 1, n in {131, 256, 512, 1024}.

For each object, two oracle families are run through the SAME v2 accounting:
  (i)  REAL ORACLE(S) -- the object's own decomposition map, with every table it
       uses charged at one operation per entry (FILL), exactly as C-1 charges the
       MITM s-sum table:
         Jacobian: factor the Mumford u-polynomial (Harley/Gaudry), o = log2(g^2 b^2)
                   per trial; FB hash table FILL = d;
         F_q^*:    (a) trial division, o = d, FILL = beta (sieve of Eratosthenes);
                   (b) batch smoothness (product/remainder tree), o = log2(n^2)
                       amortised, FILL = d + log2(d) (the product tree).
       Declared failure signature: these MUST still find sub-rho cells.
  (ii) GENERIC ORACLES -- ENUM, MITM, MITM_CAPPED at every v1 budget, evaluated by
       the COMMITTED model_v2.evaluate itself (hash-checked) at a degree label
       whose N is the object's N; d capped at the object's factor-base bound and,
       separately, uncapped. Declared failure signature: these MUST find none.

The v2 accounting is transcribed once (v2_cell) for the real oracles, whose
oracle exponent and FILL are not v2 oracle laws; the transcription is verified
against model_v2.evaluate on every v2 oracle law before use.

Reuses Dickman-rho and pi_approx from TASK-20260928-3f90b8/ptm_known_false_objects.py
(previous-round script; sha256-pinned import, its main() is not run).

Usage: python3 ptm_v2.py
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # never write __pycache__ into committed code dirs

import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
EXP = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c")
DRV = os.path.join(EXP, "code", "v2", "model_v2.py")
DIG = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "artifact-digests.json")))
PREV = os.path.join(REPO, "coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20260928-3f90b8/ptm_known_false_objects.py")
PREV_SHA = "68852843d12e73bb7b9a14d9c3c85b3dbacb80d97e3188da8ad171988f37e0c3"
LOG2_0886 = math.log2(0.886)


def load(path, name, want):
    if hashlib.sha256(open(path, "rb").read()).hexdigest() != want:
        raise SystemExit(f"{path}: sha256 mismatch; refusing")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def log2_sum(xs):
    top = max(xs)
    return top + math.log2(math.fsum(2.0 ** (x - top) for x in xs))


def v2_cell(d, tpr, o, fill):
    """The v2 header block: K = d, CALLS = K + TPR, PROBE = K + TPR + o,
    LA = 2d, TOTAL = log2(2^PROBE + 2^FILL + 2^LA)."""
    K = d
    CALLS = K + tpr
    PROBE = K + tpr + o
    LA = 2.0 * d
    return {"CALLS": CALLS, "PROBE": PROBE, "FILL": fill, "LA": LA, "TOTAL": log2_sum((PROBE, fill, LA))}


def verify_transcription(drv):
    worst = 0.0
    for n in (97, 163, 571):
        N = drv.log2_N(n)
        for m in range(2, 17):
            L = drv.log2_m_factorial(m)
            for d in (3.0, 12.25, 20.5, 33.75):
                for model in drv.MODELS:
                    for B in drv.budgets_for(model):
                        c = drv.evaluate(n, model, m, d, B)
                        s = c[0]
                        o = {"FREE": 0.0, "ENUM": (m - 1) * d}.get(model, (m - s) * d)
                        fill = s * d if (model in ("MITM", "MITM_CAPPED") and s >= 1) else 0.0
                        t = v2_cell(d, N + L - m * d, o, fill)
                        worst = max(worst, abs(t["TOTAL"] - c[6]), abs(t["CALLS"] - c[2]), abs(t["PROBE"] - c[3]))
    return worst


def generic_sweep(drv, label_n, N, d_cap):
    """Committed model_v2.sweep over PRIMARY_MODELS at degree label_n (log2_N(label_n) == N),
    d in 1.0..d_cap step 0.25; C-2 guard; sub-rho vs VOW(N); C-3 flag; analytic floor."""
    assert abs(drv.log2_N(label_n) - N) < 1e-12 and label_n != 131
    vow = LOG2_0886 + N / 2.0
    st = {"cells": 0, "in_domain": 0, "subrho_vs_VOW": 0, "C3_fires_in_domain": 0, "C3_fires_any": 0,
          "min_TOTAL_in_domain": None, "argmin": None, "min_floor_slack_bits": None}

    def visit(n, model, b, m, d, cell):
        st["cells"] += 1
        T = cell[6]
        if T < N / 2.0 - 2.0:
            st["C3_fires_any"] += 1
        floor = (N + drv.log2_m_factorial(m) + d) / 2.0 if model != "ENUM" else (N + drv.log2_m_factorial(m)) / 2.0
        if cell[2] < 0.0:
            return
        st["in_domain"] += 1
        slack = T - floor
        if st["min_floor_slack_bits"] is None or slack < st["min_floor_slack_bits"]:
            st["min_floor_slack_bits"] = slack
        if T < vow:
            st["subrho_vs_VOW"] += 1
        if T < N / 2.0 - 2.0:
            st["C3_fires_in_domain"] += 1
        if st["min_TOTAL_in_domain"] is None or T < st["min_TOTAL_in_domain"]:
            st["min_TOTAL_in_domain"] = T
            st["argmin"] = {"model": model, "B": b, "m": m, "d": d, "s": cell[0]}

    drv.sweep((label_n,), range(2, 17), drv.PRIMARY_MODELS, visit, bound_of=lambda _n: float(d_cap))
    st["VOW"] = vow
    st["margin_vs_VOW"] = st["min_TOTAL_in_domain"] - vow
    st["min_TOTAL_in_domain"] = round(st["min_TOTAL_in_domain"], 4)
    st["margin_vs_VOW"] = round(st["margin_vs_VOW"], 4)
    return st


def grid(lo, hi, step=0.25):
    k = 0
    while True:
        x = lo + k * step
        if x > hi + 1e-9:
            return
        yield x
        k += 1


def real_sweep(N, cells):
    """cells: iterable of (params, d, tpr, o, fill). Returns the min and the sub-rho count."""
    vow = LOG2_0886 + N / 2.0
    best, n_in, n_sub, n_c3 = None, 0, 0, 0
    for params, d, tpr, o, fill in cells:
        c = v2_cell(d, tpr, o, fill)
        if c["CALLS"] < 0.0:
            continue
        n_in += 1
        if c["TOTAL"] < vow:
            n_sub += 1
        if c["TOTAL"] < N / 2.0 - 2.0:
            n_c3 += 1
        if best is None or c["TOTAL"] < best[0]:
            best = (c["TOTAL"], {**params, "d": round(d, 4), **{k: round(v, 3) for k, v in c.items()}})
    return {"VOW": round(vow, 4), "cells_in_domain": n_in, "subrho_vs_VOW": n_sub,
            "C3_would_fire_if_this_were_a_generic_model": n_c3,
            "min_TOTAL": round(best[0], 4), "margin_vs_VOW": round(best[0] - vow, 4), "argmin": best[1]}


def jacobian(drv, g, b):
    N = float(g * b)
    L = math.log2(math.factorial(g))
    o = math.log2(g * g * b * b)
    out = {"object": f"genus-{g} hyperelliptic Jacobian over F_2^{b}", "g": g, "b": b, "N": N,
           "p_model": "|F|^g/(g! q^g) (GTTD Sec. 4, retrieved by TASK-20260928-3f90b8): the contract's p with m = g"}
    for label, fill_of in (("REAL_factor_u__FB_table_charged", lambda d: d),
                           ("REAL_factor_u__v2_literal_FILL_0", lambda d: 0.0)):
        out[label] = real_sweep(N, (({"m": g}, d, N + L - g * d, o, fill_of(d)) for d in grid(1.0, b)))
    out["GENERIC_v2_driver__d_le_b"] = generic_sweep(drv, g * b, N, b)
    out["GENERIC_v2_driver__d_le_n"] = generic_sweep(drv, g * b, N, g * b)
    return out


def fq_star(drv, dk, prev, n):
    N = float(n - 1)
    ta, bs, sv = [], [], []
    for beta in grid(4.0, min(n, 200)):
        u = n / beta
        if u > 95.0:
            continue
        d = math.log2(prev.pi_approx(2.0 ** beta))
        tpr = -dk.log2(u)
        params = {"beta": beta, "u": round(u, 3)}
        ta.append((params, d, tpr, d, beta))
        bs.append((params, d, tpr, math.log2(n * n), d + math.log2(d)))
        # stress variant: a table with ONE ENTRY PER CANDIDATE (sieve-array shape),
        # charged at one op per entry plus ln ln B updates per entry; o = 0.
        sv.append((params, d, tpr, 0.0, d + tpr + math.log2(max(math.log(beta * math.log(2.0)), 1.0))))
    return {"object": f"F_q^*, q a safe prime of {n} bits", "n": n, "N": N,
            "p_model": "rho(u), u = n / beta (Dickman), |F| = pi(2^beta)",
            "REAL_trial_division__sieve_charged": real_sweep(N, ta),
            "REAL_batch_smoothness__product_tree_charged": real_sweep(N, bs),
            "STRESS_per_candidate_table__charged_one_op_per_entry": real_sweep(N, sv),
            "STRESS_note": ("accounting stress test, not an algorithm: random representatives g^a h^b are not "
                            "sieveable; the variant asks only whether charging a table that grows with the "
                            "candidate count removes the win"),
            "GENERIC_v2_driver__d_le_N": generic_sweep(drv, n - 1, N, n - 1),
            "L_q_half_sqrt2_log2_reference_recalled": round(
                math.log2(math.exp(math.sqrt(2.0 * n * math.log(2) * math.log(n * math.log(2))))), 2)}


def harley(g, b1=40, b2=80):
    """v2 real-oracle accounting with o = 0 (FREE-like) and FB table charged: exponent in q."""
    def m_(b):
        N = float(g * b)
        L = math.log2(math.factorial(g))
        return min(v2_cell(d, N + L - g * d, 0.0, d)["TOTAL"] for d in grid(1.0, b, 0.01))
    return {"g": g, "measured_exponent_in_q": round((m_(b2) - m_(b1)) / (b2 - b1), 4),
            "Harley_2_minus_2_over_g_plus_1": round(2 - 2 / (g + 1), 4), "rho_g_over_2": g / 2}


def main():
    drv = load(DRV, "model_v2_committed", DIG["code_v2"][os.path.relpath(DRV, REPO)])
    raw = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "raw-result.json")))
    drv.set_subgroup_order_log2(raw["inputs"]["subgroup_order_131"]["log2_r"])
    prev = load(PREV, "ptm_prev_round", PREV_SHA)
    dk = prev.Dickman()
    out = {"task_id": "TASK-20261001-b2c916", "control": "proves_too_much (REVIEW-SEMBIN-20261001-04ec3c-v2)",
           "snapshot": "b8019a6fb", "driver_sha256": DIG["code_v2"][os.path.relpath(DRV, REPO)],
           "transcription_max_abs_error_bits": verify_transcription(drv),
           "dickman_spot": {"rho(2)": dk.rho(2.0), "1-ln2": 1 - math.log(2), "rho(10)": dk.rho(10.0)},
           "jacobian": [], "fq_star": [], "harley_exponent_check": []}
    print("transcription error", out["transcription_max_abs_error_bits"], flush=True)
    for g, b in ((2, 80), (3, 53), (5, 32), (6, 27), (8, 20), (4, 64), (5, 51), (8, 32)):
        j = jacobian(drv, g, b)
        out["jacobian"].append(j)
        r, gb, gn = j["REAL_factor_u__FB_table_charged"], j["GENERIC_v2_driver__d_le_b"], j["GENERIC_v2_driver__d_le_n"]
        print(f"JAC g={g} b={b} N={j['N']:.0f} VOW={r['VOW']:.2f} | REAL min {r['min_TOTAL']:.2f} "
              f"({r['margin_vs_VOW']:+.2f}) subrho={r['subrho_vs_VOW']} | GENERIC d<=b min {gb['min_TOTAL_in_domain']} "
              f"({gb['margin_vs_VOW']:+.2f}) subrho={gb['subrho_vs_VOW']} C3={gb['C3_fires_any']} floorslack={gb['min_floor_slack_bits']:.3f} "
              f"| d<=n min {gn['min_TOTAL_in_domain']} subrho={gn['subrho_vs_VOW']} C3={gn['C3_fires_any']}", flush=True)
    for n in (131, 256, 512, 1024):
        f = fq_star(drv, dk, prev, n)
        out["fq_star"].append(f)
        a, bsm, gg = (f["REAL_trial_division__sieve_charged"], f["REAL_batch_smoothness__product_tree_charged"],
                      f["GENERIC_v2_driver__d_le_N"])
        print(f"FQ* n={n} VOW={a['VOW']:.2f} | TD min {a['min_TOTAL']:.2f} ({a['margin_vs_VOW']:+.2f}) subrho={a['subrho_vs_VOW']} "
              f"| BATCH min {bsm['min_TOTAL']:.2f} ({bsm['margin_vs_VOW']:+.2f}) subrho={bsm['subrho_vs_VOW']} "
              f"| GENERIC min {gg['min_TOTAL_in_domain']} ({gg['margin_vs_VOW']:+.2f}) subrho={gg['subrho_vs_VOW']} "
              f"C3={gg['C3_fires_any']} floorslack={gg['min_floor_slack_bits']:.3f}", flush=True)
    for g in (3, 4, 5, 8):
        h = harley(g)
        out["harley_exponent_check"].append(h)
        print("HARLEY", h, flush=True)
    real_ok = all(j["REAL_factor_u__FB_table_charged"]["subrho_vs_VOW"] > 0
                  for j in out["jacobian"] if (j["g"] >= 5 and j["N"] <= 170) or (j["g"] >= 4 and j["N"] >= 250)) and \
        all(f[k]["subrho_vs_VOW"] > 0 for f in out["fq_star"]
            for k in ("REAL_trial_division__sieve_charged", "REAL_batch_smoothness__product_tree_charged"))
    gen_none = all(j[k]["subrho_vs_VOW"] == 0 and j[k]["C3_fires_any"] == 0 for j in out["jacobian"]
                   for k in ("GENERIC_v2_driver__d_le_b", "GENERIC_v2_driver__d_le_n")) and \
        all(f["GENERIC_v2_driver__d_le_N"]["subrho_vs_VOW"] == 0 and f["GENERIC_v2_driver__d_le_N"]["C3_fires_any"] == 0
            for f in out["fq_star"])
    out["failure_signature"] = {
        "real_oracle_still_finds_subrho_on_every_required_object": real_ok,
        "generic_oracles_find_none_and_C3_silent": gen_none,
        "signature_fired": (not real_ok) or (not gen_none)}
    print(json.dumps(out["failure_signature"], indent=1))
    with open(os.path.join(HERE, "ptm_out", "ptm_v2_results.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "ptm_out"), exist_ok=True)
    main()
