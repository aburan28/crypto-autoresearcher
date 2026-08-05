# Falsification Review — GOAL-MLKEM-004 BATCH-e87ab3, Batch 6 of 6

**Red Team task:** TASK-20260804-5d4bfa  
**Producer task:** TASK-20260804-478b74 (gauss_sieve final control)  
**Snapshot commit:** `891f85dd6060ef55e3c9b87e91c38e851c0e6c89`  
**Verdict:** **blocking_objections**  
**Reviewed at:** 2026-08-05

---

## Executive summary

The executor's work (TASK-20260804-478b74) is technically sound: gauss_sieve ran
correctly, all 50 runs completed, the N-variability anomaly was flagged explicitly,
and no finding was stated. The objections below are directed at the **Coordinator's
proposed interpretation** — specifically the N-variability correction formula and
the campaign conclusion that gauss_sieve confirms an algorithm-independent effect.

**The Coordinator's corrected ratio (~1.255) is computed under an independence
assumption that is false.** The correct within-group analysis yields ratio ≈ 0.92
(p ≈ 0.52), which reverses the conclusion: gauss_sieve shows NO excess variance
after conditioning on N, while bgj1 shows a stable excess (ratio 1.39). This is
consistent with a bgj1-specific (SIMD/AVX2 QEMU emulation) artifact, not an
algorithm-independent sieve-vector correlation.

---

## OBJ-1 (BLOCKING): Coordinator correction formula assumes N ⊥ T_N — violated at r = 0.82

### The formula and its assumption

The Coordinator applied:

```
Var_total = E[N] × Var[s] + Var[N] × (E[s])²
         = 18613.34 × 0.350568 + 45919.21 × (0.4102)²
         = 6525.24 + 7727.62
         = 14,252.86
```

This is the **independent-N law of total variance**:

> Var[T_N] = E[N] Var[s] + Var[N] (E[s])²
> holds **only when** N ⊥ {s_j}

### Why the assumption fails

Measured from the 50 run records:

| Statistic | Value |
|-----------|-------|
| Pearson r(N, T_N) | **0.820** |
| p-value | **3.3 × 10⁻¹³** |
| r² | 0.672 (67.2% of Var[T_N] explained by N) |

The N-class conditional means confirm the direction:

| N class | n runs | mean T_N | mean score (T_N/N) |
|---------|--------|----------|-------------------|
| 18,098  | 2      | 7,378.24 | 0.4077 |
| 18,469  | 27     | 7,560.93 | 0.4094 |
| 18,848  | 21     | 7,756.40 | 0.4115 |

More vectors → higher mean score per vector. This is physically plausible:
gauss_sieve terminates by stagnation; runs that continue longer (larger N) have
collected more reduction steps, yielding shorter, geometrically more
favorable vectors with slightly higher cosine scores.

### The correct decomposition

The **full** law of total variance is:

```
Var[T_N] = E[Var[T_N | N]]  +  Var[E[T_N | N]]
```

Measured from data:

| Component | Value | Source |
|-----------|-------|--------|
| E[Var[T_N\|N]] (weighted within-group var) | 6,002.7 | within-group empirical variances |
| Var[E[T_N\|N]] (variance of group means)   | 12,030.3 | N-class conditional means |
| Sum (≈ Var[T_N]) | 18,033.0 | vs empirical 17,896 ✓ |

The **N-variability** component is 12,030, not the Coordinator's 7,728. The
difference arises entirely from the N–score correlation: Var[N × E[s|N]] ≠
Var[N] × E[s]² when N and E[s|N] are positively correlated.

### The correct corrected ratio

```
within-group corrected ratio = E[Var[T_N|N]] / (E[N] × Var[s])
                              = 6,002.7 / 6,525.2
                              = 0.920
```

Versus the Coordinator's 1.255. The correct ratio is **less than 1.0**, meaning
gauss_sieve shows no excess inter-run variance once N is conditioned out.

---

## OBJ-2 (BLOCKING): Within-group chi-squared tests both fail to reject H₀

For the two N-classes with adequate sample size:

| N class | n | within-ratio | chi2(df) | p-value | Interpretation |
|---------|---|-------------|----------|---------|----------------|
| 18,469 | 27 | 0.955 | chi2(26)=24.82 | **0.529** | H₀ not rejected |
| 18,848 | 21 | 0.958 | chi2(20)=19.15 | **0.512** | H₀ not rejected |

(N=18,098 has 2 runs — 1 degree of freedom — and is uninformative.)

Both p-values are near 0.5, the median of the null distribution. There is no
evidence of excess variance within either N class. This is the opposite of the
bgj1 result (chi2(149)=207.3, p=0.00112), which rejects H₀ strongly.

**The campaign conclusion "algorithm-independent result" is unsupported. The data
support the complementary conclusion: algorithm-DEPENDENT, bgj1-specific.**

---

## OBJ-3 (MODERATE): RC-3 r = 0.30 is an N-confound artifact

