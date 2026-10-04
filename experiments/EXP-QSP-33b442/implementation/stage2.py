#!/usr/bin/env python3
"""EXP-QSP-33b442 RUN 3 -- Stage 2: the complete-splitting sweep.

n prime in {7, 11, 13, 17, 19, 23, 29, 31}; 2 <= n' <= 15 with n' < n and
n' not dividing n; 2 <= d <= min(8, 2^{n'} - 1); every lambda in F_2[X] of
exact degree d.  I2 (the compiled helper) on the whole sweep; I1 wherever 2^n
enumeration is affordable (n <= 13); I3 on every candidate with N >= 2^{n'-1},
subject to the deg D cap of AMD-20260917-001.

Usage:  python3 stage2.py RUN-QSP-33b442-S2
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qspcore import (KField, field_poly_str, deg, poly_str, tpoly_str, polys_of_degree,
                     is_linearized, is_affine, i1_brute_f2, i3_injection_f2,
                     difference_poly_f2, deg_D_and_degenerate, verify_roots_f2, f2_roots_in_K,
                     c6_linearized_N, linearized_symbol)
import runlib

HERE = os.path.dirname(os.path.abspath(__file__))
PRIMES = [7, 11, 13, 17, 19, 23, 29, 31]
I3_DEG_CAP = 1000000                 # AMD-20260917-001
I1_MAX_N = 13                        # 2^n enumeration affordable
COLUMNS = ["lambda_bits", "lambda_printed", "n", "n_prime", "d", "q", "r", "N",
           "bound", "ratio", "beta", "corollary_exact", "corollary_conservative",
           "complete", "near_complete", "linearized", "affine",
           "square_lambda_prime_zero", "I1", "I2", "I3", "deg_D", "slack",
           "i3_run", "i3_skip_reason", "field_polynomial", "degenerate_D_zero"]


def cells() -> list[tuple[int, int]]:
    out = []
    for n in PRIMES:
        for npr in range(2, 16):
            if npr >= n or n % npr == 0:
                continue
            out.append((n, npr))
    return out


def gf2rc_batch(items):
    inp = "".join("%d %d %x\n" % (n, npr, lam) for n, npr, lam in items)
    out = subprocess.run([os.path.join(HERE, "gf2rc")], input=inp, capture_output=True,
                         text=True, check=True).stdout.split("\n")
    res = [int(l.split()[-1]) for l in out if l.strip()]
    assert len(res) == len(items), (len(res), len(items))
    assert all(v >= 0 for v in res), "gf2rc rejected an input (deg lam >= 2^{n'})"
    return res


def helper_self_test(run) -> dict:
    """Exercise the two guards of the 2026-09-17 parser fix recorded in
    analysis/qsp-ecc2k130/explore/README.md, and cross-check the helper against
    the independent Python implementation of I2.

    (a) A hex input of 131073 digits (512 KiB, far above the 64 KiB line buffer
        and 32 KiB hex buffer of the pre-fix parser) must round-trip in the
        echoed output rather than truncate.
    (b) deg lam >= 2^{n'} must be REJECTED (count -1) rather than entering the
        unguarded reduction loop.
    (c) A 32769-digit hex input (above the pre-fix 32 KiB hex buffer) must be
        accepted and produce a count.
    (d) On 200 small candidates the helper must return exactly what
        qspcore.i2_gcd_f2 returns in Python.
    """
    from qspcore import i2_gcd_f2
    res = {}
    lam_bad = (1 << (1 << 19)) | 1          # deg lam = 2^19 = 2^{n'} at n' = 19
    hx = "%x" % lam_bad
    out = subprocess.run([os.path.join(HERE, "gf2rc")], input="19 19 %s\n" % hx,
                         capture_output=True, text=True, check=True).stdout.split()
    res["a_hex_digits_in"] = len(hx)
    res["a_hex_echoed_intact"] = (out[2] == hx)
    res["b_oversize_lambda_rejected_with_minus_1"] = (int(out[3]) == -1)
    lam_ok = (1 << (1 << 17)) | 1           # deg lam = 2^17 < 2^18, 32769 hex digits
    hx2 = "%x" % lam_ok
    out2 = subprocess.run([os.path.join(HERE, "gf2rc")], input="19 18 %s\n" % hx2,
                          capture_output=True, text=True, check=True).stdout.split()
    res["c_hex_digits_in"] = len(hx2)
    res["c_hex_echoed_intact"] = (out2[2] == hx2)
    res["c_count_returned"] = int(out2[3])
    from qspcore import polys_of_degree
    items, exp = [], []
    for n_, npr_ in ((11, 6), (13, 7), (7, 3)):
        for d_ in (2, 3, 4):
            for lam_ in polys_of_degree(d_):
                items.append((n_, npr_, lam_))
                exp.append(i2_gcd_f2(n_, npr_, lam_))
    got = gf2rc_batch(items)
    res["d_python_vs_c_candidates"] = len(items)
    res["d_python_vs_c_mismatches"] = sum(1 for a, b in zip(exp, got) if a != b)
    run.log("[helper self-test] (a) %d hex digits echoed intact: %s ; (b) oversize lambda "
            "rejected: %s ; (c) %d hex digits accepted, count %d ; (d) %d candidates "
            "vs the Python I2: %d mismatches"
            % (res["a_hex_digits_in"], res["a_hex_echoed_intact"],
               res["b_oversize_lambda_rejected_with_minus_1"], res["c_hex_digits_in"],
               res["c_count_returned"], res["d_python_vs_c_candidates"],
               res["d_python_vs_c_mismatches"]))
    assert res["a_hex_echoed_intact"] and res["b_oversize_lambda_rejected_with_minus_1"]
    assert res["c_hex_echoed_intact"] and res["d_python_vs_c_mismatches"] == 0
    return res


def main(run_id: str) -> int:
    rng = random.Random(0xC0FFEE)
    cl = cells()
    inputs = {
        "stage": "stage_2 (complete-splitting sweep)",
        "cells": [{"n": n, "n_prime": npr, "q": n // npr, "r": n % npr,
                   "d_range": [2, min(8, (1 << npr) - 1)],
                   "field_polynomial": field_poly_str(n)} for n, npr in cl],
        "cell_count": len(cl),
        "candidate_set": "every lambda in F_2[X] of exact degree d for "
                         "2 <= d <= min(8, 2^{n'} - 1); exhaustive, seed-free",
        "instruments": "I2 via the compiled helper gf2rc on every candidate; "
                       "I1 by enumeration of all 2^n elements for n <= %d; "
                       "I3 on every candidate with N >= 2^{n'-1} and deg D <= %d "
                       "(AMD-20260917-001)" % (I1_MAX_N, I3_DEG_CAP),
        "thresholds": {
            "beta": "l n / n'^2 with l = log_2 d",
            "primary_exact_corollary": "beta >= n / (n + n' - r)",
            "fallback_conservative_corollary": "beta >= n (n' - 1) / (n' (n + n' - r))",
        },
        "seeds": {"base_seed": runlib.BASE_SEED, "stage_2_is_seed_free": True,
                  "note": "exhaustive candidate set; the only random.Random "
                          "(seed 0xC0FFEE) drives equal-degree splitting inside I3, "
                          "whose factor set is unique"},
        "amendment_in_force": "AMD-20260917-001",
    }
    run = runlib.Run(run_id, "stage_2",
                     "python3 experiments/EXP-QSP-33b442/implementation/stage2.py " + run_id,
                     inputs, certificate_kind="root_list")
    raw: dict = {"stage": "stage_2", "specification_version": 1}
    subprocess.run("gcc -O2 -o gf2rc gf2rc.c", shell=True, cwd=HERE, check=True)
    raw["helper_build_command"] = "gcc -O2 -o gf2rc gf2rc.c"
    raw["helper_self_test"] = helper_self_test(run)

    run.log("== Stage 2 sweep: %d cells" % len(cl))
    n_i1_run = 0
    max_ratio_row = None
    attain_7_4 = []
    cell_summ = {}
    near_rows, complete_rows = [], []
    i1_disagree, i3_disagree = [], []
    c6_rows, c6_disagree = [], []
    violations = []
    i3_skipped = []
    total = 0
    for n, npr in cl:
        q, r = divmod(n, npr)
        dmax = min(8, (1 << npr) - 1)
        items = [(n, npr, lam) for d in range(2, dmax + 1) for lam in polys_of_degree(d)]
        Ns = gf2rc_batch(items)
        K = KField(n) if n <= I1_MAX_N else None
        rows = []
        for (nn, np_, lam), N in zip(items, Ns):
            d = deg(lam)
            total += 1
            bound = max(d ** (q + 1), 1 << (npr - r))
            beta = math.log2(d) * n / (npr * npr)
            cor_e = n / (n + npr - r)
            cor_c = n * (npr - 1) / (npr * (n + npr - r))
            complete = (N == (1 << npr))
            near = (N >= (1 << (npr - 1)))
            i1 = i1_brute_f2(K, lam, npr)[0] if K is not None else None
            degD, is_degenerate = deg_D_and_degenerate(lam, n, npr)
            i3N = None
            slack = None
            i3_run = False
            skip = None
            if near and not is_degenerate:
                if degD <= I3_DEG_CAP:
                    res = i3_injection_f2(K if K is not None else KField(n), lam, npr, rng)
                    i3N = res["N"]
                    slack = res["slack"]
                    i3_run = True
                else:
                    skip = "deg_D_above_declared_cap"
            elif near and is_degenerate:
                skip = "degenerate_D_zero (excluded from the M1 ratio; the trivial "\
                       "bound N <= 2^{n'-j} < 2^{n'} applies, H-QSP-5540d7 assumption 1)"
            row = dict(zip(COLUMNS, [
                lam, poly_str(lam), n, npr, d, q, r, N, bound, N / bound, beta,
                cor_e, cor_c, complete, near, is_linearized(lam), is_affine(lam),
                all(((lam >> i) & 1) == 0 for i in range(1, d + 1, 2)),
                i1, N, i3N, degD, slack, i3_run, skip, field_poly_str(n),
                is_degenerate]))
            if i1 is not None and i1 != N:
                i1_disagree.append(row)
            if i3N is not None and i3N != N:
                i3_disagree.append(row)
            if skip:
                i3_skipped.append({k: row[k] for k in
                                   ("n", "n_prime", "d", "lambda_printed", "N", "deg_D")})
            if is_linearized(lam):
                Nc6, dg, splits = c6_linearized_N(lam, npr, n)
                ok = (Nc6 == N) and (i1 is None or i1 == Nc6) and (i3N is None or i3N == Nc6)
                rec = {"n": n, "n_prime": npr, "d": d, "lambda_printed": poly_str(lam),
                       "symbol_f": tpoly_str(linearized_symbol(lam, npr)),
                       "deg_gcd_f_Tn_minus_1": dg, "N_predicted": Nc6,
                       "splits_completely": splits, "I1": i1, "I2": N, "I3": i3N,
                       "agrees_with_instruments": ok}
                c6_rows.append(rec)
                if not ok:
                    c6_disagree.append(rec)
            if N > bound:
                roots = None
                if K is not None:
                    roots = i1_brute_f2(K, lam, npr, want_roots=True)[1]
                elif degD <= I3_DEG_CAP and not is_degenerate:
                    res = i3_injection_f2(KField(n), lam, npr, rng, want_roots=True)
                    roots = [x for orb in res.get("root_orbits", []) for x in orb]
                if roots is not None:
                    row["explicit_roots_in_K"] = [KField(n).elt_str(x) for x in roots]
                    row["root_verification"] = verify_roots_f2(KField(n), lam, npr, roots)
                else:
                    row["root_verification"] = {"all_roots_verified": None,
                                                "reason": "no affordable root extraction"}
                violations.append(row)
            if near:
                near_rows.append(row)
            if complete:
                complete_rows.append(row)
            if i1 is not None:
                n_i1_run += 1
            if max_ratio_row is None or row["ratio"] > max_ratio_row["ratio"]:
                max_ratio_row = row
            if n == 7 and npr == 4 and row["ratio"] == 1.0:
                attain_7_4.append(row["lambda_printed"])
            rows.append(row)
        label = "n%d_np%d" % (n, npr)
        cell_summ[label] = {
            "n": n, "n_prime": npr, "q": q, "r": r, "candidates": len(rows),
            "field_polynomial": field_poly_str(n),
            "max_N": max(r_["N"] for r_ in rows),
            "max_ratio": max(r_["ratio"] for r_ in rows),
            "near_complete": sum(1 for r_ in rows if r_["near_complete"]),
            "complete": sum(1 for r_ in rows if r_["complete"]),
            "i1_run": K is not None,
        }
        with open(run.path("cells", label + ".json"), "w") as fh:
            json.dump({"cell": cell_summ[label], "columns": COLUMNS,
                       "rows": [[r_.get(c) for c in COLUMNS] for r_ in rows]},
                      fh, indent=0, sort_keys=False)
        run.log("   n=%2d n'=%2d q=%2d r=%2d: %4d candidates, max N = %6d, "
                "near-complete = %3d, complete = %2d%s" % (
                    n, npr, q, r, len(rows), cell_summ[label]["max_N"],
                    cell_summ[label]["near_complete"], cell_summ[label]["complete"],
                    "" if K is not None else "  (I1 not affordable)"))

    def m3_cols(r_):
        return {k: r_[k] for k in ("n", "n_prime", "d", "q", "r", "N", "bound", "ratio",
                                   "beta", "corollary_exact", "corollary_conservative",
                                   "lambda_printed", "linearized", "I1", "I2", "I3",
                                   "i3_run", "i3_skip_reason", "deg_D", "slack")} | {
            "beta_minus_exact": r_["beta"] - r_["corollary_exact"],
            "beta_minus_conservative": r_["beta"] - r_["corollary_conservative"]}

    complete_tab = [m3_cols(r_) for r_ in complete_rows]
    near_tab = [m3_cols(r_) for r_ in near_rows]
    below_exact = [r_ for r_ in complete_tab if r_["r"] >= 1 and r_["beta_minus_exact"] < 0]
    below_cons = [r_ for r_ in complete_tab if r_["r"] >= 1 and r_["beta_minus_conservative"] < 0]
    raw["stage_2_totals"] = {"cells": len(cl), "candidates": total,
                             "near_complete_rows": len(near_tab),
                             "complete_splitters": len(complete_tab)}
    raw["cell_summaries"] = cell_summ
    raw["per_cell_json_files"] = ["cells/%s.json" % k for k in cell_summ]
    raw["M3_complete_splitters"] = complete_tab
    raw["M3_near_complete"] = near_tab
    raw["M3_complete_splitter_cells"] = sorted({(r_["n"], r_["n_prime"]) for r_ in complete_tab})
    raw["M3_below_exact_corollary"] = below_exact
    raw["M3_below_conservative_corollary"] = below_cons
    raw["agreement"] = {
        "I1_run_on": n_i1_run,
        "I1_vs_I2_disagreements": len(i1_disagree),
        "I3_run_on": sum(1 for r_ in near_rows if r_["i3_run"]),
        "I3_vs_I2_disagreements": len(i3_disagree),
        "disagreeing_candidates": i1_disagree + i3_disagree,
    }
    raw["I3_skipped_above_cap"] = {
        "cap": I3_DEG_CAP, "amendment": "AMD-20260917-001",
        "count": len(i3_skipped), "candidates": i3_skipped,
        "note": "N for these candidates rests on I2 alone (and on I1 where n <= 13).",
    }
    raw["C6_linearized_cross_check"] = {"candidates": len(c6_rows),
                                        "disagreements": c6_disagree, "rows": c6_rows}
    raw["violations_of_the_bound"] = violations
    raw["tail_checks"] = {
        "attainment_at_7_4": attain_7_4,
        "largest_ratio": max_ratio_row["ratio"],
        "largest_ratio_row": max_ratio_row,
        "minimum_beta_minus_exact_over_complete_splitters":
            min((r_["beta_minus_exact"] for r_ in complete_tab), default=None),
        "minimum_beta_minus_conservative_over_complete_splitters":
            min((r_["beta_minus_conservative"] for r_ in complete_tab), default=None),
    }
    run.log("\n   totals: %d candidates, %d near-complete, %d complete splitters at cells %s"
            % (total, len(near_tab), len(complete_tab), raw["M3_complete_splitter_cells"]))
    run.log("   I1 ran on %d candidates (0 disagreements: %s); I3 ran on %d of %d "
            "near-complete (0 disagreements: %s); %d skipped above the deg D cap"
            % (raw["agreement"]["I1_run_on"], not i1_disagree,
               raw["agreement"]["I3_run_on"], len(near_tab), not i3_disagree, len(i3_skipped)))
    run.log("   complete splitters below the EXACT corollary: %d; below the "
            "CONSERVATIVE corollary: %d" % (len(below_exact), len(below_cons)))

    bad = bool(i1_disagree or i3_disagree or c6_disagree)
    if bad:
        reason = "instrument or Proposition-2 disagreement (F5)"
        run.warn("STOP:", reason)
        run.finish(raw, "invalid_measurement", reason,
                   certificate={"kind": "none", "verified": None,
                                "verifier": "n/a: run invalid"},
                   anomalies=[{"branch": "F5", "detail": reason}])
        return 1
    status = "completed_valid"
    reason = ("sweep complete: %d candidates through I2, %d complete splitters, "
              "%d below the exact corollary, %d below the conservative corollary, "
              "%d candidates above max(d^{q+1}, 2^{n'-r})"
              % (total, len(complete_tab), len(below_exact), len(below_cons), len(violations)))
    anomalies = []
    if below_exact:
        anomalies.append({"branch": "F2", "detail": "complete splitter(s) with beta below "
                          "the exact corollary", "rows": below_exact})
    if violations:
        anomalies.append({"branch": "F1", "detail": "candidate(s) above the bound",
                          "rows": violations})
    run.finish(raw, status, reason,
               certificate={"kind": "root_list",
                            "verified": all(v.get("root_verification", {})
                                            .get("all_roots_verified") for v in violations)
                            if violations else True,
                            "verifier": "qspcore.verify_roots_f2",
                            "certified_candidates": len(violations)},
               anomalies=anomalies)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
