# Red Team Falsification Review — TASK-20260803-bc2f41

**Reviewed artifact:** TASK-20260803-e53ce2 snapshot at commit `8cc51677f7202e9f9b85efdf834860254798abf4`  
**Verdict:** `pass_with_constraints`  
**Role:** Red Team (independent session, review-adversarial policy)  
**Date:** 2026-08-03

---

## Purpose and Scope

This review attacks the MEASUREMENT DESIGN, not the arithmetic. The arithmetic
(hash checks, score recomputation, null correctness, seed round-trips) was covered
by the Validator (TASK-20260803-535d15) and is not duplicated here. My task is:

1. Does the pipeline measure the object the cost models actually assume, or
   something adjacent?
2. Is the null of the right shape?
3. Is the measurement capable of showing AGREEMENT with the assumed law, or only
   DEPARTURE?
4. What is the cheapest check that would expose a harness artifact?

---

## 1. Is the Score Formula Correct? Yes, with a Critical Caveat

The formula `score_i(s') = cos(2π · t_i(s') / q)` where `t_i = centre_mod(x_i·b − y_i·s', q)` is the standard dual-sieve character score. At the correct secret, `t_i = centre_mod(x_i·e, q)`, and the expectation over the sieve database equals the characteristic function of the error distribution at frequency `1/q`:

```
E[cos(2π x·e/q)] = cf_{x·e}(2π/q)
                 ≈ exp(−2π² σ² ||x||² / q²)    (Gaussian approximation)
```

At σ=2, q=127, ||x||²≈184 (estimated from the m/d split of the median ||v||²=315):

```
predicted ≈ exp(−2π² · 4 · 184 / 16129) ≈ 0.41
measured  = +0.42738
```

These are roughly consistent. The score formula is mathematically correct and is
the right object to compare against MATZOV.Nf's predicted per-vector mean.

**The caveat:** MATZOV.Nf's independence assumption is about VARIANCE STRUCTURE,
not about the mean. This is the central design issue developed in OBJ-1 below.

---

## 2. The Core Design Issue: Mean vs. Variance (OBJ-1)

MATZOV.Nf computes the required sample count N from the signal-to-noise ratio of
the accumulated distinguisher:

```
T_N(s') = sum_{i=1}^{N} cos(2π t_i(s') / q)
```

Under the independence assumption:
- `E[T_N(s)]  = N · μ_correct`   (correct secret)
- `Var[T_N(s')] = N · Var[single score]`   (any candidate, under independence)

**The independence assumption is entirely about the second line.** If sieve vectors
are positively correlated (sharing geometric proximity in the lattice sieve
database), then `Var[T_N] > N · Var[single score]`, the SNR is lower than the
model predicts, and the true required N exceeds MATZOV.Nf's estimate. This is the
Ducas-Pulles concern.

Batch 1 measures only μ_correct = +0.42738 (the per-vector mean). It does not
measure Var[T_N]. From a single sieve run:
- T_N is a single scalar (17,919 scores summed)
- Var[T_N] cannot be estimated from one scalar
- Bootstrap estimates Var[T_N] under independent resampling — which is the null
  hypothesis, not a test of it

**To test independence, you need the empirical distribution of T_N across multiple
independent sieve runs.** With one run, you can confirm the mean but not the
variance structure.

### What this implies for batch 2

A measurement that finds `measured mean ≈ MATZOV.Nf predicted mean` would confirm
the per-vector expected contribution but would say nothing about whether
independence holds. Agreement on the mean does NOT validate independence.

Conversely, a measurement that finds `measured mean ≠ MATZOV.Nf predicted mean`
would indicate the mean is wrong, but would still not isolate whether the cause is
the wrong norm distribution (OBJ-3), wrong error model, or the independence failure
— since all three would change the per-vector mean.

**The measurement as designed is capable of showing agreement or departure with the
MODEL'S PREDICTED MEAN. It is not capable, from a single run, of showing agreement
or departure with the INDEPENDENCE ASSUMPTION.**

---

