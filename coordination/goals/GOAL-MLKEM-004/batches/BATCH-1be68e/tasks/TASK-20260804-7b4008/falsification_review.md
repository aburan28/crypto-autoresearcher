# Falsification Review — BATCH-1be68e Batch 5 Paired Test
**Task:** TASK-20260804-7b4008  
**Reviewed:** TASK-20260804-cbf6e2 (executor, snapshot commit 8b446af)  
**Red Team ID:** RT-20260804-3b82cd  
**Date:** 2026-08-04  
**Policy:** review-adversarial (independent session)  
**Verdict:** PASS WITH CONSTRAINTS

---

## 0. What the executor actually produced

Fifty paired sieve runs (bgj1_sieve, QEMU linux/amd64, g6k 0.1.2) scoring the
**same** sieve vectors against both the correct secret `s` and a wrong secret
`s*` (differing in 23/25 coordinates). All 50 runs completed; all valid.

| Statistic | Value |
|---|---|
| Pearson r(T_N_c, T_N_n) | **0.4395** (p = 0.00141) |
| Var[T_N_correct] | 9,097 |
| Var[T_N_null] | 14,059 |
| Var[T_N_diff] | 13,216 |
| Predicted Var[diff] (Cov=0) | 13,888 |
| var_diff / predicted | 0.9516 |
| Pre-reg H1 threshold | r ≥ 0.8 — NOT MET |
| Pre-reg H2 threshold | r ≤ 0.3 — NOT MET |

The executor correctly reports no finding and defers interpretation. This review
agrees with that characterization.

---

## 1. OBJ-1: r = 0.44 — what it actually tells us (and does not tell us)

### 1a. Position between the thresholds

r = 0.4395 is closer to the H2 threshold (0.3) than to the H1 threshold (0.8):

- Distance to H2 threshold (0.3): **0.14**
- Distance to H1 threshold (0.8): **0.36**

If forced to rank, r = 0.44 is "less inconsistent with H2" than with H1. But
this ranking is meaningless unless the thresholds themselves are well-calibrated.

### 1b. The thresholds were not calibrated — and the calibration shows H1 predicts r ≈ 0.31

The critical problem: the design assumed that under H1, r should be ≥ 0.8. No
simulation or closed-form derivation was provided. Here is the derivation.

Under a minimal **additive environmental model** (scalar Q_i shifts all N cosine
scores in run i equally):

    Cov(T_c, T_n) = Var(Q)
    Var(T_c)      = N·σ²_correct + Var(Q)   =   5,901 + Var(Q)
    Var(T_n)      = N·σ²_null    + Var(Q)   =   7,987 + Var(Q)

Calibrating Var(Q) to the **observed** ratio_correct = 1.5415:

    Var(Q) = (1.5415 − 1) × 5,901 = 3,195

Predicted r under this calibrated H1:

    r_H1 = 3,195 / sqrt(9,096 × 11,182) ≈ **0.317**

Fisher-z test for whether the observed r = 0.4395 significantly exceeds this:

    z_obs  = arctanh(0.4395) = 0.472
    z_pred = arctanh(0.317)  = 0.328
    SE(z)  = 1/sqrt(47)     = 0.146
    z-stat = (0.472 − 0.328) / 0.146 ≈ **0.98   (p ≈ 0.33, not significant)**

**The observed r = 0.44 is statistically indistinguishable from the pure
additive H1 model at this sample size.** The design has not discriminated
between H1 and H2.

### 1c. Why r = 0.8 was likely unreachable

For r to reach 0.8 given σ²_null > σ²_correct, Var(Q) must satisfy:

    0.64 × (5,901 + Var(Q)) × (7,987 + Var(Q)) = Var(Q)²
    → Var(Q) ≈ 27,700

This means the environmental noise would need to exceed the intrinsic
Var[T_N_correct] by a factor of **4.7×**. No evidence that QEMU produces this
level of run-to-run shift exists. The asymmetric σ (σ_null > σ_correct) means
that the null stream's larger per-vector noise dilutes the environmental
correlation signal. **The H1 threshold of r ≥ 0.8 was likely unachievable for
this wrong-secret configuration regardless of QEMU behavior.**

