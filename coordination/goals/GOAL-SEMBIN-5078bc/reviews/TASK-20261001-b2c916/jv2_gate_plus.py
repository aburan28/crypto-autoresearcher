#!/usr/bin/env python3
"""TASK-20261001-b2c916 / JV-2: a demonstrated repair of C-IMPL-GATE.

Three additional checks, each aimed at one blind spot the wrong drivers in
jv2_wrong_drivers.py exploited. They are written from the amendment's header
block alone and share no code, grid, enumerator or input with the driver:

  (b+) CLOSED FORMS EVERYWHERE. Every cell of the gate's OWN grid (d = 1.0 +
       0.25 k up to n, m 2..16, every model, every v1 budget) -- not d in
       {16, 24, 32} only -- and every returned field: s, TPR, CALLS, PROBE,
       FILL, LA, TOTAL, to 1e-6 bits. Catches off-grid and domain errors.
  (f)  ENUMERATOR COMPLETENESS. The set of (n, model, B, m, d) the driver's
       own sweep() emits equals the gate's independently generated set.
       Catches a driver that checks itself only on cells it chose to visit.
  (g)  INPUT ANCHOR. The N installed for n = 131 equals log2 of an integer r
       parsed from the frozen input by an independent parser (any 38-40 digit
       integer with log2 in (128.5, 129.5)), and r passes a probable-prime test.

Run against: the committed driver (must PASS), its four committed mutants
M1-M4 (must FAIL), and the JV-2 wrong drivers W1, W1b, W2, W3, W4, W5, W6 (must
FAIL). W5's defect lives in run_v2.read_subgroup_order, so for W5 the N handed
to the driver is the one that wrong reader returns.

Usage: python3 jv2_gate_plus.py --work DIR   (DIR = jv2_wrong_drivers.py --work)
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # never write __pycache__ into committed code dirs

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
EXP = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c")
CODE = os.path.join(EXP, "code", "v2")
BAILEY = os.path.join(REPO, "inputs", "BAILEY-2009-541-ECC2K130", "talk-35minutes_text.md")
DIG = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "artifact-digests.json")))
DEGREES = (97, 109, 131, 163, 191, 233, 239, 283, 409, 571)
MODELS = ("FREE", "ENUM", "MITM", "MITM_CAPPED")
BUDGETS = (30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, None)
TOL = 1e-6
LN2 = math.log(2.0)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- independent input parse (g) -------------------------------------------
def independent_r():
    text = open(BAILEY, encoding="utf-8").read()
    nums = [int(x) for x in re.findall(r"\b(\d{38,40})\b", text)]
    cands = sorted({x for x in nums if 128.5 < math.log2(x) < 129.5})
    if len(cands) != 1:
        raise SystemExit(f"independent parse ambiguous: {cands}")
    return cands[0]


def probable_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022, 3, 5, 7, 11, 13):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---- reference (b+) ----------------------------------------------------------
def ref_cell(N, model, m, d, B):
    L = math.lgamma(m + 1.0) / LN2
    S = m // 2 if m % 2 == 0 else (m - 1) // 2
    if model in ("FREE", "ENUM"):
        s = 0
    elif model == "MITM" or B is None:
        s = S
    else:
        s = min(S, int(math.floor(B / d)))
    TPR = N + L - m * d
    CALLS = d + TPR
    o = {"FREE": 0.0, "ENUM": (m - 1) * d}.get(model, (m - s) * d)
    PROBE = d + TPR + o
    FILL = s * d if (model in ("MITM", "MITM_CAPPED") and s >= 1) else 0.0
    LA = 2.0 * d
    top = max(PROBE, FILL, LA)
    TOTAL = top + math.log2(math.fsum(2.0 ** (x - top) for x in (PROBE, FILL, LA)))
    return (s, TPR, CALLS, PROBE, FILL, LA, TOTAL)


def gate_grid(n):
    k = 0
    while True:
        d = 1.0 + 0.25 * k
        if d > n + 1e-9:
            return
        yield d
        k += 1


def gate_plus(drv, log2_r_installed, r_indep):
    res = {}
    # (g)
    g_ok = abs(log2_r_installed - math.log2(r_indep)) < 1e-9 and probable_prime(r_indep)
    res["g_input_anchor"] = {"log2_r_installed": log2_r_installed, "log2_r_independent": math.log2(r_indep),
                             "r_probable_prime": probable_prime(r_indep), "passed": g_ok}
    N131 = math.log2(r_indep)
    # (f)
    expected, seen = set(), set()
    for n in DEGREES:
        for model in MODELS:
            for B in (BUDGETS if model == "MITM_CAPPED" else (None,)):
                for m in range(2, 17):
                    for d in gate_grid(n):
                        expected.add((n, model, B, m, d))
    drv.sweep(DEGREES, range(2, 17), MODELS, lambda n, model, b, m, d, cell: seen.add((n, model, b, m, d)))
    res["f_enumerator"] = {"expected": len(expected), "driver_emitted": len(seen),
                           "missing": len(expected - seen), "extra": len(seen - expected),
                           "passed": expected == seen}
    # (b+)
    worst, viol, cells, ex = 0.0, 0, 0, []
    for (n, model, B, m, d) in sorted(expected, key=lambda t: (t[0], t[1], -1 if t[2] is None else t[2], t[3], t[4])):
        N = N131 if n == 131 else float(n)
        ref = ref_cell(N, model, m, d, B)
        got = drv.evaluate(n, model, m, d, B)
        cells += 1
        dev = max(abs(float(got[i]) - ref[i]) for i in range(7))
        worst = max(worst, dev)
        if dev > TOL:
            viol += 1
            if len(ex) < 3:
                ex.append({"n": n, "model": model, "B": B, "m": m, "d": d,
                           "got": [round(float(x), 6) for x in got[:7]], "ref": [round(x, 6) for x in ref]})
    res["b_plus_all_cells_all_fields"] = {"cells": cells, "violations": viol, "max_abs_dev_bits": worst,
                                          "examples": ex, "passed": viol == 0}
    # (h) baseline column, GATING: VOW = log2(0.886) + N/2 with the independent N; PUB only at 131
    hv = []
    for n in DEGREES:
        N = N131 if n == 131 else float(n)
        want = math.log2(0.886) + N / 2.0
        got = drv.vow_column(n)
        pub_ok = (drv.pub_column(n) is None) == (n != 131)
        if abs(got - want) > 1e-9 or not pub_ok:
            hv.append({"n": n, "VOW_driver": got, "VOW_ref": want, "PUB_placement_ok": pub_ok})
    res["h_baseline_column"] = {"violations": hv, "passed": not hv}
    res["passed"] = all(v["passed"] for v in res.values() if isinstance(v, dict))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("JV2_WORK", "/tmp/jv2_work"))
    a = ap.parse_args()
    r = independent_r()
    raw = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "raw-result.json")))
    committed_log2_r = raw["inputs"]["subgroup_order_131"]["log2_r"]
    targets = [("committed", os.path.join(CODE, "model_v2.py"), committed_log2_r)]
    for mid, f in (("M1", "M1_drop_L_from_TPR.py"), ("M2", "M2_tabulate_floor_m_minus_1_half.py"),
                   ("M3", "M3_swap_time_and_store_halves.py"), ("M4", "M4_ceil_budget_cap.py")):
        targets.append((mid, os.path.join(CODE, "mutants", f), committed_log2_r))
    for wid in ("W1", "W1b", "W2", "W3", "W4", "W5", "W6", "W7"):
        n_in = math.log2(4 * r) if wid == "W5" else committed_log2_r
        targets.append((wid, os.path.join(a.work, wid, "code", "model_v2.py"), n_in))
    for label, path, _ in targets[:5]:
        if hashlib.sha256(open(path, "rb").read()).hexdigest() != DIG["code_v2"][os.path.relpath(path, REPO)]:
            raise SystemExit(f"{label}: hash mismatch")
    out = {"task_id": "TASK-20261001-b2c916", "checks": ["b+", "f", "g", "h"], "results": {}}
    for label, path, n_in in targets:
        drv = load(path, f"gp_{label}")
        drv.set_subgroup_order_log2(n_in)
        res = gate_plus(drv, n_in, r)
        out["results"][label] = res
        print(f"{label:9s} b+={res['b_plus_all_cells_all_fields']['passed']!s:5s} "
              f"(viol {res['b_plus_all_cells_all_fields']['violations']}, max {res['b_plus_all_cells_all_fields']['max_abs_dev_bits']:.3g}) "
              f"f={res['f_enumerator']['passed']!s:5s} (missing {res['f_enumerator']['missing']}) "
              f"g={res['g_input_anchor']['passed']!s:5s} h={res['h_baseline_column']['passed']!s:5s} "
              f"-> {'PASS' if res['passed'] else 'FAIL'}", flush=True)
    out["expected"] = "committed PASS; M1-M4 and W1-W6 FAIL"
    out["as_expected"] = (out["results"]["committed"]["passed"]
                          and not any(out["results"][k]["passed"] for k in out["results"] if k != "committed"))
    with open(os.path.join(HERE, "jv2_out", "jv2_gate_plus.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1, default=str) + "\n")
    print("as expected:", out["as_expected"])


if __name__ == "__main__":
    main()
