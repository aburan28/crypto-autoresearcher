# Validation notes — TASK-20260803-001a04

Validator, BATCH-017, GOAL-MLKEM-003, EXP-MLKEM-011.
Package under review: snapshot commit `27da1c45f876e3cfe3a57b118efa3d586fd1af1b`
(producer `TASK-20260803-f7a12c`, snapshot task `TASK-20260803-6b6f9d`).
Report: `validation_report.yaml` in this directory.

**Toy tier. Raw undivided score scale. No ML-KEM or Kyber claim in either
direction. Zero new sampling of the physical system.** AGENTS.md rule 12 stays
**UNMET and UNWAIVED**: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their
status and KN-FIND-031 stays withdrawn. Nothing here changes a ledger record.

Verdict: **ADMISSIBLE_WITH_DEFECTS** (`verdict: passed` on the
`agents/validator.md` schema). Eleven numbered defects, three major, all three
interpretive rather than integrity failures.

---

## 1. What I rebuilt, and which step each check actually tests

Standing binding (d) requires that a re-derivation reaching the same conclusion
by the same route is not counted as an independent check. Nothing below imports
anything from BATCH-015 or BATCH-017.

| step | producer's route | my route | outcome |
|---|---|---|---|
| ingest | 80-digit `Decimal(s) * M`, `ROUND_HALF_EVEN` | `float(s) * M`, `floor(x+0.5)` | same counts; band, cell counts, `sum D`, min, max identical |
| band rule | imported `regions()` | re-derived from the rule text | 551–851 / 301 and 636–1131 / 496 |
| rate model | Chebyshev basis, Gaussian elimination with partial pivoting | **Legendre** basis, **Cholesky** factorisation and inverse | slope, intercept, φ agree at **all 14 (file, degree) cells** to ≥6 s.f.; `sum(h) = P` exactly |
| null generators | Knuth product for λ<30, **rounded Gaussian** for λ≥30; recursive-Beta binomial | exact inverse CDF expanded outward from the mode, both distributions | null means and sds agree within MC error |
| seeds | master 20260806 | base **815551**, rule in the report's `validator_seeds` | disjoint streams |
| variance | Monte Carlo through the identical instrument | Monte Carlo **plus** a closed-form independent-cell null variance the package never computed | isolates the refit contribution at ≤4 % |
| the deficit itself | GLM terms + calibrated nulls | **model-free** local index of dispersion on raw increments | reproduces the deficit with no rate model at all |
| degree provenance | asserted from the report | read out of BATCH-014's archived code and results | forward deviance selection confirmed |

Fitted values and hat diagonals are basis-invariant in exact arithmetic, so the
Legendre/Cholesky refit is a genuine check of the producer's linear algebra and
not the same route. That is the step I claim as independently checked for every
"observed" number.

Commands used to establish absences (standing binding (f)):

```
find coordination/goals/GOAL-MLKEM-003/batches/BATCH-016 -type f
  -> dispatch_queue.json, archives/.../ledger_commit_receipt.json,
     tasks/TASK-20260803-6329c6/objections.md, .../red_team_report.yaml  — no script
find coordination/goals/GOAL-MLKEM-003/batches/BATCH-015 -type f
  -> tasks/TASK-20260803-d9afbd/anom5_investigation.py (+ report.md, results.json,
     the validator's two files, two receipts, and a __pycache__ .pyc)
grep -ic "rss|memory|maxrss" .../TASK-20260803-f7a12c/results.json   -> 0
```

I read the source of `ingest`, `regions`, `increments`, `glm`, `phi_of`,
`floors`, `pearson_residuals`, `autocorr`, `poisson_sample`, `binomial_sample`,
`mc_null` and `analyse_region` in the BATCH-015 script before summarising any of
them (standing binding (c)). That is how defect D-8 was found.

## 2. The arithmetic identity that governs the intercept

This is the single most important thing I found, and it settles priority
question 1.

For any fit with an intercept, `sum(mu) = sum(D)`, so

```
xbar = mean(mu)/nb = sum(D)/(K*nb)      is the SAME NUMBER at every degree
floor = 1 - xbar                        exactly, and also degree-invariant
intercept = phi - slope * xbar          exactly
```

Verified to machine precision (max deviation 2.2e-16) at all 14 cells;
`xbar = 0.08174335548172758` for n43 and `0.03300739247311828` for n50, and
`1 - xbar` reproduces the archived floors `0.9182566445182725` and
`0.9669926075268818` digit for digit.

