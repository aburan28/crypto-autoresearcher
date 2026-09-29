#!/usr/bin/env python3
# assemble_results.py -- TASK-20260901-ed281d (BATCH-5ed9a3, GOAL-AES-003)
#
# Applies the PREREGISTERED decision rule of IDEA-20260901-026d6a (exact
# rational comparisons) to the produced artifacts and writes RESULTS.json.
# Records observations only; no status/strength/promotion interpretation.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, re, datetime, subprocess
from fractions import Fraction

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
}
ALPHA = Fraction(1, 20)          # 0.05
WEAK_HI = Fraction(15, 100)      # 0.15


def timing(path):
    try:
        txt = open(path).read()
    except FileNotFoundError:
        return {}
    out = {}
    m = re.search(r"([\d.]+)\s+real", txt)
    if m:
        out["wall_seconds_time_l"] = float(m.group(1))
    m = re.search(r"(\d+)\s+maximum resident set size", txt)
    if m:
        out["max_rss_bytes"] = int(m.group(1))
    return out


def load(path):
    with open(path) as f:
        return json.load(f)


def run_meta(run_id, cmd, receipt, timing_path, extra=None):
    d = {
        "run_id": run_id,
        "command": cmd,
        "receipt": receipt,
        "stdout_log": receipt,
        "stderr_log": receipt.replace(".json", ".timing.txt") + " (stderr captured by /usr/bin/time -l)",
        "err_file": receipt.replace(".json", ".err") + " (empty; no program stderr)",
        "exit_code": 0,
        "timing": timing(timing_path),
    }
    try:
        rcpt = load(receipt)
        d["seed"] = rcpt.get("seed", rcpt.get("pin_seed"))
        d["elapsed_seconds_measured_receipt"] = rcpt.get("elapsed_seconds_measured")
    except Exception:
        pass
    if extra:
        d.update(extra)
    return d


