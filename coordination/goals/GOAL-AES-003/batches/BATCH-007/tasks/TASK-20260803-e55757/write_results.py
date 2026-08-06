#!/usr/bin/env python3
"""Compose RESULTS.json for TASK-20260803-e55757 and json.load-verify it."""
import json, os, sys, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_results as B

HERE = B.HERE
d = B.emit()
k, n, bound = d["k"], d["n"], d["bound"]
B006_BOUND = 0.784700038857546
B006_ALIVE, B006_N = 25, 27

git_now = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=HERE).stdout.strip()

R = {
  "schema": "crypto.autoresearch.task_results.v1_freeform",
  "task_id": "TASK-20260803-e55757",
  "title": "RANK 2: independent re-execution of the 27 RC-8 S-box draws",
  "goal_id": "GOAL-AES-003",
  "batch": "BATCH-007",
  "role": "executor",
  "generated_utc": d["now"],

  "inference": {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model": "claude-opus-5",
    "fallback_used": True,
    "model_verified": False,
    "model_verified_reason": "no adapter probe is available in this harness; the "
        "resolved model is reported from the runtime identity, not from a probe",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c"
  },

  "claim_tier": "toy",
  "claim_tier_basis":
    "Reduced-round AES-128 permutation, r=5, one machine, 2^30 trials per draw, "
    "27 drawn bijective S-boxes. Nothing here is a statement about full-round or "
    "deployed AES and no comparison to published cryptanalysis is made in either "
    "direction (RQ-AES-003 R3). A timeout or a killed process is resource "
    "exhaustion, never negative evidence.",
  "certificate": {"kind": "none",
                  "basis": "pure measurement run; no discrete-log solve and no "
                           "factor-base relation is claimed"},

  "WHAT_THIS_REPLICATES": {
    "target": "BATCH-006 TASK-20260803-0764fc, RANK 2 (RC-8): 27 random bijective "
              "S-box draws measured at r=5, 2^30 trials, arm seed 631001.",
    "target_result": {"ALIVE": B006_ALIVE, "n": B006_N,
                      "clopper_pearson_95_lower_bound": B006_BOUND},
    "why": "That bound rested on one implementation in one session. The BATCH-006 "
           "validator intended to re-execute it, hit ~10.6 h against a 4800 s "
           "budget, and named the omission (EV-AES-9794e1 unresolved_confounds[0]).",
    "same_objects": "The SAME 27 S-box seeds 20260803701..20260803727, the same arm "
                    "seed 631001, armid 1, 2 threads, log2N 30, rounds 5, amask 1, "
                    "smask 1. The draw, key derivation, per-thread split and trial "
                    "stream are deterministic functions of these, so a correct "
                    "implementation must reproduce the counts integer for integer. "
                    "This is bit-exact replication on the same sample, NOT an "
                    "independent resampling; replicating different draws would "
                    "answer a different question.",
    "sampling_noise_is_not_an_available_explanation":
        "Because the sample is not redrawn, a count disagreement cannot be charged "
        "to sampling. It would be an instrument fault in one of the two "
        "implementations, or a real divergence."
  },

  "INSTRUMENT": {
    "name": "rc8probe",
    "written_for_this_task": True,
    "source": "rc8probe.c",
    "source_sha256": d["sha_probe_c"],
    "measuring_binary": "rc8probe_native",
    "measuring_binary_sha256": d["sha_probe_bin"],
    "build_commands": [
      "gcc -O3 -pthread -o rc8probe rc8probe.c",
      "gcc -O3 -march=native -funroll-loops -pthread -o rc8probe_native rc8probe.c"
    ],
    "build_exit_status": 0,
    "which_binary_produced_the_reported_numbers": "rc8probe_native",
    "why_two_binaries":
      "rc8probe (-O3) was built and pinned first; rc8probe_native (-O3 -march=native "
      "-funroll-loops) measured ~6% faster on the 2^24 benchmark and was re-pinned "
      "against FIPS-197 C.1 before being used. Both pins are recorded. Every "
      "reported count comes from rc8probe_native.",
    "deliberate_differences_from_BATCH004_yoyo_sbox_v2": [
      "No T-tables: state is 16 bytes and SubBytes / ShiftRows / MixColumns / "
      "AddRoundKey are four separate byte-level steps with small GF(2^8) multiply "
      "tables (mul2, mul3, mul9, mul11, mul13, mul14). yoyo_sbox_v2 fuses "
      "SB+SR+MC into four 32-bit T-tables.",
      "Direct inverse cipher (ARK, InvShiftRows, InvSubBytes, InvMixColumns in "
      "straight reversed order, forward round keys only). yoyo_sbox_v2 uses the "
      "equivalent inverse cipher with InvMixColumns-transformed round keys and "
      "U-tables.",
      "AES S-box built from log/antilog tables over generator 0x03 with the affine "
      "map as a byte-rotation identity. yoyo_sbox_v2 finds the GF(2^8) inverse by "
      "an O(256^2) product search.",
      "Word-oriented key expansion with explicit RotWord/SubWord/Rcon over 44 "
      "4-byte words, rather than the fused byte loop."
    ],
    "deliberately_reproduced_because_they_define_the_object": [
      "splitmix64", "Fisher-Yates over 0..255 with rejection sampling",
      "the plaintext / active-word draw and its rejection condition",
      "the trivial-swap exclusion",
      "PW[j][row]=4*((j+row)%4)+row and CW[j][row]=4*((j-row) mod 4)+row",
      "key derivation kst = seed ^ 0xA5A5A5A5A5A5A5A5 then two splitmix64 draws",
      "thread seeding seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15",
      "the per-thread trial split N/nthr with the remainder on thread 0"
    ],
    "provenance_of_the_conventions":
      "Read from BATCH-006's yoyo_sbox_v2.c.readonly_copy, which the card permits "
      "in order to learn what object is measured. The code is newly written."
  },

  "PINS_AND_VALIDITY_CHECKS": {
    "P1_fips197_c1_known_answer_vector": {
      "ran": True,
      "command": "./rc8probe_native pin aes 60600002",
      "exit_status": 0,
      "key": "000102030405060708090a0b0c0d0e0f",
      "plaintext": "00112233445566778899aabbccddeeff",
      "expected_ciphertext": d["pin_aes"]["fips197_c1_kat_ciphertext_expected"],
      "computed_ciphertext": d["pin_aes"]["fips197_c1_kat_ciphertext_computed"],
      "encrypt_match": d["pin_aes"]["fips197_c1_kat_encrypt_match"],
      "decrypt_match": d["pin_aes"]["fips197_c1_kat_decrypt_match"],
      "note": "run BEFORE any measurement; the same enc_r/dec_r are used to measure"
    },
    "P2_bijectivity_and_P3_roundtrip_and_P4_sbox_identity": {
      "ran": True,
      "per_seed": d["sbox_checks"],
      "all_27_bijective": all(v["bijective"] for v in d["sbox_checks"].values()),
      "all_27_roundtrip_clean": all(v["roundtrip_failures"] == 0
                                    for v in d["sbox_checks"].values()),
      "roundtrip_checks_per_draw": 5120,
      "all_27_tables_identical_to_BATCH006_archived_tables":
          all(v["sbox_table_identical_to_BATCH006"] for v in d["sbox_checks"].values()),
      "meaning": "P4 establishes independently of any count that the two "
                 "implementations draw the SAME S-box from each seed, so a count "
                 "disagreement could not be blamed on drawing a different object."
    },
    "P5_cross_implementation_anchor_at_2^24": {
      "ran": True,
      "commands": [
        "./rc8probe arm ANCHOR-N24 rand:20260803701 5 1 1 24 631001 1 2",
        "../../../BATCH-006/tasks/TASK-20260803-0764fc/yoyo_sbox_v2 arm ANCHOR-N24 "
        "rand:20260803701 5 1 1 24 631001 1 2"
      ],
      "exit_statuses": [0, 0],
      "result": "EXACT agreement on trivial_swaps_excluded, nontrivial_trials, "
                "W_ge1_nontrivial (=2), W_ge1_by_word ([0,0,2,0]), whist, key_hex "
                "(c17835e6ca6233347781f4ba00d26ee4), thread_seeds and sbox_first8.",
      "note": "The archived binary was run ONLY as a check on my own code before "
              "measuring. No reported number comes from it."
    },
    "P6_per_arm_pin_gate": {
      "ran": True,
      "description": "Every `arm` invocation re-verifies dec_r(enc_r(x))==x under the "
                     "S-box it is about to measure, 64 random (key,plaintext) pairs "
                     "at every r in 1..10 = 640 checks, and refuses to measure on "
                     "failure (exit 5). No arm exited 5.",
      "note": "The FIPS-197 C.1 vector is applicable only to the AES S-box and is "
              "never faked for a drawn S-box."
    },
    "estimator_selftest_before_touching_my_data": d["selftest"],
    "estimator_selftest_meaning":
      "My Clopper-Pearson bisection recomputes BATCH-006's published bound "
      "0.784700038857546 from k=25,n=27 to within 1e-12, and my upward-summed "
      "Poisson tail reproduces BATCH-006's published tails for X=9 and X=6. The "
      "estimator is therefore not a source of any difference in the bound."
  },

  "THE_CRITERION": {
    "statement": "ALIVE iff X/v >= 5 AND P(K >= X | lambda = v) < 1e-6.",
    "source": "BATCH-004 TASK-20260803-367b1b/PREREGISTRATION.md, 'Decision rule "
              "(frozen)', lines 236-237.",
    "governing_record": "CORR-20260803-2cefa6",
    "only_one_reading_reported": True,
    "why_only_one":
      "CORR-20260803-2cefa6 records that this is the ONLY criterion this campaign "
      "ever froze, and that BATCH-005's looser 'at least 5x' form presents itself in "
      "its own text as a QUOTATION of this rule while dropping the Poisson conjunct. "
      "A defective restatement does not create a rule. No second reading, no "
      "'not DEAD' reading and no pooled bound is computed or reported here: "
      "reporting two readings side by side is how this campaign came to claim a "
      "0.90 bound it had not earned.",
    "v_definition": "v = nontrivial_trials * 4 / 2^32, the matched analytic null",
    "bound_estimator": "one-sided 95% Clopper-Pearson lower bound on ALIVE/n, "
                       "solving sum_{j=k}^{n} C(n,j) p^j (1-p)^(n-j) = 0.05 by "
                       "bisection; for k=n it is 0.05^(1/n)"
  },

  "PER_DRAW": d["draws"],

  "PER_DRAW_AGREEMENT_SUMMARY": {
    "stated_draw_by_draw_in": "PER_DRAW[<arm>].AGREEMENT and .per_field_agreement",
    "fields_compared": ["trivial_swaps_excluded", "nontrivial_trials",
                        "W_ge1_nontrivial", "W_ge1_by_word", "whist",
                        "key_hex", "thread_seeds", "sbox_first8"],
    "draws_completed": d["completed"],
    "draws_in_exact_agreement": d["exact"],
    "draws_in_disagreement": d["disagree"],
    "n_completed": n,
    "n_exact_agreement": len(d["exact"]),
    "n_disagreement": len(d["disagree"]),
    "draws_not_completed": d["not_completed"],
    "aggregate_is_not_the_deliverable":
      "The per-draw verdicts above are the deliverable. This block is an index into "
      "them, not a substitute: aggregate agreement can hide compensating errors."
  },

  "RESULT": {
    "ALIVE_count_strict_BATCH004": k,
    "n_draws_measured_by_this_task": n,
    "alive_arms": d["alive_arms"],
    "not_alive_arms": d["not_alive"],
    "clopper_pearson_95_lower_bound_on_the_preserving_fraction": bound,
    "bound_scope":
      "p = fraction of bijective S-boxes that are ALIVE under the strict BATCH-004 "
      "rule at THIS round count (r=5), THIS key block (arm seed 631001), THIS "
      "exposure (2^30 trials) and THIS liveness rule. Unpooled, over the draws "
      "this task actually measured.",
    "BATCH006_bound": B006_BOUND,
    "BATCH006_ALIVE": B006_ALIVE,
    "BATCH006_n": B006_N,
    "bound_differs_from_BATCH006": (bound is None) or (abs(bound - B006_BOUND) > 1e-12),
    "not_reconciled_by_adopting_the_other_implementations_numbers": True
  },

  "BUDGET": {
    "declared_wall_clock_seconds": 5400,
    "declared_memory_gb": 8,
    "maximum_runs": 35,
    "max_threads": 2,
    "start_utc": "2026-08-03T18:28:57Z",
    "start_epoch": 1785781737,
    "binding_stop_utc": "2026-08-03T19:58:57Z",
    "binding_stop_epoch": 1785787137,
    "stamps_file": "budget_stamps.jsonl",
    "arm_timings": d["timing"],
    "dropped_on_budget_lines": d["dropped"],
    "commands_executed_for_arms": d["cmds"]
  },

  "ENVIRONMENT": d["env"],
  "GIT": {
    "commit_at_task_start": "2d102750307c284f5ce489923bd92f5c7cbaf247",
    "commit_at_environment_capture": "e451574b7eb3cad9f9d242ddf7e6452cc1e62b46",
    "commit_at_results_write": git_now,
    "note": "HEAD moved during this task because another agent was committing in the "
            "shared worktree. This task committed nothing; its directory is "
            "gitignored on purpose. All three observed commits are recorded rather "
            "than one being presented as 'the' revision.",
    "dirty_tree_at_environment_capture": d["env"]["git_dirty"] or "(clean)"
  }
}

os.chdir(HERE)
with open("RESULTS.json", "w") as f:
    json.dump(R, f, indent=1)

# self-check: the file must parse
with open("RESULTS.json") as f:
    reloaded = json.load(f)
R["SELF_CHECK"] = {
    "json_load_run_on_own_RESULTS_json": True,
    "json_load_succeeded": True,
    "reloaded_top_level_keys": sorted(reloaded.keys()),
    "bytes": os.path.getsize("RESULTS.json")
}
with open("RESULTS.json", "w") as f:
    json.dump(R, f, indent=1)
with open("RESULTS.json") as f:
    json.load(f)
print("RESULTS.json written and json.load-verified twice; bytes =",
      os.path.getsize("RESULTS.json"))
print("k =", k, " n =", n, " bound =", bound)
print("exact agreement:", len(d["exact"]), "of", n, " disagreements:", d["disagree"])
print("not completed:", d["not_completed"])