The consequence is that the intercept is **the coordinate on which the two null
objects are identical**:

| | E[phi] | E[slope] | E[intercept] = E[phi] − E[slope]·xbar |
|---|---|---|---|
| N1 independent Poisson | 1 | 0 | **1** |
| N2 floor-attaining member | 1 − xbar | −1 | (1−xbar) + xbar = **1** |

So "−2.3 sd under BOTH nulls" is an identity of the regressor origin, not two
independent tests. Measured, the two intercept nulls are `+1.0056 ± 0.0947` and
`+1.0040 ± 0.0941` — indistinguishable, as the algebra requires. Centring the
regressor at `xbar` turns the intercept into φ, whose null means are 1 and the
floor 0.9183, and the two z's then **separate**: my own Monte Carlo gives
φ at z = −2.40 against N1 and −1.51 against N2.

Two further points on the intercept:

- It is numerically almost the pre-existing ANOM-5 statistic. It differs from φ
  by `slope*xbar = 0.0161`, which is 0.17 of its own null sd. Its z of −2.32 is
  slightly **weaker** than the archived φ z of about −2.36, because the slope's
  noise inflates the denominator (0.0947 against 0.0806) more than the shift
  moves the numerator. Decomposition check: `sqrt(0.0806² + 0.5916²·xbar²)
  = 0.0939` against the measured 0.0947, so φ and the slope are near-uncorrelated
  under the null and the intercept is φ plus independent noise.
- `x = 0` sits just past the top score of the band (min occupancy 0.0029 at
  T = 851), so the intercept is a small extrapolation into the deep tail the band
  deliberately excludes. The direct low-occupancy subset test below is
  interpolation and is the better handle.

## 3. The better handle, measured three ways

**Direct subset (n43, degree 5).** 164 cells with fitted occupancy below 0.02 —
half the band, where the floor moves E[t] by at most 2 % — read mean t = **0.6811**
against calibrated nulls **0.9959 ± 0.1084** (N1) and **0.9995 ± 0.1114** (N2),
i.e. **z = −2.91 and −2.86**. Thresholds 0.01 and 0.05 give −2.46/−2.45 and
−2.43/−2.30. Restricting further to leverage at or below the band mean (145
cells) gives 0.7215, so it is not a leverage or edge artifact; and the calibrated
null carries the leverage geometry anyway (mean h in the subset is 0.0168 against
a band mean of 0.0199 — the low-occupancy cells are *lower* leverage than
average).

**Monotone gradient (n43, degree 5).** By score quartile:

| quartile | mean occupancy | mean t | N2 predicts t ≈ 1 − occ |
|---|---|---|---|
| 0–25 % | 0.2762 | 0.9725 | 0.724 |
| 25–50 % | 0.0345 | 0.8348 | 0.966 |
| 50–75 % | 0.0099 | 0.7782 | 0.990 |
| 75–100 % | 0.0038 | 0.6214 | 0.996 |

The observation moves *down* as occupancy falls; N2 requires it to move *up*
toward 1. This is the inventor-protocol §3 decay test with occupancy as the
destroying parameter, over four bins rather than the slope's two effective ends,
and the quantity fails to decay in the direction N2 demands.

**Model-free (no rate model at all).** At the top of the n43 band the fitted rate
is flat (local log-slope 0.00012 per score), so a plain linear detrend of the raw
increments suffices. Detrended `var/mean` of the raw D_T, expectation 1 under
Poisson with sampling sd `sqrt(2/(L−1))`:

| L (last cells) | mean count | detrended var/mean | sd | occupancy |
|---|---|---|---|---|
| 25 | 11.9 | 0.453 | 0.289 | 0.0030 |
| 50 | 13.3 | 0.561 | 0.202 | 0.0033 |
| 75 | 15.6 | 0.688 | 0.164 | 0.0039 |
| 100 | 17.8 | 0.660 | 0.142 | 0.0045 |
| 150 | 27.5 | 1.551 | 0.116 | 0.0069 |

`L = 150` is where a *linear* detrend starts under-fitting the curvature, so the
usable window is `L ≤ 100`. The same statistic on n50's last 25/50/100 cells
gives 1.042, 0.961, 1.192 — **no deficit**. This route uses neither the Chebyshev
GLM, nor the leverage correction, nor either null generator, and it reaches the
same place. It is the independent confirmation the package did not have.

## 4. The joint test, and why the degree-2 caveat inverts

