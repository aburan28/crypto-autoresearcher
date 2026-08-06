"""
analysis.py -- pre-registered decision-table logic (spec.decision_table), applied
exactly as frozen: no post-hoc threshold tuning, no new branches invented.

Primary meters (spec.inputs.meters_primary):
  semaev_m3_relation_density        -- HIGHER is anomalous; R = max/median
  semaev_m4_relation_density        -- HIGHER is anomalous; R = max/median
  fb_decomposition_probability      -- HIGHER is anomalous; R = max/median
  macaulay_rank_defect_at_first_fall-- HIGHER is anomalous; R = max/median
  groebner_solving_degree_d_reg     -- LOWER is anomalous; delta_d = median - min

R >= 100 or delta_d >= 2 is the frozen outlier threshold (spec.preregistered_prediction
/ decision_table). When a meter's class median is exactly 0, [0.1,10]x-median
homogeneity collapses to "every value must be 0" (the natural interpretation of a
0-width band around 0); a single nonzero value against an all-zero background is
recorded as an (unbounded-ratio) outlier candidate, not silently dropped.
"""
import statistics

HIGH_METERS = [
    "semaev_m3_relation_density",
    "semaev_m4_relation_density",
    "fb_decomposition_probability",
    "macaulay_rank_defect_at_first_fall",
]
LOW_METER = "groebner_solving_degree_d_reg"
ALL_PRIMARY = HIGH_METERS + [LOW_METER]
RATIO_THRESHOLD = 100
DELTA_D_THRESHOLD = 2


def _high_meter_stat(values_by_idx):
    """values_by_idx: dict curve_idx -> value (Nones filtered out / reported censored)."""
    observed = {i: v for i, v in values_by_idx.items() if v is not None}
    censored = [i for i, v in values_by_idx.items() if v is None]
    if not observed:
        return {"median": None, "max": None, "argmax": None, "ratio": None,
                "outlier_hit": False, "censored_curves": censored}
    vals = list(observed.values())
    median = statistics.median(vals)
    max_val = max(vals)
    argmax = [i for i, v in observed.items() if v == max_val]
    if median == 0:
        ratio = None if max_val == 0 else float("inf")
        outlier_hit = max_val > 0
    else:
        ratio = max_val / median
        outlier_hit = ratio >= RATIO_THRESHOLD
    return {"median": median, "max": max_val, "argmax": argmax, "ratio": ratio,
            "outlier_hit": outlier_hit, "censored_curves": censored}


def _low_meter_stat(values_by_idx):
    observed = {i: v for i, v in values_by_idx.items() if v is not None}
    censored = [i for i, v in values_by_idx.items() if v is None]
    if not observed:
        return {"median": None, "min": None, "argmin": None, "delta_d": None,
                "outlier_hit": False, "censored_curves": censored}
    vals = list(observed.values())
    median = statistics.median(vals)
    min_val = min(vals)
    argmin = [i for i, v in observed.items() if v == min_val]
    delta = median - min_val
    outlier_hit = delta >= DELTA_D_THRESHOLD
    return {"median": median, "min": min_val, "argmin": argmin, "delta_d": delta,
            "outlier_hit": outlier_hit, "censored_curves": censored}


def per_meter_stats(curve_records):
    """curve_records: list of per-curve meter dicts (index = curve index in class)."""
    stats = {}
    for m in HIGH_METERS:
        vals = {i: rec.get(m) for i, rec in enumerate(curve_records)}
        stats[m] = _high_meter_stat(vals)
    vals = {i: rec.get(LOW_METER) for i, rec in enumerate(curve_records)}
    stats[LOW_METER] = _low_meter_stat(vals)
    return stats


def check_planted_recovered(stats, planted_index):
    """CTRL-PLANTED-OUTLIER: is the designated planted curve the (a) argmax on any
    HIGH meter with outlier_hit True, or (b) argmin on the LOW meter with
    outlier_hit True?"""
    hits = []
    for m in HIGH_METERS:
        s = stats[m]
        if s["outlier_hit"] and s["argmax"] and planted_index in s["argmax"]:
            hits.append(m)
    s = stats[LOW_METER]
    if s["outlier_hit"] and s["argmin"] and planted_index in s["argmin"]:
        hits.append(LOW_METER)
    return {"recovered": len(hits) > 0, "meters_showing_it": hits}


