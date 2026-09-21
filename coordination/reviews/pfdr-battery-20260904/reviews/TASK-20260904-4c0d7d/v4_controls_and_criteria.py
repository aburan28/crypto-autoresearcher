#!/usr/bin/env python3
"""V4: control presence table, instance multiplicity, and the literal
accounting of the frozen success criterion (1)-(5).  Reads raw records and
manifests only; writes JSON to stdout.
"""
import collections
import json
import os
import sys

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-fd901a/runs")
SWEEPS = {"p4099": "RUN-PFDR-fd901a-sweep-p4099",
          "p64": "RUN-PFDR-fd901a-sweep-p64",
          "p256": "RUN-PFDR-fd901a-sweep-p256"}


def load(run):
    with open(os.path.join(RUNS, run, "raw-result.json")) as fh:
        return json.load(fh)


def cp_upper_zero(n, alpha=0.05):
    return 1.0 - (alpha / 2.0) ** (1.0 / n)


def triples(draws):
    out = set()
    for x in draws:
        st = x["certificate"]["statement"]
        ab = ((st["curve"]["a"], st["curve"]["b"])
              if x["certificate"]["kind"] == "decomposition"
              else (st["cubic"]["a"], st["cubic"]["b"]))
        out.add((ab[0], ab[1], x["x_R"]))
    return out