---

## 2. OBJ-2: Var[T_N_null] > Var[T_N_correct] — exact computation and what it means

**Computed from batch-5 actual values (N = 17,919):**

| Quantity | Value |
|---|---|
| N × σ²_correct = 17,919 × 0.32934 | **5,901** |
| N × σ²_null    = 17,919 × 0.44572 | **7,987** |
| ratio_correct = 9,097 / 5,901 | **1.5415** |
| ratio_null    = 14,059 / 7,987 | **1.7602** |

(The handoff suggested ratio_null ≈ 1.74 and ratio_correct ≈ 1.49 using
approximate input values. Actual values: 1.760 and 1.541 respectively.)

**ratio_null (1.760) > ratio_correct (1.541):** yes, confirmed.

### Interpretation

Under the additive Q model, both ratios should give the same Var(Q):

    Var(Q)_from_ratio_c = (1.5415 − 1) × 5,901 = 3,195
    Var(Q)_from_ratio_n = (1.7602 − 1) × 7,987 = 6,072

These differ: 3,195 ≠ 6,072. The additive Q model is **internally inconsistent**
with the observed data — it cannot simultaneously explain both ratios.

Possible explanations:

1. The environmental model is multiplicative (Q_i scales score amplitude), in
   which case the null stream's higher-amplitude cosines are inflated
   proportionally more, which _could_ produce ratio_null > ratio_correct. But
   under multiplicative Q, the predicted r would be different from the additive
   calculation, and this model also predicts r based on the _means_ of T_c and
   T_n (which differ: 7,550 vs 4,145). This is a testable alternative.

2. There are genuine within-run inter-vector correlations (H2-like), but these
   correlations affect the null stream _more_ than the correct stream — perhaps
   because the wrong-secret term y·(s-s*) is not fully uniform and retains
   partial phase structure. However, this also conflicts with the simple Ducas-
   Pulles model which predicts symmetric inflation.

3. The ratio asymmetry is entirely explained by the higher per-vector variance
   for the null stream combined with a non-additive environmental effect that
   is proportional to some function of σ². This requires a more complex model.

**None of these explanations is decisively supported by the data.**

### Weak H1 signal

The direction ratio_null > ratio_correct is **weakly consistent with H1**
(environmental artifact inflates high-σ statistics more) and **weakly
inconsistent with H2** as originally stated (symmetric Ducas-Pulles inflation
should give same ratio for both). This is a soft signal, not a conclusion.

---

## 3. OBJ-3: Variance partition — the handoff uses an incorrect formula

**The handoff states:**
> "Cov[T_N_c, T_N_n] / Var[T_N_c] ≈ 4970/9097 ≈ 0.55 (about 55% of T_N_correct
> variance is shared with T_N_null)"

This is **wrong**. `Cov/Var_c` is the OLS regression slope (confirmed to be
0.5463 by the executor), not the shared variance fraction.

**The handoff also states:**
> "~9,089 / 14,059 ≈ 65% of T_N_null's variance is NOT shared with correct"

This uses `Var_n − Cov = 14,059 − 4,970 = 9,089`, which is not the correct
formula for unexplained variance.

**Correct variance partition:**

From Cov(T_N_c, T_N_n) = r × √(Var_c × Var_n):

    Cov = 0.4395 × √(9,097 × 14,059)
        = 0.4395 × 11,309
        = **4,970**

    r² = 0.4395² = **0.1931** (19.3% = true shared variance fraction)
    
    Unexplained Var[T_N_c] = (1 − r²) × 9,097 = **7,340** (80.7%)
    Unexplained Var[T_N_n] = (1 − r²) × 14,059 = **11,344** (80.7%)

    Consistency check: Var[T_N_diff] = Var_c + Var_n − 2×Cov
                                    = 9,097 + 14,059 − 9,939 = 13,217 ≈ 13,216 ✓

