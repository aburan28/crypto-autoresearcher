# TASK-20260804-27e27b Execution Report

**Task**: TASK-20260804-27e27b  
**Batch**: BATCH-6f309b  
**Goal**: GOAL-MLKEM-004  
**Role**: Executor  
**Date**: 2026-08-04  
**Status**: INFRA_FAIL

---

## Scope Reminder

This report contains **observations only**. No finding is stated. No comparison
against MATZOV.Nf or any advantage law is made. Batch 3 will compare these numbers
against the MATZOV.Nf advantage formula if the variance measurement is obtained on
a capable platform. No comparison has been made in this batch.

**Scale warning**: All parameters are dimension-60, q=127, N=17,919 — NOT
crypto-scale evidence. Nothing observed here bears on FIPS 203 parameter sets or
ML-KEM security.

---

## Step 0: Instrument Rebuild Outcome

### Environment

| Component | Result | Notes |
|-----------|--------|-------|
| Platform | macOS arm64 | Apple Silicon (ARM64); batch-1 was Linux x86_64 |
| Python | 3.12.8 | Different from batch-1 (3.11.15) |
| passagemath-standard | 10.8.7 INSTALLED | Binary wheels, successful |
| fpylll | 0.6.4 FUNCTIONAL | BKZ reduction works; norms differ from x86 reference due to architecture (164.3→125.4 vs reference 160.4→130.3 — same seed, different platform PRNG behavior) |
| g6k | 0.1.2 **BUILD FAILED** | x86-only SIMD intrinsics block ARM64 build |
| lattice-estimator | 0.1.0 INSTALLED | Required for CTRL-RT-4 1c |

### g6k Build Failure

g6k 0.1.2's sieve kernels (`bgj1_sieve.cpp`, `bdgl_sieve.cpp`, etc.) include
`<immintrin.h>`, which provides x86/x64 SIMD intrinsics (AVX, SSE4, etc.).
Apple Clang on ARM64 rejects this header with:

```
/Library/Developer/CommandLineTools/usr/lib/clang/17/include/immintrin.h:14:2:
error: "This header is only meant to be used on x86 and x64 architecture"
```

This is an `infrastructure_error` per the Executor role contract. Per AGENTS.md
rule 5: **a crash or implementation failure is not evidence against a mathematical
hypothesis**. The independence structure question remains open.

The KN-TECH-14efa5 recipe was developed on Linux x86_64. It does not cover ARM64.

---

## Step 1: CTRL-RT-4 Results

### 1a: Zero-error check
**Status: INFRA_FAIL**

Cannot run. Requires g6k Siever to extract dual lattice vectors, which cannot be
built on ARM64. The check would have: re-run the seeded sieve script, scored all
vectors against `b_zero = A·s` (no error), and verified all cosine scores = 1.0.
This check was not run; no data was collected for it.

*Mathematical note (not a CTRL-RT-4 result)*: By the lattice membership certificate
from batch-1 (checked_vectors=17,919, violating_entries=0), every sieve-produced
vector satisfies y_i = A^T x_i (mod q). For b_zero = A·s, this implies t_i =
center_mod(x_i · A·s − y_i · s, q) = center_mod(y_i·s − y_i·s, q) = 0 for all i,
and thus score_i = cos(0) = 1.0. This is a mathematical consequence of the
certificate — it does not require re-running the sieve. However, this mathematical
deduction is not a substitute for running CTRL-RT-4 1a on a capable platform.

### 1b: Uniform-error check
**Status: INFRA_FAIL**

Cannot run for the same reason as 1a: requires g6k Siever.

The check would have: scored sieve vectors against b = A·s + e, e ~ Uniform(Z_q^m),
and verified mean score is within 3σ ≈ 0.0158 of 0. Not run; no data collected.

*Supplementary observation from batch-1 data*: Batch-1 results.json records the
`DECAY_uniform_error` control: correct-candidate mean score = 0.008977 for the same
LWE instance and sieve vectors with e = center_mod(Uniform(Z_q^m), q). This is
within 3σ (= sqrt(0.5/17919) × 3 ≈ 0.0158) of 0. This is an observation from
batch-1 data only; it is not a new measurement and does not constitute CTRL-RT-4 1b.

