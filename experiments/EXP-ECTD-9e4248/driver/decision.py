"""
decision.py -- the frozen FIVE-branch decision table (spec.decision_table, v2,
red-team finding D1 fix), applied exactly as pre-registered: no post-hoc threshold
tuning, no new branches invented, moderate_effect_unresolved computed as the exact
logical complement of the other two data-bearing branches (never enumerated).
"""
from .reused import analysis
from . import ks as ks_mod

RATIO_THRESHOLD = 100
BAND_LO, BAND_HI = 0.1, 10
DELTA_D_THRESHOLD = 2
ALL_METERS = analysis.ALL_PRIMARY  # 5 primary meters, identical set/order to EXP-ECTD-001


def edge_any_meter_ge_100_or_delta2(edge):
    for m, r in edge["ratios"].items():
        if r != float("inf") and r >= RATIO_THRESHOLD:
            return True
        if r == float("inf"):
            return True  # unbounded ratio counts as an extreme hit, never silently excluded
    if edge["delta_d_reg"] >= DELTA_D_THRESHOLD:
        return True
    return False


def edge_all_meters_in_band(edge):
    for m, r in edge["ratios"].items():
        if r == float("inf"):
            return False
        if not (BAND_LO <= r <= BAND_HI):
            return False
    return True


def build_ratio_samples(edges, horizontal_pairs):
    vertical_ratios = []
    for e in edges:
        for m in ALL_METERS:
            vertical_ratios.append(e["ratios"][m])
    horizontal_ratios = []
    for h in horizontal_pairs:
        for m in ALL_METERS:
            horizontal_ratios.append(h["ratios"][m])
    return vertical_ratios, horizontal_ratios


def decide(completed_edges, all_edges_attempted, min_vertical_edges,
           end_ring_cert_fail_count, glv_result, permutation_results):
    """completed_edges: list of edge dicts with status=='ok'.
    Returns dict with decision_branch and full supporting statistics -- OBSERVATIONS
    ONLY, no interpretive language about the hypothesis being supported/refuted."""
    n_completed = len(completed_edges)

    # instrument_void: two independently-sufficient OR'd conditions (D5 fix)
    glv_failed_expected_move = False
    glv_reason = None
    if glv_result.get("status") != "ok":
        glv_failed_expected_move = True
        glv_reason = f"glv_instrument status={glv_result.get('status')}"
    else:
        if not glv_result.get("phi_is_on_curve", False):
            glv_failed_expected_move = True
            glv_reason = "phi(P) not on curve"
        elif not glv_result.get("phi_equals_scalar_mul_lambda", False):
            glv_failed_expected_move = True
            glv_reason = "phi(P) != lambda*P (endomorphism did not show its expected move)"

    if end_ring_cert_fail_count > 1 or glv_failed_expected_move:
        return {
            "decision_branch": "instrument_void",
            "reason": {
                "end_ring_cert_fail_count_gt_1": end_ring_cert_fail_count > 1,
                "end_ring_cert_fail_count": end_ring_cert_fail_count,
                "glv_failed_expected_move": glv_failed_expected_move,
                "glv_reason": glv_reason,
            },
            "n_completed_edges": n_completed,
        }

    if n_completed < min_vertical_edges:
        return {
            "decision_branch": "resource_incomplete",
            "reason": f"only {n_completed} of {min_vertical_edges} required vertical "
                      f"edges completed within budget",
            "n_completed_edges": n_completed,
        }

    horizontal_pairs = [e["horizontal"] for e in completed_edges if e["horizontal"]["status"] == "ok"]
    if len(horizontal_pairs) < min_vertical_edges:
        return {
            "decision_branch": "resource_incomplete",
            "reason": f"only {len(horizontal_pairs)} of {min_vertical_edges} required "
                      f"matched horizontal pairs completed within budget",
            "n_completed_edges": n_completed,
            "n_horizontal_pairs": len(horizontal_pairs),
        }

    vertical_ratios, horizontal_ratios = build_ratio_samples(completed_edges, horizontal_pairs)
    ks_result = ks_mod.ks_two_sample(vertical_ratios, horizontal_ratios)

    any_edge_ge_100 = any(edge_any_meter_ge_100_or_delta2(e) for e in completed_edges)
    all_edges_in_band = all(edge_all_meters_in_band(e) for e in completed_edges)
    ks_rejects = bool(ks_result["rejects"]) if ks_result["rejects"] is not None else False

    discontinuity = ks_rejects and any_edge_ge_100
    continuity = all_edges_in_band and (not ks_rejects)

    if discontinuity:
        branch = "discontinuity_nominates_endpoint"
    elif continuity:
        branch = "continuity_scoped"
    else:
        branch = "moderate_effect_unresolved"

    shape = None
    if branch == "moderate_effect_unresolved":
        if (not ks_rejects) and (not all_edges_in_band):
            shape = "i: KS does not reject; >=1 edge ratio outside [0.1,10] but none >=100/delta2"
        elif ks_rejects and (not any_edge_ge_100):
            shape = "ii: KS rejects (real distributional difference) but no single edge "\
                    "individually crosses the 100x/delta_d_reg-2 threshold (diffuse signal)"
        else:
            shape = "unexpected combination -- recorded verbatim, not smoothed"

    return {
        "decision_branch": branch,
        "moderate_effect_shape": shape,
        "ks_result": ks_result,
        "ks_rejects_exchangeability": ks_rejects,
        "any_edge_ge_100_or_delta2": any_edge_ge_100,
        "all_edges_in_band_0p1_10": all_edges_in_band,
        "n_completed_edges": n_completed,
        "n_horizontal_pairs": len(horizontal_pairs),
        "n_vertical_ratio_samples": len(vertical_ratios),
        "n_horizontal_ratio_samples": len(horizontal_ratios),
        "per_edge_flags": [
            {"seed": e["seed"], "any_ge_100_or_delta2": edge_any_meter_ge_100_or_delta2(e),
             "all_in_band": edge_all_meters_in_band(e), "max_ratio": e["max_ratio"],
             "delta_d_reg": e["delta_d_reg"]}
            for e in completed_edges
        ],
    }
