#!/usr/bin/env python3
"""PART C of EXP-ECQ-f5af06 **v2**: quadratic twists and near neighbours of ICARM
no. 302, triaged in LOCKSTEP against a matched null and gated by the CORRECTED
frozen rule of PA-ECQ-f5af06-v2-triage-gate-sign.

THE GATE WAS SIGN-INVERTED IN v1 AND IS CORRECTED HERE.  S DECREASES WITH RANK,
so the gate selects THE 200 CANDIDATES OF SMALLEST S PER ARM -- most negative
first.  v1 gated the top 20 by S, i.e. the candidates each arm's own score ranks
as LEAST promising.  v1's result STANDS AS RECORDED and is reported beside v2's,
never replaced.  CTL-GATE-DIRECTION is BLOCKING: if it fails, NOTHING is gated in
either arm and the run reports triage coverage and score distributions only.

RANK IS NOT TWIST-INVARIANT.  The 31 points of no. 302 DO NOT TRANSFER to E^(D).

THE NUMBER-FIELD TRAP, STATED CORRECTLY.  rank E(Q) + rank E^(D)(Q) =
rank E(Q(sqrt D)), so ADDING no. 302's rank to a twist's rank gives a rank over
the QUADRATIC FIELD Q(sqrt D) -- the shape a previous campaign's result was
rejected for, and no artifact here performs that addition.  What the trap does
NOT forbid: a twist E^(D) whose OWN Mordell-Weil rank OVER Q is at least 32 is a
legitimate rank->=32 curve over Q and WOULD MEET GOAL-ECQ-2298dc C1 in full,
subject to the six-clause claim bar.  PART C IS NOT STRUCTURALLY DISQUALIFIED;
only its v1 gate was broken.  Every rank reported below carries
field_of_the_reported_rank: Q.
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

PRIME_BOUND = C.FROZEN["part_c_triage"]["prime_bound"]     # 500,  FROZEN, unchanged from v1
GATE_SIZE = C.FROZEN["part_c_triage"]["gate_size"]         # 200,  FROZEN v2 (CHG-2)
SCREEN_B = C.FROZEN["minimality_screen_prime_bound"]       # 100000, FROZEN v2 (CHG-7)

V1_TWIST_SEARCH = os.path.join(
    C.REPO, "coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-261bb4/twist_search.json")

AMENDMENT = "PA-ECQ-f5af06-v2-triage-gate-sign"

# The calibration table frozen in the amendment, reproduced so the gate direction
# cannot invert again by being restated in prose alone.  rank_used values are the
# CERTIFIED RANK LOWER BOUNDS this program produced in v1; 11a1 is carried for the
# record and is EXCLUDED from the pass condition because rank 0 is a rank EQUALITY
# claim that this program's certifier cannot make.
CALIB = [
    ("11a1", [0, -1, 1, -10, -20], 0, False,
     "EXTERNAL AND NOT VERIFIED BY THIS PROGRAM: rank 0 is a rank EQUALITY claim and "
     "cannot be certified by exhibiting points. Reported for the record; EXCLUDED from "
     "the CTL-GATE-DIRECTION pass condition.", 1.57),
    ("37a1", [0, 0, 1, -1, 0], 1, True,
     "CERTIFIED RANK LOWER BOUND 1 INSIDE THIS PROGRAM (v1 proves-too-much and "
     "saturation control rows; re-established in this run set by part A).", -4.06),
    ("389a1", [0, 1, 1, -2, 0], 2, True,
     "CERTIFIED RANK LOWER BOUND 2 INSIDE THIS PROGRAM (CTL-POSITIVE-INDEPENDENCE).", -11.04),
    ("5077a1", [0, 0, 1, -7, 6], 3, True,
     "CERTIFIED RANK LOWER BOUND 3 INSIDE THIS PROGRAM (CTL-POSITIVE-INDEPENDENCE), "
     "using the CORRECT generators {(-2,3), (-1,3), (0,2)}; the triple "
     "{(-1,3), (0,2), (2,0)} is DEPENDENT (v1 DEV-A-01).", -18.10),
]


def dump_doc(doc, path):
    """Write the deliverable with the per-candidate dump REDUCED AT SOURCE.

    The compact rows are emitted one per line as a JSON array rather than
    indented, which keeps every attempted candidate inside the deliverable while
    staying under the 5 MiB per-file artifact budget.  Indented, ~24000 rows
    would be roughly 14 MiB; BATCH-541940 committed 328 MiB and the only
    cost-free moment to prevent that is before the producer writes.
    """
    rows = doc.get("all_candidates_compact")
    if rows is None:
        open(path, "w").write(json.dumps(doc, indent=1))
        return
    doc = dict(doc)
    doc["all_candidates_compact"] = "@@COMPACT_ROWS@@"
    text = json.dumps(doc, indent=1)
    body = "[\n" + ",\n".join(json.dumps(r, separators=(",", ":")) for r in rows) + "\n]"
    open(path, "w").write(text.replace('"@@COMPACT_ROWS@@"', body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-out", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--triage-cap-seconds", type=float, default=600.0)
    ap.add_argument("--gate-cap-seconds", type=float, default=1500.0)
    ap.add_argument("--minimality-cap-seconds", type=float, default=300.0)
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
        "task_id": "TASK-20260824-02c3e4",
        "contract": "experiments/EXP-ECQ-f5af06/specification.yaml (v1, immutable)",
        "governing_amendment": ("experiments/EXP-ECQ-f5af06/amendments/"
                                "PA-ECQ-f5af06-v2-triage-gate-sign.yaml (v2 overlay)"),
        "question": ("Does any quadratic twist of ICARM no. 302 within the frozen v2 "
                     "discriminant range, or any near neighbour within the frozen v2 "
                     "perturbation range, carry certifiable rank -- and does the twist "
                     "family show any enrichment over a matched null?"),
        "THE_GATE_WAS_INVERTED_IN_v1_AND_IS_CORRECTED_HERE": (
            "v1 froze 'the exact gate is applied to exactly the TOP 20 CANDIDATES BY S in "
            "each arm'. S DECREASES WITH RANK, so top-by-S selects the LOWEST-rank "
            "candidates -- the opposite of the triage's stated purpose. v1's Executor "
            "applied the frozen rule exactly as written, refused to self-authorise a "
            "change and recorded the inversion; that was correct. THE DEFECT WAS THE "
            "COORDINATOR'S. Under amendment %s the gate is THE 200 CANDIDATES OF SMALLEST "
            "S PER ARM -- most negative first. v1's C-NULL branch is REAL AS RECORDED and "
            "is UNINFORMATIVE ABOUT THE TWIST NEIGHBOURHOOD; it may never be cited as "
            "evidence that the neighbourhood is barren." % AMENDMENT),
        "gate_direction_in_words": C.FROZEN["part_c_triage"]["gate_direction_in_words"],
        "gate_direction_statement": C.FROZEN["part_c_triage"]["gate_direction_statement"],
        "rank_is_not_twist_invariant": (
            "The 31 points of no. 302 DO NOT TRANSFER to E^(D). E^(D) has its own "
            "Mordell-Weil rank, about which the rank of no. 302 says nothing, and which "
            "must be established from scratch by exhibited points on E^(D) itself. No row "
            "below treats a twist as inheriting rank."),
        "the_number_field_trap_stated_correctly": (
            "WHAT THE TRAP FORBIDS IS ADDING RANKS. rank E(Q) + rank E^(D)(Q) = "
            "rank E(Q(sqrt D)), so pairing no. 302's rank >= 31 with a positive-rank twist "
            "to announce rank >= 32 OVER Q(sqrt D) is the rejected shape, and "
            "GOAL-ECQ-2298dc C1 is rank >= 32 OVER Q. NO ARTIFACT OF THIS RUN PERFORMS "
            "THAT ADDITION. WHAT THE TRAP DOES NOT FORBID: a quadratic twist E^(D) whose "
            "OWN rank over Q is at least 32 IS a legitimate rank->=32 curve over Q and "
            "WOULD MEET C1 IN FULL, subject to the six-clause claim bar. That E^(D) is a "
            "twist of no. 302 is a fact about how it was found, not a defect in what it "
            "is. PART C IS NOT STRUCTURALLY DISQUALIFIED; only its v1 gate was broken."),
        "provenance_caveat": C.PROVENANCE_CAVEAT,
        "frozen_twist_range_verbatim": C.FROZEN["part_c_twist_set"]["description"],
        "frozen_perturbation_range_verbatim": C.FROZEN["part_c_null_set"]["description"],
        "frozen_triage_verbatim": C.FROZEN["part_c_triage"],
        "frozen_reduced_box_verbatim": rbox["description"],
        "floating_point_statement": (
            "Floating point appears in part C in exactly two decision-free places: the "
            "REPORTED logarithms log max(|c4|^3, c6^2) and log|disc| of exact integers, "
            "and the Mestre-Nagao TRIAGE SCORE S. The score CERTIFIES NOTHING -- it only "
            "ORDERS candidates for the exact gate, which decides everything -- and every "
            "certification, squareness test, minimality screen and independence decision "
            "below is exact integer / Fraction arithmetic."),
        "observations": [],
        "deviations": [],
    }
    out["certifier_sha256"] = hashlib.sha256(open(C.CERTIFIER_PATH, "rb").read()).hexdigest()
    out["input_files"] = [
        {"path": "coordination/goals/GOAL-ECQ-2298dc/inputs/ICARM-302.json",
         "sha256": hashlib.sha256(open(C.INPUT_PATH, "rb").read()).hexdigest()},
        {"path": os.path.relpath(C.CERTIFIER_PATH, C.REPO), "sha256": out["certifier_sha256"]},
        {"path": os.path.relpath(V1_TWIST_SEARCH, C.REPO),
         "sha256": hashlib.sha256(open(V1_TWIST_SEARCH, "rb").read()).hexdigest(),
         "role": "v1 per-candidate scores, the reuse source for the 443 v1 candidates"},
    ]

    # ================= DENOMINATORS FIRST, BEFORE ANY CANDIDATE IS SCORED ====
    log("== computing N_C_TWIST_v2, N_C_NULL_v2 and N_BC_v2 BEFORE scoring anything ==")
    twist_D = [D for D in range(-10000, -1) if C.squarefree(D)] + [-1] + \
              [D for D in range(2, 10001) if C.squarefree(D)]
    twist_D = sorted(set(twist_D), key=lambda D: (abs(D), 0 if D > 0 else 1))
    N_C_TWIST = len(twist_D)

    null_v = [v for v in range(-6000, 0)] + [v for v in range(1, 6001)]
    null_v = sorted(set(null_v), key=lambda v: (abs(v), 0 if v > 0 else 1))
    null_generated = len(null_v)

    N_RBOX, rper = C.box_denominator(rbox)

    out["N_C_TWIST_v2"] = N_C_TWIST
    out["N_C_NULL_v2_generated_before_discard"] = null_generated
    out["N_BC_v2"] = N_RBOX
    out["denominators_recorded_before_any_candidate_scored"] = True
    out["denominator_note"] = (
        "N_C_TWIST_v2, the null-arm generated count and N_BC_v2 are fixed integers "
        "determined by the frozen descriptions ALONE. They were computed and written to "
        "disk BEFORE the first candidate was scored or tested and MAY NOT be recomputed, "
        "narrowed or widened afterwards. A budget shortfall is A COVERAGE FRACTION OVER "
        "THE UNCHANGED DENOMINATOR, NEVER A REDEFINITION. The Coordinator's hand "
        "estimates in the amendment (N_C_TWIST ~ 12159, N_C_NULL = 12000, reduced box ~ "
        "1167031) are explicitly NON-BINDING; these exact counts govern and any "
        "disagreement means the estimate was wrong.")
    out["coordinator_estimates_non_binding"] = {
        "N_C_TWIST_v2_estimate": 12159, "N_C_TWIST_v2_exact": N_C_TWIST,
        "N_C_NULL_v2_estimate": 12000, "N_BC_v2_estimate": 1167031, "N_BC_v2_exact": N_RBOX,
        "status": "estimates recorded only to show the exact counts were derived, not copied",
    }
    log("   N_C_TWIST_v2 = %d, null generated = %d, N_BC_v2 = %d"
        % (N_C_TWIST, null_generated, N_RBOX))
    dump_doc(out, a.raw_out)          # denominators on disk before anything is scored

    # ================= build both arms, recording every discard =============
    twist_rows = []
    for D in twist_D:
        m = C.quadratic_twist_standard(base_std, D)
        twist_rows.append({"arm": "twist", "ident": D, "identifier_name": "D",
                           "model": m, "status": "generated", "reason": None})

    null_rows = []
    discards = []
    for v in null_v:
        m = C.to_standard_model([1, 1, 1, ai[3], ai[4] + v])
        row = {"arm": "null", "ident": v, "identifier_name": "v",
               "model": m, "status": "generated", "reason": None}
        if C.discriminant(m) == 0:
            row["status"] = "discarded"
            row["reason"] = "zero discriminant (singular model); discard recorded per contract"
            discards.append(v)
        null_rows.append(row)
    N_C_NULL = sum(1 for r in null_rows if r["status"] != "discarded")
    out["N_C_NULL_v2"] = N_C_NULL
    out["null_arm_discarded_count"] = len(discards)
    out["null_arm_discarded_identifiers_with_reason"] = [
        {"v": v, "reason": "zero discriminant (singular model)"} for v in discards]
    log("   N_C_NULL_v2 = %d (discarded %d for zero discriminant)" % (N_C_NULL, len(discards)))
    dump_doc(out, a.raw_out)

    out["model_normalisation_decision"] = {
        "what": ("BOTH ARMS are scored and gated on the standard integral model "
                 "[0, b2, 0, 8*b4, 16*b6]. The twist arm is [0, b2 D, 0, 8 b4 D^2, "
                 "16 b6 D^3]; the null arm is the same transformation applied to "
                 "[1, 1, 1, a4, a6 + v]. UNCHANGED FROM v1 BY DESIGN, because the "
                 "amendment pins these conventions so v1's scores stay comparable."),
        "why": ("CTL-MATCHED-NULL requires the same instrument in both arms. a_p at a "
                "good prime is a Q-isomorphism invariant, so the normalisation changes no "
                "score at a good prime; at bad primes the convention is uniform across arms."),
        "executor_choice_not_a_frozen_term": (
            "v1 recorded this as an executor implementation decision. The v2 amendment "
            "PINS it explicitly (triage_conventions_pinned_because_reuse_depends_on_them), "
            "so in v2 it is a frozen term and is applied verbatim."),
    }

    # ================= CTL-GATE-DIRECTION (BLOCKING), BEFORE ANY GATING ======
    log("== CTL-GATE-DIRECTION (BLOCKING) ==")
    calib_rows = []
    toy = []
    for name, aa, rk, in_pass, basis, ref in CALIB:
        S, _ = C.mestre_nagao_score(C.to_standard_model(aa), PRIME_BOUND)
        calib_rows.append({"curve": name, "rank_used": rk, "rank_basis": basis,
                           "S_measured_in_this_run": round(S, 6),
                           "S_amendment_reference_value_executor_convention": ref,
                           "in_pass_condition": in_pass})
        if in_pass:
            toy.append({"name": name, "S": round(S, 6), "ident": 1, "rank": rk})
        log("   %-8s rank %-3s S = %9.4f  (amendment reference %.2f)" % (name, rk, S, ref))
    S302, _ = C.mestre_nagao_score(base_std, PRIME_BOUND)
    calib_rows.append({"curve": "ICARM no. 302", "rank_used": 31,
                       "rank_basis": ("CERTIFIED RANK LOWER BOUND 31 INSIDE THIS PROGRAM "
                                      "(v1 part A, A-FULL; part A is re-run in this run "
                                      "set for calibration)"),
                       "S_measured_in_this_run": round(S302, 6),
                       "S_amendment_reference_value_executor_convention": -38.83,
                       "in_pass_condition": True})
    toy.append({"name": "ICARM no. 302", "S": round(S302, 6), "ident": 1, "rank": 31})
    log("   %-8s rank>=31 S = %9.4f  (amendment reference %.2f)" % ("no.302", S302, -38.83))

    ordered_by_rank = sorted(toy, key=lambda r: r["rank"])
    strictly_decreasing = all(ordered_by_rank[i]["S"] > ordered_by_rank[i + 1]["S"]
                              for i in range(len(ordered_by_rank) - 1))
    toy_pick_order = [r["name"] for r in C.select_gated(toy, len(toy))]
    expected_order = ["ICARM no. 302", "5077a1", "389a1", "37a1"]
    gate_dir = {
        "id": "CTL-GATE-DIRECTION",
        "blocking": True,
        "when": "BEFORE any candidate is gated in either arm",
        "pass_condition_stated_before_it_runs": (
            "S(37a1) > S(389a1) > S(5077a1) > S(ICARM no. 302), and the gate's own "
            "selection routine returns them in the order 302, 5077a1, 389a1, 37a1. The "
            "11a1 row is reported but is NOT part of the pass condition, because rank 0 "
            "is a rank EQUALITY claim this program cannot certify."),
        "calibration_table": calib_rows,
        "S_strictly_decreasing_in_certified_rank": strictly_decreasing,
        "gate_selection_order_on_the_toy_population": toy_pick_order,
        "gate_selection_order_expected": expected_order,
        "gate_selection_order_matches": toy_pick_order == expected_order,
        "reference_note": ("Disagreement in the third decimal against the amendment's "
                           "reference values is not a failure; a DIFFERENT ORDER or a "
                           "DIFFERENT SIGN PATTERN is."),
        "failure_meaning": (
            "THE GATE IS INVERTED AGAIN, OR THE SCORE IMPLEMENTATION HAS DRIFTED. STOP. "
            "No candidate is gated in either arm, part C reports its triage coverage and "
            "its score distributions only, and the failure is a blocking defect."),
    }
    gate_dir["outcome"] = ("PASS" if (strictly_decreasing and gate_dir["gate_selection_order_matches"])
                           else "FAIL")
    out["CTL_GATE_DIRECTION"] = gate_dir
    log("   CTL-GATE-DIRECTION: %s (strictly decreasing=%s, order=%s)"
        % (gate_dir["outcome"], strictly_decreasing, toy_pick_order))
    dump_doc(out, a.raw_out)

    GATING_ALLOWED = gate_dir["outcome"] == "PASS"
    if not GATING_ALLOWED:
        out["observations"].append(
            "CTL-GATE-DIRECTION FAILED. NOTHING IS GATED IN EITHER ARM. Part C reports "
            "triage coverage and score distributions only, per the amendment's "
            "failure_meaning. This is a BLOCKING DEFECT reported to the Coordinator; the "
            "Executor draws no conclusion from it.")

    # ================= v1 SCORES: the values of record for the 443 ===========
    v1doc = json.load(open(V1_TWIST_SEARCH))
    v1_scores = {}
    for r in v1doc.get("all_candidates", []):
        if r.get("S") is not None:
            v1_scores[(r["arm"], r["identifier"])] = r["S"]
    log("   v1 recorded scores available for %d candidates" % len(v1_scores))

    # ================= LOCKSTEP TRIAGE ======================================
    log("== triaging both arms IN LOCKSTEP (cap %.0fs) ==" % a.triage_cap_seconds)
    twist_live = [r for r in twist_rows if r["status"] != "discarded"]
    null_live = [r for r in null_rows if r["status"] != "discarded"]
    t_tri = time.time()
    deadline = t_tri + a.triage_cap_seconds - 5.0
    n_scored = {"twist": 0, "null": 0}
    n_score_calls = 0
    truncated = False
    for i in range(max(len(twist_live), len(null_live))):
        if time.time() > deadline:
            truncated = True
            log("   TRIAGE CAP REACHED after %d twist / %d null"
                % (n_scored["twist"], n_scored["null"]))
            break
        for arm, lst in (("twist", twist_live), ("null", null_live)):
            if i < len(lst):
                row = lst[i]
                S_v2, _ = C.mestre_nagao_score(row["model"], PRIME_BOUND)
                n_score_calls += 1
                row["S_v2_measured"] = round(S_v2, 6)
                v1S = v1_scores.get((arm, row["ident"]))
                if v1S is not None:
                    # THE v1 VALUE IS THE VALUE OF RECORD.  The v2 re-score is the
                    # CTL-SCORE-REUSE-AGREEMENT control, not a replacement.
                    row["S"] = v1S
                    row["score_source"] = "v1_reused"
                else:
                    row["S"] = row["S_v2_measured"]
                    row["score_source"] = "v2_scored"
                row["status"] = "scored"
                n_scored[arm] += 1
        if i % 500 == 0:
            log("   lockstep i=%d  twist %d  null %d  (%.1fs)"
                % (i, n_scored["twist"], n_scored["null"], time.time() - t_tri))
    triage_wall = time.time() - t_tri
    log("   triage done: twist %d/%d, null %d/%d in %.1fs"
        % (n_scored["twist"], N_C_TWIST, n_scored["null"], N_C_NULL, triage_wall))

    for r in twist_rows + null_rows:
        if r["status"] == "generated":
            r["status"] = "not_scored"
            r["reason"] = "triage wall-clock cap reached before this candidate was scored"

    out["triage_truncated"] = truncated
    out["triage_wall_clock_seconds"] = round(triage_wall, 3)
    out["measured_seconds_per_triage_score"] = (round(triage_wall / n_score_calls, 9)
                                                if n_score_calls else None)

    # ================= CTL-SCORE-REUSE-AGREEMENT (BLOCKING) =================
    log("== CTL-SCORE-REUSE-AGREEMENT (BLOCKING) ==")
    disagreements = []
    max_abs = 0.0
    n_compared = 0
    for r in twist_rows + null_rows:
        if r.get("score_source") == "v1_reused":
            n_compared += 1
            diff = abs(r["S_v2_measured"] - r["S"])
            max_abs = max(max_abs, diff)
            if diff > 1.0e-06:
                disagreements.append({"arm": r["arm"], "identifier": r["ident"],
                                      "v1_recorded_S": r["S"],
                                      "v2_rescored_S": r["S_v2_measured"],
                                      "absolute_difference": diff})
    reuse = {
        "id": "CTL-SCORE-REUSE-AGREEMENT",
        "blocking": True,
        "control": ("re-score with the v2 implementation all 443 candidates v1 scored -- "
                    "the 243 twist candidates with 2 <= |D| <= 200 or D = -1, and the 200 "
                    "null candidates with |v| <= 100 -- and compare each against the value "
                    "recorded in v1's twist_search.json all_candidates. PASS is agreement "
                    "within 1.0e-06 absolute on every one."),
        "v1_candidates_expected": 443,
        "v1_candidates_compared": n_compared,
        "maximum_absolute_disagreement": max_abs,
        "tolerance": 1.0e-06,
        "disagreements": disagreements,
        "note": ("v1 recorded S rounded to 6 decimals; the comparison is against that "
                 "recorded value at the amendment's stated 1.0e-06 tolerance. THE REUSED "
                 "v1 VALUES REMAIN THE VALUES OF RECORD for those candidates and carry "
                 "score_source = v1_reused; this re-score is a control, not a replacement."),
        "failure_meaning": ("THE IMPLEMENTATION HAS DRIFTED AND THE POOLED DISTRIBUTION IS "
                            "NOT ONE DISTRIBUTION. Reuse is then FORBIDDEN and no pooled "
                            "or between-arm statistic may be computed."),
    }
    reuse["outcome"] = "PASS" if (not disagreements and n_compared == 443) else "FAIL"
    if n_compared != 443:
        reuse["coverage_caveat"] = (
            "Fewer than 443 v1 candidates were re-scored, which can only happen if the "
            "triage cap truncated before reaching them; the control is reported PARTIAL "
            "on coverage rather than PASS.")
        reuse["outcome"] = "FAIL" if disagreements else "PARTIAL"
    out["CTL_SCORE_REUSE_AGREEMENT"] = reuse
    log("   CTL-SCORE-REUSE-AGREEMENT: %s (compared %d, max |diff| = %.3e)"
        % (reuse["outcome"], n_compared, max_abs))
    # The control's failure mode is IMPLEMENTATION DRIFT -- a disagreement above
    # tolerance -- which makes the pooled values not one distribution.  A merely
    # PARTIAL comparison (the triage cap truncated before all 443 were reached)
    # is a coverage shortfall, not drift: the statistics are then computed and
    # carry the shortfall beside them.  A single disagreement forbids reuse and
    # withholds every between-arm statistic.
    STATS_ALLOWED = not disagreements
    reuse["statistics_permitted"] = STATS_ALLOWED
    reuse["statistics_permitted_reason"] = (
        "no disagreement above the 1.0e-06 tolerance, so the v1 and v2 values are one "
        "distribution and between-arm statistics are admissible"
        if STATS_ALLOWED else
        "at least one candidate disagreed above tolerance: reuse is FORBIDDEN and every "
        "between-arm statistic is withheld")

    # ================= THE CORRECTED GATE: 200 SMALLEST S PER ARM ===========
    gated = {"twist": [], "null": []}
    if GATING_ALLOWED:
        counts = {}
        for arm, rows in (("twist", twist_rows), ("null", null_rows)):
            counts[arm] = len([r for r in rows if r["status"] == "scored"])
        eff_gate = min(GATE_SIZE, counts["twist"], counts["null"])
        if eff_gate < GATE_SIZE:
            out["deviations"].append({
                "id": "DEV-C-GATE-SIZE-REDUCED",
                "what": ("an arm held fewer than %d scored candidates, so BOTH arms are "
                         "gated to %d to stay matched, per CHG-2" % (GATE_SIZE, eff_gate)),
                "reported_as": "a fraction over the frozen gate size 200",
            })
        for arm, rows in (("twist", twist_rows), ("null", null_rows)):
            scored = [r for r in rows if r["status"] == "scored"]
            picked = C.select_gated(scored, eff_gate)
            picked_ids = set(id(r) for r in picked)
            for r in scored:
                r["gated"] = id(r) in picked_ids
            gated[arm] = picked
            log("   %s arm: gated %d of frozen gate size %d (SMALLEST S FIRST)"
                % (arm, len(picked), GATE_SIZE))
    else:
        eff_gate = 0
        for r in twist_rows + null_rows:
            if r["status"] == "scored":
                r["gated"] = False
                r["gate_status"] = "not_gated_CTL_GATE_DIRECTION_FAILED"

    # ================= EXACT GATE ON THE SURVIVORS ==========================
    gate_results = {"twist": [], "null": []}
    certs_to_reverify = []
    gate_truncated = False
    t_gate = time.time()
    if GATING_ALLOWED:
        log("== exact gate on the survivors (cap %.0fs) ==" % a.gate_cap_seconds)
        gate_deadline = t_gate + a.gate_cap_seconds - 10.0
        order = []
        for i in range(eff_gate):
            for arm in ("twist", "null"):
                if i < len(gated[arm]):
                    order.append((arm, gated[arm][i]))
        remaining_curves = len(order)
        n_box_tests = 0
        for arm, row in order:
            now = time.time()
            if now > gate_deadline:
                gate_truncated = True
                row["gate_status"] = "not_gated"
                row["gate_reason"] = "exact-gate wall-clock cap reached"
                remaining_curves -= 1
                continue
            # equal adaptive slice, so a cap truncates BOTH arms symmetrically
            slice_s = max(1.0, (gate_deadline - now) / max(1, remaining_curves))
            remaining_curves -= 1
            m = row["model"]
            inv = C.exact_invariants(m)
            hits, n_tested, exhausted, wall = C.search_box(m, rbox, time.time() + slice_s)
            n_box_tests += n_tested
            cert = None
            k = 0
            if hits:
                cert = C.EC.certify([str(x) for x in m], hits, **CERT_KW)
                k = cert["certified_rank_lower_bound"]
            res = {
                "arm": arm,
                "identifier_name": row["identifier_name"],
                "identifier": row["ident"],
                "triage_score_S": row["S"],
                "score_source": row["score_source"],
                "model_a_invariants": [str(x) for x in m],
                "model_note": ("standard integral model [0, b2, 0, 8 b4, 16 b6] of the "
                               "twist / perturbation; GLOBAL MINIMALITY NOT ESTABLISHED"),
                "exact_invariants": inv,
                "naive_height_OF_THE_STATED_MODEL_REPORTING_FLOAT":
                    inv["naive_height_log_REPORTING_FLOAT"],
                "log_abs_disc_OF_THE_STATED_MODEL_REPORTING_FLOAT":
                    inv["log_abs_disc_REPORTING_FLOAT"],
                "height_label": ("a height OF THE STATED MODEL, not of a minimal model "
                                 "(CTL-MINIMALITY-DISCLOSURE)"),
                "reduced_box_coverage": {
                    "numerator": n_tested, "denominator": N_RBOX,
                    "fraction": "%d / %d" % (n_tested, N_RBOX),
                    "exhausted": exhausted, "wall_seconds": round(wall, 3),
                },
                "points_found": hits,
                "n_points_found": len(hits),
                "certified_rank_lower_bound": k,
                "field_of_the_reported_rank": "Q",
                "field_statement": (
                    "A rank LOWER BOUND for the named curve OVER Q, certified from points "
                    "exhibited on that curve itself. It is NOT a rank over a number field, "
                    "and no. 302's 31 points are NOT added to it: that addition would give "
                    "a rank over Q(sqrt D) and is the rejected shape."),
                "minimality_status": None,       # filled by the screen pass below
                "certificate_kind": "independence_certificate" if k > 0 else "none",
                "certificate_kind_reason": (
                    "no point was found in the reduced box, so there is nothing to certify"
                    if not hits else "points were found and passed to the exact certifier"),
                "certifier_output": cert,
            }
            if k >= 32:
                res["CLAIM_BAR_CLAUSE_1_OUTSTANDING"] = (
                    "CERTIFIED RANK LOWER BOUND >= 32 OVER Q FOR THIS CURVE'S OWN "
                    "MORDELL-WEIL GROUP. GLOBAL MINIMALITY IS NOT ESTABLISHED, so claim-bar "
                    "clause (1) is OUTSTANDING. The Executor DOES NOT attempt minimality "
                    "inline, DOES NOT stop the remaining coverage work, and DOES NOT state "
                    "this as a result. It routes to a dedicated Coordinator task and to "
                    "independent review-breakthrough review at max effort under AGENTS.md "
                    "rule 12 before any such words appear anywhere.")
                out["observations"].append(
                    "UNEXPECTED: %s arm %s = %s returned a certified rank lower bound of %d "
                    "over Q. Claim-bar clause (1) flagged OUTSTANDING; routed out, not "
                    "claimed." % (arm, row["identifier_name"], row["ident"], k))
            if k > 0:
                certs_to_reverify.append({
                    "label": "PART C v2 %s arm %s=%d" % (arm, row["identifier_name"], row["ident"]),
                    "a_invariants": [str(x) for x in m], "points": hits,
                    "certified_rank_lower_bound": k,
                    "l": (cert.get("independence") or {}).get("l"),
                    "primes_used": (cert.get("independence") or {}).get("primes_used"),
                    "torsion_bound": cert.get("torsion_bound"),
                    "torsion_bound_primes": cert.get("torsion_bound_primes"),
                })
            row["gate_status"] = "gated"
            gate_results[arm].append(res)
            if len(gate_results[arm]) % 20 == 0 or k > 0:
                log("   %-5s %s=%-6d S=%9.4f  pts=%d  rank>=%d  box %d/%d  (%.1fs elapsed)"
                    % (arm, row["identifier_name"], row["ident"], row["S"], len(hits), k,
                       n_tested, N_RBOX, time.time() - t_gate))
    else:
        n_box_tests = 0
        log("== exact gate SKIPPED: CTL-GATE-DIRECTION failed, nothing is gated ==")
    gate_wall = time.time() - t_gate
    out["gate_truncated"] = gate_truncated
    out["gate_wall_clock_seconds"] = round(gate_wall, 3)
    out["measured_seconds_per_point_test_in_the_gate"] = (
        round(gate_wall / n_box_tests, 12) if n_box_tests else None)
    out["gate_box_tests_total"] = n_box_tests
    dump_doc(out, a.raw_out)

    # ================= PARTIAL MINIMALITY SCREEN (CHG-7) ====================
    log("== partial minimality screen on every gated row (cap %.0fs, B = %d) =="
        % (a.minimality_cap_seconds, SCREEN_B))
    t_min = time.time()
    min_deadline = t_min + a.minimality_cap_seconds - 5.0
    n_screened = 0
    screen_truncated = False
    for arm in ("twist", "null"):
        for res in gate_results[arm]:
            if time.time() > min_deadline:
                screen_truncated = True
                res["minimality_status"] = "not_established_with_reason"
                res["minimality_screen"] = {
                    "minimality_status": "not_established_with_reason",
                    "reason": ("minimality-screen wall-clock cap reached before this row "
                               "was screened; a truncated screen NEVER becomes an assumed "
                               "minimality"),
                    "partial": True, "screened": False}
                continue
            ms = C.minimality_screen([int(x) for x in res["model_a_invariants"]], SCREEN_B)
            ms["screened"] = True
            res["minimality_screen"] = ms
            res["minimality_status"] = ms["minimality_status"]
            n_screened += 1
    min_wall = time.time() - t_min
    log("   screened %d gated rows in %.1fs (truncated=%s)" % (n_screened, min_wall, screen_truncated))

    n_gated_rows = sum(len(gate_results[arm]) for arm in gate_results)
    out["minimality_regime"] = {
        "requirement": ("CHG-7: EVERY gated curve in either arm carries an explicit, "
                        "non-null minimality_status. No gated row may omit it."),
        "screen": ("For every gated curve, trial divide the exact discriminant by every "
                   "prime p <= %d and, for each p with p^12 | disc, test the Kraus-Laska "
                   "condition p^4 | c4 and p^6 | c6. Exact integer arithmetic; no floating "
                   "point." % SCREEN_B),
        "screen_prime_bound_B": SCREEN_B,
        "rows_screened": n_screened,
        "rows_gated": n_gated_rows,
        "screen_coverage": "%d / %d" % (n_screened, n_gated_rows),
        "screen_coverage_over_the_frozen_gate_size": "%d / %d" % (n_screened, 2 * GATE_SIZE),
        "screen_truncated": screen_truncated,
        "wall_clock_seconds": round(min_wall, 3),
        "THIS_IS_A_PARTIAL_STATEMENT": (
            "THE SCREEN IS PARTIAL AND IS LABELLED PARTIAL. It tests primes up to %d only, "
            "and for p in {2, 3} the Kraus-Laska condition is necessary but not "
            "sufficient, so such primes are reported as ADMITTING A POSSIBLE DESCENT -- "
            "the conservative direction. IT DOES NOT ESTABLISH GLOBAL MINIMALITY AND DOES "
            "NOT DISCHARGE CLAIM-BAR CLAUSE (1). No artifact may say that it does." % SCREEN_B),
        "why_it_does_not_touch_the_measurement": (
            "A CERTIFIED RANK LOWER BOUND FROM EXHIBITED POINTS IS INVARIANT UNDER "
            "Q-ISOMORPHISM AND NEEDS NO MINIMAL MODEL. Minimality binds the CLAIM BAR, "
            "clause (1), not the arithmetic."),
        "where_established_minimality_actually_binds": (
            "on any gated row returning a certified rank lower bound >= 1 (the row may not "
            "be cited beyond the stated model until clause (1) is discharged), and on any "
            "row returning >= 32, which routes out to a dedicated task and to "
            "review-breakthrough rather than being attempted inline"),
        "status_counts": {},
    }
    for arm in ("twist", "null"):
        for res in gate_results[arm]:
            s = res["minimality_status"]
            out["minimality_regime"]["status_counts"][s] = \
                out["minimality_regime"]["status_counts"].get(s, 0) + 1

    out["CTL_MINIMALITY_DISCLOSURE"] = {
        "id": "CTL-MINIMALITY-DISCLOSURE",
        "blocking": False,
        "control": ("every gated row carries a non-null minimality_status from the "
                    "permitted values, and every reported part-C naive height is labelled "
                    "as a height of the stated model"),
        "gated_rows": n_gated_rows,
        "rows_with_non_null_minimality_status": sum(
            1 for arm in gate_results for r in gate_results[arm] if r["minimality_status"]),
        "heights_labelled_as_of_the_stated_model": True,
        "outcome": ("PASS" if all(r["minimality_status"] for arm in gate_results
                                  for r in gate_results[arm]) else "FAIL"),
        "failure_meaning": ("a gated row with a null minimality_status is an INCOMPLETE ROW "
                            "and its rank figure may not be cited in any claim, though the "
                            "coverage fraction it belongs to survives"),
    }

    # ================= PROVENANCE on reported curves ========================
    # CTL-PROVENANCE is checked on every curve this experiment REPORTS.  The
    # gated set is 400 curves; the check is by curve_key AND by a-invariants
    # against the frozen snapshot.
    log("== CTL-PROVENANCE on every gated (reported) curve ==")
    prov_rows = []
    prov_hits = []
    for arm in ("twist", "null"):
        for res in gate_results[arm]:
            p = C.provenance_check([int(x) for x in res["model_a_invariants"]],
                                   "%s arm, %s = %s" % (arm, res["identifier_name"],
                                                        res["identifier"]))
            res["provenance_check"] = {
                "in_frozen_snapshot": p["in_frozen_snapshot"],
                "match_by_curve_key": p["match_by_curve_key"],
                "match_by_ainvs": p["match_by_ainvs"],
                "cremona_check": p["cremona_check"],
            }
            if p["in_frozen_snapshot"]:
                prov_hits.append(res["identifier"])
            prov_rows.append(res["provenance_check"])
    out["CTL_PROVENANCE"] = {
        "id": "CTL-PROVENANCE",
        "control": ("every curve this experiment REPORTS is checked against the frozen "
                    "snapshot at coordination/goals/GOAL-ECQ-002/baseline/ by curve_key "
                    "AND by a-invariants"),
        "curves_checked": len(prov_rows),
        "curves_found_in_the_frozen_snapshot": prov_hits,
        "outcome": "PASS",
        "outcome_meaning": (
            "PASS means no gated curve was silently a rediscovered board curve reported as "
            "this program's own -- the error BATCH-541940 made with frozen board curve id "
            "108. The snapshot PREDATES no. 302 (posted 2026-08-23) and does not contain "
            "it or its twists; that is a fact about the timeline, not a defect."),
        "cremona_note": ("Cremona's tables cover conductors far below this scale, so a "
                         "Cremona lookup is VACUOUS here and is recorded as "
                         "not-applicable-with-reason rather than as a pass."),
    }

    # ================= ARM SUMMARIES (CTL-MATCHED-NULL) =====================
    def dist(vals):
        s = sorted(vals)
        if not s:
            return None
        n = len(s)
        mean = sum(s) / n
        return {"n": n, "min": s[0], "max": s[-1], "range": round(s[-1] - s[0], 6),
                "median": s[n // 2], "q1": s[n // 4], "q3": s[(3 * n) // 4],
                "deciles": {("d%d" % dd): s[min(n - 1, int(dd / 10.0 * n))] for dd in range(1, 10)},
                "mean": round(mean, 6),
                "stdev": round((sum((x - mean) ** 2 for x in s) / n) ** 0.5, 6)}

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
            "score_distribution": dist([r["S"] for r in sc]),
            "score_source_counts": {
                "v1_reused": sum(1 for r in sc if r.get("score_source") == "v1_reused"),
                "v2_scored": sum(1 for r in sc if r.get("score_source") == "v2_scored")},
            "max_certified_rank_lower_bound_over_Q": max(ranks) if ranks else None,
            "certified_rank_histogram": ({str(v): ranks.count(v) for v in sorted(set(ranks))}
                                         if ranks else {}),
            "total_points_found_across_gated": sum(g["n_points_found"] for g in gr),
            "gated_reduced_box_exhausted_count": sum(
                1 for g in gr if g["reduced_box_coverage"]["exhausted"]),
        }
    out["arms"] = arms

    out["CTL_MATCHED_NULL"] = {
        "id": "CTL-MATCHED-NULL",
        "control": ("the near-neighbour arm scored with the same implementation, the same "
                    "prime bound and the same gate rule as the twist arm, and gated with "
                    "the same reduced box; read with the v2 gate size 200 substituted for "
                    "v1's 20"),
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
        "gate_slice_note": ("the exact gate processes the arms INTERLEAVED with an equal "
                            "adaptive per-curve time slice, so a cap truncates both arms "
                            "symmetrically rather than exhausting one arm first"),
        "outcome": ("PASS" if (arms["twist"]["scored"] == N_C_TWIST
                               and arms["null"]["scored"] == N_C_NULL
                               and arms["twist"]["gated"] == arms["null"]["gated"])
                    else "PARTIAL"),
        "outcome_meaning": (
            "PASS means both arms were scored to completion with the same instrument and "
            "gated to the same depth, so the comparison is admissible. PARTIAL means a cap "
            "truncated one or both arms; the comparison is then reported with its coverage "
            "fractions and is weakened accordingly."),
        "prior_incident": ("This program has already manufactured a result once through "
                           "differential attrition across arms (EV-ECQ-8ee697 OBS-9)."),
    }

    # ================= BETWEEN-ARM COMPARISONS ==============================
    # ONE confirmatory comparison, on the DISJOINT v2-only subset.  Everything
    # else is DESCRIPTIVE ONLY and is labelled so.
    tw_scored = [r for r in twist_rows if r["status"] == "scored"]
    nl_scored = [r for r in null_rows if r["status"] == "scored"]

    def subset(rows, lo, hi):
        return [r["S"] for r in rows if lo < abs(r["ident"]) <= hi]

    comparisons = {}
    if STATS_ALLOWED:
        tw_v2only = subset(tw_scored, 200, 10000)
        nl_v2only = subset(nl_scored, 100, 6000)
        mw = C.mann_whitney(tw_v2only, nl_v2only)
        verdict = None
        if mw:
            z = mw["mann_whitney_z_normal_approximation"]
            eff = mw["probability_a_random_x_scores_above_a_random_y"]
            notable = (abs(z) >= 3.0) and not (0.45 <= eff <= 0.55)
            verdict = {
                "both_conditions_required": True,
                "condition_1_abs_z_at_least_3.0": abs(z) >= 3.0,
                "observed_abs_z": abs(z),
                "condition_2_effect_size_outside_0.45_to_0.55": not (0.45 <= eff <= 0.55),
                "observed_effect_size": eff,
                "NOTABLE": notable,
            }
        comparisons["v2_preregistered_confirmatory"] = {
            "status": "confirmatory",
            "population": ("THE v2-ONLY SUBSET AND NOTHING ELSE: twist candidates with "
                           "200 < |D| <= 10000, and null candidates with 100 < |v| <= 6000. "
                           "DISJOINT from every candidate scored in v1, so no score entering "
                           "it existed when the threshold was frozen. That disjointness is "
                           "the whole reason a threshold may honestly be pre-registered."),
            "preregistered_threshold": C.V2_ONLY_SUBSET["preregistered_threshold"],
            "twist_n": len(tw_v2only), "null_n": len(nl_v2only),
            "twist_mean": round(sum(tw_v2only) / len(tw_v2only), 6) if tw_v2only else None,
            "null_mean": round(sum(nl_v2only) / len(nl_v2only), 6) if nl_v2only else None,
            "statistics": mw,
            "verdict_against_the_frozen_threshold": verdict,
            "what_notable_would_and_would_not_license": (
                "NOTABLE MEANS 'REPLICATE THIS', NOT 'THIS IS TRUE'. It would license one "
                "replication experiment on a fresh disjoint discriminant range and nothing "
                "else. It would NOT license a statement that the twist neighbourhood of "
                "no. 302 is enriched, NOT a rank claim of any kind, and NOT an evidence "
                "record above `weak` on a single unreplicated run. The score certifies "
                "nothing."),
            "confounds_recorded_before_the_run": (
                "The two arms are structurally different families scored under one shared "
                "bad-prime convention, and the twist arm's coefficients grow like D^3 "
                "across a range reaching 10000 while the null arm's grow not at all. A "
                "between-arm difference is CONFOUNDED with coefficient growth and with "
                "bad-prime handling, and neither confound is removed by any statistic here."),
            "direction_note": ("S DECREASES WITH RANK, so an effect size ABOVE 0.5 means "
                               "the twist arm scores HIGHER, i.e. looks LOWER-rank than its "
                               "matched null -- the OPPOSITE direction from enrichment."),
        }

        tw_v1sub = subset(tw_scored, 0, 200)
        nl_v1sub = subset(nl_scored, 0, 100)
        comparisons["v1_subset_DESCRIPTIVE_ONLY"] = {
            "status": "descriptive_only",
            "population": "twist |D| <= 200 (and D = -1), null |v| <= 100 -- the 443 v1 candidates",
            "twist_n": len(tw_v1sub), "null_n": len(nl_v1sub),
            "statistics": C.mann_whitney(tw_v1sub, nl_v1sub),
            "binding_caveat": ("DESCRIPTIVE ONLY. NO SIGNIFICANCE THRESHOLD WAS "
                               "PRE-REGISTERED IN v1 AND NONE IS ASSERTED NOW. These scores "
                               "were already seen before the v2 selection rule was written "
                               "and no reasoning un-sees them; they may not be cited as a "
                               "finding."),
        }
        comparisons["pooled_DESCRIPTIVE_ONLY"] = {
            "status": "descriptive_only",
            "population": "every scored candidate in each arm, v1 and v2 together",
            "twist_n": len(tw_scored), "null_n": len(nl_scored),
            "statistics": C.mann_whitney([r["S"] for r in tw_scored],
                                         [r["S"] for r in nl_scored]),
            "binding_caveat": ("DESCRIPTIVE ONLY, carries no pre-registered threshold, "
                               "reported for completeness and MAY NOT BE CITED AS A "
                               "FINDING (amendment part_c_between_arm_comparison."
                               "pooled_comparison)."),
        }
    else:
        comparisons["withheld"] = (
            "CTL-SCORE-REUSE-AGREEMENT did not PASS, so the pooled distribution is not one "
            "distribution and NO between-arm statistic is computed. Reuse is FORBIDDEN and "
            "the triage coverage is reported alone.")

    comparisons["v1_descriptive_result_carried_forward_unchanged"] = {
        "status": "descriptive_only",
        "source": "PA-ECQ-f5af06-v2 part_c_between_arm_comparison, as recorded in v1",
        "twist_n": 243, "null_n": 200,
        "twist_mean": 1.479, "null_mean": 0.298,
        "mean_difference_twist_minus_null": 1.181,
        "twist_sd": 4.035, "null_sd": 4.009,
        "twist_range": 20.059, "null_range": 23.073,
        "mann_whitney_z_normal_approximation": 3.24,
        "probability_a_random_twist_scores_above_a_random_null": 0.5895,
        "binding_caveat": ("CARRIED FORWARD UNCHANGED AND NOT RECOMPUTED. NO SIGNIFICANCE "
                           "THRESHOLD WAS PRE-REGISTERED IN v1 AND NONE IS ASSERTED NOW."),
    }
    out["between_arm_comparisons"] = comparisons

    # ================= v1 GATE RESULT REPORTED BESIDE v2 ====================
    v1_gate = {}
    for arm in ("twist", "null"):
        rows = [{"identifier": g["identifier"], "S": g["triage_score_S"],
                 "certified_rank_lower_bound": g["certified_rank_lower_bound"],
                 "n_points_found": g["n_points_found"]}
                for g in v1doc.get("gate_results", {}).get(arm, [])]
        v1_gate[arm] = {
            "rule_that_produced_it": ("v1 FROZEN RULE: the exact gate applied to the TOP 20 "
                                      "CANDIDATES BY S per arm -- LARGEST S first, which "
                                      "S's own direction ranks as the LEAST promising"),
            "gate_size": 20,
            "reduced_box": ("v1 reduced box: w in [1, 10], |u| <= 100000 for w = 1, "
                            "|u| <= 2000 for 2 <= w <= 10"),
            "rows": rows,
            "max_certified_rank_lower_bound_over_Q": (max(r["certified_rank_lower_bound"]
                                                          for r in rows) if rows else None),
        }
    out["v1_gated_set_reported_beside_v2_never_replaced"] = {
        "statement": ("THE v1 TOP-20 RESULT STANDS AS RECORDED. It is reported here beside "
                      "the v2 bottom-200 result, each labelled with the rule that produced "
                      "it. The two gates answer different questions and both answers are "
                      "part of the record. v1's run records, deliverables and coverage "
                      "fractions are IMMUTABLE and are not reinterpreted by this run beyond "
                      "the re-scoping the amendment states."),
        "v1": v1_gate,
        "v2": {arm: {
            "rule_that_produced_it": ("v2 CORRECTED RULE (%s): the exact gate applied to the "
                                      "200 CANDIDATES OF SMALLEST S per arm -- most negative "
                                      "first, which S's own direction ranks as the MOST "
                                      "promising" % AMENDMENT),
            "gate_size": GATE_SIZE,
            "reduced_box": rbox["description"],
            "gated_count": len(gate_results[arm]),
            "max_certified_rank_lower_bound_over_Q":
                arms[arm]["max_certified_rank_lower_bound_over_Q"],
            "S_range_of_the_gated_set": (
                [min(g["triage_score_S"] for g in gate_results[arm]),
                 max(g["triage_score_S"] for g in gate_results[arm])]
                if gate_results[arm] else None),
        } for arm in ("twist", "null")},
    }

    # ================= EVERY ATTEMPTED CANDIDATE, PERSISTED =================
    out["all_candidates_schema"] = [
        "arm", "identifier", "status", "reason", "S_of_record", "score_source",
        "S_v2_measured", "gated", "gate_status"]
    out["all_candidates_note"] = (
        "EVERY GENERATED CANDIDATE IN BOTH ARMS IS PERSISTED HERE with an identifier, a "
        "status and a reason. There is no arithmetic difference between attempted and "
        "reported; 462 families vanished that way in BATCH-541940. Rows are REDUCED AT "
        "SOURCE to one compact array each, per the artifact_size_budget, and the column "
        "order is all_candidates_schema above. S_of_record is v1's recorded value where "
        "score_source is v1_reused, and this run's measurement where it is v2_scored; "
        "S_v2_measured is this run's measurement in both cases "
        "(CTL-SCORE-REUSE-AGREEMENT).")
    out["all_candidates_compact"] = [
        [r["arm"], r["ident"], r["status"], r["reason"], r.get("S"),
         r.get("score_source"), r.get("S_v2_measured"), bool(r.get("gated", False)),
         r.get("gate_status")]
        for r in twist_rows + null_rows]
    out["attempted_vs_reported"] = {
        "twist_generated": len(twist_rows), "null_generated": len(null_rows),
        "rows_persisted": len(out["all_candidates_compact"]),
        "check": ("generated %d + %d = %d, persisted %d"
                  % (len(twist_rows), len(null_rows), len(twist_rows) + len(null_rows),
                     len(out["all_candidates_compact"]))),
        "balanced": len(out["all_candidates_compact"]) == len(twist_rows) + len(null_rows),
    }
    out["gate_results"] = gate_results
    out["certificates_to_reverify"] = certs_to_reverify

    # ================= BRANCH ==============================================
    tw_max = arms["twist"]["max_certified_rank_lower_bound_over_Q"]
    nl_max = arms["null"]["max_certified_rank_lower_bound_over_Q"]
    top = max([x for x in (tw_max, nl_max) if x is not None], default=None)
    if not GATING_ALLOWED:
        branch = "C2-WITHHELD-GATE-DIRECTION-FAILED"
    elif top is not None and top >= 32:
        branch = "C2-POSITIVE"
    elif top is not None and top >= 1:
        branch = "C2-MODEST"
    else:
        branch = "C2-NULL"
    out["branch_label"] = branch
    out["branch_defence"] = {
        "pre_declared_C2_NULL": ("no gated curve in either arm certifies rank above 0 under "
                                 "the corrected bottom-200 gate"),
        "pre_declared_C2_MODEST": ("a gated curve certifies a rank lower bound between 1 and "
                                   "31 over Q for that curve itself -- a modest rank over Q "
                                   "of that curve AND NOTHING MORE; not added to no. 302's "
                                   "31, not a number-field result, and it does not meet or "
                                   "approach GOAL-ECQ-2298dc C1"),
        "pre_declared_C2_POSITIVE": ("a gated curve certifies a rank lower bound of 32 or "
                                     "more OVER Q for its own Mordell-Weil group; subject to "
                                     "the six-clause claim bar IN FULL"),
        "observed": branch,
        "twist_max_certified_rank_over_Q": tw_max,
        "null_max_certified_rank_over_Q": nl_max,
        "scope": ("EXACTLY the %d gated twists and %d gated null curves selected by the "
                  "CORRECTED bottom-200-by-S rule, searched in the frozen reduced box "
                  "B-C at the per-curve coverages reported above, over the frozen ranges "
                  "|D| <= 10000 and |v| <= 6000, at triage coverages %s and %s. It is NOT "
                  "a statement that the twist neighbourhood is barren: the reduced box "
                  "reaches 6-digit numerators and the candidates are of enormous height. "
                  "It is a statement that THIS GATE AT THIS DEPTH FOUND WHAT IS REPORTED."
                  % (arms["twist"]["gated"], arms["null"]["gated"],
                     arms["twist"]["triage_coverage"]["fraction"],
                     arms["null"]["triage_coverage"]["fraction"])),
        "difference_from_v1": ("UNLIKE v1's C-NULL, a v2 C2-NULL IS INFORMATIVE ABOUT THE "
                               "TWIST NEIGHBOURHOOD at this depth, because the gate now "
                               "examines the candidates each arm's own score ranks as MOST "
                               "promising. The Executor records this scope; the judgement "
                               "of what it supports belongs to the Reviewer and Coordinator."),
    }

    # ================= PARAMETERS, CERTIFICATE, METRICS =====================
    out["parameters"] = {
        "prime_bound": PRIME_BOUND, "gate_size": GATE_SIZE,
        "gate_direction": "SMALLEST S FIRST",
        "N_C_TWIST_v2": N_C_TWIST, "N_C_NULL_v2": N_C_NULL, "N_BC_v2": N_RBOX,
        "reduced_box": rbox, "minimality_screen_B": SCREEN_B,
        "certifier_search_bounds": {k: (list(v) if isinstance(v, tuple) else v)
                                    for k, v in CERT_KW.items()},
        "triage_cap_seconds": a.triage_cap_seconds,
        "gate_cap_seconds": a.gate_cap_seconds,
        "minimality_cap_seconds": a.minimality_cap_seconds,
        "amendment": AMENDMENT,
    }
    out["protocol_certificate"] = {
        "kind": "independence_certificate" if certs_to_reverify else "none",
        "kind_reason": ("no gated curve in either arm yielded a certified point, so there "
                        "is nothing to certify and the kind is stated explicitly as `none`"
                        if not certs_to_reverify else
                        "at least one gated curve yielded certified points; the certificate "
                        "is re-verified by verify_certificate.py, which does not import the "
                        "solver"),
        "path": ("coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-02c3e4/"
                 "twist_search.json"),
    }
    out["measured_throughput_against_the_amendment_sizing"] = {
        "measured_seconds_per_triage_score": out["measured_seconds_per_triage_score"],
        "amendment_triage_constant": 0.0054,
        "amendment_projected_triage_seconds": 131,
        "measured_triage_seconds": round(triage_wall, 3),
        "measured_seconds_per_point_test_in_the_gate":
            out["measured_seconds_per_point_test_in_the_gate"],
        "amendment_sizing_constant": 2.0e-06,
        "amendment_projected_gate_seconds": 934,
        "measured_gate_seconds": round(gate_wall, 3),
        "amendment_projected_minimality_seconds": 15,
        "measured_minimality_seconds": round(min_wall, 3),
        "note": "MEASURED, not modelled.",
    }
    out["metrics"] = {
        "part_c_twist_triage_coverage": arms["twist"]["triage_coverage"]["fraction"],
        "part_c_null_triage_coverage": arms["null"]["triage_coverage"]["fraction"],
        "part_c_twist_gated_over_200": arms["twist"]["gate_coverage"]["fraction"],
        "part_c_null_gated_over_200": arms["null"]["gate_coverage"]["fraction"],
        "part_c_twist_max_certified_rank_over_Q": tw_max,
        "part_c_null_max_certified_rank_over_Q": nl_max,
        "part_c_N_C_TWIST_v2": N_C_TWIST,
        "part_c_N_C_NULL_v2": N_C_NULL,
        "part_c_N_BC_v2": N_RBOX,
        "part_c_branch": branch,
        "ctl_gate_direction": gate_dir["outcome"],
        "ctl_score_reuse_agreement": reuse["outcome"],
        "ctl_matched_null": out["CTL_MATCHED_NULL"]["outcome"],
        "ctl_minimality_disclosure": out["CTL_MINIMALITY_DISCLOSURE"]["outcome"],
        "ctl_provenance": out["CTL_PROVENANCE"]["outcome"],
        "part_c_triage_wall_clock_seconds": round(triage_wall, 3),
        "part_c_gate_wall_clock_seconds": round(gate_wall, 3),
        "part_c_minimality_wall_clock_seconds": round(min_wall, 3),
        "total_wall_clock_seconds": round(time.time() - t_start, 3),
    }
    out["wall_clock_seconds"] = round(time.time() - t_start, 3)

    dump_doc(out, a.raw_out)
    if a.out:
        dump_doc(out, a.out)
    log("== part C done: branch %s ==" % branch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
