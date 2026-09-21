#!/usr/bin/env python3
"""PART C of EXP-ECQ-f5af06: quadratic twists and near neighbours of ICARM no. 302,
triaged in LOCKSTEP against a matched null and gated by the frozen top-20 rule.

RANK IS NOT TWIST-INVARIANT. The 31 points of no. 302 DO NOT TRANSFER to E^(D).
E^(D) has its own Mordell-Weil rank, about which the rank of no. 302 says nothing.

THE NUMBER-FIELD TRAP. rank E(Q) + rank E^(D)(Q) = rank E(Q(sqrt D)). Since
rank E(Q) >= 31, ANY twist of positive rank gives rank >= 32 OVER THE QUADRATIC
FIELD Q(sqrt D). THAT IS NOT THIS GOAL'S OBJECTIVE. GOAL-ECQ-2298dc C1 is rank
>= 32 OVER Q, and a previous campaign's rank->=31 result over multiquadratic
fields was REJECTED for exactly this reason. Every positive twist row below
carries `field_of_the_reported_rank: Q` and the explicit statement that the
quadratic-field consequence does not meet C1.
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from part_a import CERT_KW

PRIME_BOUND = C.FROZEN["part_c_triage"]["prime_bound"]     # 500, FROZEN
GATE_SIZE = C.FROZEN["part_c_triage"]["gate_size"]         # 20, FROZEN


def sort_key(row):
    """FROZEN selection rule: descending S; ties broken by smallest |identifier|,
    then positive sign before negative."""
    return (-row["S"], abs(row["ident"]), 0 if row["ident"] > 0 else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-out", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--triage-cap-seconds", type=float, default=600.0)
    ap.add_argument("--gate-cap-seconds", type=float, default=500.0)
    a = ap.parse_args()

    t_start = time.time()
    log = lambda s: (print(s), sys.stdout.flush())

    d = C.load_input()
    ai = [int(x) for x in d["ainvs"]]
    base_std = C.to_standard_model(ai)
    rbox = C.FROZEN["part_c_reduced_box"]

    out = {
        "part": "C",
        "experiment_id": "EXP-ECQ-f5af06",
        "task_id": "TASK-20260824-261bb4",
        "question": ("Does any quadratic twist of ICARM no. 302 within a frozen "
                     "discriminant range, or any near neighbour within a frozen "
                     "perturbation range, carry certifiable rank -- and does the twist "
                     "family show any enrichment over a matched null?"),
        "rank_is_not_twist_invariant": (
            "The 31 points of no. 302 DO NOT TRANSFER to E^(D). E^(D) has its own "
            "Mordell-Weil rank, about which the rank of no. 302 says nothing, and which "
            "must be established from scratch by exhibited points on E^(D) itself. No row "
            "below treats a twist as inheriting rank."),
        "the_number_field_trap": (
            "rank E(Q) + rank E^(D)(Q) = rank E(Q(sqrt D)). Since rank E(Q) >= 31, ANY "
            "twist of positive rank immediately gives rank >= 32 OVER THE QUADRATIC FIELD "
            "Q(sqrt D). THAT IS NOT THIS GOAL'S OBJECTIVE AND IS NOT PRESENTED AS MEETING "
            "OR APPROACHING IT: GOAL-ECQ-2298dc C1 is rank >= 32 OVER Q. Every rank "
            "reported below is a rank OVER Q of the named curve."),
        "provenance_caveat": C.PROVENANCE_CAVEAT,
        "frozen_twist_range_verbatim": C.FROZEN["part_c_twist_set"]["description"],
        "frozen_perturbation_range_verbatim": C.FROZEN["part_c_null_set"]["description"],
        "frozen_triage_verbatim": C.FROZEN["part_c_triage"],
        "frozen_reduced_box_verbatim": rbox["description"],
        "floating_point_statement": (
            "Floating point appears in part C in exactly two decision-free places: the "
            "REPORTED logarithms log max(|c4|^3, c6^2) and log|disc| of exact integers, "
            "and the Mestre-Nagao TRIAGE SCORE S. The score CERTIFIES NOTHING -- it only "
            "selects which candidates receive the exact gate -- and every certification, "
            "squareness test and independence decision below is exact integer / Fraction "
            "arithmetic."),
        "observations": [],
        "deviations": [],
    }
    out["certifier_sha256"] = hashlib.sha256(open(C.CERTIFIER_PATH, "rb").read()).hexdigest()
    out["input_files"] = [
        {"path": "coordination/goals/GOAL-ECQ-2298dc/inputs/ICARM-302.json",
         "sha256": hashlib.sha256(open(C.INPUT_PATH, "rb").read()).hexdigest()},
        {"path": os.path.relpath(C.CERTIFIER_PATH, C.REPO), "sha256": out["certifier_sha256"]},
    ]

    # ---------------- DENOMINATORS FIRST, BEFORE ANY CANDIDATE IS SCORED ----
    log("== computing N_C_TWIST, N_C_NULL and the reduced-box denominator BEFORE scoring ==")
    twist_D = [D for D in range(-200, -1) if C.squarefree(D)] + [-1] + \
              [D for D in range(2, 201) if C.squarefree(D)]
    twist_D = sorted(set(twist_D), key=lambda D: (abs(D), 0 if D > 0 else 1))
    N_C_TWIST = len(twist_D)

    null_v = [v for v in range(-100, 0)] + [v for v in range(1, 101)]
    null_v = sorted(set(null_v), key=lambda v: (abs(v), 0 if v > 0 else 1))
    null_generated = len(null_v)

    N_RBOX, rper = C.box_denominator(rbox)

    out["N_C_TWIST"] = N_C_TWIST
    out["N_C_TWIST_members"] = twist_D
    out["N_C_NULL_generated_before_discard"] = null_generated
    out["N_reduced_box"] = N_RBOX
    out["denominators_recorded_before_any_candidate_scored"] = True
    out["denominator_note"] = (
        "N_C_TWIST, the null-arm generated count and the reduced-box denominator are "
        "fixed integers determined by the contract alone. They were computed and written "
        "here BEFORE the first candidate was scored and MAY NOT be recomputed, narrowed "
        "or widened afterwards. If the budget forces fewer candidates to be scored, that "
        "is A COVERAGE SHORTFALL REPORTED AS A FRACTION, NEVER A REDEFINITION.")
    log("   N_C_TWIST = %d, null generated = %d, N_reduced_box = %d"
        % (N_C_TWIST, null_generated, N_RBOX))
    json.dump(out, open(a.raw_out, "w"), indent=1)

    # ---------------- build both arms, recording every discard --------------
    twist_rows = []
    for D in twist_D:
        m = C.quadratic_twist_standard(base_std, D)
        disc = C.discriminant(m)
        twist_rows.append({"arm": "twist", "ident": D, "identifier_name": "D",
                           "model": [str(x) for x in m], "disc_zero": disc == 0,
                           "status": "generated", "reason": None})

    null_rows = []
    n_discarded = 0
    for v in null_v:
        m = C.to_standard_model([1, 1, 1, ai[3], ai[4] + v])
        disc = C.discriminant(m)
        row = {"arm": "null", "ident": v, "identifier_name": "v",
               "model": [str(x) for x in m], "disc_zero": disc == 0,
               "status": "generated", "reason": None}
        if disc == 0:
            row["status"] = "discarded"
            row["reason"] = "zero discriminant (singular model); discard recorded per contract"
            n_discarded += 1
        null_rows.append(row)
    N_C_NULL = sum(1 for r in null_rows if r["status"] != "discarded")
    out["N_C_NULL"] = N_C_NULL
    out["null_arm_discarded_count"] = n_discarded
    out["null_arm_discarded_identifiers"] = [r["ident"] for r in null_rows if r["status"] == "discarded"]
    log("   N_C_NULL = %d (discarded %d for zero discriminant)" % (N_C_NULL, n_discarded))

    out["model_normalisation_decision"] = {
        "what": ("BOTH ARMS are scored and gated on the standard integral model "
                 "[0, b2, 0, 8*b4, 16*b6], obtained from the a-invariants by completing "
                 "the square. The twist arm is [0, b2 D, 0, 8 b4 D^2, 16 b6 D^3]; the "
                 "null arm is the same transformation applied to [1, 1, 1, a4, a6 + v]."),
        "why": ("CTL-MATCHED-NULL requires the same instrument in both arms. Applying the "
                "same model normalisation to both means the two arms differ only in the "
                "perturbation being studied, not in model shape. a_p at a good prime is a "
                "Q-isomorphism invariant, so the normalisation does not change any score "
                "at a good prime; at bad primes the convention is uniform across arms."),
        "executor_choice_not_a_frozen_term": (
            "The contract does not fix the model normalisation, only the twist set, the "
            "perturbation set, the score, the prime bound and the top-20 rule. This is "
            "recorded as an executor implementation decision, applied identically to both "
            "arms."),
    }
    out["minimality_limitation"] = {
        "what": ("GLOBAL MINIMALITY OF THE TWIST AND NULL MODELS IS NOT ESTABLISHED. "
                 "Laska-Kraus-Connell minimalisation requires factoring the discriminant, "
                 "which here is an integer of roughly 450 to 900 decimal digits, and that "
                 "is not feasible within this budget or any budget."),
        "why_it_does_not_invalidate_the_measurements": (
            "A rank LOWER bound from exhibited points is invariant under Q-isomorphism and "
            "does not require a minimal model. The naive heights reported below are "
            "therefore heights OF THE STATED MODEL, not minimal-model heights, and are "
            "labelled as such."),
        "where_it_would_bind": (
            "Claim-bar clause (1) requires minimality to be ESTABLISHED rather than "
            "assumed before the words 'rank 32' may appear. No such claim is made from "
            "part C; if a gated curve had certified rank >= 32 over Q, this limitation "
            "would be a blocking gap against the claim bar and is recorded here in "
            "advance so that it cannot be skipped later."),
    }

    # ---------------- CALIBRATION of the frozen score (recorded, decides nothing)
    log("== calibrating the frozen triage score against curves of known rank ==")
    calib = []
    for name, aa, rk, src in (
            ("11a1", [0, -1, 1, -10, -20], 0, "Cremona 11.a1 / LMFDB 11.a1"),
            ("37a1", [0, 0, 1, -1, 0], 1, "Cremona 37.a1 / LMFDB 37.a1"),
            ("389a1", [0, 1, 1, -2, 0], 2, "Cremona 389.a1 / LMFDB 389.a1"),
            ("5077a1", [0, 0, 1, -7, 6], 3, "Cremona 5077.a1 / LMFDB 5077.a1")):
        S, _ = C.mestre_nagao_score(C.to_standard_model(aa), PRIME_BOUND)
        calib.append({"curve": name, "source": src, "published_rank": rk, "S": round(S, 6)})
        log("   %-8s rank %d  S = %8.4f" % (name, rk, S))
    S302, _ = C.mestre_nagao_score(base_std, PRIME_BOUND)
    calib.append({"curve": "ICARM no. 302", "source": "the target curve, part A",
                  "published_rank": ">= 31 (certified by part A)", "S": round(S302, 6)})
    log("   %-8s rank>=31 S = %8.4f" % ("no.302", S302))

    out["frozen_score_calibration"] = {
        "table": calib,
        "measured_with": ("the SAME implementation, the SAME prime bound 500 and the SAME "
                          "conventions used for both arms below"),
        "bad_prime_convention_STATED_FOR_RECONCILIATION": (
            "THIS RUN INCLUDES EVERY PRIME p <= 500 IN THE SUM, GOOD OR BAD. For each p, "
            "#E(F_p) is the naive count of affine solutions of the Weierstrass equation "
            "of the STATED MODEL over F_p, plus one point at infinity, and a_p = p + 1 - "
            "#E(F_p). At a prime of BAD reduction that count is the point count of the "
            "SINGULAR model, which is a well-defined uniform convention rather than the "
            "arithmetic a_p of the curve. It is applied identically to every candidate in "
            "both arms, which is what CTL-MATCHED-NULL requires. "
            "THE COORDINATOR'S INDEPENDENT RE-DERIVATION SKIPS p | disc, which is why the "
            "two absolute scales differ slightly -- e.g. 11a1 gives S = +1.57 here and "
            "S = +0.66 under the skip-bad-primes convention, and no. 302 gives -38.83 "
            "here and -38.78 there. THE TWO ARE RECONCILABLE BY EXACTLY THAT CHOICE. The "
            "ordering and the direction of the effect are identical under both "
            "conventions, and the direction is the whole of the observation."),
        "OBSERVATION_THE_FROZEN_GATE_IS_SIGN_INVERTED": (
            "S DECREASES MONOTONICALLY WITH RANK across the calibration curves: rank 0 "
            "gives S = +1.57, rank 1 gives -4.06, rank 2 gives -11.04, rank 3 gives "
            "-18.10, and rank >= 31 gives -38.83. This is the expected direction: a_p = "
            "p + 1 - #E(F_p) is small or negative exactly when #E(F_p) is large, which is "
            "the Mestre-Nagao signature of HIGH rank. THE CONTRACT'S FROZEN GATE SELECTS "
            "THE TOP 20 BY S, i.e. THE LARGEST S, WHICH SELECTS THE LOWEST-RANK "
            "CANDIDATES IN EACH ARM -- the opposite of the triage's stated purpose."),
        "what_was_done_about_it": (
            "NOTHING WAS CHANGED. The gate is applied exactly as frozen. Changing a "
            "frozen selection rule after any score is known makes the numerator and the "
            "denominator both functions of the outcome, which is the defect class this "
            "program has already paid for twice, and the contract requires a versioned "
            "protocol_amendment for any such change. The FULL SCORE OF EVERY SCORED "
            "CANDIDATE IN BOTH ARMS is recorded below, so a re-gate under an amendment "
            "needs no new scoring run."),
        "what_it_means_for_the_readout": (
            "The matched-null comparison is UNHARMED, because the same rule is applied to "
            "both arms. But a null result from this gate is NOT evidence that the twist "
            "neighbourhood of no. 302 is barren: the gate looked at the least promising "
            "20 candidates by the score's own logic. This is an observation for the "
            "Coordinator and the Reviewer; the Executor draws no conclusion from it."),
    }

    # ---------------- LOCKSTEP TRIAGE -------------------------------------
    log("== triaging both arms IN LOCKSTEP (cap %.0fs) ==" % a.triage_cap_seconds)
    twist_live = [r for r in twist_rows if r["status"] != "discarded"]
    null_live = [r for r in null_rows if r["status"] != "discarded"]
    deadline = t_start + a.triage_cap_seconds
    t_tri = time.time()
    n_scored = {"twist": 0, "null": 0}
    truncated = False
    for i in range(max(len(twist_live), len(null_live))):
        if time.time() > deadline:
            truncated = True
            log("   TRIAGE CAP REACHED after %d twist / %d null" % (n_scored["twist"], n_scored["null"]))
            break
        for arm, lst in (("twist", twist_live), ("null", null_live)):
            if i < len(lst):
                row = lst[i]
                m = [int(x) for x in row["model"]]
                S, _ = C.mestre_nagao_score(m, PRIME_BOUND)
                row["S"] = round(S, 6)
                row["status"] = "scored"
                n_scored[arm] += 1
        if i % 50 == 0:
            log("   lockstep i=%d  twist %d  null %d  (%.1fs)"
                % (i, n_scored["twist"], n_scored["null"], time.time() - t_tri))
    triage_wall = time.time() - t_tri
    log("   triage done: twist %d/%d, null %d/%d in %.1fs"
        % (n_scored["twist"], N_C_TWIST, n_scored["null"], N_C_NULL, triage_wall))

    for r in twist_rows + null_rows:
        if r["status"] == "generated":
            r["status"] = "not_scored"
            r["reason"] = "triage wall-clock cap reached before this candidate was scored"

    # ---------------- THE FROZEN GATE: exactly the top 20 by S per arm ------
    gated = {}
    for arm, rows in (("twist", twist_rows), ("null", null_rows)):
        scored = [r for r in rows if r["status"] == "scored"]
        ordered = sorted(scored, key=sort_key)
        gated[arm] = ordered[:GATE_SIZE]
        for r in gated[arm]:
            r["gated"] = True
        for r in ordered[GATE_SIZE:]:
            r["gated"] = False
        log("   %s arm: gated %d of %d (frozen gate size %d)"
            % (arm, len(gated[arm]), GATE_SIZE, GATE_SIZE))

    # ---------------- EXACT GATE on the survivors --------------------------
    log("== exact gate on the survivors (cap %.0fs) ==" % a.gate_cap_seconds)
    t_gate = time.time()
    gate_deadline = t_gate + a.gate_cap_seconds
    gate_results = {"twist": [], "null": []}
    certs_to_reverify = []
    gate_truncated = False
    order = []
    for i in range(GATE_SIZE):
        for arm in ("twist", "null"):
            if i < len(gated[arm]):
                order.append((arm, gated[arm][i]))
    for arm, row in order:
        if time.time() > gate_deadline:
            gate_truncated = True
            row["gate_status"] = "not_gated"
            row["gate_reason"] = "exact-gate wall-clock cap reached"
            continue
        m = [int(x) for x in row["model"]]
        inv = C.exact_invariants(m)
        remaining = gate_deadline - time.time()
        hits, n_tested, exhausted, wall = C.search_box(
            m, rbox, time.time() + max(1.0, min(remaining, 40.0)))
        cert = None
        k = 0
        if hits:
            cert = C.EC.certify([str(x) for x in m], hits, **CERT_KW)
            k = cert["certified_rank_lower_bound"]
        prov = C.provenance_check(m, "%s arm, %s = %d" % (arm, row["identifier_name"], row["ident"]))
        res = {
            "arm": arm,
            "identifier_name": row["identifier_name"],
            "identifier": row["ident"],
            "triage_score_S": row["S"],
            "model_a_invariants": [str(x) for x in m],
            "model_note": ("standard integral model [0, b2, 0, 8 b4, 16 b6] of the twist / "
                           "perturbation; GLOBAL MINIMALITY NOT ESTABLISHED, see "
                           "minimality_limitation"),
            "exact_invariants": inv,
            "naive_height_of_the_stated_model_REPORTING_FLOAT": inv["naive_height_log_REPORTING_FLOAT"],
            "log_abs_disc_of_the_stated_model_REPORTING_FLOAT": inv["log_abs_disc_REPORTING_FLOAT"],
            "reduced_box_coverage": {
                "numerator": n_tested, "denominator": N_RBOX,
                "fraction": "%d / %d" % (n_tested, N_RBOX),
                "exhausted": exhausted,
                "wall_seconds": round(wall, 3),
            },
            "points_found": hits,
            "n_points_found": len(hits),
            "certified_rank_lower_bound": k,
            "field_of_the_reported_rank": "Q",
            "field_statement": (
                "This is a rank lower bound for E^(D)(Q) / the perturbed curve OVER Q. It "
                "is NOT a rank over a number field. Any quadratic-field consequence of a "
                "positive value here (rank E(Q) + rank E^(D)(Q) = rank E(Q(sqrt D))) DOES "
                "NOT MEET AND DOES NOT APPROACH GOAL-ECQ-2298dc C1, which is rank >= 32 "
                "OVER Q."),
            "certificate_kind": "independence_certificate" if k > 0 else "none",
            "certificate_kind_reason": (
                "no point was found in the reduced box, so there is nothing to certify"
                if not hits else
                "points were found and passed to the exact certifier"),
            "certifier_output": cert,
            "provenance_check": prov,
        }
        if k > 0:
            certs_to_reverify.append({
                "label": "PART C %s arm %s=%d" % (arm, row["identifier_name"], row["ident"]),
                "a_invariants": [str(x) for x in m], "points": hits,
                "certified_rank_lower_bound": k,
                "l": (cert.get("independence") or {}).get("l"),
                "primes_used": (cert.get("independence") or {}).get("primes_used"),
                "torsion_bound": cert.get("torsion_bound"),
                "torsion_bound_primes": cert.get("torsion_bound_primes"),
            })
        row["gate_status"] = "gated"
        gate_results[arm].append(res)
        log("   %-5s %s=%-5d S=%9.4f  pts=%d  rank>=%d  box %d/%d"
            % (arm, row["identifier_name"], row["ident"], row["S"], len(hits), k,
               n_tested, N_RBOX))
    gate_wall = time.time() - t_gate

    # ---------------- arm-by-arm summary (CTL-MATCHED-NULL) ----------------
    def dist(rows):
        s = sorted(r["S"] for r in rows if r.get("S") is not None)
        if not s:
            return None
        n = len(s)
        q = lambda f: s[min(n - 1, int(f * n))]
        return {"n": n, "min": s[0], "max": s[-1],
                "range": round(s[-1] - s[0], 6),
                "median": s[n // 2],
                "q1": s[n // 4], "q3": s[(3 * n) // 4],
                "deciles": {("d%d" % d): q(d / 10.0) for d in range(1, 10)},
                "mean": round(sum(s) / n, 6),
                "stdev": round((sum((x - sum(s) / n) ** 2 for x in s) / n) ** 0.5, 6)}

    arms = {}
    for arm, rows, denom in (("twist", twist_rows, N_C_TWIST), ("null", null_rows, N_C_NULL)):
        sc = [r for r in rows if r["status"] == "scored"]
        gr = gate_results[arm]
        ranks = [g["certified_rank_lower_bound"] for g in gr]
        arms[arm] = {
            "generated": len([r for r in rows if r["status"] != "discarded"]),
            "discarded": len([r for r in rows if r["status"] == "discarded"]),
            "scored": len(sc),
            "gated": len(gr),
            "denominator": denom,
            "triage_coverage": {"numerator": len(sc), "denominator": denom,
                                "fraction": "%d / %d" % (len(sc), denom),
                                "percent": round(100.0 * len(sc) / denom, 4)},
            "gate_coverage": {"numerator": len(gr), "denominator": GATE_SIZE,
                              "fraction": "%d / %d" % (len(gr), GATE_SIZE)},
            "score_distribution": dist(sc),
            "max_certified_rank_lower_bound_over_Q": max(ranks) if ranks else None,
            "certified_rank_histogram": {str(v): ranks.count(v) for v in sorted(set(ranks))} if ranks else {},
            "total_points_found_across_gated": sum(g["n_points_found"] for g in gr),
        }

    out["arms"] = arms

    # ---- between-arm score comparison, requested for the amendment record --
    tw_S = sorted(r["S"] for r in twist_rows if r["status"] == "scored")
    nl_S = sorted(r["S"] for r in null_rows if r["status"] == "scored")
    comp = {"twist_n": len(tw_S), "null_n": len(nl_S)}
    if tw_S and nl_S:
        mt = sum(tw_S) / len(tw_S)
        mn = sum(nl_S) / len(nl_S)
        # Mann-Whitney U with midranks, exact integer counting of pairwise wins
        greater = ties = 0
        for x in tw_S:
            for y in nl_S:
                if x > y:
                    greater += 1
                elif x == y:
                    ties += 1
        n1, n2 = len(tw_S), len(nl_S)
        U = greater + 0.5 * ties
        mu = n1 * n2 / 2.0
        sd = (n1 * n2 * (n1 + n2 + 1) / 12.0) ** 0.5
        comp.update({
            "twist_mean": round(mt, 6), "null_mean": round(mn, 6),
            "mean_difference_twist_minus_null": round(mt - mn, 6),
            "twist_median": tw_S[len(tw_S) // 2], "null_median": nl_S[len(nl_S) // 2],
            "median_difference_twist_minus_null": round(tw_S[len(tw_S) // 2] - nl_S[len(nl_S) // 2], 6),
            "mann_whitney_U_twist_over_null": U,
            "mann_whitney_U_expected_under_no_difference": mu,
            "mann_whitney_z_normal_approximation": round((U - mu) / sd, 4) if sd else None,
            "probability_a_random_twist_scores_above_a_random_null": round(U / (n1 * n2), 4),
            "twist_range": [tw_S[0], tw_S[-1]], "null_range": [nl_S[0], nl_S[-1]],
            "overlap_of_ranges": (max(tw_S[0], nl_S[0]) <= min(tw_S[-1], nl_S[-1])),
        })
    comp["what_this_is"] = (
        "A DESCRIPTIVE COMPARISON of the two arms' triage-score distributions, requested "
        "for the amendment record. It is the ONE comparison the frozen rule preserved "
        "intact, because both arms were scored with the same implementation, the same "
        "prime bound and the same conventions regardless of which end of the distribution "
        "the gate selected. The Mann-Whitney z is a normal approximation reported as a "
        "descriptive statistic; no significance threshold was pre-registered and none is "
        "asserted.")
    comp["what_this_is_not"] = (
        "It is NOT a rank measurement and NOT a certification. The triage score certifies "
        "nothing. The Executor records these numbers and draws no conclusion from them.")
    out["between_arm_score_comparison"] = comp
    out["CTL_MATCHED_NULL"] = {
        "id": "CTL-MATCHED-NULL",
        "control": ("the near-neighbour arm scored with the same implementation, the same "
                    "prime bound and the same top-20 rule as the twist arm, and gated "
                    "with the same reduced box"),
        "same_implementation": True,
        "same_prime_bound": PRIME_BOUND,
        "same_gate_rule": C.FROZEN["part_c_triage"]["gate"],
        "same_reduced_box": rbox["description"],
        "generated_scored_gated_per_arm": {
            arm: {"generated": arms[arm]["generated"], "scored": arms[arm]["scored"],
                  "gated": arms[arm]["gated"]} for arm in arms},
        "differential_attrition": (
            "twist scored %d/%d, null scored %d/%d; twist gated %d, null gated %d"
            % (arms["twist"]["scored"], N_C_TWIST, arms["null"]["scored"], N_C_NULL,
               arms["twist"]["gated"], arms["null"]["gated"])),
        "outcome": ("PASS" if (arms["twist"]["scored"] == N_C_TWIST
                               and arms["null"]["scored"] == N_C_NULL
                               and arms["twist"]["gated"] == arms["null"]["gated"])
                    else "PARTIAL"),
        "outcome_meaning": (
            "PASS means both arms were scored to completion with the same instrument and "
            "gated to the same depth, so the comparison is admissible. PARTIAL means a "
            "cap truncated one or both arms; the comparison is then reported with its "
            "coverage fractions and is weakened accordingly."),
        "prior_incident": ("This program has already manufactured a result once through "
                           "differential attrition across arms (EV-ECQ-8ee697 OBS-9)."),
    }

    # every attempted candidate, with identifier, status and reason
    out["all_candidates"] = [
        {"arm": r["arm"], "identifier_name": r["identifier_name"], "identifier": r["ident"],
         "status": r["status"], "reason": r["reason"], "S": r.get("S"),
         "gated": r.get("gated", False), "gate_status": r.get("gate_status")}
        for r in twist_rows + null_rows]
    out["attempted_vs_reported"] = {
        "twist_generated": len(twist_rows), "null_generated": len(null_rows),
        "rows_persisted": len(out["all_candidates"]),
        "check": ("every generated candidate in both arms is persisted above with an "
                  "identifier, a status and a reason; there is no arithmetic difference "
                  "between attempted and reported. 462 families vanished that way in "
                  "BATCH-541940."),
    }
    out["gate_results"] = gate_results
    out["certificates_to_reverify"] = certs_to_reverify

    # a labelled view of the score extremes -- NOT a gate, just a view of the
    # required per-candidate score data
    out["score_extremes_VIEW_NOT_A_GATE"] = {}
    for arm, rows in (("twist", twist_rows), ("null", null_rows)):
        sc = sorted([r for r in rows if r["status"] == "scored"], key=sort_key)
        out["score_extremes_VIEW_NOT_A_GATE"][arm] = {
            "top_20_by_S_THESE_ARE_THE_GATED_ONES":
                [{"ident": r["ident"], "S": r["S"]} for r in sc[:GATE_SIZE]],
            "bottom_20_by_S_NOT_GATED":
                [{"ident": r["ident"], "S": r["S"]} for r in sc[-GATE_SIZE:]],
            "note": ("The bottom-20 list is a VIEW of the per-candidate score data the "
                     "contract already requires to be reported, not a second gate. NO "
                     "EXACT GATE WAS APPLIED TO IT. It is surfaced only because the "
                     "calibration above shows S decreases with rank, so these are the "
                     "candidates the score itself ranks as most promising. Gating them "
                     "would require a versioned protocol_amendment and a new run."),
        }

    tw_max = arms["twist"]["max_certified_rank_lower_bound_over_Q"]
    nl_max = arms["null"]["max_certified_rank_lower_bound_over_Q"]
    if (tw_max or 0) >= 32 or (nl_max or 0) >= 32:
        out["branch_label"] = "C-POSITIVE"
    else:
        out["branch_label"] = "C-NULL"
    out["branch_defence"] = {
        "pre_declared_C_NULL": ("no gated curve in either arm certifies rank above 0 or 1, "
                                "with no separation between arms; the coverage fractions "
                                "and the two score distributions ARE the result"),
        "observed": out["branch_label"],
        "twist_max_certified_rank_over_Q": tw_max,
        "null_max_certified_rank_over_Q": nl_max,
        "separation_between_arms": (
            "none measurable: both arms' maximum certified rank lower bound over Q is %s "
            "and %s respectively, at the gate coverages reported above"
            % (tw_max, nl_max)),
        "scope": ("This statement is about EXACTLY the %d gated twists and %d gated null "
                  "curves selected by the frozen top-20-by-S rule, searched in the frozen "
                  "reduced box. It is not a statement about the twist family as a whole, "
                  "and given the sign-inversion observation above it is not evidence that "
                  "the twist neighbourhood is barren."
                  % (arms["twist"]["gated"], arms["null"]["gated"])),
    }

    out["triage_truncated"] = truncated
    out["gate_truncated"] = gate_truncated
    out["triage_wall_clock_seconds"] = round(triage_wall, 3)
    out["gate_wall_clock_seconds"] = round(gate_wall, 3)
    out["parameters"] = {
        "prime_bound": PRIME_BOUND, "gate_size": GATE_SIZE,
        "N_C_TWIST": N_C_TWIST, "N_C_NULL": N_C_NULL, "N_reduced_box": N_RBOX,
        "reduced_box": rbox,
        "certifier_search_bounds": {k: (list(v) if isinstance(v, tuple) else v)
                                    for k, v in CERT_KW.items()},
        "triage_cap_seconds": a.triage_cap_seconds, "gate_cap_seconds": a.gate_cap_seconds,
    }
    out["protocol_certificate"] = {
        "kind": "independence_certificate" if certs_to_reverify else "none",
        "kind_reason": ("no gated curve in either arm yielded a certified point, so there "
                        "is nothing to certify and the kind is stated explicitly as `none`"
                        if not certs_to_reverify else
                        "at least one gated curve yielded certified points"),
        "path": ("coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-261bb4/"
                 "twist_search.json"),
    }
    out["metrics"] = {
        "part_c_twist_triage_coverage": arms["twist"]["triage_coverage"]["fraction"],
        "part_c_null_triage_coverage": arms["null"]["triage_coverage"]["fraction"],
        "part_c_twist_gated_over_20": arms["twist"]["gate_coverage"]["fraction"],
        "part_c_null_gated_over_20": arms["null"]["gate_coverage"]["fraction"],
        "part_c_twist_max_certified_rank_over_Q": tw_max,
        "part_c_null_max_certified_rank_over_Q": nl_max,
        "part_c_N_reduced_box": N_RBOX,
        "part_c_triage_wall_clock_seconds": round(triage_wall, 3),
        "part_c_gate_wall_clock_seconds": round(gate_wall, 3),
        "ctl_matched_null": out["CTL_MATCHED_NULL"]["outcome"],
        "total_wall_clock_seconds": round(time.time() - t_start, 3),
    }
    out["wall_clock_seconds"] = round(time.time() - t_start, 3)

    json.dump(out, open(a.raw_out, "w"), indent=1)
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
    log("== part C done: branch %s ==" % out["branch_label"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
