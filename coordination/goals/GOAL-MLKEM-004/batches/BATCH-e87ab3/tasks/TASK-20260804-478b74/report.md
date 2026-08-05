# TASK-20260804-478b74 — Gauss Sieve Algorithm Control (Batch 6 of 6, FINAL)

**Goal:** GOAL-MLKEM-004  
**Batch:** BATCH-e87ab3  
**Sieve algorithm:** `gauss_sieve` (g6k 0.1.2)  
**Executor model:** amazon-bedrock/us.anthropic.claude-sonnet-4-6  
**states_a_finding:** false  
**compared_against_matzov_nf:** false  
**rule12_status:** UNMET and UNWAIVED

---

## Purpose

Prior batches 2–5 used `bgj1_sieve`. Batch 3 observed variance_ratio ≈ 1.39
(p ≈ 0.0011, n=150) and batch 5 (null control) observed variance_ratio ≈ 1.53
(p ≈ 0.0096, n=50). The open question was whether the ratio > 1 result is:

- **(A) bgj1-specific QEMU emulation artifact** — bgj1 uses AVX2 SIMD; QEMU may
  introduce correlation in that code path specifically.
- **(B) Algorithm-independent sieve-vector correlation** — would appear in both
  bgj1 and gauss_sieve runs.

This batch runs `gauss_sieve` (combinatorial, no SIMD-specific inner products)
on the identical LWE instance and seeds from a fresh seed expression.

---

## Sieve parameters

| Parameter | Value |
|-----------|-------|
| instance_seed | 20260803001 |
| fpylll_seed | 20260803005 |
| m, n, q | 35, 25, 127 |
| D (lattice dim) | 60 |
| eta, sigma | 2, 2.0 |
| siever_seeds_expr | `numpy.random.default_rng(20260804004).integers(0, 2**32, size=50).tolist()` |
| n_runs_requested | 50 |
| n_runs_completed | 50 |
| stopped_early | false |

---

## Variance test results

| Statistic | Value |
|-----------|-------|
| N_vectors_run0 | 18469 |
| within_env_single_score_var_run0 | 0.350568 |
| independence_predicted_var | 6474.640 |
| empirical_var_TN (ddof=1) | 17896.107 |
| **variance_ratio_gauss** | **2.764** |
| chi2_stat | 135.438 |
| chi2_df | 49 |
| p_value | 4.92 × 10⁻¹⁰ |
| 95% CI for ratio | [1.929, 4.292] |
| mean_TN | 7635.720 |

### Comparison with bgj1_sieve batches

| Batch | Algorithm | n_runs | variance_ratio | p_value |
|-------|-----------|--------|----------------|---------|
| BATCH-d2a728 (batch 1) | bgj1_sieve | 50 | 1.225 (batch-2 formula) | — |
| BATCH-6f309b (batch 2) | bgj1_sieve | 50 | 1.225 | — |
| BATCH-68471b (batch 3) | bgj1_sieve | 150 | 1.392 | 0.00112 |
| BATCH-6ec7a4 (batch 5, null) | bgj1_sieve (wrong secret) | 50 | 1.533 | 0.00959 |
| **BATCH-e87ab3 (batch 6)** | **gauss_sieve** | **50** | **2.764** | **4.92e-10** |

---

## RC-3 cross-run correlation test

Pearson r of T_N[even-indexed] vs T_N[odd-indexed] (25 pairs):

| Statistic | Value |
|-----------|-------|
| r | 0.3025 |
| p (two-tailed) | 0.1416 |
| n_pairs | 25 |

---

## Anomaly: N_vectors varies across gauss_sieve runs

Unlike `bgj1_sieve`, which consistently produced **N=17919** vectors on this
instance across all 200+ prior runs, `gauss_sieve` produced **variable N**:

| N_vectors | Observed in runs |
|-----------|-----------------|
| 18098 | 2 runs (run 16, run 38) |
| 18469 | 31 runs |
| 18848 | 17 runs |

The independence prediction uses `N_run0 = 18469` (fixed). However, the
empirical `Var[T_N]` is computed across runs where `T_N = sum_{i=1}^{N_k} s_i`
with `N_k ∈ {18098, 18469, 18848}`. If the N-count variation is itself a random
variable, then:

```
Var[T_N] = E[N] × Var[s_i] + Var[N] × (E[s_i])²   (law of total variance)
```

The second term adds Var[N] × (mean_score)² ≈ Var[N] × (0.403)² to the total.
The `N_run0`-normalized ratio of 2.764 thus may include a contribution from N
variability, not just score correlation. This observation is recorded for
Coordinator assessment.

---

## Observations (no finding stated)

The gauss_sieve variance_ratio (2.764) is substantially larger than the bgj1
values (1.39 / 1.53) observed in prior batches. The p_value is 4.92 × 10⁻¹⁰.
The RC-3 cross-run correlation (r=0.30, p=0.14) is not significant at α=0.05.

**This is an observation. See coordinator decision for interpretation.**

Contributing factors to be assessed by the Coordinator:
1. N_vectors varies across gauss_sieve runs (18098–18848), unlike bgj1 (constant 17919)
2. The normalization uses N_run0=18469, which may not equal mean(N_vectors)
3. gauss_sieve may produce a qualitatively different score distribution than bgj1
4. gauss_sieve does not use SIMD code paths → any common-factor inflation
   cannot be attributed to bgj1-specific SIMD QEMU emulation

---

## Rule 12 reminder

> **Rule 12 (AGENTS.md):** Any claim proposed as a breakthrough, closure result,
> or contradiction of established evidence must receive independent
> `review-breakthrough` review at `max` effort. That review may not be degraded
> or run on a backend that cannot reach `max`.

**This report does not make such a claim.** The above are observations only.
Status and interpretation remain with the Coordinator.

---

## Artifacts

| File | Description |
|------|-------------|
| `gauss_test.py` | Experiment script |
| `rebuild_transcript.txt` | Docker build + run log |
| `gauss_results.json` | T_N values, variance stats, RC-3 |
| `report.md` | This file |
| `receipt.json` | Full parameter record |