The floor member predicts the **pair** `(slope, intercept) = (−1, +1)`. The
package tests only one coordinate at a time. Using the Monte-Carlo covariance of
the null cloud (`corr(slope, intercept) ≈ −0.52 to −0.59`):

| cell | vs N1: D² (replicates ≥ obs) | vs N2: D² (replicates ≥ obs) |
|---|---|---|
| n43 deg 2 | 9.40 (5/400) | **27.97 (0/400)** |
| n43 deg 5 | 6.14 (23/400) | 13.62 (1/400) |
| n50 deg 3 | 3.50 (70/400) | 10.67 (2/400) |
| n50 deg 5 | 2.63 (85/300) | 6.94 (9/300) |

So the row the report offers as "consistent with the floor-attaining member" —
n43 degree 2, slope z = +1.55 — is the row where the floor member is rejected
**hardest**: the slope moved toward −1 but the intercept went to +1.278, which is
+3.12 sd above its null. Section 5 of the report discusses degree 2 only through
the slope, and does not mention that the degree-2 intercept z is +2.77/+3.16, an
excess of the same magnitude as the headline deficit. That is defect D-3, and the
same defect applies to "n=50 at every degree ≥ 4 is consistent with the
floor-attaining member".

Both files' φ readings put the joint picture plainly: n43 mid-band φ = 0.80 is a
deficit; n50 mid-band φ = 1.09–1.11 is an **excess**, sitting +2.1 to +2.3 sd
*above* the floor member. n50 is not a weak second instance of the same
phenomenon.

## 5. Degree provenance — checked in BATCH-014, not taken from the report

`coordination/goals/GOAL-MLKEM-003/batches/BATCH-014/tasks/TASK-20260803-f81a66/dispersion_control_c1.py`
lines 668–693:

> the degree is chosen by forward selection on the deviance — keep adding a
> parameter while it buys a chi^2_1-significant deviance drop — and the whole
> sweep is reported so the reader can see the sensitivity

with `degree_selection_rule` archived as "accept degree d+1 while it buys a
deviance drop >= chi^2_{1,0.95} = 3.841". Archived deviances, mid band:

| degree | n43 deviance | Δ | n50 deviance | Δ |
|---|---|---|---|---|
| 2 | 367.00 | | 617.69 | |
| 3 | 270.36 | **96.6** | 523.19 | **94.5** |
| 4 | 259.15 | 11.2 | 519.79 | **3.39** ← stops here |
| 5 | 238.25 | 20.9 | 513.45 | 6.34 |
| 6 | 238.10 | 0.15 ← stops here | 511.86 | 1.60 |

So degree 5 (n43) and degree 3 (n50) are **inherited from a criterion fixed
before this question was asked**, and degree 2 for n43 is not a free choice — the
archived rule rejects it by a deviance drop of 96.6, twenty-five times the
threshold. The producer declined to discount the degree-2 row and relied instead
on post-hoc under-fit diagnostics (φ = 1.237, residual ρ₁ = +0.413); that
conservatism is correct in spirit but the archive already supplied a
pre-registered reason, and the package did not look for it.

The n50 selection is the fragile one: the degree-3→4 drop is **3.39 against a
threshold of 3.841**, a 12 % margin. n50's only above-2-sd reading at an
admissible degree sits on that margin, and at degree 5 — which a 90 % threshold
would have selected — the reading is +1.81.

Plainly, as asked: **BATCH-016's tercile result inherits exactly the same degree
exposure**, because it used the same inherited degrees. For n43 that exposure is
mild — the conclusion is stable over the whole at-or-above-selected family, z vs
N2 in +3.57…+3.98 at degrees 5–8 and larger at 3–4. For n50 it is decisive.

## 6. Variance treatment: what actually makes OLS wrong

The package asserts two causes (heteroscedasticity, fit-induced dependence) and
quantifies neither. I separated them.

Closed-form null variance with the cells independent and μ **known** (no refit),
`Var(slope) = Σ c_T² Var(t_T)` with `c_T = (x_T − xbar)/Sxx` and

```
Var(t_T) = (2 + 1/mu)/(1-h)^2                                   under N1
Var(t_T) = [2(1-p)^2 + (1-p)(1-6p+6p^2)/mu]/(1-h)^2 , p = mu/nb  under N2
```