## 3. Is the Null of the Right Shape? Necessary but Insufficient (OBJ-2)

The null (uniform b, same sieve vectors) correctly tests: "does the pipeline find
LWE structure when there is none?" It passes: rank 18/33, mean ≈ 0.003.

But independence failure is a different phenomenon:

| Failure mode | What it looks like | Does current null detect it? |
|---|---|---|
| Spurious signal from b structure | Pipeline ranks correct secret high even for uniform b | **Yes** — null catches this |
| Correlated sieve vectors | Var[T_N] > N · Var[single score] even when mean is right | **No** — replacing b with uniform doesn't change vector correlation |

The independence null of the right shape is: same A, same b, same e, but a
DIFFERENT sieve run (different random seed → different vector set). If the
accumulated score T_N from different sieve seeds has empirical variance larger than
N · Var[single score], failure mode B is confirmed.

This is not a defect in batch 1 (the stated goal was signal-removal control, which
the null correctly addresses). But it means the existing null is insufficient for
the independence test that GOAL-MLKEM-004 requires.

---

## 4. Vector Norm Inflation Confounds the Comparison (OBJ-3)

The sieve database contains vectors with:
- ||v||² ∈ [218, 329] (min 218, median 315)
- Gaussian heuristic minimum: ~199
- All 17,919 vectors exceed the GH minimum by 10–65%

Per the Gaussian approximation, longer vectors contribute less per vector
(larger |x·e| → cos farther from +1). The per-vector mean at GH-norm vectors
would be higher than the measured +0.42738. If MATZOV.Nf assumes GH-norm vectors
(or its theoretical sieve output distribution), the comparison is of:

```
measured mean (at actual, longer-than-GH vectors)
vs.
MATZOV.Nf prediction (at assumed norm distribution, likely near GH)
```

Any discrepancy would be partially attributable to the norm distribution difference,
not just to the independence assumption. The two effects are confounded unless the
comparison is norm-conditioned.

Since all actual vectors exceed the GH minimum, there is no sub-population in
the existing data at GH-norm to condition on. Batch 2 needs either:
(a) a longer sieve run producing shorter (more saturated) vectors, or
(b) an explicit model of MATZOV.Nf's assumed norm distribution for comparison.

---

## 5. The Wrong-Candidate Pooling Artifact (OBJ-4)

The `wrong_mean_of_means` = +0.18082 in results.json is computed over:
- 16 uniform-Z_q candidates: mean ≈ +0.004
- 8 secret-distribution candidates: mean ≈ +0.29
- 8 near-miss candidates: mean ≈ +0.42