**Both streams have 80.7% independent variance, not 20% and 35% as the handoff
implies.** The asymmetry is in the ABSOLUTE SIZE of independent variance (7,340
vs 11,344), which directly reflects the per-vector variance ratio (σ_null/σ_correct)²
= (0.4457/0.3293)² = 1.83, explaining most of the 11,344/7,340 = 1.55 ratio.

The handoff's underlying conclusion (null has more independent variance than
correct) is correct, but the mechanism is a design artifact — not a signal.

---

## 4. OBJ-4: Wrong-secret distance and null score variance analysis

### 4a. Formula error in the handoff

**The handoff claims:** `E[‖s-s*‖²] = 2 × n × 2η(η+1)/3 ≈ 2×25×2×2×3/3 = 200`

**This is wrong.** For CB(η=2) with values {−2,−1,0,1,2}:

    P(X=0)  = 6/16 = 0.375
    P(X=±1) = 4/16 = 0.250 each
    P(X=±2) = 1/16 = 0.0625 each

    E[X²] = Var[CB(2)] = 0×(6/16) + 1×(8/16) + 4×(2/16) = 16/16 = **1.000**

For 23 differing coordinates (s and s* independent CB(2) samples):

    E[‖s−s*‖²] = 23 × 2 × Var[CB(2)] = 23 × 2 × 1.0 = **46**
    ‖s−s*‖_rms ≈ **6.78**  (not 14 as the handoff claims; off by 2.1×)

The error in the handoff formula is that it uses `η(η+1)/3` as the per-coordinate
variance formula. For CB(2): `η(η+1)/3 = 2×3/3 = 2 ≠ Var[CB(2)] = 1`. The
formula `η(η+1)/3` does not apply to CB(η) as defined in ML-KEM.

### 4b. Actual null score variance

    σ²_correct = 0.32934  (structured phase ≈ correct lattice vector)
    σ²_null    = 0.44572  (partially randomized by wrong-secret term)
    σ²_uniform = 0.50000  (Var[cos(2πU/127)] with U ~ Uniform(Z₁₂₇))

The null scores are **68.2% of the way from correct to uniform**:

    (0.44572 − 0.32934) / (0.50000 − 0.32934) = 68.2%

This means: the null phases are significantly but **not fully** randomized.
Despite ‖s−s*‖ ≈ 6.78, the y·(s−s*) term still retains structure because
‖y‖ is not large enough (y lives in Z_q = Z₁₂₇, so y·(s−s*) mod 127 is not
uniform). The residual structure in null scores is why σ²_null = 0.446 < 0.500.

### 4c. Design artifact statement (mandatory)

**Var[T_N_null] > Var[T_N_correct] is a predetermined design consequence of the
null construction and carries no research meaning.** Under any wrong-secret with
‖s−s*‖ > 0, the per-vector null variance σ²_null > σ²_correct is guaranteed by
the increased phase randomization. This propagates to Var[T_N_null] > Var[T_N_correct]
regardless of QEMU, sieve structure, or any ML-KEM property. No inference about
independence failure or security should use this inequality as evidence.

---

## 5. OBJ-5: What the evidence supports with 1 batch remaining

### Campaign ratio summary (all QEMU)

| Batch | Stream | n | ratio | p-value |
|---|---|---|---|---|
| Batch-2 (TASK-736f46) | correct | 50 | 1.225 | 0.135 |
| Batch-3 (TASK-52cc2b) | correct | 150 | 1.392 | 0.001 |
| Batch-4 (TASK-ff2c2b) | null | 50 | 1.533 | 0.0096 |
| Batch-5 (TASK-cbf6e2) | correct | 50 | 1.542 | — |
| Batch-5 (TASK-cbf6e2) | null | 50 | 1.760 | — |

**Critical observation**: Every ratio > 1 result in this campaign comes
exclusively from QEMU. The ARM64 native attempt failed as infrastructure. No
native Linux x86_64 result has been obtained.

### Weakest supported conclusion

"In the QEMU linux/amd64 environment, the bgj1_sieve produces T_N statistics
with variance above the per-vector independence prediction. Both correct-secret
and null-secret streams are inflated (batch 4, batch 5). The inflation co-varies
weakly between streams (r = 0.44). All results are QEMU-only."

