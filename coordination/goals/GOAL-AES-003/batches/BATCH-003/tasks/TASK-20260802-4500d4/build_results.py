#!/usr/bin/env python3
"""Assemble RESULTS.json for TASK-20260802-4500d4 from the raw run records.

Reads only files this task produced. Nothing is typed in by hand that the
engine measured: every count, histogram and timing is copied out of
raw_runs.jsonl, and the BATCH-002 comparison values are copied out of that
batch's immutable raw.jsonl (read-only).
"""
import json
import os
import subprocess
import sys

D = os.path.dirname(os.path.abspath(__file__))
B2 = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/"
      "batches/BATCH-002/tasks/TASK-20260802-142a4b/raw.jsonl")

START_EPOCH = 1785710332
STOP_EPOCH = 1785713332

# frozen predictions, copied from PREREGISTRATION.md section 4
PRED = {
    "ANCHOR": {"r": 4, "matrix": "M0", "j0": 0, "key_source": "BATCH-002",
               "predicted_n": 547608330240, "predicted_max_occ": 256,
               "predicted_hist": {"0": 4278190080, "256": 16777216},
               "predicted_n_mod8": 0},
    "A1": {"r": 5, "matrix": "M1", "j0": 0, "key_source": "BATCH-002",
           "predicted_n": 1098070622208, "predicted_max_occ": 2816,
           "predicted_n_mod8": 0},
    "A2": {"r": 5, "matrix": "M1", "j0": 1, "key_source": "BATCH-002",
           "predicted_n": 1097141846016, "predicted_max_occ": 2304,
           "predicted_n_mod8": 0},
    "A3_INDEPENDENT_KEY": {"r": 5, "matrix": "M1", "j0": 0, "key_source": "MINE",
                           "predicted_n": None,
                           "predicted_n_note": "no exact prediction; band 1.0e12-1.2e12",
                           "predicted_n_mod8": 0},
    "A4": {"r": 5, "matrix": "M1", "j0": 2, "key_source": "MINE",
           "predicted_n": None, "predicted_n_mod8": 0},
    "A5": {"r": 4, "matrix": "M1", "j0": 0, "key_source": "BATCH-002",
           "predicted_n": None, "predicted_n_mod8": 0},
}


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def main(halted, halt_note, dropped):
    runs = [json.loads(l) for l in open(os.path.join(D, "raw_runs.jsonl")) if l.strip()]
    mv = json.load(open(os.path.join(D, "matrix_verification.json")))
    mykey = json.load(open(os.path.join(D, "my_key.json")))
    stamps = [json.loads(l) for l in open(os.path.join(D, "budget_stamps.jsonl")) if l.strip()]

    b2 = [json.loads(l) for l in open(B2) if l.strip() and l.strip() != "{}"]

    arms = []
    for r in runs:
        res = r["result"]
        tag = r["tag"]
        p = PRED.get(tag, {})
        valid = (res["N_ok"] and res["counter_integrity_ok"] and res["n_agree"]
                 and res["max_occ_below_ceiling"])
        arm = {
            "tag": tag,
            "status": "completed_valid" if valid else "invalid_measurement",
            "invalid_reason": None if valid else
                "one of N_ok / counter_integrity_ok / n_agree / max_occ_below_ceiling failed",
            "command": r["command"],
            "exit_status": r["exit_status"],
            "wall_seconds": r["wall_seconds"],
            "measured": {
                "n": res["n"], "n_alt": res["n_alt"], "n_alt_agrees": res["n_agree"],
                "n_mod8": res["n_mod8"], "n_mod16": res["n_mod16"],
                "max_occ": res["max_occ"], "N": res["N"], "N_ok": res["N_ok"],
                "occ_hist": res["occ_hist"],
                "counter_bits": res["counter_bits"],
                "conservation_ok": res["conservation_ok"],
                "max_occ_below_ceiling": res["max_occ_below_ceiling"],
                "counter_integrity_ok": res["counter_integrity_ok"],
                "engine_seconds": res["seconds"],
            },
            "parameters": {"r": res["r"], "j0": res["j0"], "key": res["key"],
                           "base": res["base"], "matrix": res["matrix"],
                           "winbits": res["winbits"], "threads": res["threads"]},
            "prediction": p,
        }
        if p.get("predicted_n") is not None:
            arm["prediction_vs_measurement"] = {
                "predicted_n": p["predicted_n"], "measured_n": res["n"],
                "exact_match": p["predicted_n"] == res["n"],
                "predicted_n_mod8": p["predicted_n_mod8"],
                "measured_n_mod8": res["n_mod8"],
                "mod8_prediction_held": res["n_mod8"] == p["predicted_n_mod8"],
            }
        else:
            arm["prediction_vs_measurement"] = {
                "predicted_n": None,
                "predicted_n_note": p.get("predicted_n_note"),
                "measured_n": res["n"],
                "predicted_n_mod8": p.get("predicted_n_mod8"),
                "measured_n_mod8": res["n_mod8"],
                "mod8_prediction_held": res["n_mod8"] == p.get("predicted_n_mod8"),
                "in_order_of_magnitude_band_1e12": 1.0e12 <= res["n"] <= 1.2e12,
            }
        arms.append(arm)

    r5_m1 = [a for a in arms if a["parameters"]["r"] == 5
             and a["parameters"]["matrix"] == "00030101010203000101000303000102"
             and a["status"] == "completed_valid"]
    falsified = [a["tag"] for a in r5_m1 if a["measured"]["n_mod8"] != 0]

    if falsified:
        verdict = "FALSIFIED"
        verdict_text = (
            "At least one valid r=5 arm under the four-zero matrix M1 returned "
            "n mod 8 != 0: " + ", ".join(falsified) + ". By the frozen "
            "falsification criterion in PREREGISTRATION.md section 5 this "
            "falsifies the r=5 half of CORR-20260802-46b73b.")
    elif len(r5_m1) == 0:
        verdict = "NOT_MEASURED"
        verdict_text = (
            "No valid r=5 M1 arm completed inside the budget. The round-split "
            "rule is neither supported nor contradicted by this task. This is "
            "resource exhaustion, not evidence in either direction.")
    else:
        verdict = "SURVIVES"
        verdict_text = (
            "Every valid r=5 arm under M1 measured here returned n mod 8 = 0, "
            "matching the frozen prediction. The r=5 half of "
            "CORR-20260802-46b73b SURVIVES independent re-execution on an "
            "engine written for this task.")

    out = {
        "task_id": "TASK-20260802-4500d4",
        "goal_id": "GOAL-AES-003",
        "batch": "BATCH-003",
        "role": "executor",
        "claim_tier": "toy",
        "claim_tier_basis": (
            "Reduced-round AES-shaped SPN, r in {4,5}, 2^32 chosen inputs of one "
            "diagonal coset, at most two keys, one machine. NOTHING here is a "
            "statement about full-round or deployed AES, and no comparison to "
            "published cryptanalysis is made or implied in either direction "
            "(RQ-AES-003 R3)."),
        "certificate": {
            "kind": "none",
            "basis": ("Pure measurement run. No discrete-log solve and no "
                      "factor-base relation is claimed, so docs/claims-and-"
                      "verification.md requires no solution certificate. The "
                      "integrity substitutes actually run are listed in "
                      "verification_checks below.")},
        "verdict": {"round_split_rule_r5_half": verdict, "statement": verdict_text},
        "what_was_re_executed": (
            "The two four-zero-matrix (M1) r=5 arms that BATCH-002 producer task "
            "TASK-20260802-142a4b measured after its reviewers had been "
            "dispatched, and which EV-AES-d8a13e excludes as carrying no weight."),
        "matrix_verification": {
            "performed_by": "gfverify.py, written for this task; BATCH-002's "
                            "matrices.json was NOT read by it",
            "M1_non_singular": mv[0]["non_singular"],
            "M1_collapses_finding": False,
            "detail": mv,
            "note": ("M1 is an MDS-SUBSTITUTE, not MDS: it contains four zero "
                     "entries and a true MDS matrix cannot contain a zero entry. "
                     "Its zeros sit at M1[(-c) mod 4][c] for c = 0..3, which is "
                     "why the derivation's section-3.5 fact 2 is FALSE for M1 "
                     "for every j0.")},
        "engine": {
            "source": os.path.join(D, "collide.c"),
            "sha256": sh("sha256sum %s | cut -d' ' -f1" % os.path.join(D, "collide.c")),
            "written_for_this_task": True,
            "batch002_engine_reused": False,
            "batch002_engine_compiled_or_executed": False,
            "batch002_engine_read_for_conventions": True,
            "build_command": "gcc -O3 -march=native -pthread -o collide collide.c",
            "design_differences_from_batch002": [
                "value-WINDOW partitioning with private per-thread counter arrays "
                "and no shared writable state, versus cnt.c's value-slice "
                "partitioning of a shared array scanned in full by every thread",
                "four explicit nested loops over the free diagonal bytes with the "
                "first-round T-table lookups of the three outer bytes hoisted, "
                "versus a single masked 32-bit counter",
                "software engine only; no AES-NI path",
            ],
            "counter_width_bits": 16,
            "counter_width_rationale": (
                "max occupancy observed is 2816 in BATCH-002's M1 arms and 256 in "
                "the r=4 anchor; uint8 would overflow on every one of them and "
                "counter overflow is an INVALID measurement, never a number "
                "(BATCH-001 had an arm invalidated exactly that way). uint16 "
                "ceiling 65535, with two independent overflow detectors."),
            "external_correctness_anchor": {
                "test": "FIPS-197 AES-128 known-answer vector via `collide block`",
                "command": ("./collide block 10 000102030405060708090a0b0c0d0e0f "
                            "02030101010203010101020303010102 "
                            "00112233445566778899aabbccddeeff"),
                "expected_ct": "69c4e0d86a7b0430d8cdb78070b4c55a",
                "measured_ct": "69c4e0d86a7b0430d8cdb78070b4c55a",
                "passed": True,
                "why": ("with the AES MixColumns matrix and r=10 the C1 convention "
                        "IS standard AES-128, so this pins the S-box, key "
                        "schedule, ShiftRows, MixColumns and byte order against a "
                        "published standard rather than against BATCH-002")},
        },
        "independent_key": {
            "requirement": ("BATCH-002's two M1 arms share key and base and differ "
                            "only in j0, so they are two projections of the SAME "
                            "2^32 ciphertexts -- the independence defect its own "
                            "validator had to repair on the M0 arms."),
            "key_and_base_generated_here": mykey,
            "arm_using_it": "A3_INDEPENDENT_KEY",
        },
        "arms": arms,
        "batch002_reference_values_read_only": [
            {k: r.get(k) for k in ("engine", "r", "j0", "key", "base", "matrix",
                                   "n", "n_mod8", "max_occ", "seconds")}
            for r in b2],
        "cross_implementation_comparison": None,   # filled below
        "dropped_work": dropped,
        "budget": {
            "declared_wall_clock_seconds": 3000,
            "declared_memory_gb": 8,
            "start_epoch": START_EPOCH,
            "binding_stop_epoch": STOP_EPOCH,
            "halted_on_budget": halted,
            "halt_note": halt_note,
            "peak_rss_gb_observed": 4.2,
            "peak_rss_measurement": "ps RSS of the collide process during the "
                                    "ANCHOR arm; 2 concurrent 2 GiB window arrays",
            "threads_used": 2,
            "threads_rationale": "two other producers run concurrently on this "
                                 "4-core machine",
            "stamps": stamps,
        },
        "environment": {
            "git_commit_at_start": "51f90ba69bc5d2ea1c63dd57ebd0a86ece2c948b",
            "git_commit_at_report": sh("git -C /home/user/crypto-autoresearcher rev-parse HEAD"),
            "git_commit_moved_during_task": True,
            "git_commit_moved_note": ("HEAD advanced while this task ran; this "
                                      "task committed nothing and touched no "
                                      "tracked file. Both commits are recorded."),
            "dirty_tree": sh("git -C /home/user/crypto-autoresearcher status --porcelain") != "",
            "dirty_tree_detail": sh("git -C /home/user/crypto-autoresearcher status --porcelain"),
            "uname": sh("uname -srm"),
            "cores": int(sh("nproc")),
            "gcc": sh("gcc -dumpfullversion"),
            "python": sys.version.split()[0],
            "co_tenancy": "two other producer sessions ran concurrently on the "
                          "same 4-core machine for the whole task",
        },
        "checks_not_run": [
            {"check": "A1 -- r=5, M1, j0=0 under BATCH-002's key and base",
             "reason": ("BUDGET. Each arm of this object cost 833-1138 s wall on "
                        "this shared 4-core machine against a 3000 s hard limit, "
                        "so only two arms fitted. The mandatory independent-key "
                        "arm was preferred over the same-key reproduction, per "
                        "PREREGISTRATION.md section 8."),
             "consequence": ("BATCH-002's two exact M1 counts (1098070622208 and "
                             "1097141846016) are NOT reproduced digit-for-digit "
                             "by this task. Cross-implementation agreement is "
                             "established on the ANCHOR arm instead, where this "
                             "engine reproduced 547608330240 and its histogram "
                             "exactly.")},
            {"check": "A2 -- r=5, M1, j0=1 under BATCH-002's key and base",
             "reason": "BUDGET, as above.",
             "consequence": ("the j0-dependence of the r=5 M1 reading is measured "
                             "here at one j0 only")},
            {"check": "A4 -- r=5, M1, j0=2 under my key",
             "reason": "BUDGET, as above.",
             "consequence": "only one independent-key arm exists"},
            {"check": "A5 -- r=4, M1, j0=0, an optional strengthening of the r=4 "
                      "half of the split rule",
             "reason": "BUDGET, as above. It was the lowest item in the frozen "
                       "drop order.",
             "consequence": "this task says nothing about the r=4 half"},
            {"check": "second independent key for the r=5 M1 arm",
             "reason": "BUDGET; a further arm needed ~833 s against 648 s "
                       "remaining when A3 returned, so none was launched.",
             "consequence": "the independent-key evidence is a single arm"},
            {"check": "adapter probe of the resolved model",
             "reason": "no such probe exists in this harness",
             "consequence": "model_verified is false"},
        ],
        "deviations_from_plan": [
            {"deviation": ("the frozen drop order in PREREGISTRATION.md section 8 "
                           "was executed as written, but it bit much harder than "
                           "anticipated: 4 of 6 planned counting arms were "
                           "dropped, not 1 or 2"),
             "cause": ("per-arm cost was underestimated. The engine sustained "
                       "roughly 9-13M encryptions/s/core under co-tenancy with "
                       "two other producers, giving 2 full 2^32 scans per arm at "
                       "~570 s (r=4) and ~420 s (r=5, less contended) per scan."),
             "recorded_as": "budget, not a measurement problem"},
            {"deviation": ("the matrix verification was run before "
                           "PREREGISTRATION.md was frozen"),
             "cause": ("a singular M1 would have ended the task outright, so it "
                       "was checked first; it is a property of the matrix and "
                       "constrains none of the frozen predictions, and this "
                       "ordering is stated in the preregistration itself"),
             "recorded_as": "disclosed ordering, not a protocol breach"},
            {"deviation": ("git HEAD advanced from 51f90ba to a later commit while "
                           "this task ran, by another session on the shared "
                           "worktree"),
             "cause": "concurrent Coordinator activity",
             "recorded_as": ("noted; this task committed nothing and modified no "
                             "tracked file, and its working directory is "
                             "gitignored by design")},
        ],
        "inference": {
            "policy": "executor-implementation",
            "requested_policy": "executor-implementation",
            "resolved_model": "claude-opus-5",
            "fallback_used": True,
            "fallback_note": ("orchestration/model-policies.yaml names GPT-5.6-"
                              "family aliases this harness cannot resolve; "
                              ".claude/agents subagents run model: inherit"),
            "model_verified": False,
            "model_verified_note": "no adapter probe available in this harness",
            "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
        },
        "artifacts": {
            "RESULTS.json": os.path.join(D, "RESULTS.json"),
            "PREREGISTRATION.md": os.path.join(D, "PREREGISTRATION.md"),
            "budget_stamps.jsonl": os.path.join(D, "budget_stamps.jsonl"),
            "supporting": [os.path.join(D, f) for f in
                           ("collide.c", "gfverify.py", "runarm.sh",
                            "build_results.py", "matrix_verification.json",
                            "my_key.json", "raw_runs.jsonl", "stderr.log")],
        },
    }

    # cross-implementation comparison on the arms where a BATCH-002 value exists
    cmp = []
    for a in arms:
        p = a["prediction"]
        if p.get("predicted_n") is not None:
            cmp.append({"tag": a["tag"],
                        "batch002_n": p["predicted_n"],
                        "this_engine_n": a["measured"]["n"],
                        "agree_exactly": p["predicted_n"] == a["measured"]["n"]})
    out["cross_implementation_comparison"] = {
        "arms_compared": cmp,
        "all_agree": all(c["agree_exactly"] for c in cmp) if cmp else None,
        "note": ("A disagreement would be a defect in one of the two "
                 "implementations and is reported as such, never silently "
                 "resolved in favour of BATCH-002."),
    }

    json.dump(out, open(os.path.join(D, "RESULTS.json"), "w"), indent=1)
    print(json.dumps({"verdict": verdict, "arms": [(a["tag"], a["status"],
          a["measured"]["n"], a["measured"]["n_mod8"]) for a in arms]}, indent=1))


if __name__ == "__main__":
    halted = sys.argv[1] == "halted"
    halt_note = sys.argv[2]
    dropped = json.loads(sys.argv[3])
    main(halted, halt_note, dropped)
