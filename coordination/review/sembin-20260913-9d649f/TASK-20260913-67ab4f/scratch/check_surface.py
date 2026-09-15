#!/usr/bin/env python3
"""M1(2)(3)(4), M2, proves_too_much object 1 -- all read from raw-result.json / surface.json and
recomputed with own_model.py."""
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

import own_model as om

RUN = "/workspace/experiments/EXP-SEMBIN-2c40bb/runs/RUN-SEMBIN-3ae91c"
out = {}

raw = json.load(open(os.path.join(RUN, "raw-result.json")))
codes, fields, cells = raw["codes"], raw["cell_fields"], raw["cells"]
F = {f: i for i, f in enumerate(fields)}


def decode(c):
    d = dict(zip(fields, c))
    for k in ("metric", "baseline_charging_mode", "storage_reading", "k_reading", "m_selection"):
        d[k] = codes[k][d[k]]
    return d


def fam_par(metric):
    if "[" not in metric:
        return metric, None
    fam, rest = metric.split("[")
    return fam, float(rest.split("=")[1].rstrip("]"))


# ------------------------------------------------------------------ M1(2): 12 cells
random.seed(20260915)
chosen_idx = []
# deliberate picks across metrics / stores / kappa / cofactor / modes / readings / k / m_sel
def find(**want):
    for i, c in enumerate(cells):
        d = decode(c)
        if all(d[k] == v for k, v in want.items()):
            return i
    raise KeyError(want)