| cell | analytic sd(slope) | calibrated sd(slope) | analytic sd(int) | calibrated sd(int) |
|---|---|---|---|---|
| n43 deg 5, N1 | 0.5935 | 0.5916 | 0.0959 | 0.0947 |
| n43 deg 5, N2 | 0.3399 | 0.3274 | 0.0920 | 0.0941 |
| n50 deg 3, N1 | 1.3396 | 1.3727 | 0.0782 | 0.0749 |
| n50 deg 3, N2 | 1.1616 | 1.1830 | 0.0767 | 0.0764 |

The full refit changes the null **spread** by under 4 % on the slope and under
3 % on the intercept. It does move the N2 null **mean**, from −0.980 (known μ) to
−1.005 (refit). So pushing replicates through a full refit is *sufficient* for
the shared-rate-model dependence, and the dependence is small at this K — but the
package's stated reason for distrusting OLS is not the operative one.

The operative one: the ratio is essentially `sqrt(Var_null(t) / s²_observed)`.
With `Var_null(t) ≈ 2` under N1 and the observed scatter of t about the fitted
line `s² = 1.01` at n43 degree 5, `sqrt(2/1.01) = 1.41` — exactly the measured
1.405. Under N2 the `c_T²` weights concentrate on the high-occupancy cells where
the binomial variance is strongly suppressed (`2(1−p)² = 0.14` at p = 0.739),
which is why the same formula gives 0.78 in the other direction. Both ratios
reproduce; **0.469 to 1.405 across all 28 cells**, matching the reported
0.47–1.41.

Related fragility the package does not state (D-6): with weights
`w_T = (x_T − xbar)²`, the top 10 of 301 cells carry **47.6 %** of Sxx at n43
degree 5 and the effective design size `(Σw)²/Σw²` is **33.0**; at n50 degree 3
the top 10 carry 27.0 % and the effective size is 73.4. "301-cell resolution" is
not 301 independent lever arms for the slope coordinate.

I also attempted a moving-block bootstrap of the `(x_T, t_T)` pairs as a
dependence-robust slope sd. It is **not usable** here — because `x_T` is
near-monotone in the score index, block resampling changes the design matrix
between replicates and inflates the variance for reasons unrelated to serial
correlation (L = 1/5/15 gives 0.45/0.51/1.23 at n43 degree 3). Recorded rather
than dropped; no conclusion rests on it.

## 7. The deflation

`sqrt(1 + 2ρ₁)` is the leading variance-inflation term for a **mean** of a
stationary series. Three separate problems:

1. The slope is a different linear functional (x-centred weights), so it is not a
   derived correction for this estimator. The producer says this and labels it.
2. The ρ₁ used is that of the Pearson **residuals** e_T, while the series being
   averaged is their **squares** t_T. For approximately Gaussian e, the lag-1
   correlation of the squares is `ρ₁(e)² = 0.0108`; I measure `ρ₁(t) = +0.0147 ±
   0.058` directly. The correct first-order factor is `sqrt(1+2·0.0147) = 1.015`,
   not the applied **1.099** — an over-correction of the excess by about 6.5×.
   Conservative, so the conclusion is unthreatened; the *undeflated* z is the more
   nearly correct one.
3. It is applied to the slope z but **not** to the intercept z. The report's two
   headline numbers therefore use different conventions; the producer's own
   convention applied to the intercept gives **−2.11**, not −2.32.

And a 12-lag estimate of the inflation is 1.385 with a sampling sd of order 0.4
on that factor, so at K = 301 no serial-correlation correction is resolvable at
all. Answer: a heuristic, mis-targeted, conservative, inconsistently applied.

## 8. Null-object integrity

I re-derived the floor from BATCH-015's own argument after reading the code:
`Var(X) ≥ E[X] − E[X]²` for non-negative-integer X with equality iff X ∈ {0,1},
then Cauchy–Schwarz over the nb_iteration independent iterations gives
`Var(D_T) ≥ mu_T(1 − mu_T/nb)`. `Binomial(nb, mu_T/nb)` is a sum of nb i.i.d.
Bernoulli, so it attains both steps with equality. **N2 is genuinely the
minimum-variance member — per cell.**

Limit, recorded: N2 as implemented is independent *across* cells, while one
iteration of the physical process deposits `q^k_fft` candidates jointly
constrained across cells. Neither null carries cross-cell dependence, and the
observed residuals do (ρ₁ = +0.104). So every z in the package and in this report
is optimistic to that extent; the induced correlation on the *terms* is +0.015
and I bound the effect at under 2 %, but that is a first-order estimate, not a
bound. Standing binding (g) is respected throughout: the floor is a **minimum**
over a family and N2 is the member attaining it, never a preferred description of
the process.