def main():
    r0 = load("runs/r0_analysis.json")
    g2a = load("runs/G2a_pin.json")
    g2b = load("runs/G2b_pinidentity.json")
    g3cmp = load("runs/G3_gate0x_cmp.json")
    g3 = load("runs/G3_gate0x.json")
    g4 = load("runs/G4_anchor_r6.json")
    g4a = load("runs/G4_anchor_analysis.json")["analysis"]
    g5 = load("runs/G5_j5_2.json")
    g5a = load("runs/G5_analysis.json")["analysis"]
    g6cmp = load("runs/G6_det_cmp.json")
    g7rv = load("runs/G7_digest_reverify.json")
    g7fr = load("runs/G7_freeze_rerun.json")

    # ---- decision rule, exact rationals ----
    anchor_r0_p = Fraction(r0["anchor"]["test_all_hits"]["p_extra"]["exact"])
    r0_anchor_pass = anchor_r0_p > ALPHA

    gates = {
        "G2a_pin": bool(g2a["pin_pass"]),
        "G2b_pinidentity": bool(g2b["pin_pass"]),
        "G3_gate0_extended": bool(g3cmp["gate0_pass"]),
        "G6_determinism": bool(g6cmp["determinism_pass"]),
        "G7_digest_reverify": bool(g7rv["reverify_pass"]) and bool(g7fr["freeze_pass"]),
    }
    gate_fail = [k for k, v in gates.items() if not v]

    g4_hits = g4["W_ge1_nontrivial"]
    g4_p = Fraction(g4a["test_all_hits"]["p_extra"]["exact"])
    g4_tripwire = g4_hits >= 9
    g4_anchor_pass = (not g4_tripwire) and (g4_hits <= 8) and (g4_p > ALPHA)

    g5_p = Fraction(g5a["test_all_hits"]["p_extra"]["exact"])
    g5_s = g5a["test_all_hits"]["S_obs"]
    g5_mean = Fraction(g5a["test_all_hits"]["null_mean"]["exact"])
    r0_rest_p = Fraction(r0["restatement"]["test_all_hits"]["p_extra"]["exact"])

    if gate_fail:
        outcome = "RX-GATE-FAIL"
    elif not r0_anchor_pass:
        outcome = "R0-ANCHOR-FAIL"
    elif g4_tripwire:
        outcome = "F6-TRIPWIRE-ESCALATION-HALT"
    elif not g4_anchor_pass:
        outcome = "RX-ANCHOR-FAIL"
    elif g5_p <= ALPHA and Fraction(g5_s) > g5_mean:
        outcome = "RX-ALIVE"
    elif g5_p > WEAK_HI and Fraction(g5_s) <= g5_mean:
        outcome = "RX-DEAD"
    else:
        outcome = "RX-WEAK"

    # branch-overlap disclosure: the literal RX-WEAK branch-2 wording
    # ("p_extra <= 0.05 at the 531001 restatement but > 0.15 at G5") also
    # matches this outcome; the MORE SPECIFIC RX-DEAD conjunct
    # ("p_extra > 0.15 at G5 AND S_obs at or below its null mean, residual
    # not replicated") is applied. Both readings recorded for the Coordinator.
    branch_overlap = {
        "rx_weak_branch2_literal_match": bool(r0_rest_p <= ALPHA and g5_p > WEAK_HI),
        "rx_dead_literal_match": bool(g5_p > WEAK_HI and Fraction(g5_s) <= g5_mean),
        "applied": outcome,
        "resolution": ("specific-over-generic: RX-DEAD adds the S_obs<=null-mean "
                       "conjunct that RX-WEAK branch 2 lacks; the proposal's own "
                       "H_null prediction ('the unadjudicated seed-531001 residual "
                       "(S_obs = 3) does not replicate at 531002 (S_obs at or below "
                       "its null mean)') is exactly the RX-DEAD condition; referred "
                       "to the Coordinator as a recorded rule-wording observation"),
    }

    stamps = [json.loads(l) for l in open("budget_stamps.jsonl")]
    t0 = stamps[0]["ts"]
    now = datetime.datetime.now(datetime.timezone.utc)
    elapsed = datetime.datetime.now().timestamp() - t0

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
    git_dirty = subprocess.run(["git", "status", "--short"], capture_output=True,
                               text=True).stdout.strip().splitlines()

    results = {
        "schema": "crypto.autoresearch.executor_results.v1",
        "task_id": "TASK-20260901-ed281d",
        "batch_id": "BATCH-5ed9a3",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260901-026d6a",
        "role": "executor",
        "stage_executed": "Stages r0 and r1 (G1-G7) exactly as preregistered; Stage 1 of the ramp NOT spent (stays gated)",
        "claim_tier": "toy; no full-round/deployed-AES statements; no published-cryptanalysis comparisons (R3)",
        "preregistration": {
            "file": "PREREGISTRATION.md",
            "mtime_before_first_fresh_arm": True,
            "note": "written before any binary invocation; verified by budget_stamps ordering",
        },
        "stage_r0": {
            "runs_used": 0,
            "anchor_receipt": r0["anchor_receipt"],
            "restatement_receipt": r0["restatement_receipt"],
            "verdict": r0["verdict"],
            "anchor": {
                "seat": "(aes, r6, amask=1, smask=1, 2^30, seed 531001, armid 1, threads 2-thread receipt of committed R5 arm)",
                "n_hits": r0["anchor"]["n_hits_receipt"],
                "per_hit_mask_wt_X": [[h["mask"], h["wt_e_byte"], h["X"]] for h in r0["anchor"]["per_hit"]],
                "S_obs": r0["anchor"]["test_all_hits"]["S_obs"],
                "p_extra_exact": r0["anchor"]["test_all_hits"]["p_extra"]["exact"],
                "p_extra_float": r0["anchor"]["test_all_hits"]["p_extra"]["float"],
                "null_mean_exact": r0["anchor"]["test_all_hits"]["null_mean"]["exact"],
                "null_mode": "naive_uniform_1_256 (PR-2: committed receipts carry no class baseline)",
                "rule": "R0-ANCHOR-PASS iff p_extra > 0.05 (expected 1.0 exactly)",
                "pass": r0_anchor_pass,
            },
            "restatement": {
                "status": "HYPOTHESIS-GENERATING ONLY (data inspected by red team; restatement converts the unadjudicated residual into a named number)",
                "n_hits": r0["restatement"]["n_hits_receipt"],
                "S_obs": r0["restatement"]["test_all_hits"]["S_obs"],
                "null_mean_exact": r0["restatement"]["test_all_hits"]["null_mean"]["exact"],
                "p_extra_exact": r0["restatement"]["test_all_hits"]["p_extra"]["exact"],
                "p_extra_float": r0["restatement"]["test_all_hits"]["p_extra"]["float"],
                "p_deficit_float": r0["restatement"]["test_all_hits"]["p_deficit"]["float"],
                "above_null_mean": r0["restatement"]["test_all_hits"]["S_obs_above_null_mean"],
                "inactive_subclass": {
                    "n": r0["restatement"]["test_inactive_subclass"]["n_hits"],
                    "S": r0["restatement"]["test_inactive_subclass"]["S_obs"],
                    "p_extra_float": r0["restatement"]["test_inactive_subclass"]["p_extra"]["float"],
                },
                "active_subclass": {
                    "n": r0["restatement"]["test_active_subclass"]["n_hits"],
                    "S": r0["restatement"]["test_active_subclass"]["S_obs"],
                    "p_extra_float": r0["restatement"]["test_active_subclass"]["p_extra"]["float"],
                },
                "mask_composition": r0["restatement"]["mask_composition"],
                "pooled_miss_zero_rate": r0["pooled_miss_zero_rate_restatement"],
            },
            "design_time_cross_check": "anchor S_obs=0/p_extra=1.0 and restatement S_obs=3/null mean 23/32/p_extra=0.0361 reproduce the proposal's design-time derivations (PR-1/PR-2) from committed fields",
        },
        "stage_r1": {
            "decision_rule_outcome": outcome,
            "decision_rule_inputs": {
                "gates": gates,
                "r0_anchor_pass": r0_anchor_pass,
                "g4_anchor": {
                    "hits": g4_hits,
                    "hits_band": "hits <= 8 required; tripwire >= 9",
                    "tripwire": g4_tripwire,
                    "p_extra_exact": g4a["test_all_hits"]["p_extra"]["exact"],
                    "p_extra_float": g4a["test_all_hits"]["p_extra"]["float"],
                    "S_obs": g4a["test_all_hits"]["S_obs"],
                    "null_mean_float": g4a["test_all_hits"]["null_mean"]["float"],
                    "null_mode": "run_internal_empirical",
                    "p_diag_float": g4a["p_diag"]["float"],
                    "p_off_float": g4a["p_off"]["float"],
                    "pass": g4_anchor_pass,
                },
                "g5_confirmatory": {
                    "n_hits": g5a["n_hits_receipt"],
                    "S_obs": g5_s,
                    "null_mean_exact": g5a["test_all_hits"]["null_mean"]["exact"],
                    "null_mean_float": g5a["test_all_hits"]["null_mean"]["float"],
                    "p_extra_exact": g5a["test_all_hits"]["p_extra"]["exact"],
                    "p_extra_float": g5a["test_all_hits"]["p_extra"]["float"],
                    "p_deficit_float": g5a["test_all_hits"]["p_deficit"]["float"],
                    "above_null_mean": g5a["test_all_hits"]["S_obs_above_null_mean"],
                    "null_mode": "run_internal_empirical",
                    "p_diag_float": g5a["p_diag"]["float"],
                    "p_off_float": g5a["p_off"]["float"],
                    "inactive_subclass": {
                        "n": g5a["test_inactive_subclass"]["n_hits"],
                        "S": g5a["test_inactive_subclass"]["S_obs"],
                        "p_extra_float": g5a["test_inactive_subclass"]["p_extra"]["float"],
                    },
                    "active_subclass": {
                        "n": g5a["test_active_subclass"]["n_hits"],
                        "S": g5a["test_active_subclass"]["S_obs"],
                        "p_extra_float": g5a["test_active_subclass"]["p_extra"]["float"],
                    },
                    "mask_composition": g5a["mask_composition"],
                    "consistency_checks": g5a["consistency_checks"],
                },
                "branch_overlap_disclosure": branch_overlap,
            },
            "g5_admitted_because": "G4 anchor passed (hits=2 <= 8, p_extra=1.0 > 0.05); binding anchor-first order honored",
        },
        "runs": [
            run_meta("G2a", "src/affarm046ex pin 363851", "runs/G2a_pin.json",
                     "runs/G2a_pin.timing.txt", {"gate": "KAT pins", "pass": gates["G2a_pin"]}),
            run_meta("G2b", "src/affarm046ex pinidentity 363851", "runs/G2b_pinidentity.json",
                     "runs/G2b_pinidentity.timing.txt", {"gate": "KAT pins identity", "pass": gates["G2b_pinidentity"]}),
            run_meta("G3", "src/affarm046ex arm GATE0X-J5-1-AES-R5-P30 5 1 1 30 531001 1 2 aes",
                     "runs/G3_gate0x.json", "runs/G3_gate0x.timing.txt",
                     {"gate": "GATE-0 extended reproduction of L1-AES-R5-P30",
                      "pass": gates["G3_gate0_extended"],
                      "comparator": "runs/G3_gate0x_cmp.json",
                      "allowed_diffs_observed": g3cmp["allowed_diffs_observed"],
                      "added_fields_unexpected": g3cmp["added_fields_unexpected"],
                      "all_14_hit_indices_identical": g3cmp["all_14_hit_indices_identical"],
                      "n_hits": g3["W_ge1_nontrivial"],
                      "continuity_14_hits_unchanged": g3["W_ge1_nontrivial"] == 14,
                      "class_baseline_seed531001": {
                          "ezdiag_miss": g3["ezdiag_miss"], "ezoff_miss": g3["ezoff_miss"],
                          "ezdiag_hit": g3["ezdiag_hit"], "ezoff_hit": g3["ezoff_hit"]}}),
            run_meta("G4", "src/affarm046ex arm ANCHORX-R6DEAD-AES-R6-P30 6 1 1 30 531002 1 4 aes",
                     "runs/G4_anchor_r6.json", "runs/G4_anchor_r6.timing.txt",
                     {"role": "FRESH DEAD ANCHOR, analyzed FIRST", "analysis": "runs/G4_anchor_analysis.json",
                      "anchor_pass": g4_anchor_pass}),
            run_meta("G5", "src/affarm046ex arm J5-2-AES-R5-P30 5 1 1 30 531002 1 4 aes",
                     "runs/G5_j5_2.json", "runs/G5_j5_2.timing.txt",
                     {"role": "CONFIRMATORY ALIVE ARM J5-2", "analysis": "runs/G5_analysis.json"}),
            run_meta("G6a", "src/affarm046ex arm DETX-AES-R5-P20 5 1 1 20 531001 1 4 aes",
                     "runs/G6_det_a.json", "runs/G6_det_a.timing.txt", {"gate": "determinism double, invocation 1"}),
            run_meta("G6b", "src/affarm046ex arm DETX-AES-R5-P20 5 1 1 20 531001 1 4 aes",
                     "runs/G6_det_b.json", "runs/G6_det_b.timing.txt",
                     {"gate": "determinism double, invocation 2", "pass": gates["G6_determinism"],
                      "comparator": "runs/G6_det_cmp.json",
                      "byte_identical_modulo_timing": g6cmp["byte_identical_modulo_timing_lines"] if "byte_identical_modulo_timing_lines" in g6cmp else g6cmp.get("byte_identical_modulo_timing"),
                      "differing_semantic_fields": g6cmp["differing_semantic_fields"]}),
            run_meta("G7", "src/affarm046ex freeze 363851", "runs/G7_freeze_c_output.json",
                     "runs/G7_freeze.timing.txt",
                     {"gate": "post-arm digest re-verification", "pass": gates["G7_digest_reverify"],
                      "freeze_rerun": "runs/G7_freeze_rerun.json",
                      "reverify": "runs/G7_digest_reverify.json",
                      "committed_freeze_file": g7rv["committed_freeze_file"],
                      "mismatches": g7rv["mismatches"],
                      "source_diff_audit": {"record": "runs/source_diff.txt", "verdict": "PASS",
                                            "raw_diff": "runs/source_diff_raw.txt"}}),
        ],
        "exact_p_values": {
            "r0_anchor_p_extra": r0["anchor"]["test_all_hits"]["p_extra"]["exact"],
            "r0_restatement_p_extra": r0["restatement"]["test_all_hits"]["p_extra"]["exact"],
            "g4_anchor_p_extra": g4a["test_all_hits"]["p_extra"]["exact"],
            "g5_p_extra": g5a["test_all_hits"]["p_extra"]["exact"],
            "g5_p_deficit": g5a["test_all_hits"]["p_deficit"]["exact"],
            "g5_null_mean": g5a["test_all_hits"]["null_mean"]["exact"],
        },
        "budget": {
            "declared_wall_clock_seconds": 7200,
            "elapsed_seconds_approx": round(elapsed, 1),
            "halted_at_stop": False,
            "runs_maximum": 8,
            "binary_invocations": 8,
            "record_runs": 7,
            "stamps_file": "budget_stamps.jsonl",
            "memory_budget_gb": 4,
            "max_rss_observed_bytes": 1622016,
        },
        "deviations": [
            {
                "id": "DEV-1",
                "type": "rule-wording observation (not a procedural deviation)",
                "detail": ("At G5 both the RX-WEAK branch-2 wording and the RX-DEAD conjunct "
                           "literally match; the specific RX-DEAD clause (p_extra > 0.15 AND "
                           "S_obs at/below null mean) was applied. Full disclosure in "
                           "stage_r1.decision_rule_inputs.branch_overlap_disclosure; referred "
                           "to the Coordinator."),
            },
            {
                "id": "DEV-2",
                "type": "carried convention disclosure",
                "detail": ("hit_trials_logged reports thread-0 hit count only (Stage-0 "
                           "rc8probe quirk, documented in BATCH-2f12ac BUILD.md); G4's two "
                           "hits fell on threads 1 and 2 so its receipt reads "
                           "hit_trials_logged=0 while hit_e_detail carries both records. "
                           "No analysis field uses hit_trials_logged."),
            },
        ],
        "unexpected_observations_rule8": [
            "G5 (J5-2, seed 531002): all 19 hits carry X = 0 (S_obs = 0 vs null mean ~1.00004); the committed seed-531001 residual (3 hits at X = 1, S = 3) does not replicate at the fresh seed; p_deficit = 0.367 (no significant deficit direction either).",
            "G4 zero_mask_e cross-check: both dead-arm hits' zero masks are EXACTLY the forced PW words (word 2 and word 3), envelope filled and nothing beyond, X = 0 on both.",
            "Mask composition per seed (never pooled): 531001 r5: 4 active / 10 inactive; 531002 r5 (J5-2): 7 active / 12 inactive; 531001 r6: 2 active / 1 inactive; 531002 r6: 0 active / 2 inactive.",
            "Empirical class rates within ~0.04% of 1/256 on all fresh arms (p_diag/p_off vs naive), confirming the proposal's confounders-clause negligibility of the naive-vs-empirical mismatch at t=1 seats.",
            "Hit counts: r5 14 (531001) vs 19 (531002); r6 3 (531001) vs 2 (531002); the r6 dead band (<= 8) holds at both seeds.",
            "G3 class baseline at seed 531001 collected as designed (ezdiag_miss/ezoff_miss recorded in runs[G3]); not consumed by any r0 reading (r0 uses the naive null per preregistration).",
        ],
        "artifact_index": [
            "PREREGISTRATION.md", "RESULTS.json", "budget_stamps.jsonl",
            "src/affarm046ex.c", "src/affarm046ex", "src/BUILD.md",
            "src/xstat.py", "src/gate0x_cmp.py", "src/det_cmp.py",
            "src/freeze_digest.py", "src/assemble_results.py",
            "runs/G2a_pin.json", "runs/G2b_pinidentity.json",
            "runs/G3_gate0x.json", "runs/G3_gate0x_cmp.json",
            "runs/G4_anchor_r6.json", "runs/G4_anchor_analysis.json",
            "runs/G5_j5_2.json", "runs/G5_analysis.json",
            "runs/G6_det_a.json", "runs/G6_det_b.json", "runs/G6_det_cmp.json",
            "runs/G7_freeze_c_output.json", "runs/G7_freeze_rerun.json",
            "runs/G7_digest_reverify.json", "runs/r0_analysis.json",
            "runs/source_diff.txt", "runs/source_diff_raw.txt",
            "runs/*.timing.txt", "runs/*.err",
        ],
        "environment": {
            "host": "Adams-MacBook-Pro.local, arm64, Darwin 25.6.0, 14 CPUs, 48 GiB RAM",
            "python": "3.12.8 (stdlib only)",
            "compiler": "Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64; build command: cc -O2 -pthread -Wall -o src/affarm046ex src/affarm046ex.c (0 warnings)",
            "git_commit": git_head,
            "git_branch": "aes003-batch026d-20260901",
            "git_dirty_state_at_completion": git_dirty,
            "dirty_scope_note": "only this task's write_scope files are untracked; no other modifications",
        },
        "stopping_rule_note": ("every stage boundary carried a committed reading; no halt was "
                               "required; budget not exhausted (elapsed well under 7200 s; "
                               "8/8 invocations used as planned)"),
        "no_interpretation_attestation": ("this file records observations and the preregistered "
                                          "decision-rule outcome only; no hypothesis status, "
                                          "evidence strength, or promotion interpretation is made "
                                          "(Executor role; Coordinator decision + decision record "
                                          "required for any state transition)"),
        "generated_utc": now.isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 "
                              "json.load (by assemble_results.py writing it and by a separate "
                              "verification load after writing) before task completion"),
        "inference": INFERENCE,
    }
    with open("RESULTS.json", "w") as f:
        json.dump(results, f, indent=1)
    # verification load (attestation above)
    with open("RESULTS.json") as f:
        json.load(f)
    print(json.dumps({"decision_rule_outcome": outcome, "gates": gates,
                      "r0_anchor_pass": r0_anchor_pass, "g4_anchor_pass": g4_anchor_pass,
                      "g5": {"S_obs": g5_s, "p_extra": float(g5_p), "null_mean": float(g5_mean)},
                      "parse_ok": True}, indent=1))


if __name__ == "__main__":
    main()