### Strongest supported conclusion

"The QEMU environment produces a systematic inflation of variance in cosine-sum
statistics from bgj1_sieve (ratio_correct ≈ 1.39–1.54 across batches 3 and 5).
This inflation is consistent with a pure additive environmental model (predicted
r ≈ 0.317 under calibration; observed r = 0.44 is within ~1 SE). Null-stream
inflation is also present and larger, consistent with design arithmetic (σ²_null
> σ²_correct). Neither the genuine sieve-correlation hypothesis (H2) nor the
environmental-artifact hypothesis (H1) can be excluded on current evidence.
Native hardware is required to disentangle the two."

### What batch 6 can and cannot do

**What QEMU batch 6 CAN do:**
- Deploy the near-secret null control (s** differing by 1-2 coords). Under H2:
  r(T_c, T_n_near) >> r(T_c, T_n_far). Under H1: both equal. This test does
  not require native hardware and provides genuine within-batch discrimination.
- Extend n to 100-150 runs to tighten confidence intervals on r.
- Compute cross-run r (T_c[odd], T_n[even]) to check for temporal QEMU drift
  (this can be computed NOW from the batch-5 data without new execution).

**What QEMU batch 6 CANNOT do:**
- Rule out QEMU as the source of ratio > 1 (only native hardware can do this).
- Provide evidence about ML-KEM or real-world sieve behavior.
- Close the campaign with a positive conclusion about Ducas-Pulles independence
  failure — all positive results would remain QEMU-conditioned.

---

## 6. Summary of blocking and non-blocking findings

### Blocking (must be addressed before the Coordinator draws a conclusion)

| ID | Issue |
|---|---|
| OBJ-1 | Pre-registered thresholds (r≥0.8, r≤0.3) were not calibrated; pure additive H1 predicts r≈0.317, consistent with observed 0.44. Design cannot discriminate. |
| OBJ-5 | All ratio > 1 results are QEMU-only. No ML-KEM conclusion can be drawn without native x86_64 confirmation. |
| OBJ-6 | No null calibration for r itself (cross-run r control missing); same-run r=0.44 cannot be attributed to within-run co-movement without establishing that cross-run r≈0. |

### Non-blocking (notation / minor)

| ID | Issue |
|---|---|
| OBJ-3 | Handoff OBJ-3 uses Cov/Var_c as "shared fraction" (should be r²=0.193); uses Var_n−Cov as "unexplained" (should be (1−r²)×Var_n=11,344=80.7%). Corrected numbers above. |
| OBJ-4 | Handoff OBJ-4 formula E[‖s-s*‖²]≈200 is wrong; correct is 46 (‖s-s*‖≈6.78). The design-artifact conclusion still holds. Null scores are 68% toward uniform, not fully uniform. |
| OBJ-2 | ratio_null (1.760) > ratio_correct (1.541) confirmed; additive Q model is internally inconsistent (3,195 ≠ 6,072 for Var(Q)); conclusion "weakly consistent with H1" stands but is based on model inconsistency, not clean signal. |

---

## 7. Verdict

**PASS WITH CONSTRAINTS.**

The executor's execution was clean and the data is reliable. The
executor correctly reports no finding and defers interpretation. The
Coordinator may use batch-5 data for decision-making subject to:

1. Acknowledging that the pre-registered thresholds are not achievable
   discriminators (OBJ-1) and that no H1/H2 conclusion follows from r = 0.44.
2. Recognizing that all variance inflation results are QEMU-conditioned (OBJ-5).
3. Deploying the near-secret null control in batch 6 for genuine discrimination (RC-4).
4. Correcting the variance-partition and wrong-secret-distance numbers in any
   downstream synthesis document (OBJ-3, OBJ-4).

The campaign should NOT be closed or its conclusion stated as "H1 supported" or
"H2 weakened" without native hardware confirmation or the near-secret null test.

---

## Artifact Inventory

| File | Description |
|---|---|
| `red_team_report.yaml` | Structured objections with computed numbers |
| `falsification_review.md` | This document |
