#!/usr/bin/env python3
"""Validator TASK-20260913-67ab4f -- joints M1(2,3,4), M2, M3(C3,C4), M4(2,3,5), PTM.

My own implementation of the column definitions disclosed in
experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c/implementation.md and in
COST-SEMBIN-8d123b (Semaev time/memory, four storage readings, three baseline
charging modes, five metric families, kappa, cofactor, two k readings, two
m_selection conventions). Nothing is imported from the run's code; the run's
JSON is read only as DATA to compare against.

Run AFTER rederive_pre_code.py (the pre-code blind re-derivations M1(1), M4(1),
M5(4)) and after reading the run's code, as the sequencing log records.
"""
import json
import math
import os
import random
from math import comb, lgamma, log2

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c"
OUT = os.path.join(HERE, "validate_surface.json")
INF = float("inf")
N_LO, N_HI, M_HI = 3, 700, 30
PARENT_WINDOW = (250, 650)


def log2_add(a, b):
    if a == -INF:
        return b
    if b == -INF:
        return a
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 60 else hi + log2(1.0 + 2.0 ** (lo - hi))


def log2_fact(m):
    return lgamma(m + 1.0) / math.log(2.0)


def kval(n, m, kr):
    return n / m if kr == "unceiled_n_over_m_as_in_table3" else float(-(-n // m))


def sem_time(n, m, kr, omega=3.0, omega_p=2.0, free_yield=False):
    k = kval(n, m, kr)
    s1 = k + 4.0 * omega * log2(n)
    if not free_yield:
        s1 += log2_fact(m) + (n - m * k)
    s2 = k * omega_p
    return log2_add(s1, s2), s1


def width_log2(nvars, degree=4):
    return log2(sum(comb(nvars, d) for d in range(degree + 1)))


def sem_mem(n, m, storage, degree=4):
    k = -(-n // m)
    rel = k + log2(m * k + 2 * n)
    nvars = (m - 2) * n + k * m
    wl = width_log2(nvars, degree)
    if storage == "dense_row_echelon":
        ws = 2.0 * wl
    elif storage == "semaev_sparse":
        ws = (4.0 * log2(n * m) - log2(24.0)) + (3.0 * log2(n) - log2(m))
    elif storage == "rows_times_cols_dense":
        ws = log2(n * (m - 1)) + log2(nvars + 1) + wl
    elif storage == "nonzeros_with_index_sparse":
        v = 2 * n + k
        ws = log2(n * (m - 1)) + log2(nvars + 1) + log2(sum(comb(v, d) for d in range(4))) + log2(wl)
    else:
        raise ValueError(storage)
    return rel, ws, wl, nvars


def vow_W(n, h=1, frob=False):
    W = log2(0.886) + n / 2.0 - 0.5 * log2(h)
    if frob:
        W -= 0.5 * log2(n)
    return W


def vow_point(n, mode, store_log2, p, h=1, frob=False, budget=None):
    W = vow_W(n, h, frob)
    unit = log2(3.0 * n)
    room = INF if budget is None else budget - unit
    if room != INF and room < 0:
        raise ValueError("budget below 3n bits")
    if mode == "record_point_M1_w30":
        return W - min(p, room), min(store_log2, room) + unit
    if mode == "own_curve_product_minimum":
        pe = min(p, room)
        return W - pe + 1.0, pe + unit
    if mode == "sect113r2_calibrated_ratio":
        if room == INF:
            pe, we = p, p + 13.3
        else:
            pe = max(0.0, min(p, room - 13.3))
            we = min(pe + 13.3, room)
        return W + log2(2.0 ** (-pe) + 2.0 ** (-we)), we + unit
    if mode == "zero_memory_comparator":
        return W - p, -INF
    raise ValueError(mode)


def metric_cost(T, Mem, fam, par):
    if fam == "time_only":
        return T
    if fam == "time_memory_product":
        return T + Mem
    if fam == "memory_weighted_time_alpha":
        return T if par == 0.0 else T + par * Mem
    if fam == "fixed_budget_hard":
        return T if Mem <= par else INF
    if fam == "fixed_budget_soft":
        return T + max(0.0, Mem - par)
    raise ValueError(fam)


def cell_curves(fam, par, store, p, mode, kappa, h, storage, kr, msel,
                degree=4, omega=3.0, free_yield=False, frob=False):
    budget = par if fam.startswith("fixed_budget") else None
    margins, wins = {}, {}
    m_at = {}
    for n in range(N_LO, N_HI + 1):
        ms = list(range(2, min(M_HI, n) + 1))
        if msel == "stage1_argmin":
            m = min(ms, key=lambda mm: sem_time(n, mm, kr, omega, free_yield=free_yield)[1])
            t, _ = sem_time(n, m, kr, omega, free_yield=free_yield)
            rel, ws, _, _ = sem_mem(n, m, storage, degree)
            T = t - log2(kappa) - p
            Mem = log2_add(rel, ws + p)
            sc = metric_cost(T, Mem, fam, par)
        else:
            best = None
            for mm in ms:
                t, _ = sem_time(n, mm, kr, omega, free_yield=free_yield)
                rel, ws, _, _ = sem_mem(n, mm, storage, degree)
                T = t - log2(kappa) - p
                Mem = log2_add(rel, ws + p)
                c = metric_cost(T, Mem, fam, par)
                if best is None or c < best[0]:
                    best = (c, mm)
            sc, m = best
        Tv, Mv = vow_point(n, mode, store, p, h, frob, budget)
        bc = metric_cost(Tv, Mv, fam, par)
        if sc == INF and bc == INF:
            margins[n], wins[n] = None, False
        elif sc == INF:
            margins[n], wins[n] = "semaev_infeasible", False
        elif bc == INF:
            margins[n], wins[n] = "semaev_only_feasible", True
        else:
            margins[n] = bc - sc
            wins[n] = (bc - sc) > 0
        m_at[n] = m
    intervals, start = [], None
    for n in range(N_LO, N_HI + 1):
        if wins[n] and start is None:
            start = n
        if not wins[n] and start is not None:
            intervals.append([start, n - 1])
            start = None
    if start is not None:
        intervals.append([start, N_HI])
    first = intervals[0][0] if intervals else None
    persistent = intervals[-1][0] if intervals and intervals[-1][1] == N_HI else None
    parent = next((n for n in range(*(PARENT_WINDOW[0], PARENT_WINDOW[1] + 1)) if wins[n]), None)
    return {"first_crossing_n": first, "persistent_crossover_n": persistent,
            "crossover_n_parent_window_250_650": parent,
            "semaev_cheaper_intervals": intervals,
            "margin_409_bits": margins[409], "margin_571_bits": margins[571],
            "m_at_409": m_at[409], "m_at_571": m_at[571]}


out = {}

# ------------------------------------------------------------------ load raw cells
raw = json.load(open(os.path.join(RUN, "raw-result.json")))
codes = raw["codes"]
FIELDS = raw["cell_fields"]
idx = {f: i for i, f in enumerate(FIELDS)}
CELLS = {}
for c in raw["cells"]:
    key = (codes["metric"][c[idx["metric"]]], c[idx["store_log2"]], c[idx["processors_log2"]],
           codes["baseline_charging_mode"][c[idx["baseline_charging_mode"]]],
           c[idx["kappa"]], c[idx["cofactor_h"]],
           codes["storage_reading"][c[idx["storage_reading"]]],
           codes["k_reading"][c[idx["k_reading"]]],
           codes["m_selection"][c[idx["m_selection"]]])
    CELLS[key] = c
out["raw_cells_loaded"] = len(CELLS)


def parse_metric(label):
    if "[" not in label:
        return label, None
    fam, rest = label.split("[", 1)
    par = float(rest.rstrip("]").split("=")[1])
    if fam == "fixed_budget_hard" or fam == "fixed_budget_soft":
        par = float(par)
    return fam, par


def raw_cell(label, store, p, mode, kappa, h, storage, kr, msel):
    c = CELLS[(label, store, p, mode, kappa, h, storage, kr, msel)]
    return {f: c[idx[f]] for f in FIELDS[9:]}


# ------------------------------------------------------------------ M1(2): 12 cells
TWELVE = [
    ("time_only", 30, 0, "record_point_M1_w30", 1, 1, "dense_row_echelon", "unceiled_n_over_m_as_in_table3", "stage1_argmin"),
    ("time_memory_product", 30, 0, "record_point_M1_w30", 1, 1, "semaev_sparse", "unceiled_n_over_m_as_in_table3", "stage1_argmin"),
    ("time_memory_product", 30, 0, "own_curve_product_minimum", 1, 1, "dense_row_echelon", "unceiled_n_over_m_as_in_table3", "stage1_argmin"),
    ("time_memory_product", 60, 20, "record_point_M1_w30", 10, 2, "rows_times_cols_dense", "ceil_n_over_m", "metric_reoptimised"),
    ("memory_weighted_time_alpha[alpha=0.5]", 48, 40, "sect113r2_calibrated_ratio", 100, 4, "nonzeros_with_index_sparse", "unceiled_n_over_m_as_in_table3", "stage1_argmin"),
    ("memory_weighted_time_alpha[alpha=0.811]", 0, 0, "record_point_M1_w30", 1, 1, "dense_row_echelon", "ceil_n_over_m", "stage1_argmin"),
    ("fixed_budget_hard[budget_log2=70]", 20, 0, "record_point_M1_w30", 1, 1, "semaev_sparse", "unceiled_n_over_m_as_in_table3", "metric_reoptimised"),
    ("fixed_budget_hard[budget_log2=89]", 40, 20, "own_curve_product_minimum", 10, 1, "dense_row_echelon", "unceiled_n_over_m_as_in_table3", "metric_reoptimised"),
    ("fixed_budget_soft[budget_log2=40]", 10, 0, "record_point_M1_w30", 1, 4, "semaev_sparse", "ceil_n_over_m", "stage1_argmin"),
    ("fixed_budget_soft[budget_log2=65]", 30, 40, "sect113r2_calibrated_ratio", 100, 1, "rows_times_cols_dense", "unceiled_n_over_m_as_in_table3", "metric_reoptimised"),
    ("time_memory_product", 0, 40, "own_curve_product_minimum", 100, 2, "nonzeros_with_index_sparse", "ceil_n_over_m", "stage1_argmin"),
    ("memory_weighted_time_alpha[alpha=1.0]", 48, 0, "record_point_M1_w30", 10, 1, "semaev_sparse", "ceil_n_over_m", "metric_reoptimised"),
]
twelve = []
worst = 0.0
for key in TWELVE:
    fam, par = parse_metric(key[0])
    mine = cell_curves(fam, par, key[1], key[2], key[3], key[4], key[5], key[6], key[7], key[8])
    theirs = raw_cell(*key)
    d = {}
    for f in ["margin_409_bits", "margin_571_bits"]:
        a, b = mine[f], theirs[f]
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            d[f] = round(a - b, 8)
            worst = max(worst, abs(a - b))
        else:
            d[f] = f"mine={a} theirs={b}"
    twelve.append({"cell": dict(zip(["metric", "store_log2", "processors_log2", "baseline_charging_mode",
                                     "kappa", "cofactor_h", "storage_reading", "k_reading", "m_selection"], key)),
                   "mine": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in mine.items()},
                   "theirs": theirs, "margin_diff_bits": d,
                   "crossovers_agree": (mine["first_crossing_n"] == theirs["first_crossing_n"]
                                        and mine["persistent_crossover_n"] == theirs["persistent_crossover_n"]
                                        and mine["crossover_n_parent_window_250_650"] == theirs["crossover_n_parent_window_250_650"]),
                   "intervals_agree": mine["semaev_cheaper_intervals"] == theirs["semaev_cheaper_intervals"],
                   "m_agree": (mine["m_at_409"] == theirs["m_at_409"] and mine["m_at_571"] == theirs["m_at_571"])})
out["M1_twelve_cells"] = {"rows": twelve, "worst_margin_disagreement_bits": worst,
                          "all_crossovers_agree": all(r["crossovers_agree"] for r in twelve),
                          "all_intervals_agree": all(r["intervals_agree"] for r in twelve),
                          "all_m_agree": all(r["m_agree"] for r in twelve)}

# ------------------------------------------------------------------ M1(3): collisions
# definition (surface.json): same (metric, storage, k_reading, kappa, h, m_selection) and same
# persistent_crossover_n, differing in (store_log2, processors_log2, baseline_charging_mode).
groups = {}
for key, c in CELLS.items():
    label, store, p, mode, kappa, h, storage, kr, msel = key
    pc = c[idx["persistent_crossover_n"]]
    groups.setdefault((label, storage, kr, kappa, h, msel, pc), []).append((store, p, mode))
pairs = 0
pair_samples = []
for g, members in groups.items():
    if g[6] is None:
        continue            # null crossover: not a colliding value
    L = len(members)
    pairs += L * (L - 1) // 2
    if len(pair_samples) < 4000 and L > 1:
        for i in range(L):
            for j in range(i + 1, L):
                a, b = members[i], members[j]
                if a[0] != b[0] or a[1] != b[1] or a[2] != b[2]:
                    pair_samples.append((g, a, b))
                if len(pair_samples) > 4000:
                    break
            if len(pair_samples) > 4000:
                break
out["M1_collision_recount"] = {"my_count_excluding_null_crossovers": pairs,
                               "run_reported": 1556684}
# include nulls variant
pairs_with_null = sum(len(v) * (len(v) - 1) // 2 for v in groups.values())
out["M1_collision_recount"]["my_count_including_null_crossovers"] = pairs_with_null

# classify 20 sampled pairs
random.seed(20260915)
sample = random.sample(pair_samples, min(20, len(pair_samples)))
classified = []
for g, a, b in sample:
    label, storage, kr, kappa, h, msel, pc = g
    fam, par = parse_metric(label)
    store_differs, p_differs, mode_differs = a[0] != b[0], a[1] != b[1], a[2] != b[2]
    # does store act in this cell?  time_only ignores memory; own_curve/sect113 ignore store_log2;
    # budget metrics cap it.
    store_acts = not (fam == "time_only" or (fam == "memory_weighted_time_alpha" and par == 0.0))
    store_acts = store_acts and a[2] == "record_point_M1_w30" and b[2] == "record_point_M1_w30"
    reasons = []
    if fam == "time_only" or (fam == "memory_weighted_time_alpha" and par == 0.0):
        reasons.append("metric ignores memory entirely: store_log2 is a labelled axis that does not act")
    for cell in (a, b):
        if cell[2] in ("own_curve_product_minimum", "sect113r2_calibrated_ratio"):
            reasons.append(f"{cell[2]} ignores store_log2 by construction")
    if fam.startswith("fixed_budget"):
        reasons.append("budget metric caps the baseline store at budget - log2(3n)")
    # genuine: both cells record_point, memory-charging metric, and the acting axis differs
    genuine = store_acts and (store_differs or p_differs)
    if genuine:
        # check whether store - processors is equal (the disclosed difference-only dependence)
        genuine = (a[0] - a[1]) != (b[0] - b[1])
        if not genuine:
            reasons.append("record_point under a multiplicative metric depends on store_log2 - processors_log2 only; this pair has the same difference")
    classified.append({"group": {"metric": label, "storage_reading": storage, "k_reading": kr,
                                 "kappa": kappa, "cofactor_h": h, "m_selection": msel,
                                 "persistent_crossover_n": pc},
                       "cell_a": {"store_log2": a[0], "processors_log2": a[1], "baseline_charging_mode": a[2]},
                       "cell_b": {"store_log2": b[0], "processors_log2": b[1], "baseline_charging_mode": b[2]},
                       "axes_differing": [x for x, d in [("store_log2", store_differs), ("processors_log2", p_differs), ("baseline_charging_mode", mode_differs)] if d],
                       "inert_axis_reasons": sorted(set(reasons)),
                       "two_mechanisms_reaching_one_number": bool(genuine)})
out["M1_collision_classification_20"] = classified
out["M1_collision_classification_summary"] = {
    "inert_axis_only": sum(1 for r in classified if not r["two_mechanisms_reaching_one_number"]),
    "genuinely_two_mechanisms": sum(1 for r in classified if r["two_mechanisms_reaching_one_number"]),
}

# ------------------------------------------------------------------ M2: ranges
STORE_DECLARED = [30, 40, 48, 60]
STORE_FULL = [0, 10, 20, 30, 40, 48, 60]
PARENT_METRICS = ["time_only", "time_memory_product"]
ALL_METRICS = codes["metric"]
m2 = {}
for storage in codes["storage_reading"]:
    for xover in ["persistent_crossover_n", "first_crossing_n", "crossover_n_parent_window_250_650"]:
        def val(label, store):
            return raw_cell(label, store, 0, "record_point_M1_w30", 1, 1, storage,
                            "unceiled_n_over_m_as_in_table3", "stage1_argmin")[xover]
        sd = [val("time_memory_product", s) for s in STORE_DECLARED]
        sf = [val("time_memory_product", s) for s in STORE_FULL]
        pm = [val(l, 30) for l in PARENT_METRICS]
        fm = [val(l, 30) for l in ALL_METRICS]

        def rng(vals):
            v = [x for x in vals if x is not None]
            return (max(v) - min(v)) if v else None, len(vals) - len(v), vals
        r_sd, n_sd, v_sd = rng(sd)
        r_sf, n_sf, v_sf = rng(sf)
        r_pm, n_pm, v_pm = rng(pm)
        r_fm, n_fm, v_fm = rng(fm)
        m2[f"{storage}/{xover}"] = {
            "store_declared_grid_range": r_sd, "store_declared_values": v_sd,
            "store_full_grid_range": r_sf, "store_full_values": v_sf,
            "parent_metric_set_range": r_pm, "parent_metric_values": v_pm,
            "full_metric_set_range": r_fm, "full_metric_nulls": n_fm,
            "C2_true_vs_parent_metric_set": (None if r_sd is None or r_pm is None else r_sd > r_pm),
            "C2_true_vs_full_metric_set": (None if r_sd is None or r_fm is None else r_sd > r_fm),
        }
out["M2_ranges"] = m2
# independent recomputation of the four declared-store crossovers, sparse + dense, persistent
m2_ind = {}
for storage in ["dense_row_echelon", "semaev_sparse"]:
    row = {}
    for s in STORE_FULL:
        r = cell_curves("time_memory_product", None, s, 0, "record_point_M1_w30", 1, 1, storage,
                        "unceiled_n_over_m_as_in_table3", "stage1_argmin")
        row[s] = {"persistent": r["persistent_crossover_n"], "first": r["first_crossing_n"],
                  "parent_window": r["crossover_n_parent_window_250_650"]}
    for l in PARENT_METRICS:
        fam, par = parse_metric(l)
        r = cell_curves(fam, par, 30, 0, "record_point_M1_w30", 1, 1, storage,
                        "unceiled_n_over_m_as_in_table3", "stage1_argmin")
        row[l] = {"persistent": r["persistent_crossover_n"], "first": r["first_crossing_n"]}
    m2_ind[storage] = row
out["M2_independent_recompute"] = m2_ind

# ------------------------------------------------------------------ M3: C3 decomposition
c3 = {}
for storage in codes["storage_reading"]:
    for kr in codes["k_reading"]:
        to = cell_curves("time_only", None, 30, 0, "record_point_M1_w30", 1, 1, storage, kr, "stage1_argmin")
        null = cell_curves("time_memory_product", None, 0, 0, "record_point_M1_w30", 1, 1, storage, kr, "stage1_argmin")
        rec = cell_curves("time_memory_product", None, 30, 0, "record_point_M1_w30", 1, 1, storage, kr, "stage1_argmin")
        c3[f"{storage}/{kr}"] = {
            "time_only_persistent": to["persistent_crossover_n"],
            "informative_null_store0_persistent": null["persistent_crossover_n"],
            "record_store30_persistent": rec["persistent_crossover_n"],
            "step1_semaev_memory_in_n": null["persistent_crossover_n"] - to["persistent_crossover_n"],
            "step2_baseline_store_in_n": rec["persistent_crossover_n"] - null["persistent_crossover_n"],
            "net_in_n": rec["persistent_crossover_n"] - to["persistent_crossover_n"],
            "margin_409_null": round(null["margin_409_bits"], 4),
            "margin_409_record": round(rec["margin_409_bits"], 4),
            "step1_bits_at_409": round(null["margin_409_bits"] - to["margin_409_bits"], 4),
            "step2_bits_at_409": round(rec["margin_409_bits"] - null["margin_409_bits"], 4),
            "sums": (null["persistent_crossover_n"] - to["persistent_crossover_n"]) + (rec["persistent_crossover_n"] - null["persistent_crossover_n"]) == rec["persistent_crossover_n"] - to["persistent_crossover_n"],
        }
out["M3_C3_decomposition"] = c3
# zero-memory comparator under product and under a budget metric
zm = {}
for fam, par in [("time_memory_product", None), ("fixed_budget_hard", 70.0), ("fixed_budget_soft", 40.0)]:
    Tv, Mv = vow_point(409, "zero_memory_comparator", 30, 0)
    bc = metric_cost(Tv, Mv, fam, par)
    zm[f"{fam}{'' if par is None else '[' + str(par) + ']'}"] = {
        "baseline_metric_cost_at_409": (bc if bc not in (INF, -INF) else str(bc)),
        "degenerate": bc == -INF}
out["M3_zero_memory_comparator"] = zm

# ------------------------------------------------------------------ M3: C4 free yield
c4 = []
for fam, par in [("time_only", None), ("time_memory_product", None), ("fixed_budget_hard", 70.0)]:
    for storage in codes["storage_reading"]:
        for msel in codes["m_selection"]:
            with_f = cell_curves(fam, par, 30, 0, "record_point_M1_w30", 1, 1, storage,
                                 "unceiled_n_over_m_as_in_table3", msel, free_yield=False)
            free = cell_curves(fam, par, 30, 0, "record_point_M1_w30", 1, 1, storage,
                               "unceiled_n_over_m_as_in_table3", msel, free_yield=True)
            def num(x):
                return x if isinstance(x, (int, float)) else None
            row = {"metric": fam if par is None else f"{fam}[budget_log2={int(par)}]",
                   "storage_reading": storage, "m_selection": msel,
                   "first_with": with_f["first_crossing_n"], "first_free": free["first_crossing_n"],
                   "persistent_with": with_f["persistent_crossover_n"], "persistent_free": free["persistent_crossover_n"],
                   "margin_409_with": with_f["margin_409_bits"] if not isinstance(with_f["margin_409_bits"], float) else round(with_f["margin_409_bits"], 4),
                   "margin_409_free": free["margin_409_bits"] if not isinstance(free["margin_409_bits"], float) else round(free["margin_409_bits"], 4),
                   "m_at_409_with": with_f["m_at_409"], "m_at_409_free": free["m_at_409"],
                   "floor_pinned": with_f["first_crossing_n"] == 3}
            a, b = num(with_f["margin_409_bits"]), num(free["margin_409_bits"])
            row["margin_moved_toward_semaev"] = (None if a is None or b is None else b > a)
            f1, f2 = with_f["first_crossing_n"], free["first_crossing_n"]
            row["first_moved_down"] = (None if f1 is None or f2 is None else f2 < f1)
            c4.append(row)
out["M3_C4_free_yield_at_record_point"] = c4
# the free-yield stage-1 argmin: is it m = 30?  and does m = 30 blow a 2^70 hard budget?
fy = {}
for n in [303, 409, 571]:
    ms = list(range(2, min(M_HI, n) + 1))
    mfree = min(ms, key=lambda mm: sem_time(n, mm, "unceiled_n_over_m_as_in_table3", free_yield=True)[1])
    mwith = min(ms, key=lambda mm: sem_time(n, mm, "unceiled_n_over_m_as_in_table3")[1])
    row = {"argmin_m_free_yield": mfree, "argmin_m_with_factor": mwith}
    for storage in ["rows_times_cols_dense", "semaev_sparse", "dense_row_echelon"]:
        rel, ws, _, _ = sem_mem(n, mfree, storage)
        row[f"mem_at_m_free_{storage}"] = round(log2_add(rel, ws), 4)
        row[f"exceeds_2^70_{storage}"] = log2_add(rel, ws) > 70.0
    fy[n] = row
out["M3_C4_free_yield_argmin_and_budget"] = fy

# ------------------------------------------------------------------ PTM object 1: time_only invariance
ptm1 = {}
for storage in codes["storage_reading"]:
    for mode in codes["baseline_charging_mode"]:
        vals = {}
        for s in STORE_FULL:
            r = cell_curves("time_only", None, s, 0, mode, 1, 1, storage,
                            "unceiled_n_over_m_as_in_table3", "stage1_argmin")
            vals[s] = r["persistent_crossover_n"]
        raws = {s: raw_cell("time_only", s, 0, mode, 1, 1, storage,
                            "unceiled_n_over_m_as_in_table3", "stage1_argmin")["persistent_crossover_n"]
                for s in STORE_FULL}
        ptm1[f"{storage}/{mode}"] = {"mine": vals, "run": raws,
                                     "spread_over_store_mine": max(vals.values()) - min(vals.values()),
                                     "spread_over_store_run": max(raws.values()) - min(raws.values()),
                                     "agree": vals == raws}
out["PTM1_time_only_invariance"] = ptm1
out["PTM1_across_readings_at_fixed_mode"] = {
    mode: sorted(set(ptm1[f"{s}/{mode}"]["mine"][30] for s in codes["storage_reading"]))
    for mode in codes["baseline_charging_mode"]}
out["PTM1_across_modes"] = {mode: ptm1[f"dense_row_echelon/{mode}"]["mine"][30]
                            for mode in codes["baseline_charging_mode"]}

# ------------------------------------------------------------------ PTM object 2: C4 at coherent mode
ptm2 = []
for storage in codes["storage_reading"]:
    for msel in codes["m_selection"]:
        for kr in codes["k_reading"]:
            wf = cell_curves("time_memory_product", None, 30, 0, "own_curve_product_minimum", 1, 1,
                             storage, kr, msel, free_yield=False)
            fr = cell_curves("time_memory_product", None, 30, 0, "own_curve_product_minimum", 1, 1,
                             storage, kr, msel, free_yield=True)
            ptm2.append({"metric": "time_memory_product", "mode": "own_curve_product_minimum",
                         "storage_reading": storage, "m_selection": msel, "k_reading": kr,
                         "first_with": wf["first_crossing_n"], "first_free": fr["first_crossing_n"],
                         "persistent_with": wf["persistent_crossover_n"], "persistent_free": fr["persistent_crossover_n"],
                         "margin_409_with": round(wf["margin_409_bits"], 4), "margin_409_free": round(fr["margin_409_bits"], 4),
                         "crossover_moved_down": fr["persistent_crossover_n"] < wf["persistent_crossover_n"],
                         "margin_moved_toward_semaev": fr["margin_409_bits"] > wf["margin_409_bits"],
                         "m_at_409_with": wf["m_at_409"], "m_at_409_free": fr["m_at_409"]})
out["PTM2_free_yield_at_coherent_mode"] = ptm2

# ------------------------------------------------------------------ M4: bands, soft semantics, alpha
def hard_verdict_at(n, b, storage, kr, mode, msel="metric_reoptimised"):
    ms = list(range(2, min(M_HI, n) + 1))
    best = None
    for mm in ms:
        rel, ws, _, _ = sem_mem(n, mm, storage)
        mem = log2_add(rel, ws)
        if mem > b:
            continue
        t, _ = sem_time(n, mm, kr)
        if best is None or t < best[0]:
            best = (t, mm, mem)
    Tv, Mv = vow_point(n, mode, 30, 0, budget=b)
    if best is None:
        return {"verdict": "vow", "semaev_feasible": False, "t_v": round(Tv, 4)}
    return {"verdict": "semaev" if Tv - best[0] > 0 else "vow", "semaev_feasible": True,
            "m": best[1], "t_s": round(best[0], 4), "t_v": round(Tv, 4)}


def soft_cost_at(n, b, storage, kr, mode, msel="metric_reoptimised"):
    ms = list(range(2, min(M_HI, n) + 1))
    best = None
    for mm in ms:
        rel, ws, _, _ = sem_mem(n, mm, storage)
        mem = log2_add(rel, ws)
        t, _ = sem_time(n, mm, kr)
        c = t + max(0.0, mem - b)
        if best is None or c < best[0]:
            best = (c, mm, mem, t)
    Tv, Mv = vow_point(n, mode, 30, 0, budget=b)
    bc = Tv + max(0.0, Mv - b)
    return {"verdict": "semaev" if bc - best[0] > 0 else "vow", "m": best[1],
            "semaev_cost": round(best[0], 4), "baseline_cost": round(bc, 4),
            "margin_bits": round(bc - best[0], 4)}


def flip(fn, storage, kr, mode, lo=20.0, hi=120.0, step=0.0001):
    prev, flips = None, []
    b = lo
    while b <= hi + 1e-12:
        v = fn(409, b, storage, kr, mode)["verdict"]
        if prev is not None and v != prev:
            flips.append([round(b, 4), f"{prev}->{v}"])
        prev = v
        b += step
    return flips


m4 = {}
for mode in ["record_point_M1_w30", "own_curve_product_minimum"]:
    for storage in ["dense_row_echelon", "semaev_sparse"]:
        m4[f"hard/{storage}/{mode}"] = flip(hard_verdict_at, storage, "unceiled_n_over_m_as_in_table3", mode, 55.0, 95.0, 0.0002)
        m4[f"soft/{storage}/{mode}"] = flip(soft_cost_at, storage, "unceiled_n_over_m_as_in_table3", mode, 20.0, 60.0, 0.0002)
out["M4_flip_budgets_at_409"] = m4
# cheapest memory over m at 409 with the run's relation-store convention
m4c = {}
for storage in codes["storage_reading"]:
    vals = {}
    for mm in range(2, M_HI + 1):
        rel, ws, _, _ = sem_mem(409, mm, storage)
        vals[mm] = round(log2_add(rel, ws), 4)
    mstar = min(vals, key=vals.get)
    m4c[storage] = {"cheapest_m": mstar, "cheapest_mem_log2": vals[mstar],
                    "within_1_bit": [mm for mm in vals if vals[mm] <= vals[mstar] + 1.0],
                    "by_m_2_to_14": {mm: vals[mm] for mm in range(2, 15)}}
out["M4_cheapest_memory_over_m_at_409_run_convention"] = m4c
# alpha flips
alpha = {}
for storage in codes["storage_reading"]:
    m = min(range(2, M_HI + 1), key=lambda mm: sem_time(409, mm, "unceiled_n_over_m_as_in_table3")[1])
    t_s, _ = sem_time(409, m, "unceiled_n_over_m_as_in_table3")
    rel, ws, _, _ = sem_mem(409, m, storage)
    mem_s = log2_add(rel, ws)
    Tv, Mv = vow_point(409, "record_point_M1_w30", 30, 0)
    a = (Tv - t_s) / (mem_s - Mv)
    alpha[storage] = {"alpha_flip": round(a, 4), "m": m, "t_s": round(t_s, 4), "mem_s": round(mem_s, 4),
                      "t_v": round(Tv, 4), "mem_v": round(Mv, 4), "inside_0_1": 0.0 <= a <= 1.0}
out["M4_alpha_flips_record_point_409"] = alpha

with open(OUT, "w") as f:
    json.dump(out, f, indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in
                  ("M1_twelve_cells", "M1_collision_classification_20", "M2_ranges",
                   "M3_C4_free_yield_at_record_point", "PTM1_time_only_invariance", "PTM2_free_yield_at_coherent_mode")},
                 indent=1, default=str))
print("TWELVE worst:", out["M1_twelve_cells"]["worst_margin_disagreement_bits"],
      out["M1_twelve_cells"]["all_crossovers_agree"], out["M1_twelve_cells"]["all_intervals_agree"],
      out["M1_twelve_cells"]["all_m_agree"])
print("wrote", OUT)
