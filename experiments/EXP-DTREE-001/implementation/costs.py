"""RUN-DTREE-003 through RUN-DTREE-011: single-level cost (C1), depth-2 cost
(C2), medium-base log-table preprocessing cost, the matched rho baseline, and
decomposition-probability sampling with the generic-heuristic control.

Every "does this decompose" answer is the FAST EXACT test (curvegroup.py,
ground truth, decoupled from Groebner's performance -- see curvegroup.py's
module docstring). Every C_solve(k) reported number is a REAL subprocess-
isolated Groebner wall-clock measurement (gb_isolated.py), hard-capped at 20s
per CTRL-FAILED-DESCENT ("capped solves count at full cap cost as
failures") -- never modeled, never extrapolated in place of a measurement.
"""
from __future__ import annotations

import math
import random

import numpy as np

from harness.toycurve import EllipticCurve
import curvegroup as cg
import gb_isolated

CAP_SECONDS = 20.0
Z_95 = 1.959963984540054


# --------------------------------------------------------------------------
# Reconstruction helpers
# --------------------------------------------------------------------------

def curve_of(rec: dict) -> EllipticCurve:
    return EllipticCurve(rec["p"], rec["a"], rec["b"])


def targets_of(rec: dict) -> list[dict]:
    return rec["targets"]


def medium_base(rec: dict, mult: int) -> list[int]:
    return rec["medium_bases"][mult]["factor_base"]


# --------------------------------------------------------------------------
# Wilson score interval
# --------------------------------------------------------------------------

def wilson_interval(successes: int, n: int, z: float = Z_95) -> dict:
    if n == 0:
        return {"successes": 0, "n": 0, "phat": None, "lo": None, "hi": None}
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    return {"successes": successes, "n": n, "phat": phat,
            "lo": max(0.0, center - half), "hi": min(1.0, center + half)}


# --------------------------------------------------------------------------
# One decomposition attempt: fast-exact ground truth + capped Groebner cost.
# --------------------------------------------------------------------------

def attempt(E: EllipticCurve, V: list[int], R, arity: int,
            pairsum_index, p: int, a: int, b: int) -> dict:
    if arity == 2:
        found, witness = cg.decompose_arity2(E, V, R)
    elif arity == 3:
        if pairsum_index is None:
            return {"fast_found": None, "fast_witness": None,
                    "fast_skipped_reason": "pairsum index unavailable (infeasible_within_budget)",
                    "gb": None}
        found, witness = cg.decompose_arity3(E, V, R, pairsum_index)
    else:
        raise ValueError(arity)
    if R is None:
        # The target is the identity O, which has no x-coordinate: the
        # standard Semaev embedding S_{arity+1}(x1,...,x_arity, x_R) = 0
        # requires x_R, so this specific target cannot be posed to the
        # Groebner solver as constructed (that would need the DIFFERENT
        # system S_arity(x1,...,x_arity) = 0 with no target slot, which this
        # experiment does not implement). The fast-exact ground-truth test
        # above is unaffected and still reports a real, checked answer; only
        # the Groebner COST sample is skipped for this one target, recorded
        # explicitly rather than silently omitted or faked.
        #
        # No formal certificate is emitted here even when found=True:
        # harness.semaev.verify_decomposition_certificate does
        # `tuple(st["target"])`, which raises TypeError on a None target (an
        # affine [x,y] pair is all it is written to expect) -- shared code
        # this experiment does not modify. Rather than pass it an input
        # shape it cannot handle (crashing verification instead of cleanly
        # failing it), the raw found/witness fields are still recorded in
        # full, just not routed through certificate verification.
        return {"fast_found": found,
                "fast_witness_x": [pt[0] for pt in witness] if found else [],
                "certificate": None, "gb": None,
                "identity_target_witness_uncertified": ([pt[0] for pt in witness] if found else None),
                "gb_skipped_reason": "target is the identity point O (no x-coordinate); "
                                      "the S_{k+1}(...,x_R)=0 Semaev embedding this experiment "
                                      "implements requires a target x-coordinate"}
    gb = gb_isolated.capped_solve(arity, p, a, b, V, R[0], cap_seconds=CAP_SECONDS)
    cert = None
    if found:
        cert = {
            "kind": "decomposition",
            "curve_id": None,
            "statement": {
                "target": list(R),
                "summands": [list(pt) for pt in witness],
                "curve": {"p": p, "a": a, "b": b},
            },
        }
    return {"fast_found": found,
            "fast_witness_x": [pt[0] for pt in witness] if found else [],
            "certificate": cert, "gb": gb}


