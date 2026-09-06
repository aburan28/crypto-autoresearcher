"""EXP-PFDR-4bfc6f Stage 1 -- CTRL-METER-CROSSCHECK.

Feeds the EXACT same polynomial systems the Sage reconstructed inline meter
measured (stage1_driver.sage, stage1_driver_result.json) into the shared F_p
port (harness/macaulay_fp/, ordinary-monomial mode, 3 free variables e1,e2,e3)
and compares d_ff, D_reg, fires, kernel dimension and the shrink test.

No Sage dependency; pure Python; reads harness/macaulay_fp/ at its committed
path (write_scope: experiments/EXP-PFDR-4bfc6f/ only -- this file lives there
and only reads harness/macaulay_fp/, never writes to it).
"""
import json
import sys

sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees/agent-ad60a5f9e11a8eacd")

from harness.macaulay_fp.poly import Ring
from harness.macaulay_fp.macaulay import analyze_degrees, first_nontrivial_syzygy
from harness.macaulay_fp.series import semiregular_prediction
from harness.macaulay_fp.localization import localization_gate

IN_JSON = "/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees/agent-ad60a5f9e11a8eacd/experiments/EXP-PFDR-4bfc6f/source/stage1_driver_result.json"
OUT_JSON = "/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees/agent-ad60a5f9e11a8eacd/experiments/EXP-PFDR-4bfc6f/source/stage1_fp_crosscheck_result.json"


def coeffs_to_poly(coeffs, p):
    out = {}
    for k, v in coeffs.items():
        exps = tuple(int(x) for x in k.strip("()").split(",") if x.strip() != "")
        c = int(v) % p
        if c != 0:
            out[(0, exps)] = c
    return out


def measure(ring, polys, sum_index, label):
    degs = [max(sum(e) for (_, e) in poly) for poly in polys]
    Dmax = max(degs) + 6
    layers = analyze_degrees(ring, polys, min(degs), Dmax, "per_layer", leading_forms=True)
    d_ff = first_nontrivial_syzygy(layers)
    pred = semiregular_prediction(ring, degs, Dmax + 2, frobenius=False)
    D_reg = pred.d_reg
    fires = (d_ff is not None) and (d_ff < D_reg)
    result = {
        "label": label, "degs": degs, "d_ff": d_ff, "D_reg": D_reg, "fires": fires,
    }
    if d_ff is not None:
        g = localization_gate(ring, polys, d_ff, subset=[sum_index])
        result["shrink_test"] = {
            "D": d_ff,
            "nontriv_full": g.nontriv_full_series if g.nontriv_full_series is not None else g.nontriv_full_pairwise,
            "nontriv_fb": g.nontriv_fb_series if g.nontriv_fb_series is not None else g.nontriv_fb_pairwise,
            "shrink": g.localization_bit_series if g.localization_bit_series is not None else g.localization_bit_pairwise,
        }
    return result


def main():
    with open(IN_JSON) as f:
        data = json.load(f)

    out = {"cells": {}}
    for fb_key, cell in data["e_ring_cells"].items():
        pe = cell["poly_export"]
        p = pe["p"]
        ring = Ring(p, 0, 3)

        S4sym = coeffs_to_poly(pe["S4sym"], p)
        cons = [coeffs_to_poly(c, p) for c in pe["membership_cons"]]
        null_s4_poly = coeffs_to_poly(pe["null_s4_poly"], p)
        null_fb_polys = [coeffs_to_poly(c, p) for c in pe["null_fb_polys"]]
        gt_polys = [coeffs_to_poly(c, p) for c in pe["generic_twin_polys"]]

        semaev_sys = [S4sym] + cons
        null_s4_sys = [null_s4_poly] + cons
        null_fb_sys = [S4sym] + null_fb_polys

        r_semaev = measure(ring, semaev_sys, 0, "semaev_arm FB=%s" % fb_key)
        r_nulls4 = measure(ring, null_s4_sys, 0, "null_s4 FB=%s" % fb_key)
        r_nullfb = measure(ring, null_fb_sys, 0, "null_fb FB=%s" % fb_key)
        r_gt = measure(ring, gt_polys, 0, "generic_twin FB=%s" % fb_key)

        sage_semaev = cell["semaev_arm"]
        sage_nulls4 = cell["null_s4"]
        sage_nullfb = cell["null_fb"]
        sage_gt = cell["generic_twin"]

        def agree(fp_r, sage_r):
            # CONVENTION DIFFERENCE (disclosed, not silently patched): the
            # reconstructed inline meter (Sage side, matching the archived
            # round005 meter() literally) defaults d_ff = D_reg when no
            # nontrivial syzygy is found at or below D_reg ("if d_ff is
            # None: d_ff = Dreg"); the F_p port's first_nontrivial_syzygy
            # returns None in that case ("no early fall observed in the
            # scanned range") rather than synonymising it with D_reg. Both
            # report the SAME fires bit and the SAME D_reg in every
            # measured cell; only the None-vs-D_reg default for a
            # non-firing d_ff differs. Normalised here for the agreement
            # check; the raw values are still recorded unnormalised above.
            fp_dff = fp_r["d_ff"] if fp_r["d_ff"] is not None else fp_r["D_reg"]
            return (fp_dff == sage_r["d_ff"] and fp_r["D_reg"] == sage_r["D_reg_pred"]
                    and fp_r["fires"] == sage_r["fires"])

        agreement = {
            "semaev_arm": agree(r_semaev, sage_semaev),
            "null_s4": agree(r_nulls4, sage_nulls4),
            "null_fb": agree(r_nullfb, sage_nullfb),
            "generic_twin": agree(r_gt, sage_gt),
        }
        shrink_agree = None
        if "shrink_test" in r_semaev:
            shrink_agree = (r_semaev["shrink_test"]["shrink"] == cell["semaev_arm"]["shrink_test"]["shrink"])

        out["cells"][fb_key] = {
            "fp_meter": {"semaev_arm": r_semaev, "null_s4": r_nulls4, "null_fb": r_nullfb, "generic_twin": r_gt},
            "agreement_with_inline_meter": agreement,
            "shrink_test_agreement": shrink_agree,
        }
        print("FB=%s semaev_arm fp=(d_ff=%s,D_reg=%s,fires=%s) sage=(d_ff=%s,D_reg=%s,fires=%s) agree=%s shrink_agree=%s"
              % (fb_key, r_semaev["d_ff"], r_semaev["D_reg"], r_semaev["fires"],
                 sage_semaev["d_ff"], sage_semaev["D_reg_pred"], sage_semaev["fires"],
                 agreement["semaev_arm"], shrink_agree))
        print("  null_s4 agree=%s null_fb agree=%s generic_twin agree=%s"
              % (agreement["null_s4"], agreement["null_fb"], agreement["generic_twin"]))

    all_agree = all(
        all(cellres["agreement_with_inline_meter"].values())
        for cellres in out["cells"].values()
    )
    out["all_controls_agree"] = all_agree
    print("ALL_CONTROLS_AGREE =", all_agree)

    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote", OUT_JSON)


if __name__ == "__main__":
    main()