picks = [
    dict(metric="time_memory_product", store_log2=40, processors_log2=0, baseline_charging_mode="record_point_M1_w30", kappa=1, cofactor_h=1, storage_reading="semaev_sparse", k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin"),
    dict(metric="time_memory_product", store_log2=60, processors_log2=20, baseline_charging_mode="record_point_M1_w30", kappa=10, cofactor_h=2, storage_reading="dense_row_echelon", k_reading="ceil_n_over_m", m_selection="metric_reoptimised"),
    dict(metric="memory_weighted_time_alpha[alpha=0.5]", store_log2=30, processors_log2=0, baseline_charging_mode="record_point_M1_w30", kappa=100, cofactor_h=1, storage_reading="rows_times_cols_dense", k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin"),
    dict(metric="memory_weighted_time_alpha[alpha=0.811]", store_log2=30, processors_log2=0, baseline_charging_mode="record_point_M1_w30", kappa=1, cofactor_h=1, storage_reading="dense_row_echelon", k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin"),
    dict(metric="fixed_budget_hard[budget_log2=70]", store_log2=30, processors_log2=0, baseline_charging_mode="own_curve_product_minimum", kappa=1, cofactor_h=1, storage_reading="semaev_sparse", k_reading="unceiled_n_over_m_as_in_table3", m_selection="metric_reoptimised"),
    dict(metric="fixed_budget_hard[budget_log2=80]", store_log2=48, processors_log2=40, baseline_charging_mode="sect113r2_calibrated_ratio", kappa=10, cofactor_h=4, storage_reading="dense_row_echelon", k_reading="unceiled_n_over_m_as_in_table3", m_selection="metric_reoptimised"),
    dict(metric="fixed_budget_soft[budget_log2=40]", store_log2=30, processors_log2=0, baseline_charging_mode="record_point_M1_w30", kappa=1, cofactor_h=1, storage_reading="dense_row_echelon", k_reading="unceiled_n_over_m_as_in_table3", m_selection="metric_reoptimised"),
    dict(metric="fixed_budget_soft[budget_log2=65]", store_log2=10, processors_log2=20, baseline_charging_mode="own_curve_product_minimum", kappa=100, cofactor_h=2, storage_reading="nonzeros_with_index_sparse", k_reading="ceil_n_over_m", m_selection="stage1_argmin"),
    dict(metric="time_only", store_log2=0, processors_log2=40, baseline_charging_mode="sect113r2_calibrated_ratio", kappa=100, cofactor_h=4, storage_reading="semaev_sparse", k_reading="ceil_n_over_m", m_selection="metric_reoptimised"),
    dict(metric="time_memory_product", store_log2=20, processors_log2=0, baseline_charging_mode="sect113r2_calibrated_ratio", kappa=1, cofactor_h=1, storage_reading="nonzeros_with_index_sparse", k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin"),
    dict(metric="time_memory_product", store_log2=30, processors_log2=0, baseline_charging_mode="own_curve_product_minimum", kappa=1, cofactor_h=1, storage_reading="dense_row_echelon", k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin"),
    dict(metric="memory_weighted_time_alpha[alpha=1.0]", store_log2=48, processors_log2=20, baseline_charging_mode="record_point_M1_w30", kappa=10, cofactor_h=4, storage_reading="semaev_sparse", k_reading="ceil_n_over_m", m_selection="metric_reoptimised"),
]
table12, worst = [], 0.0
for want in picks:
    i = find(**want)
    d = decode(cells[i])
    fam, par = fam_par(d["metric"])
    r = om.compare(fam, par, d["storage_reading"], d["k_reading"] == "ceil_n_over_m", d["store_log2"],
                   d["processors_log2"], d["baseline_charging_mode"], d["kappa"], d["cofactor_h"], d["m_selection"])
    def num(x):
        return x if isinstance(x, (int, float)) else None
    diffs = []
    for mine, theirs in ((r["margin_409"], d["margin_409_bits"]), (r["margin_571"], d["margin_571_bits"])):
        if isinstance(theirs, str) or theirs is None:
            diffs.append("n/a" if (mine in (None, om.INF, -om.INF)) else f"MISMATCH mine={mine}")
        else:
            diffs.append(abs(mine - theirs))
            worst = max(worst, abs(mine - theirs))
    row = {"cell": want, "run": {k: d[k] for k in ("first_crossing_n", "persistent_crossover_n", "crossover_n_parent_window_250_650", "margin_409_bits", "margin_571_bits", "m_at_409", "m_at_571")},
           "mine": {"first": r["first"], "persistent": r["persistent"], "parent_window": r["parent_window"],
                    "margin_409": r["margin_409"], "margin_571": r["margin_571"], "m_409": r["m_409"], "m_571": r["m_571"]},
           "crossovers_agree": (r["first"] == d["first_crossing_n"] and r["persistent"] == d["persistent_crossover_n"]
                                and r["parent_window"] == d["crossover_n_parent_window_250_650"]),
           "margin_abs_diff_409_571_bits": diffs}
    table12.append(row)
out["M1_2_twelve_cells"] = {"rows": table12, "worst_margin_disagreement_bits": worst,
                            "all_crossovers_agree": all(r["crossovers_agree"] for r in table12)}

# ------------------------------------------------------------------ M1(3): collision count
key_fields = ("metric", "storage_reading", "k_reading", "kappa", "cofactor_h", "m_selection")
groups = defaultdict(list)
for i, c in enumerate(cells):
    groups[tuple(c[F[k]] for k in key_fields)].append(i)
total_pairs_nonnull, total_pairs_incl_null, pair_samples = 0, 0, []
for g, idxs in groups.items():
    byval = defaultdict(list)
    for i in idxs:
        byval[cells[i][F["persistent_crossover_n"]]].append(i)
    for v, lst in byval.items():
        npairs = len(lst) * (len(lst) - 1) // 2
        total_pairs_incl_null += npairs
        if v is not None:
            total_pairs_nonnull += npairs
            if npairs and len(pair_samples) < 200000:
                pair_samples.append((g, v, lst))
out["M1_3_collisions"] = {"run_total": json.load(open(os.path.join(RUN, "surface.json")))["collisions"]["total_colliding_pairs"],
                          "mine_nonnull_persistent": total_pairs_nonnull, "mine_including_null": total_pairs_incl_null}

# classify 20 sampled pairs
random.seed(7)
def classify(a, b):
    da, db = decode(a), decode(b)
    diff = [k for k in ("store_log2", "processors_log2", "baseline_charging_mode") if da[k] != db[k]]
    fam, _ = fam_par(da["metric"])
    reasons = []
    if fam == "time_only":
        reasons.append("time_only ignores store and mode-memory; store/mode axis does not act")
        if "processors_log2" in diff:
            reasons.append("processors shift both sides by p under time_only: axis does not act")
    if "store_log2" in diff and da["baseline_charging_mode"] == db["baseline_charging_mode"] and da["baseline_charging_mode"] != "record_point_M1_w30":
        reasons.append("store_log2 ignored by non-record mode: axis does not act")
    if "store_log2" in diff and fam.startswith("fixed_budget"):
        reasons.append("budget caps the store; store axis may not act (check)")
    if not reasons:
        # recompute margins to see whether the curves are genuinely different (two mechanisms) or saw-tooth pinned
        fa, pa = fam_par(da["metric"])
        ra = om.compare(fa, pa, da["storage_reading"], da["k_reading"] == "ceil_n_over_m", da["store_log2"], da["processors_log2"], da["baseline_charging_mode"], da["kappa"], da["cofactor_h"], da["m_selection"])
        rb = om.compare(fa, pa, db["storage_reading"], db["k_reading"] == "ceil_n_over_m", db["store_log2"], db["processors_log2"], db["baseline_charging_mode"], db["kappa"], db["cofactor_h"], db["m_selection"])
        if ra["margin_409"] == rb["margin_409"] or (isinstance(ra["margin_409"], float) and isinstance(rb["margin_409"], float) and abs(ra["margin_409"] - rb["margin_409"]) < 1e-9):
            reasons.append("margins identical: axes cancel exactly (e.g. store-p under record product where ws dominates)")
        else:
            reasons.append(f"GENUINELY DIFFERENT CURVES sharing a crossover (margins 409: {ra['margin_409']} vs {rb['margin_409']}); saw-tooth/pinning candidate")
    return diff, reasons
sample_rows = []
picked = random.sample(pair_samples, 20)
for g, v, lst in picked:
    a, b = random.sample(lst, 2)
    diff, reasons = classify(cells[a], cells[b])
    da = decode(cells[a]); db = decode(cells[b])
    sample_rows.append({"shared": dict(zip(key_fields, [codes[k][x] if k in codes else x for k, x in zip(key_fields, g)])),
                        "persistent_crossover_n": v,
                        "cell_a": {k: da[k] for k in ("store_log2", "processors_log2", "baseline_charging_mode")},
                        "cell_b": {k: db[k] for k in ("store_log2", "processors_log2", "baseline_charging_mode")},
                        "differing_axes": diff, "classification": reasons})
out["M1_3_sample_20"] = sample_rows
out["M1_3_sample_summary"] = Counter("genuine" if any("GENUINELY" in r for r in s["classification"]) else
                                     ("exact_cancel" if any("identical" in r for r in s["classification"]) else "axis_does_not_act")
                                     for s in sample_rows)

# ------------------------------------------------------------------ M1(4): determinism hashes
det = json.load(open(os.path.join(RUN, "determinism-check.json")))
hashes = []
for f in det["files_compared"]:
    h = hashlib.sha256(open(os.path.join(RUN, f["file"]), "rb").read()).hexdigest()
    hashes.append({"file": f["file"], "my_sha256_of_retained_file": h, "exec1": f["sha256_execution_1"], "exec2": f["sha256_execution_2"],
                   "retained_equals_exec1": h == f["sha256_execution_1"], "retained_equals_exec2": h == f["sha256_execution_2"]})
out["M1_4_determinism"] = {"rows": hashes, "all_match": all(r["retained_equals_exec1"] and r["retained_equals_exec2"] for r in hashes),
                           "note": "second-execution copies were deleted by the producer; only the retained files can be hashed. An independent re-execution is done separately (rerun_determinism)."}

# ------------------------------------------------------------------ M2: ranges
def cells_where(**want):
    outl = []
    for c in cells:
        d = decode(c)
        if all(d[k] == v for k, v in want.items()):
            outl.append(d)
    return outl

base = dict(processors_log2=0, kappa=1, cofactor_h=1, baseline_charging_mode="record_point_M1_w30",
            k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin")
parent_set = ["time_only", "time_memory_product"]   # the parent's 4 metrics collapse to these two values (AT == product, max == time-only)
full_set = codes["metric"]
m2 = {}
for st in om.STORAGES:
    m2[st] = {}
    for cdef in ("persistent_crossover_n", "first_crossing_n"):
        def rng(vals):
            v = [x for x in vals if x is not None]
            return {"min": min(v) if v else None, "max": max(v) if v else None, "range": (max(v) - min(v)) if v else None,
                    "n_null": len(vals) - len(v), "values": vals}
        store_vals = [cells_where(metric="time_memory_product", store_log2=s, storage_reading=st, **base)[0][cdef] for s in (30, 40, 48, 60)]
        parent_vals = [cells_where(metric=mt, store_log2=30, storage_reading=st, **base)[0][cdef] for mt in parent_set]
        full_vals = [cells_where(metric=mt, store_log2=30, storage_reading=st, **base)[0][cdef] for mt in full_set]
        rs, rp, rf = rng(store_vals), rng(parent_vals), rng(full_vals)
        m2[st][cdef] = {"store_declared_grid": rs, "parent_metric_set": rp, "full_metric_set_28": rf,
                        "C2_true_vs_parent_set": (rs["range"] > rp["range"]) if None not in (rs["range"], rp["range"]) else None,
                        "C2_true_vs_full_set": (rs["range"] > rf["range"]) if None not in (rs["range"], rf["range"]) else None}
out["M2_ranges"] = m2
# my own recomputation of the store range (persistent + first) for dense and sparse, independent of raw
own = {}
for st in ("dense_row_echelon", "semaev_sparse"):
    rows = {}
    for s in (30, 40, 48, 60):
        r = om.compare("time_memory_product", None, st, False, s, 0, "record_point_M1_w30", 1, 1, "stage1_argmin")
        rows[s] = {"first": r["first"], "persistent": r["persistent"], "intervals": r["intervals"]}
    t = om.compare("time_only", None, st, False, 30, 0, "record_point_M1_w30", 1, 1, "stage1_argmin")
    own[st] = {"product_by_store": rows, "time_only": {"first": t["first"], "persistent": t["persistent"]}}
out["M2_own_recompute"] = own

# ------------------------------------------------------------------ proves_too_much object 1: time_only
ptm = defaultdict(dict)
for st in om.STORAGES:
    for mode in codes["baseline_charging_mode"]:
        vals = {}
        for s in (0, 10, 20, 30, 40, 48, 60):
            d = cells_where(metric="time_only", store_log2=s, storage_reading=st, processors_log2=0, kappa=1, cofactor_h=1,
                            baseline_charging_mode=mode, k_reading="unceiled_n_over_m_as_in_table3", m_selection="stage1_argmin")[0]
            vals[s] = (d["first_crossing_n"], d["persistent_crossover_n"], d["margin_409_bits"])
        ptm[st][mode] = vals
distinct = {st: {mode: sorted(set(v for v in vals.values())) for mode, vals in modes.items()} for st, modes in ptm.items()}
allvals = set()
for st in ptm:
    for mode in ptm[st]:
        for v in ptm[st][mode].values():
            allvals.add((v[0], v[1]))
out["PTM1_time_only"] = {"per_storage_mode_distinct_values": distinct, "all_distinct_crossovers_first_persistent": sorted(allvals),
                         "my_own_time_only": {mode: om.compare("time_only", None, "dense_row_echelon", False, 30, 0, mode, 1, 1, "stage1_argmin")["persistent"] for mode in codes["baseline_charging_mode"]}}

json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in ("M1_3_sample_20", "M1_2_twelve_cells", "M1_4_determinism", "M2_own_recompute")}, indent=1, default=str)[:9000])
print("12-cell worst margin disagreement (bits):", out["M1_2_twelve_cells"]["worst_margin_disagreement_bits"], "all crossovers agree:", out["M1_2_twelve_cells"]["all_crossovers_agree"])
for r in table12:
    print(" ", r["crossovers_agree"], r["margin_abs_diff_409_571_bits"], r["run"]["persistent_crossover_n"], r["mine"]["persistent"], r["cell"]["metric"], r["cell"]["storage_reading"], r["cell"]["store_log2"], r["cell"]["baseline_charging_mode"])
print("determinism all match:", out["M1_4_determinism"]["all_match"])
print("own M2:", json.dumps(own, default=str)[:1500])