def gb_cost_series(attempts: list[dict]) -> list[float]:
    """Every attempt contributes its Groebner seconds -- real time if
    completed, else the full cap (CTRL-FAILED-DESCENT). None only for
    attempts that could not even be tried (fast-exact infeasible)."""
    out = []
    for a in attempts:
        gb = a.get("gb")
        if gb is None:
            continue
        out.append(gb["groebner_seconds"])
    return out


def summarize_costs(costs: list[float]) -> dict:
    if not costs:
        return {"n": 0, "mean": None, "median": None, "iqr": None}
    arr = np.array(costs, dtype=float)
    return {"n": len(costs), "mean": float(arr.mean()), "median": float(np.median(arr)),
            "iqr": [float(np.percentile(arr, 25)), float(np.percentile(arr, 75))],
            "min": float(arr.min()), "max": float(arr.max())}


# --------------------------------------------------------------------------
# RUN-DTREE-003/4/5: single-level C1
# --------------------------------------------------------------------------

def run_single_level(rec: dict, cumulative_cap_seconds: float = 1500.0) -> dict:
    E = curve_of(rec)
    B = rec["standard_B"]
    V = rec["standard_factor_base"]
    p, a, b = rec["p"], rec["a"], rec["b"]

    pairsum, pairsum_info = cg.build_pairsum_index_or_skip(E, V)

    targets = targets_of(rec)
    per_target = []
    cumulative_gb_seconds = 0.0
    censored_by_budget = []
    for t in targets:
        if cumulative_gb_seconds >= cumulative_cap_seconds:
            censored_by_budget.append(t["index"])
            continue
        R = tuple(t["R"]) if t["R"] is not None else None
        res = attempt(E, V, R, 3, pairsum, p, a, b)
        rec_out = {"target_index": t["index"], **res}
        per_target.append(rec_out)
        if res["gb"] is not None:
            cumulative_gb_seconds += res["gb"]["groebner_seconds"]

    found_count = sum(1 for r in per_target if r["fast_found"])
    n_measured = len(per_target)
    p_dec = (found_count / n_measured) if n_measured else None
    costs = gb_cost_series(per_target)
    c_solve_summary = summarize_costs(costs)
    c1 = (c_solve_summary["mean"] / p_dec) if (p_dec and p_dec > 0 and c_solve_summary["mean"] is not None) else None

    return {
        "standard_B": B, "pairsum_index_info": pairsum_info,
        "n_targets_requested": len(targets), "n_measured": n_measured,
        "censored_by_budget": censored_by_budget,
        "cumulative_gb_seconds": cumulative_gb_seconds,
        "per_target": per_target,
        "decomposition_found_count": found_count,
        "p_dec_m3_B": p_dec,
        "c_solve_m3": c_solve_summary,
        "c1_single_level": c1,
        "c1_undefined_reason": None if c1 is not None else "p_dec is 0 or unmeasured; C1 = C_solve/P is not computable",
    }


# --------------------------------------------------------------------------
# RUN-DTREE-006/7/8: depth-2 C2
# --------------------------------------------------------------------------

FROZEN_CONFIG_ORDER = [(2, mult) for mult in (2, 4, 8, 16)] + [(3, mult) for mult in (2, 4, 8, 16)]


