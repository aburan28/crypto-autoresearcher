#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- READING RULES of the addendum (pure functions, no I/O).

  A1-3  HEUR-GFPN-DFLAT evaluation sets and triple accounting, per (arm, shape).
  A1-4  the off-shape label for every (p' = 16777291, ecgfp5_shaped) row.
  AA-4  the matched-triple figure (DEC-20260923-8b2dbf): descriptive, never a verdict.
The definition of relative variation, the 0.10 threshold and the span rule are v2_scoring.heur_dflat's,
called unchanged on each triple (so with exactly three rungs A1-3 and heur_dflat give the same verdict).
Nothing here concludes that HEUR-GFPN-DFLAT is supported or refuted.
"""
import itertools
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

import v2_scoring as SC                                  # noqa: E402

M5_ARMS_2T = ["torsion_S5_rq", "S5", "S5_rescaled", "torsion_S5_norm"]

# A1-3 sets (31-bit plan). Under FB-1 the primary set would be {4111, 262151, 16777291/c_fb1} and the controls v2's three rungs.
EVAL_SETS = {
    "ecgfp5_shaped": {"arms": M5_ARMS_2T, "S": [4111, 262151, 1073741831], "not_applicable_arms": {"raw": "m = 5 not_attempted by design (A-6)"}},
    "random_2torsion": {"arms": M5_ARMS_2T, "S": [4111, 262151, 16777291, 1073741831], "not_applicable_arms": {"raw": "m = 5 not_attempted by design (A-6)"}},
    "random_no2torsion": {"arms": ["S5"], "S": [4111, 262151, 16777291, 1073741831],
                          "not_applicable_arms": {"torsion_S5_rq": "recorded refusal: no rational 2-torsion (R-6, R-9)",
                                                  "S5_rescaled": "recorded refusal: no rational 2-torsion (R-6, R-9)",
                                                  "torsion_S5_norm": "recorded refusal: no rational 2-torsion (R-6, R-9)",
                                                  "raw": "m = 5 not_attempted by design (A-6)"}},
}
MATCHED_TRIPLE = [4111, 262151, 1073741831]
MATCHED_LABEL = "matched-triple figure (same rungs as the primary set); descriptive; not a verdict"
ALL_POINTS_LABEL = "all-points figure, descriptive"


def is_off_shape(p, shape):
    return (int(p), shape) == AC.OFF_SHAPE_KEY


def reading_label(p, shape):
    """A1-4: the label a row is READ under (never written into a v2 byte)."""
    return AC.OFF_SHAPE_LABEL if is_off_shape(p, shape) else shape


def span_bits(ps):
    return max(ps).bit_length() - min(ps).bit_length()


def a1_3_verdict(S, cell_D):
    """S: the declared rung set. cell_D: {p: defined cell D or None} for this (arm, shape), m = 5 random cells.
    Returns the A1-3 block: verdict, triples evaluated, triples not evaluable, and the all-points figure."""
    S = sorted(int(p) for p in S)
    measured = {p: cell_D.get(p) for p in S if cell_D.get(p)}
    eligible = [t for t in itertools.combinations(S, 3) if span_bits(t) >= 12]
    evaluated, not_evaluable = [], []
    for t in eligible:
        if all(p in measured for p in t):
            fig = SC.heur_dflat([(p, measured[p]) for p in t])
            evaluated.append({"triple": list(t), "bits": [p.bit_length() for p in t], "span_bits": span_bits(t),
                              "D": {str(p): measured[p] for p in t}, "D_relative_variation": fig["D_relative_variation"],
                              "D_max_over_min": fig["D_max_over_min"], "below_threshold": fig["heur_dflat_pass"] is True,
                              "threshold": SC.DFLAT_THRESHOLD, "v2_heur_dflat_on_triple": fig})
        else:
            not_evaluable.append({"triple": list(t), "span_bits": span_bits(t),
                                  "missing_D_at": [p for p in t if p not in measured]})
    if not evaluated:
        verdict = "not_applicable"
        reason = "no eligible triple has a defined cell D at all three rungs (A1-3)"
    elif all(e["below_threshold"] for e in evaluated):
        verdict, reason = True, None
    else:
        verdict = False
        reason = "at least one evaluated eligible triple has relative variation >= %s" % SC.DFLAT_THRESHOLD
    allpts = SC.heur_dflat(sorted(measured.items()))
    allpts = dict(allpts, label=ALL_POINTS_LABEL)
    return {"rule": "A1-3", "S": S, "measured_rungs": sorted(measured), "heur_dflat_pass": verdict, "reason": reason,
            "eligible_triples": [list(t) for t in eligible], "triples_evaluated": evaluated, "triples_not_evaluable": not_evaluable,
            "all_points_figure": allpts, "D_per_prime": {str(p): measured[p] for p in sorted(measured)}}


def matched_triple_figure(cell_D, triple=MATCHED_TRIPLE):
    """AA-4: relative variation on the primary set's rungs, for a control (arm, shape). Descriptive only."""
    if not all(cell_D.get(p) for p in triple):
        return {"label": MATCHED_LABEL, "triple": list(triple), "status": "not_applicable",
                "reason": "not all three rungs have a defined cell D", "missing_D_at": [p for p in triple if not cell_D.get(p)]}
    fig = SC.heur_dflat([(p, cell_D[p]) for p in triple])
    return {"label": MATCHED_LABEL, "triple": list(triple), "status": "emitted", "D": {str(p): cell_D[p] for p in triple},
            "D_relative_variation": fig["D_relative_variation"], "D_max_over_min": fig["D_max_over_min"],
            "note": "no pass/fail is attached to this figure; A1-3's verdict rules, sets and threshold are unchanged"}


def evaluate_all(cellD_by_arm_shape, sets=EVAL_SETS):
    """cellD_by_arm_shape: {(arm, shape): {p: D}} over PRIMARY-READ rows (off-shape rows already excluded)."""
    out = {}
    for shape, spec in sets.items():
        blk = {}
        for arm in spec["arms"]:
            blk[arm] = a1_3_verdict(spec["S"], cellD_by_arm_shape.get((arm, shape), {}))
        for arm, why in spec.get("not_applicable_arms", {}).items():
            blk[arm] = {"rule": "A1-3", "heur_dflat_pass": "not_applicable", "reason": why}
        out[shape] = blk
    out[AC.OFF_SHAPE_LABEL] = {"status": "NOT EVALUATED", "reason": "A1-3: the (16777291, ecgfp5_shaped, c = 59) rows form no set and yield no verdict"}
    return out


def matched_triples(cellD_by_arm_shape):
    out = {"random_2torsion": {}, "random_no2torsion": {}}
    for arm in M5_ARMS_2T:
        out["random_2torsion"][arm] = matched_triple_figure(cellD_by_arm_shape.get((arm, "random_2torsion"), {}))
    out["random_no2torsion"]["S5"] = matched_triple_figure(cellD_by_arm_shape.get(("S5", "random_no2torsion"), {}))
    return out
