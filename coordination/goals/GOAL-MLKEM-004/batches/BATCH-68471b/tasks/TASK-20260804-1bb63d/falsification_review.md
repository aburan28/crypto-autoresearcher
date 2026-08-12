# Falsification Review — BATCH-68471b chi-squared test

**Red Team Task**: TASK-20260804-1bb63d  
**Producer Task**: TASK-20260804-52cc2b  
**Snapshot commit under review**: a54fe74d94e796d4cb8d1d5fe90a48a768425e78  
**Reviewed at**: 2026-08-04  
**Verdict**: **blocking_objections**  
**Admissible as chi2 test (arithmetic)**: YES — within the QEMU environment  
**Admissible as evidence against Ducas-Pulles independence assumption**: NOT YET — blocked by OBJ-QEMU and OBJ-OUTLIER  
**States a finding**: false (preserved — this report does not elevate to a finding)  
**No ML-KEM security claim**: confirmed  

---

## 0. Summary

The Batch-3 chi-squared test is arithmetically correct. Independent recomputation confirms chi2(149)=207.34, p=0.001123, variance_ratio=1.3916, 95% CI=[1.1227, 1.7707]. Batch-2 OBJ-5 (underpowered at n=50) is fully resolved: n=150 with p=0.001 is significant at any conventional threshold.

However, two independently blocking concerns prevent interpreting this as evidence against the theoretical independence assumption:

1. **OBJ-QEMU (blocking)**: Every data point comes from QEMU x86_64 emulation on ARM64 (Apple Silicon). The persistent ~107 T_N unit deficit below batch-1 expected — reproduced identically in both batch-2 and batch-3 — demonstrates that QEMU systematically changes the sieve vector distribution. Variance inflation in QEMU could be an emulation artifact.

2. **OBJ-OUTLIER (blocking)**: Three runs (indices 27, 67, 97) have T_N ≈ 7790 each (z ≈ 2.6). Removing these 3 runs drops p from 0.001123 to 0.034260. These outliers are unusual under the null (expected ≈ 0.72 such runs; observing 3 has p ≈ 0.01). Their validity under QEMU must be checked natively before the un-trimmed p-value can be trusted.

---

## 1. Arithmetic Verification

All reported statistics verified independently from `variance_results.json`:

| Statistic | Reported | Verified | Match |
|-----------|----------|----------|-------|
| empirical_var_TN | 8492.3096 | 8492.3096 | ✓ |
| chi2_stat | 207.3448 | 207.3448 | ✓ |
| p_value | 0.001123 | 0.001123 | ✓ |
| variance_ratio | 1.3916 | 1.3916 | ✓ |
| 95% CI lower | 1.1227 | 1.1227 | ✓ |
| 95% CI upper | 1.7707 | 1.7707 | ✓ |
| n_runs_completed | 150 | 150 | ✓ |
| all N_vectors = 17919 | true | true | ✓ |
| seeds unique | true | 150/150 | ✓ |

**T_N passes Shapiro-Wilk normality test** (W=0.9907, p=0.432). This validates the chi2 test's normality assumption.

---

## 2. OBJ-QEMU: Critical Emulation Confound (BLOCKING)

### What the receipt says
```
host_platform: macOS arm64 (Apple Silicon)
docker_platform_flag: linux/amd64
container_arch: x86_64
container_kernel: Linux-6.12.76-linuxkit-x86_64-with-glibc2.41
```

