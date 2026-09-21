#!/usr/bin/env python3
"""
EXP-MONO-cb905d, RUN-MONO-cb905d-2: corrected re-run of Part A ONLY
(Stage 1 and Stage 2), under the group-uniform sampler construction fixed
by experiments/EXP-MONO-cb905d/amendments/v1.yaml (base version 1 ->
resulting version 2), per handoff ledger/handoffs/TASK-20260831-52f3df.yaml.

WHAT THIS SCRIPT DOES
----------------------
- Re-derives the SAME p=617 matched pair (ordinary A=340,B=362; CM j=1728
  A=69,B=0; N=580, tau=4) EXP-MONO-64aaa4 and RUN-MONO-cb905d-1 both used,
  and confirms it matches the archived transcript exactly (the same
  stopping-rule gate RUN-MONO-cb905d-1's own script applied).
- Draws 20000 FRESH tuples per curve under the CORRECTED group-uniform
  sampler (`sample_group_uniform_v2_corrected` below), replacing
  RUN-MONO-cb905d-1's verified-biased construction
  (`sample_group_uniform_v1_biased`, kept below for historical
  reproducibility ONLY -- never called by this script's `main()`).
- Reuses RUN-MONO-cb905d-1's own TRANSVERSAL arm counts directly from that
  run's raw-result.json (unaffected by the sampler defect; not redrawn, per
  the amendment and handoff).
- Computes P1, P2, P3 exactly as the original specification.yaml defines
  them (rate_pairs_per_tuple ratios, ratio-of-ratios, Fisher-exact
  comparison of group-uniform collision counts).
- Runs an empirical point-uniformity sanity check on the corrected sampler
  (see `check_point_uniformity`), independent of, and in addition to, the
  amendment's own analytic slot-counting proof (cited, not re-derived,
  in the execution report addendum).
- Does NOT touch Part B (Stage 0's full cell enumeration, Stage 3's
  cross-prime extension): those are unaffected by this defect and are not
  re-executed, per the handoff's explicit scope. This script performs the
  narrow Part-A curve re-derivation check only (a small subset of what
  Stage 0 in the original script did), sufficient to satisfy Part A's own
  stopping rule; it does not enumerate or measure any Part-B cell.

CODE REUSE DISCIPLINE
----------------------
EXP-MONO-64aaa4's own implementation module is loaded read-only by file
path (never copied/edited), exactly as RUN-MONO-cb905d-1's own script did.
Its helper functions (draw_uniform, quad_char, sqrt_mod_p, ec_neg, ec_add,
construct_ordinary, construct_cm_j1728, SIGN_CLASSES, NCLASSES,
fisher_exact_2x2) are called directly from the loaded module object.

This script performs measurement only. It changes no hypothesis, experiment,
or goal status.
"""
import importlib.util
import json
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_ROOT = HERE.parent  # experiments/EXP-MONO-cb905d
REPO_ROOT = EXP_ROOT.parent.parent  # crypto-autoresearcher

EXP64_ROOT = REPO_ROOT / "experiments" / "EXP-MONO-64aaa4"
EXP64_IMPL = EXP64_ROOT / "implementation" / "run_experiment.py"
EXP64_RAW_RESULT = EXP64_ROOT / "runs" / "RUN-MONO-64aaa4-1" / "raw-result.json"

RUN1_RAW_RESULT = EXP_ROOT / "runs" / "RUN-MONO-cb905d-1" / "raw-result.json"

# Domain used for RUN-MONO-cb905d-1's group-uniform arm (the biased v1
# construction). NEVER used by this script's own new draws below; recorded
# here only so the deliberate domain change to CB_DOMAIN_V2 is legible.
CB_DOMAIN_V1 = "EXP-MONO-cb905d/v1"

