#!/usr/bin/env python3
"""EXP-SEMBIN-04ec3c protocol version 2 run (AMD-20261001-e61f2b), executed under
TASK-20261001-c2a58e.

Order of operations, which IS the stopping discipline:
  1. Read r (ECC2K-130 prime subgroup order) from the frozen input.
  2. Verify the committed mutant sources equal a fresh regeneration.
  3. C-IMPL-GATE (a)-(d) over the unmutated driver and mutants M1-M4; (e) gate
     power. Write gate/gate_report.json. ANY FAILURE -> STOP: no data pass, no row.
  4. Data pass over the unmutated driver. Generic-lower-bound flag (C-3) is
     evaluated FIRST; if it fires -> STOP: arithmetic defect, no row written.
  5. Only then: rows, controls, A6, C-BOUND-PROBE, C-BASELINE-CONSISTENCY, A4
     null, the probe-only v1 reference column, E-1..E-4 side by side, and the
     segregated exploratory block X-1..X-8.

Exit codes: 0 completed; 3 stopped by C-IMPL-GATE; 4 stopped by the C-3 flag;
2 input/implementation precondition failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gate_v2 as G          # noqa: E402
import make_mutants as MM    # noqa: E402
import exploratory_v2 as X   # noqa: E402

I_S, I_TPR, I_CALLS, I_PROBE, I_FILL, I_LA, I_TOTAL, I_TABLE = range(8)

# AMD-20261001-e61f2b expectations_post_data E-2 (reviewer-derived; NOT targets)
E2_STORE_FREE_MARGIN_VS_VOW = {97: 16.54, 109: 17.69, 131: 19.12, 163: 21.55,
                               191: 23.55, 233: 26.22, 239: 26.55, 283: 29.00,
                               409: 35.49, 571: 42.70}
E2_131_DETAIL = {"min_total_log2": 83.44, "m": 8, "s": 4, "d_about": 20.55,
                 "margin_vs_PUB_bits_about": 22.6}
COMMITTED_FLOOR = {2: 89.25, 3: 68.58, 4: 56.40, 5: 48.44, 6: 42.85, 8: 35.61}
M3_MEASURED_BASE = 132.58


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def bkey(b):
    return "unlimited" if b is None else f"{int(b)}"


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------
def _miller_rabin(n: int, bases) -> bool:
    if n < 2:
        return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def read_subgroup_order(path):
    text = open(path, encoding="utf-8").read()
    found = re.findall(r"has 4\S*points, where \S*is the prime\s*\n\s*(\d{30,})", text)
    if not found:
        raise SystemExit(f"could not locate the subgroup order in {path}")
    vals = sorted(set(int(v) for v in found))
    if len(vals) != 1:
        raise SystemExit(f"inconsistent subgroup orders in {path}: {vals}")
    r = vals[0]
    bases = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
    return {"r": r, "occurrences": len(found), "log2_r": math.log2(r),
            "bit_length": r.bit_length(), "log2_4r": math.log2(4 * r),
            "miller_rabin_fixed_bases_16_pass": _miller_rabin(r, bases),
            "primality_note": "Miller-Rabin with the first 16 prime bases; a probable-prime sanity check, not a proof"}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# gate
# --------------------------------------------------------------------------
def run_gate_on(drv, log2_r, degrees, label):
    t0 = time.time()
    checks = G.SweepChecks(log2_r)
    drv.sweep(degrees, range(2, 17), drv.MODELS, checks.observe)
    ra = checks.result_a()
    rc = checks.result_c()
    rb = G.check_b(drv, log2_r)
    rd = G.check_d(drv, checks, degrees)
    passed = ra["passed"] and rb["passed"] and rc["passed"] and rd["passed"]
    log(f"gate {label}: a={ra['passed']} b={rb['passed']} c={rc['passed']} d={rd['passed']} "
        f"({time.time() - t0:.1f}s)")
    return {"driver": label, "a_yield_identity": ra, "b_closed_forms": rb,
            "c_budget_invariant": rc, "d_m_bound_probe": rd,
            "gate_passed": passed,
            "failed_checks": [k for k, v in (("a", ra), ("b", rb), ("c", rc), ("d", rd))
                              if not v["passed"]],
            "seconds": round(time.time() - t0, 3)}


# --------------------------------------------------------------------------
# data pass
# --------------------------------------------------------------------------
class DataPass:
    def __init__(self, drv):
        self.drv = drv
        self.counts = {}
        self.flag = {"threshold_rule": "TOTAL < N/2 - 2.0 on any ENUM, MITM or MITM_CAPPED cell",
                     "cells_checked": 0, "fired_in_domain": 0, "fired_out_of_domain": 0,
                     "min_slack_bits_by_degree": {}, "examples": []}
        self.argmin = {}
        self.step3 = {}

    def visit(self, n, model, b, m, d, cell):
        drv = self.drv
        N = drv.log2_N(n)
        vow = drv.vow_column(n)
        pub = drv.pub_column(n)
        ood = cell[I_CALLS] < 0.0
        T = cell[I_TOTAL]
        if model in drv.PRIMARY_MODELS:
            thr = N / 2.0 - 2.0
            self.flag["cells_checked"] += 1
            slack = T - thr
            cur = self.flag["min_slack_bits_by_degree"].get(n)
            if cur is None or slack < cur:
                self.flag["min_slack_bits_by_degree"][n] = slack
            if T < thr:
                self.flag["fired_out_of_domain" if ood else "fired_in_domain"] += 1
                if len(self.flag["examples"]) < 5:
                    self.flag["examples"].append({"n": n, "model": model, "B": bkey(b),
                                                  "m": m, "d": d})
        bounds = ("n", "n/2") if d <= n / 2.0 + 1e-9 else ("n",)
        for bd in bounds:
            ck = (n, model, bkey(b), bd)
            c = self.counts.get(ck)
            if c is None:
                c = self.counts[ck] = {"cells": 0, "in_domain": 0, "out_of_domain": 0,
                                       "subrho_vs_VOW": 0, "subrho_vs_PUB": 0 if pub is not None else None}
            c["cells"] += 1
            if ood:
                c["out_of_domain"] += 1
                continue
            c["in_domain"] += 1
            if T < vow:
                c["subrho_vs_VOW"] += 1
            if pub is not None and T < pub:
                c["subrho_vs_PUB"] += 1
            ak = (n, model, bkey(b), m, bd)
            cur = self.argmin.get(ak)
            if cur is None or T < cur[0]:
                self.argmin[ak] = (T, d, cell)
            if model in ("MITM", "MITM_CAPPED"):
                sk = (n, m, bd)
                st = self.step3.get(sk)
                if st is None:
                    st = self.step3[sk] = {"min_total": None, "min_store_subrho_VOW": None,
                                           "min_store_subrho_PUB": None}
                store = cell[I_TABLE] if cell[I_TABLE] is not None else 0.0
                if st["min_total"] is None or T < st["min_total"]["TOTAL"]:
                    st["min_total"] = {"TOTAL": T, "model": model, "B": bkey(b), "d": d,
                                       "s": cell[I_S], "log2_table_entries": cell[I_TABLE]}
                if T < vow and (st["min_store_subrho_VOW"] is None
                                or store < st["min_store_subrho_VOW"]["log2_table_entries"]):
                    st["min_store_subrho_VOW"] = {"TOTAL": T, "model": model, "B": bkey(b),
                                                  "d": d, "s": cell[I_S],
                                                  "log2_table_entries": store}
                if pub is not None and T < pub and (st["min_store_subrho_PUB"] is None
                                                    or store < st["min_store_subrho_PUB"]["log2_table_entries"]):
                    st["min_store_subrho_PUB"] = {"TOTAL": T, "model": model, "B": bkey(b),
                                                  "d": d, "s": cell[I_S],
                                                  "log2_table_entries": store}


def step4_continuous(drv, n, m, target, bound, d_step=0.05):
    """A6 step 4: continuous store x = s*d in [0, S*d], minimum x with TOTAL < target."""
    N = drv.log2_N(n)
    L = drv.log2_m_factorial(m)
    S = m // 2
    best = None
    k = 0
    while True:
        d = 1.0 + k * d_step
        k += 1
        if d > bound + 1e-9:
            break
        if d + N + L - m * d < 0.0:          # C-2 domain guard
            continue
        LA = 2.0 * d
        if LA >= target:
            continue
        A = N + L + d                         # PROBE + x
        r = 1.0 - 2.0 ** (LA - target)
        lq = A - 2.0 * target                 # log2 of q = 2^A / 2^(2T)
        if lq > 2.0 * math.log2(r) - 2.0:     # r^2 < 4q: no real root, infeasible
            continue
        q = 2.0 ** lq
        disc = math.sqrt(max(r * r - 4.0 * q, 0.0))
        x_lo = (A - target) + 1.0 - math.log2(r + disc)
        x_hi = target + math.log2((r + disc) / 2.0)
        x_min = max(x_lo, 0.0)
        if x_min > min(x_hi, S * d):
            continue
        if best is None or x_min < best["log2_store_infimum"]:
            best = {"log2_store_infimum": x_min, "d": round(d, 4), "s_continuous": x_min / d}
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--bailey", default="inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md")
    ap.add_argument("--v1-raw", default="experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json")
    ap.add_argument("--smoke-degrees", default=None,
                    help="DEVELOPMENT ONLY: comma list of NON-protocol degrees; never used for the run")
    a = ap.parse_args()

    os.makedirs(os.path.join(a.run_dir, "gate", "mutants"), exist_ok=True)
    result = {"experiment_id": "EXP-SEMBIN-04ec3c", "protocol_version": 2,
              "amendment": "AMD-20261001-e61f2b", "approval_decision": "DEC-20261001-5c9e7a",
              "handoff": "TASK-20261001-c2a58e", "hypothesis_id": "H-SEMBIN-8e7ae3",
              "confirmatory_status": "exploratory_only (post-data amendment)",
              "wording": "the oracle table's construction is charged as operations, one per entry; memory is reported, not charged",
              "halted": None}

    def write_raw():
        with open(os.path.join(a.run_dir, "raw-result.json"), "w") as fh:
            fh.write(json.dumps(result, indent=1) + "\n")

    # 1. inputs
    inp = read_subgroup_order(a.bailey)
    log(f"r read from frozen input: {inp['bit_length']} bits, log2 r = {inp['log2_r']:.6f}, "
        f"{inp['occurrences']} occurrences, MR={inp['miller_rabin_fixed_bases_16_pass']}")
    result["inputs"] = {"subgroup_order_131": {**inp, "r": str(inp["r"]), "source": a.bailey}}
    log2_r = inp["log2_r"]

    drv = load_module(os.path.join(HERE, "model_v2.py"), "model_v2_unmutated")
    drv.set_subgroup_order_log2(log2_r)
    if a.smoke_degrees:
        degs = tuple(int(x) for x in a.smoke_degrees.split(","))
        if set(degs) & set(drv.DEGREES) or 131 in degs:
            raise SystemExit("smoke degrees must not be protocol degrees")
        drv.DEGREES = degs
        G.GATE_DEGREES = degs
        result["SMOKE_TEST_NOT_A_RUN"] = True
    degrees = drv.DEGREES
    result["parameters"] = {"degrees": list(degrees), "m_range": [2, 16], "d_grid": "1.0 .. bound step 0.25 (v1)",
                            "d_bounds": ["n", "n/2"], "budgets_log2_entries": [bkey(b) for b in drv.BUDGETS],
                            "models": list(drv.MODELS), "primary_models": list(drv.PRIMARY_MODELS),
                            "LA_exponent": drv.LA_EXPONENT, "vow_const_log2": drv.LOG2_VOW_CONST,
                            "PUB_131": drv.PUB_131, "N_rule": "log2 r at n = 131, n elsewhere"}

    # 2. mutants
    built = MM.build_all()
    mismatch = []
    for mid, text in built.items():
        p = os.path.join(MM.MUTANT_DIR, MM.MUTATIONS[mid]["file"])
        if not os.path.exists(p) or open(p, encoding="utf-8").read() != text:
            mismatch.append(mid)
    if mismatch:
        result["halted"] = {"by": "precondition", "reason": f"mutant sources differ from regeneration: {mismatch}"}
        write_raw()
        return 2
    mutants = {}
    for mid in sorted(built):
        src = os.path.join(MM.MUTANT_DIR, MM.MUTATIONS[mid]["file"])
        shutil.copyfile(src, os.path.join(a.run_dir, "gate", "mutants", MM.MUTATIONS[mid]["file"]))
        mod = load_module(src, f"mutant_{mid}")
        mod.set_subgroup_order_log2(log2_r)
        if a.smoke_degrees:
            mod.DEGREES = degrees
        mutants[mid] = mod

    # 3. gate
    log("C-IMPL-GATE: unmutated driver")
    g0 = run_gate_on(drv, log2_r, degrees, "v2-unmutated")
    gm = {}
    for mid, mod in mutants.items():
        log(f"C-IMPL-GATE: mutant {mid} ({MM.MUTATIONS[mid]['what']})")
        gm[mid] = run_gate_on(mod, log2_r, degrees, mid)
        gm[mid]["mutation"] = MM.MUTATIONS[mid]["what"]
        gm[mid]["source"] = f"gate/mutants/{MM.MUTATIONS[mid]['file']}"
        with open(os.path.join(a.run_dir, "gate", "mutants", f"{mid}_gate_output.json"), "w") as fh:
            fh.write(json.dumps(gm[mid], indent=1) + "\n")
    e_pass = g0["gate_passed"] and all(not v["gate_passed"] for v in gm.values())
    gate_report = {
        "control": "C-IMPL-GATE (AMD-20261001-e61f2b C-4), stopping",
        "unmutated": g0,
        "mutants": {mid: {"mutation": v["mutation"], "gate_passed": v["gate_passed"],
                          "failed_checks": v["failed_checks"], "source": v["source"],
                          "output": f"gate/mutants/{mid}_gate_output.json"}
                    for mid, v in gm.items()},
        "e_gate_power_self_test": {
            "unmutated_passes": g0["gate_passed"],
            "every_mutant_fails": all(not v["gate_passed"] for v in gm.values()),
            "mutants_passing": [mid for mid, v in gm.items() if v["gate_passed"]],
            "passed": e_pass},
        "gate_passed": bool(e_pass),
        "operationalisation_notes": [
            "(a) falling factorial via log1p, m! via lgamma; pure three-lgamma form cross-checked for d <= 24 (precision)",
            "(d) pass criterion = every argmin at m = 16 probed to m = 24 and re-evaluation consistent; moving argmins labelled bound-tracking"],
    }
    with open(os.path.join(a.run_dir, "gate", "gate_report.json"), "w") as fh:
        fh.write(json.dumps(gate_report, indent=1) + "\n")
    result["gate"] = {"report": "gate/gate_report.json", "gate_passed": bool(e_pass),
                      "unmutated_failed_checks": g0["failed_checks"],
                      "mutant_failed_checks": {mid: v["failed_checks"] for mid, v in gm.items()}}
    if not e_pass:
        result["halted"] = {"by": "C-IMPL-GATE", "reason": "gate failed (see gate/gate_report.json); no row computed or read"}
        write_raw()
        log("STOP: C-IMPL-GATE failed")
        return 3
    log("C-IMPL-GATE passed; mutants all failed")

    # 4. data pass + generic-lower-bound flag (stopping)
    log("data pass")
    dp = DataPass(drv)
    drv.sweep(degrees, range(2, 17), drv.MODELS, dp.visit)
    fired = dp.flag["fired_in_domain"] + dp.flag["fired_out_of_domain"]
    dp.flag["fired"] = fired > 0
    dp.flag["thresholds_by_degree"] = {str(n): drv.log2_N(n) / 2.0 - 2.0 for n in degrees}
    dp.flag["min_slack_bits_by_degree"] = {str(k): v for k, v in dp.flag["min_slack_bits_by_degree"].items()}
    result["generic_lower_bound_flag"] = dp.flag
    if fired:
        result["halted"] = {"by": "C-3 generic-lower-bound flag", "reason": "ARITHMETIC DEFECT; no row written"}
        write_raw()
        log("STOP: generic-lower-bound flag fired")
        return 4
    log("generic-lower-bound flag did not fire")

    # 5. rows and controls
    v1 = json.load(open(a.v1_raw))
    v1_idx = {}
    for r in v1.get("mitm_store_free", []):
        v1_idx[(r["n"], "MITM", "unlimited", r["m"])] = r
        v1_idx[(r["n"], "MITM_CAPPED", "unlimited", r["m"])] = r
    for r in v1.get("mitm_capped", []):
        v1_idx[(r["n"], "MITM_CAPPED", bkey(r["budget_log2_entries"]), r["m"])] = r

    rows = []
    for (n, model, bk, m, bd), (T, d, cell) in sorted(
            dp.argmin.items(), key=lambda kv: (kv[0][0], drv.MODELS.index(kv[0][1]),
                                               999 if kv[0][2] == "unlimited" else int(kv[0][2]),
                                               kv[0][3], kv[0][4])):
        vow = drv.vow_column(n)
        pub = drv.pub_column(n)
        bound = float(n) if bd == "n" else n / 2.0
        v1r = v1_idx.get((n, model, bk, m)) if bd == "n" else None
        N = drv.log2_N(n)
        rows.append({
            "n": n, "model": model, "B": bk, "m": m, "d_bound": bd,
            "d": d, "s": cell[I_S], "TPR": cell[I_TPR], "CALLS": cell[I_CALLS],
            "PROBE": cell[I_PROBE], "FILL": cell[I_FILL], "LA": cell[I_LA], "TOTAL": T,
            "log2_table_entries": cell[I_TABLE], "log2_matrix_entries": d + math.log2(m),
            "VOW": vow, "margin_vs_VOW_bits": T - vow,
            "PUB": pub, "margin_vs_PUB_bits": None if pub is None else T - pub,
            "subrho_vs_VOW": T < vow, "subrho_vs_PUB": None if pub is None else T < pub,
            "at_d_lower_bound": d == 1.0, "at_d_upper_bound": abs(d - bound) < 1e-9,
            "at_domain_edge": (cell[I_CALLS] - (m - 1) * 0.25) < 0.0,
            "degenerate": (N / m < 2.0) or (m > n) or (d < 1.0),
            "probe_only_v1_reference_NOT_A_COST": None if v1r is None else {
                "label": "probe-only v1 reference, not a cost (RUN-SEMBIN-c68773, evidence-inadmissible)",
                "v1_log2_total": v1r["log2_total"], "v1_d": v1r["d"]},
        })
    result["argmin_rows"] = rows
    primary_rows_n = [r for r in rows if r["d_bound"] == "n" and r["model"] in drv.PRIMARY_MODELS]

    # counts
    counts = []
    for (n, model, bk, bd), c in sorted(dp.counts.items(), key=lambda kv: (kv[0][0], drv.MODELS.index(kv[0][1]),
                                                                          999 if kv[0][2] == "unlimited" else int(kv[0][2]), kv[0][3])):
        counts.append({"n": n, "model": model, "B": bk, "d_bound": bd, **c,
                       "primary": model in drv.PRIMARY_MODELS})
    result["cell_counts"] = counts
    prim_n = [c for c in counts if c["primary"] and c["d_bound"] == "n"]
    result["primary_subrho_totals"] = {
        "cells_in_domain": sum(c["in_domain"] for c in prim_n),
        "cells_out_of_domain": sum(c["out_of_domain"] for c in prim_n),
        "subrho_vs_VOW": sum(c["subrho_vs_VOW"] for c in prim_n),
        "subrho_vs_PUB_at_131": sum(c["subrho_vs_PUB"] or 0 for c in prim_n if c["n"] == 131),
        "argmin_rows_subrho_vs_VOW": sum(1 for r in primary_rows_n if r["subrho_vs_VOW"]),
        "argmin_rows_subrho_vs_PUB_at_131": sum(1 for r in primary_rows_n if r["subrho_vs_PUB"]),
    }
    ood = {}
    for c in counts:
        if c["d_bound"] != "n":
            continue
        k = f"{c['n']}|{c['model']}"
        ood[k] = ood.get(k, 0) + c["out_of_domain"]
    result["out_of_domain_counts_by_degree_model"] = ood

    # per-degree minimum construction-charged TOTAL
    per_degree = {}
    for n in degrees:
        for bd in ("n", "n/2"):
            prim = [r for r in rows if r["n"] == n and r["d_bound"] == bd and r["model"] in drv.PRIMARY_MODELS]
            sf = [r for r in prim if r["model"] == "MITM"]
            best = min(prim, key=lambda r: r["TOTAL"])
            bsf = min(sf, key=lambda r: r["TOTAL"])
            ent = {"primary_min": {k: best[k] for k in ("model", "B", "m", "d", "s", "TOTAL",
                                                        "margin_vs_VOW_bits", "margin_vs_PUB_bits",
                                                        "log2_table_entries", "at_domain_edge")},
                   "store_free_min_MITM": {k: bsf[k] for k in ("m", "d", "s", "TOTAL", "margin_vs_VOW_bits",
                                                              "margin_vs_PUB_bits", "log2_table_entries",
                                                              "at_domain_edge")}}
            if bd == "n":
                e2 = E2_STORE_FREE_MARGIN_VS_VOW.get(n)
                ent["E2_expectation_margin_vs_VOW"] = e2
                if e2 is not None:
                    diff = bsf["margin_vs_VOW_bits"] - e2
                    ent["v2_minus_E2_bits"] = diff
                    ent["differs_from_E2_by_more_than_0_1_bit"] = abs(diff) > 0.1
                ent["per_budget_min"] = {}
                for bk in [bkey(b) for b in drv.BUDGETS]:
                    rr = [r for r in prim if r["model"] == "MITM_CAPPED" and r["B"] == bk]
                    bb = min(rr, key=lambda r: r["TOTAL"])
                    ent["per_budget_min"][bk] = {k: bb[k] for k in ("m", "d", "s", "TOTAL", "margin_vs_VOW_bits",
                                                                   "margin_vs_PUB_bits", "log2_table_entries")}
                ent["ENUM_min"] = {k: min([r for r in prim if r["model"] == "ENUM"], key=lambda r: r["TOTAL"])[k]
                                   for k in ("m", "d", "TOTAL", "margin_vs_VOW_bits", "margin_vs_PUB_bits")}
            per_degree.setdefault(str(n), {})[bd] = ent
    result["per_degree_minimum"] = per_degree
    if 131 in degrees:
        result["E2_131_detail_expectation"] = E2_131_DETAIL

    controls = {}
    controls["C-IMPL-GATE"] = {"stopping": True, "passed": True, "report": "gate/gate_report.json"}
    controls["C-GENERIC-LOWER-BOUND-FLAG"] = {"stopping": True, "fired": False,
                                              "cells_checked": dp.flag["cells_checked"]}

    # C-BOUND-PROBE
    disagreements = []
    half_idx = {(r["n"], r["model"], r["B"], r["m"]): r for r in rows if r["d_bound"] == "n/2"}
    agree = 0
    for r in rows:
        if r["d_bound"] != "n":
            continue
        h = half_idx.get((r["n"], r["model"], r["B"], r["m"]))
        if h is not None and h["d"] == r["d"] and abs(h["TOTAL"] - r["TOTAL"]) < 1e-12:
            agree += 1
        else:
            disagreements.append({"n": r["n"], "model": r["model"], "B": r["B"], "m": r["m"],
                                  "d_at_n": r["d"], "TOTAL_at_n": r["TOTAL"],
                                  "d_at_n_half": None if h is None else h["d"],
                                  "TOTAL_at_n_half": None if h is None else h["TOTAL"],
                                  "label": "bound-tracking"})
    deg_agree = {}
    for n in degrees:
        a1 = per_degree[str(n)]["n"]["primary_min"]
        a2 = per_degree[str(n)]["n/2"]["primary_min"]
        s1 = per_degree[str(n)]["n"]["store_free_min_MITM"]
        s2 = per_degree[str(n)]["n/2"]["store_free_min_MITM"]
        deg_agree[str(n)] = {"primary_min_agrees": a1["TOTAL"] == a2["TOTAL"] and a1["d"] == a2["d"],
                             "store_free_min_agrees": s1["TOTAL"] == s2["TOTAL"] and s1["d"] == s2["d"]}
    prim_dis = [x for x in disagreements if x["model"] in drv.PRIMARY_MODELS]
    controls["C-BOUND-PROBE"] = {
        "bounds": ["n", "n/2"],
        "argmin_rows_compared": agree + len(disagreements),
        "argmin_rows_agreeing": agree,
        "argmin_rows_disagreeing": len(disagreements),
        "argmin_rows_disagreeing_primary": len(prim_dis),
        "disagreements": disagreements,
        "per_degree_minimum_agreement": deg_agree,
        "pass_criterion": "both bounds agree on every reported argmin, or the disagreement is reported per bound and the figure downgraded to bound-tracking",
        "passed": True,
        "note": "non-stopping (AMD stopping_rules); every disagreeing argmin is reported per bound and labelled bound-tracking",
    }

    # A6 table
    a6 = []
    for n in degrees:
        vow = drv.vow_column(n)
        pub = drv.pub_column(n)
        for m in range(2, 17):
            for bd in ("n", "n/2"):
                bound = float(n) if bd == "n" else n / 2.0
                st3 = dp.step3.get((n, m, bd), {})
                entry = {"n": n, "m": m, "d_bound": bd}
                for col, target, key in (("VOW", vow, "min_store_subrho_VOW"), ("PUB", pub, "min_store_subrho_PUB")):
                    if target is None:
                        continue
                    s4 = step4_continuous(drv, n, m, target, bound)
                    s3 = st3.get(key)
                    realised = None
                    if s4 is not None:
                        realised = bool(s3 is not None and abs(s3["log2_table_entries"] - s4["log2_store_infimum"]) < 1e-6)
                    entry[col] = {"step4_continuous_min_store": s4 if s4 is not None else "infeasible: no (d, continuous s) cell in range has TOTAL below the column",
                                  "step3_best_integer_s_subrho_cell": s3 if s3 is not None else "none: no in-domain integer-s cell below the column",
                                  "step4_minimum_realised_by_a_step3_cell": realised if s4 is not None else "not applicable (no continuous minimum)"}
                entry["step3_min_total_cell"] = st3.get("min_total")
                a6.append(entry)
    controls["A6-TABLE"] = {"rows": a6,
                            "step4_feasible_count": sum(1 for e in a6 for c in ("VOW", "PUB")
                                                        if c in e and isinstance(e[c]["step4_continuous_min_store"], dict)),
                            "step3_subrho_count": sum(1 for e in a6 for c in ("VOW", "PUB")
                                                      if c in e and isinstance(e[c]["step3_best_integer_s_subrho_cell"], dict)),
                            "note": "step 4 solves TOTAL < column for the minimum continuous store x = s*d in [0, S*d] at d step 0.05 with the C-2 guard; step 3 is the integer-s MITM / MITM_CAPPED sweep (all B). An unrealised step-4 minimum is a model bound, never an attack parameter."}

    # C-BASELINE-CONSISTENCY (restated, C-6 (iii))
    bc = {"per_degree": {}}
    ok = True
    for n in degrees:
        v = drv.vow_column(n)
        indep = math.log2(0.886) + G.ref_N(n, log2_r) / 2.0
        ok = ok and abs(v - indep) < 1e-9 and (drv.pub_column(n) is None) == (n != 131)
        bc["per_degree"][str(n)] = {"VOW": v, "independent_recompute": indep,
                                    "PUB": drv.pub_column(n)}
    if 131 in degrees:
        v131 = drv.vow_column(131)
        naive = math.log2(0.886) + 131 / 2.0
        bc["n131"] = {"VOW_from_r": v131, "log2_of_0.886_times_2_pow_65.5": naive,
                      "VOW_below_naive_bits": naive - v131,
                      "PUB": drv.PUB_131, "VOW_minus_PUB_bits": v131 - drv.PUB_131,
                      "PUB_minus_VOW_bits": drv.PUB_131 - v131,
                      "log2_sqrt_131": math.log2(math.sqrt(131.0)),
                      "expected_gap_per_amendment": 3.516,
                      "A7_4_52_bit_attribution": "WITHDRAWN by AMD-20261001-e61f2b C-6 (iii)"}
    bc["PUB_used_only_at_131"] = all((drv.pub_column(n) is None) == (n != 131) for n in degrees)
    bc["margins_name_their_column"] = "every margin field in this file is margin_vs_VOW_bits or margin_vs_PUB_bits; no field mixes columns"
    bc["passed"] = bool(ok and bc["PUB_used_only_at_131"])
    controls["C-BASELINE-CONSISTENCY"] = bc

    # A4 genuine null (C-6 (iv))
    def anysub(pred, col):
        k = "subrho_vs_VOW" if col == "VOW" else "subrho_vs_PUB"
        return any((c[k] or 0) > 0 for c in prim_n if pred(c))
    sf_pred = lambda c: c["model"] in ("ENUM", "MITM") or (c["model"] == "MITM_CAPPED" and c["B"] == "unlimited")
    sb_pred = lambda c: c["model"] == "ENUM" or (c["model"] == "MITM_CAPPED" and c["B"] != "unlimited")
    sb80_pred = lambda c: c["model"] == "ENUM" or (c["model"] == "MITM_CAPPED" and c["B"] != "unlimited" and int(c["B"]) <= 80)
    a4 = {}
    for col in ("VOW", "PUB"):
        sf, sb, sb80 = anysub(sf_pred, col), anysub(sb_pred, col), anysub(sb80_pred, col)
        a4[col] = {"store_free_any_subrho_cell": sf, "store_budgeted_any_subrho_cell": sb,
                   "store_budgeted_le_2_80_any_subrho_cell": sb80, "verdicts_differ": sf != sb}
    differ = any(a4[c]["verdicts_differ"] for c in a4)
    a4["verdict_differs_between_treatments"] = differ
    a4["A4_report"] = ("The family's verdict DIFFERS between store-free and store-budgeted treatments under C-1."
                       if differ else
                       "A4 refutation branch, in A4's terms: the verdict does not differ between store-free and store-budgeted treatments under C-1 -- the oracle's unpriced STORE was not the asymmetry; the unpriced BUILD TIME was.")
    a4["scope"] = "PUB column evaluated at n = 131 only"
    controls["A4-GENUINE-NULL"] = a4

    # C-BINDINGNESS-DIAGNOSTIC (A4 relabel of C-NULL-NO-MEMORY-CHARGE)
    sub_free, sub_cap = set(), set()
    for r in primary_rows_n:
        if r["model"] == "MITM" and r["subrho_vs_VOW"]:
            for b in drv.FINITE_BUDGETS:
                sub_free.add((r["n"], r["m"], bkey(b)))
        if r["model"] == "MITM_CAPPED" and r["B"] != "unlimited" and r["subrho_vs_VOW"]:
            sub_cap.add((r["n"], r["m"], r["B"]))
    controls["C-BINDINGNESS-DIAGNOSTIC"] = {
        "subrho_argmin_cells_store_free_per_finite_budget_label": len(sub_free),
        "subrho_argmin_cells_capped": len(sub_cap), "sets_identical": sub_free == sub_cap,
        "note": "diagnostic only, never read as a refutation (A4); column VOW; construction charged"}

    # C-M3-ANCHOR (v1 control, retained; A8 unconferred grade)
    m3 = {}
    if 131 in degrees:
        for model in ("ENUM", "MITM"):
            tots, oodc = [], 0
            for d in range(10, 61, 2):
                c = drv.evaluate(131, model, 3, float(d), None)
                if c[I_CALLS] < 0:
                    oodc += 1
                    continue
                tots.append(c[I_TOTAL])
            m3[model] = {"d_range": [10, 60], "d_step": 2, "out_of_domain": oodc,
                         "log2_total_min": min(tots), "log2_total_max": max(tots),
                         "spread_bits": max(tots) - min(tots),
                         "d_independent_within_1_bit": max(tots) - min(tots) < 1.0,
                         "offset_from_measured_bits": min(tots) - M3_MEASURED_BASE,
                         "within_5_bits_of_measured": abs(min(tots) - M3_MEASURED_BASE) <= 5.0}
        m3["passed"] = all(m3[k]["d_independent_within_1_bit"] and m3[k]["within_5_bits_of_measured"] for k in ("ENUM", "MITM"))
        m3["note"] = "consistency anchor of UNCONFERRED grade (A8); a failure would be ambiguous, not resolved against this contract; non-stopping"
    controls["C-M3-ANCHOR"] = m3

    # C-DEGENERATE-M
    controls["C-DEGENERATE-M"] = {"argmin_rows_flagged": sum(1 for r in rows if r["degenerate"]),
                                  "rule": "k = N/m < 2, or m > n, or d < 1", "diagnostic": True}

    # C-5: A1(i) structural floor reproduction, NON-GATING diagnostic
    if 131 in degrees:
        fl = []
        for m in sorted(COMMITTED_FLOOR):
            r = next(x for x in rows if x["n"] == 131 and x["model"] == "FREE" and x["B"] == "unlimited"
                     and x["m"] == m and x["d_bound"] == "n")
            fl.append({"m": m, "committed": COMMITTED_FLOOR[m], "recomputed_v2_FREE": r["TOTAL"],
                       "d": r["d"], "offset_committed_minus_recomputed_bits": COMMITTED_FLOOR[m] - r["TOTAL"],
                       "committed_below_PUB": COMMITTED_FLOOR[m] < drv.PUB_131,
                       "recomputed_below_PUB": r["TOTAL"] < drv.PUB_131})
        offs = [x["offset_committed_minus_recomputed_bits"] for x in fl]
        controls["C-FLOOR-REPRO-DIAGNOSTIC"] = {
            "gating": False, "rows": fl,
            "committed_strictly_decreasing": all(fl[i]["committed"] > fl[i + 1]["committed"] for i in range(len(fl) - 1)),
            "recomputed_strictly_decreasing": all(fl[i]["recomputed_v2_FREE"] > fl[i + 1]["recomputed_v2_FREE"] for i in range(len(fl) - 1)),
            "all_signs_vs_PUB_agree": all(x["committed_below_PUB"] == x["recomputed_below_PUB"] for x in fl),
            "m3_above_PUB_recomputed": not fl[1]["recomputed_below_PUB"],
            "m4_below_PUB_recomputed": fl[2]["recomputed_below_PUB"],
            "offset_trend_monotone_increasing_in_m": all(offs[i] < offs[i + 1] for i in range(len(offs) - 1)),
            "A1_ii_offset_signature": "WITHDRAWN (C-5); not evaluated",
            "A8": "committed table is of unconferred grade"}

    # M0 reference object: probe-only agreement with RUN-SEMBIN-c68773 (non-gating)
    mx_probe, mx_tot, nrows = 0.0, 0.0, 0
    for (n, model, bk, m), r in v1_idx.items():
        if n not in degrees or model == "MITM_CAPPED" and bk == "unlimited":
            continue
        b = None if bk == "unlimited" else float(bk)
        c = drv.evaluate(n, model, m, float(r["d"]), b)
        mx_probe = max(mx_probe, abs(c[I_PROBE] - r["log2_relation_phase"]))
        mx_tot = max(mx_tot, abs(drv.probe_only_total(c) - r["log2_total"]))
        nrows += 1
    controls["M0-PROBE-ONLY-REFERENCE"] = {
        "gating": False, "object": "RUN-SEMBIN-c68773 raw-result.json (evidence-inadmissible; probe-only v1 reference, not a cost)",
        "v1_rows_compared": nrows,
        "max_abs_diff_v2_PROBE_vs_v1_log2_relation_phase": mx_probe,
        "max_abs_diff_v2_probe_only_total_vs_v1_log2_total": mx_tot,
        "note": "v1 values are rounded to 4 decimals; agreement within 5e-5 means v2's PROBE term reproduces v1's relation-phase arithmetic"}

    result["controls"] = controls
    result["controls_reported"] = len(controls)

    # E-1..E-4 side by side (expectations, NOT targets)
    result["expectations_side_by_side"] = {
        "E-1": {"expectation": "zero in-domain primary sub-rho cells against either column",
                "computed_subrho_vs_VOW": result["primary_subrho_totals"]["subrho_vs_VOW"],
                "computed_subrho_vs_PUB_at_131": result["primary_subrho_totals"]["subrho_vs_PUB_at_131"]},
        "E-2": {str(n): {"E2": E2_STORE_FREE_MARGIN_VS_VOW.get(n),
                         "v2": per_degree[str(n)]["n"]["store_free_min_MITM"]["margin_vs_VOW_bits"],
                         "diff": per_degree[str(n)]["n"].get("v2_minus_E2_bits"),
                         "over_0_1_bit": per_degree[str(n)]["n"].get("differs_from_E2_by_more_than_0_1_bit")}
                for n in degrees},
        "E-3": {"expectation": "gate passes unmutated, fails M1-M4", "computed": gate_report["e_gate_power_self_test"]},
        "E-4": {"expectation": "generic flag does not fire", "computed_fired": dp.flag["fired"]},
        "rule": "expectations are reviewer-derived, not preregistered, not targets; nothing adjusted toward them",
    }

    # exploratory block (segregated)
    log("exploratory X-1..X-8")
    if not a.smoke_degrees:
        result["EXPLORATORY_NON_GATING_NEVER_CONFIRMATORY"] = X.all_columns(drv)
    result["halted"] = False
    write_raw()
    log(f"completed; controls_reported={len(controls)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