Instrument controls, re-measured with exact samplers and my own seeds: N1
recovers slope −0.012/+0.028/−0.000/+0.024/+0.066 and N2 recovers
−1.005/−1.002/−0.983/−0.963/−1.016 at the five cells I ran; N2's whole-band φ is
0.9203 ± 0.0784 against the exact floor 0.9182566. All pass.

One inherited inexactness (D-8): `poisson_sample` is `round(λ + √λ·Z)` with a
non-negativity reject for λ ≥ 30, and **205 of 301** fitted rates in the n43 mid
band exceed 30 — so N1 is a rounded Gaussian over two thirds of the band, not a
Poisson. Measured directly on 60 000 draws per λ with no GLM: `E[(D−λ)²/λ]` is
1.0038–1.0047 for the approximation against 0.9996–1.0009 exact, and `Var` is
2.016 against 1.998–2.001. Bias under 0.5 %, inside my own MC noise, so the
consequence is bounded and immaterial here — but undisclosed in both packages.

## 9. On the amendment and the lost attempt

AMEND-BATCH-017-001 is handled correctly on my check. No attempt-1 statistic
appears anywhere in the package or the queue; the producer's seeds are its own
(master 20260806, distinct from BATCH-016's 20260803); the amendment's two
`find` commands rerun to what it says; and the anti-contamination decision — not
telling attempt 2 the lost numbers — is what makes attempt 2 an independent
execution rather than a manufactured agreement. The Coordinator's added
degree-sensitivity requirement was the single most productive control in the
package: it is what dissolved the n50 corroboration. One observation, not a
defect: the amendment describes a one-degree quote as "an uncalibrated point
estimate" without noting that the archive already held a pre-registered selection
rule; knowing that would have sharpened the requirement to "report the
at-or-above-selected family", which is the family that actually matters.

## 10. Answer to the question the batch exists to settle

**Is the low-occupancy deficit structural at per-cell resolution?**

For **n=43: yes**, and on stronger grounds than the package gives. The deficit
lives in the low-occupancy half of the band, where the independent-iteration
floor moves the reference by at most 2 %; it survives a leverage restriction; it
is monotone across four occupancy quartiles in the direction opposite to what the
floor member requires; and it is visible in the raw increments with no rate model
at all. The floor-attaining member is rejected jointly at every degree examined,
including degree 2. At per-cell resolution the BATCH-016 tercile result is **not**
an artifact of binning into three groups.

But it is **not** structural in the sense the report's intercept language
implies. Occupancy is a near-monotone function of the score index over this band
(3 non-monotone steps in 300 for n43, 0 in 495 for n50), so an occupancy effect
and any smooth score-position effect are perfectly confounded by this design
(D-4). Testing N2 remains valid — N2 predicts a specific curve — but
"occupancy-independent level shift" attributes a mechanism this design cannot
establish. The supported statement is narrower and sufficient: *the deficit lives
where the floor is inoperative, therefore it is not a floor effect.*

For **n=50: the question does not apply.** There is no deficit — φ = 1.09–1.11 is
an excess, +2.1 to +2.3 sd *above* the floor member; the low-occupancy subset
reads +0.46 sd; and the slope cannot separate the two nulls at any degree
(separation 0.81–0.98 sd, which is identically `1/sd(slope|N2)` and follows from
n50's occupancy lever arm being 3.2× shorter). n=50 neither corroborates nor
refutes n=43, and it disagrees with it about the sign of the underlying level
anomaly.

So the honest joint outcome is the one the handoff anticipated: **n=43 says one
thing at per-cell resolution; n=50 cannot say anything about it.** I do not force
it further.

## 11. Scope of this pass

This report verifies an instrument applied to two archived byte streams. It does
not adjudicate whether the occupancy floor is the right reference point, says
nothing about Approximation 4.9, supports no ML-KEM or Kyber claim in either
direction, and authorises no promotion. Every conclusion is scoped to q=241,
m=40, n=43 and n=50, the mid band of each file, the raw undivided score scale,
and the two null objects examined. Toy-scale throughout (AGENTS.md rule 7).
AGENTS.md rule 12 remains UNMET and UNWAIVED.

Resources for this validation: pure-Python, no new sampling, about 4 400
replicate GLM refits of my own plus 240 000 sampler draws; peak RSS under 10 MB;
well inside the 3 000 s / 4 GB budget. No git state was touched: nothing staged,
nothing committed, and no producer artifact was edited.
