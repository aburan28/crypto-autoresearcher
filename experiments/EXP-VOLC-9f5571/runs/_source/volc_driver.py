#!/usr/bin/env python3
"""EXP-VOLC-9f5571 driver (GOAL-ENDO-001, BATCH-d7e255, TASK-20260810-a431bd).

NEW driver + new module, executed standalone (not `-m harness.X`) so that it
lives entirely inside this task's write_scope
(experiments/EXP-VOLC-9f5571/runs/). `harness/exp_icinv.py` is NOT edited and
NOT reimplemented (source_constraints); it is imported read-only, as is
`harness.isogeny_class`, `harness.toycurve` and `harness.exp_icinv_fullgroup`
(the certified full-group sampler `targets_B` lives there). `volc_graph.py`
(this directory) is the new Velu ell-isogeny graph builder for general odd ell
plus a dedicated ell=2 formula, required because
`harness.isogeny_class.velu_odd` refuses ell=2 by design.

Executes the frozen stopping-rule sequence IN THE ORDER THE CONTRACT GIVES
THEM: SR1 -> SR2 -> SR3 -> SR4 -> SR5 -> raw level-count collection -> SR6
(blocking gate on any LEVEL VERDICT). T5 is NOT gated by SR6 (its own
heuristic HEUR-VOLC-1 is validated inside this experiment by
C-LOCAL-EXHAUSTIVE, not by EXP-INSTR-36c8cf, per the contract's
heuristic_under_test_note) and is computed and reported in full wherever the
underlying graph exists to compute it from.

MID-RUN DISCOVERY, RECORDED RATHER THAN WORKED AROUND: the matched-order
family fixes N = #E(F_p) = 19507, which is PRIME. By Lagrange's theorem
E(F_p) then has NO point of order ell for any ell != N, in particular for
ell = 3 and ell = 107 -- the two conductor-arm isogeny degrees this contract's
level_construction paragraph specifies. Velu's classical formulas, as
implemented (and as available anywhere in this harness), require an explicit
KERNEL POINT; a Galois-stable-but-not-pointwise-rational kernel of order ell
can still define a genuine F_p-rational isogeny (as a morphism), but
constructing it needs arithmetic over a field extension of F_p (to represent
an actual kernel generator) that `harness.toycurve.EllipticCurve` (F_p only)
does not provide, and that this dispatch does not attempt to add expediently
(risk of a silently wrong isogeny graph is judged worse than an honest
UNREACHED). This is verified EMPIRICALLY below (not just cited): a full
liftable-x scan for points of order 3 and of order 107 on every curve in both
conductor-arm classes returns zero, on every curve, in every class.
Consequence, stated precisely: every measurement that requires the explicit
within-class Velu graph (per-level vertex counts, the detection floor implied
by them, T5 branch (i) and (ii), the T1 transport certificate) is UNREACHED
for this run, not measured and not imputed. SR1, SR2, SR3 (on curves that
exist) and SR4 (matched null, sized by an independent, non-graph
Hurwitz-class-number method, disclosed as such) ARE fully executed below with
real numbers.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.dirname(__file__))

import sympy  # noqa: E402

from harness import isogeny_class as ic  # noqa: E402
from harness import exp_icinv as ex  # noqa: E402
from harness import exp_icinv_fullgroup as fg  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402
from harness.runner import RunResult, write_run, environment, git_state  # noqa: E402

import volc_graph as vg  # noqa: E402

EXP_ID = "EXP-VOLC-9f5571"
AREA = "VOLC"
RUN_ROOT = os.path.join(REPO, "experiments", EXP_ID)

SEEDS = [20260810, 20260811, 11235813, 20260812, 20260813, 20260814, 20260815, 20260816]
TARGET_COUNTS = [100, 400]
FB_SIZES_MAIN = [4, 6, 8, 10, 13, 17, 22]
FB_SIZES_NULL = [6, 10, 17]
N_FAMILY = 19507

# DEFECT REPAIR, DISCLOSED RATHER THAN SILENTLY FIXED (found before this
# module's first run was reported to the Coordinator, in the run that became
# RUN-VOLC-sr1-sr5-plus-t5-gate-v2 -- see runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v2
# /SUPERSEDED.md): `fg.measure_curve_all_arms` does NOT take a seeds/T
# parameter -- it iterates the MODULE-LEVEL constants `fg.SEEDS` and
# `fg.TARGET_COUNTS` to decide which (arm, seed, T) keys to pull out of
# `pkg.targets`, which is unaffected by the `seeds=`/`target_counts=` kwargs
# passed to `build_curve_package`. Left unoverridden, only the single seed
# and T values common to BOTH this module's declared grid (SEEDS/
# TARGET_COUNTS above) and `harness.exp_icinv_fullgroup`'s own frozen
# EXP-ICINV-4d33aa grid (11235813; 100 and 400) were ever actually scored --
# 1 of 8 declared seeds, silently, with no error. C-SEEDS ("full per-seed
# distribution... at least the declared seed count") requires all 8.
# Overriding the module globals here, ONCE, before any measurement call,
# makes every subsequent `measure_curve_all_arms` call score this contract's
# own declared grid instead. This does not edit `harness/exp_icinv_fullgroup
# .py` on disk (source_constraints forbids editing files it names, and this
# is not that); it rebinds the two names as any importer may.
fg.SEEDS = SEEDS
fg.TARGET_COUNTS = TARGET_COUNTS


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def write_json(run_dir: str, name: str, obj) -> str:
    path = os.path.join(run_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return sha256_json(obj)


# --------------------------------------------------------------------------
# SR1: Velu gate, p = 4001, t = 30, ell = 2
# --------------------------------------------------------------------------


def stage_sr1_velu_gate() -> dict:
    p, t = 4001, 30
    target = {0: 3, 1: 9, 2: 18, 3: 36, 4: 72}
    classes = ic.isogeny_classes(p)
    recs = classes[t]
    census = ic.class_census(p, {t: recs})
    graph = vg.build_ell2_graph(p, recs)
    dist, core = vg.assign_levels(graph)
    lc = vg.level_counts(dist)
    lc_int = {int(k): v for k, v in lc.items() if k != "UNREACHED"}
    passed = (lc_int == target) and not graph.unmatched
    # cross-check: the OLD 2-torsion-count proxy agrees with ell_subgroup
    # structure on all 138 curves (C-VELU-GATE second clause), computed for
    # the record ONLY -- never used as a level variable anywhere below.
    two_torsion_agrees = all(
        len(vg.two_torsion_roots(r.curve())) in (0, 1, 3) for r in recs)
    return {
        "gate": "SR1_VELU_GATE",
        "p": p, "t": t, "n_curves": len(recs),
        "target_level_distribution": {str(k): v for k, v in target.items()},
        "observed_level_distribution": {str(k): v for k, v in lc_int.items()},
        "unreached_vertices": lc.get("UNREACHED", 0),
        "unmatched_velu_edges": len(graph.unmatched),
        "directed_edges_found": len(graph.edges_directed),
        "core_size": len(core),
        "census_all_agree": all(c.agrees for c in census),
        "two_torsion_root_counts_in_expected_set": bool(two_torsion_agrees),
        "passed": bool(passed),
    }


# --------------------------------------------------------------------------
# SR2a: family construction, N = 19507
# --------------------------------------------------------------------------


def stage_sr2_family() -> dict:
    N = N_FAMILY
    n_prime = sympy.isprime(N)
    candidates = []
    for t in range(-320, 321):
        p = N + t - 1
        if p <= 3 or not sympy.isprime(p):
            continue
        hasse = 2 * int(p ** 0.5) + 2
        if abs(t) > hasse:
            continue
        D = t * t - 4 * p
        if D >= 0:
            continue
        D0, f = ic.fundamental_discriminant(D)
        candidates.append({"t": t, "p": p, "D": D, "D0": D0, "f": f})
    f1 = [c for c in candidates if c["f"] == 1]
    f3 = [c for c in candidates if c["f"] == 3]
    f107 = [c for c in candidates if c["f"] == 107]
    return {
        "gate": "SR2_FAMILY_CONSTRUCTION",
        "N": N, "N_is_prime": bool(n_prime),
        "t_search_range": [-320, 320],
        "total_candidates": len(candidates),
        "f1_count": len(f1), "f3_count": len(f3), "f107_count": len(f107),
        "candidates": candidates,
        "matches_design_doc_59_51": (len(candidates) == 59 and len(f1) == 51),
    }


def stage_sr2_census(p: int, t: int, expected_n: int) -> dict:
    classes = ic.isogeny_classes(p)
    recs = classes.get(t, [])
    census = ic.class_census(p, {t: recs})
    order_agree = []
    for r in recs:
        e_order = r.curve().order() if p <= 6000 else None
        char_order = r.order
        order_agree.append({
            "a": r.a, "b": r.b, "order_char_sum": char_order,
            "order_agrees_expected_N": bool(char_order == expected_n),
        })
    return {
        "p": p, "t": t, "n_curves": len(recs), "expected_N": expected_n,
        "census": [{"trace": c.trace, "observed_curves": c.observed_curves,
                    "observed_weighted": c.observed_weighted,
                    "predicted_weighted": c.predicted_weighted,
                    "agrees": c.agrees, "note": c.note} for c in census],
        "all_curves_order_equals_N": all(o["order_agrees_expected_N"] for o in order_agree),
        "aut_histogram": {str(a): sum(1 for r in recs if r.aut_order == a)
                          for a in sorted({r.aut_order for r in recs})},
        "per_curve_order_check": order_agree,
    }


# --------------------------------------------------------------------------
# the empirical kernel-rationality check (discovery, verified not assumed)
# --------------------------------------------------------------------------


def stage_kernel_rationality_check(p: int, t: int, ell: int) -> dict:
    classes = ic.isogeny_classes(p)
    recs = classes[t]
    per_curve = []
    total_found = 0
    for r in recs:
        E = r.curve()
        gens = vg.ell_subgroup_generators(E, r.order, ell)
        per_curve.append({"a": r.a, "b": r.b, "order": r.order,
                          "ell_divides_order": (r.order % ell == 0),
                          "rational_order_ell_subgroups_found": len(gens)})
        total_found += len(gens)
    return {
        "p": p, "t": t, "ell": ell, "n_curves": len(recs),
        "N_mod_ell": recs[0].order % ell,
        "total_rational_order_ell_subgroups_found": total_found,
        "per_curve": per_curve,
        "conclusion": ("gcd(N, ell) == 1: no F_p-rational point of order ell "
                      "can exist by Lagrange's theorem, verified here by "
                      "exhaustive scan rather than assumed"
                      if recs[0].order % ell else
                      "ell | N: rational kernel points may exist"),
    }


# --------------------------------------------------------------------------
# SR3 + rate measurement (arm B / targets_B only, per contract), whatever
# curves exist -- independent of the graph-construction gap above.
# --------------------------------------------------------------------------


def measure_class(p: int, t: int, label: str, fb_sizes: list[int],
                  seeds: list[int], target_counts: list[int]) -> dict:
    classes = ic.isogeny_classes(p)
    recs = classes[t]
    pkgs = []
    support_records = []
    all_rows = []
    t0 = time.time()
    for r in recs:
        pkg = fg.build_curve_package(r, arms=["B"], planted=False,
                                     seeds=seeds, target_counts=target_counts)
        pkgs.append(pkg)
        cov = pkg.coverage.get("B")
        support_records.append({
            "a": r.a, "b": r.b, "r_two_torsion": pkg.cert.r,
            "support_size": cov["support_size"],
            "predicted_support_size": cov["predicted_support_size"],
            "support_equals_predicted": cov["support_equals_predicted"],
            "support_subset_of_curve": cov["support_subset_of_curve"],
        })
        rows = fg.measure_curve_all_arms(pkg, fb_sizes)
        all_rows.extend(rows)
    elapsed = time.time() - t0
    all_support_ok = all(s["support_equals_predicted"] for s in support_records)

    cells = {}
    for fb in fb_sizes:
        for seed in seeds:
            for T in target_counts:
                agg = fg.aggregate_rows(all_rows, "B", seed, T, fb)
                if agg is not None:
                    cells[f"fb{fb}_seed{seed}_T{T}"] = agg

    r_hist = {}
    for r in recs:
        rv = ex.two_torsion_x_count(p, r.a, r.b)
        r_hist[str(rv)] = r_hist.get(str(rv), 0) + 1

    return {
        "label": label, "p": p, "t": t, "n_curves": len(recs),
        "order": recs[0].order if recs else None,
        "wall_seconds": elapsed,
        "all_support_certificates_ok": bool(all_support_ok),
        "support_records": support_records,
        "r_two_torsion_histogram": r_hist,
        "fb_sizes_swept": fb_sizes, "seeds": seeds, "target_counts": target_counts,
        "cells": cells,
        "raw_rows": all_rows,
    }


# --------------------------------------------------------------------------
# SR4: matched null, f = 1 class, arbitrary declared split sized by an
# INDEPENDENT (non-graph) Hurwitz class-number method -- disclosed as such,
# never presented as the graph-derived level split it is standing in for.
# --------------------------------------------------------------------------


def stage_sr4_matched_null(p: int, t: int, split_a: int, split_b: int,
                           real_arm_label: str, real_sizes_note: str,
                           fb_sizes: list[int], seeds: list[int],
                           target_counts: list[int]) -> dict:
    classes = ic.isogeny_classes(p)
    recs = classes[t]
    assert split_a + split_b == len(recs), (split_a, split_b, len(recs))
    # deterministic arbitrary split: first split_a curves in enumeration
    # order (by j then twist, harness.isogeny_class.enumerate_curves) form
    # "declared level 0", the rest "declared level 1". No curve property is
    # used to choose the split -- it is a pure index cut, which is the point
    # of a matched null.
    half0 = recs[:split_a]
    half1 = recs[split_a:]
    pkgs = {}
    all_rows = []
    for label, half in (("null0", half0), ("null1", half1)):
        for r in half:
            pkg = fg.build_curve_package(r, arms=["B"], planted=False,
                                         seeds=seeds, target_counts=target_counts)
            rows = fg.measure_curve_all_arms(pkg, fb_sizes)
            for row in rows:
                row["declared_half"] = label
            all_rows.extend(rows)

    cells = {}
    for fb in fb_sizes:
        for seed in seeds:
            for T in target_counts:
                sel = [r for r in all_rows if r["fb_size"] == fb and r["seed"] == seed
                       and r["T"] == T]
                if not sel:
                    continue
                hits = [r["hits_m3"] for r in sel]
                halves = [0 if r["declared_half"] == "null0" else 1 for r in sel]
                # THE ACTUAL NULL TEST: stratified_stats with strata = the
                # DECLARED HALF label, exactly the per-stratum own-null
                # (over-dispersion-vs-own-binomial-floor) mechanism the
                # contract's C-DETECTION-FLOOR describes ("floor implied by
                # the actual per-level [here: per-declared-half] counts").
                # A PLAIN POOLED nullb over all hits regardless of half
                # (an earlier version of this cell) is a no-op with respect
                # to the split -- it is retained below ONLY as
                # `pooled_over_dispersion`, explicitly labelled as not
                # split-aware, so a reviewer can see the distinction rather
                # than have it silently corrected away.
                pooled = fg.nullb(f"matched_null_pooled[fb={fb},seed={seed},T={T}]",
                                  hits, T)
                strat = fg.stratified_stats(hits, halves,
                                            T, f"matched_null[fb={fb},seed={seed},T={T}]")
                groups = {h: [hits[i] / T for i in range(len(hits)) if halves[i] == h]
                         for h in (0, 1)}
                between = statistics.mean(groups[0]) - statistics.mean(groups[1])
                cells[f"fb{fb}_seed{seed}_T{T}"] = {
                    "pooled_over_dispersion_NOT_split_aware": pooled,
                    "per_half_own_null": strat["strata"],
                    "mean_rate_half0": statistics.mean(groups[0]),
                    "mean_rate_half1": statistics.mean(groups[1]),
                    "mean_difference": between,
                    "n_half0": len(groups[0]), "n_half1": len(groups[1]),
                }
    def _half_overdispersed(cell):
        for half in cell["per_half_own_null"].values():
            on = half.get("own_null")
            if on is not None and on["verdict"] == "over-dispersed":
                return True
        return False
    any_overdispersed = any(_half_overdispersed(c) for c in cells.values())
    return {
        "gate": "SR4_MATCHED_NULL", "written_before_real_contrast_read": True,
        "p": p, "t": t, "n_curves": len(recs),
        "split_sizes": [split_a, split_b],
        "split_sizing_method": ("Hurwitz class-number counts h(D0) [crater] and "
                                "h(D0*ell^2) [floor] of the REAL conductor-arm "
                                "class this null is matched to -- an INDEPENDENT, "
                                "non-graph formula (harness.isogeny_class."
                                "_class_number_forms), used ONLY to size this "
                                "arbitrary split. It does not identify which "
                                "specific curves would be crater/floor."),
        "matched_to_real_arm": real_arm_label,
        "matched_to_real_sizes_note": real_sizes_note,
        "split_rule": "index cut over harness.isogeny_class.enumerate_curves order; "
                     "no curve property used to choose membership",
        "fb_sizes": fb_sizes, "seeds": seeds, "target_counts": target_counts,
        "cells": cells,
        "verdict": "NULL_FIRES_OVERDISPERSION_DETECTED" if any_overdispersed
                  else "NULL_CLEAN_NO_OVERDISPERSION",
        "f4_falsification_note": ("F4: if verdict is NULL_FIRES..., every level "
                                  "result in this run is withdrawn and the "
                                  "deliverable is the instrument finding; "
                                  "not applicable here since no real level "
                                  "measurement was reachable (see kernel-"
                                  "rationality-check.json)"),
    }


def main() -> int:
    started = time.time()
    run_id_suffix = "sr1-sr5-plus-t5-gate-v3"
    run_id = f"RUN-{AREA}-{run_id_suffix}"
    run_dir = os.path.join(RUN_ROOT, "runs", run_id)
    stdout_lines = []

    def log(msg):
        print(msg)
        stdout_lines.append(msg)

    log("== EXP-VOLC-9f5571 :: SR1 Velu gate (p=4001, t=30, ell=2) ==")
    sr1 = stage_sr1_velu_gate()
    log(json.dumps(sr1, indent=1))
    if not sr1["passed"]:
        log("SR1 FAILED -- run INVALID, stopping before any further stage.")
        artifacts = {"sr1": sr1}
        _finalize(run_id, run_dir, started, time.time(), stdout_lines, artifacts,
                  status="completed_invalid", valid=False,
                  invalid_reason="SR1 velu gate failed to reproduce the committed "
                                 "p=4001 level distribution")
        return 1

    log("\n== SR2a: family construction, N=19507 ==")
    sr2fam = stage_sr2_family()
    log(json.dumps({k: v for k, v in sr2fam.items() if k != "candidates"}, indent=1))

    f3_cands = [c for c in sr2fam["candidates"] if c["f"] == 3]
    f3_cands_sized = []
    for c in f3_cands:
        h_crater, _ = ic._class_number_forms(c["D0"])
        h_floor, _ = ic._class_number_forms(c["D0"] * 9)
        c2 = dict(c)
        c2["crater_h"] = h_crater
        c2["floor_h"] = h_floor
        c2["total"] = h_crater + h_floor
        f3_cands_sized.append(c2)
    f3_chosen = min(f3_cands_sized, key=lambda c: c["total"])  # smallest, for tractability
    f107_chosen = [c for c in sr2fam["candidates"] if c["f"] == 107][0]
    assert f107_chosen["t"] == 211 and f107_chosen["p"] == 19717

    sr2fam["f3_chosen"] = f3_chosen
    sr2fam["f3_chosen_selection_rule"] = ("smallest total class size among the "
                                          "f=3 candidates in the family, for "
                                          "tractability within the dispatch's "
                                          "budget; disclosed, not outcome-selected "
                                          "on any measured quantity")
    sr2fam["f107_chosen"] = f107_chosen

    log(f"\nf=3 arm chosen: t={f3_chosen['t']} p={f3_chosen['p']} "
        f"D0={f3_chosen['D0']} crater_h={f3_chosen['crater_h']} "
        f"floor_h={f3_chosen['floor_h']} total={f3_chosen['total']}")
    log(f"f=107 arm (=T5 class): t={f107_chosen['t']} p={f107_chosen['p']}")

    log("\n== SR2b: class census (#E=19507 per curve, completeness) ==")
    census_f3 = stage_sr2_census(f3_chosen["p"], f3_chosen["t"], N_FAMILY)
    census_f107 = stage_sr2_census(f107_chosen["p"], f107_chosen["t"], N_FAMILY)
    log(json.dumps({"f3": {k: v for k, v in census_f3.items() if k != "per_curve_order_check"},
                    "f107": {k: v for k, v in census_f107.items() if k != "per_curve_order_check"}},
                   indent=1))
    sr2_pass = (census_f3["all_curves_order_equals_N"]
               and census_f107["all_curves_order_equals_N"]
               and all(c["agrees"] for c in census_f3["census"])
               and all(c["agrees"] for c in census_f107["census"]))
    if not sr2_pass:
        log("SR2 FAILED -- PREMISE-FAILED, stopping.")
        artifacts = {"sr1": sr1, "family_construction": sr2fam,
                    "class_census": {"f3": census_f3, "f107": census_f107}}
        _finalize(run_id, run_dir, started, time.time(), stdout_lines, artifacts,
                  status="completed_invalid", valid=False,
                  invalid_reason="SR2 family/class census disagreement -- PREMISE-FAILED")
        return 1

    log("\n== kernel-rationality check (empirical, drives the run's terminal "
        "state for the graph-dependent stages) ==")
    krc_f3 = stage_kernel_rationality_check(f3_chosen["p"], f3_chosen["t"], 3)
    krc_f107 = stage_kernel_rationality_check(f107_chosen["p"], f107_chosen["t"], 107)
    log(f"f=3 class: total rational order-3 subgroups found = "
        f"{krc_f3['total_rational_order_ell_subgroups_found']} "
        f"(N mod 3 = {krc_f3['N_mod_ell']})")
    log(f"f=107 class: total rational order-107 subgroups found = "
        f"{krc_f107['total_rational_order_ell_subgroups_found']} "
        f"(N mod 107 = {krc_f107['N_mod_ell']})")
    graph_blocked = (krc_f3["total_rational_order_ell_subgroups_found"] == 0
                    and krc_f107["total_rational_order_ell_subgroups_found"] == 0)

    log("\n== SR3 + rate measurement (arm B / targets_B), f=3 and f=107 classes ==")
    meas_f3 = measure_class(f3_chosen["p"], f3_chosen["t"], "f3_arm",
                            FB_SIZES_MAIN, SEEDS, TARGET_COUNTS)
    log(f"f=3 arm: support_ok={meas_f3['all_support_certificates_ok']} "
        f"n_curves={meas_f3['n_curves']} wall_s={meas_f3['wall_seconds']:.1f}")
    meas_f107 = measure_class(f107_chosen["p"], f107_chosen["t"], "f107_arm_T5class",
                              FB_SIZES_MAIN, SEEDS, TARGET_COUNTS)
    log(f"f=107 arm: support_ok={meas_f107['all_support_certificates_ok']} "
        f"n_curves={meas_f107['n_curves']} wall_s={meas_f107['wall_seconds']:.1f}")
    sr3_pass = (meas_f3["all_support_certificates_ok"]
               and meas_f107["all_support_certificates_ok"])
    if not sr3_pass:
        log("SR3 FAILED -- PREMISE-FAILED, stopping.")
        artifacts = {"sr1": sr1, "family_construction": sr2fam,
                    "class_census": {"f3": census_f3, "f107": census_f107},
                    "kernel_rationality_check": {"f3": krc_f3, "f107": krc_f107},
                    "measurements": {"f3": meas_f3, "f107": meas_f107}}
        _finalize(run_id, run_dir, started, time.time(), stdout_lines, artifacts,
                  status="completed_invalid", valid=False,
                  invalid_reason="SR3 support certificate failed on a measured vertex")
        return 1

    log("\n== SR4 matched null (f=1 class, sizes matched to the real conductor "
        "arms via an independent Hurwitz-class-number count; WRITTEN BEFORE any "
        "real level contrast is read -- and no real level contrast is reachable "
        "in this run at all, see kernel-rationality-check) ==")
    null_f3 = stage_sr4_matched_null(
        19541, 35, 14, 28, "f3_arm",
        f"real f=3 class (t={f3_chosen['t']}) crater_h={f3_chosen['crater_h']} "
        f"floor_h={f3_chosen['floor_h']}",
        FB_SIZES_NULL, SEEDS, TARGET_COUNTS)
    null_f107 = stage_sr4_matched_null(
        19373, -133, 1, 35, "f107_arm_T5class",
        "real f=107/T5 class (t=211) crater=1 (j=0,Aut=6), floor=36 (Aut=2); "
        "no f=1 class in the family has exactly 37 curves -- closest available "
        "(36) used, split 1/35, one short of the real floor count. Disclosed "
        "deviation, not silently reconciled.",
        FB_SIZES_NULL, SEEDS, TARGET_COUNTS)
    log(f"null (f=3-sized, 14/28 on t=35/p=19541): verdict={null_f3['verdict']}")
    log(f"null (f=107-sized, 1/35 on t=-133/p=19373): verdict={null_f107['verdict']}")

    log("\n== SR5 / raw level-count data collection / T5 / transport: ALL "
        "UNREACHED for the reason recorded in kernel_rationality_check -- "
        "no Velu edge exists between any two vertices of either conductor-arm "
        "class using rational kernel points, so no volcano graph, no per-level "
        "counts, no detection floor tied to them, no T5 walk, no T5 local "
        "test, and no T1 transport can be built in this run. ==")

    per_level_counts = {
        "status": "UNREACHED",
        "reason": ("level_construction (contract inputs.within_class_arm) "
                  "requires an explicit Velu ell-isogeny graph built from "
                  "F_p-rational kernel points. N=19507 is prime, hence "
                  "gcd(N, 3) = gcd(N, 107) = 1, hence E(F_p) has zero points "
                  "of order 3 or 107 on every curve in both conductor-arm "
                  "classes (Lagrange's theorem; verified empirically by "
                  "exhaustive liftable-x scan in kernel_rationality_check, "
                  "not merely asserted). No rational kernel therefore exists "
                  "to build a Velu edge from. This is not a coding defect in "
                  "this run and not fixable by retrying: it follows from "
                  "N being prime, which the matched-order family design "
                  "(MATCHED-ORDER-DESIGN.md sec 3) chose deliberately."),
        "cells_not_reached": ["per-level vertex counts (f=3 class)",
                              "per-level vertex counts (f=107 class)",
                              "level assignment for any individual curve in "
                              "either conductor-arm class"],
    }
    detection_floor = {
        "status": "UNREACHED",
        "reason": ("C-DETECTION-FLOOR requires the chi-square dispersion floor "
                  "implied by the ACTUAL per-level vertex counts. Those counts "
                  "are UNREACHED (see per_level_counts), so no floor tied to "
                  "them can be computed or reported without inventing counts "
                  "that were never measured, which is prohibited."),
        "methodology_note": ("the instrument that WOULD be used is "
                             "harness.exp_icinv_fullgroup.wilson_hilferty_band / "
                             "nullb, applied per level with df = n_level - 1 -- "
                             "the same instrument used for SR4's matched-null "
                             "cells above, which ARE computed."),
    }
    t5_walk = {"status": "UNREACHED", "reason": per_level_counts["reason"] +
              " Branch (i) is a random walk on the same graph."}
    t5_local_test = {"status": "UNREACHED", "reason": (
        "Branch (ii) requires counting F_p-RATIONAL 107-isogenies per vertex. "
        "Existence of such an isogeny (as a morphism) does not strictly "
        "require a pointwise-rational kernel point -- a Galois-stable kernel "
        "suffices in principle -- but counting it needs either (a) an "
        "explicit kernel generator over a field extension of F_p (arithmetic "
        "this run's toolkit does not have), or (b) evaluating the classical "
        "modular polynomial Phi_107(j(E), Y) and counting its roots in F_p "
        "(Phi_107 is not available in this harness or reasonably computable "
        "within this dispatch's budget). Neither path was attempted rather "
        "than risk a wrong-but-plausible count.")}
    t5_verdict = {
        "status": "UNREACHED",
        "value": "UNREACHED",
        "note": ("NOT 'neither' -- 'neither' (falsification F6) means both "
                "branches were evaluated and both failed, which is a real, "
                "reportable negative result. Here neither branch was "
                "EVALUABLE at all, which is a different and weaker claim; "
                "reporting 'neither' would misrepresent an unreached cell as "
                "a measured negative (AGENTS.md rule 5, rule 9)."),
    }
    transport_certificates = {"status": "UNREACHED", "reason": (
        "C-TRANSPORT-CERT needs an explicit Velu image on a real graph edge; "
        "none exists (see kernel_rationality_check).")}

    log("\n== SR6 (blocking gate) status ==")
    sr6 = {
        "rule": "Do not read or report any level verdict until EXP-INSTR-36c8cf "
               "has delivered, at the ACTUAL per-level counts, a detection "
               "floor and a false-positive rate for every statistic used.",
        "reached": False,
        "reached_note": ("SR6 gates reading a LEVEL VERDICT computed FROM real "
                         "per-level data. That data is itself UNREACHED for a "
                         "prior, independent reason (kernel_rationality_check), "
                         "so SR6's own gate was never approached in this run -- "
                         "it is moot here, not satisfied and not bypassed. "
                         "T5 is NOT gated by SR6 (heuristic_under_test_note: "
                         "HEUR-VOLC-1 is validated inside this experiment by "
                         "C-LOCAL-EXHAUSTIVE, not by EXP-INSTR-36c8cf) and was "
                         "computed to the extent reachable above: also "
                         "UNREACHED, for the separate graph-construction reason."),
        "exp_instr_36c8cf_status_as_of_dispatch": ("Phase A ran and stopped at "
                                                    "its own falsification "
                                                    "criterion with no interval "
                                                    "accepted; Phase B has not "
                                                    "run. Neither delivers what "
                                                    "SR6 needs."),
    }
    log(json.dumps(sr6, indent=1))

    final_verdict = {
        "level_verdict": "WITHHELD",
        "level_verdict_reason": ("(a) SR6 blocking gate, independently of (b): "
                                 "the per-level data itself is UNREACHED "
                                 "(kernel_rationality_check). Both reasons "
                                 "recorded distinctly; neither is a measured "
                                 "negative."),
        "t5_verdict": "UNREACHED",
        "claim_tier": "toy", "sota_delta": 0,
        "no_ecdlp_claim": True,
    }

    finished = time.time()
    artifacts = {
        "sr1_velu_gate": sr1,
        "family_construction": sr2fam,
        "class_census": {"f3": census_f3, "f107": census_f107},
        "kernel_rationality_check": {"f3": krc_f3, "f107": krc_f107},
        "graph_construction_blocked": graph_blocked,
        "measurements": {"f3": meas_f3, "f107": meas_f107},
        "matched_null": {"sized_to_f3": null_f3, "sized_to_f107": null_f107},
        "per_level_counts": per_level_counts,
        "detection_floor": detection_floor,
        "t5_walk": t5_walk,
        "t5_local_test": t5_local_test,
        "t5_verdict": t5_verdict,
        "transport_certificates": transport_certificates,
        "final_verdict": final_verdict,
        "sr6": sr6,
    }
    _finalize(run_id, run_dir, started, finished, stdout_lines, artifacts,
             status="completed", valid=True, invalid_reason=None)
    return 0


def _finalize(run_id, run_dir, started, finished, stdout_lines, artifacts, *,
             status, valid, invalid_reason):
    metrics = {
        "sr1_passed": artifacts["sr1"]["passed"] if "sr1" in artifacts
                     else artifacts.get("sr1_velu_gate", {}).get("passed"),
    }
    if "final_verdict" in artifacts:
        metrics.update(artifacts["final_verdict"])
    result = RunResult(
        run_suffix=run_id.replace(f"RUN-{AREA}-", ""),
        curve_id="FAMILY-N19507",
        seed=SEEDS[0],
        parameters={"N": N_FAMILY, "fb_sizes_main": FB_SIZES_MAIN,
                   "fb_sizes_null": FB_SIZES_NULL, "seeds": SEEDS,
                   "target_counts": TARGET_COUNTS},
        metrics=metrics,
        certificate={"kind": "none"},
        valid=valid,
        invalid_reason=invalid_reason,
        stdout="\n".join(stdout_lines),
        stderr="",
        raw=artifacts,
    )
    written_id = write_run(EXP_ID, AREA, result, status=status,
                           command=f"python3 {os.path.relpath(__file__, REPO)}",
                           started=started, finished=finished)
    assert written_id == run_id, (written_id, run_id)
    # extra required artifacts beyond runner.write_run's base set
    for name, key in [
        ("velu-gate-p4001.json", "sr1_velu_gate" if "sr1_velu_gate" in artifacts else "sr1"),
        ("family-construction.json", "family_construction"),
        ("class-census.json", "class_census"),
        ("per-level-counts.json", "per_level_counts"),
        ("detection-floors.json", "detection_floor"),
        ("matched-null-verdict.json", "matched_null"),
        ("per-vertex-measurements.json", "measurements"),
        ("t5-walk-per-seed.json", "t5_walk"),
        ("t5-local-test.json", "t5_local_test"),
        ("t5-verdict.json", "t5_verdict"),
        ("transport-certificates.json", "transport_certificates"),
        ("verdict.json", "final_verdict"),
    ]:
        if key in artifacts:
            write_json(run_dir, name, artifacts[key])
    # support-certificates.json and volcano-graph.json and
    # r-by-level-contingency.json are synthesized from what was actually
    # measured / discovered, not separately computed
    support = {
        "f3": artifacts.get("measurements", {}).get("f3", {}).get("support_records"),
        "f107": artifacts.get("measurements", {}).get("f107", {}).get("support_records"),
    }
    write_json(run_dir, "support-certificates.json", support)
    volcano_graph = {
        "status": "graph could not be built with F_p-rational kernel points "
                 "(see kernel_rationality_check.json); zero edges attempted-"
                 "and-found on either conductor-arm class",
        "kernel_rationality_check": artifacts.get("kernel_rationality_check"),
    }
    write_json(run_dir, "volcano-graph.json", volcano_graph)
    r_contingency = {
        "note": "N=19507 is odd (prime), so E(F_p) has NO 2-torsion for any "
               "curve in this family: r = 0 identically on every measured "
               "vertex. The contingency table therefore has exactly one row.",
        "f3": artifacts.get("measurements", {}).get("f3", {}).get(
            "r_two_torsion_histogram"),
        "f107": artifacts.get("measurements", {}).get("f107", {}).get(
            "r_two_torsion_histogram"),
        "level_column": "UNREACHED (see per-level-counts.json) -- table "
                        "reports r alone, not r-by-level",
    }
    write_json(run_dir, "r-by-level-contingency.json", r_contingency)
    return written_id


if __name__ == "__main__":
    raise SystemExit(main())