def config_key(m_prime: int, mult: int) -> str:
    """String key for a (m', B_med multiplier) configuration -- dict keys
    must be JSON-serializable strings, never Python tuples (json.dumps
    raises TypeError on a tuple key; using strings throughout avoids that
    entirely rather than special-casing serialization)."""
    return f"m{m_prime}_x{mult}"


def run_depth2(rec: dict, cumulative_cap_seconds: float = 1500.0) -> dict:
    E = curve_of(rec)
    B = rec["standard_B"]
    standard_fb = rec["standard_factor_base"]
    p, a, b = rec["p"], rec["a"], rec["b"]
    targets = targets_of(rec)

    standard_pairsum, standard_pairsum_info = cg.build_pairsum_index_or_skip(E, standard_fb)

    medium_pairsum = {}   # mult -> (index_or_None, info), only built for m'=3 configs
    configs = {}
    for m_prime, mult in FROZEN_CONFIG_ORDER:
        configs[config_key(m_prime, mult)] = {
            "m_prime": m_prime, "b_med_multiplier": mult, "b_med_size": rec["medium_bases"][mult]["size"],
            "stage1": [], "stage2": [],
        }

    cumulative_gb_seconds = 0.0
    budget_exhausted = False
    rounds_completed = 0
    target_order = [t["index"] for t in targets]
    censored = {key: [] for key in configs}

    for round_idx, t_idx in enumerate(target_order):
        if budget_exhausted:
            break
        t = targets[t_idx]
        R = tuple(t["R"]) if t["R"] is not None else None
        for m_prime, mult in FROZEN_CONFIG_ORDER:
            key = config_key(m_prime, mult)
            if cumulative_gb_seconds >= cumulative_cap_seconds:
                budget_exhausted = True
                censored[key].append(t_idx)
                continue
            cfg = configs[key]
            V_med = medium_base(rec, mult)
            if m_prime == 2:
                pairsum_1 = None  # arity-2 doesn't need one
            else:
                if mult not in medium_pairsum:
                    medium_pairsum[mult] = cg.build_pairsum_index_or_skip(E, V_med)
                pairsum_1 = medium_pairsum[mult][0]
            stage1_res = attempt(E, V_med, R, m_prime, pairsum_1, p, a, b)
            if stage1_res["gb"] is not None:
                cumulative_gb_seconds += stage1_res["gb"]["groebner_seconds"]
            cfg["stage1"].append({"target_index": t_idx, **stage1_res})

            if stage1_res["fast_found"]:
                for elt_x in stage1_res["fast_witness_x"]:
                    if cumulative_gb_seconds >= cumulative_cap_seconds:
                        budget_exhausted = True
                        cfg["stage2"].append({
                            "target_index": t_idx, "medium_element_x": elt_x,
                            "fast_found": None, "gb": None,
                            "note": "cancelled_by_budget before stage-2 attempt",
                        })
                        continue
                    elt_pt = E.lift_x(elt_x)
                    stage2_res = attempt(E, standard_fb, elt_pt, 3, standard_pairsum, p, a, b)
                    if stage2_res["gb"] is not None:
                        cumulative_gb_seconds += stage2_res["gb"]["groebner_seconds"]
                    cfg["stage2"].append({"target_index": t_idx, "medium_element_x": elt_x, **stage2_res})
        rounds_completed = round_idx + 1

    per_config_summary = {}
    for key, cfg in configs.items():
        m_prime, mult = cfg["m_prime"], cfg["b_med_multiplier"]
        n1 = len(cfg["stage1"])
        found1 = sum(1 for r in cfg["stage1"] if r["fast_found"])
        p1 = (found1 / n1) if n1 else None
        c_solve_1 = summarize_costs(gb_cost_series(cfg["stage1"]))
        n2 = len(cfg["stage2"])
        found2 = sum(1 for r in cfg["stage2"] if r.get("fast_found"))
        attempted2 = sum(1 for r in cfg["stage2"] if r.get("gb") is not None)
        p2 = (found2 / attempted2) if attempted2 else None
        c_solve_2 = summarize_costs(gb_cost_series(cfg["stage2"]))

        c2 = None
        c2_undefined_reason = None
        if p1 and p1 > 0 and c_solve_1["mean"] is not None and p2 and p2 > 0 and c_solve_2["mean"] is not None:
            c2 = c_solve_1["mean"] / p1 + m_prime * (c_solve_2["mean"] / p2)
        else:
            c2_undefined_reason = (
                f"p1={p1}, p2={p2}: one or both stage success probabilities are 0/unmeasured, "
                f"so C_2 = C_solve(m')/P(m',B_med) + m'*C_solve(m)/P(m,B) is not computable")

        per_config_summary[key] = {
            "m_prime": m_prime, "b_med_multiplier": mult, "b_med_size": rec["medium_bases"][mult]["size"],
            "stage1_n_measured": n1, "stage1_found": found1, "p_m_prime_Bmed": p1,
            "c_solve_m_prime": c_solve_1,
            "stage2_n_attempted": attempted2, "stage2_n_total_including_uncancelled": n2,
            "stage2_found": found2, "p_m_B_stage2": p2,
            "c_solve_m_stage2": c_solve_2,
            "c2": c2, "c2_undefined_reason": c2_undefined_reason,
            "censored_by_budget_target_indices": censored[key],
        }

    return {
        "standard_B": B, "standard_pairsum_index_info": standard_pairsum_info,
        "medium_pairsum_info": {str(mult): info for mult, (_, info) in medium_pairsum.items()},
        "cumulative_gb_seconds": cumulative_gb_seconds,
        "budget_exhausted": budget_exhausted,
        "rounds_completed": rounds_completed,
        "n_targets_total": len(targets),
        "configs": configs,
        "per_config_summary": per_config_summary,
    }


