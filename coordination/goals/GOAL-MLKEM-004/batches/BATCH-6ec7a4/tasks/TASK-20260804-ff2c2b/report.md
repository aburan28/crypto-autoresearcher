# TASK-20260804-ff2c2b Execution Report

**Task:** TASK-20260804-ff2c2b  
**Batch:** BATCH-6ec7a4  
**Goal:** GOAL-MLKEM-004  
**Role:** Executor  
**states_a_finding:** false  
**compared_against_matzov_nf:** false  
**rule12_status:** UNMET and UNWAIVED  
**Date:** 2026-08-04

---

## Summary

Both Test A (null control, n=50) and Test B (outlier seed re-run, n=4) completed successfully in Docker linux/amd64 QEMU emulation. 54/54 total sieve runs valid.

---

## Protocol Deviations

The handoff-specified Docker command (`apt-get install -y -qq gcc g++ make`) was **insufficient** to build g6k 0.1.2:

1. **`autoconf` and `automake` missing from install line.** g6k requires `automake` for its autotools build system. These were added. The batch-3 rebuild transcript confirms both were installed in that run (transcript line 65-73).

2. **`aclocal-1.16` symlink required.** g6k's `setup.py` invokes `make`, which calls `aclocal-1.16`. The installed automake provides only `aclocal-1.17`. Batch-3 included a "FIX aclocal VERSION SYMLINK" step (transcript lines 300-303) that created `ln -sf /usr/bin/aclocal /usr/local/bin/aclocal-1.16`. This step was reproduced. Without it, the `make` step fails with `aclocal-1.16: command not found`.

These two deviations were required to reproduce the stated intent: "same environment as batch-3." The corrections match batch-3's confirmed working environment exactly. The sieve vectors and T_N values are unaffected by the symlink (it only affects the build step, not execution).

Additionally: Docker's root filesystem ran out of space on the first attempt (`[Errno 28] No space left on device`). `docker system prune -f` reclaimed 27.66 GB. The second attempt succeeded. The failed attempt produced no score data.

---

## Test A — Null Control (50 runs, wrong secret s_wrong)

**Setup:**
- LWE instance: `instance_seed=20260803001`, `fpylll_seed=20260803005` (same as batch-3)
- Wrong secret: `wrong_secret_seed=20260804999` → centered-binomial CB(η=2), n=25 components
- s_wrong ≠ s_correct verified: 23 of 25 coordinates differ
- Phase: x·b − y·s_wrong = x·e + y·(s − s_wrong) ≠ x·e (wrong-secret, no clean collapse)
- 50 null seeds from `numpy.random.default_rng(20260804002).integers(0, 2**32, size=50)`
- Platform: Linux-6.12.76-linuxkit-x86_64-with-glibc2.41 (QEMU linux/amd64)

**Measurements:**
| Statistic | Value |
|---|---|
| n_runs_completed | 50 / 50 |
| null_single_score_mean (run-0) | 0.230835 |
| null_single_score_var (run-0) | 0.446341 |
| null_predicted_var = N₀ × ssv | 7997.993 |
| mean(T_N_null) | ~4163 |
| std(T_N_null) | ~110.8 |
| empirical_var(T_N_null) | ~12269 |
| **variance_ratio_null** | **1.5332** |
| chi2_stat | 75.125 |
| df | 49 |
| **p_value_null** | **0.009589** |
| 95% CI variance_ratio | [1.0698, 2.3808] |

**Observations:**
- The null mean T_N (~4163) is substantially lower than the correct-secret batch-3 mean T_N (~7551), as expected when scoring against a wrong secret with 23/25 components differing.
- The null variance_ratio = 1.5332 is greater than 1.0 (p = 0.0096, n=50).
- The null 95% CI [1.07, 2.38] substantially overlaps the batch-3 correct-secret 95% CI [1.12, 1.77].
- The null single_score_var (0.446) is larger than the correct single_score_var (0.341); consequently the null_predicted_var (7998) is larger than the correct predicted_var (6102).
- Both the null and correct-secret signals exhibit empirical variance exceeding the independence prediction in this QEMU environment.

No finding is stated.

---

## Test B — Outlier Seed Re-run (4 seeds)

**Setup:**
- Same LWE instance (instance_seed=20260803001, fpylll_seed=20260803005)
- 4 seeds tested: 2941775225, 26883012, 2418421570, 1873347320
- For each seed: T_N_correct and T_N_wrong both computed

**Results:**
| Seed | T_N_correct (this run) | T_N_correct (batch-3) | Delta | T_N_wrong |
|---|---|---|---|---|
| 2941775225 | 7789.567405817314 | 7789.567405817314 | **0.000** | 4167.083 |
| 26883012 | 7791.775311646041 | 7791.775311646041 | **0.000** | 4433.895 |
| 2418421570 | 7789.812131511126 | 7789.812131511126 | **0.000** | 4238.163 |
| 1873347320 | 7420.548667265 | 7420.548667265 | **0.000** | 4178.842 |

**Observations:**
- T_N_correct values are bit-for-bit identical to batch-3 across all 4 seeds (delta = 0.000 in all cases). The QEMU environment is deterministic: identical seeds, instance, and platform produce identical results.
- The 3 high-T_N seeds (2941775225, 26883012, 2418421570) consistently produce T_N_correct ≈ 7789–7792, reproducing the elevated batch-3 observations. These are **not one-time fluctuations**.
- The run-0 seed (1873347320) reproduces T_N_correct = 7420.549, consistent with batch-3.
- T_N_wrong for the high-T_N seeds (~4167–4434) falls near the null distribution mean (~4163), not near the correct T_N (~7790). The batch-3 outlier seeds' high T_N values are specific to the correct-secret scoring.

No finding is stated.

---

## Anomalies and Unexpected Observations

1. **Null variance_ratio > 1:** The null control also shows variance_ratio > 1 (1.5332, p=0.0096). The n=50 estimate has wider confidence intervals [1.07, 2.38] than the batch-3 correct estimate (n=150, CI [1.12, 1.77]). The overlap between these intervals is substantial.

2. **Null predicted_var > correct predicted_var:** null_ssv=0.446 vs correct_ssv=0.341. The wrong-secret scores have higher within-run variance, which is expected: without the signal component (which pulls phases near zero), the wrong-secret phases are more dispersed across [−q/2, q/2], producing higher cosine variance.

3. **Floating-point identity in outlier re-runs:** All 4 outlier seed T_N_correct values reproduced to zero delta vs batch-3. This confirms the QEMU environment is numerically deterministic.

---

## Budget
- Runs: 54 (50 null + 4 outlier). Budget: 54. Within budget.
- Wall time: ~727 seconds total (sieve runs only); Docker startup + install ≈ additional ~730s overhead.
- Memory: 8g Docker limit; not exceeded.

---

## Artifact Paths

- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/null_variance_test.py`
- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/rebuild_transcript.txt`
- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/null_control_results.json`
- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/outlier_rerun_results.json`
- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/report.md`
- `coordination/goals/GOAL-MLKEM-004/batches/BATCH-6ec7a4/tasks/TASK-20260804-ff2c2b/receipt.json`

---

*This report states no finding. All results are observations. Interpretation and official state transitions are the Coordinator's responsibility.*