def main():
    out = {}
    data = {k: load(v) for k, v in SWEEPS.items()}

    # ---- control table ---------------------------------------------------
    ctrl = {}
    ctrl["CTRL-FROZEN-FIXTURE"] = {
        "contract": ("exact integer agreement of the rank profile at every "
                     "D <= 6 with EXP-PFDR-5726af's engine on the SAME "
                     "instance, or with an independent second implementation "
                     "in the same run if 5726af has not run"),
        "blocking": True,
        "realised_by": "RUN-PFDR-fd901a-fixture-p4099, 1 instance, 1 draw",
        "route_used": "fallback (independent second implementation in-run)",
        "validator_finding": ("fallback legitimately available: the fd901a "
                              "fixture ran 2026-09-03T20:29:17Z; the earliest "
                              "EXP-PFDR-5726af run started 20:34:34Z and its "
                              "package was first committed at 21:08:06Z"),
    }
    fx = load("RUN-PFDR-fd901a-fixture-p4099")["raw"]
    ctrl["CTRL-FROZEN-FIXTURE"]["fd901a_instance"] = {
        "p": fx["curve"]["p"], "A": fx["curve"]["a"], "B": fx["curve"]["b"],
        "x_R": fx["target"]["x_R"], "curve_seed": fx["curve"]["seed"],
        "target_seed": fx["target"]["target_seed"]}
    f2 = json.load(open(os.path.join(
        ROOT, "experiments/EXP-PFDR-5726af/runs/RUN-PFDR-5726af-m2-s3/"
        "raw-result.json")))["raw"]["draws"][0]
    ctrl["CTRL-FROZEN-FIXTURE"]["5726af_frozen_fixture_instance"] = {
        "p": f2["p"], "A": f2["curve"]["a"], "B": f2["curve"]["b"],
        "x_R": f2["target"]["x_R"], "curve_seed": f2["curve_seed"],
        "target_seed": f2["target"]["target_seed"],
        "is_frozen_fixture_flag": f2["is_frozen_fixture"]}
    ctrl["CTRL-FROZEN-FIXTURE"]["instances_identical"] = (
        ctrl["CTRL-FROZEN-FIXTURE"]["fd901a_instance"]["A"]
        == ctrl["CTRL-FROZEN-FIXTURE"]["5726af_frozen_fixture_instance"]["A"]
        and ctrl["CTRL-FROZEN-FIXTURE"]["fd901a_instance"]["x_R"]
        == ctrl["CTRL-FROZEN-FIXTURE"]["5726af_frozen_fixture_instance"]["x_R"])

    pc = {}
    for lbl, run in [("p4099", "RUN-PFDR-fd901a-posctrl-p4099"),
                     ("p16411", "RUN-PFDR-fd901a-posctrl-p16411")]:
        d = load(run)
        draws = d["raw"]["draws"]
        pc[lbl] = {"draws": len(draws),
                   "curves": len({x["curve_seed"] for x in draws}),
                   "targets_per_curve": len({x["target_seed"] for x in draws}),
                   "B": sorted({x["B"] for x in draws}),
                   "d_ff": sorted({x["d_ff"] for x in draws}),
                   "d_top_full": sorted({x["d_top_full"] for x in draws}),
                   "series_d_reg": sorted({x["series_d_reg"] for x in draws})}
    ctrl["CTRL-POSITIVE-P-DEPENDENCE"] = {
        "contract": "3 curves x 2 planted targets at p in {4099, 16411}",
        "blocking": True, "realised": pc}

    for name, arms, expect in [
            ("NULL-SUPPORT", ["null_support", "null_support_named_p256"],
             "5 null seeds per (curve, target, p)"),
            ("NEARBY-NON-CURVE-CUBIC", ["noncurve_cubic"],
             "8 curves x 5 targets per sweep prime"),
            ("CTRL-SECONDARY-DIRECT-FIXED-B", ["secondary_direct_B8"],
             "3 curves x 2 targets, B = 8, at the three primes"),
            ("CTRL-NAMED-CURVE", ["semaev_named_p256", "null_support_named_p256"],
             "NIST P-256 at the 256-bit prime")]:
        rec = {"contract": expect, "realised": {}}
        for pk, d in data.items():
            c = collections.Counter(x["arm"] for x in d["raw"]["draws"])
            rec["realised"][pk] = {a: c.get(a, 0) for a in arms}
        ctrl[name] = rec
    ctrl["CTRL-CONFOUNDERS-NAMED"] = {
        "contract": "named and excluded by construction",
        "validator_finding": ("no Groebner-basis call, quotient dimension or "
                              "solution count appears in any metric read by "
                              "this validator; every invariant compared here "
                              "is a graded rank of a generator-level Macaulay "
                              "layer (checked by recomputing 245 of them)"),
    }
    out["controls"] = ctrl

    # ---- instance multiplicity ------------------------------------------
    mult = {}
    for pk, d in data.items():
        for arm in ["semaev", "semaev_named_p256", "noncurve_cubic"]:
            draws = [x for x in d["raw"]["draws"] if x["arm"] == arm]
            if not draws:
                continue
            t = triples(draws)
            ab = {(a, b) for a, b, _ in t}
            mult[f"{pk}:{arm}"] = {
                "draws": len(draws),
                "distinct_A_B_xR": len(t),
                "distinct_A_B": len(ab),
                "cp95_upper_for_0_of_draws": cp_upper_zero(len(draws)),
                "cp95_upper_for_0_of_distinct_triples": cp_upper_zero(len(t)),
                "cp95_upper_for_0_of_distinct_curves": cp_upper_zero(len(ab)),
            }
    out["instance_multiplicity"] = mult

    # ---- do the paired primes share objects? ----------------------------
    shared = {}
    for arm in ["semaev", "noncurve_cubic"]:
        t64 = triples([x for x in data["p64"]["raw"]["draws"] if x["arm"] == arm])
        t256 = triples([x for x in data["p256"]["raw"]["draws"] if x["arm"] == arm])
        shared[arm] = {"triples_64": len(t64), "triples_256": len(t256),
                       "shared_A_B_xR": len(t64 & t256)}
    nl = {}
    for pk in ("p64", "p256"):
        nl[pk] = {x["rng_seed_mixed"] for x in data[pk]["raw"]["draws"]
                  if x["arm"] == "null_support"}
    shared["null_support_rng_seed_overlap_64_vs_256"] = len(nl["p64"] & nl["p256"])
    out["cross_prime_object_sharing"] = shared

    # ---- criterion accounting -------------------------------------------
    crit = {}
    crit["1_frozen_fixture"] = {
        "frozen_text": "the frozen fixture agrees exactly",
        "measured": ("meter = sympy DomainMatrix = naive elimination at "
                     "D = 3..6 in the fixture run; independently reproduced "
                     "by the validator's own elimination"),
        "literal_reading": "met (via the contract's fallback route)",
        "qualification": ("the primary route -- agreement with EXP-PFDR-5726af "
                          "on the SAME instance -- was never executed and "
                          "cannot be executed from these artifacts, because "
                          "the two contracts' seed->(A,B,x_R) derivations "
                          "produce different instances at the same seed labels"),
    }
    crit["2_positive_control"] = {
        "frozen_text": "the positive control shows d_ff = 65 and 129 (strictly increasing)",
        "measured_first_fall_d_ff": {"p4099_B64": pc["p4099"]["d_ff"],
                                     "p16411_B128": pc["p16411"]["d_ff"]},
        "measured_top_block_full_rank_degree": {
            "p4099_B64": pc["p4099"]["d_top_full"],
            "p16411_B128": pc["p16411"]["d_top_full"]},
        "measured_series_d_reg": {"p4099_B64": pc["p4099"]["series_d_reg"],
                                  "p16411_B128": pc["p16411"]["series_d_reg"]},
        "literal_reading": ("NOT met: under the contract's own d_ff definition "
                            "(first D with per-layer fall_dim > 0, the same "
                            "definition used for every other arm) the measured "
                            "integers are 66 and 130, not 65 and 129"),
        "disposition_reading": ("the control's forced disposition is met: "
                               "strictly increasing (66 -> 130), no early fall "
                               "(fall_dim = 0 at every D below the first fall), "
                               "instrument not blind to p; the O1 bar "
                               "('flatness here means the instrument is blind "
                               "to p') therefore does not apply"),
        "alternative_reading": ("the frozen integers 65 / 129 are exactly the "
                                "top-block-full-rank degree and the "
                                "semi-regular series d_reg = B + 1, both "
                                "recorded per draw in the raw records"),
    }
    crit["3_flatness"] = {
        "frozen_text": ("every Semaev-arm invariant is identical at the 64-bit "
                        "and 256-bit primes in at least 38 of 40 draws per cell"),
        "measured": "40 of 40 label-paired draws identical on all 29 invariants",
        "literal_reading": "met",
        "qualification": ("the pairing is by seed label, not by object: the "
                          "curve draw mixes p into the hash, so no (A, B, x_R) "
                          "triple is shared between the two primes (0 shared). "
                          "Each arm also has exactly one profile at every prime "
                          "(zero spread), so any bijection between the two "
                          "40-draw sets gives 40 of 40"),
    }
    sem4099 = [x for x in data["p4099"]["raw"]["draws"] if x["arm"] == "semaev"]
    crit["4_rank_drop_rate"] = {
        "frozen_text": ("the rank-drop rate at 4099 is reported with its "
                        "interval and is below 0.1 per draw"),
        "measured_rate": 0.0,
        "measured_events": 0,
        "n_draws": len(sem4099),
        "cp95_upper_n40": cp_upper_zero(40),
        "n_distinct_triples": len(triples(sem4099)),
        "cp95_upper_on_distinct_triples": cp_upper_zero(len(triples(sem4099))),
        "literal_reading": "met (the rate, 0.0, is below 0.1)",
        "qualification": ("the reported interval [0, 0.0881] assumes 40 "
                          "independent draws; the rank profile is a "
                          "deterministic function of (A, B, x_R) and only "
                          f"{len(triples(sem4099))} distinct triples occur, "
                          "so the exact Clopper-Pearson upper bound on the "
                          "distinct instances is "
                          f"{cp_upper_zero(len(triples(sem4099))):.4f}, which "
                          "is ABOVE the criterion's 0.1 threshold"),
    }
    crit["5_semaev_minus_null"] = {
        "frozen_text": ("the Semaev-minus-null table at the large primes is "
                        "reported and is the same at both"),
        "measured": ("nonzero entries only top_rank@5 = -4, fall_dim@5 = +4, "
                     "d_ff = -1; identical at 4099, 2^64-59 and the P-256 prime"),
        "literal_reading": "met",
    }
    out["criterion_accounting"] = crit

    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