The raw RC-3 test correlates T_N values at even indices with T_N values at odd
indices. Since r(N, T_N) = 0.82, any accidental N imbalance between the two
sub-sequences inflates the correlation.

After regressing N out of both T_N_even and T_N_odd independently:

| Quantity | Value |
|----------|-------|
| Raw RC-3 r | 0.302, p = 0.142 |
| N-residualized RC-3 r | **−0.063, p = 0.765** |

The N-residualized RC-3 is consistent with zero sequential correlation. The
executor's report correctly notes the raw r is not significant, but the
N-confound mechanism is not identified. The QEMU-state-leakage hypothesis is
not supported by this data.

---

## OBJ-4 (MODERATE): Raw ratio table mixes non-comparable denominators

The report.md comparison table lists:

| Batch | Algorithm | variance_ratio |
|-------|-----------|----------------|
| BATCH-68471b | bgj1_sieve | 1.392 |
| BATCH-6ec7a4 | bgj1 null | 1.533 |
| **BATCH-e87ab3** | **gauss_sieve** | **2.764** |

These ratios use different denominators:
- bgj1: N_bgj1 × Var[s_bgj1] = 17919 × 0.3406 = 6103
- gauss: N_run0 × Var[s_gauss] = 18469 × 0.3506 = 6475

The gauss_sieve denominator is **6% larger**, and more importantly, the gauss
denominator uses a single fixed N while the actual T_N values span N ∈ {18098,
18469, 18848}. The ratio 2.764 is not a comparable measure of "excess variance."
Presenting it alongside bgj1 ratios without correction note is misleading.
Var[s_gauss]/Var[s_bgj1] = 1.029 (3%); the score distribution difference is
minor and is not the driver.

---

## What the executor did correctly

The executor (TASK-20260804-478b74) is **not** the subject of these objections:

1. Ran gauss_sieve with frozen parameters; 50/50 valid runs completed.
2. Explicitly flagged N-variability as a methodological concern requiring
   Coordinator attention (`protocol_deviations[0]`).
3. Correctly stated no finding (`states_a_finding: false`).
4. Recorded `rule12_status: "UNMET and UNWAIVED"`.
5. Reported RC-3 without overinterpreting it.
6. Recorded anomalies faithfully.

The executor fulfilled its role correctly. The objections concern the
interpretation layer applied on top of the executor's output.

---

## Required controls before campaign conclusion

### RC-A (HIGH PRIORITY): gauss_sieve with fixed N cap

Run gauss_sieve with `--database-size-limit 18469` (or equivalent g6k parameter)
so every run terminates with exactly the same N. This eliminates N variability
entirely and produces a ratio directly comparable to bgj1. If ratio ≈ 0.95–1.05,
the algorithm-independence hypothesis is rejected; if ratio ≈ 1.4, it is
supported.

### RC-B (HIGH PRIORITY): bgj1 on native x86_64

Rerun bgj1_sieve on native x86_64 hardware (same g6k version, same LWE instance,
same seeds) without QEMU emulation. If ratio drops to ≈ 1.0, the bgj1 inflation
is a confirmed QEMU/AVX2 emulation artifact. This is the cheapest discriminant
between "environment artifact" and "mathematical signal."

### RC-C (MEDIUM): Per-vector score autocorrelation within each run

Compute lag-1 to lag-10 autocorrelation of the score sequence within each run
for both bgj1 and gauss_sieve. A positive lag-1 autocorrelation in bgj1 but not
gauss_sieve would directly identify the correlation structure producing the excess
variance in bgj1 without any N-variability confound.

---

## Narrowest supported campaign statement

> bgj1_sieve in Docker linux/amd64 QEMU on Apple Silicon shows excess cross-run
> T_N variance (ratio = 1.392, n=150, chi2(149)=207.3, p=0.00112) that is
> present regardless of whether the correct or a wrong secret is used (batch-5
> null ratio = 1.533, p=0.0096), ruling out any LWE-signal explanation.
> gauss_sieve on the same instance and environment shows NO excess variance once
> N is conditioned out (within-group ratios 0.955 and 0.958, p≈0.52 for both
> primary N classes), consistent with approximate independence of cross-run scores.
> The evidence is consistent with a bgj1-specific QEMU/AVX2 emulation artifact
> and does NOT support an algorithm-independent sieve-vector correlation.
> No inference about LWE hardness, ML-KEM security, or any attack performance
> is supported by this campaign.

---

## Forward guidance

Three controls would fully characterize the remaining uncertainty:

1. **bgj1 native-hardware replication** — cheapest, most discriminating.
2. **gauss_sieve fixed-N replication** — eliminates N-variability confound definitively.
3. **Per-run within-run score autocorrelation** — maps the correlation structure
   directly without aggregate statistics.

Until at least RC-A and RC-B are completed, no conclusion about mechanism can be
supported. The current data are consistent with (and most parsimoniously explained
by) QEMU SIMD emulation artifacts in the bgj1 code path.