MATZOV.Nf models wrong candidates as drawn from the secret distribution, but the
key wrong-candidate comparison for the distinguishing advantage is against a
uniformly random candidate (the baseline the model's advantage formula uses).

The pooled +0.18 understates the correct-vs-uniform gap by approximately 2×
(0.424 vs 0.247) and overstates the discriminability of near-miss candidates.
Batch 2 must explicitly restrict the wrong-candidate baseline to the uniform-Z_q
population only. The near-miss population is a separate question about enumeration
precision, not about the distinguisher advantage against a random wrong candidate.

---

## 6. Near-Miss Indistinguishability at N=17,919 (OBJ-5)

Near-miss candidates score +0.42496 vs correct at +0.42738, a gap of ~0.0024 per
vector. With Var[cos(·)] ≈ 0.5 and N=17,919:

```
SE of mean difference ≈ sqrt(2 · 0.5 / 17919) ≈ 0.0075
Gap / SE ≈ 0.32 standard errors
```

At this N, the correct secret and near-miss candidates are statistically
indistinguishable. Distinguishing them at 80% power would require approximately
390,000 vectors (rough estimate). This sets a floor on the N batch 2 needs for
any near-miss analysis, well above the ~18K vectors in this run. This is a
scope observation for batch 2's design, not a defect in batch 1.

---

## 7. CTRL-RT-4 Deferral — Correct for Batch 1, Must Unblock for Batch 2 (OBJ-6)

CTRL-RT-4 (known-answer test on `estimator.lwe_dual.matzov.Nf`) was correctly
deferred because batch 1 makes no comparison against the callable. Its absence
does not make batch 1 inadmissible.

However, the predecessor (GOAL-MLKEM-003) spent twelve batches arguing about this
callable without anyone verifying that it computes what it claims to compute. If
batch 2 compares the measured score against MATZOV.Nf's prediction and finds a
discrepancy, there is no way to know whether the discrepancy is in the physics or
in the callable's implementation. CTRL-RT-4 must become a batch 2 completion gate.

---

## 8. Decay Control Coarseness (OBJ-7)

The signal collapses from +0.427 to +0.018 between σ=2 and σ=4. This is a 24×
collapse in one doubling — the kind of waterfall behavior Ducas-Pulles observed
and which suggests σ=2 may be near the regime boundary. Adding two points (σ=2.5
and σ=3.0) costs no sieve time (same vectors, different error draws) and would
characterize whether σ=2 is in the signal interior or near the cliff. This is
worth doing before batch 2's N comparison, since a regime-boundary position would
mean small changes in N translate to large changes in advantage.

---

## 9. Overall Admissibility Assessment

Batch 1 correctly establishes:
- The measurement pipeline is functional
- The score formula is mathematically correct
- The null passes (no spurious structure without LWE signal)
- The decay control passes (signal disappears when error dominates)
- The raw per-vector data is emitted and independently verifiable

These together demonstrate the measurement CAN be made and the basic controls
hold, which is batch 1's stated goal.

The design limitations identified above are constraints on what batch 2 can
conclude, not defects in batch 1's data:

| Limitation | Blocks batch 1? | Blocks independence test in batch 2? |
|---|---|---|
| Single sieve run → can't estimate Var[T_N] | No | Yes, unless batch 2 adds multiple runs |
| Current null doesn't probe variance structure | No | Yes, unless batch 2 adds sieve-seed variation |
| Norm inflation confounds mean comparison | No | Partially — requires norm modeling |
| Pooled wrong_mean_of_means | No | Partially — use uniform group only |
| CTRL-RT-4 absent | No | Yes, must complete before comparison |

**Verdict: `pass_with_constraints`.** The data is admissible. The constraints are
five concrete requirements batch 2 must address (detailed in the YAML report as
B2-1 through B2-5) before the comparison against MATZOV.Nf's independence
assumption can produce an interpretable result.

---

## 10. Cheapest Harness Artifact Check

The cheapest check that would expose a systematic harness artifact (as opposed to
physical LWE signal) is the **decay control at σ=0**, which the batch did not run:

```
b_zero_error = A·s (mod q),  e = 0
```

At zero error, t_i = center_mod(x_i · 0, q) = 0 for all i (since x_i·b_zero = x_i·As = y_i·s by the lattice definition), so score_i = cos(0) = 1.0 for ALL vectors, regardless of the candidate. Every candidate that happens to agree with y_i·s' mod q on all components would score 1.0, and all others would diverge. This is the ultimate known-answer test for the scoring pipeline and costs one new target computation on the existing sieve output (no re-sieve needed).

If the zero-error run does NOT produce score = 1.0 for the correct secret (or produces 1.0 for wrong candidates), there is a pipeline error. This takes about 10 lines of Python on the existing sieve vectors.

A second artifact check: run the scoring with e drawn from the SAME distribution as the error but INDEPENDENT of A and s (so b = A·s + e but e is a fresh draw that is also independently stored). Confirm that the correct secret still ranks first and the mean score matches the decay prediction for this σ. This rules out an artifact where the signal is coming from A rather than from e.

---

*Reviewed by: TASK-20260803-bc2f41 (Red Team, independent session)*  
*Policy: review-adversarial (fallback_allowed: true)*  
*Resolved model: amazon-bedrock/us.anthropic.claude-sonnet-4-6*  
*Snapshot commit: 8cc51677f7202e9f9b85efdf834860254798abf4*
