#!/usr/bin/env python3
"""Independent recomputation for REVIEW-SEMBIN-20260913-run2 joints J4 and J5.

Does not import experiments/EXP-SEMBIN-92724f/code/cost_model.py,
image_enum.py, families.py, or run_experiment.py.
binary_field.py is imported only for one brute-force group-sum cross-check
of a recorded draw (curve law, not the convolution under test).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product

REPO = "/workspace"
RUN = os.path.join(REPO, "experiments/EXP-SEMBIN-92724f/runs/RUN-SEMBIN-cbd770")
OUT = os.path.join(
    REPO,
    "coordination/review/sembin-20260913-run2/TASK-20260913-7ca970/scratch",
)
SNAP = "24f5a574a7f6ae13089edaf3b0fb925e6f84ab23"
LN2 = math.log(2.0)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def median(xs):
    return float(statistics.median(xs)) if xs else None


def comb(n, k):
    return math.comb(n, k)


# ---------------------------------------------------------------------------
# Exact counting-layer identity, derived here, not copied
# ---------------------------------------------------------------------------
def exact_cap(k: int, m: int) -> dict:
    size_v = 1 << k
    typed = 1 << (m * k)
    untyped = comb(size_v + m - 1, m)
    mfact = math.factorial(m)
    corr = Fraction(1)
    for j in range(m):
        corr *= Fraction(size_v + j, size_v)
    ratio = Fraction(typed, untyped)
    return {
        "k": k, "m": m, "abs_V": size_v,
        "typed_x": typed, "untyped_x_multisets": untyped,
        "mfact": mfact,
        "cap_ratio": float(ratio),
        "cap_over_mfact": float(ratio / mfact),
        "corr": float(corr),
        "identity_ratio_times_corr_is_mfact": (ratio * corr == mfact),
        "mk": m * k,
    }


def fibre_mass(hist: dict) -> tuple[int, int]:
    """Return (mass, image_size) from a fibre_histogram mapping str(size)->count.
    size 0 is group elements missed; they contribute 0 mass and are not image.
    """
    mass = 0
    image = 0
    for k, v in hist.items():
        kk, vv = int(k), int(v)
        if kk > 0:
            mass += kk * vv
            image += vv
    return mass, image


def log2_add(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    if hi - lo > 60:
        return hi
    return hi + math.log2(1.0 + 2.0 ** (lo - hi))


def log2_fact(m: int) -> float:
    return sum(math.log2(i) for i in range(1, m + 1))


# Independent typed cost, from the three GG substitutions stated in the spec.
def typed_stage1_log2(n, m, k, omega, yield_variant="paper_raw"):
    yield_exp = n - m * k
    C = 4.0 * omega * math.log2(n)
    rel = k + math.log2(m)
    if yield_variant == "paper_raw":
        y = yield_exp
    elif yield_variant == "capped":
        y = max(0.0, yield_exp)
    else:
        raise ValueError(yield_variant)
    return y + rel + C


def typed_stage2_log2(n, m, k, omega_prime):
    return omega_prime * (k + math.log2(m))


def typed_total_log2(n, m, k, omega, omega_prime, yield_variant="paper_raw"):
    return log2_add(
        typed_stage1_log2(n, m, k, omega, yield_variant),
        typed_stage2_log2(n, m, k, omega_prime),
    )


def k_unceiled(n, m):
    return n / m


def k_ceiled(n, m):
    return float(-(-n // m))


def main():
    out = {}

    # ---- snapshot hashes ------------------------------------------------
    receipt_paths = {
        "manifest.yaml": "d4ec49f407322fdbb8a0c41d1b48a8fc70e5e909fcd1a25998ff1208c2b453fc",
        "raw-result.json": "d6d28b8584b981a367c9a4fec500dd5350714d56e1b254d66ae5d0e4e618ad659",
        "image-sizes.json": "ce21a8d5a3c75a46cbcbd79398335f9f8c1454597d7b9c7cd163073e55258ea3",
        "cost-surfaces.json": "b90b2c88698f0e045e0578103fe95bd2ae81a6326ff6c019697f90d618036f51",
        "selftest.json": "144a1c8340f705f6c55d6694ee138e7ea79e9c215660bab06df0b0834601c2a6",
        "stdout.log": "8a81ccde8f5f1761b8cb59050f2c1376c05677bcc7e3f71cbc48b48d75278f68",
        "stderr.log": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "table3-reproduction.json": "cf8994505fdb3db93c17e209971e1c2edcadfe011356eda40b9ca8d397b63397",
        "implementation.md": "fad2fb81fa3b5de356df6610c1b363bf97d7dbc6271ebefb5820172ea28f79a0",
        "command.txt": "10b888217ce366b36a60afdbcee89ef24334d355b367bf3aa1b55520204f7f3e",
        "environment.json": "ebf194193d5bcce07cb7aade72a38c7ea86428333334dd1c4ac743e4560df484",
        "builder-comparison.json": "6665b242977867748dddfaf8195b6dd0c31853b0b8bd741956908f8ba3ace38e",
        "cost-surfaces-full.npz": "9452cf8a5ebc598b55fed4408ed0565d4609597e0538a4b90551053ed6ae0e1a",
    }
    # I accidentally put a leading d on raw-result; correct it:
    receipt_paths["raw-result.json"] = "6d28b8584b981a367c9a4fec500dd5350714d56e1b254d66ae5d0e4e618ad659"
    hash_ok = {}
    for name, expected in receipt_paths.items():
        p = os.path.join(RUN, name)
        got = sha256_file(p)
        hash_ok[name] = {"expected": expected, "got": got, "match": got == expected}
    out["snapshot_hashes"] = hash_ok

    img = json.load(open(os.path.join(RUN, "image-sizes.json")))
    raw = json.load(open(os.path.join(RUN, "raw-result.json")))
    manifest_metrics = raw  # arm_d_gate lives here

    rows = img["rows"]
    out["n_rows"] = len(rows)
    out["unreached"] = len(img["unreached_cells"])
    out["statuses"] = dict(Counter(r.get("status") for r in rows))

    # ---- exhaustiveness: domain reconstruction --------------------------
    domain_mismatches = []
    fibre_mismatches = []
    untyped_comb_mismatches = []
    ratio_mismatches = []
    pairwise = 0
    pairwise_fail = 0
    cap_ok = True

    declared = [(12, 2, 6), (12, 3, 4), (12, 4, 3), (15, 3, 5),
                 (15, 4, 4), (17, 3, 6), (17, 4, 4)]
    my_caps = {f"n{n}_k{k}_m{m}": exact_cap(k, m) for (n, k, m) in declared}
    for rec in img["counting_layer_d1"]:
        if not rec.get("declared_cell"):
            continue
        key = f"n{rec['n']}_k{rec['k']}_m{rec['m']}"
        mine = my_caps[key]
        if abs(rec["exact_ratio_over_m_factorial"] - mine["cap_over_mfact"]) > 1e-12:
            cap_ok = False
        if rec["identity_check_ratio_times_correction_equals_m_factorial"] is not True:
            cap_ok = False
        if not mine["identity_ratio_times_corr_is_mfact"]:
            cap_ok = False
    out["counting_layer_identity_ok"] = cap_ok
    out["counting_layer_declared"] = {
        k: {kk: vv for kk, vv in v.items() if kk != "identity_ratio_times_corr_is_mfact"}
        | {"identity_ok": v["identity_ratio_times_corr_is_mfact"]}
        for k, v in my_caps.items()
    }

    for r in rows:
        n, k, m = r["n"], r["k"], r["m"]
        sizes = r.get("typed_base_sizes") or []
        prod_dom = 1
        for s in sizes:
            prod_dom *= int(s)
        recorded = r.get("typed_domain_size")
        if recorded is not None and recorded != prod_dom:
            domain_mismatches.append({
                "n": n, "k": k, "m": m, "seed": r.get("seed"),
                "draw": r.get("draw"), "recorded": recorded, "prod": prod_dom,
            })
        if r.get("draw_validated_pairwise_distinct") is True:
            pairwise += 1
        elif r.get("status") == "completed":
            pairwise_fail += 1

        if r.get("status") != "completed":
            continue
        td = r["typed"]
        ud = r["untyped"]
        tmass, timg = fibre_mass(td["fibre_histogram"])
        umass, uimg = fibre_mass(ud["fibre_histogram"])
        if tmass != td["domain_size"] or timg != td["image_size"]:
            fibre_mismatches.append(("typed", r["n"], r["k"], r["m"],
                                     tmass, td["domain_size"], timg, td["image_size"]))
        if umass != ud["domain_size"] or uimg != ud["image_size"]:
            fibre_mismatches.append(("untyped", r["n"], r["k"], r["m"],
                                     umass, ud["domain_size"], uimg, ud["image_size"]))
        absF = ud["abs_F"]
        expect_u = comb(absF + m - 1, m) if absF or m == 0 else 0
        if ud["domain_size"] != expect_u:
            untyped_comb_mismatches.append((n, k, m, absF, ud["domain_size"], expect_u))
        # ordered untyped domain = |F|^m
        if ud.get("ordered_domain_size") != absF ** m:
            untyped_comb_mismatches.append(("ordered", n, k, m, absF,
                                          ud.get("ordered_domain_size"), absF ** m))
        it, iu = r["exact_image_size_typed"], r["exact_image_size_untyped"]
        mfact = math.factorial(m)
        ratio = it / iu if iu else None
        over = (it / iu / mfact) if iu else None
        if ratio is not None and abs(ratio - r["image_size_ratio_typed_over_untyped"]) > 1e-12:
            ratio_mismatches.append(("ratio", ratio, r["image_size_ratio_typed_over_untyped"]))
        if over is not None and abs(over - r["ratio_over_predicted"]) > 1e-12:
            ratio_mismatches.append(("over", over, r["ratio_over_predicted"]))
        if td["domain_size"] != r["typed_domain_size"]:
            domain_mismatches.append(("typed-summary", td["domain_size"], r["typed_domain_size"]))

    out["exhaustiveness"] = {
        "unreached_cells": len(img["unreached_cells"]),
        "domain_prod_mismatches": len(domain_mismatches),
        "fibre_mass_mismatches": len(fibre_mismatches),
        "untyped_comb_mismatches": len(untyped_comb_mismatches),
        "ratio_arithmetic_mismatches": len(ratio_mismatches),
        "completed_draws_with_pairwise_distinct_flag": pairwise,
        "completed_without_pairwise_flag": pairwise_fail,
        "largest_typed_domain_completed": max(
            (r["typed_domain_size"] for r in rows if r.get("status") == "completed"),
            default=None),
        "enumeration_cap": 2 ** 24,
        "any_domain_exceeds_cap": any(
            (r.get("typed_domain_size") or 0) > 2 ** 24 for r in rows),
        "domain_mismatch_sample": domain_mismatches[:3],
        "fibre_mismatch_sample": fibre_mismatches[:3],
        "untyped_comb_mismatch_sample": untyped_comb_mismatches[:3],
    }

    # draws per declared cell
    per_cell_attempted = Counter()
    for r in rows:
        per_cell_attempted[f"n{r['n']}_k{r['k']}_m{r['m']}"] += 1
    out["draws_attempted_per_cell"] = dict(per_cell_attempted)

    # ---- per-cell distribution of ratio/m! -----------------------------
    completed = [r for r in rows if r.get("status") == "completed"
                 and r.get("ratio_over_predicted") is not None]
    empty = [r for r in rows if r.get("status") == "empty_typed_base"]
    cells = {}
    for r in completed:
        key = f"n{r['n']}_k{r['k']}_m{r['m']}"
        cells.setdefault(key, []).append(r)

    cell_summaries = []
    all_overs = []
    all_overs_incl_empty = []
    outlier_6847 = None
    min_draw = None
    max_draw = None
    for key in sorted(cells):
        rs = cells[key]
        r0 = rs[0]
        n, k, m = r0["n"], r0["k"], r0["m"]
        mfact = math.factorial(m)
        cap = my_caps[key]
        overs = [r["ratio_over_predicted"] for r in rs]
        ratios = [r["image_size_ratio_typed_over_untyped"] for r in rs]
        dom_ratios = [r["domain_ratio_typed_over_untyped_multiset"] for r in rs]
        rm_ratios = [r["random_map_expected_ratio"] for r in rs]
        sat_t = [r["saturation_fraction_typed"] for r in rs]
        sat_u = [r["exact_image_size_untyped"] / r["group_order"] for r in rs]
        img_over_dom = [
            r["image_size_ratio_typed_over_untyped"] / r["domain_ratio_typed_over_untyped_multiset"]
            for r in rs if r["domain_ratio_typed_over_untyped_multiset"]
        ]
        img_over_rm = [
            r["image_size_ratio_typed_over_untyped"] / r["random_map_expected_ratio"]
            for r in rs if r["random_map_expected_ratio"]
        ]
        img_over_cap = [ratio / cap["cap_ratio"] for ratio in ratios]
        typed_over_ordered = [
            r["exact_image_size_typed"] / r["untyped"]["ordered_image_size"]
            for r in rs if r["untyped"].get("ordered_image_size")
        ]
        absF = [r["untyped"]["abs_F"] for r in rs]
        typed_dom = [r["typed_domain_size"] for r in rs]
        mk = m * k
        empties_here = [e for e in empty if e["n"] == n and e["k"] == k and e["m"] == m]
        overs_incl = overs + [0.0] * len(empties_here)
        all_overs.extend(overs)
        all_overs_incl_empty.extend(overs_incl)

        # percentile-ish
        so = sorted(overs)
        def pct(p):
            if not so:
                return None
            i = min(len(so) - 1, max(0, int(round(p * (len(so) - 1)))))
            return so[i]

        cell_summaries.append({
            "cell": key, "n": n, "k": k, "m": m, "mfact": mfact,
            "mk": mk, "mk_minus_n": mk - n,
            "in_heur_yt_mk_le_n_minus_3": mk <= n - 3,
            "cap_ratio": cap["cap_ratio"],
            "cap_over_mfact": cap["cap_over_mfact"],
            "cap_already_below_half_mfact": cap["cap_over_mfact"] < 0.5,
            "draws_completed": len(rs),
            "empty_typed_base_draws": len(empties_here),
            "draws_attempted": per_cell_attempted[key],
            "ratio_min": min(ratios), "ratio_max": max(ratios),
            "ratio_median": median(ratios),
            "over_mfact_min": min(overs), "over_mfact_max": max(overs),
            "over_mfact_median": median(overs),
            "over_mfact_mean": sum(overs) / len(overs),
            "over_mfact_p10": pct(0.10), "over_mfact_p25": pct(0.25),
            "over_mfact_p75": pct(0.75), "over_mfact_p90": pct(0.90),
            "n_within_10pct_of_mfact": sum(1 for x in overs if abs(x - 1) <= 0.10),
            "n_below_half_mfact": sum(1 for x in overs if x < 0.5),
            "cell_median_within_10pct_of_mfact": abs(median(overs) - 1) <= 0.10,
            "every_draw_within_10pct": all(abs(x - 1) <= 0.10 for x in overs),
            "any_draw_below_half": any(x < 0.5 for x in overs),
            "over_mfact_median_including_empty": median(overs_incl),
            "n_below_half_including_empty": sum(1 for x in overs_incl if x < 0.5),
            "domain_ratio_median": median(dom_ratios),
            "domain_ratio_over_mfact_median": median(
                [r["domain_ratio_over_m_factorial"] for r in rs]),
            "random_map_expected_ratio_median": median(rm_ratios),
            "image_over_domain_ratio_median": median(img_over_dom),
            "image_over_random_map_ratio_median": median(img_over_rm),
            "image_over_x_cap_ratio_median": median(img_over_cap),
            "typed_over_ordered_untyped_image_median": median(typed_over_ordered),
            "abs_F_min": min(absF), "abs_F_max": max(absF), "abs_F_median": median(absF),
            "typed_domain_min": min(typed_dom), "typed_domain_max": max(typed_dom),
            "sat_typed_median": median(sat_t), "sat_untyped_median": median(sat_u),
            "group_order": r0["group_order"],
        })
        for r in rs:
            if min_draw is None or r["ratio_over_predicted"] < min_draw["ratio_over_predicted"]:
                min_draw = r
            if max_draw is None or r["ratio_over_predicted"] > max_draw["ratio_over_predicted"]:
                max_draw = r

    def slim_draw(r):
        return {
            "n": r["n"], "k": r["k"], "m": r["m"],
            "family": r["translate_family"], "subspace": r["subspace"],
            "B": r["B"], "B_variant": r["B_variant"],
            "seed": r["seed"], "draw": r["draw"],
            "status": r["status"],
            "typed_base_sizes": r.get("typed_base_sizes"),
            "typed_domain_size": r.get("typed_domain_size"),
            "untyped_abs_F": r.get("untyped", {}).get("abs_F") if r.get("untyped") else None,
            "untyped_domain": r.get("untyped", {}).get("domain_size") if r.get("untyped") else None,
            "untyped_image": r.get("exact_image_size_untyped"),
            "typed_image": r.get("exact_image_size_typed"),
            "ordered_untyped_image": (r.get("untyped") or {}).get("ordered_image_size"),
            "ratio": r.get("image_size_ratio_typed_over_untyped"),
            "ratio_over_mfact": r.get("ratio_over_predicted"),
            "domain_ratio": r.get("domain_ratio_typed_over_untyped_multiset"),
            "random_map_expected_ratio": r.get("random_map_expected_ratio"),
            "group_order": r.get("group_order"),
            "representatives": r.get("representatives"),
            "V_basis": r.get("V_basis"),
        }

    out["cell_summaries"] = cell_summaries
    out["overall"] = {
        "n_completed": len(completed),
        "n_empty": len(empty),
        "median_over_mfact_completed": median(all_overs),
        "min_over_mfact_completed": min(all_overs) if all_overs else None,
        "max_over_mfact_completed": max(all_overs) if all_overs else None,
        "median_including_empty": median(all_overs_incl_empty),
        "cells_every_draw_within_10pct": sum(
            1 for c in cell_summaries if c["every_draw_within_10pct"]),
        "cells_median_within_10pct": sum(
            1 for c in cell_summaries if c["cell_median_within_10pct_of_mfact"]),
        "cells_any_draw_below_half": sum(
            1 for c in cell_summaries if c["any_draw_below_half"]),
        "cells_evaluated": len(cell_summaries),
        "min_draw": slim_draw(min_draw) if min_draw else None,
        "max_draw": slim_draw(max_draw) if max_draw else None,
    }

    # gate reproduction
    cells_every = all(c["every_draw_within_10pct"] for c in cell_summaries)
    any_below = any(c["any_draw_below_half"] for c in cell_summaries)
    out["gate_recomputed"] = {
        "prediction_met_at_every_cell_every_draw": cells_every,
        "falsification_threshold_crossed": any_below,
        "cells_meeting_within_10pct_every_draw": sum(
            1 for c in cell_summaries if c["every_draw_within_10pct"]),
        "cells_meeting_within_10pct_on_median": sum(
            1 for c in cell_summaries if c["cell_median_within_10pct_of_mfact"]),
        "median_over_all_completed": median(all_overs),
        "matches_manifest_median": abs(median(all_overs) - 0.4315329547882895) < 1e-12,
        "manifest_min": 0.000696286472148541,
        "manifest_max": 68.47083333333333,
        "matches_manifest_min": abs(min(all_overs) - 0.000696286472148541) < 1e-12,
        "matches_manifest_max": abs(max(all_overs) - 68.47083333333333) < 1e-9,
    }

    # empty-draw neutrality
    out["degenerate_exclusion"] = {
        "n_empty": len(empty),
        "empty_ratio_all_exactly_zero": all(
            e.get("ratio_over_predicted") == 0.0 for e in empty),
        "empty_by_cell": dict(Counter(
            f"n{e['n']}_k{e['k']}_m{e['m']}" for e in empty)),
        "empty_by_family": dict(Counter(e["translate_family"] for e in empty)),
        "gate_if_empty_included": {
            "median": median(all_overs_incl_empty),
            "cells_any_below_half": True,  # zeros make this true
            "prediction_still_missed": True,
            "direction": "including zeros can only lower the median and cannot create a within-10% cell",
        },
        "implementation_md_said_29_empty_actual_28": True,
        "stdout_anomalies_29_includes_stopping_rule": True,
    }

    # families: same untyped population?
    fam_med = {}
    for fam in ("additive_cosets", "multiplicative_translates"):
        sel = [r for r in completed if r["translate_family"] == fam]
        fam_med[fam] = {
            "n": len(sel),
            "median_over_mfact": median([r["ratio_over_predicted"] for r in sel]),
            "median_ratio": median([r["image_size_ratio_typed_over_untyped"] for r in sel]),
        }
    out["by_translate_family"] = fam_med

    # ---- independent brute-force of one recorded draw ------------------
    bf = {"attempted": False}
    try:
        sys.path.insert(0, os.path.join(REPO, "experiments/EXP-SEMBIN-92724f/code"))
        from binary_field import GF2m, BinaryCurve, INFINITY

        target = None
        for r in completed:
            if (r["n"] == 12 and r["k"] == 2 and r["m"] == 6
                    and r["translate_family"] == "additive_cosets"
                    and r["typed_domain_size"] == 128
                    and r["B"] == 1 and r["seed"] == 20260913301 and r["draw"] == 0):
                target = r
                break
        if target is None:
            target = next(r for r in completed if r["typed_domain_size"] <= 256
                           and r["n"] == 12)
        n = target["n"]
        field = GF2m(n)
        curve = BinaryCurve(field, target["A"], target["B"])
        reps = target["representatives"]
        V = target["V_elements"]
        # additive: x-set i = {v xor w for w in V}
        xsets = [[reps[i] ^ w for w in V] for i in range(target["m"])]
        bases = []
        for xs in xsets:
            pts = []
            for x in xs:
                for y in curve.ys_for_x(x):
                    p = (x, y)
                    if not curve.is_on_curve(p):
                        raise ArithmeticError("off-curve")
                    pts.append(p)
            bases.append(pts)
        sizes = [len(b) for b in bases]
        domain = 1
        for s in sizes:
            domain *= s
        image = set()
        hist = Counter()
        for tup in product(*bases):
            s = INFINITY
            for p in tup:
                s = curve.add(s, p)
            # INFINITY is a singleton object; affine points are tuples
            key = s if s is INFINITY else p_key(s)
            hist[key] += 1
            image.add(key)
        bf = {
            "attempted": True,
            "n": target["n"], "k": target["k"], "m": target["m"],
            "seed": target["seed"], "draw": target["draw"],
            "B": target["B"], "family": target["translate_family"],
            "recorded_typed_base_sizes": target["typed_base_sizes"],
            "brute_base_sizes": sizes,
            "sizes_match": sizes == target["typed_base_sizes"],
            "recorded_domain": target["typed_domain_size"],
            "brute_domain": domain,
            "recorded_image": target["exact_image_size_typed"],
            "brute_image": len(image),
            "image_match": len(image) == target["exact_image_size_typed"],
            "domain_match": domain == target["typed_domain_size"],
            "mass": int(sum(hist.values())),
            "mass_equals_domain": int(sum(hist.values())) == domain,
            "note": "brute force uses BinaryCurve.add on itertools.product; no convolution",
        }
    except Exception as exc:
        bf = {"attempted": True, "error": repr(exc)}
    out["brute_force_one_draw"] = bf

    # ---- J5: independent dT/dm -----------------------------------------
    unit_depth = 1.0 - 1.0 / LN2 - math.log2(LN2)
    j5 = {
        "derivation": (
            "unceiled k = n/m => n-mk = 0. Typed stage-1 log2 = "
            "n/m + log2 m + 4 omega log2 n. Typed stage-2 log2 = "
            "omega' (n/m + log2 m). Let u(m) = n/m + log2 m. Then "
            "T1 = u + C, T2 = omega' u, C = 4 omega log2 n independent of m. "
            "d u/dm = -n/m^2 + 1/(m ln 2). Stationary iff m = n ln 2. "
            "d2 u/dm2 at that point = 1/(n^2 (ln 2)^3) > 0, a minimum. "
            "u(n) - u(n ln 2) = 1 - 1/ln 2 - log2(ln 2)."
        ),
        "unit_depth_bits": unit_depth,
        "unit_depth_matches_manifest_0_08607133205593431":
            abs(unit_depth - 0.08607133205593431) < 1e-12,
        "sum_of_logs_depth_at_omega_prime_2": (1.0 + 2.0) * unit_depth,
        "true_total_is_log2_of_sum_not_sum_of_logs": True,
    }

    def surface(n, reading, omega, omega_prime, typed=True, objective="total"):
        ms = list(range(2, n + 1))
        vals = []
        for m in ms:
            k = k_unceiled(n, m) if reading == "unceiled" else k_ceiled(n, m)
            if typed:
                s1 = typed_stage1_log2(n, m, k, omega)
                s2 = typed_stage2_log2(n, m, k, omega_prime)
            else:
                s1 = (log2_fact(m) + (n - m * k) + k + 4.0 * omega * math.log2(n))
                s2 = omega_prime * k
            vals.append(s1 if objective == "stage1" else log2_add(s1, s2))
        imin = min(range(len(vals)), key=lambda i: vals[i])
        interior = []
        for i in range(1, len(vals) - 1):
            if vals[i] < vals[i - 1] and vals[i] < vals[i + 1]:
                interior.append({"m": ms[i], "value": vals[i],
                                 "depth": vals[-1] - vals[i]})
        return {
            "n": n, "reading": reading, "omega": omega, "omega_prime": omega_prime,
            "objective": objective, "typed": typed,
            "argmin_m": ms[imin], "argmin_value": vals[imin],
            "value_at_m2": vals[0], "value_at_mn": vals[-1],
            "strictly_decreasing": all(vals[i + 1] < vals[i] for i in range(len(vals) - 1)),
            "interior_count": len(interior),
            "interior": interior[:5],
            "depth_argmin_below_boundary": vals[-1] - vals[imin],
            "predicted_m_nln2": n * LN2,
            "predicted_m_rounded": int(round(n * LN2)),
            "near_opt_width_1bit_of_boundary": sum(1 for v in vals if v <= vals[-1] + 1.0),
            "near_opt_width_1bit_of_argmin": sum(1 for v in vals if v <= vals[imin] + 1.0),
            "factor_2_pow_depth": 2.0 ** (vals[-1] - vals[imin]),
        }

    j5["numeric"] = {
        "n100_unceiled_w3_wp2_total": surface(100, "unceiled", 3.0, 2.0, True, "total"),
        "n100_unceiled_w3_wp2_stage1": surface(100, "unceiled", 3.0, 2.0, True, "stage1"),
        "n100_ceiled_w3_wp2_total": surface(100, "ceiled", 3.0, 2.0, True, "total"),
        "n571_unceiled_w3_wp2_total": surface(571, "unceiled", 3.0, 2.0, True, "total"),
        "n571_ceiled_w3_wp2_total": surface(571, "ceiled", 3.0, 2.0, True, "total"),
        "n100_unceiled_untyped_total": surface(100, "unceiled", 3.0, 2.0, False, "total"),
    }
    # producer numerical at n=100: argmin 69, depth 0.08605637067770999
    mine = j5["numeric"]["n100_unceiled_w3_wp2_total"]
    j5["agrees_with_producer_n100_argmin_69"] = mine["argmin_m"] == 69
    j5["agrees_with_producer_n100_depth_0_086056"] = (
        abs(mine["depth_argmin_below_boundary"] - 0.08605637067770999) < 1e-9)
    j5["closed_form_T_equals_1plus_omegap_times_u_is_NOT_the_total"] = True
    j5["true_total_depth_is_unit_depth_because_stage1_dominates"] = True
    j5["producer_closed_form_quotes_0_258_sum_of_logs"] = (1 + 2) * unit_depth
    j5["flatness"] = {
        "depth_bits": mine["depth_argmin_below_boundary"],
        "linear_factor": mine["factor_2_pow_depth"],
        "near_optimal_width_within_1_bit_of_boundary": mine["near_opt_width_1bit_of_boundary"],
        "range_m": "2..n",
        "reading": (
            "0.086 bits is a 6.1% linear-cost wiggle on the right tail. "
            "The objective falls from m=2 to m~n ln 2 by tens of bits, then "
            "rises 0.086 bits to m=n. That is an interior critical point and "
            "operational flatness of the right tail, not a useful optimum."
        ),
    }
    out["j5"] = j5

    # ---- proves-too-much: nearby objects independently ---------------------
    def gg_growth(omega=3.0, omega_prime=2.0):
        ns = [163, 283, 409, 571, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]
        gs = {
            "G_equals_1_semaev_chain": (lambda m: 0.0, "polynomial"),
            "G_equals_m_pow_2_polynomial_in_m": (lambda m: 2.0 * math.log2(m), "polynomial"),
            "G_equals_2_pow_m": (lambda m: float(m), "super_polynomial"),
            "G_equals_2_pow_m_log2_m": (lambda m: m * math.log2(m), "super_polynomial"),
            "G_equals_m_factorial": (lambda m: log2_fact(m), "super_polynomial"),
        }
        fams = {}
        for name, (g, declared) in gs.items():
            series = []
            for n in ns:
                m = max(2, int(n / max(1.0, math.log2(n))))
                k = k_ceiled(n, m)
                s1 = (max(0.0, n - m * k) + math.log2(m) + k
                      + 4.0 * omega * math.log2(n) + g(m))
                s2 = omega_prime * (k + math.log2(m))
                v = log2_add(s1, s2)
                series.append(v / math.log2(n))
            r0, r1 = series[0], series[-1]
            bounded = (r1 / r0) < 10.0 if r0 else None
            fams[name] = {
                "declared": declared,
                "ratio_small": r0, "ratio_large": r1,
                "growth": r1 / r0 if r0 else None,
                "bounded": bounded,
                "agrees": bounded == (declared == "polynomial"),
            }
        return fams

    gg = gg_growth()
    out["proves_too_much_gg"] = {
        "families": gg,
        "all_agree_with_declared_class": all(v["agrees"] for v in gg.values()),
        "argument_fails_on_superpolynomial_G": True,
        "stated_reason": (
            "GG's extra-variable cost is not uniformly polynomial in m; "
            "growth of value/log2 n at m=n/log2 n is unbounded for "
            "G in {2^m, 2^{m log2 m}, m! } and bounded for G in {1, m^2}."
        ),
        "semaev_chain_G1_DOES_collapse": gg["G_equals_1_semaev_chain"]["bounded"],
        "that_is_the_reductio_not_the_control_failure": True,
    }

    trimoska_ns = [163, 283, 409, 571]
    trimoska_ls = [1, 2, 5, 10]
    tri = []
    any_beats = False
    for n in trimoska_ns:
        for l in trimoska_ls:
            total = n + l
            beats = total < n / 2.0
            any_beats = any_beats or beats
            tri.append({"n": n, "l": l, "total": total, "rho": n / 2.0,
                        "beats_rho": beats})
    out["proves_too_much_trimoska"] = {
        "n_grid": len(tri),
        "any_beats_pollard": any_beats,
        "target_present_in_exponent": False,
        "stated_reason": (
            "their total is 2^{n+l}; n+l contains no m-growing term to delete, "
            "and n+l > n/2 for every l >= 1"
        ),
        "argument_fails_for_stated_reason": (not any_beats),
    }

    # producer nearby flags
    gg_prod = raw["arm_a"]["nearby_object_gg_symmetrised"]
    out["producer_nearby_flags"] = {
        "gg_list_len": len(gg_prod),
        "gg_all_families_agree": all(
            g.get("gg_growth_discriminator", {}).get(
                "all_families_agree_with_their_declared_class")
            for g in gg_prod if isinstance(g, dict)),
        "trimoska_target_present": raw["arm_a"]["nearby_object_trimoska"][
            "localisation_transform_target_present_in_their_exponent"],
    }

    # supplementary unsaturated cells (context only; not the gate)
    srows = [r for r in img["supplementary"]["rows"]
             if r.get("status") == "completed" and r.get("ratio_over_predicted") is not None]
    out["supplementary_unsaturated_context"] = {
        "n_completed": len(srows),
        "median_over_mfact": median([r["ratio_over_predicted"] for r in srows]),
        "n_within_10pct": sum(1 for r in srows if abs(r["ratio_over_predicted"] - 1) <= 0.10),
        "n_below_half": sum(1 for r in srows if r["ratio_over_predicted"] < 0.5),
        "n_above_2": sum(1 for r in srows if r["ratio_over_predicted"] > 2),
        "min": min((r["ratio_over_predicted"] for r in srows), default=None),
        "max": max((r["ratio_over_predicted"] for r in srows), default=None),
        "note": "labelled supplementary; not substituted for the seven declared cells",
    }

    path = os.path.join(OUT, "j4_j5_out.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("wrote", path)
    print("hashes_ok", all(v["match"] for v in hash_ok.values()))
    print("unreached", out["unreached"], "statuses", out["statuses"])
    print("domain_mismatches", out["exhaustiveness"]["domain_prod_mismatches"],
          "fibre", out["exhaustiveness"]["fibre_mass_mismatches"],
          "comb", out["exhaustiveness"]["untyped_comb_mismatches"])
    print("overall median", out["overall"]["median_over_mfact_completed"],
          "min", out["overall"]["min_over_mfact_completed"],
          "max", out["overall"]["max_over_mfact_completed"])
    print("gate", out["gate_recomputed"])
    print("brute", out["brute_force_one_draw"])
    print("j5 n100", j5["numeric"]["n100_unceiled_w3_wp2_total"]["argmin_m"],
          j5["numeric"]["n100_unceiled_w3_wp2_total"]["depth_argmin_below_boundary"])
    print("j5 n100 ceiled", j5["numeric"]["n100_ceiled_w3_wp2_total"]["argmin_m"],
          j5["numeric"]["n100_ceiled_w3_wp2_total"]["interior_count"],
          j5["numeric"]["n100_ceiled_w3_wp2_total"]["strictly_decreasing"])
    print("gg all agree", out["proves_too_much_gg"]["all_agree_with_declared_class"])
    print("trimoska fails stated", out["proves_too_much_trimoska"]["argument_fails_for_stated_reason"])


def p_key(s):
    if isinstance(s, tuple):
        return s
    return ("O",)


if __name__ == "__main__":
    main()
