#!/usr/bin/env python3
"""Assemble comparison.json (the CP-2 / CP-3 / CP-4 deliverable of
TASK-20260926-f50294) from the outputs of cp1_verify.py, check_blind_certs.py,
cp2_compare.py, cp2_floor_ceiling.py and third_check_m4_witnesses.py, and add
the ambiguity table (every re-deriver and every J1 ambiguity set against the
run's resolution). Stdlib only.

Usage: python3 assemble_comparison.py <task_dir>
"""
import hashlib
import json
import os
import sys
from collections import Counter

AMBIGUITIES = [
    # ------------------------------------------------ re-deriver (TASK-20260926-f0736e)
    {"id": "f0736e AMB-1", "topic": "column order: (-degree, bitmask ascending) used for every matrix instead of descending degrevlex",
     "run_resolution": "engine closure.column_order; the specification equates the ann-v1 order with closure.column_order(4, 20), and J1 (its AMB-10) self-tested that (-degree, bitmask ascending) equals descending degrevlex with the constant last",
     "same_as_run": True, "could_change_a_compared_item": "no: rank and 1-membership are order-free; dims_by_deg needs only a degree-graded order, which both use",
     "observed": "every M / W / R' item agrees on every system"},
    {"id": "f0736e AMB-2", "topic": "W_D dims list runs to the confirming W^(i*+1); fixpoint index = first i with dim W^(i+1) = dim W^(i)",
     "run_resolution": "closures.jsonl.gz lists dim W^(0..i*) only (records; not stated in trial-plan or implementation.md)",
     "same_as_run": False, "could_change_a_compared_item": "encoding only; the fixpoint index is defined identically",
     "observed": "compared with the encoding applied: 90/90 agree; the extra entry is re-deriver-only and equals the last run entry on 90/90"},
    {"id": "f0736e AMB-3", "topic": "iterate to the dimension fixpoint after 1 appears",
     "run_resolution": "records show iteration continued to the fixpoint (iterations_to_fixpoint recorded after one_first_iteration)",
     "same_as_run": True, "could_change_a_compared_item": "fixpoint index and final dim if one side stopped at 1; in this pool W^(1) is already all of B_<=4 wherever 1 appears, so the two readings cannot be told apart here (ceiling)",
     "observed": "agree 90/90"},
    {"id": "f0736e AMB-4", "topic": "route 2 to s: exact case analysis of S_3 as a quadratic in x_2",
     "run_resolution": "oracle A (O(2^l) root finding per EXP-CERTBIN-4e92d7 C-ORACLE) and oracle B (exhaustive 2^20); different algorithm, same quantity",
     "same_as_run": True, "could_change_a_compared_item": "s", "observed": "route 1 90/90 and route 2 60/60 agree with the run's s"},
    {"id": "f0736e AMB-5", "topic": "hex without 0x prefix",
     "run_resolution": "E_hex and L_hex are lowercase hex strings without 0x (J1 AMB-1: canonical form 2100/2100)", "same_as_run": True,
     "could_change_a_compared_item": "no", "observed": "E_hex equal on 90/90 (as integers)"},
    {"id": "f0736e AMB-6", "topic": "mu as ascending index list; node ids 0..N-1 in order",
     "run_resolution": "run certificates use the same form (J1 AMB-6, AMB-7: all 1200 wdag-v1 conform)", "same_as_run": True,
     "could_change_a_compared_item": "no", "observed": "the comparator's checker requires only unique ids; no certificate distinguishes the readings"},
    {"id": "f0736e AMB-7", "topic": "rc_b step (1): kernel dim > 1 -> the lowest unit vector e_k in the kernel (the text names e_18 for N-ELL19)",
     "run_resolution": "c_rule 'kernel vector (dim 1)' on all 250 N-ELL19 records; the kernel is 1-dimensional on every pool system of every arm with an ell",
     "same_as_run": "not exercised", "could_change_a_compared_item": "c, ell, j* and every R' item, but only if a kernel of dim > 1 contained e_k with k < 18; no such kernel occurs in the run",
     "observed": "kernel dim and c agree on 80/80"},
    {"id": "f0736e AMB-8", "topic": "rc_b step (3) (ell linear part zero): R' fields null, ell_route still computed",
     "run_resolution": "no step-3 case in the run's pool keys", "same_as_run": "not exercised", "could_change_a_compared_item": "no case", "observed": "all 80 applicable pool systems substituted on both sides"},
    {"id": "f0736e AMB-9", "topic": "ell_route computed for every input with an ell (both kinds)",
     "run_resolution": "specification derived_per_instance: 'for S_3 and N-CONV19: ell_route'; the run records null for N-ELL19",
     "same_as_run": False, "could_change_a_compared_item": "no disagreement possible; 10 N-ELL19 values are re-deriver-only",
     "observed": "ell_route agree 70/70 where both computed"},
    {"id": "f0736e AMB-10", "topic": "c_k = Tr(t^k / x_R^2) check null for explicit inputs",
     "run_resolution": "the run records C-ELL_ok for N-CONV19 (it knows the slot's x_R)", "same_as_run": False,
     "could_change_a_compared_item": "no; 10 N-CONV19 values are run-only", "observed": "agree 60/60 on curve-kind systems"},
    {"id": "f0736e AMB-11", "topic": "ell * B_<=3 = span of ell * m over the 1351 monomials of degree <= 3",
     "run_resolution": "not stated in trial-plan-v1.json or implementation.md; by D-2 any spanning set of ell * B_<=3 gives the same answer",
     "same_as_run": "equivalent", "could_change_a_compared_item": "ell_route",
     "observed": "ell_route agree 70/70; the re-deriver's direct space dimension equals rank R'_4 + 1160 on 80/80 (D-2 space identity)"},
    {"id": "f0736e AMB-12", "topic": "Q7 (W'_4) wherever the substitution applied",
     "run_resolution": "W'_4 only on the C-T4 subsets (every N-ELL19, first 50 S3-U400, first 50 N-CONV19 unsat, S3-U400 not refuted)", "same_as_run": False,
     "could_change_a_compared_item": "no disagreement possible; 20 values (15 F-RANDX19, 5 S3-SAT100) are re-deriver-only", "observed": "W'_4 items agree 60/60 where both computed"},
    {"id": "f0736e AMB-13", "topic": "skeleton / seal ordering", "run_resolution": "procedural; no run counterpart", "same_as_run": "n/a", "could_change_a_compared_item": "no", "observed": "-"},
    {"id": "f0736e AMB-14", "topic": "brute-force self-test semantics", "run_resolution": "procedural; C-SELF (viii) is the run's analogue", "same_as_run": "n/a", "could_change_a_compared_item": "no", "observed": "-"},
    {"id": "f0736e AMB-15", "topic": "dims_by_deg of R'_4 and W'_4 in the 19 relabelled variables",
     "run_resolution": "the run records 19-variable cumulative profiles (e.g. [1, 20, 191, 1160, 5036])", "same_as_run": True,
     "could_change_a_compared_item": "dims_by_deg(R'_4), dims_by_deg(W'_4)", "observed": "agree 80/80 and 60/60"},
    {"id": "f0736e AMB-16", "topic": "wdag-v1 construction: collapse per variable",
     "run_resolution": "iteration-0 one-node form; prefix-shared chains where ell_route holds; otherwise the recommended grouped construction (implementation.md). The construction is not binding",
     "same_as_run": False, "could_change_a_compared_item": "no; validity is construction-independent (D-6)",
     "observed": "run: 2 nodes (1198) or 3 (2), one prods level, j = 0 (or 0 and 1); blind: 2 nodes, one prod, j = 0; all valid"},
    # ------------------------------------------------ J1 (TASK-20260926-401771)
    {"id": "401771 AMB-1", "topic": "E_sha256 preimage", "run_resolution": "trial-plan executor_interpretations: sha256 of the compact JSON list of the 19 lowercase E_hex strings", "same_as_run": True,
     "could_change_a_compared_item": "E_sha256 only", "observed": "J1 E_sha256 match 2100/2100"},
    {"id": "401771 AMB-2", "topic": "bit order of a listed solution (bit j = v_j)", "run_resolution": "not stated; J1's reading makes all 776 listed solutions satisfy and each list equal the full solution set", "same_as_run": True,
     "could_change_a_compared_item": "no compared item", "observed": "-"},
    {"id": "401771 AMB-3", "topic": "x_1 = bits 0..9, x_2 = bits 10..19 of the assignment", "run_resolution": "the specification text", "same_as_run": True, "could_change_a_compared_item": "s", "observed": "s agree 2100/2100"},
    {"id": "401771 AMB-4", "topic": "flat-v1 sort key", "run_resolution": "run flats sorted by (mu tuple, k)", "same_as_run": True, "could_change_a_compared_item": "no (the sum is order-free)", "observed": "-"},
    {"id": "401771 AMB-5", "topic": "flat-v1 counting only at max |mu| <= 2", "run_resolution": "run verifier counts = false on all 1200 flats (max |mu| = 3)", "same_as_run": True,
     "could_change_a_compared_item": "MR19-1, MR19-3 counting", "observed": "counts_toward_W4 agree 2400/2400"},
    {"id": "401771 AMB-6", "topic": "node id = list position", "run_resolution": "run certificates conform", "same_as_run": True, "could_change_a_compared_item": "no", "observed": "-"},
    {"id": "401771 AMB-7", "topic": "mu strictly increasing in 0..19", "run_resolution": "run certificates conform", "same_as_run": True, "could_change_a_compared_item": "no", "observed": "-"},
    {"id": "401771 AMB-8", "topic": "degrees after multilinear reduction; deg(0) = -1", "run_resolution": "run verifier 'own multilinear arithmetic' (code not inspected); the re-deriver and the comparator read the same", "same_as_run": "not inspected; verdicts agree",
     "could_change_a_compared_item": "wdag-v1 verdicts (rule (c) is load-bearing: every child has formal degree 4 and degree 3 in B)", "observed": "verified agree 2400/2400"},
    {"id": "401771 AMB-9", "topic": "prods depth convention", "run_resolution": "the run records n_nodes / n_prods, not depth", "same_as_run": "n/a", "could_change_a_compared_item": "descriptive only", "observed": "-"},
    {"id": "401771 AMB-10", "topic": "ann-v1 coordinate order: bitmask bit i = v_i; constant last", "run_resolution": "the engine's closure.column_order(4, 20); the run's 15 ann-v1 satisfy (A1) under J1's reading",
     "same_as_run": True, "could_change_a_compared_item": "ann-v1 verdicts (completeness only; soundness is order-free)", "observed": "ann-v1 verified agree 15/15; 25/25 blind ann-v1 valid under the comparator's identical reading"},
    {"id": "401771 AMB-11", "topic": "M_4 row convention", "run_resolution": "the specification (4e92d7 convention)", "same_as_run": True, "could_change_a_compared_item": "no ((A1) is order-free)", "observed": "-"},
    {"id": "401771 AMB-12", "topic": "(A2) basis = null space of L restricted to the degree <= 3 coordinates", "run_resolution": "run rule text: 'own elimination for S cap B_{<=3}' (code not inspected)",
     "same_as_run": "consistent", "could_change_a_compared_item": "ann-v1 verdicts; J8 shows the lenient alternative (filtering a basis of S) is unsound", "observed": "verified agree 15/15"},
    {"id": "401771 AMB-13..16", "topic": "negative-control conventions", "run_resolution": "C-VERIFIER types (a)-(e3)", "same_as_run": "n/a", "could_change_a_compared_item": "no", "observed": "J1 215/215 rejected; run C-VERIFIER pass"},
    {"id": "401771 AMB-17", "topic": "N-CONV19 slot i carries S3-U400:i's x_R", "run_resolution": "trial-plan: 'slot i = S3-U400:i'", "same_as_run": True, "could_change_a_compared_item": "no", "observed": "-"},
    {"id": "401771 AMB-18", "topic": "N-ELL19 row 18 = ell_lin + c", "run_resolution": "the specification draw_rule", "same_as_run": True, "could_change_a_compared_item": "no", "observed": "J1 250/250"},
    {"id": "401771 AMB-19", "topic": "N-AFF19 derived support constraint", "run_resolution": "no run counterpart (J1-derived check)", "same_as_run": "n/a", "could_change_a_compared_item": "no", "observed": "J1 250/250"},
    {"id": "401771 AMB-20", "topic": "U from E^0 and E^j", "run_resolution": "support.json (C-SUPPORT)", "same_as_run": True, "could_change_a_compared_item": "no compared item",
     "observed": "record-level: run support.json U_size 2291, S_L_size 391, per-row sizes and tau equal J1's vc2 context"},
    {"id": "401771 AMB-21", "topic": "1 in rowspace iff the constant column is a pivot; witness checked by parity", "run_resolution": "the specification ('1 in R_D iff the constant column is a pivot column')", "same_as_run": True,
     "could_change_a_compared_item": "1 in R_4", "observed": "J1 one/rank/dims_by_deg(M_4) agree with the run 2100/2100"},
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    td = sys.argv[1]
    ck = os.path.join(td, "checks")
    cp1 = json.load(open(os.path.join(ck, "cp1_verify.out.json")))
    cp3 = json.load(open(os.path.join(ck, "cp3_blind_certs.json")))
    cp2 = json.load(open(os.path.join(ck, "cp2_compare.json")))
    fc = json.load(open(os.path.join(ck, "cp2_floor_ceiling.json")))
    tc = json.load(open(os.path.join(ck, "third_check_m4_witnesses.json")))
    neg = Counter((x["kind"].split("/")[0], x["rejected"]) for x in cp3["negative_controls"])
    status_counts = cp3["counts"]
    per_label = {lab: {"key": v["key"], "arm": v["arm"], "wdag_v1": v["wdag"]["status"], "wdag_first_violation": v["wdag"].get("first_violation"),
                       "ann_v1": v["ann"]["status"], "ann_first_violation": v["ann"].get("first_violation")} for lab, v in cp3["per_label"].items()}
    out = {
        "schema": "certbin.n19.comparison.v1",
        "task_id": "TASK-20260926-f50294",
        "review_plan_id": "REVIEW-CERTBIN-20260926-d7249d",
        "joints": ["J7", "J8"],
        "run_id": "RUN-CERTBIN-a3fc60",
        "worktree": {"commit": cp1["worktree_head"], "clean": cp1["worktree_clean"],
                     "kind": "dedicated sparse git worktree at the TASK-20260926-e8779d archive commit (disk allowance: 2.5 GB free, so a full checkout was refused by the filesystem; sparse paths listed in validation-report.yaml)"},
        "CP-1": {"all_pass": cp1["all_pass"], "checks": cp1["checks"]},
        "key_mapping": cp2["key_mapping"],
        "CP-2": {
            "compared_item_instances": cp2["compared_item_instances"],
            "per_item_table": cp2["per_item_table"],
            "disagreements": cp2["disagreements"],
            "status_legend": {"agree": "both sides computed it and the values are equal (after the stated encoding map)",
                              "disagree": "both computed, values differ", "run_only": "the run recorded it, the re-deriver did not (by input kind)",
                              "re-deriver_only": "the re-deriver computed it, the run did not (outside the run's C-T4 / derived_per_instance scope)",
                              "both_absent": "neither side has it for this system (e.g. route 2 of s and the degenerate flag for explicit-kind inputs)"},
            "gaps_named": {
                "dims_by_deg(M_3)": "run-only on 90: the re-deriver's Q2 records rank_3 and 1 in R_3 but no M_3 profile (not a CP-2 item)",
                "s route 2 and degenerate flag": "absent for the 30 explicit-kind inputs (no x_R by construction, PD-R2)",
                "ell_route": "10 N-ELL19 re-deriver-only (run computes it for S_3 and N-CONV19 only); 10 N-F219 / N-AFF19 have no ell",
                "C-ELL c = Tr(t^k / x_R^2)": "10 N-CONV19 run-only (explicit kind withholds x_R); 10 N-ELL19 neither",
                "W'_4": "20 re-deriver-only (15 F-RANDX19, 5 S3-SAT100: outside the run's C-T4 sets)",
                "dim W^(i*+1)": "re-deriver-only on 90 (the run lists W^(0..i*)); equal to dim W^(i*) on 90/90",
            },
            "per_system": cp2["per_system"],
            "J1_vs_run_certificate_verdicts": cp2["J1_vs_run_certificates"],
            "J1_vs_run_ann_v1_verdicts": cp2["J1_vs_run_ann_v1"],
            "recount_from_J1_verdicts_only": cp2["recount_from_J1_verdicts"],
            "recount_vs_run_recorded": cp2["recount_vs_run_recorded"],
            "verdict_changes": cp2["recount_changes"],
            "J1_VC2_VC3_vs_instances_every_kept_system": cp2["J1_VC2_VC3_vs_instances_all_kept"],
            "J1_VC6_vs_run_M4_records": cp2["J1_VC6_vs_run_M4"],
            "ambiguities_vs_run_resolution": AMBIGUITIES,
        },
        "CP-3": {
            "checker": cp3["checker"],
            "checker_seal": "checks/checker-seal.txt (mini.py and check_blind_certs.py hashed before any re-deriver code was opened)",
            "f_k_sources": cp3["f_k_sources"],
            "cross_check_all_equal_run_E_hex": cp3["cross_check_all_equal"],
            "counts": status_counts,
            "per_label": per_label,
            "negative_controls": {"total": len(cp3["negative_controls"]), "all_rejected": cp3["negative_controls_all_rejected"],
                                  "by_format": {f"{k[0]}|rejected={k[1]}": v for k, v in neg.items()}},
            "certification_status_per_pool_key": cp2["certification_status_per_pool_key"],
            "certification_counts_per_arm": cp2["certification_counts_per_arm"],
            "seconds": cp3["seconds"], "max_rss_mb": cp3["max_rss_mb"],
        },
        "CP-4": {
            "disagreements_to_localise": len(cp2["disagreements"]),
            "localisations": [],
            "third_checks_declared": {"count_of_archived_systems": 20, "what": "J1 VC-6 M_4 witnesses re-verified with the comparator's own descent, M_4 rows and coordinate order on S3-U400:0..19 (for J8's certificate-backed table; no disagreement required a localisation)",
                                      "all_valid": tc["all_valid"], "file": "checks/third_check_m4_witnesses.json"},
            "D-2_on_independent_numbers": {
                "membership_form (ell_route == 1 in R'_4)": "holds on 80/80 re-deriver records and on 70/70 run records where both exist; every value is FALSE on both sides (a floor), so the membership form is never exercised in the TRUE direction here",
                "space_form (dim(rowspace(M_4) + ell*B_<=3) == rank R'_4 + 1160)": fc["D-2_space_identity_rederiver (dim(M_4 + ell*B_<=3) == rank R'_4 + 1160)"],
                "space_form_reading": "the re-deriver's DIRECT 20-variable elimination of rowspace(M_4) + ell*B_<=3 has dimension exactly rank R'_4 + 1160 on 80/80 systems, which is what D-2's space identity (the preimage of R'_4 under pi, restricted to B_<=4, with kernel ell*B_<=3 of dimension 6196 - 5036 = 1160) predicts; rank R'_4 itself agrees with the run on 80/80",
                "cross_side": "the re-deriver's direct ell_route equals the run's R'_4 'one' on 80/80 and the run's ell_route on 70/70",
            },
        },
        "floor_ceiling": fc["per_item"],
        "N-ELL19_kernel_dim_whole_arm": fc["N-ELL19_whole_arm_kernel_dim (run records)"],
        "input_sha256": {},
    }
    if len(sys.argv) > 2:
        wt = sys.argv[2]
        for rel in ("coordination/review/certbin-20260926-d7249d/blind/blind-inputs.json",
                    "coordination/review/certbin-20260926-d7249d/blind-inputs-key.json",
                    "coordination/review/certbin-20260926-d7249d/review-plan.yaml",
                    "coordination/review/certbin-20260926-d7249d/archives/TASK-20260926-e8779d/snapshot-receipt.json",
                    "coordination/review/certbin-20260926-d7249d/archives/TASK-20260926-5d1557/snapshot-receipt.json",
                    "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/rederivation.json",
                    "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/wdag.jsonl.gz",
                    "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/ann.jsonl.gz",
                    "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/verification.json",
                    "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/m4-witnesses.jsonl.gz",
                    "experiments/EXP-CERTBIN-060020/specification.yaml",
                    "experiments/EXP-CERTBIN-060020/trial-plan-v1.json",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/instances.jsonl.gz",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/closures.jsonl.gz",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/certificates.jsonl.gz",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/annihilators.jsonl.gz",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/certificate-verification.json",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/annihilator-verification.json",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/cell-summary.json",
                    "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/decision-rules.json"):
            out["input_sha256"][rel] = sha(os.path.join(wt, rel))
    json.dump(out, open(os.path.join(td, "comparison.json"), "w"), indent=1, default=str)
    print("comparison.json written;", out["CP-2"]["compared_item_instances"], status_counts)


if __name__ == "__main__":
    main()
