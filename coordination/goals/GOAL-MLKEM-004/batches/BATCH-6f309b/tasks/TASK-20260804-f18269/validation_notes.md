# Validation Notes — TASK-20260804-f18269

**Validator task:** TASK-20260804-f18269  
**Producer task:** TASK-20260804-736f46 (repair run of TASK-20260804-27e27b)  
**Snapshot commit:** `3c7032c748bb1d520e1a5cc515535e02cfd6de47`  
**Validated at:** 2026-08-04  
**Inference:** amazon-bedrock/us.anthropic.claude-sonnet-4-6 (review-adversarial, independent session)

---

## Verdict: ACCEPT WITH QUALIFICATIONS

All five required checks passed. One minor provenance qualification is noted but does not affect admissibility.

---

## CHK-1 — Hash check: PASS

All four artifact files were independently SHA-256 hashed and compared against the snapshot receipt at `TASK-20260804-42e24b/snapshot_receipt.json`. Every hash matched exactly, character for character:

| File | Expected | Computed | Match |
|------|----------|----------|-------|
| rebuild_transcript.txt | `4df09ee0...` | `4df09ee0...` | ✓ |
| receipt.json | `28eb9860...` | `28eb9860...` | ✓ |
| variance_results.json | `e9a48ecf...` | `e9a48ecf...` | ✓ |
| report.md | `52aed062...` | `52aed062...` | ✓ |

The commit `3c7032c748bb1d520e1a5cc515535e02cfd6de47` is reachable from `HEAD`, has the declared parent `64d8260e59edea6deefae704e32b7e0d32aaed69`, and introduces exactly these 4 files with no other changes.

---

## CHK-2 — Arithmetic re-derivation of variance_ratio: PASS

The 50 `TN_values` were loaded from `variance_results.json` and all statistics were independently recomputed using Python's standard floating-point arithmetic (no external libraries):

| Statistic | Reported | Independently Computed | Match |
|-----------|----------|------------------------|-------|
| n (TN_values count) | 50 | 50 | ✓ |
| mean(T_N) | 7554.191666525788 | 7554.191666525788 | ✓ |
| var(T_N, ddof=1) | 7296.781604786730 | 7296.781604786730 | ✓ |
| std(T_N) | 85.421201143432 | 85.421201143432 | ✓ |
| independence_predicted_var | 5958.153480907375 | 17919 × 0.332504798309469 = 5958.153480907375 | ✓ |
| variance_ratio | 1.2246716416703476 | 7296.782... / 5958.153... = 1.2246716416703476 | ✓ |

All reported values replicate to floating-point precision (tolerance 1e-6). No fabrication or rounding artifact is present.

---

## CHK-3 — Scope check: PASS

- `states_a_finding: false` — confirmed in `variance_results.json` ✓  
- `compared_against_matzov_nf: false` — confirmed in `variance_results.json` ✓  
- Text search of `variance_results.json` for `MATZOV`, `Nf`, `cost`: **none found** ✓  
- `receipt.json` declares `rule12_status: "UNMET and UNWAIVED"` — correctly self-assesses that no breakthrough review has been conducted (appropriate, since no finding is stated) ✓  
- `report.md` § 4 explicitly states: "**NO FINDING IS STATED.** This report records raw T_N values and the variance ratio as observations only."  
- The `interpretation_note` in `independence_test` block is a neutral definitional statement, not a comparative claim.

The artifact correctly presents itself as a raw observation record with no claimed conclusion.

---

## CHK-4 — Platform and run count: PASS

Platform was confirmed at three independent points:

1. **`variance_results.json`** platform field: `Linux-6.12.76-linuxkit-x86_64-with-glibc2.41` — contains "Linux" and "x86_64" ✓  
2. **`receipt.json`** platform block: `docker_platform: linux/amd64`, `container_uname_m: x86_64`, `emulation: QEMU x86_64 via Docker Desktop` ✓  
3. **`rebuild_transcript.txt`** lines 2–3: `x86_64` (uname -m) and full `uname -a` showing x86_64 GNU/Linux ✓  

The QEMU emulation on ARM64 host is explicitly declared as an infrastructure deviation in `receipt.json` and `report.md`. This is an appropriate use of x86_64 emulation to overcome the original ARM64 build failure (g6k 0.1.2 requires x86 SIMD intrinsics). The emulation does not invalidate the numerical results as a variance measurement.

Run count: `n_runs_completed = 50`, `n_runs_requested = 50`. All 50 `run_records` entries have `valid: true` and `N_vectors: 17919`. Transcript confirms "Completed 50/50 runs". ✓

---

## CHK-5 — Single-score variance cross-check: PASS

The `single_score_var = 0.332504798309469` was cross-checked directly against batch-1's `raw_scores.json` at `BATCH-d2a728/tasks/TASK-20260803-e53ce2/raw_scores.json`.

Procedure: extracted the `scores_cos` array for the `correct` candidate under target `MAIN_lwe_sigma2`, computed sample variance (ddof=1) independently.

| Quantity | Value |
|----------|-------|
| N scores in raw_scores.json | 17919 |
| mean (independently computed) | 0.427375 |
| var (ddof=1, independently computed) | 0.332504798 |
| sqrt → std | 0.576632 |

- `var` matches `single_score_var = 0.332504798309469` to 9 significant figures (tolerance 1e-6) ✓  
- `mean` matches `batch-1 results.json correct_label_mean = 0.427375` ✓  
- `std ≈ 0.5766` matches the "std≈0.5766" reference cited in the handoff ✓  

The independence prediction denominator is correctly sourced from batch-1 data.

---

## Qualification (minor)

**QUAL-1:** The `task` field inside `variance_results.json` reads `TASK-20260804-27e27b` (the original failed task ID, embedded in the script at authoring time) rather than `TASK-20260804-736f46` (the repair task that actually executed the script and produced the file). This is a self-label discrepancy only within `variance_results.json`. The `receipt.json` correctly identifies the file as belonging to `TASK-20260804-736f46` and declares `repair_of: TASK-20260804-27e27b`, so the full provenance chain is traceable. No numerical result is affected. The Coordinator may wish to note this for any future script reuse.

---

## Summary

The run is a clean, complete, and internally consistent 50-run variance measurement. All hashes match, all arithmetic re-derives, the scope is correctly scoped as an observation-only record, the platform is confirmed as x86_64, all 50 runs completed with N=17919, and the single-score variance anchor is verified against batch-1 source data.

**Admissible as a variance measurement for downstream Coordinator synthesis.**

The artifact does not state a finding. Any interpretation of whether `variance_ratio ≈ 1.225` supports or challenges any model is a Coordinator decision, not a validator assertion.