This confirms: all 150 runs execute via QEMU binary translation of x86_64 g6k code on ARM64 hardware. The QEMU layer translates AVX2 SIMD intrinsics (used throughout g6k's bgj1_sieve bucketing and update loops) to ARM64 NEON equivalents.

### The smoking gun: persistent mean shortfall

| Batch | Environment | Mean T_N | vs Batch-1 Expected (7658.2) |
|-------|-------------|----------|------------------------------|
| Batch-1 | Native Linux x86_64 | 7658.2 (expected) | — |
| Batch-2 | QEMU, n=50 | 7554.2 | −104.0 (−1.13 σ) |
| Batch-3 | QEMU, n=150 | 7551.1 | −107.1 (−1.16 σ) |

The batch-2 and batch-3 QEMU means differ by only 3.1 T_N units (0.03 σ) while both sit ~107 units below batch-1. This is not sampling noise: two independent experiments in the same QEMU environment converge to the same mean, 1.16 σ below the native result. **QEMU changes the sieve vector distribution in a statistically unambiguous way.**

### Why this blocks interpretation

The chi2 test asks: "Does Var[T_N] exceed N × Var[s_i] in this environment?" It correctly rejects H0 in the QEMU environment. But the target question is: "Does Var[T_N] exceed N × Var[s_i] for the correctly-implemented native sieve?"

QEMU-specific variance inflation mechanisms (not mutually exclusive):
- **JIT non-determinism**: QEMU's JIT recompiles hot loops when code cache pressure occurs. Different translations of the same x86_64 SIMD loop can produce subtly different floating-point results, creating run-to-run variation in sieve output quality that does not exist in native execution.
- **AVX2 gather/scatter emulation**: g6k's bucketing uses 256-bit gather loads; QEMU must emulate these as multiple 64-bit loads, with possible differences in element ordering or exception handling.
- **Memory ordering**: QEMU emulates x86 TSO memory model on ARM relaxed consistency; under single-threaded execution this should be benign, but multi-word SIMD state transitions may differ.

Note: g6k does NOT use RDRAND/RDSEED (PRNG is software Xorshift). The OBJ-1 from batch-2 red team correctly flagged this distinction; the present concern is SIMD instruction quality, not random number generation.

### What would falsify OBJ-QEMU

Run 10 of the batch-3 seeds natively on bare-metal x86_64 (e.g., AWS c5.large, ~$0.01/10 runs). If:
- Native mean T_N shifts up by ~107 units (toward 7658): confirms QEMU changes distribution
- Native variance_ratio is substantially LOWER than 1.39 (e.g., <1.10): QEMU is the source of inflation → **OBJ-QEMU confirmed, batch-3 result is an artifact**
- Native variance_ratio remains near 1.39 even with different mean: genuine signal → **OBJ-QEMU resolved, batch-3 result is valid**

Cost: ~4 minutes on any x86_64 Linux box.

---

## 3. OBJ-OUTLIER: Three Extreme Runs Drive Significance (BLOCKING)

### The numerical case

Three runs have T_N ≈ 7790 (z ≈ 2.60):

| Run | Seed | T_N | z-score | sieve_s |
|-----|------|-----|---------|---------|
| 27 | 2941775225 | 7789.567 | +2.588 | 14.108 (+2.1 σ above mean) |
| 67 | 26883012 | 7791.775 | +2.611 | 13.209 (near mean) |
| 97 | 2418421570 | 7789.812 | +2.590 | 13.561 (above mean) |

After removing these 3 runs:
- n = 147, var_TN = 7466.45, ratio = 1.2235, chi2 = 178.63, **p = 0.0343**
- With them included: ratio = 1.3916, chi2 = 207.34, **p = 0.00112**

The p-value changes by one order of magnitude. These 3 runs (2% of sample) account for a substantial fraction of the significance.

### Is this unusual under the null?

Under H0, T_N ~ Normal(μ, σ²). Expected number of runs with |z| > 2.6 in n=150 is approximately 150 × 2 × P(Z > 2.6) ≈ 150 × 2 × 0.0047 ≈ 1.41. Observing 3 in the same (upper) tail has probability approximately P(Poisson(0.72) ≥ 3) ≈ 0.012. Unusual but not extreme.

More suspicious: all three outliers cluster in a 2.2-unit T_N window (7789.57 to 7791.78), out of a typical range of ~460 units. This clustering of the three largest values is more concentrated than expected from extreme order statistics.

### The QEMU JIT hypothesis for outliers

Run 27 has sieve_seconds = 14.108s, which is 0.71s above the mean (2.1σ in sieve-time units). A sieve that runs longer (due to BGJ1 making extra reduction passes) produces a higher-quality database of shorter vectors, yielding higher cosine scores and thus higher T_N. If QEMU's JIT occasionally triggers extra BGJ1 iterations for specific seed values (perhaps because a particular SIMD code path is re-compiled mid-sieve), this could produce occasional "super-quality" sieve runs that are not reproducible natively.

Run 67 (seed=26883012) has a notably small seed value (~27 million) compared to most other seeds (~1-4 billion). Under g6k's Xorshift PRNG, the initial state is derived from the seed by a mixing function, so small vs large seeds should not produce biased outcomes. But this is worth verifying natively.

### Why this is blocking

The p-value of 0.034 (after removing the 3 outliers) still rejects H0 at α=0.05. So OBJ-OUTLIER alone does not completely invalidate the result. However:
1. The un-trimmed p=0.001 should not be reported without noting its sensitivity to 3 runs.
2. If the 3 outliers are QEMU artifacts (not reproducible natively), the correct p-value is 0.034, not 0.001.
3. The **combination** of OBJ-QEMU and OBJ-OUTLIER is blocking: even the trimmed p=0.034 rests on data from an environment that demonstrably changes the distribution.

---

## 4. OBJ-DENOM: Denominator Sensitivity (Concern, Not Blocking)

### Direction of bias

Run-0 has T_N = 7421 (z = −1.42). A below-average run reflects below-average sieve vector quality. For sieve vectors with more spread-out phases (lower T_N), cosine scores are more variable (higher Var[s_i]). Run-0's Var[s_i] = 0.340569 vs batch-1's 0.332505 (2.4% higher) is consistent with this: run-0 is a below-average quality run with above-average single-score variance.

Using run-0 as denominator likely **overestimates** E[Var[s_i]], making the denominator **too large** and the ratio **too small** — i.e., the test is conservative. The result would be more significant with a proper denominator.

Verification: using batch-1's Var[s_i] = 0.332505 gives p = 0.000504 (even more significant). The direction of any bias from run-0 is toward UNDERSTATEMENT, not overstatement.

### Robustness

The denominator would need to be inflated by **16.2%** (from 0.340569 to 0.395636) to make the test non-significant. For a denominator estimated from N=17919 observations, this is implausible from sampling error alone (95% CI for Var[s_i] from N=17919 has half-width ≈ Var[s_i] × √(2/N) ≈ 0.5%). However, if the TRUE population E[Var[s_i]] varies systematically across runs in a way correlated with sieve quality, the 16.2% threshold might be reachable. This warrants a per-run Var[s_i] check in batch-4.

---

## 5. OBJ-LAG2: Marginal Lag-2 Autocorrelation (Note)

Lag-2 autocorrelation r(2) = −0.1716, Bartlett z = −2.10, p ≈ 0.036. This is:
- Marginally significant at α=0.05
- OUTSIDE the Bartlett ±0.1600 95% confidence band
- Consistent with a possible quasi-periodic sieve quality oscillation on a 2-run cycle

However: under an AR(2) model with ρ₂ = −0.17, the effective sample size is n_eff ≈ 141. With n_eff = 141, the chi2 test gives chi2 ≈ 195.4, p ≈ 0.0015 — still highly significant. The lag-2 concern does not change the within-QEMU conclusion.

Lag-1 autocorrelation is negligible (r(1) = −0.0011, DW = 1.9621). The batch-2 red team's JIT warm-up concern is not supported by lag-1 analysis.

---

## 6. What Batch-4 Must Address

The ordering is by priority:

### Priority 1 (CRITICAL — must precede any finding assessment)

**Native hardware control**: Run seeds {1873347320, 2941775225, 26883012, 2418421570} (runs 0, 27, 67, 97) plus 6-10 additional batch-3 seeds on native x86_64 Linux (AWS c5, GCP n2, or equivalent — no QEMU). This costs ~10 minutes and is decisive. Record:
- T_N for each native seed
- single_score_var natively
- Whether batch-3 outliers (runs 27, 67, 97) are still extreme in native execution
- Whether mean T_N shifts toward batch-1 expected (7658.2)

**Falsification criterion (OBJ-QEMU)**:  
IF native T_N means are ≈ 7658 (+107 shift) AND native variance_ratio ≈ 1.0 → QEMU is the source → batch-3 is an artifact.  
IF native T_N means ≈ 7658 AND native variance_ratio ≈ 1.39 → genuine signal → OBJ-QEMU resolved.

### Priority 2 (Required for valid chi2 denominator)

**Per-run Var[s_i]**: Modify script to record within-run Var[s_i] for each of the 150 runs. In batch-4, use the average per-run Var[s_i] as the denominator (not just run-0). This resolves OBJ-DENOM and provides the theoretically correct null variance.

**Null control**: Run same seeds but score against s* ≠ s (e.g., s*=0). Compute ratio^null under the wrong secret. If ratio^null ≈ 1.0, the current ratio=1.39 reflects a property of the correct secret. If ratio^null > 1 in QEMU, the excess variance is an environment artifact.

### Priority 3 (Recommended)

**Outlier run investigation**: For native execution, verify runs with seeds 2941775225, 26883012, 2418421570. Record sieve_seconds. If sieve_seconds for these seeds cluster near 14.1s (as run-27 did in QEMU), the outliers may represent a seed-dependent BGJ1 convergence pattern that persists natively.

**Lag-2 autocorrelation check in native environment**: Verify whether r(2) ≈ −0.17 persists natively. If it persists, it is a sieve property and the effective sample size should be reported alongside chi2. If it vanishes, it is QEMU-specific.

---

## 7. Narrowest Supported Statement

> "In 150 independent bgj1_sieve runs on the same toy LWE instance (m=35, n=25, q=127, σ=2.0, D=60) executed in a QEMU x86_64 emulation environment on macOS ARM64, using 150 distinct pseudorandom 32-bit seeds, each producing exactly N=17919 sieve vectors, the empirical Var[T_N] = 8492.3 exceeds the within-environment independence prediction N × Var[s_i | run-0] = 6102.7 with chi2(149) = 207.34, p = 0.001123 (one-sided upper), variance_ratio = 1.3916, 95% CI [1.1227, 1.7707]. The result is statistically significant in the QEMU environment. However, the execution environment (QEMU emulation) demonstrably shifts the mean sieve score by −1.40% relative to a native batch-1 measurement, three extreme runs (indices 27, 67, 97) account for a p-value shift from 0.034 to 0.001, and no native-hardware control has been run. states_a_finding=false. No conclusion about native sieve behavior, the Ducas-Pulles independence assumption, or ML-KEM security is supported."

---

## 8. Disposition of Prior Batch-2 Objections

| Prior ID | Title | Disposition |
|----------|-------|-------------|
| OBJ-1 | QEMU vs unverified batch-1 environment | **ELEVATED to blocking** — NOW CRITICAL. Batch-3 uses same QEMU environment; shortfall confirmed. |
| OBJ-2 | N constant across runs | **RESOLVED** — All 150 runs have N_vectors=17919 ✓ |
| OBJ-3 | Baseline Var[s_i] from different environment | **PARTIALLY RESOLVED** — Within-env Var[s_i] now used (design fix). Run-0 representativeness remains a concern (see OBJ-DENOM). Test is conservative, not biased high. |
| OBJ-4 | Variable N would confound test | **RESOLVED** — N=17919 constant ✓ |
| OBJ-5 | n=50 underpowered, p=0.135 | **FULLY RESOLVED** — n=150, p=0.001 ✓ |
| OBJ-6 | Seeds 0-49 marginal Spearman trend | **RESOLVED** — Batch-3 uses randomized seeds; Spearman(run_index, T_N)=0.084, p=0.306 ✓ |

**New objections this review** (not in batch-2):
- OBJ-OUTLIER: Three extreme runs drive significance; sensitivity analysis required
- OBJ-LAG2: Lag-2 autocorrelation marginally significant; noted, not blocking

---

*This review was conducted in an independent session separate from the executor and validator. No official status change is made. All findings are handed to the Coordinator.*
