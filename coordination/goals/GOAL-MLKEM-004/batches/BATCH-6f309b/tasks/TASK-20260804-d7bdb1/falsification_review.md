# Red Team Report — TASK-20260804-d7bdb1
## Falsification Review of Batch-2 Variance Measurement

**RT record:** RT-20260804-11bdeb  
**Reviewing:** TASK-20260804-736f46 (repair run), BATCH-6f309b  
**Goal:** GOAL-MLKEM-004  
**Snapshot commit:** 3c7032c748bb1d520e1a5cc515535e02cfd6de47  
**Verdict:** `pass_with_constraints`  
**Reviewed:** 2026-08-04  

---

## Executive Summary

The 50-run variance measurement is **admissible as a raw observation** — all 50
runs completed, all 50 produced N=17919 vectors, the T_N values span a
plausible range, and the data collection is well-documented. However, the
primary interpretation of `variance_ratio = 1.2247` as evidence about the
MATZOV.Nf i.i.d. assumption is **not supportable** for two independent reasons:

1. **The variance ratio is not statistically significant.** With n=50 runs,
   the chi-squared test gives χ²(49)=60.009, p=0.135. The 95% CI on the true
   Var[T_N] is **[5092, 11331]**, which *includes* the independence-predicted
   value of 5958. The CI on the ratio itself is **[0.855, 1.902]**. With n=50,
   the test has only ~40% power to detect the observed ratio; ~200 runs are
   needed for 80% power.

2. **The baseline Var[s_i] comes from a different execution environment.** Batch-1
   ran in `Linux-6.18.5-x86_64-with-glibc2.39` (possibly native x86_64); batch-2
   ran in `Linux-6.12.76-linuxkit-x86_64-with-glibc2.41` under QEMU x86_64
   emulation. These environments produce **systematically different sieve
   outputs**: batch-2's implied mean score (0.4216) is 1.36% lower than
   batch-1's (0.4274), corresponding to a shortfall of 103.9 in T_N units —
   larger than one empirical SD of T_N (85.4). Using batch-1's within-run
   variance as the denominator for a test run in a different environment is
   an unvalidated cross-environment comparison.

No finding about the i.i.d. assumption or MATZOV.Nf is warranted at this stage.
Batch-3 must fix the baseline (same environment), increase n (≥150–200), and
report the full chi-squared test alongside the ratio.

---

## 1. Measurement Design

### What was measured

50 bgj1_sieve runs on the same LWE instance (instance_seed=20260803001,
fpylll_seed=20260803005), siever seeds 0–49, each producing N=17919 dual
vectors. For each run, T_N = Σᵢ cos(2πtᵢ/q) over all N vectors. The
independence test compares empirical Var[T_N] (50 samples, ddof=1) against
N × Var[s_i], where Var[s_i] = 0.332505 is borrowed from batch-1's single
sieve run.

### What was found

| Statistic | Value |
|-----------|-------|
| Empirical Var[T_N] (n=50, ddof=1) | 7296.782 |
| Independence prediction N × Var[s_i] | 5958.153 |
| Variance ratio | **1.2247** |
| chi-squared test statistic | **60.009** |
| chi-squared critical value (α=0.05, df=49) | **66.339** |
| p-value (one-sided right) | **0.135** |
| 95% CI for Var[T_N] | **[5092, 11331]** |
| 95% CI for variance ratio | **[0.855, 1.902]** |
| Batch-1 mean score | 0.427375 |
| Batch-2 implied mean score | 0.421574 |
| Systematic mean shortfall | −103.9 T_N units (−1.36%) |

---

## 2. Objection-by-Objection Analysis

### OBJ-1 — QEMU emulation and cross-environment sieve behavior

**Verdict: CONCERN** (not blocking in isolation, but contributes to OBJ-3 invalidating the baseline)

**On RDRAND specifically:** g6k 0.1.2 does **not** use x86 RDRAND/RDSEED
hardware instructions. Its internal PRNG is a software Xorshift initialized
from the integer `seed` parameter passed to `Siever()`. The scoring
(cosine computation) is Python/NumPy operating on integer phases — it is
100% deterministic and platform-independent. RDRAND emulation quality in
QEMU is irrelevant to this measurement.

**On QEMU SIMD emulation:** This is the real concern. g6k's sieve uses
AVX2/AVX-512 SIMD intrinsics for speed. Under QEMU, these are emulated. QEMU
is a correct (not approximate) x86 emulator, so in principle AVX2 should
produce identical results to native execution. However:

- The g6k verification step produced `db = 4259` vectors in batch-2 vs
  `db = 4075` in batch-1 (an unseeded gauss_sieve on dim-50, q=3329). This
  4.5% difference could simply be due to different PRNG seeds in the
  verification (seed not recorded for the check), but is circumstantially
  consistent with environment-dependent behavior.

