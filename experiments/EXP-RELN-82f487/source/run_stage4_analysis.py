"""Stage 4: gates and (non-fittable, single-rung) branch classification for
the priority-2 cell (rung=2^14, curve_seed=101, base_seed=201,
training_seed=301, sigma=1/8)."""
import json
import sys

SIGMA = 0.125


def analyze(all_arms):
    out = {}
    # Fixtures
    fixtures = {}
    for arm, d in all_arms.items():
        fixtures[arm] = {
            "total_check_deviation": d["total_check"]["deviation"],
            "sigma_one_lambda": d["sigma_one_fixture"]["lambda"],
            "sigma_one_rho": d["sigma_one_fixture"]["rho"],
            "grammar_all_exact": d["grammar_reproduction_fixture"]["all_exact"],
        }
    out["fixtures"] = fixtures
    out["fixtures_all_pass"] = all(
        f["total_check_deviation"] == 0 and f["sigma_one_lambda"] == 1.0 and f["sigma_one_rho"] == 1.0
        and f["grammar_all_exact"] for f in fixtures.values()
    )

    # Z/N-interval positive control (half-ceiling threshold = 0.5/sigma)
    ceiling = 1.0 / SIGMA
    half_ceiling = 0.5 * ceiling
    pos_control = {}
    for regime in ["F0", "F1"]:
        r = all_arms["ZN_interval"]["regimes"][regime]
        for cls in ["gnn", "trees"]:
            m = r["model_metrics"][cls]["metrics"]
            pos_control[f"{regime}_{cls}"] = {
                "lambda": m["lambda"], "rho": m["rho"],
                "half_ceiling_threshold": half_ceiling, "ceiling": ceiling,
                "pass": bool(m["lambda"] >= half_ceiling and m["rho"] >= half_ceiling),
            }
    out["positive_control_ZN_interval"] = pos_control
    out["positive_control_any_class_pass_every_regime"] = {
        regime: any(pos_control[f"{regime}_{cls}"]["pass"] for cls in ["gnn", "trees"])
        for regime in ["F0", "F1"]
    }

    # Label-permutation null verdict (every arm, F0 and F1, both classes).
    # Per specification.yaml's label_permutation_null control: "A permuted-
    # label lift ABOVE band is a LEAK" -- a value BELOW the lower band bound
    # is not a leak (the model failed to exploit permuted-random labels,
    # which is the innocuous direction); only above-band is blocking. Both
    # directions are recorded, but only above-band is gated on.
    perm_verdict = {}
    leak_found = False
    for arm, d in all_arms.items():
        for regime in ["F0", "F1"]:
            r = d["regimes"][regime]
            band_lo_lam, band_hi_lam = r["selection_null"]["lambda_band"]
            band_lo_rho, band_hi_rho = r["selection_null"]["rho_band"]
            for cls, pv in r.get("label_permutation_null", {}).items():
                key = f"{arm}_{regime}_{cls}"
                m = pv["metrics"]
                above_lam = m["lambda"] > band_hi_lam
                above_rho = m["rho"] > band_hi_rho
                below_lam = m["lambda"] < band_lo_lam
                below_rho = m["rho"] < band_lo_rho
                perm_verdict[key] = {
                    "lambda": m["lambda"], "rho": m["rho"],
                    "band_lambda": [band_lo_lam, band_hi_lam], "band_rho": [band_lo_rho, band_hi_rho],
                    "above_band_lambda": above_lam, "above_band_rho": above_rho,
                    "below_band_lambda": below_lam, "below_band_rho": below_rho,
                    "leak_verdict_per_spec_above_band_only": bool(above_lam or above_rho),
                }
                if above_lam or above_rho:
                    leak_found = True
    out["label_permutation_verdicts"] = perm_verdict
    out["label_permutation_leak_detected"] = leak_found

    # Canary check (E_log_interval_canary): per spec "A lift ABOVE band is a
    # leak of the logarithm or a DLP predictor" -- below-band is not gated.
    canary = {}
    canary_leak = False
    for regime in ["F0", "F1"]:
        r = all_arms["E_log_interval_canary"]["regimes"][regime]
        band_lo_lam, band_hi_lam = r["selection_null"]["lambda_band"]
        band_lo_rho, band_hi_rho = r["selection_null"]["rho_band"]
        for cls in ["gnn", "trees"]:
            m = r["model_metrics"][cls]["metrics"]
            above_lam = m["lambda"] > band_hi_lam
            above_rho = m["rho"] > band_hi_rho
            canary[f"{regime}_{cls}"] = {
                "lambda": m["lambda"], "rho": m["rho"],
                "band_lambda": [band_lo_lam, band_hi_lam], "band_rho": [band_lo_rho, band_hi_rho],
                "above_band_lambda": above_lam, "above_band_rho": above_rho,
                "leak_verdict_per_spec_above_band_only": bool(above_lam or above_rho),
            }
            if above_lam or above_rho:
                canary_leak = True
    out["canary_check"] = canary
    out["canary_leak_detected"] = canary_leak

    # E/random vs Z/N-random agreement (pipeline-fault check). Per spec:
    # "E/random must agree with Z/N-random within band (nearby-object
    # control)" -- this compares the two arms' rho DIRECTLY against each
    # other, using the combined selection-null band half-width as the
    # tolerance (the two arms have independent selection-null draws so we
    # use the larger of the two band half-widths, conservative). Each arm
    # being inside its OWN null band is reported separately as a diagnostic,
    # not folded into the pipeline-fault verdict (H2 predicts Z/N-random
    # lift is lookup capacity, subtracted, not itself a fault).
    pipeline_fault = False
    er_vs_zr = {}
    for regime in ["F0", "F1"]:
        er = all_arms["E_random_matched"]["regimes"][regime]
        zr = all_arms["ZN_random"]["regimes"][regime]
        for cls in ["gnn", "trees"]:
            er_m = er["model_metrics"][cls]["metrics"]
            zr_m = zr["model_metrics"][cls]["metrics"]
            er_band = er["selection_null"]["rho_band"]
            zr_band = zr["selection_null"]["rho_band"]
            er_in = er_band[0] <= er_m["rho"] <= er_band[1]
            zr_in = zr_band[0] <= zr_m["rho"] <= zr_band[1]
            er_halfwidth = (er_band[1] - er_band[0]) / 2.0
            zr_halfwidth = (zr_band[1] - zr_band[0]) / 2.0
            tolerance = max(er_halfwidth, zr_halfwidth)
            diff = abs(er_m["rho"] - zr_m["rho"])
            agree = bool(diff <= tolerance)
            er_vs_zr[f"{regime}_{cls}"] = {
                "E_random_rho": er_m["rho"], "ZN_random_rho": zr_m["rho"],
                "abs_difference": diff, "tolerance_band_halfwidth": tolerance,
                "agree_within_band": agree,
                "E_random_in_own_selection_null_band": er_in,
                "ZN_random_in_own_selection_null_band": zr_in,
            }
            if not agree:
                pipeline_fault = True
    out["E_random_vs_ZN_random"] = er_vs_zr
    out["pipeline_fault_detected"] = pipeline_fault

    # GNN-minus-trees difference (all arms, both regimes)
    gmt = {}
    for arm, d in all_arms.items():
        for regime in ["F0", "F1"]:
            r = d["regimes"][regime]
            gmt[f"{arm}_{regime}"] = r["gnn_minus_trees"]
    out["gnn_minus_trees"] = gmt

    # E/x-interval excess over null (the primary quantity), both regimes/classes
    ex_slice = {}
    for regime in ["F0", "F1"]:
        r = all_arms["E_x_interval"]["regimes"][regime]
        for cls in ["gnn", "trees"]:
            ex_slice[f"{regime}_{cls}"] = r["excess"][cls]
    out["E_x_interval_excess"] = ex_slice

    # INV-6 theorem arm
    out["inv6_theorem_arm"] = all_arms["E_x_interval"]["inv6_theorem_arm"]

    # Gating logic per specification.yaml's success_criterion /
    # falsification_criterion / decision_paths
    gates_ok = (out["fixtures_all_pass"] and not out["label_permutation_leak_detected"]
                and not out["canary_leak_detected"] and not out["pipeline_fault_detected"])
    out["all_blocking_gates_pass"] = gates_ok

    classification = {}
    for regime in ["F0", "F1"]:
        pc_pass = out["positive_control_any_class_pass_every_regime"][regime]
        if not gates_ok:
            classification[regime] = "INCONCLUSIVE: blocking gate failed (see label_permutation_leak_detected / canary_leak_detected / pipeline_fault_detected / fixtures_all_pass)"
        elif not pc_pass:
            classification[regime] = "INCONCLUSIVE: Z/N-interval positive control below half-ceiling for every class at this rung -- this rung is UNINFORMATIVE for this regime, no negative or positive may be reported"
        else:
            e_in_band = {cls: ex_slice[f"{regime}_{cls}"]["rho_inside_band"] and ex_slice[f"{regime}_{cls}"]["lambda_inside_band"]
                         for cls in ["gnn", "trees"]}
            classification[regime] = (
                f"NOT FITTABLE (single rung only, 2^14): E/x-interval excess "
                f"inside selection-null band for both classes = {e_in_band}. "
                f"A slope needs >=2 rungs; this cell alone cannot distinguish "
                f"the -1/2 (predicted) vs 0 (alive) branch by slope. If excess "
                f"is inside band here that is CONSISTENT WITH (not proof of) "
                f"the predicted branch at this one rung; it is equally "
                f"consistent with an alive excess that happens to be small at "
                f"this smallest rung. Reported as inconclusive-for-branch-"
                f"classification, with the raw excess numbers themselves as "
                f"the reportable observation."
            )
    out["branch_classification"] = classification
    return out


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        all_arms = json.load(f)
    result = analyze(all_arms)
    with open(sys.argv[2], "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
