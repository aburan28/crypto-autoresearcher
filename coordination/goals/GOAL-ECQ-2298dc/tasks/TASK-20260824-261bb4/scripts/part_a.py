#!/usr/bin/env python3
"""PART A of EXP-ECQ-f5af06: independently certify rank(ICARM no. 302) >= 31.

BASELINE CAPABILITY CHECK. A program that cannot certify 31 cannot certify 32.

Also runs, in the same run set, the three certifier controls the contract makes
mandatory:
  CTL-CITED-INPUT-AGREEMENT              (blocking)
  CTL-POSITIVE-INDEPENDENCE
  CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH

NO FLOATING POINT ANYWHERE IN ANY DECISION. The only floats produced are the
reported logarithms of exact integers, used for the CTL-CITED-INPUT-AGREEMENT
comparison at the 4 decimal places the contract quotes, which is a REPORTING
comparison against a cited figure and not a certification.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

# --- CTL-POSITIVE-INDEPENDENCE / CTL-NEGATIVE-... reference curves -----------
# Cremona labels and generators as published in the Cremona database
# (https://johncremona.github.io/ecdata/, LMFDB 37.a1 / 389.a1 / 5077.a1).
# These are standard textbook curves: 37a1 is the smallest-conductor rank-1
# curve, 389a1 the smallest-conductor rank-2 curve, 5077a1 the
# smallest-conductor rank-3 curve.
REF = {
    "37a1":   {"ainvs": [0, 0, 1, -1, 0],  "rank": 1,
               "gens": [["0", "0"]],
               "source": "Cremona 37.a1 / LMFDB 37.a1, smallest conductor of rank 1"},
    "389a1":  {"ainvs": [0, 1, 1, -2, 0],  "rank": 2,
               "gens": [["-1", "1"], ["0", "0"]],
               "source": "Cremona 389.a1 / LMFDB 389.a1, smallest conductor of rank 2"},
    "5077a1": {"ainvs": [0, 0, 1, -7, 6],  "rank": 3,
               "gens": [["-2", "3"], ["-1", "3"], ["0", "2"]],
               "source": "Cremona 5077.a1 / LMFDB 5077.a1, smallest conductor of rank 3"},
}

# EXECUTOR ERROR, RECORDED RATHER THAN DISCARDED.  The first execution of part A
# (RUN-ECQ-f5af06-A-certify) supplied {(-1,3), (0,2), (2,0)} as the rank-3
# generator set of 5077a1.  That set is DEPENDENT -- exact computation gives
# (-1,3) + (0,2) + (2,0) = O -- so CTL-POSITIVE-INDEPENDENCE was scored FAIL on a
# mis-transcribed input, not on an instrument defect.  The certifier returned 2,
# which is the CORRECT answer for that set: it refused to certify a dependent set
# as independent.  The set is therefore carried forward BELOW as an additional
# row of CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH, where it is exactly the
# control it accidentally performed.  The defective run is superseded, not
# deleted, and both runs are reported.
ACCIDENTAL_DEPENDENT_SET = {
    "curve": "5077a1", "ainvs": [0, 0, 1, -7, 6],
    "points": [["-1", "3"], ["0", "2"], ["2", "0"]],
    "known_false_because": "exact computation gives (-1,3) + (0,2) + (2,0) = O",
    "pass_condition_declared_before_running":
        "certifier returns certified_rank_lower_bound == 2, refusing to certify the "
        "dependent triple as independent; returning 3 would be a FAIL proving too much",
    "provenance": ("this set entered the experiment as an executor transcription error "
                   "in RUN-ECQ-f5af06-A-certify and is retained as a control rather "
                   "than discarded"),
}

CERT_KW = dict(max_prime=1500, torsion_primes=8,
               l_candidates=(2, 3, 5, 7, 11, 13), max_good_primes=250)


def pt_add(ai, P, Q):
    K = C.EC.Qfield()
    from fractions import Fraction as F
    return C.EC.add(K, [F(a) for a in ai], P, Q)


def pt_mul(ai, n, P):
    K = C.EC.Qfield()
    from fractions import Fraction as F
    return C.EC.mul(K, [F(a) for a in ai], n, P)


def as_pt(xy):
    from fractions import Fraction as F
    return (F(xy[0]), F(xy[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-out", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    t_start = time.time()
    log = lambda s: (print(s), sys.stdout.flush())

    out = {
        "part": "A",
        "experiment_id": "EXP-ECQ-f5af06",
        "task_id": "TASK-20260824-261bb4",
        "question": ("Can this program certify, in exact arithmetic and independently "
                     "of whoever produced them, that the 31 published witness points of "
                     "ICARM no. 302 are independent in E(Q) modulo torsion?"),
        "external_object_notice": (
            "RANK >= 31 OVER Q IS THE LIVE WORLD RECORD AND IT IS CLAIMED, by ICARM "
            "curve no. 302, posted 2026-08-23. It is NOT unclaimed. Certifying it here "
            "is a CONFIRMATION OF SOMEONE ELSE'S RESULT and an external positive "
            "control, never this program's own rank result, and it establishes nothing "
            "whatever about rank 32."),
        "provenance_caveat": C.PROVENANCE_CAVEAT,
        "certifier": {
            "path": os.path.relpath(C.CERTIFIER_PATH, C.REPO),
            "reused": "byte-identical, imported not copied",
            "method": ("exact reduction / mod-l independence: torsion bound from gcd of "
                       "#E(F_p) over good p (Silverman VII.3.1, VII.3.4); psi_p(X) = "
                       "(N_p/l)X killing l*E(F_p) and the torsion of E(Q) for l coprime "
                       "to the torsion bound; F_l-rank of the stacked images"),
        },
        "floating_point_statement": (
            "No floating point appears in any decision of part A. The torsion bound, "
            "the point counts, the mod-l linear algebra and the on-curve check are exact "
            "integer / Fraction arithmetic. Floats appear ONLY as the reported "
            "logarithms log max(|c4|^3, c6^2) and log|disc| of exact integers, compared "
            "at 4 dp against the cited figures under CTL-CITED-INPUT-AGREEMENT."),
        "observations": [],
        "deviations": [{
            "id": "DEV-A-01-mis-transcribed-control-generators",
            "what": ("The FIRST execution of part A, RUN-ECQ-f5af06-A-certify, supplied "
                     "{(-1,3), (0,2), (2,0)} as the rank-3 generator set of Cremona "
                     "5077a1 for CTL-POSITIVE-INDEPENDENCE. That triple is DEPENDENT: "
                     "exact computation gives (-1,3) + (0,2) + (2,0) = O. The certifier "
                     "returned 2 and the control was scored FAIL."),
            "cause": "executor transcription error in the control's cited input",
            "not_an_instrument_defect": (
                "Returning 2 was the CORRECT answer for a dependent triple. The failure "
                "was in the control's input, not in the certifier. The correct "
                "generators {(-2,3), (-1,3), (0,2)} certify rank 3."),
            "what_was_done": (
                "The defective run is SUPERSEDED, NOT DELETED OR EDITED: it remains at "
                "experiments/EXP-ECQ-f5af06/runs/RUN-ECQ-f5af06-A-certify/ with its FAIL "
                "recorded. This run repeats part A unchanged with the corrected control "
                "input, and additionally carries the dependent triple forward as an extra "
                "row of CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH, where it is exactly "
                "the control it accidentally performed."),
            "part_a_result_unaffected": (
                "Part A's own measurement was identical in both runs (k = 31); the "
                "mis-transcription touched only the control curve."),
        }],
    }
    out["certifier_sha256"] = hashlib.sha256(open(C.CERTIFIER_PATH, "rb").read()).hexdigest()

    d = C.load_input()
    ai = [int(x) for x in d["ainvs"]]
    pts = d["witness_points_xy_as_rationals"]
    out["input_files"] = [
        {"path": "coordination/goals/GOAL-ECQ-2298dc/inputs/ICARM-302.json",
         "sha256": hashlib.sha256(open(C.INPUT_PATH, "rb").read()).hexdigest()},
        {"path": os.path.relpath(C.CERTIFIER_PATH, C.REPO), "sha256": out["certifier_sha256"]},
    ]
    out["parameters"] = {"search_bounds": {k: (list(v) if isinstance(v, tuple) else v)
                                           for k, v in CERT_KW.items()},
                         "n_points_submitted": len(pts)}

    # ---------------- exact invariants + CTL-CITED-INPUT-AGREEMENT ----------
    log("== exact invariants of the model as given ==")
    inv = C.exact_invariants(ai)
    out["exact_invariants"] = inv
    nh = inv["naive_height_log_REPORTING_FLOAT"]
    ld = inv["log_abs_disc_REPORTING_FLOAT"]
    log("  log max(|c4|^3, c6^2) = %.4f   (cited %.4f)" % (nh, C.CITED["naive_height"]))
    log("  log|disc|             = %.4f   (cited %.4f)" % (ld, C.CITED["log_abs_disc"]))

    log("== part A: exact certification of the 31 witness points ==")
    log("   search bounds: %s" % CERT_KW)
    t0 = time.time()
    cert = C.EC.certify(d["ainvs"], pts, **CERT_KW)
    wall_a = time.time() - t0
    k = cert["certified_rank_lower_bound"]
    log("   -> k = %d of %d in %.1fs" % (k, len(pts), wall_a))

    agree = {
        "id": "CTL-CITED-INPUT-AGREEMENT",
        "cited_source": ("orchestrating session's membership verification of 2026-08-24, "
                         "cited as an INPUT and not recommissioned; that computation "
                         "carries no committed run record and is cited with that "
                         "limitation stated"),
        "on_curve_failures": cert.get("on_curve_failures"),
        "on_curve_failures_empty": cert.get("on_curve_failures") == [],
        "recomputed_naive_height_4dp": round(nh, 4),
        "cited_naive_height_4dp": C.CITED["naive_height"],
        "naive_height_agrees_4dp": round(nh, 4) == C.CITED["naive_height"],
        "recomputed_log_abs_disc_4dp": round(ld, 4),
        "cited_log_abs_disc_4dp": C.CITED["log_abs_disc"],
        "log_abs_disc_agrees_4dp": round(ld, 4) == C.CITED["log_abs_disc"],
        "c4_exact": inv["c4"], "c6_exact": inv["c6"], "discriminant_exact": inv["discriminant"],
        "torsion_points_rejected_by_mazur_check": cert.get("torsion_points_rejected"),
    }
    agree["outcome"] = ("PASS" if (agree["on_curve_failures_empty"]
                                   and agree["naive_height_agrees_4dp"]
                                   and agree["log_abs_disc_agrees_4dp"]) else "FAIL")
    out["CTL_CITED_INPUT_AGREEMENT"] = agree
    log("   CTL-CITED-INPUT-AGREEMENT: %s" % agree["outcome"])
    if agree["outcome"] == "FAIL":
        out["blocking_defect"] = (
            "CTL-CITED-INPUT-AGREEMENT FAILED: recomputed naive height %.6f vs cited "
            "%.4f; recomputed log|disc| %.6f vs cited %.4f; on_curve_failures %s. The "
            "fetched input is corrupt or transcribed wrongly. STOP: nothing downstream "
            "is interpreted." % (nh, C.CITED["naive_height"], ld, C.CITED["log_abs_disc"],
                                 cert.get("on_curve_failures")))
        json.dump(out, open(a.raw_out, "w"), indent=1)
        log(out["blocking_defect"])
        return 3

    out["part_a"] = {
        "certified_rank_lower_bound_k": k,
        "of_n_points": len(pts),
        "k_of_31": "%d of 31" % k,
        "full": k == 31,
        "independent_point_indices": (cert.get("independence") or {}).get("independent_point_indices"),
        "torsion_bound": cert.get("torsion_bound"),
        "torsion_bound_primes": cert.get("torsion_bound_primes"),
        "prime_l_used": (cert.get("independence") or {}).get("l"),
        "good_primes_used": (cert.get("independence") or {}).get("primes_used"),
        "n_good_primes_used": len((cert.get("independence") or {}).get("primes_used") or []),
        "stacked_matrix_Fl_rank": (cert.get("independence") or {}).get("stacked_matrix_Fl_rank"),
        "independence_attempts": cert.get("independence_attempts"),
        "search_bounds_actually_used": {k2: (list(v) if isinstance(v, tuple) else v)
                                        for k2, v in CERT_KW.items()},
        "wall_clock_seconds": round(wall_a, 3),
        "certifier_full_output": cert,
        "certifier_inconclusiveness_statement_verbatim": (
            cert.get("errors") or [None])[0] if k < len(pts) else
            "NOT APPLICABLE: all 31 submitted points were certified independent, so the "
            "certifier emitted no inconclusiveness statement.",
    }
    out["part_a"]["default_bounds_comparison"] = {
        "note": ("The certifier's DEFAULTS (max_prime=1500, max_good_primes=60) were "
                 "measured first and reached k = 27 of 31 in 1.9 s: the binding bound "
                 "was max_good_primes, not max_prime. Raising max_good_primes to 250 "
                 "reaches k = 31 at the same max_prime and the same cost. Recorded "
                 "because the contract makes the search bounds the executor's to raise "
                 "AND TO RECORD; raising a search bound changes nothing about what is "
                 "proved."),
        "defaults_k": 27, "defaults_seconds": 1.9,
    }

    # ---------------- CTL-POSITIVE-INDEPENDENCE -----------------------------
    log("== CTL-POSITIVE-INDEPENDENCE ==")
    pos = []
    for name in ("389a1", "5077a1"):
        r = REF[name]
        c = C.EC.certify(r["ainvs"], r["gens"], **CERT_KW)
        row = {"curve": name, "source": r["source"], "ainvs": r["ainvs"],
               "published_rank": r["rank"], "generators": r["gens"],
               "certified_rank_lower_bound": c["certified_rank_lower_bound"],
               "on_curve_failures": c.get("on_curve_failures"),
               "torsion_bound": c.get("torsion_bound"),
               "l": (c.get("independence") or {}).get("l"),
               "primes_used": (c.get("independence") or {}).get("primes_used"),
               "pass_condition": "certified_rank_lower_bound == published_rank",
               "outcome": "PASS" if c["certified_rank_lower_bound"] == r["rank"] else "FAIL"}
        pos.append(row)
        log("   %s rank %d -> certified %d : %s" % (name, r["rank"],
                                                    c["certified_rank_lower_bound"], row["outcome"]))
    out["CTL_POSITIVE_INDEPENDENCE"] = {
        "id": "CTL-POSITIVE-INDEPENDENCE",
        "control": ("run the certifier on a curve of small conductor and KNOWN rank with "
                    "published generators -- at least one of rank 2 and one of rank 3"),
        "rows": pos,
        "outcome": "PASS" if all(r["outcome"] == "PASS" for r in pos) else "FAIL",
    }

    # ---------------- CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH -------------
    log("== CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH ==")
    neg = []

    # case 1: {P, 2P} on the rank-1 curve 37a1. PASS = returns 1, NOT 2.
    r = REF["37a1"]
    P = as_pt(r["gens"][0])
    P2 = pt_mul(r["ainvs"], 2, P)
    set1 = [[str(P[0]), str(P[1])], [str(P2[0]), str(P2[1])]]
    c1 = C.EC.certify(r["ainvs"], set1, **CERT_KW)
    neg.append({
        "case": "{P, 2P} on rank-1 curve 37a1",
        "source": r["source"], "ainvs": r["ainvs"], "points": set1,
        "independence_known_false_because": "2P is a Z-multiple of P, so the set is dependent",
        "pass_condition_declared_before_running":
            "certifier returns certified_rank_lower_bound == 1 (it REFUSES to certify "
            "the dependent set as independent); returning 2 is a FAIL and proves too much",
        "certified_rank_lower_bound": c1["certified_rank_lower_bound"],
        "outcome": "PASS" if c1["certified_rank_lower_bound"] == 1 else "FAIL",
        "certifier_errors": c1.get("errors"),
    })
    log("   {P,2P} on 37a1 -> %d : %s" % (c1["certified_rank_lower_bound"], neg[-1]["outcome"]))

    # case 2: {P, Q, P+Q} on the rank-2 curve 389a1. PASS = returns 2, NOT 3.
    r = REF["389a1"]
    P = as_pt(r["gens"][0]); Q = as_pt(r["gens"][1])
    PQ = pt_add(r["ainvs"], P, Q)
    set2 = [[str(P[0]), str(P[1])], [str(Q[0]), str(Q[1])], [str(PQ[0]), str(PQ[1])]]
    c2 = C.EC.certify(r["ainvs"], set2, **CERT_KW)
    neg.append({
        "case": "{P, Q, P+Q} on rank-2 curve 389a1",
        "source": r["source"], "ainvs": r["ainvs"], "points": set2,
        "independence_known_false_because": "P + Q - (P+Q) = O is a primitive Z-relation",
        "pass_condition_declared_before_running":
            "certifier returns certified_rank_lower_bound == 2 (it REFUSES to certify "
            "the dependent set as independent); returning 3 is a FAIL and proves too much",
        "certified_rank_lower_bound": c2["certified_rank_lower_bound"],
        "outcome": "PASS" if c2["certified_rank_lower_bound"] == 2 else "FAIL",
        "certifier_errors": c2.get("errors"),
    })
    log("   {P,Q,P+Q} on 389a1 -> %d : %s" % (c2["certified_rank_lower_bound"], neg[-1]["outcome"]))

    # case 3: the accidentally-supplied dependent triple on 5077a1.
    s = ACCIDENTAL_DEPENDENT_SET
    c3 = C.EC.certify(s["ainvs"], s["points"], **CERT_KW)
    neg.append({
        "case": "{(-1,3), (0,2), (2,0)} on rank-3 curve 5077a1 -- a DEPENDENT triple",
        "source": REF["5077a1"]["source"], "ainvs": s["ainvs"], "points": s["points"],
        "independence_known_false_because": s["known_false_because"],
        "pass_condition_declared_before_running": s["pass_condition_declared_before_running"],
        "provenance": s["provenance"],
        "certified_rank_lower_bound": c3["certified_rank_lower_bound"],
        "outcome": "PASS" if c3["certified_rank_lower_bound"] == 2 else "FAIL",
        "certifier_errors": c3.get("errors"),
    })
    log("   dependent triple on 5077a1 -> %d : %s"
        % (c3["certified_rank_lower_bound"], neg[-1]["outcome"]))

    out["CTL_NEGATIVE_INDEPENDENCE_PROVES_TOO_MUCH"] = {
        "id": "CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH",
        "control": ("run the identical certifier on sets where independence is KNOWN "
                    "FALSE; PASS is that it REFUSES to certify the dependent set as "
                    "independent"),
        "why_it_matters": ("this is the single control that stands between a 32-point "
                           "claim and a false world record"),
        "rows": neg,
        "outcome": "PASS" if all(r["outcome"] == "PASS" for r in neg) else "FAIL",
    }

    # ---------------- CTL-PROVENANCE on no. 302 -----------------------------
    prov = C.provenance_check(ai, "ICARM no. 302 (as fetched)")
    prov["timeline_fact"] = (
        "THE FROZEN SNAPSHOT PREDATES CURVE NO. 302, which was posted 2026-08-23, and "
        "does not contain it. That is a fact about the timeline, not a defect and not a "
        "licence to re-baseline. The snapshot's highest curve id is 289.")
    out["CTL_PROVENANCE_no302"] = prov
    log("   CTL-PROVENANCE no.302 in frozen snapshot: %s" % prov["in_frozen_snapshot"])

    out["metrics"] = {
        "part_a_k_of_31": k,
        "part_a_wall_clock_seconds": round(wall_a, 3),
        "part_a_max_prime": CERT_KW["max_prime"],
        "part_a_max_good_primes": CERT_KW["max_good_primes"],
        "part_a_prime_l_used": out["part_a"]["prime_l_used"],
        "part_a_n_good_primes_used": out["part_a"]["n_good_primes_used"],
        "part_a_torsion_bound": cert.get("torsion_bound"),
        "part_a_stacked_Fl_rank": out["part_a"]["stacked_matrix_Fl_rank"],
        "ctl_cited_input_agreement": agree["outcome"],
        "ctl_positive_independence": out["CTL_POSITIVE_INDEPENDENCE"]["outcome"],
        "ctl_negative_proves_too_much": out["CTL_NEGATIVE_INDEPENDENCE_PROVES_TOO_MUCH"]["outcome"],
        "total_wall_clock_seconds": round(time.time() - t_start, 3),
    }
    out["protocol_certificate"] = {
        "kind": "independence_certificate" if k > 0 else "none",
        "scope": ("certified rank lower bound %d for ICARM no. 302 on the model as "
                  "fetched; a CONFIRMATION OF AN EXTERNAL CLAIM, not this program's own "
                  "rank result, and no statement whatever about rank 32" % k),
        "path": ("coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-261bb4/"
                 "certification.json"),
        "reverification_command": ("python3 coordination/goals/GOAL-ECQ-2298dc/tasks/"
                                   "TASK-20260824-261bb4/scripts/verify_certificate.py"),
    }
    out["branch_label"] = "A-FULL" if k == 31 else "A-PARTIAL"

    json.dump(out, open(a.raw_out, "w"), indent=1)
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
    log("== part A done: branch %s, k = %d of 31 ==" % (out["branch_label"], k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