def validity_prefix_check(per_config_summary: dict, min_targets: int = 10, min_configs: int = 2) -> dict:
    qualifying = [k for k, v in per_config_summary.items() if v["stage1_n_measured"] >= min_targets]
    return {
        "min_targets_per_config": min_targets, "min_configs_required": min_configs,
        "configs_meeting_minimum": qualifying,
        "n_configs_meeting_minimum": len(qualifying),
        "validity_prefix_met": len(qualifying) >= min_configs,
    }


# --------------------------------------------------------------------------
# Bootstrap CI on C2/C1 -- paired at the shared-target level.
# --------------------------------------------------------------------------

def bootstrap_c2_over_c1(single_level_per_target: list[dict], depth2_config: dict,
                          n_boot: int = 2000, seed: int = 0) -> dict:
    """Nonparametric bootstrap, paired on shared target index: each replicate
    resamples (with replacement) from the target indices attempted in BOTH
    the single-level run and this depth-2 configuration's stage-1 pass,
    recomputing C1 and C2 from the resampled bundle each time. Stage-2
    records for a resampled target are included once per occurrence of that
    target in the resample (so a target picked twice contributes its stage-2
    attempts twice), preserving the natural dependency between stage 1 and
    stage 2 within a target.
    """
    sl_by_idx = {r["target_index"]: r for r in single_level_per_target}
    d2_stage1_by_idx = {r["target_index"]: r for r in depth2_config["stage1"]}
    shared_idx = sorted(set(sl_by_idx) & set(d2_stage1_by_idx))
    if len(shared_idx) < 2:
        return {"applicable": False, "reason": f"only {len(shared_idx)} shared measured target(s) "
                                                f"between single-level and this depth-2 configuration; "
                                                f"bootstrap requires at least 2"}
    stage2_by_idx: dict = {}
    for r in depth2_config["stage2"]:
        stage2_by_idx.setdefault(r["target_index"], []).append(r)

    rng = np.random.default_rng(seed)
    m_prime = depth2_config["m_prime"]
    ratios = []
    c1_samples = []
    c2_samples = []
    for _ in range(n_boot):
        sample = rng.choice(shared_idx, size=len(shared_idx), replace=True)
        sl_costs, sl_found = [], 0
        s1_costs, s1_found = [], 0
        s2_costs, s2_found, s2_attempted = [], 0, 0
        for idx in sample:
            sl = sl_by_idx[idx]
            if sl.get("gb") is not None:
                sl_costs.append(sl["gb"]["groebner_seconds"])
            if sl["fast_found"]:
                sl_found += 1
            d1 = d2_stage1_by_idx[idx]
            if d1.get("gb") is not None:
                s1_costs.append(d1["gb"]["groebner_seconds"])
            if d1["fast_found"]:
                s1_found += 1
            for s2 in stage2_by_idx.get(idx, []):
                if s2.get("gb") is not None:
                    s2_costs.append(s2["gb"]["groebner_seconds"])
                    s2_attempted += 1
                if s2.get("fast_found"):
                    s2_found += 1
        n = len(sample)
        p_sl = sl_found / n if n else None
        c_sl = float(np.mean(sl_costs)) if sl_costs else None
        c1 = (c_sl / p_sl) if (p_sl and c_sl is not None) else None
        p1 = s1_found / n if n else None
        c1_stage = float(np.mean(s1_costs)) if s1_costs else None
        p2 = (s2_found / s2_attempted) if s2_attempted else None
        c2_stage = float(np.mean(s2_costs)) if s2_costs else None
        c2 = None
        if p1 and c1_stage is not None and p2 and c2_stage is not None:
            c2 = c1_stage / p1 + m_prime * (c2_stage / p2)
        if c1 is not None and c2 is not None and c1 > 0:
            ratios.append(c2 / c1)
            c1_samples.append(c1)
            c2_samples.append(c2)

    if len(ratios) < n_boot * 0.5:
        return {"applicable": False,
                "reason": f"only {len(ratios)}/{n_boot} bootstrap replicates produced a "
                          f"computable C2/C1 ratio (too many replicates hit p=0 in a "
                          f"resample); CI not reported",
                "n_valid_replicates": len(ratios), "n_boot": n_boot}

    arr = np.array(ratios)
    return {
        "applicable": True, "n_boot": n_boot, "n_valid_replicates": len(ratios),
        "n_shared_targets": len(shared_idx),
        "ci_95": [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))],
        "median_ratio": float(np.median(arr)),
        "mean_ratio": float(np.mean(arr)),
        "ci_entirely_below_1": bool(np.percentile(arr, 97.5) < 1.0),
    }


