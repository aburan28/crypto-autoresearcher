"""RED-TEAM ANALYSIS (TASK-20260907-ee1ca7, joint J4).  NOT A RUN RECORD.

THE VERDICT STATISTIC.  Under the frozen rule "G3 PASSES iff at least 4 of the
5 seeds have margin_s >= 0", the ONLY function of the five margins that the
verdict reads is the 4th-LARGEST margin, m(4).  Verdict = PASS iff m(4) >= 0.
Every other margin -- including the single margin closest to zero, which the
producer reports as `closest_seed_margin_to_zero` -- is invisible to the rule.

CONTROL POWER UNDER A UNIFORM ADDITIVE BIAS.  Model one concrete way the
argument could be wrong: a systematic upward bias b applied identically to
every measured margin (e.g. a coverage/denominator convention that inflates
TopShare, or deflates StaticCov, by the same amount at every cell).  Then:

  * a known-false object FIRES the proves-too-much control iff b >= -m(4)
    at that object;
  * a primary cell's PASS is FAKE (it would be FAIL at b = 0) iff
    b > m(4) at that cell.

So each primary cell has a BLIND BAND of biases that would manufacture its
PASS without firing any known-false object:  ( m(4)_primary ,
min over known-false objects of -m(4)_kf ).  An empty band means the control
protects the cell; a wide one means it does not.

This computes those numbers from the producer's own committed table.
"""
from __future__ import annotations
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, *([".."] * 8)))
TBL = os.path.join(_REPO, "experiments/EXP-ECDLP-612fb1/runs/"
                          "RUN-ECDLP-612fb1-v3-analysis-001/g3_verdict_table.json")

KNOWN_FALSE = [(24, 0.1875, 2), (24, 0.25, 2)] + \
              [(n, a, 8) for n in (20, 24) for a in (0.0625, 0.125, 0.1875, 0.25)]
PRIMARY = [(24, 0.0625, 2), (24, 0.125, 2)]


def load():
    rows = json.load(open(TBL))["rows"]
    out = {}
    for row in rows:
        n = int(row["N"]).bit_length() - 1
        ms = sorted((s["margin"] for s in row["per_seed"]), reverse=True)
        out[(n, row["a"], row["r"])] = {
            "margins_desc": ms,
            "m4_verdict_statistic": ms[3],
            "closest_to_zero": min(ms, key=abs),
            "pass_count": row["pass_count"],
            "verdict": row["verdict"],
        }
    return out


def main():
    cells = load()
    kf = {k: cells[k] for k in KNOWN_FALSE if k in cells}
    # firing threshold of each known-false object under a uniform upward bias
    for k, v in kf.items():
        v["uniform_bias_to_fire"] = -v["m4_verdict_statistic"]
    binding_obj = min(kf, key=lambda k: kf[k]["uniform_bias_to_fire"])
    binding = kf[binding_obj]["uniform_bias_to_fire"]

    report = {
        "analysis": "red-team control-power analysis, TASK-20260907-ee1ca7 joint J4",
        "is_a_run_record": False,
        "source": "experiments/EXP-ECDLP-612fb1/runs/RUN-ECDLP-612fb1-v3-analysis-001/"
                  "g3_verdict_table.json (committed; provenance internal)",
        "verdict_statistic_definition":
            "m(4), the 4th-largest of the five per-seed margins. The frozen "
            ">= 4-of-5 rule reads this and nothing else: verdict = PASS iff m(4) >= 0.",
        "bias_model":
            "a uniform additive bias b added to every measured margin. One model of "
            "how the argument could be wrong, not the only one; a bias that is "
            "cell-dependent is not covered and would need a different control.",
        "known_false_objects": [],
        "binding_known_false_object": None,
        "primary_cells": [],
    }
    for k in sorted(kf, key=lambda k: kf[k]["uniform_bias_to_fire"]):
        n, a, r = k
        v = kf[k]
        report["known_false_objects"].append({
            "object": f"N=2^{n}, a={a}, r={r}", "verdict": v["verdict"],
            "pass_count_of_5": v["pass_count"],
            "margins_desc": v["margins_desc"],
            "closest_single_seed_margin_to_zero": v["closest_to_zero"],
            "m4_verdict_statistic": v["m4_verdict_statistic"],
            "uniform_bias_that_would_make_this_object_FIRE": v["uniform_bias_to_fire"],
        })
    n, a, r = binding_obj
    report["binding_known_false_object"] = {
        "object": f"N=2^{n}, a={a}, r={r}",
        "uniform_bias_that_would_make_the_whole_Section_6_set_fire": binding,
        "note": "The Section 6 set as a whole detects a uniform upward bias only "
                "once b reaches this value; every other object is weaker.",
    }
    for k in PRIMARY:
        v = cells[k]
        n, a, r = k
        head = v["m4_verdict_statistic"]
        band = (head, binding)
        report["primary_cells"].append({
            "cell": f"N=2^{n}, a={a}, r={r}", "verdict": v["verdict"],
            "pass_count_of_5": v["pass_count"],
            "margins_desc": v["margins_desc"],
            "m4_verdict_statistic_is_the_PASS_headroom": head,
            "smallest_uniform_bias_that_would_MANUFACTURE_this_PASS": head,
            "blind_band_low": band[0], "blind_band_high": band[1],
            "blind_band_is_empty": band[1] <= band[0],
            "blind_band_width": max(0.0, band[1] - band[0]),
            "blind_band_width_over_PASS_headroom":
                (max(0.0, band[1] - band[0]) / head) if head > 0 else None,
            "reading": ("PROTECTED by the Section 6 set under this bias model"
                        if band[1] <= band[0] else
                        "NOT PROTECTED: a uniform upward bias in the open interval "
                        "(low, high) manufactures this PASS while every Section 6 "
                        "known-false object still returns FAIL"),
        })
    out = os.path.join(_HERE, "control_power.json")
    json.dump(report, open(out, "w"), indent=1)
    print(json.dumps(report["binding_known_false_object"], indent=1))
    for p in report["primary_cells"]:
        print(p["cell"], "headroom m(4)=%.9f" % p["m4_verdict_statistic_is_the_PASS_headroom"],
              "band=(%.9f, %.9f)" % (p["blind_band_low"], p["blind_band_high"]),
              "width=%.9f" % p["blind_band_width"], "|", p["reading"][:40])
    print("wrote", out)


if __name__ == "__main__":
    main()