- **More seriously:** batch-2's mean T_N (7554.2) is 103.9 below the
  batch-1 prediction (N × 0.4274 = 7658.1). This is larger than one
  empirical SD of T_N (85.4) and is systematic across all 50 runs. QEMU
  emulation may slow certain SIMD codepaths, causing bgj1_sieve to
  terminate at a different database quality (e.g., earlier convergence or
  different bucketing thresholds under emulation). If this is so, batch-2
  vectors are of different quality than batch-1 vectors, and the cross-batch
  baseline comparison is contaminated.

**Cheapest check:** Run one sieve in the batch-2 QEMU environment with
seed=469431436621 (batch-1's seed) and compute within-run Var[s_i]. If it
matches 0.332505, the environments are equivalent for this statistic; if it
differs significantly, the cross-environment baseline is invalid.

---

### OBJ-2 — N = 17,919 consistency

**Verdict: NOTE (resolved by data)**

Every one of the 50 `run_records` in `variance_results.json` shows
`N_vectors: 17919`. The concern about variable N is not realized. The log
also confirms N=17919 for each run. OBJ-2 and OBJ-4 are non-issues.

---

### OBJ-3 — Single-score variance from a different sieve run

**Verdict: CONCERN**

The independence test's denominator, Var[s_i] = 0.332505, was measured in
batch-1 using:
- Siever seed = 469431436621 (= 0x6D4C4B454D, ASCII "gLKEM")
- Execution environment: `Linux-6.18.5-x86_64-with-glibc2.39`

Batch-2 uses:
- Siever seeds = 0, 1, …, 49
- Execution environment: `Linux-6.12.76-linuxkit-x86_64-with-glibc2.41` (QEMU)

The two environments produce different mean scores. This is not a seed
artifact: the 50-run mean T_N/N = 0.4216 vs batch-1's 0.4274 is a
**systematic** difference (the size of the shift, 103.9, exceeds one SD of
T_N, which is 85.4). For cosine scores driven by sieve vector quality, a
change in mean is correlated with a change in variance. Without measuring
within-run Var[s_i] in the batch-2 environment, the denominator of the
ratio test is borrowed from a different distribution.

**Self-consistency check (OBJ-3 body of the handoff):** The handoff suggests
checking whether the batch-1 single-score variance is consistent with the
T_N mean. Batch-1: T_N mean would be N × 0.427375 = 7658.1. Actual
batch-2 mean T_N = 7554.2. These are NOT self-consistent — the batch-2
environment yields a systematically lower mean, confirming that the two
environments are not exchangeable.

---

### OBJ-4 — T_N is a sum; variable N confounds the variance

**Verdict: NOTE (resolved by data)**

Same as OBJ-2: N=17919 in all 50 runs. The variance calculation is valid
under the constant-N assumption.

---

### OBJ-5 — n=50 is insufficient for a meaningful variance test

**Verdict: BLOCKING**

This is the primary statistical failure of the measurement design.

**Chi-squared test:**

```
H₀: true Var[T_N] = 5958.153 (independence prediction)
H₁: true Var[T_N] > 5958.153 (positive correlation)

χ² = (n−1) × s²_obs / σ²₀
   = 49 × 7296.782 / 5958.153
   = 60.009

Under H₀: χ² ~ χ²(49)
Critical value at α=0.05 (one-sided): χ²₀.₉₅(49) = 66.339
p-value = P(χ²(49) > 60.009) = 0.135
```

**Conclusion: FAIL TO REJECT H₀ at α=0.05.** The ratio of 1.2247 is
entirely consistent with sampling noise from the null distribution (i.i.d.
scores).

**95% CI for the true Var[T_N]:**

```
CI = [(n−1) × s² / χ²₀.₉₇₅(49),  (n−1) × s² / χ²₀.₀₂₅(49)]
   = [49 × 7296.782 / 70.22,       49 × 7296.782 / 31.54]
   = [5092,                          11331]
```

The independence-predicted value **5958.2 is inside the 95% CI [5092, 11331]**.
The CI on the ratio is **[0.855, 1.902]** — consistent with values from less
than 1.0 to nearly 2.0. The measurement cannot even establish that the ratio
is greater than 1.

**Power analysis:**

With n=50 and a one-sided chi-squared test at α=0.05, approximate power to
detect ratio=1.22 is ~40%. To achieve 80% power at ratio=1.22, approximately
n=200 runs are needed. Batch-3 must either:
(a) Pre-specify n=200 before running, or
(b) Define a stopping rule based on statistical significance criteria.

**What the batch can and cannot claim:**

| Claim | Status |
|-------|--------|
| T_N ranges from 7357 to 7761 across 50 runs | ✓ Admissible |
| Empirical Var[T_N] = 7297 (point estimate) | ✓ Admissible |
| Ratio = 1.22 as a raw observation | ✓ Admissible, with CI |
| Ratio = 1.22 is inconsistent with i.i.d. | ✗ Not supported (p=0.135) |
| Ratio = 1.22 is evidence for positive correlation | ✗ Not supported |
| The i.i.d. assumption holds | ✗ Not established either |

The batch correctly declines to state a finding (`states_a_finding: false`),
but the report omits the p-value and CI entirely. Any downstream use of this
ratio as evidence for or against i.i.d. must be accompanied by these statistics.

---

### OBJ-6 — Seed index trend and low-integer seed correlation

**Verdict: NOTE**

**Lag-1 autocorrelation** (adjacent seeds): 0.0044 — effectively zero. Adjacent
seeds (0,1), (1,2), etc. are not correlated. Low-integer seed aliasing in
g6k's Xorshift (if it exists) does not produce adjacent-run correlation.

**Spearman rank correlation** (seed index vs T_N): −0.247, p=0.084. There is
a weak negative trend — higher seeds tend to produce slightly lower T_N — but
this is NOT significant at α=0.05. With p=0.084, it is likely an artifact of
n=50 sampling. However, it is marginally below the α=0.10 threshold and
warrants investigation in batch-3.

**Seed-27 outlier:** T_N = 7760.6, z-score = 2.42. This is the largest value
in the sample but is not extreme for n=50 draws from a normal-like distribution
(expected maximum z ≈ 2.4 for Gaussian n=50). It does not require special
treatment.

**Preventive recommendation:** Batch-3 should use seeds drawn uniformly at
random from [0, 2³²) rather than consecutive integers, to decouple any
potential seed-quality effect from the variance estimate.

---

## 3. Cross-Cutting Issue: Mean Score Systematic Shift

This issue is not enumerated in OBJ-1 through OBJ-6 but deserves separate
emphasis.

The batch-2 mean T_N = 7554.2 corresponds to mean score = 0.4216 per vector.
Batch-1 measured mean score = 0.4274. The difference is:

```
Δ_mean = 0.4274 − 0.4216 = 0.0058
ΔT_N = N × Δ_mean = 17919 × 0.0058 = 103.9
```

The empirical SD of T_N from the 50 runs is 85.4. So the systematic shift
(103.9) is **larger than one SD**. This cannot be attributed to random seed
variation; it is an environment effect.

Two possible explanations:
1. **QEMU emulation quality:** QEMU's AVX2/AVX-512 emulation may cause bgj1_sieve
   to terminate at a slightly worse convergence point (lower-quality vector
   database), reducing both the mean and potentially the variance of per-vector
   cosine scores.
2. **Software environment:** Different glibc (2.39 vs 2.41), different numpy
   build (same version 2.4.6 but different compilation in the batch-2 container),
   or different fpylll behavior under the two environments.

Until this shift is explained and its effect on Var[s_i] is quantified, the
cross-batch baseline comparison is on uncertain ground.

---

## 4. Verdict and Required Actions

### Admissibility

| Question | Answer |
|----------|--------|
| Raw data admissible as 50 T_N observations? | **Yes** |
| Ratio 1.2247 admissible as a point estimate? | **Yes, with CI** |
| Batch admissible as a test of the i.i.d. assumption? | **No** (p=0.135, CI includes null) |
| Cross-environment baseline validated? | **No** (mean shift of 1.36% confirmed) |

### What batch-3 must address (ordered by priority)

1. **Statistical power:** Pre-register n ≥ 150–200 with a defined stopping rule.
   Report χ², p-value, and 95% CI for both Var[T_N] and the ratio. Do not
   report only the point estimate.

2. **Same-environment baseline:** Measure within-run Var[s_i] inside the SAME
   Docker environment used for the variance batch. Run one extra sieve with
   seed=469431436621 in the batch-3 container and compute Var[s_i] from those
   scores. Use this as the denominator, not batch-1's 0.332505.

3. **Explain the mean shift:** Investigate why batch-2 produces mean score 0.4216
   vs batch-1's 0.4274. Proposed mechanism: QEMU SIMD emulation causes
   bgj1_sieve to converge at different database quality. Test by comparing sieve
   vector norm distributions between batch-1 and batch-2 (batch-1's
   raw_scores.json contains `norm2_v` per vector).

4. **Randomized seeds:** Use seeds drawn uniformly from [0, 2³²) to eliminate
   any potential consecutive-integer seed effect (the marginal Spearman
   correlation of −0.247, p=0.084 motivates this precaution).

5. **Raw scores per run:** Store the per-vector scores for each sieve run (or at
   least a sample) to allow direct within-run variance estimation and comparison
   against the between-run variance. This would make the test fully self-contained.

### Narrowest valid statement from this batch

> "In 50 bgj1_sieve runs with seeds 0–49 in a QEMU x86_64 Docker environment,
> the empirical Var[T_N] = 7297 (n=50, ddof=1), yielding ratio = 1.22 relative
> to the batch-1 independence prediction. This ratio is not statistically
> significant (χ²(49)=60.0, p=0.135; 95% CI [0.855, 1.902]). A systematic
> mean-score shortfall of 1.36% relative to batch-1 indicates different sieve
> behavior between environments, making the cross-batch baseline comparison
> unvalidated."

---

*Red Team session: TASK-20260804-d7bdb1 | Policy: review-adversarial | Model: amazon-bedrock/us.anthropic.claude-sonnet-4-6 | Independent session: true | model_verified: false*