# --------------------------------------------------------------------------
# RUN-DTREE-009: CTRL-MEDBASE-LOGS
# --------------------------------------------------------------------------

def run_medbase_logs(rec: dict, n_sample: int = 10, seed_tag: str = "medlog") -> dict:
    from harness.toycurve import _seed_int
    E = curve_of(rec)
    B = rec["standard_B"]
    standard_fb = rec["standard_factor_base"]
    p, a, b = rec["p"], rec["a"], rec["b"]
    pairsum, pairsum_info = cg.build_pairsum_index_or_skip(E, standard_fb)

    smallest_mult = 2
    V_med = medium_base(rec, smallest_mult)
    n_sample = min(n_sample, len(V_med))
    rng = random.Random(_seed_int(rec["seed"], seed_tag))
    sampled_elements = rng.sample(V_med, n_sample) if n_sample else []

    per_element = []
    for x in sampled_elements:
        pt = E.lift_x(x)
        res = attempt(E, standard_fb, pt, 3, pairsum, p, a, b)
        per_element.append({"element_x": x, **res})

    costs = gb_cost_series(per_element)
    summary = summarize_costs(costs)
    per_element_cost = summary["mean"]

    extrapolation = {}
    if per_element_cost is not None:
        for mult in (2, 4, 8, 16):
            size = rec["medium_bases"][mult]["size"]
            extrapolation[mult] = {
                "b_med_size": size,
                "extrapolated_total_seconds": per_element_cost * size,
                "basis": "measured_per_element_cost_times_size (EXTRAPOLATION, not a measurement)",
            }

    return {
        "smallest_b_med_multiplier": smallest_mult, "b_med_size": rec["medium_bases"][smallest_mult]["size"],
        "n_sampled_elements": n_sample, "sampled_elements": sampled_elements,
        "per_element": per_element,
        "measured_per_element_cost_seconds": {"mean": per_element_cost, "summary": summary},
        "extrapolation_to_full_grid": extrapolation,
        "extrapolation_flagged": True,
    }


