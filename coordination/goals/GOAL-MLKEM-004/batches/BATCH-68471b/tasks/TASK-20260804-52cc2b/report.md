# TASK-20260804-52cc2b Execution Report

**Task**: TASK-20260804-52cc2b  
**Batch**: BATCH-68471b (batch 3 of 6)  
**Goal**: GOAL-MLKEM-004  
**Role**: Executor  
**Date**: 2026-08-05  
**Status**: COMPLETED  
**states_a_finding**: false  
**compared_against_matzov_nf**: false  

---

## Scope Reminder

This report contains **observations only**. No finding is stated. No comparison
against MATZOV.Nf or any advantage law is made.

**Scale warning**: All parameters are dimension-60, q=127, N=17,919 — NOT
crypto-scale evidence. Nothing observed here bears on FIPS 203 parameter sets or
ML-KEM security.

---

## Context

Batch 2 (BATCH-6f309b, TASK-20260804-736f46) ran 50 sieve realizations and
obtained variance_ratio = 1.2247. The Red Team (OBJ-5) showed this was NOT
statistically significant: chi2(49) = 60.009, p = 0.135, 95% CI [0.855, 1.902].
This batch runs 150 realizations for adequate power (~80% at ratio = 1.22).

Methodological change from batch-2: The independence prediction denominator
(single_score_var) is now computed **within-environment** from run-0's sieve
vectors, rather than loaded from batch-1's raw_scores.json. This makes the
prediction self-contained and removes the cross-session dependency on batch-1
data.

---

## Step 1: Docker Build

**Platform**: Docker --platform linux/amd64, confirmed x86_64.

| Component | Version | Status |
|-----------|---------|--------|
| Host | macOS arm64 (Apple Silicon) | OK — Docker emulates x86_64 |
| Container OS | Debian (python:3.11-slim) | OK |
| Python | 3.11.12 | OK |
| passagemath-standard | 10.8.7 | INSTALLED (binary wheels) |
| fpylll | 0.6.4 | INSTALLED |
| scipy | 1.17.1 | INSTALLED |
| g6k | 0.1.2 | BUILT AND INSTALLED |

**Build note**: `apt-get install autoconf automake libtool libgmp-dev` was
required before `pip install --no-build-isolation g6k`. A symlink
`/usr/local/bin/aclocal-1.16 → /usr/bin/aclocal` was needed because g6k's
build system looks for `aclocal-1.16` while Debian ships automake 1.17 (which
installs `aclocal-1.17`/`aclocal` but not `aclocal-1.16`). This is the same
fix used in BATCH-6f309b TASK-20260804-736f46.

---

## Step 2: Run Execution

All 150 runs completed. No failures.

| Metric | Value |
|--------|-------|
| n_runs_requested | 150 |
| n_runs_completed | 150 |
| sieve algorithm | bgj1_sieve |
| instance_seed | 20260803001 (fixed, same as batch-1/2) |
| fpylll_seed | 20260803005 (fixed, same as batch-1/2) |
| siever_seeds_expression | `numpy.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()` |
| wall_seconds | 2022.8 |

---

## Step 3: Within-Environment Variance Baseline (Run-0)

Single-score statistics derived from run-0 sieve vectors (17,919 vectors):

| Metric | Value |
|--------|-------|
| N_run0 | 17,919 |
| single_score_mean_run0 | 0.414116 |
| single_score_var (ddof=1) | 0.340569 |
| independence_predicted_var = N_0 × Var[s_i] | 6,102.657 |

**Comparison with batch-1/batch-2 baseline**:
- Batch-1 (raw_scores.json) had single_score_var = 0.332505, mean = 0.427375
- Batch-3 run-0 has single_score_var = 0.340569, mean = 0.414116
- The run-0 within-environment measurement differs from the batch-1 mean score
  (0.414 vs 0.427). This is an observation; different sieve seeds produce
  different vector sets. The independence_predicted_var is therefore different
  from that used in batch-2 (batch-2 used 5,958.15; batch-3 uses 6,102.66).

