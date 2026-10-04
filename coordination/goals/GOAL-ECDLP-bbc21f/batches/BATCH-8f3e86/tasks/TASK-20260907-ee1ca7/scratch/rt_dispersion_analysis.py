"""RED-TEAM ANALYSIS (TASK-20260907-ee1ca7, joint J4/J5).  NOT A RUN RECORD.

Pools the frozen seeds {1..5} (from the producer's committed table) with the
red team's fresh seeds {6..20} (scratch/dispersion_s6_s20.json) at
N = 2^24, r = 2, and asks two questions the batch's own five seeds cannot:

 (Q1) CONTROL STRENGTH.  Over 5-seed draws at the known-false object a = 3/16,
      how often does the frozen ">= 4 of 5" rule return PASS -- i.e. how often
      does the proves-too-much control FIRE?  And what is the most
      discriminating (largest m(4)) five-seed known-false object available at
      this cell, which is the strongest form the control could have taken?

 (Q2) DRAW DEPENDENCE OF THE CLAIM.  At a = 1/8, is the reported 5/5 a
      property of the cell or of the frozen draw?

Exhaustive over all C(20,5) = 15504 five-seed subsets; no sampling.
"""
from __future__ import annotations
import itertools, json, os, statistics as st

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, *([".."] * 8)))
VT = os.path.join(_REPO, "experiments/EXP-ECDLP-612fb1/runs/"
                         "RUN-ECDLP-612fb1-v3-analysis-001/g3_verdict_table.json")
A_GRID = (0.0625, 0.125, 0.1875, 0.25)
KNOWN_FALSE_A = (0.1875, 0.25)


def m4(ms):
    return sorted(ms, reverse=True)[3]


def main():
    frozen = {}
    for row in json.load(open(VT))["rows"]:
        if row["n_bits"] == 24 and row["r"] == 2:
            frozen[row["a"]] = {s["seed"]: s["margin"] for s in row["per_seed"]}
    fresh = {}
    for r in json.load(open(os.path.join(_HERE, "dispersion_s6_s20.json")))["rows"]:
        fresh.setdefault(r["a"], {})[r["seed"]] = r["margin"]

    out = {
        "analysis": "red-team seed-dispersion analysis, TASK-20260907-ee1ca7",
        "is_a_run_record": False, "changes_any_verdict": False,
        "cell": "N = 2^24, T = 256, T_sel = 128, r = 2, frozen v2 instrument",
        "frozen_seeds": [1, 2, 3, 4, 5],
        "red_team_fresh_seeds": sorted(fresh[A_GRID[0]]),
        "note": "The batch's verdicts are computed on seeds {1..5} ONLY and are "
                "unchanged by anything here. These are statements about the "
                "SAMPLING BEHAVIOUR of the frozen rule, not re-scorings of it.",
        "per_a": [],
    }
    for a in A_GRID:
        allm = dict(frozen[a]); allm.update(fresh[a])
        seeds = sorted(allm)
        ms = [allm[s] for s in seeds]
        pos = [s for s in seeds if allm[s] >= 0.0]
        subs = list(itertools.combinations(seeds, 5))
        m4s = [m4([allm[s] for s in c]) for c in subs]
        n_pass = sum(1 for v in m4s if v >= 0.0)
        best = max(range(len(subs)), key=lambda i: m4s[i])
        frozen_m4 = m4([frozen[a][s] for s in (1, 2, 3, 4, 5)])
        rec = {
            "a": a,
            "role": ("KNOWN-FALSE control object" if a in KNOWN_FALSE_A
                     else "PRIMARY claim cell"),
            "n_seeds_total": len(seeds),
            "per_seed_margin_min": min(ms), "per_seed_margin_max": max(ms),
            "per_seed_margin_mean": st.fmean(ms),
            "per_seed_margin_stdev": st.stdev(ms),
            "seeds_with_margin_ge_0": pos,
            "fraction_of_seeds_with_margin_ge_0": len(pos) / len(seeds),
            "five_seed_subsets_examined": len(subs),
            "subsets_returning_PASS": n_pass,
            "fraction_of_5seed_draws_returning_PASS": n_pass / len(subs),
            "frozen_draw_m4_verdict_statistic": frozen_m4,
            "frozen_draw_verdict": "PASS" if frozen_m4 >= 0 else "FAIL",
            "best_available_m4_over_all_5seed_draws": m4s[best],
            "best_available_5seed_draw": list(subs[best]),
            "m4_median_over_draws": st.median(m4s),
            "m4_min_over_draws": min(m4s), "m4_max_over_draws": max(m4s),
        }
        if a in KNOWN_FALSE_A:
            rec["strongest_constructible_known_false_object"] = {
                "seeds": list(subs[best]),
                "m4": m4s[best],
                "uniform_bias_that_would_make_it_FIRE": -m4s[best],
                "vs_frozen_object_bias_to_fire": -frozen_m4,
                "improvement_factor": (-frozen_m4) / (-m4s[best]) if m4s[best] < 0 else None,
            }
        out["per_a"].append(rec)

    # does a strengthened known-false object close the a = 1/8 blind band?
    kf_best = min(-r["best_available_m4_over_all_5seed_draws"]
                  for r in out["per_a"] if r["a"] in KNOWN_FALSE_A)
    a18 = [r for r in out["per_a"] if r["a"] == 0.125][0]
    a116 = [r for r in out["per_a"] if r["a"] == 0.0625][0]
    out["blind_band_under_a_strengthened_control"] = {
        "strengthened_control_fires_at_uniform_bias": kf_best,
        "a_1_8_PASS_headroom_frozen_draw": a18["frozen_draw_m4_verdict_statistic"],
        "a_1_8_band_now_empty": kf_best <= a18["frozen_draw_m4_verdict_statistic"],
        "a_1_16_PASS_headroom_frozen_draw": a116["frozen_draw_m4_verdict_statistic"],
        "a_1_16_band_now_empty": kf_best <= a116["frozen_draw_m4_verdict_statistic"],
    }
    p = os.path.join(_HERE, "seed_dispersion_analysis.json")
    json.dump(out, open(p, "w"), indent=1)
    for r in out["per_a"]:
        print("a=%-7s %-26s seeds>=0: %2d/%2d   P(PASS on a 5-seed draw)=%.4f   "
              "frozen m(4)=%+.6f   best m(4)=%+.6f"
              % (r["a"], r["role"], len(r["seeds_with_margin_ge_0"]),
                 r["n_seeds_total"], r["fraction_of_5seed_draws_returning_PASS"],
                 r["frozen_draw_m4_verdict_statistic"],
                 r["best_available_m4_over_all_5seed_draws"]))
    print(json.dumps(out["blind_band_under_a_strengthened_control"], indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