# --------------------------------------------------------------------------
# RUN-DTREE-010: CTRL-MATCHED-RHO
# --------------------------------------------------------------------------

def run_rho_baseline(rec: dict) -> dict:
    from harness.toycurve import ECDLPInstance
    from harness import rho as rho_mod

    per_target = []
    for t in targets_of(rec):
        # rho solves Q = k*P for the INSTANCE's own (P,Q); the shared targets
        # R = a*P+b*Q are a different per-target discrete-log instance, so we
        # build a throwaway ECDLPInstance whose Q is this target R (k unknown
        # to the solver -- rho.solve never reads it) and let rho recover it.
        R = tuple(t["R"]) if t["R"] is not None else None
        if R is None:
            per_target.append({"target_index": t["index"], "solved": False,
                                "reason": "target is the identity point, no discrete log to find"})
            continue
        inst = ECDLPInstance(p=rec["p"], a=rec["a"], b=rec["b"],
                              P=tuple(rec["P"]), Q=R, n=rec["n"], k=None,
                              field_bits=rec["field_bits"], seed=rec["seed"])
        result = rho_mod.solve(inst)
        cert = None
        if result.solved:
            cert = {"kind": "discrete_log", "curve_id": None,
                    "statement": {"P": list(rec["P"]), "Q": list(R), "k": result.k,
                                  "curve": {"p": rec["p"], "a": rec["a"], "b": rec["b"]}}}
        per_target.append({
            "target_index": t["index"], "solved": result.solved, "k_found": result.k,
            "total_group_operations": result.total_group_operations,
            "iterations": result.iterations, "reason": result.reason,
            "certificate": cert,
        })

    solved = [r for r in per_target if r.get("solved")]
    ops = [r["total_group_operations"] for r in solved]
    return {
        "n_targets": len(per_target), "n_solved": len(solved),
        "per_target": per_target,
        "group_operations_summary": summarize_costs(ops),
    }


# --------------------------------------------------------------------------
# RUN-DTREE-011: decomposition-probability sampling + CTRL-GENERIC-HEURISTIC
# --------------------------------------------------------------------------

def heuristic_predicted_p(m: int, b_prime: int, n: int) -> float:
    """HEUR-001: P_dec(m, B') = Theta((B'/N)^(m-1)); the constant is fixed to
    1 for a point prediction (the falsification condition tests the EXPONENT,
    which is what this experiment's slope claim addresses; this control uses
    the same functional form to price a predicted C_2, exactly as
    CTRL-GENERIC-HEURISTIC specifies)."""
    return min(1.0, (b_prime / n) ** (m - 1)) if n > 0 else 0.0