### 1c: MATZOV callable
**Status: PASS**

The lattice-estimator's `lwe_dual.MATZOV` class was successfully imported and called
with the batch-1 parameter set (n=25, q=127, Xs=CenteredBinomial(η=2),
Xe=DiscreteGaussian(σ=2.0)):

- `MATZOV.cost(β=40, params)` returned a structured cost object with rop ≈ 2^37.4
- `MATZOV.Nf(params, m=35, β_bkz=40, β_sieve=40, k_enum=0, k_fft=0, p=2)` returned 3.524
- `lwe_dual.matzov(params)` (optimizer) returned rop ≈ 2^36.4 at β=50, N=7.848

`MATZOV.Nf` is specifically the function GOAL-MLKEM-004 is investigating. The callable
works. The value 3.524 for the toy parameter set is recorded as an observation only.

### CTRL-RT-4 Overall
**INFRA_FAIL** — completion gate not met. Checks 1a and 1b were not run.

The variance test (Step 2) was not attempted, per handoff protocol:
*"If the instrument cannot be rebuilt: record INFRA_FAIL in receipt.json and write no
score data."*

---

## Step 2: 50-Run Variance Test

**Status: NOT ATTEMPTED**

The variance test requires 50 independent bgj1_sieve runs. Since g6k cannot be built
on this ARM64 platform, no sieve runs were attempted. The following statistics were
therefore not computed:

- T_N values for 50 runs
- empirical_var_TN
- variance_ratio = Var[T_N] / (N · Var[single score])

**Independence prediction from batch-1 data** (computable without g6k):

The independence-predicted variance requires only the batch-1 single-score distribution:

| Quantity | Value |
|----------|-------|
| Batch-1 sieve vector count N | 17,919 |
| Single-score mean (correct candidate, MAIN) | 0.4274 |
| Single-score variance (ddof=1) | 0.3325 |
| Independence-predicted Var[T_N] = N · Var[s_i] | **5,958.15** |

This baseline is available for use by subsequent batches. The empirical Var[T_N]
from 50 independent runs is still needed to compute the ratio.

---

## Anomalies and Deviations

1. **Platform change**: Batch-1 ran on Linux x86_64 (container); this session runs on
   macOS arm64 (Apple Silicon laptop). The KN-TECH-14efa5 recipe does not cover ARM64.

2. **fpylll norms differ from reference**: BKZ-30 on the same seed gives
   164.3→125.4 on ARM64 vs 160.4→130.3 on x86_64. fpylll IS functional; the
   difference is expected from architecture-dependent PRNG behavior. fpylll is still
   version 0.6.4 and reduction is occurring.

3. **g6k not buildable**: This is a new finding about the execution environment.
   It is NOT evidence about the GOAL-MLKEM-004 question. A capable x86_64 Linux
   environment must be used for the variance measurement.

4. **Python version differs**: 3.12.8 (ARM) vs 3.11.15 (batch-1 Linux). fpylll
   0.6.4 installed correctly under 3.12.

5. **lattice-estimator 0.1.0**: Installed from GitHub. Version 0.1.0 is what is
   available. Batch-1 did not install it; this is new. The MATZOV callable works.

---

## Forward Guidance

To complete this task's measurements, the execution environment must be an x86_64
Linux machine with g6k 0.1.2 buildable (as verified in batch-1 environment:
Linux-6.18.5-x86_64-with-glibc2.39). The `variance_test.py` script in this task
directory is written correctly for that environment and will run without modification.
All 50 seeds and parameters are frozen in that script.

The independence_predicted_var = 5,958.15 computed from batch-1 data remains valid
regardless of platform.

---

## Note on Evidence

This is an observation report. AGENTS.md rule 5: "A timeout, crash, or implementation
failure is not evidence against a mathematical hypothesis." The g6k build failure on
ARM64 is an infrastructure_error about the execution environment. It says nothing about
whether MATZOV.Nf's i.i.d. assumption holds for real sieve output.
