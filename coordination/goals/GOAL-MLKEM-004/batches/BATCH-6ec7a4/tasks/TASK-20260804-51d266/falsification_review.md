# Falsification Review — TASK-20260804-51d266

**Reviewed artifact:** TASK-20260804-ff2c2b (Batch 4 executor report)  
**Snapshot commit:** 4d5defb29cbdc012dfe9180827b7f397f6bde135  
**Reviewer task:** TASK-20260804-51d266 (Red Team, independent session)  
**Verdict:** `blocking_objections`  
**Reviewed at:** 2026-08-04

---

## Executive Summary

Batch 4 ran two well-designed tests:

- **Test A (null control, n=50):** scored the WRONG secret against 50 independent sieve
  runs. Result: variance_ratio_null = 1.533 (p = 0.010).
- **Test B (outlier seed re-run, n=4):** confirmed the 3 high-T_N outlier seeds reproduce
  deterministically to floating-point identity.

Both tests produced valid data and the arithmetic is correct. However, the central claim
being tested — that the null control **resolves OBJ-QEMU** — does not hold. The analysis
below shows that:

1. ratio_null > 1 is equally consistent with QEMU-artifact (H1) and genuine-sieve-correlation
   (H2). The null control cannot distinguish between them.
2. The difference ratio_null − ratio_correct = 0.141 is not statistically significant
   (F(49,149) = 1.10, p = 0.32). No discriminating information is carried by this gap.
3. Native x86_64 hardware execution — the primary blocking test from batch 3, still the only
   decisive falsification — was not run.

OBJ-QEMU remains blocking. With 2 batches remaining, this must be the priority for batch 5.

---

## OBJ-1: Does ratio_null > 1 distinguish between QEMU-artifact and genuine-sieve-correlation?

**Answer: No. It cannot.**

The key ambiguity is between:

- **H1 (QEMU artifact):** QEMU's JIT translation of AVX2 SIMD introduces run-to-run
  variation in sieve quality (different translation decisions, cache effects, NEON
  approximations). This inflates Var[T_N] for **all** cosine-sum statistics—both correct
  and null.

- **H2 (genuine sieve correlation):** bgj1_sieve produces structurally correlated vector
  databases across runs (positive correlation between T_N values for different seeds,
  independent of which secret is scored). This also inflates Var[T_N] for **both** correct
  and null scoring.

Under **both** H1 and H2:
- T_N^correct sums N cosines over correlated/quality-variable sieve vectors → Var > predicted
- T_N^null sums N cosines over the **same** correlated/quality-variable sieve vectors → Var > predicted

There is no configuration of (ratio_correct, ratio_null) that H1 predicts but H2 does not,
or vice versa, in the qualitative space the test explores. Both predict both ratios elevated
and of similar magnitude. The test answers: "is the inflation secret-specific?" (No). It does
not answer: "is the inflation environment-specific?" (which is what OBJ-QEMU asks).

This is not a flaw in the test design per se — ruling out secret-specificity is valuable
structural information. But it is a category error to present ratio_null > 1 as evidence
that addresses OBJ-QEMU. It does not.

---

## OBJ-2: Is ratio_null > ratio_correct significant?

**Answer: No. F(49,149) = 1.10, p = 0.32.**

The formal test for whether the two variance inflation factors differ:

```
F = (chi2_null / df_null) / (chi2_correct / df_correct)
  = (75.125 / 49)         / (207.345 / 149)
  = 1.5332 / 1.3916
  = 1.1017
```

Under H0 (ratio_null = ratio_correct = R), this follows F(49, 149). The 95th percentile
is 1.44; the one-sided p-value (H1: ratio_null > ratio_correct) is **0.32**. The difference
is completely consistent with sampling variation given n=50 vs n=150.

The 95% confidence intervals confirm this: ratio_null's CI is [1.07, 2.38] — more than 2×
wider than ratio_correct's CI [1.12, 1.77] due to the 3× smaller sample. The two intervals
share nearly their entire extent.

**Direction argument.** There is a secondary observation: after normalizing by respective
independence predictions, ratio_correct / ratio_null = 1.3916 / 1.5332 = **0.908 < 1.0**.
The correct-secret variance is 9% *lower* than the null-secret variance (normalized). If a
genuine Ducas-Pulles violation specific to the correct secret were driving excess variance,
we'd expect ratio_correct > ratio_null (the correct-secret sum would have extra correlation
not present in the null-secret sum). The observed direction (0.908 < 1.0) is mildly
consistent with H1 (pure environment) rather than H2 (genuine signal-specific correlation),
but with p = 0.32 this is noise.

**Conclusion for OBJ-2:** The data provide no significant evidence that the two variance
ratios differ. Interpretations premised on "ratio_null > ratio_correct" have no statistical
basis.

---

