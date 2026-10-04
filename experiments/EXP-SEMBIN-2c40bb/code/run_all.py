#!/usr/bin/env python3
"""EXP-SEMBIN-2c40bb / RUN-SEMBIN-3ae91c orchestrator.

Arms in the frozen order R, N, S, B, F, I. Every arm's JSON is written to the run
directory the moment the arm finishes. Arm outputs carry NO timestamps so that two
executions can be diffed byte for byte; timestamps live only in manifest.yaml,
stdout.log and artifact-digests.json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
import os
import resource
import subprocess
import sys
import time

import surface_cost as S
import sparse_independent as SI

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PARENT_RECORD = os.path.join(
    REPO, "experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml")
RECOMP = os.path.join(
    REPO, "coordination/review/sembin-20260913-9d649f/red-team-cf9d98/recomputations.json")
TABLES = os.path.join(REPO, "inputs/SEMAEV-2015-310/tables.yaml")
KR_U, KR_C = S.K_READINGS
RECORD_MODE = "record_point_M1_w30"
GATE_TOL_BITS = 4.8e-5


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean(o):
    if isinstance(o, float):
        if math.isinf(o):
            return "+inf" if o > 0 else "-inf"
        if math.isnan(o):
            return "nan"
        return o
    if isinstance(o, dict):
        return {str(k) if not isinstance(k, (str, int)) else k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def dump(path, obj):
    with open(path, "w") as fh:
        json.dump(_clean(obj), fh, indent=1, sort_keys=False, allow_nan=False)
        fh.write("\n")


def _json_default(o):
    if isinstance(o, float):
        if math.isinf(o):
            return "inf" if o > 0 else "-inf"
    raise TypeError(repr(o))


def finite(x):
    if x is None:
        return None
    if isinstance(x, float) and math.isinf(x):
        return "+inf" if x > 0 else "-inf"
    return x


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Log:
    def __init__(self, out_dir):
        self.f = open(os.path.join(out_dir, "stdout.log"), "a")

    def __call__(self, msg):
        line = f"[{now()}] {msg}"
        print(line)
        self.f.write(line + "\n")
        self.f.flush()


# ============================================================================ ARM R

def arm_r(tab, out_dir, log):
    import yaml
    rec = yaml.safe_load(open(PARENT_RECORD))["concrete_cost"]
    recomp = json.load(open(RECOMP))["step0_reproduction_of_the_record"]
    kr = KR_U
    st_map = {"dense": "dense_row_echelon", "semaev_sparse": "semaev_sparse",
              "sparse": "semaev_sparse"}
    parent_metrics = {"time_only_zero_memory_weight": ("time_only", None),
                      "time_memory_product": ("time_memory_product", None),
                      "area_time_AT": ("time_memory_product", None),
                      "equal_rate_max_of_time_and_memory": "max"}
    # crossovers in the parent's own window [250, 650]
    cross = {}
    for pm, inst in parent_metrics.items():
        cross[pm] = {}
        for rs, st in (("dense", "dense_row_echelon"), ("semaev_sparse", "semaev_sparse")):
            if inst == "max":
                sem = {}
                for n in tab.ns:
                    m = tab.argmin_m[kr][n]
                    T, M = tab.semaev_point(n, m, st, kr)
                    sem[n] = (max(T, M), m, T, M)
                base = {}
                for n in tab.ns:
                    T, M = S.vow_point(n, RECORD_MODE, 30, 0)
                    base[n] = (max(T, M), T, M)
            else:
                sem = S.semaev_curve(tab, inst, st, kr, 0, "stage1_argmin")
                base = S.baseline_curve(inst, RECORD_MODE, 30, 0)
            c = S.compare_curves(sem, base)
            got = c["crossover_n_parent_window_250_650"]
            want = rec["crossover_n_by_metric"][pm][rs]
            cross[pm][rs] = {"recomputed": got, "record": want, "agrees": got == want}
    # margins at the five parameter sets
    per_n, worst_rec, worst_rt = [], 0.0, 0.0
    gate_m_mismatch = []
    rt_by_n = {r["n"]: r for r in recomp["per_n"]}
    for ps in rec["parameter_sets"]:
        n = int(str(ps["security_parameter"]).split("=")[-1].strip())
        m = tab.argmin_m[kr][n]
        T, _ = tab.semaev_point(n, m, "dense_row_echelon", kr)
        _, Md = tab.semaev_point(n, m, "dense_row_echelon", kr)
        _, Ms = tab.semaev_point(n, m, "semaev_sparse", kr)
        Tv, Mv = S.vow_point(n, RECORD_MODE, 30, 0)
        vals = {"t": T, "d": Md, "s": Ms, "v": Tv, "mt": Tv - T,
                "md": (Tv + Mv) - (T + Md), "ms": (Tv + Mv) - (T + Ms), "m": m}
        rec_vals = {"mt": ps["margin_bits_time_only"],
                    "md": ps["margin_bits_time_memory_dense"],
                    "ms": ps["margin_bits_time_memory_sparse"],
                    "t": ps["semaev_time_log2"], "d": ps["semaev_memory_log2_dense"],
                    "s": ps["semaev_memory_log2_sparse"], "v": ps["vow_time_log2"]}
        if ps["semaev_optimal_m"] != m:
            gate_m_mismatch.append(n)
        row = {"n": n, "m": m, "recomputed_here": {k: round(v, 6) for k, v in vals.items()},
               "record_values": rec_vals, "diff_vs_record_bits": {},
               "red_team_recomputed": rt_by_n.get(n, {}).get("recomputed"),
               "diff_vs_red_team_bits": {}}
        for k, v in rec_vals.items():
            d = vals[k] - v
            row["diff_vs_record_bits"][k] = round(d, 6)
            worst_rec = max(worst_rec, abs(d))
        if n in rt_by_n:
            for k, v in rt_by_n[n]["recomputed"].items():
                if k == "m":
                    row["diff_vs_red_team_bits"]["m_agrees"] = (v == m)
                    continue
                d = vals[k] - v
                row["diff_vs_red_team_bits"][k] = round(d, 6)
                worst_rt = max(worst_rt, abs(d))
        per_n.append(row)
    m409 = next(r for r in per_n if r["n"] == 409)
    gate_cross = all(v["agrees"] for pm in cross.values() for v in pm.values())
    gate_margins = (all(abs(m409["diff_vs_record_bits"][k]) < 5e-5 for k in ("mt", "md", "ms"))
                    and not gate_m_mismatch)
    gate_rt = worst_rt <= GATE_TOL_BITS + 5e-5   # their per_n values are printed to 4 dp
    out = {
        "arm": "R", "cell": {"store_log2": 30, "processors_log2": 0, "kappa": 1,
                             "cofactor_h": 1, "degree_bound": 4, "omega": 3.0,
                             "k_reading_time": kr, "k_reading_memory": KR_C,
                             "baseline_charging_mode": RECORD_MODE,
                             "m_selection": "stage1_argmin",
                             "scan_window_for_crossover": list(S.PARENT_WINDOW)},
        "crossovers": cross,
        "crossovers_red_team": recomp["crossovers_recomputed"],
        "margins_per_parameter_set": per_n,
        "n409": {"time_only": m409["recomputed_here"]["mt"],
                 "product_dense": m409["recomputed_here"]["md"],
                 "product_sparse": m409["recomputed_here"]["ms"]},
        "largest_disagreement_vs_record_bits": worst_rec,
        "largest_disagreement_vs_red_team_recomputations_bits": worst_rt,
        "red_team_stated_worst_vs_record_bits": recomp["worst_absolute_disagreement_bits"],
        "note_on_red_team_comparison": (
            "recomputations.json is read as DATA and compared cell by cell; it is NOT "
            "imported and agreement with it is a comparison against this experiment's own "
            "input, not independent corroboration (specification independence_note). Its "
            "per_n values are printed to 4 decimals, so a disagreement below 5e-5 bits is "
            "at its printing precision."),
        "gate": {"crossovers_exact": gate_cross, "margins_409_exact_to_4dp": gate_margins,
                 "within_red_team_tolerance": gate_rt,
                 "passed": gate_cross and gate_margins and gate_rt},
    }
    dump(os.path.join(out_dir, "reproduction-gate.json"), out)
    log(f"ARM R gate passed={out['gate']['passed']} worst_vs_record={worst_rec:.2e} "
        f"worst_vs_red_team={worst_rt:.2e}")
    return out


# ============================================================================ ARM N

def arm_n(out_dir, log):
    spec_path = "experiments/EXP-ICEX-c32447/specification.yaml"
    out = {
        "arm": "N", "control": "C6 prime_field_nearby_object",
        "status": "UNREACHED",
        "model_named_by_contract": spec_path,
        "what_was_attempted": (
            "Read EXP-ICEX-c32447's specification to extract a closed-form prime-field "
            "index-calculus cost model (time and memory as functions of N, B, m, kappa) "
            "and a multi-target rho baseline with a shared distinguished-point table, to "
            "be charged under this experiment's store grid and coherent-baseline modes."),
        "concrete_missing_pieces": [
            {"piece": "C_LA (linear algebra) and C_descent (per-target) counters",
             "why_missing": ("EXP-ICEX-c32447 defines them as MEASURED group-operation "
                             "counters read off an instrumented exhaustive solver at "
                             "N in [2^20, 2^30]; the specification states no closed form "
                             "for either, and the experiment is status draft with no "
                             "runs, so no measured values exist to charge.")},
            {"piece": "index-calculus memory",
             "why_missing": ("declared as a measured 'peak stored elements' counter "
                             "(factor base N^beta plus relation matrix), not as a formula; "
                             "inventing one here would be a fabricated comparator.")},
            {"piece": "multi-target rho arm with shared distinguished-point table",
             "why_missing": ("a MEASURED baseline on shared instances at T in {1,4,16,64}; "
                             "no run exists.")},
            {"piece": "extrapolation to cryptographic size",
             "why_missing": ("ICEX's model is stated for N <= 2^30 and declares no "
                             "transfer to the 2^256 scale at which C6 asks for a verdict; "
                             "the only closed-form term it states, the shared cost "
                             "m! N B^(m-1)(sigma-1) -> m! N at sigma = 1, carries no memory "
                             "term and no B dependence, so charging it under the store "
                             "grid would test nothing about memory charging.")},
        ],
        "not_substituted": (
            "The red team's J6 located a DIFFERENT prime-field cost model "
            "(experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml, conditional "
            "on HEUR-001 at a 0.05 prior). It is not EXP-ICEX-c32447's model, and the "
            "stopping rule forbids counting a same-family substitute as this control. "
            "It is therefore NOT instantiated here; a Coordinator amendment naming it as "
            "the control model would be needed first."),
        "impediment_for_coordinator": {
            "what_is_blocked": "control C6 of EXP-SEMBIN-2c40bb (and the owed prime-field control of RUN-SEMBIN-121b59)",
            "clears_when": ("either EXP-ICEX-c32447 has completed runs supplying C_rel, C_LA, "
                            "C_descent and peak-stored-element counters, or an amendment "
                            "names a closed-form prime-field model as the C6 comparator"),
            "recheck": "ls experiments/EXP-ICEX-c32447/runs/ ; read the amendment record",
            "asserts_nothing_about": "the science; UNREACHED is not a pass and not a fail",
        },
        "consequence": ("Every row of ARM S/B/F below is reported WITHOUT the prime-field "
                        "control having been run. The parent's substituted eq.(4) control "
                        "is retained only as the C5 typo detector."),
    }
    dump(os.path.join(out_dir, "arm-n-prime-field-control.json"), out)
    log("ARM N: UNREACHED, impediment recorded")
    return out


# ============================================================================ ARM S

CELL_FIELDS = ["metric", "store_log2", "processors_log2", "baseline_charging_mode", "kappa",
               "cofactor_h", "storage_reading", "k_reading", "m_selection",
               "first_crossing_n", "persistent_crossover_n",
               "crossover_n_parent_window_250_650", "monotone_after_first_crossing",
               "semaev_cheaper_intervals", "margin_409_bits", "margin_571_bits",
               "m_at_409", "m_at_571"]


def arm_s(tab, out_dir, log):
    insts = S.metric_instances()
    sem_cache, base_cache = {}, {}
    rows = []
    t0 = time.time()
    count = 0
    for inst in insts:
        lab = S.metric_label(inst)
        for st, kr, msel, p in itertools.product(S.STORAGES, S.K_READINGS, S.M_SELECTIONS,
                                                 S.PROC_GRID):
            key = (lab, st, kr, msel, p)
            sem1 = S.semaev_curve(tab, inst, st, kr, p, msel, 1)
            for kappa in S.KAPPA_GRID:
                shift = math.log2(kappa)
                sem = sem1 if kappa == 1 else {
                    n: (c - shift if c != S.INF else S.INF, m, T - shift, M)
                    for n, (c, m, T, M) in sem1.items()}
                for mode, s, h in itertools.product(S.MODES, S.STORE_GRID, S.COFACTOR_GRID):
                    bkey = (lab, mode, s, p, h)
                    base = base_cache.get(bkey)
                    if base is None:
                        base = S.baseline_curve(inst, mode, s, p, h)
                        base_cache[bkey] = base
                    c = S.compare_curves(sem, base)
                    rows.append([lab, s, p, mode, kappa, h, st, kr, msel,
                                 c["first_crossing_n"], c["persistent_crossover_n"],
                                 c["crossover_n_parent_window_250_650"],
                                 c["monotone_after_first_crossing"],
                                 c["semaev_cheaper_intervals"], c["margin_409_bits"],
                                 c["margin_571_bits"], c["m_at_409"], c["m_at_571"]])
                    count += 1
        log(f"ARM S metric {lab}: {count} cells so far, {time.time() - t0:.1f}s")
    raw = {"experiment_id": "EXP-SEMBIN-2c40bb", "run_id": "RUN-SEMBIN-3ae91c", "arm": "S",
           "scan_domain_n": [S.N_LO, S.N_HI], "m_range": [2, S.M_HI],
           "fixed_in_this_surface": {"degree_bound": tab.degree, "omega": tab.omega,
                                     "omega_prime": 2.0, "curve_label": "none (generic n; "
                                     "curve labels are a separate sensitivity table)"},
           "crossover_definitions": {
               "first_crossing_n": "smallest n in [3,700] where Semaev is strictly cheaper",
               "persistent_crossover_n": "smallest n such that Semaev is cheaper for every n' >= n up to 700 (null if not cheaper at 700)",
               "crossover_n_parent_window_250_650": "the parent's definition: first win in [250,650]",
               "semaev_cheaper_intervals": "the cheaper set as closed intervals over [3,700]",
               "margins": "baseline_metric_cost - semaev_metric_cost in bits; 'semaev_infeasible' where Semaev exceeds a hard budget at every m",
           },
           "encoding": {"metric": "index into codes.metric", "baseline_charging_mode": "index into codes.baseline_charging_mode",
                        "storage_reading": "index into codes.storage_reading", "k_reading": "index into codes.k_reading",
                        "m_selection": "index into codes.m_selection", "other fields": "literal"},
           "codes": {"metric": [S.metric_label(i) for i in insts], "baseline_charging_mode": S.MODES,
                     "storage_reading": S.STORAGES, "k_reading": S.K_READINGS, "m_selection": S.M_SELECTIONS},
           "cell_fields": CELL_FIELDS, "cell_count": len(rows), "cells": None}
    codes = raw["codes"]
    enc = []
    for r in rows:
        enc.append([codes["metric"].index(r[0]), r[1], r[2], codes["baseline_charging_mode"].index(r[3]), r[4], r[5],
                    codes["storage_reading"].index(r[6]), codes["k_reading"].index(r[7]),
                    codes["m_selection"].index(r[8])] + r[9:])
    with open(os.path.join(out_dir, "raw-result.json"), "w") as fh:
        head = dict(raw)
        head.pop("cells")
        fh.write(json.dumps(_clean(head), indent=1)[:-2] + ',\n "cells": [\n')
        for i, r in enumerate(enc):
            fh.write(json.dumps(_clean(r), separators=(",", ":")) + (",\n" if i + 1 < len(enc) else "\n"))
        fh.write(" ]\n}\n")
    log(f"ARM S: {len(rows)} cells written to raw-result.json in {time.time() - t0:.1f}s")
    return rows


def index_rows(rows):
    idx = {}
    for r in rows:
        idx[tuple(r[:9])] = r
    return idx


def rng(values):
    vals = [v for v in values if v is not None]
    return {"min": min(vals) if vals else None, "max": max(vals) if vals else None,
            "range": (max(vals) - min(vals)) if vals else None,
            "cells_with_no_crossover_in_domain": sum(1 for v in values if v is None),
            "values": values}


def surface_summary(rows, out_dir, log):
    idx = index_rows(rows)
    base_lab = dict(kappa=1, h=1, p=0, msel="stage1_argmin")

    def get(metric, s, p, mode, kappa, h, st, kr, msel, field):
        r = idx[(metric, s, p, mode, kappa, h, st, kr, msel)]
        return r[CELL_FIELDS.index(field)]

    families_at_store30 = [S.metric_label(i) for i in S.metric_instances()]
    parent_metric_set = ["time_only", "time_memory_product"]
    ranges = {}
    for st in S.STORAGES:
        ranges[st] = {}
        for kr in S.K_READINGS:
            ranges[st][kr] = {}
            for msel in S.M_SELECTIONS:
                for field in ("persistent_crossover_n", "crossover_n_parent_window_250_650"):
                    e = {}
                    e["over_store_declared_grid_30_40_48_60_product_metric"] = rng(
                        [get("time_memory_product", s, 0, RECORD_MODE, 1, 1, st, kr, msel, field)
                         for s in (30, 40, 48, 60)])
                    e["over_store_full_grid_product_metric"] = rng(
                        [get("time_memory_product", s, 0, RECORD_MODE, 1, 1, st, kr, msel, field)
                         for s in S.STORE_GRID])
                    e["over_parent_metric_set_time_only_and_product_at_store30"] = rng(
                        [get(mt, 30, 0, RECORD_MODE, 1, 1, st, kr, msel, field)
                         for mt in parent_metric_set])
                    e["over_full_metric_set_28_instances_at_store30"] = rng(
                        [get(mt, 30, 0, RECORD_MODE, 1, 1, st, kr, msel, field)
                         for mt in families_at_store30])
                    e["over_processors_product_metric_store30"] = rng(
                        [get("time_memory_product", 30, p, RECORD_MODE, 1, 1, st, kr, msel, field)
                         for p in S.PROC_GRID])
                    e["over_baseline_mode_product_metric_store30"] = rng(
                        [get("time_memory_product", 30, 0, mode, 1, 1, st, kr, msel, field)
                         for mode in S.MODES])
                    e["over_kappa_product_metric_store30"] = rng(
                        [get("time_memory_product", 30, 0, RECORD_MODE, k, 1, st, kr, msel, field)
                         for k in S.KAPPA_GRID])
                    e["over_cofactor_product_metric_store30"] = rng(
                        [get("time_memory_product", 30, 0, RECORD_MODE, 1, h, st, kr, msel, field)
                         for h in S.COFACTOR_GRID])
                    e["over_kappa_time_only"] = rng(
                        [get("time_only", 30, 0, RECORD_MODE, k, 1, st, kr, msel, field)
                         for k in S.KAPPA_GRID])
                    e["store_range_exceeds_metric_range_declared_grid_vs_parent_metric_set"] = (
                        None if (e["over_store_declared_grid_30_40_48_60_product_metric"]["range"] is None
                                 or e["over_parent_metric_set_time_only_and_product_at_store30"]["range"] is None)
                        else e["over_store_declared_grid_30_40_48_60_product_metric"]["range"]
                        > e["over_parent_metric_set_time_only_and_product_at_store30"]["range"])
                    ranges[st][kr][f"{msel}/{field}"] = e
    # two-parameter grids metric x store for re-plotting, at p=0, kappa=1, h=1
    grids = {}
    for st in S.STORAGES:
        grids[st] = {}
        for kr in S.K_READINGS:
            grids[st][kr] = {}
            for msel in S.M_SELECTIONS:
                grids[st][kr][msel] = {}
                for mode in S.MODES:
                    g = {"store_log2": S.STORE_GRID, "metrics": families_at_store30,
                         "persistent_crossover_n": [], "first_crossing_n": [],
                         "crossover_n_parent_window_250_650": [], "margin_409_bits": []}
                    for mt in families_at_store30:
                        for f in ("persistent_crossover_n", "first_crossing_n",
                                  "crossover_n_parent_window_250_650", "margin_409_bits"):
                            g[f].append([get(mt, s, 0, mode, 1, 1, st, kr, msel, f)
                                         for s in S.STORE_GRID])
                    g["cell_label_fixed"] = {"processors_log2": 0, "kappa": 1, "cofactor_h": 1,
                                             "baseline_charging_mode": mode,
                                             "storage_reading": st, "k_reading": kr,
                                             "m_selection": msel}
                    grids[st][kr][msel][mode] = g
    # collisions: same persistent crossover, same (metric, storage, kr, kappa, h, msel),
    # different (store, p, mode)
    groups = {}
    for r in rows:
        key = (r[0], r[6], r[7], r[4], r[5], r[8], r[10])
        groups.setdefault(key, []).append((r[1], r[2], r[3]))
    pairs, n_pairs = [], 0
    for key, cells in groups.items():
        if key[6] is None or len(cells) < 2:
            continue
        cells = sorted(set(cells))
        for a, b in itertools.combinations(cells, 2):
            n_pairs += 1
            if len(pairs) < 400 and key[3] == 1 and key[4] == 1 and key[5] == "stage1_argmin":
                reason = []
                if a[2] != b[2]:
                    reason.append("different baseline_charging_mode")
                if a[0] != b[0] and a[1] != b[1] and (a[0] - a[1]) == (b[0] - b[1]):
                    reason.append("store_log2 - processors_log2 equal (record mode product depends on the difference)")
                elif a[0] != b[0]:
                    reason.append("different store_log2 (baseline mode or metric ignores the store)")
                if a[1] != b[1] and "store_log2 - processors_log2" not in " ".join(reason):
                    reason.append("different processors_log2")
                pairs.append({"metric": key[0], "storage_reading": key[1], "k_reading": key[2],
                              "kappa": key[3], "cofactor_h": key[4], "m_selection": key[5],
                              "persistent_crossover_n": key[6],
                              "cell_a": {"store_log2": a[0], "processors_log2": a[1], "baseline_charging_mode": a[2]},
                              "cell_b": {"store_log2": b[0], "processors_log2": b[1], "baseline_charging_mode": b[2]},
                              "why_same_value": reason})
    collisions = {
        "definition": ("two grid cells sharing (metric, storage_reading, k_reading, kappa, "
                       "cofactor_h, m_selection) and the same persistent_crossover_n but "
                       "differing in (store_log2, processors_log2, baseline_charging_mode)"),
        "total_colliding_pairs": n_pairs,
        "structural_sources": [
            "time_only ignores store_log2 entirely, so all 7 stores collide per (mode, p)",
            "own_curve_product_minimum sets w = M and never reads store_log2, so all 7 stores collide",
            "sect113r2_calibrated_ratio sets w = M 2^13.3 and never reads store_log2, so all 7 stores collide",
            "record_point under time_memory_product depends on store_log2 - processors_log2 only where Semaev's working set dominates his relation store, so (40,20) collides with (20,0) and (60,20) with (40,0)",
            "fixed_budget metrics cap the baseline store at the budget, so stores above budget - log2(3n) collide",
        ],
        "examples_kappa1_h1_stage1_argmin": pairs,
    }
    out = {"arm": "S", "cell_label_fixed_in_grids": "see each grid's cell_label_fixed",
           "crossover_ranges": ranges, "metric_by_store_grids": grids, "collisions": collisions}
    dump(os.path.join(out_dir, "surface.json"), out)
    log("ARM S summary written to surface.json")
    return out


# ============================================================================ ARM B

def near_optimal_width(costs: dict, within=1.0):
    best = min(costs.values())
    ms = sorted(m for m, c in costs.items() if c <= best + within)
    return {"argmin_m": min(costs, key=costs.get), "within_1_bit_m": ms, "width": len(ms)}


def arm_b(tab, out_dir, log):
    kr_out = {}
    inst = ("time_memory_product", None)
    for kr in S.K_READINGS:
        per_st = {}
        for st in S.STORAGES:
            row = {"modes": {}}
            for msel in S.M_SELECTIONS:
                sem = S.semaev_curve(tab, inst, st, kr, 0, msel)
                for mode in S.MODES:
                    base = S.baseline_curve(inst, mode, 30, 0)
                    c = S.compare_curves(sem, base)
                    row["modes"][f"{mode}/{msel}"] = {
                        "cell": {"metric": "time_memory_product", "store_log2": 30,
                                 "processors_log2": 0, "baseline_charging_mode": mode,
                                 "kappa": 1, "cofactor_h": 1, "storage_reading": st,
                                 "k_reading": kr, "m_selection": msel},
                        "persistent_crossover_n": c["persistent_crossover_n"],
                        "first_crossing_n": c["first_crossing_n"],
                        "crossover_n_parent_window_250_650": c["crossover_n_parent_window_250_650"],
                        "margin_409_bits": c["margin_409_bits"], "margin_571_bits": c["margin_571_bits"],
                        "m_at_409": c["m_at_409"], "semaev_cheaper_intervals": c["semaev_cheaper_intervals"]}
            for msel in S.M_SELECTIONS:
                a = row["modes"][f"{RECORD_MODE}/{msel}"]
                b = row["modes"][f"own_curve_product_minimum/{msel}"]
                cc = row["modes"][f"sect113r2_calibrated_ratio/{msel}"]
                row[f"shift_record_to_own_curve/{msel}"] = {
                    "in_n_persistent": (None if a["persistent_crossover_n"] is None or b["persistent_crossover_n"] is None
                                        else b["persistent_crossover_n"] - a["persistent_crossover_n"]),
                    "in_n_parent_window": (None if a["crossover_n_parent_window_250_650"] is None or b["crossover_n_parent_window_250_650"] is None
                                           else b["crossover_n_parent_window_250_650"] - a["crossover_n_parent_window_250_650"]),
                    "in_bits_at_409": (None if not isinstance(a["margin_409_bits"], float) or not isinstance(b["margin_409_bits"], float)
                                       else round(b["margin_409_bits"] - a["margin_409_bits"], 4))}
                row[f"shift_record_to_sect113r2/{msel}"] = {
                    "in_n_persistent": (None if a["persistent_crossover_n"] is None or cc["persistent_crossover_n"] is None
                                        else cc["persistent_crossover_n"] - a["persistent_crossover_n"]),
                    "in_bits_at_409": (None if not isinstance(a["margin_409_bits"], float) or not isinstance(cc["margin_409_bits"], float)
                                       else round(cc["margin_409_bits"] - a["margin_409_bits"], 4))}
            per_st[st] = row
        kr_out[kr] = per_st
    # product excess per n and the pareto table at FIPS n
    excess, pareto = {}, {}
    for n in S.FIPS_N:
        Tr, Mr = S.vow_point(n, RECORD_MODE, 30, 0)
        To, Mo = S.vow_point(n, "own_curve_product_minimum", 30, 0)
        Ts, Ms = S.vow_point(n, "sect113r2_calibrated_ratio", 30, 0)
        excess[n] = {"record_product_log2": round(Tr + Mr, 4),
                     "own_curve_min_product_log2": round(To + Mo, 4),
                     "excess_bits": round((Tr + Mr) - (To + Mo), 4),
                     "sect113r2_product_log2": round(Ts + Ms, 4),
                     "sect113r2_excess_bits": round((Ts + Ms) - (To + Mo), 4)}
        pareto[n] = {}
        for kr in S.K_READINGS:
            for st in S.STORAGES:
                costs = {m: sum(tab.semaev_point(n, m, st, kr)) for m in tab.time[kr][n]}
                w = near_optimal_width(costs)
                m_arg = tab.argmin_m[kr][n]
                pareto[n][f"{st}/{kr}"] = {
                    "semaev_min_product_log2": round(costs[w["argmin_m"]], 4),
                    "m_attaining": w["argmin_m"], "m_within_1_bit": w["within_1_bit_m"],
                    "semaev_product_at_stage1_argmin_m": round(costs[m_arg], 4),
                    "stage1_argmin_m": m_arg,
                    "margin_vs_vow_min_product_bits": round((To + Mo) - costs[w["argmin_m"]], 4)}
    out = {"arm": "B", "per_k_reading": kr_out, "vow_product_excess_per_n": excess,
           "pareto_min_of_own_curves_at_fips_n": pareto,
           "heuristic_note": ("HEUR-VOW-CURVE: T = W(1/M + 1/w), Mem = 3n max(w, M); an "
                              "internal restatement (red team J2(b)) from KN-TECH-006 and "
                              "KN-LIT-012; UNVALIDATED; the primary van Oorschot-Wiener paper "
                              "has NOT been opened by any agent in this program.")}
    dump(os.path.join(out_dir, "arm-b-coherent-baseline.json"), out)
    log("ARM B written")
    return out


# ============================================================================ ARM F

def arm_f(tab, out_dir, log):
    res = {"arm": "F", "per_fips_n": {}, "budget_grid_verdicts": {}, "alpha_flip": {},
           "disagreement_bands": {}}
    for n in S.FIPS_N:
        res["per_fips_n"][n] = {}
        res["budget_grid_verdicts"][n] = {}
        res["alpha_flip"][n] = {}
        for kr in S.K_READINGS:
            for mode in S.MODES:
                Tv, Mv = S.vow_point(n, mode, 30, 0)
                for st in S.STORAGES:
                    key = f"{st}/{kr}/{mode}"
                    pts = {m: tab.semaev_point(n, m, st, kr) for m in tab.time[kr][n]}
                    mems = {m: M for m, (T, M) in pts.items()}
                    cheapest_m = min(mems, key=mems.get)
                    w_mem = near_optimal_width(mems)
                    # hard: verdict semaev iff exists m with Mem<=B and T<Tv; threshold
                    hard_candidates = [M for m, (T, M) in pts.items() if T < Tv]
                    hard_thr = min(hard_candidates) if hard_candidates else None
                    hard_thr_m = (min((m for m, (T, M) in pts.items() if T < Tv), key=lambda m: pts[m][1])
                                  if hard_candidates else None)
                    # soft: cost T + max(0, Mem-B) < Tv ; threshold B_m = T + Mem - Tv for T<Tv
                    soft_candidates = {m: T + M - Tv for m, (T, M) in pts.items() if T < Tv}
                    soft_thr = min(soft_candidates.values()) if soft_candidates else None
                    soft_thr_m = min(soft_candidates, key=soft_candidates.get) if soft_candidates else None
                    res["per_fips_n"][n][key] = {
                        "cell": {"store_log2": 30, "processors_log2": 0, "kappa": 1,
                                 "cofactor_h": 1, "baseline_charging_mode": mode,
                                 "storage_reading": st, "k_reading": kr,
                                 "m_selection": "metric_reoptimised (budget metrics re-choose m)"},
                        "vow_time_log2": round(Tv, 4), "vow_memory_log2_bits": round(Mv, 4),
                        "semaev_cheapest_memory_log2_bits": round(mems[cheapest_m], 4),
                        "m_attaining_cheapest_memory": cheapest_m,
                        "m_within_1_bit_of_cheapest_memory": w_mem["within_1_bit_m"],
                        "hard_budget_threshold_log2_bits": None if hard_thr is None else round(hard_thr, 4),
                        "hard_threshold_m": hard_thr_m,
                        "soft_budget_threshold_log2_bits": None if soft_thr is None else round(soft_thr, 4),
                        "soft_threshold_m": soft_thr_m,
                        "hard_verdict_by_budget": {},
                        "soft_verdict_by_budget": {},
                    }
                    for B in S.BUDGET_GRID:
                        feas = {m: T for m, (T, M) in pts.items() if M <= B}
                        if feas:
                            mb = min(feas, key=feas.get)
                            hv = {"verdict": "semaev" if feas[mb] < Tv else "vow",
                                  "m": mb, "margin_bits": round(Tv - feas[mb], 4), "feasible": True}
                        else:
                            hv = {"verdict": "vow", "m": None, "margin_bits": "semaev_infeasible", "feasible": False}
                        soft = {m: T + max(0.0, M - B) for m, (T, M) in pts.items()}
                        ms_ = min(soft, key=soft.get)
                        sv = {"verdict": "semaev" if soft[ms_] < Tv else "vow", "m": ms_,
                              "margin_bits": round(Tv - soft[ms_], 4)}
                        res["per_fips_n"][n][key]["hard_verdict_by_budget"][B] = hv
                        res["per_fips_n"][n][key]["soft_verdict_by_budget"][B] = sv
                    # alpha flip (stage1 argmin m, closed form) and reoptimised (scan)
                    m0 = tab.argmin_m[kr][n]
                    T0, M0 = pts[m0]
                    alpha_star = None if M0 == Mv else (Tv - T0) / (M0 - Mv)
                    flip_scan = None
                    for a in [i / 1000.0 for i in range(0, 1001)]:
                        sc = min(T + a * M for (T, M) in pts.values())
                        bc = Tv + a * Mv
                        if sc >= bc:
                            flip_scan = a
                            break
                    res["alpha_flip"][n][key] = {
                        "alpha_star_closed_form_stage1_argmin_m": (
                            None if alpha_star is None else round(alpha_star, 4)),
                        "semaev_wins_at_alpha0": T0 < Tv,
                        "flip_inside_0_1_stage1_argmin": (alpha_star is not None and 0.0 <= alpha_star <= 1.0
                                                           and T0 < Tv),
                        "first_alpha_where_semaev_loses_metric_reoptimised_m_step_0p001": flip_scan,
                        "grid_verdicts_stage1_argmin_m": {
                            a: ("semaev" if (T0 + a * M0) < (Tv + a * Mv) else "vow") for a in S.ALPHA_GRID},
                    }
            # disagreement bands between pairs of storage readings, record mode
            for mode in S.MODES:
                for a, b in itertools.combinations(S.STORAGES, 2):
                    ka, kb = f"{a}/{kr}/{mode}", f"{b}/{kr}/{mode}"
                    ra, rb = res["per_fips_n"][n][ka], res["per_fips_n"][n][kb]
                    for reading in ("hard", "soft"):
                        ta, tb = ra[f"{reading}_budget_threshold_log2_bits"], rb[f"{reading}_budget_threshold_log2_bits"]
                        band = None
                        if ta is not None and tb is not None:
                            band = {"lower_log2": min(ta, tb), "upper_log2": max(ta, tb),
                                    "reading_turning_first": a if ta < tb else b,
                                    "width_bits": round(abs(ta - tb), 4)}
                        elif ta is not None or tb is not None:
                            band = {"lower_log2": ta if ta is not None else tb, "upper_log2": "never",
                                    "reading_turning_first": a if ta is not None else b}
                        res["disagreement_bands"].setdefault(str(n), {})[f"{a}|{b}/{kr}/{mode}/{reading}"] = band
    dump(os.path.join(out_dir, "arm-f-fixed-budget.json"), res)
    log("ARM F written")
    return res


# ============================================================================ ARM I

def arm_i(tab, out_dir, log):
    worst, worst_cell, cells = 0.0, None, 0
    samples = []
    for n in tab.ns:
        for m in range(2, min(S.M_HI, n) + 1):
            a = SI.sparse_working_set_log2_bits(n, m)["total_nonzeros_log2"]
            b = tab.mem["semaev_sparse"][n][m][1]
            d = abs(a - b)
            cells += 1
            if d > worst:
                worst, worst_cell = d, {"n": n, "m": m, "independent": a, "surface": b}
            if n in S.FIPS_N and m in (tab.argmin_m[KR_U][n], 6, 8):
                samples.append({"n": n, "m": m, "independent_log2": round(a, 6),
                                "surface_log2": round(b, 6), "diff_bits": round(a - b, 9)})
    out = {"arm": "I", "control": "C7",
           "independent_implementation": "sparse_independent.py (exact integer n^7 m^3 / 24 then log2)",
           "compared_against": "surface_cost.Tables.mem['semaev_sparse'] (float sum of logarithms)",
           "cells_compared": cells, "domain": {"n": [S.N_LO, S.N_HI], "m": [2, S.M_HI]},
           "largest_cellwise_disagreement_bits": worst, "at_cell": worst_cell,
           "samples_at_fips_n": samples,
           "kn_lit_e77232_n571_check": SI.kn_lit_e77232_n571_check(),
           "what_this_does_and_does_not_show": (
               "Two arithmetic routes to Semaev's self-estimated formula agree. That raises "
               "confidence in the arithmetic of the term, not in the formula, which is "
               "corroborated nowhere outside the thread KN-LIT-e77232 records."),
           "independence_deviation": (
               "PD-I: the executor had read memory_charged_cost.py in full (including "
               "semaev_memory_log2) during contract intake BEFORE writing "
               "sparse_independent.py. The module imports nothing from it and uses a "
               "different arithmetic route, but the blindness the contract asked for was "
               "not achieved and this arm's independence is weaker than specified.")}
    dump(os.path.join(out_dir, "sparse-implementation-comparison.json"), out)
    log(f"ARM I written; largest disagreement {worst:.3e} bits")
    return out


# ============================================================================ C10

def c10_measurements(out_dir, log):
    import yaml
    t = yaml.safe_load(open(TABLES))
    rows = []
    for tname, tbl in (("table_1", t["table_1"]), ("table_2", t["table_2"])):
        for r in tbl["rows"]:
            n = r["n"]
            tt = r["t_eq_m"] if "t_eq_m" in r else r["t"]
            k = r["k"]
            mb = r.get("total_MB")
            if mb is None:
                continue
            nvars = max(tt - 2, 0) * n + k * tt
            width = S.log2_macaulay_width(nvars, 4)
            rows_log2 = math.log2(n * max(tt - 1, 1)) + math.log2(nvars + 1)
            model = {
                "dense_row_echelon": 2.0 * width,
                "semaev_sparse": (4.0 * math.log2(n * tt) - math.log2(24.0)
                                  + 3.0 * math.log2(n) - math.log2(tt)),
                "rows_times_cols_dense": rows_log2 + width,
                "nonzeros_with_index_sparse": (rows_log2
                                               + math.log2(sum(math.comb(2 * n + k, d) for d in range(4)))
                                               + math.log2(width)),
            }
            measured_peak = math.log2(mb * 8 * 2 ** 20)              # reading A: MB is per-system peak
            measured_total100 = math.log2(mb * 8 * 2 ** 20 / 100.0)  # reading B: MB is total over 100 systems
            row = {"table": tname, "n": n, "t": tt, "k": k, "nvars": nvars,
                   "macaulay_width_log2": round(width, 4), "total_MB_printed": mb,
                   "measured_log2_bits_reading_A_peak_per_system": round(measured_peak, 4),
                   "measured_log2_bits_reading_B_total_over_100_systems_per_system": round(measured_total100, 4),
                   "model_log2_bits": {kk: round(v, 4) for kk, v in model.items()},
                   "model_minus_measured_bits_reading_A": {kk: round(v - measured_peak, 4) for kk, v in model.items()},
                   "model_minus_measured_bits_reading_B": {kk: round(v - measured_total100, 4) for kk, v in model.items()}}
            rows.append(row)
    upper = {}
    for st in S.STORAGES:
        upper[st] = {
            "reading_A_upper_bounds_every_row": all(r["model_minus_measured_bits_reading_A"][st] >= 0 for r in rows),
            "reading_A_rows_exceeded": sum(1 for r in rows if r["model_minus_measured_bits_reading_A"][st] < 0),
            "reading_B_upper_bounds_every_row": all(r["model_minus_measured_bits_reading_B"][st] >= 0 for r in rows),
            "reading_B_rows_exceeded": sum(1 for r in rows if r["model_minus_measured_bits_reading_B"][st] < 0),
            "min_residual_A": min(r["model_minus_measured_bits_reading_A"][st] for r in rows),
            "max_residual_A": max(r["model_minus_measured_bits_reading_A"][st] for r in rows),
            "min_residual_B": min(r["model_minus_measured_bits_reading_B"][st] for r in rows),
            "max_residual_B": max(r["model_minus_measured_bits_reading_B"][st] for r in rows),
        }
    # gap widening dense - sparse from measured scale to FIPS
    gap = []
    for r in rows:
        gap.append({"n": r["n"], "t": r["t"], "nvars": r["nvars"],
                    "dense_minus_sparse_bits": round(r["model_log2_bits"]["dense_row_echelon"]
                                                     - r["model_log2_bits"]["semaev_sparse"], 4)})
    tab = S.Tables()
    for n in S.FIPS_N:
        m = tab.argmin_m[KR_U][n]
        d = tab.mem["dense_row_echelon"][n][m][1]
        s_ = tab.mem["semaev_sparse"][n][m][1]
        gap.append({"n": n, "t": m, "nvars": S.macaulay_nvars(n, m, -(-n // m)),
                    "dense_minus_sparse_bits": round(d - s_, 4)})
    out = {"control": "C10", "rows_compared": len(rows), "rows": rows,
           "upper_bound_check_per_reading": upper,
           "dense_minus_sparse_gap_measured_scale_to_fips": gap,
           "column_reading_dispute_NOT_settled": (
               "tables.yaml transcription_limits state the MB column is the total over 100 "
               "systems (reading B); the validator's J1 report infers a per-process peak "
               "(reading A). Both are reported; neither is picked."),
           "note": ("The model charges bits of one Macaulay matrix at degree 4 with t chain "
                    "variables; MAGMA's MB includes its own process overhead, so a positive "
                    "residual is not a validation of the model and a negative one is a "
                    "failure to upper-bound.")}
    dump(os.path.join(out_dir, "measurement-comparison.json"), out)
    log(f"C10 written: {len(rows)} rows")
    return out


# ============================================================================ controls

def matched_null(tab, out_dir_unused, log):
    out = {"control": "C3", "per_metric_and_storage": {}}
    fams = [("time_memory_product", None), ("memory_weighted_time_alpha", 0.5),
            ("fixed_budget_soft", 40), ("fixed_budget_hard", 70)]
    for inst in fams:
        lab = S.metric_label(inst)
        for st in S.STORAGES:
            for kr in S.K_READINGS:
                sem_t = S.semaev_curve(tab, ("time_only", None), st, kr, 0, "stage1_argmin")
                sem = S.semaev_curve(tab, inst, st, kr, 0, "stage1_argmin")
                t_only = S.compare_curves(sem_t, S.baseline_curve(("time_only", None), RECORD_MODE, 30, 0))
                inf_null = S.compare_curves(sem, S.baseline_curve(inst, RECORD_MODE, 0, 0))
                rec = S.compare_curves(sem, S.baseline_curve(inst, RECORD_MODE, 30, 0))
                zero = S.compare_curves(sem, S.baseline_curve(inst, "zero_memory_comparator", 0, 0))
                fam = inst[0]
                zero_degenerate = zero["degenerate"] and fam in ("time_memory_product", "memory_weighted_time_alpha")
                e = {
                    "cell": {"metric": lab, "processors_log2": 0, "kappa": 1, "cofactor_h": 1,
                             "storage_reading": st, "k_reading": kr, "m_selection": "stage1_argmin",
                             "baseline_charging_mode": RECORD_MODE},
                    "time_only_persistent_crossover": t_only["persistent_crossover_n"],
                    "informative_null_store0_3n_bits": {
                        "persistent_crossover_n": inf_null["persistent_crossover_n"],
                        "margin_409_bits": inf_null["margin_409_bits"]},
                    "record_store30": {"persistent_crossover_n": rec["persistent_crossover_n"],
                                       "margin_409_bits": rec["margin_409_bits"]},
                    "zero_memory_comparator": (
                        {"status": "DEGENERATE", "reason": "log2(0) = -inf memory makes the baseline's metric cost -inf; Semaev never wins; no crossover exists; this is NOT a share of zero"}
                        if zero_degenerate else
                        {"status": "non_degenerate_for_this_metric", "persistent_crossover_n": zero["persistent_crossover_n"],
                         "margin_409_bits": zero["margin_409_bits"],
                         "note": "budget metrics cap memory, so a zero-memory baseline is just a feasible baseline"}),
                }
                a, b, c = (t_only["persistent_crossover_n"], inf_null["persistent_crossover_n"],
                           rec["persistent_crossover_n"])
                e["decomposition_in_n"] = {
                    "charging_semaev_memory_only (time_only -> informative null)": None if a is None or b is None else b - a,
                    "charging_baseline_store_2^30 (informative null -> record)": None if b is None or c is None else c - b,
                    "net (time_only -> record)": None if a is None or c is None else c - a}
                if isinstance(inf_null["margin_409_bits"], float) and isinstance(rec["margin_409_bits"], float) and isinstance(t_only["margin_409_bits"], float):
                    e["decomposition_in_bits_at_409"] = {
                        "charging_semaev_memory_only": round(inf_null["margin_409_bits"] - t_only["margin_409_bits"], 4),
                        "charging_baseline_store_2^30": round(rec["margin_409_bits"] - inf_null["margin_409_bits"], 4)}
                out["per_metric_and_storage"][f"{lab}/{st}/{kr}"] = e
    e0 = out["per_metric_and_storage"][f"time_memory_product/dense_row_echelon/{KR_U}"]
    out["baseline_store_contribution_near_zero"] = (
        e0["decomposition_in_n"]["charging_baseline_store_2^30 (informative null -> record)"] in (0, None))
    log("C3 matched null done")
    return out


def free_yield_control(tab, log):
    rows, verdicts = [], []
    insts = [("time_only", None), ("time_memory_product", None), ("memory_weighted_time_alpha", 0.5),
             ("fixed_budget_hard", 70), ("fixed_budget_soft", 40)]
    for inst in insts:
        for st in S.STORAGES:
            for msel in S.M_SELECTIONS:
                base = S.baseline_curve(inst, RECORD_MODE, 30, 0)
                c0 = S.compare_curves(S.semaev_curve(tab, inst, st, KR_U, 0, msel), base)
                c1 = S.compare_curves(S.semaev_curve(tab, inst, st, KR_U, 0, msel, 1, True), base)
                m0, m1 = c0["margin_409_bits"], c1["margin_409_bits"]
                margin_improved = (m1 > m0) if isinstance(m0, float) and isinstance(m1, float) else None
                for f in ("first_crossing_n", "persistent_crossover_n"):
                    a, b = c0[f], c1[f]
                    if a is None and b is None:
                        moved, why = None, "no crossover in [3,700] either way"
                    elif a == S.N_LO and b == S.N_LO:
                        moved, why = None, "pinned at the domain floor n = 3 (low-n artefact); cannot move further down"
                    elif a is None:
                        moved, why = True, "crossover appears where there was none"
                    elif b is None:
                        moved, why = False, "crossover disappears"
                    else:
                        moved, why = (b < a), ""
                    if moved is False and inst[0] == "fixed_budget_hard" and msel == "stage1_argmin":
                        why = ("m_selection interaction: deleting log2(m!) moves the stage-1 argmin to m = 30, "
                               "whose working set exceeds the hard budget at every n; the metric_reoptimised "
                               "counterpart is the informative cell")
                    rows.append({"metric": S.metric_label(inst), "storage_reading": st, "m_selection": msel,
                                 "field": f, "with_factor": a, "free_yield": b, "moved_down": moved,
                                 "margin_409_with": m0, "margin_409_free": m1,
                                 "margin_409_improved": margin_improved, "note": why})
                    verdicts.append((moved, margin_improved, inst[0], msel))
    hard_argmin_exceptions = [r for r in rows if r["moved_down"] is False and r["metric"].startswith("fixed_budget_hard")
                              and r["m_selection"] == "stage1_argmin"]
    genuine_failures = [r for r in rows if r["moved_down"] is False and r not in hard_argmin_exceptions]
    margins_all_improved = all(r["margin_409_improved"] is not False for r in rows)
    passed = (not genuine_failures) and margins_all_improved
    log(f"C4 free-yield: passed={passed} genuine_failures={len(genuine_failures)} "
        f"floor_pinned={sum(1 for r in rows if r['moved_down'] is None and 'floor' in r['note'])} "
        f"hard_argmin_exceptions={len(hard_argmin_exceptions)}")
    return {"control": "C4", "deleted": "exactly log2(m!) + (n - m k) from stage 1; nothing else",
            "passed": passed,
            "criterion": ("every crossover moves DOWN or is pinned at the domain floor with the n = 409 margin "
                          "moving in Semaev's favour; the hard-budget/stage1_argmin cells where the modified "
                          "argmin m blows the budget are listed as m_selection interactions, not as sign failures, "
                          "and their metric_reoptimised counterparts must move down"),
            "genuine_failures": genuine_failures, "m_selection_interactions": hard_argmin_exceptions,
            "rows": rows}


def invalid_inputs():
    cases = [("m<2", dict(n=409, m=1)), ("m>n", dict(n=10, m=11)), ("t>m", dict(n=409, m=11, t=12)),
             ("non-integer n", dict(n=409.5)), ("negative store_log2", dict(n=409, store_log2=-1)),
             ("budget below 3n bits", dict(n=409, budget_log2=10)), ("kappa<=0", dict(n=409, kappa=0))]
    out = []
    for name, kw in cases:
        try:
            S.validate_inputs(**kw)
            out.append({"case": name, "rejected": False, "error": None})
        except (ValueError, TypeError) as exc:
            out.append({"case": name, "rejected": True, "error": str(exc)})
    return {"control": "C9", "passed": all(c["rejected"] for c in out), "cases": out}


# ============================================================================ sensitivities

def sensitivities(out_dir, log):
    out = {"omega_x_degree": [], "curve_labels": [], "kappa": [], "cofactor": []}
    tabs = {}
    for om in S.OMEGA_GRID:
        for dg in S.DEGREE_GRID:
            tabs[(om, dg)] = S.Tables(om, dg)
            for inst in [("time_only", None), ("time_memory_product", None)]:
                for st in S.STORAGES:
                    for mode in S.MODES:
                        c = S.compare_curves(S.semaev_curve(tabs[(om, dg)], inst, st, KR_U, 0, "stage1_argmin"),
                                             S.baseline_curve(inst, mode, 30, 0))
                        out["omega_x_degree"].append({
                            "cell": {"metric": S.metric_label(inst), "store_log2": 30, "processors_log2": 0,
                                     "baseline_charging_mode": mode, "kappa": 1, "cofactor_h": 1,
                                     "storage_reading": st, "k_reading": KR_U, "m_selection": "stage1_argmin",
                                     "omega": om, "degree_bound_GIVEN_not_measured": dg},
                            "persistent_crossover_n": c["persistent_crossover_n"],
                            "first_crossing_n": c["first_crossing_n"],
                            "margin_409_bits": c["margin_409_bits"], "margin_571_bits": c["margin_571_bits"]})
    tab = tabs[(3.0, 4)]
    curves = [("B-409", 409, 2, False), ("K-409", 409, 4, True), ("B-571", 571, 2, False), ("K-571", 571, 4, True)]
    for label, n, h, frob in curves:
        for inst in [("time_only", None), ("time_memory_product", None)]:
            for st in S.STORAGES:
                for mode in S.MODES:
                    m = tab.argmin_m[KR_U][n]
                    T, M = tab.semaev_point(n, m, st, KR_U)
                    sc = S.metric_cost(T, M, inst)
                    row = {"curve_label": label, "n": n, "cofactor_h_used": h,
                           "cofactor_provenance": "recalled (FIPS 186 cofactors 2 for B-curves, 4 for a=0 Koblitz curves); NOT verified from a source in this run; all h in {1,2,4} are in the surface",
                           "frobenius_discount_applied": frob,
                           "frobenius_discount_bits": round(0.5 * math.log2(n), 4) if frob else 0.0,
                           "cell": {"metric": S.metric_label(inst), "store_log2": 30, "processors_log2": 0,
                                    "baseline_charging_mode": mode, "kappa": 1, "storage_reading": st,
                                    "k_reading": KR_U, "m_selection": "stage1_argmin"}}
                    for hh, ff, tag in ((1, False, "h1_no_discount"), (h, False, "cofactor_only"), (h, frob, "cofactor_and_frobenius")):
                        Tv, Mv = S.vow_point(n, mode, 30, 0, hh, ff)
                        row[f"margin_bits_{tag}"] = round(S.metric_cost(Tv, Mv, inst) - sc, 4)
                    out["curve_labels"].append(row)
    for inst in [("time_only", None), ("time_memory_product", None)]:
        for st in S.STORAGES:
            for kappa in S.KAPPA_GRID:
                c = S.compare_curves(S.semaev_curve(tab, inst, st, KR_U, 0, "stage1_argmin", kappa),
                                     S.baseline_curve(inst, RECORD_MODE, 30, 0))
                out["kappa"].append({"cell": {"metric": S.metric_label(inst), "store_log2": 30, "processors_log2": 0,
                                              "baseline_charging_mode": RECORD_MODE, "kappa": kappa, "cofactor_h": 1,
                                              "storage_reading": st, "k_reading": KR_U, "m_selection": "stage1_argmin"},
                                     "persistent_crossover_n": c["persistent_crossover_n"],
                                     "margin_409_bits": c["margin_409_bits"]})
            for h in S.COFACTOR_GRID:
                c = S.compare_curves(S.semaev_curve(tab, inst, st, KR_U, 0, "stage1_argmin"),
                                     S.baseline_curve(inst, RECORD_MODE, 30, 0, h))
                out["cofactor"].append({"cell": {"metric": S.metric_label(inst), "store_log2": 30, "processors_log2": 0,
                                                 "baseline_charging_mode": RECORD_MODE, "kappa": 1, "cofactor_h": h,
                                                 "storage_reading": st, "k_reading": KR_U, "m_selection": "stage1_argmin"},
                                        "persistent_crossover_n": c["persistent_crossover_n"],
                                        "margin_409_bits": c["margin_409_bits"],
                                        "direction": "baseline time - 0.5 log2(h): the baseline gets CHEAPER (red team J2(d) corrected direction)"})
    dump(os.path.join(out_dir, "sensitivities.json"), out)
    log("sensitivities written")
    return out


# ============================================================================ main

def execute(out_dir, log):
    t0 = time.time()
    tab = S.Tables()
    r = arm_r(tab, out_dir, log)
    if not r["gate"]["passed"]:
        log("ARM R FAILED: stopping per stopping rule 1")
        return {"halted": "ARM R reproduction gate failed", "arm_r": r}
    n = arm_n(out_dir, log)
    rows = arm_s(tab, out_dir, log)
    surf = surface_summary(rows, out_dir, log)
    b = arm_b(tab, out_dir, log)
    f = arm_f(tab, out_dir, log)
    i = arm_i(tab, out_dir, log)
    c10 = c10_measurements(out_dir, log)
    c2 = S.table3_control(tab)
    c3 = matched_null(tab, out_dir, log)
    c4 = free_yield_control(tab, log)
    c5 = S.eq4_typo_detector(tab)
    c9 = invalid_inputs()
    sens = sensitivities(out_dir, log)
    controls = {
        "C1_reproduction_gate": {"passed": r["gate"]["passed"], "detail": "reproduction-gate.json",
                                 "largest_disagreement_vs_record_bits": r["largest_disagreement_vs_record_bits"],
                                 "largest_disagreement_vs_red_team_bits": r["largest_disagreement_vs_red_team_recomputations_bits"]},
        "C2_table3_baseline_reproduction": c2,
        "C3_informative_matched_null": c3,
        "C4_known_false_free_yield": c4,
        "C5_known_false_eq4_typo_detector": c5,
        "C6_prime_field_nearby_object": {"status": "UNREACHED", "detail": "arm-n-prime-field-control.json",
                                         "missing": [p["piece"] for p in n["concrete_missing_pieces"]]},
        "C7_independent_sparse_working_set": {"largest_cellwise_disagreement_bits": i["largest_cellwise_disagreement_bits"],
                                              "n571_check_all_agree": i["kn_lit_e77232_n571_check"]["all_agree"],
                                              "independence_deviation": i["independence_deviation"]},
        "C8_full_scan_domain": {"scan_domain": [S.N_LO, S.N_HI], "parent_window_also_reported": list(S.PARENT_WINDOW),
                                "low_n_artefact_example": next(
                                    (row for row in rows if row[0] == "time_memory_product" and row[1] == 30 and row[2] == 0
                                     and row[3] == RECORD_MODE and row[4] == 1 and row[5] == 1
                                     and row[6] == "dense_row_echelon" and row[7] == KR_U and row[8] == "stage1_argmin"), None),
                                "note": "a baseline charged a fixed 2^30-point store in a group of 2^3..2^4 elements is 'beaten' at n = 3..4 under the product; labelled, not excluded"},
        "C9_invalid_input_rejection": c9,
        "C10_measurement_comparison": {"detail": "measurement-comparison.json",
                                       "rows_compared": c10["rows_compared"],
                                       "upper_bound_check_per_reading": c10["upper_bound_check_per_reading"]},
    }
    dump(os.path.join(out_dir, "controls.json"), controls)
    log(f"controls.json written; total compute {time.time() - t0:.1f}s")
    return {"halted": None, "arm_r": r, "arm_n": n, "surface": surf, "arm_b": b, "arm_f": f,
            "arm_i": i, "c10": c10, "controls": controls, "sensitivities": sens,
            "compute_seconds": time.time() - t0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    log = Log(run_dir)
    log("execution 1 start")
    res = execute(run_dir, log)
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    log(f"execution 1 done: cpu={ru1.ru_utime + ru1.ru_stime:.1f}s peak_rss_kb={ru1.ru_maxrss}")
    if res["halted"]:
        dump(os.path.join(run_dir, "halted.json"), {"halted": res["halted"]})
        return 2
    # determinism: second execution into a subdirectory, then byte diff
    second = os.path.join(run_dir, "determinism-second-execution")
    os.makedirs(second, exist_ok=True)
    log2 = Log(second)
    log2("execution 2 start")
    execute(second, log2)
    log2("execution 2 done")
    files = [f for f in sorted(os.listdir(second)) if f.endswith(".json")]
    det = {"files_compared": [], "all_identical": True}
    for f in files:
        a, b = sha256(os.path.join(run_dir, f)), sha256(os.path.join(second, f))
        det["files_compared"].append({"file": f, "sha256_execution_1": a, "sha256_execution_2": b, "identical": a == b})
        det["all_identical"] &= (a == b)
    det["files_that_differ"] = ["stdout.log (timestamps only; not compared byte-wise)"]
    det["second_execution_copies"] = ("deleted after hashing to avoid duplicating the surface in the repository; "
                                      "the sha256 values above are the evidence; determinism-second-execution/stdout.log is kept")
    for f in files:
        os.remove(os.path.join(second, f))
    dump(os.path.join(run_dir, "determinism-check.json"), det)
    log(f"determinism: all arm JSON identical across two executions = {det['all_identical']}")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    dump(os.path.join(run_dir, "resources.json"),
         {"cpu_seconds_both_executions": ru.ru_utime + ru.ru_stime, "peak_rss_bytes": ru.ru_maxrss * 1024,
          "compute_seconds_execution_1": res["compute_seconds"]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