def permutation_stability_check(curve_records, meter_name, rng, n_trials=5):
    """CTRL-PERMUTATION / TAIL-ECTD-PERM-STABLE: shuffle the value<->label mapping,
    re-identify the argmax/argmin under the shuffled labeling, undo the shuffle, and
    check the recovered original index is still among the TRUE argmax/argmin set.
    Ties are handled by set-membership (not a single canonical index)."""
    n = len(curve_records)
    is_low = meter_name == LOW_METER
    values = [rec.get(meter_name) for rec in curve_records]
    idxs_with_value = [i for i, v in enumerate(values) if v is not None]
    if len(idxs_with_value) < 2:
        return {"stable": True, "trials": 0, "note": "fewer than 2 observed values; trivially stable"}
    observed_vals = [values[i] for i in idxs_with_value]
    target = min(observed_vals) if is_low else max(observed_vals)
    true_winners = {idxs_with_value[k] for k, v in enumerate(observed_vals) if v == target}
    all_stable = True
    trial_results = []
    for t in range(n_trials):
        perm = list(range(len(idxs_with_value)))
        rng.shuffle(perm)
        shuffled_vals = [observed_vals[perm[k]] for k in range(len(perm))]
        winner_target = min(shuffled_vals) if is_low else max(shuffled_vals)
        winners_shuffled_pos = [k for k, v in enumerate(shuffled_vals) if v == winner_target]
        recovered_original = {idxs_with_value[perm[k]] for k in winners_shuffled_pos}
        stable = recovered_original.issubset(true_winners) and len(recovered_original) > 0
        trial_results.append({"recovered": sorted(recovered_original), "stable": stable})
        all_stable = all_stable and stable
    return {"stable": all_stable, "trials": n_trials, "true_winners": sorted(true_winners),
            "trial_results": trial_results}


def outside_class_null_gate(real_stats, outside_curve_records):
    """CTRL-OUTSIDE-CLASS: recompute the same per-meter stats on the outside-class
    sample; gate passes for a meter iff the outside-class sample does NOT also clear
    the outlier threshold at the same rate."""
    outside_stats = per_meter_stats(outside_curve_records)
    gates = {}
    for m in ALL_PRIMARY:
        real_hit = real_stats[m]["outlier_hit"]
        null_hit = outside_stats[m]["outlier_hit"]
        gates[m] = {
            "real_outlier_hit": real_hit,
            "null_also_hits": null_hit,
            "gate_pass": (not real_hit) or (not null_hit),
        }
    return {"outside_class_stats": outside_stats, "gates": gates}


def _exceeds(real, null):
    """True iff `real` advantage strictly exceeds `null` advantage, with clean
    handling of None (no signal -> any real signal exceeds it) and inf (unbounded
    ratio from a zero-median class)."""
    if real is None:
        return False
    if null is None:
        return True
    if real == float("inf"):
        return null != float("inf")
    if null == float("inf"):
        return False
    return real > null


def degree_profile_null_gate(real_stats, null_records):
    """CTRL-DEGREE-PROFILE: applies to the two algebraic-complexity meters
    (groebner d_reg, macaulay rank defect); real outlier advantage must exceed the
    null's own advantage computed over the same shaped random systems."""
    null_stats_gb = _low_meter_stat({i: rec.get(LOW_METER) for i, rec in enumerate(null_records)})
    null_stats_mac = _high_meter_stat({i: rec.get("macaulay_rank_defect_at_first_fall")
                                        for i, rec in enumerate(null_records)})
    gates = {}
    real_gb = real_stats[LOW_METER]
    gates[LOW_METER] = {
        "real_delta_d": real_gb["delta_d"],
        "null_delta_d": null_stats_gb["delta_d"],
        "gate_pass": (not real_gb["outlier_hit"]) or _exceeds(real_gb["delta_d"], null_stats_gb["delta_d"]),
    }
    real_mac = real_stats["macaulay_rank_defect_at_first_fall"]
    gates["macaulay_rank_defect_at_first_fall"] = {
        "real_ratio": real_mac["ratio"],
        "null_ratio": null_stats_mac["ratio"],
        "gate_pass": (not real_mac["outlier_hit"]) or _exceeds(real_mac["ratio"], null_stats_mac["ratio"]),
    }
    return {"null_stats": {LOW_METER: null_stats_gb,
                            "macaulay_rank_defect_at_first_fall": null_stats_mac},
            "gates": gates}


def confirmed_outlier_meters(stats, planted_index, permutation_results,
                              outside_gate_gates=None, degprofile_gate_gates=None):
    """A meter counts as a genuine (non-planted) heavy-tail hit only if ALL of:
    outlier_hit, the winning curve(s) exclude the planted index, permutation-stable,
    and (when the corresponding null gate was computed) the null gate passes. This
    directly operationalizes spec.decision_table's heavy_tail_hit condition
    ('>=1 class with R>=100 or delta_d>=2, permutation-stable, nulls pass, planted
    control recovered') at the per-meter level."""
    confirmed = []
    for m in ALL_PRIMARY:
        s = stats[m]
        if not s["outlier_hit"]:
            continue
        winners = s.get("argmax") if m in HIGH_METERS else s.get("argmin")
        if not winners or all(idx == planted_index for idx in winners):
            continue  # only the planted curve shows it -- not a "real" hit
        if not permutation_results.get(m, {}).get("stable", False):
            continue
        if outside_gate_gates is not None and not outside_gate_gates.get(m, {}).get("gate_pass", True):
            continue
        if degprofile_gate_gates is not None and m in degprofile_gate_gates:
            if not degprofile_gate_gates[m].get("gate_pass", True):
                continue
        confirmed.append(m)
    return confirmed


def class_factor10_homogeneous(stats):
    """scoped_homogeneity ingredient: every primary meter's values lie within
    [0.1,10]x class median (median==0 collapses to 'all values are 0')."""
    for m in HIGH_METERS:
        s = stats[m]
        if s["outlier_hit"]:
            return False
    if stats[LOW_METER]["outlier_hit"]:
        return False
    return True