## OBJ-3: Is T_N^wrong ≈ 4175 consistent with the test design?

**Answer: Yes, and T_N^wrong is fully deterministic.**

For the wrong secret s*, the scoring phase is:
```
phase_i = center_mod(x_i · e + y_i · (s − s*), q)
```
where (x_i, y_i) are the i-th sieve vectors and (s − s*) has 23/25 non-zero coordinates
(confirmed: 23 of 25 coordinates differ). This expression is **entirely deterministic**
given the sieve seed, LWE instance, and wrong_secret_seed.

The mean T_N^null ≈ 4175.5 (55.3% of T_N^correct ≈ 7551) reflects partial-overlap
structure from the 2/25 matching coordinates plus the lattice residuals from the wrong
phases. It is neither 0 (which would require uniformly random phases) nor ~7551 (which
would require s* = s). The observed value is physically plausible.

**Interpretation note error (confirmed by validator Q-1):** The `outlier_rerun_results.json`
states: *"T_N_wrong expected near batch-3 T_N mean (~7551) if wrong-secret scores are
unstructured."* This is inverted. Unstructured wrong-secret scores → T_N^wrong near 0 or the
null mean (~4175), not 7551. The correct-secret mean 7551 would only be matched if the wrong
secret were (nearly) identical to the correct secret. The note is a metadata error; the data
values are correct and consistent with correct behavior.

**Test B outlier cross-check reveals an internal inconsistency** (informative, not blocking):

| Seed | T_N_correct | z_correct | T_N_wrong | z_null |
|---|---|---|---|---|
| 2941775225 | 7789.6 | +2.59 | 4167.1 | −0.08 |
| 26883012   | 7791.8 | +2.61 | 4433.9 | +2.33 |
| 2418421570 | 7789.8 | +2.59 | 4238.2 | +0.57 |
| 1873347320 | 7420.5 | −1.42 | 4178.8 | +0.03 |

Seeds 2941775225 and 2418421570 show T_N_correct ≈ 2.6σ above the correct-secret mean
but T_N_wrong near the null mean (z ≈ −0.08 and +0.57). Under a "better sieve quality"
explanation, both should be elevated. Only seed 26883012 shows both T_N_correct and
T_N_wrong elevated (z = +2.61 and +2.33). The inconsistency suggests seeds 2941775225 and
2418421570 produce sieve vectors with selectively smaller |x·e| projections, not globally
better-quality sieve databases. This is consistent with natural sieve randomness (some seeds
happen to place vectors more orthogonally to e) but doesn't distinguish QEMU from genuine —
QEMU could induce this selectively for specific seeds.

---

## OBJ-4: The decisive test (native hardware) was not run

**Batch 3 red team priority-1 action: NOT completed.**

The batch-3 red team (TASK-20260804-1bb63d, `what_batch_4_must_address.action:
native_hardware_control, priority: 1`) requested:

> "Run exactly seeds {1873347320, 2941775225, 26883012, 2418421570} (runs 0, 27, 67, 97)
> plus 6-10 other batch-3 seeds on native Linux x86_64 hardware (not QEMU). [...]
> This is the decisive falsification of OBJ-QEMU."

Batch 4 ran neither of these seeds natively. Instead it ran:
- Test A (50 null seeds, also in QEMU): provides no resolution for QEMU vs genuine
- Test B (4 outlier seeds, also in QEMU): confirms determinism, not nativeness

The predictions for native execution are crisp and discriminating:

| | T_N^correct for outlier seeds (natively) | Variance ratio (natively) |
|---|---|---|
| H1 (QEMU artifact) | Near native mean ~7658 ± 92; NOT ~7790 | Close to 1.0 |
| H2 (genuine correlation) | Still near ~7790 relative to native mean | Still ~1.39 |

A single 4-6 minute native run resolves the entire campaign's open objection.

**Budget assessment.** Two batches remain (5 and 6). Native x86_64 access costs
~$0.10-0.12/hr (AWS c5.large or GCP n2-standard-2) and requires 4-6 minutes of compute.
It is feasible within batch 5. If batch 5 does not run native hardware, the campaign
closes with OBJ-QEMU unresolved — the strongest available conclusion would remain
"variance inflation observed in QEMU environment; origin unknown." This is weaker than
"variance inflation confirmed in native execution" or "variance inflation is QEMU
artifact only."

---

## OBJ-5: The comparative variance ratio Var[T_N^correct] / Var[T_N^null]

This is a new diagnostic the campaign has not formally computed. From the available data:

```
Var[T_N^correct] = 8492.3  (n=150, batch-3, predicted = 6102.7, ratio = 1.3916)
Var[T_N^null]    = 12262.2 (n=50,  batch-4, predicted = 7998.0, ratio = 1.5332)

Normalized ratio: ratio_correct / ratio_null = 1.3916 / 1.5332 = 0.908
```