def run_probability_sampling_one_size(rec: dict, depth2_summary: dict, single_level: dict,
                                       n_sample: int = 200, seed_tag: str = "probsamp") -> dict:
    from harness.toycurve import _seed_int
    E = curve_of(rec)
    N = rec["n"]
    standard_fb = rec["standard_factor_base"]
    standard_pairsum, _ = cg.build_pairsum_index_or_skip(E, standard_fb)

    def sample_targets(tag: str, k: int) -> list:
        pts = []
        for i in range(k):
            aa = _seed_int(rec["seed"], f"{seed_tag}_{tag}_a_{i}") % N
            bb = _seed_int(rec["seed"], f"{seed_tag}_{tag}_b_{i}") % N
            pts.append(E.add(E.mul(aa, tuple(rec["P"])), E.mul(bb, tuple(rec["Q"]))))
        return pts

    cells = {}
    for m_prime, mult in FROZEN_CONFIG_ORDER:
        V_med = medium_base(rec, mult)
        pairsum = None
        if m_prime == 3:
            pairsum, _ = cg.build_pairsum_index_or_skip(E, V_med)
            if pairsum is None:
                cells[f"m{m_prime}_x{mult}"] = {
                    "m_prime": m_prime, "b_med_multiplier": mult,
                    "applicable": False,
                    "reason": "arity-3 exact test infeasible_within_budget at this B_med",
                }
                continue
        sample = sample_targets(f"m{m_prime}_x{mult}", n_sample)
        found = 0
        for R in sample:
            if m_prime == 2:
                f, _w = cg.decompose_arity2(E, V_med, R)
            else:
                f, _w = cg.decompose_arity3(E, V_med, R, pairsum)
            found += int(f)
        wilson = wilson_interval(found, len(sample))
        cells[f"m{m_prime}_x{mult}"] = {
            "m_prime": m_prime, "b_med_multiplier": mult, "b_med_size": rec["medium_bases"][mult]["size"],
            "applicable": True, "n_sample": len(sample), "found": found,
            "wilson_95": wilson,
        }

    # CTRL-GENERIC-HEURISTIC: compare measured C2 (from the depth2 run) to
    # the C2 HEUR-001 predicts, using MEASURED C_solve values but HEURISTIC
    # (not measured) success probabilities.
    B = rec["standard_B"]
    generic_control = {}
    for key, cfg_summary in depth2_summary["per_config_summary"].items():
        m_prime, mult = cfg_summary["m_prime"], cfg_summary["b_med_multiplier"]
        b_med_size = cfg_summary["b_med_size"]
        p1_pred = heuristic_predicted_p(m_prime, b_med_size, N)
        p2_pred = heuristic_predicted_p(3, B, N)
        c_solve_1 = cfg_summary["c_solve_m_prime"]["mean"]
        c_solve_2 = cfg_summary["c_solve_m_stage2"]["mean"]
        predicted_c2 = None
        if c_solve_1 is not None and c_solve_2 is not None and p1_pred > 0 and p2_pred > 0:
            predicted_c2 = c_solve_1 / p1_pred + m_prime * (c_solve_2 / p2_pred)
        measured_c2 = cfg_summary["c2"]
        ratio = None
        label = "not_computable"
        if predicted_c2 is not None and measured_c2 is not None and predicted_c2 > 0:
            ratio = measured_c2 / predicted_c2
            label = "generic_equivalent" if 0.5 <= ratio <= 2.0 else "non_generic_signal"
        generic_control[key] = {
            "m_prime": m_prime, "b_med_multiplier": mult,
            "p1_predicted_heur001": p1_pred, "p2_predicted_heur001": p2_pred,
            "predicted_c2": predicted_c2, "measured_c2": measured_c2,
            "ratio_measured_over_predicted": ratio, "label": label,
        }

    return {"n_sample_per_cell": n_sample, "cells": cells, "generic_heuristic_control": generic_control}


def run_probability_sampling_all_sizes(main_instances: dict, depth2_summaries: dict,
                                        single_level_summaries: dict, n_sample: int = 200) -> dict:
    """RUN-DTREE-011 is ONE run spanning all three main sizes (the planned-run
    list names a single RUN-DTREE-011 "at 16-24 bits"), unlike RUN-DTREE-003..
    008 which are explicitly split one-run-per-size."""
    by_size = {}
    for bits, rec in main_instances.items():
        by_size[bits] = run_probability_sampling_one_size(
            rec, depth2_summaries[bits], single_level_summaries[bits], n_sample=n_sample)
    return {"n_sample_per_cell": n_sample, "by_size": by_size}