---

## Step 4: T_N Statistics (150 Runs)

| Metric | Value |
|--------|-------|
| empirical_var_TN (ddof=1) | 8,492.310 |
| mean_TN | 7,551.119 |
| std_TN | 92.154 |
| min_TN | 7,334.068 |
| max_TN | 7,791.775 |

---

## Step 5: Chi-Squared Test

H₀: Var[T_N] = N₀ × Var[s_i]  (i.e., variance_ratio = 1.0)

| Statistic | Value |
|-----------|-------|
| chi2_stat | 207.3448 |
| df | 149 |
| p_value | 0.001123 |
| variance_ratio | 1.3916 |
| 95% CI for variance_ratio | [1.1227, 1.7707] |

**H0 rejected at alpha=0.05** (p = 0.001123 < 0.05, two-sided). This is a
pure statistical observation. The 95% CI for variance_ratio excludes 1.0.

---

## Step 6: Mean T_N Cross-Batch Comparison

| Batch | Mean T_N | Source |
|-------|----------|--------|
| Batch-1 (expected) | 7,658.2 | 17,919 × 0.42738 (batch-1 correct score mean) |
| Batch-2 (n=50) | 7,554.2 | empirical from 50 runs |
| Batch-3 (n=150) | 7,551.119 | empirical from 150 runs |

Delta batch-3 vs batch-1 expected: −107.1  
Delta batch-3 vs batch-2: −3.1 (less than 0.04 std units; consistent)

The batch-3 mean is consistent with batch-2. Both batches produce a mean T_N
that is roughly 100 below the batch-1 expected value (17,919 × 0.42738 = 7,658).
This delta is an observation. No comparison against MATZOV.Nf is made.

---

## No Finding

**This is an observation. Batch 4 will assess whether a statistically significant
ratio warrants further investigation.**

The chi-squared test rejects H₀ at alpha=0.05. This is recorded as a
statistical observation, not a finding. Per the binding contract:
- `states_a_finding: false`
- `compared_against_matzov_nf: false`
- No claim that "the independence assumption fails" is made.
- No ML-KEM security implication is drawn.

---

## Rule 12 Status

**rule12_status: UNMET and UNWAIVED**

Rule 12 of AGENTS.md: "Any claim proposed as a breakthrough, closure result,
or contradiction of established evidence must receive independent
`review-breakthrough` review at `max` effort. That review may not be degraded
or run on a backend that cannot reach it."

This task states no finding and no claim. Rule 12 is not triggered by an
observation. No review at `review-breakthrough` has been performed or is being
waived. The status is UNMET and UNWAIVED because no finding is stated.

---

## Anomalies and Deviations

1. **aclocal-1.16 symlink required**: Docker automake 1.17 does not install
   `aclocal-1.16` binary; symlink `/usr/local/bin/aclocal-1.16 → /usr/bin/aclocal`
   was created before g6k build. Identical to the fix in batch-2.

2. **independence_predicted_var differs from batch-2**: Batch-3 uses within-env
   run-0 variance (0.340569, predicted_var = 6102.66) vs batch-2's batch-1 
   raw_scores.json (0.332505, predicted_var = 5958.15). This is by design (the
   task specification mandates within-environment computation for batch-3).

3. **mean_TN offset from batch-1 expected**: Batch-3 mean (7551.1) and batch-2
   mean (7554.2) are both ~107 below batch-1 expected (7658.2). This is an
   observation recorded per executor.md §12. No anomaly note is triggered
   (batch-2 and batch-3 are mutually consistent).

---

## Artifacts

| File | Description |
|------|-------------|
| `variance_test_b3.py` | Adapted batch-3 script (150 runs, randomised seeds, within-env single_score_var, chi2 test) |
| `rebuild_transcript.txt` | Verbatim Docker build log |
| `variance_results.json` | 150 T_N values + chi2 + p-value + 95% CI |
| `report.md` | This file |
| `receipt.json` | Parameters, seeds, git commit, platform |