**Interpretation:**
- If = 1.0: the correct-secret and null-secret runs exhibit identical variance inflation
  factors — consistent with purely environmental inflation (H1) that affects both equally.
- If > 1.0: the correct-secret sums have EXTRA variance beyond what the environment/sieve
  explains — this would be evidence of a secret-specific correlation (Ducas-Pulles H2).
- If < 1.0 (observed at 0.908): the correct-secret variance is *less* inflated than the
  null-secret variance, the opposite of what H2 would predict.

The observed 0.908 is not significantly different from 1.0 (p = 0.32), but the direction
is weakly consistent with H1 over H2.

**Key limitation:** This comparison uses 150 seeds (batch-3) for correct-secret and 50
*different* seeds (batch-4) for null-secret. An unpaired comparison confounds sieve-vector
variation with score-type effects. A **paired** design — same seeds for both correct and
null scoring — would directly estimate the secret-specific excess variance by differencing:

```
D_i = T_N_correct(seed_i) - T_N_null(seed_i)
```

Under H1 (QEMU): D_i would be large and DETERMINISTIC (both elevated/depressed together),
making Var[D] small relative to Var[T_N_correct] + Var[T_N_null] (high covariance).

Under H2 (genuine secret-specific extra correlation): D_i would show extra variability
beyond what sieve quality explains, making Var[D] larger than expected under H1.

Test B already computed (T_N_correct, T_N_wrong) for 4 seeds — the paired design over 4
points. Extending to 50-100 seeds in batch 5 would provide this with adequate statistical
power. This is the second most informative test after native hardware, and it can be run
entirely within the QEMU environment.

---

## Additional Structural Observations

### Denominator consistency (OBJ-DENOM from batch-3, not yet resolved)

OBJ-DENOM from the batch-3 red team requested per-run Var[s_i] for all 150 runs to verify
the run-0 denominator is not biased. Batch 4 did not collect this. The run-0 bias direction
is conservative (run-0 has T_N below average → likely higher Var[s_i] → larger denominator
→ smaller variance ratio), so OBJ-DENOM is not blocking. But it remains unresolved and
should be completed in batch 5 alongside the paired test.

### Seed pool independence (affirmed)

Batch-3 seeds: `default_rng(20260804001)`, batch-4 null seeds: `default_rng(20260804002)`.
These are non-overlapping pseudo-random seed pools. No seed appears in both experiments.
The seed design is sound.

### Batch reproducibility (affirmed)

Test B confirmed QEMU determinism to floating-point identity across all 4 outlier seeds
(delta = 0.000). This rules out QEMU **stochastic** JIT as the source of the outliers
(they would vary across runs if stochastic). The outliers are systematic, not random.
This is consistent with BOTH H1 (systematic QEMU handling for specific seeds) and H2
(genuine sieve property for those seeds). Native hardware is still required to distinguish.

---

## Narrowest Valid Conclusion

The narrowest conclusion supportable by all four batches of data:

> In the QEMU linux/amd64 emulation environment (Apple Silicon host, Docker
> linux/amd64 platform), bgj1_sieve cosine-sum statistics exhibit variance inflation
> above the independence prediction for both correct-secret scoring
> (ratio = 1.392, CI [1.12, 1.77], p = 0.001, n = 150) and null-secret scoring
> (ratio = 1.533, CI [1.07, 2.38], p = 0.010, n = 50). The inflation is not
> secret-specific. The variance inflation factors are not significantly different
> (F(49,149) = 1.10, p = 0.32). Three high-T_N outlier seeds reproduce
> deterministically (delta = 0.000 vs prior run). The source of variance inflation
> (QEMU emulation artifact vs genuine bgj1 sieve vector correlation) is unresolved.
> No statement about the Ducas-Pulles independence assumption or ML-KEM security
> is warranted.

---

## What Batch 5 Must Do

| Priority | Action | Resolves |
|---|---|---|
| **1 (blocking)** | Native x86_64 run: 4 outlier seeds + 10-15 batch-3 seeds on **bare-metal or non-QEMU x86_64** | OBJ-QEMU (decisive) |
| **2 (strongly recommended)** | Paired correct/null run: same 50-100 seeds, compute both T_N_correct and T_N_null per seed, test paired variance ratio | OBJ-PAIRED-TEST |
| **3 (needed)** | Per-run Var[s_i] for all seeds in paired run | OBJ-DENOM from batch-3 |

If native hardware cannot be obtained for batch 5, the campaign should close with the
narrowest supported statement above and explicitly record OBJ-QEMU as **unresolved**,
not as negative evidence against the Ducas-Pulles hypothesis.

---

*This report states no finding. All conclusions are bounded to the QEMU execution environment.
No claim is made about the Ducas-Pulles independence assumption or ML-KEM security.*