# NEW domain for this run's group-uniform draws. Because this program's
# seed derivation is `sha256(domain|label|p|role|draw_index|counter)` with
# NO separate external PRNG seed folded in (confirmed by reading
# EXP-MONO-64aaa4's own `seed_bytes`), changing the domain string alone is
# what produces a byte-different, non-overlapping seed stream from
# RUN-MONO-cb905d-1's group-uniform draws -- required per the handoff
# ("fresh seed stream ... do not reuse RUN-MONO-cb905d-1's exact seeds").
# The nominal SEED integer below is carried forward unchanged as a run
# label only (as in RUN-MONO-cb905d-1's own script, it does not itself
# enter `seed_bytes`); domain separation is the actual mechanism.
CB_DOMAIN_V2 = "EXP-MONO-cb905d/v2"
SEED = 20260901  # nominal label only; see note above -- domain, not this
                  # integer, is what changes the draw stream.

NTUPLES = 20000
UNIFORMITY_CHECK_DRAWS_PER_CURVE = 58000  # ~100x N=580; see check_point_uniformity

RUN_DIR = EXP_ROOT / "runs" / "RUN-MONO-cb905d-2"


def load_m64():
    """Load EXP-MONO-64aaa4's own implementation module, read-only, by file
    path. Never edits or copies that file."""
    spec = importlib.util.spec_from_file_location("exp_mono_64aaa4_impl_v2", str(EXP64_IMPL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------
# HISTORICAL (v1, BIASED) SAMPLER -- kept verbatim for historical
# reproducibility of RUN-MONO-cb905d-1's own numbers from source. NEVER
# called by this script's main(). Confirmed biased per
# CORR-20260831-ba2118 / amendments/v1.yaml: unconditionally accepts every
# 2-torsion x (probability 1/p, i.e. double a generic point's 1/(2p)), and
# never allocates a domain slot for the point at infinity O.
# ---------------------------------------------------------------------
def sample_group_uniform_v1_biased(m64, p, A, B, role, tid, counter):
    """DEPRECATED / BIASED. Do not use for new measurement. Reproduced here,
    unmodified in behavior, only so RUN-MONO-cb905d-1's own group-uniform
    numbers remain re-derivable from source code checked into this
    directory (see implementation.md item 4 of RUN-MONO-cb905d-1's own
    implementation.md for the original disclosure)."""
    while True:
        x, counter = m64.draw_uniform("gu-x", p, role, tid, counter, p)
        f = (x * x * x + A * x + B) % p
        if f == 0:
            return (x, 0), counter  # BIASED: unconditional accept, no coin flip.
        chi = m64.quad_char(f, p)
        if chi == 1:
            small, large = m64.sqrt_mod_p(f, p)
            bit, counter = m64.draw_uniform("gu-sign", p, role, tid, counter, 2)
            y = small if bit == 0 else large
            return (x, y), counter
        # chi == -1: reject, redraw.


# ---------------------------------------------------------------------
# CORRECTED (v2) SAMPLER -- the one this script actually uses.
# Implements amendments/v1.yaml changes[0].new_construction exactly:
# rejection sampling over 2p+1 equiprobable slots {(x,b)} union {O}.
# ---------------------------------------------------------------------
def sample_group_uniform_v2_corrected(m64, p, A, B, role, tid, counter):
    """Corrected group-uniform point draw per
    amendments/v1.yaml changes[0].new_construction.

    Implementation note (disclosed): the construction is described as a
    single draw of one of 2p+1 equiprobable slots. This function realizes
    that as two independent per-iteration sub-draws with the SAME net
    per-iteration acceptance probability for every point (verified below):
      1. Draw u uniformly in [0, 2p+1) (label "gu-inf"). If u == 2p, accept
         O immediately. [Per-iteration acceptance prob for O: 1/(2p+1).]
      2. Otherwise (probability 2p/(2p+1)), draw x uniformly in F_p (label
         "gu-x") and a fair bit b (label "gu-sign") [joint probability of
         any specific (x,b), given step 2 is reached: 1/(2p)]. Then:
         - f(x) a nonzero square: accept the root selected by b.
           Per-iteration acceptance prob for that specific point:
           (2p/(2p+1)) * (1/(2p)) = 1/(2p+1). Matches a generic point's
           slot probability exactly.
         - f(x) == 0: accept the 2-torsion point when b == 0, reject when
           b == 1. Per-iteration acceptance prob for that 2-torsion point:
           (2p/(2p+1)) * (1/p) * (1/2) = 1/(2p+1). NOT double-weighted,
           unlike sample_group_uniform_v1_biased above.
         - f(x) a non-residue: reject regardless of b (rejects for both b
           values), redraw.
      Every group point (affine two-root, affine 2-torsion, and O alike)
      therefore has per-iteration acceptance probability exactly 1/(2p+1),
      so conditional on acceptance every point is drawn with probability
      exactly 1/N -- matching amendments/v1.yaml's own
      `independent_content_verification` slot-counting proof, which this
      empirically checks (not re-derives) via `check_point_uniformity`.

    Returns (point_or_None, next_counter); point is None for O (matching
    this codebase's own ec_add/ec_neg convention that None == point at
    infinity).
    """
    while True:
        u, counter = m64.draw_uniform("gu-inf", p, role, tid, counter, 2 * p + 1)
        if u == 2 * p:
            return None, counter  # O, the point at infinity.
        x, counter = m64.draw_uniform("gu-x", p, role, tid, counter, p)
        f = (x * x * x + A * x + B) % p
        if f == 0:
            b, counter = m64.draw_uniform("gu-sign", p, role, tid, counter, 2)
            if b == 0:
                return (x, 0), counter
            continue  # b == 1: reject, redraw (this is the fix).
        chi = m64.quad_char(f, p)
        if chi == 1:
            small, large = m64.sqrt_mod_p(f, p)
            b, counter = m64.draw_uniform("gu-sign", p, role, tid, counter, 2)
            y = small if b == 0 else large
            return (x, y), counter
        # chi == -1 (non-residue): reject, redraw.


def measure_group_uniform_v2(m64, curve, ntuples, budget_deadline=None):
    """Group-uniform arm measurement using sample_group_uniform_v2_corrected.
    Distinctness rule generalizes RUN-MONO-cb905d-1's own "distinct
    x-coordinates" rule to also cover O (which has no x-coordinate): the
    3 drawn points per tuple must have distinct KEYS, where a point's key
    is its x-coordinate if affine, or the sentinel "O" if it is the point
    at infinity (so two draws of O in the same tuple are also rejected as
    a duplicate, consistent with treating O as one more group element that
    must not repeat within a tuple)."""
    A, B, p = curve["A"], curve["B"], curve["p"]
    role = curve["role"] + str(curve.get("j"))

    total_pairs_colliding = 0
    tuples_with_collision = 0

    for tid in range(ntuples):
        counter = 0
        chosen_keys = set()
        pts = []
        while len(pts) < 3:
            pt, counter = sample_group_uniform_v2_corrected(m64, p, A, B, role, tid, counter)
            key = "O" if pt is None else pt[0]
            if key in chosen_keys:
                continue
            chosen_keys.add(key)
            pts.append(pt)

        sums = []
        for eps in m64.SIGN_CLASSES:
            acc = None
            for k in range(3):
                term = pts[k] if eps[k] == 1 else m64.ec_neg(pts[k], p)
                acc = m64.ec_add(acc, term, A, p)
            xval = "INF" if acc is None else acc[0]
            sums.append(xval)

        collisions_this_tuple = 0
        for i in range(m64.NCLASSES):
            for j in range(i + 1, m64.NCLASSES):
                if sums[i] == sums[j]:
                    collisions_this_tuple += 1
        total_pairs_colliding += collisions_this_tuple
        if collisions_this_tuple > 0:
            tuples_with_collision += 1

        if budget_deadline is not None and tid % 2000 == 0 and time.time() > budget_deadline:
            raise TimeoutError(f"budget deadline exceeded during group-uniform measurement at tuple {tid}")

    return {
        "ntuples": ntuples,
        "total_pairs_colliding": total_pairs_colliding,
        "tuples_with_collision": tuples_with_collision,
        "rate_pairs_per_tuple": total_pairs_colliding / ntuples,
        "rate_any_collision": tuples_with_collision / ntuples,
    }


def enumerate_group_points(A, B, p):
    """Enumerate all N group elements of E(F_p) as keys: "O" for the point
    at infinity, (x, 0) for each affine 2-torsion point, (x, y) for each
    of the two roots at a two-root x. Used only by the point-uniformity
    sanity check below (never by the headline measurement)."""
    points = ["O"]
    for x in range(p):
        f = (x * x * x + A * x + B) % p
        if f == 0:
            points.append((x, 0))
            continue
        # quad_char computed inline to avoid importing m64 into this
        # pure-enumeration helper's signature.
        r = pow(f, (p - 1) // 2, p)
        if r == 1:
            for y in range(1, (p // 2) + 1):
                if (y * y) % p == f:
                    other = (p - y) % p
                    points.append((x, min(y, other)))
                    points.append((x, max(y, other)))
                    break
    return points


def check_point_uniformity(m64, curve, n_draws, budget_deadline=None):
    """Empirical sanity check (in addition to, not instead of, the
    amendment's own analytic slot-counting proof cited in the execution
    report): draw n_draws single points independently from
    sample_group_uniform_v2_corrected and confirm no point-class is
    over/under-represented beyond ordinary sampling noise. Reports:
    - per-category (O / affine-2-torsion / generic) observed-vs-expected
      ratios (expected = n_draws / N for every individual point, summed
      per category),
    - a chi-square goodness-of-fit statistic over all N individual points
      against the uniform null (df = N - 1; stat/df ~ 1 under the null),
    - the max and min per-point observed/expected ratio across all N
      points actually enumerated.
    Uses a run-scoped, disjoint label ("gu-unif-check-*") so this check's
    own draws never share a seed stream with the headline measurement's
    "gu-inf"/"gu-x"/"gu-sign" draws above."""
    A, B, p, N = curve["A"], curve["B"], curve["p"], curve["N"]
    role = "unifcheck-" + curve["role"] + str(curve.get("j"))

    all_points = enumerate_group_points(A, B, p)
    assert len(all_points) == N, f"enumerate_group_points found {len(all_points)} points, expected N={N}"

    counts = {}
    for tid in range(n_draws):
        counter = 0
        pt, counter = sample_group_uniform_v2_corrected(m64, p, A, B, role, tid, counter)
        key = "O" if pt is None else pt
        counts[key] = counts.get(key, 0) + 1
        if budget_deadline is not None and tid % 5000 == 0 and time.time() > budget_deadline:
            raise TimeoutError(f"budget deadline exceeded during point-uniformity check at draw {tid}")

    expected_per_point = n_draws / N
    chi_sq = 0.0
    ratios = []
    for key in all_points:
        obs = counts.get(key, 0)
        chi_sq += (obs - expected_per_point) ** 2 / expected_per_point
        ratios.append(obs / expected_per_point if expected_per_point > 0 else None)

    O_obs = counts.get("O", 0)
    affine_2tors_keys = [k for k in all_points if k != "O" and k[1] == 0]
    generic_keys = [k for k in all_points if k != "O" and k[1] != 0]
    affine_2tors_obs = sum(counts.get(k, 0) for k in affine_2tors_keys)
    generic_obs = sum(counts.get(k, 0) for k in generic_keys)

    def ratio(obs, n_keys):
        expected = n_keys * expected_per_point
        return obs / expected if expected > 0 else None

    unseen = sum(1 for k in all_points if k not in counts)

    return {
        "n_draws": n_draws,
        "N": N,
        "expected_count_per_point": expected_per_point,
        "chi_square_statistic": chi_sq,
        "chi_square_df": N - 1,
        "chi_square_stat_over_df": chi_sq / (N - 1),
        "n_points_never_observed": unseen,
        "category_ratios_observed_over_expected": {
            "O": ratio(O_obs, 1),
            "affine_2_torsion": ratio(affine_2tors_obs, len(affine_2tors_keys)),
            "generic": ratio(generic_obs, len(generic_keys)),
        },
        "per_point_ratio_min": min(ratios),
        "per_point_ratio_max": max(ratios),
        "note": (
            "chi_square_stat_over_df near 1.0 and all three category ratios "
            "near 1.0 (no systematic ~2x gap between affine_2_torsion and "
            "generic, unlike the v1-biased sampler) is consistent with the "
            "amendment's own analytic 1/N-per-point proof; this is a "
            "spot-check, not a substitute for that proof."
        ),
    }


def main():
    t_start = time.time()
    hard_deadline = t_start + 3600  # same budget cap as the original spec

    result = {
        "run": "RUN-MONO-cb905d-2",
        "seed_label": SEED,
        "domain_v2": CB_DOMAIN_V2,
        "status": None,
        "part_a": {},
        "point_uniformity_check": {},
        "anomalies": [],
        "timing": {},
    }

    m64 = load_m64()  # m64.DOMAIN == "EXP-MONO-64aaa4/v1" here

    with open(EXP64_RAW_RESULT) as f:
        raw64 = json.load(f)
    with open(RUN1_RAW_RESULT) as f:
        raw1 = json.load(f)

    part_a = {}

    # Stopping rule (same as RUN-MONO-cb905d-1's own script): re-derive the
    # p=617 curves under EXP-MONO-64aaa4's OWN domain and require an EXACT
    # match against the archived transcript before proceeding.
    archived_ord = raw64["stage1"]["primary"]["construction_transcript"]["ord"]
    archived_cm = raw64["stage1"]["primary"]["construction_transcript"]["cm"]
    rederived_ord = m64.construct_ordinary(617)
    rederived_cm = m64.construct_cm_j1728(617)

    ord_match = (rederived_ord["A"] == archived_ord["A"] and
                 rederived_ord["B"] == archived_ord["B"] and
                 rederived_ord["N"] == archived_ord["N"] and
                 rederived_ord["tau"] == archived_ord["tau"])
    cm_match = (rederived_cm["A"] == archived_cm["A"] and
                rederived_cm["B"] == archived_cm["B"] and
                rederived_cm["N"] == archived_cm["N"] and
                rederived_cm["tau"] == archived_cm["tau"])

    part_a["curve_rederivation_check"] = {
        "ord_match": ord_match, "cm_match": cm_match,
        "rederived_ord": {k: rederived_ord[k] for k in ("A", "B", "N", "tau")},
        "archived_ord": {k: archived_ord[k] for k in ("A", "B", "N", "tau")},
        "rederived_cm": {k: rederived_cm[k] for k in ("A", "B", "N", "tau")},
        "archived_cm": {k: archived_cm[k] for k in ("A", "B", "N", "tau")},
    }

    if not (ord_match and cm_match):
        result["status"] = "failed_infrastructure"
        result["part_a"] = part_a
        result["part_a"]["disposition"] = (
            "STOPPING RULE TRIGGERED: re-derived p=617 curve(s) do not match "
            "EXP-MONO-64aaa4's own archived transcript exactly. Reported as "
            "failed_infrastructure per the frozen contract; NOT proceeding "
            "with a silently-different curve. No mathematical evidence."
        )
        result["timing"]["total_seconds"] = time.time() - t_start
        return result

    # From here on, use the NEW v2 domain for every group-uniform draw this
    # script performs (both the headline measurement and the point-
    # uniformity check).
    m64.DOMAIN = CB_DOMAIN_V2

    # Part A transversal arm: reused DIRECTLY from RUN-MONO-cb905d-1's own
    # raw-result.json (unaffected by the sampler defect; NOT redrawn), per
    # the handoff's explicit instruction.
    part_a["transversal_arm_reused_from"] = str(RUN1_RAW_RESULT.relative_to(REPO_ROOT))
    part_a["transversal"] = raw1["part_a"]["transversal"]

    curve_ord_617 = {"A": archived_ord["A"], "B": archived_ord["B"], "p": 617,
                      "N": archived_ord["N"], "tau": archived_ord["tau"],
                      "role": "ord", "j": None}
    curve_cm_617 = {"A": archived_cm["A"], "B": archived_cm["B"], "p": 617,
                     "N": archived_cm["N"], "tau": archived_cm["tau"],
                     "role": "cm", "j": "j1728"}

    gu_ord = measure_group_uniform_v2(m64, curve_ord_617, NTUPLES, budget_deadline=hard_deadline - 300)
    gu_cm = measure_group_uniform_v2(m64, curve_cm_617, NTUPLES, budget_deadline=hard_deadline - 300)

    part_a["group_uniform"] = {"ord": gu_ord, "cm": gu_cm}
    part_a["group_uniform_sampler"] = "sample_group_uniform_v2_corrected"

    ord_transversal_rate = part_a["transversal"]["ord"]["rate_pairs_per_tuple"]
    cm_transversal_rate = part_a["transversal"]["cm"]["rate_pairs_per_tuple"]
    P1 = gu_ord["rate_pairs_per_tuple"] / ord_transversal_rate if ord_transversal_rate > 0 else None
    P2 = gu_cm["rate_pairs_per_tuple"] / cm_transversal_rate if cm_transversal_rate > 0 else None

    obj6_lo, obj6_hi = 1.84, 2.08
    part_a["metrics"] = {
        "P1_ord_group_uniform_over_transversal_ratio": P1,
        "P2_cm_group_uniform_over_transversal_ratio": P2,
        "obj6_prior_range": [obj6_lo, obj6_hi],
        "obj6_prior_source": "experiments/EXP-MONO-12ce1c/reviews/red-team/red-team-report.yaml OBJ-6 (measured 1.84-2.08x at m=4)",
        "P1_in_obj6_range": (P1 is not None and obj6_lo <= P1 <= obj6_hi),
        "P2_in_obj6_range": (P2 is not None and obj6_lo <= P2 <= obj6_hi),
    }
    if not (part_a["metrics"]["P1_in_obj6_range"] and part_a["metrics"]["P2_in_obj6_range"]):
        result["anomalies"].append({
            "type": "obj6_effect_reproduction_check",
            "detail": (
                f"P1={P1}, P2={P2} vs OBJ-6 prior range [{obj6_lo},{obj6_hi}]. "
                "Reported PROMINENTLY per the falsification_criterion/stopping_rules: "
                "at least one curve's group-uniform/transversal ratio fell outside "
                "the previously-measured 1.84-2.08x range."
            ),
        })

    ratio_of_ratios = (P1 / P2) if (P1 is not None and P2 is not None and P2 != 0) else None
    a_gu = gu_ord["tuples_with_collision"]
    b_gu = gu_ord["ntuples"] - a_gu
    c_gu = gu_cm["tuples_with_collision"]
    d_gu = gu_cm["ntuples"] - c_gu
    gu_odds_ratio, gu_pvalue = m64.fisher_exact_2x2(a_gu, b_gu, c_gu, d_gu)

    part_a["P3_headline_comparison"] = {
        "ratio_of_ratios_P1_over_P2": ratio_of_ratios,
        "group_uniform_fisher_exact_ord_vs_cm": {
            "table": {"ord_collision": a_gu, "ord_no_collision": b_gu,
                      "cm_collision": c_gu, "cm_no_collision": d_gu},
            "odds_ratio": gu_odds_ratio,
            "p_value": gu_pvalue,
            "significant_at_0.05": bool(gu_pvalue < 0.05),
        },
        "note": (
            "Headline result per stage_2_part_a. Two-sided, genuinely open per "
            "preregistered_prediction: agreement (ratio near 1, p >= 0.05) reads "
            "as (N,tau)-determined; material disagreement (ratio far from 1, "
            "p < 0.05) reads as endomorphism-ring-linked. This script reports "
            "the comparison statistics only; it does NOT declare either reading."
        ),
    }

    result["part_a"] = part_a

    # ---------------- POINT-UNIFORMITY SANITY CHECK ----------------
    puc_ord = check_point_uniformity(m64, curve_ord_617, UNIFORMITY_CHECK_DRAWS_PER_CURVE,
                                      budget_deadline=hard_deadline - 60)
    puc_cm = check_point_uniformity(m64, curve_cm_617, UNIFORMITY_CHECK_DRAWS_PER_CURVE,
                                     budget_deadline=hard_deadline - 60)
    result["point_uniformity_check"] = {"ord": puc_ord, "cm": puc_cm}

    result["status"] = "completed_valid"
    result["timing"]["total_seconds"] = time.time() - t_start
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result["timing"]["peak_rss_bytes"] = peak_rss * 1024 if sys.platform != "darwin" else peak_rss
    return result


if __name__ == "__main__":
    try:
        res = main()
        print(json.dumps(res, indent=2))
        if res.get("status") == "failed_infrastructure":
            sys.exit(3)
    except TimeoutError as e:
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": "TimeoutError", "message": str(e)}, indent=2))
        sys.exit(2)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": type(e).__name__, "message": str(e),
                           "traceback": traceback.format_exc()}, indent=2))
        sys.exit(1)
