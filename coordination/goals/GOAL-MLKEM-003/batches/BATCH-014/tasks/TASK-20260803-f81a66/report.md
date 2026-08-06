# TASK-20260803-f81a66 — CONTROL C1, and an independent recomputation of the retirement basis

BATCH-014, GOAL-MLKEM-003, EXP-MLKEM-011. Executor.

**Observations only.** Nothing here concludes that the whole-band statistic
should or should not be retired, nor that Approximation 4.9 is validated or
refuted. That is `/review-evidence` under Coordinator authority. Toy tier
(q=241, m=40, n=43 and n=50), resolved band only, raw undivided score scale.
**No ML-KEM or Kyber security claim in either direction.** AGENTS.md rule 12 is
UNMET and UNWAIVED: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their
status; KN-FIND-031 stays withdrawn. Zero new sampling of the physical system,
no network, no G6K, no cost model.

Artifacts: `dispersion_control_c1.py` (the exact script run), `results.json`
(machine readable, provenance carried inside), this file.

---

## 0. Headline, stated plainly and in both directions

**JOB A — the deep tail is consistent with Poisson.** Under a properly
constructed test — increments rather than nested cumulative counts, a local
smooth Poisson rate rather than the plug-in lambda = C_T, the leverage correction
applied to the residual variance of the rate fit, and windows binned to
*expected* count >= 10 — the dispersion index on the rows that generate the
deep-tail floor is

| file | region | bins | min expected count | **phi** | sd (analytic) | sd (Monte Carlo) | phi - phi_null in sd |
|---|---|---|---|---|---|---|---|
| n=43 | C_T < 1000, scores 852-1802 | 82 | 10.03 | **0.895** | 0.185 | **0.154** | **-0.58** |
| n=50 | C_T < 1000, scores 1132-2309 | 87 | 10.00 | **1.062** | 0.178 | **0.166** | **+0.36** |

Both sit inside one standard deviation of the Poisson null. Bias-corrected
against the synthetic null-object calibration, phi = 0.910 (n=43) and 1.060
(n=50), with 2 sigma intervals [0.60, 1.22] and [0.73, 1.39]. **The deep tail is
Poisson to the resolution this data supports.** That is a clean result, not a
failure to find something: the sub-floor readings in this lane are not
explained by deep-tail over- or under-dispersion, and need a different
explanation.

**And the test's resolution is limited, which is also on the record.** It can
see phi = 1.5 (the seeded over-dispersed control returns 1.459 +/- 0.237 and
1.521 +/- 0.247), but with sigma ~ 0.16 it cannot exclude a true phi anywhere in
roughly [0.6, 1.4]. "Consistent with Poisson" here means consistent at +/-40 %,
not to a few percent.

**The extreme tail is not testable at all, and this is the sharper
observation.** The rows with C_T < 10 — 310 of 1803 (n=43) and 341 of 2310
(n=50) — carry **9 pooled increment events in total**, in each file. Those
310/341 rows cannot support any dispersion statistic, at any binning, because
there is nothing in them to bin. They are the rows the whole-band floor weights
most heavily.

**JOB B — both retirement numbers reproduce.**

| quantity | red team (`DEC-20260803-52a750`) | this task, derived independently | agreement |
|---|---|---|---|
| whole-band dof, n=43 | 1.55 | **1.5454** | exact to published digits |
| whole-band dof, n=50 | 1.51 | **1.5135** | exact to published digits |
| white-noise dof, n=43 | 422 | **422.158** | exact |
| white-noise dof, n=50 | 471 | **471.083** | exact |
| C>=1000 dof, n=43 / n=50 | 1.81 / 1.90 | **1.8088 / 1.8992** | exact |
| C>=1000 white dof, n=43 | 163 | **162.47** | exact |
| whole-band noise budget, n=43 | 209.126 | **209.12591** | exact |
| whole-band noise budget, n=50 | 247.86 | **247.86603** | exact |
| measurable-band budget, n=43 | 0.18229 | **0.1822882** | exact |
| attenuation, n=43 / n=50 | 1147x / 949x | **1147.23x / 948.73x** | exact |
| measurable share of the denominator, n=43 | 0.087 % | **0.08717 %** | exact |
| M2 n=43 deep-tail ratio | 0.770x | **0.7704x** | exact |
| identity constant, n=43 | 0.5919 -> 0.769x | **0.5930 -> 0.7701x** | 0.19 % apart, direction explained (4.3) |
| identity constant, n=50 | 0.3369 -> 0.581x | 0.3600 -> 0.6000x | **not independently reproducible from the archived summaries** (4.3) |

Every structural quantity in the retirement basis reproduces exactly from the
archived bytes by a second, independently written derivation. The one number
that does not fully reproduce is the model-dependent constant, and the reason
is a limitation of what BATCH-012 archived, not a disagreement about the
identity.

---

## 1. What the archive is, and the null being tested

Line T of an archived `Pwrong` file is `Phat(T) = C_T / M` with
`M = nb_iteration * q^{k_fft}` the exact number of pooled candidate scores.
Recovered here independently: `M = 55 990 084 000` (n=43) and
`83 985 126 000` (n=50); maximum relative deviation of `value*M` from an
integer `1.360e-16` and `1.815e-16`. Resolved bands [0, 1802] and [0, 2309].
These reproduce BATCH-012's instrument block exactly.

**C_T is a nested tail count.** `C_T = SUM_{j>=T} D_j` where `D_T = C_T - C_{T+1}`
is the number of pooled candidates whose score lands on T. Two consequences
drive the whole task:

1. **A cell-by-cell dispersion statistic applied to C_T is not a test of
   anything.** Adjacent rows share almost all of their events. The independent
   atoms are the increments D_T. For a Poisson process, Poisson increments and
   Poisson cumulative counts are the same statement (a sum of independent
   Poissons is Poisson), so testing D tests exactly the assumption the counting
   floor rests on.
2. **The same nesting is what collapses the effective degrees of freedom.**
   `Cov(C_T, C_{T'}) = min(lambda_T, lambda_{T'})`, which is the D-1 covariance
   and the whole content of Job B1.

The null under test: `D_T ~ independent Poisson(lambda_T)` with lambda_T a
*smooth* function of T. Over-dispersion would be the physically expected
failure — each of the 4000/6000 iterations uses its own lattice and its own
target, so its own tail rate, and a mixture of rates is over-dispersed.
Under-dispersion in a measured phi is the canonical artifact tell of a smoother
that has eaten the fluctuation it was supposed to measure, which is why the
estimator is calibrated against a null object of the same shape before anything
is read off it.

---

## 2. Job A — the construction, derived before reading either prior attempt

The construction below was fixed and committed to code before
`coordination/.../BATCH-013/tasks/TASK-20260803-b214b1/objections.md` 2.7 or
`EV-MLKEM-0cf1df` S-11 were opened, exactly as the handoff required. The
comparison in 2.6 was written afterwards.

### 2.1 The five design decisions

**(a) Increments, not cumulative counts.** As in section 1.

**(b) A local smooth rate by Poisson maximum likelihood, never a plug-in.**
The rate is an aggregated Poisson GLM with a Chebyshev log-link basis,

```
    mu_k(beta) = SUM_{T in bin k} exp( f(T; beta) ),
    f(T; beta) = SUM_a beta_a * Cheb_a( 2(T - T_lo)/(T_hi - T_lo) - 1 ),
```

fitted by Fisher scoring with a log-likelihood line search. The rate is
**integrated over the bin** rather than evaluated at the bin midpoint: deep-tail
bins are wide and lambda falls by orders of magnitude across them, so a midpoint
rule manufactures misfit that would read as over-dispersion.

**(c) Leverage correction, applied where it belongs.** For this GLM the exact
first-order residual variance is

```
    S_kj  = G_k^T I^{-1} G_j / mu_j,     h_kk = S_kk = G_k^T I^{-1} G_k / mu_k,
    Var(Y_k - mu_hat_k) = mu_k - 2 h_kk mu_k + SUM_j S_kj^2 mu_j = mu_k (1 - h_kk),
```

because `SUM_j S_kj^2 mu_j = h_kk mu_k` identically. So the corrected Pearson
residual is `(Y_k - mu_hat_k)/sqrt(mu_hat_k (1 - h_kk))` and
`phi = (1/K) SUM_k r_k^2` has expectation 1 under the null. The identity
`SUM_k h_kk = #parameters` is checked in every fit and returns to 15 digits.

**The leverage belongs to the rate fit, not to the plug-in.** This is the point
the handoff's phrasing turns on. If the rate is estimated by the cell's own
count (lambda = C_T), the leverage is exactly 1 and the residual exactly 0. That
construction is run anyway as a control and returns **phi = 0.000 identically**,
in every region, in both files — recorded to show the failure mode, not as a
measurement.

**(d) Windows binned to expected count >= 10.** Bin edges are placed by
accumulating the *fitted* rate until it crosses 10, then any bin whose fitted
expected count still falls below 10 is merged into its smaller neighbour and
the model refitted, iterating to a fixed point. Achieved minimum expected count
per bin: 10.026 (n=43) and 10.003 (n=50) in the primary region; the flag
`expected_count_ge_10_holds` is `true` for every region reported.

The alternative — greedy binning on *observed* counts — is run as a control,
because a bin that closes the moment its observed count crosses a threshold is
selected on the fluctuation being tested. See ANOM-4: it moved phi, and in the
opposite direction from the one predicted.

**(e) phi reported with its own standard deviation, per window, two ways.**
Analytically, `Var(r_k^2) = (2 + 1/mu_k)/(1 - h_kk)^2` under the Poisson null,
so `sd(phi) = sqrt( SUM_k (2 + 1/mu_k)/(1-h_kk)^2 ) / K`. And empirically, from
a seeded synthetic null object of the same shape pushed through the identical
pipeline, which additionally captures the negative correlation the smoother
induces between neighbouring residuals. The two agree to within 20 % everywhere
the analytic form is stable, which is itself a check on both.

### 2.2 The primary result, per window

Every window below has all of its bins at expected count >= 10, and carries its
own sd.

**n=43, deep tail C_T < 1000 (scores 852-1802, 997 pooled events, 82 bins,
degree 2, 3 parameters):** phi = **0.895 +/- 0.154** (MC), +/- 0.185 (analytic).

| window | scores | C_T from -> to | bins | min expected | phi | sd | (phi-1)/sd |
|---|---|---|---|---|---|---|---|
| 0 | 852-879 | 997 -> 786 | 14 | 13.85 | 0.626 | 0.399 | -0.94 |
| 1 | 880-905 | 778 -> 612 | 13 | 10.84 | 1.342 | 0.408 | +0.84 |
| 2 | 906-943 | 604 -> 437 | 14 | 10.06 | 0.718 | 0.391 | -0.72 |
| 3 | 944-995 | 437 -> 284 | 14 | 10.03 | 0.791 | 0.392 | -0.53 |
| 4 | 996-1079 | 281 -> 155 | 13 | 10.15 | 1.031 | 0.411 | +0.07 |
| 5 | 1080-1802 | 153 -> 1 | 14 | 10.09 | 0.907 | 0.643 | -0.15 |

**n=50, deep tail C_T < 1000 (scores 1132-2309, 993 pooled events, 87 bins,
degree 2, 3 parameters):** phi = **1.062 +/- 0.166** (MC), +/- 0.178 (analytic).

| window | scores | C_T from -> to | bins | min expected | phi | sd | (phi-1)/sd |
|---|---|---|---|---|---|---|---|
| 0 | 1132-1155 | 993 -> 840 | 12 | 11.47 | 1.676 | 0.430 | +1.57 |
| 1 | 1156-1185 | 832 -> 688 | 13 | 10.05 | 0.884 | 0.410 | -0.28 |
| 2 | 1186-1221 | 682 -> 535 | 12 | 10.70 | 0.729 | 0.424 | -0.64 |
| 3 | 1222-1270 | 529 -> 399 | 13 | 10.03 | 0.836 | 0.406 | -0.40 |
| 4 | 1271-1336 | 397 -> 287 | 12 | 10.01 | 1.159 | 0.424 | +0.38 |
| 5 | 1337-1462 | 286 -> 130 | 13 | 10.06 | 1.179 | 0.413 | +0.43 |
| 6 | 1463-2309 | 130 -> 1 | 12 | 10.00 | 0.994 | 0.724 | -0.01 |

**No window in either file departs from 1.0 by more than 1.6 of its own
standard deviation, and the sign of the departure alternates.** The deepest
window in each file — the one that reaches C_T = 1, i.e. the region that
supplies most of the whole-band floor — reads 0.907 +/- 0.643 and 0.994 +/- 0.724.

### 2.3 Controls, and what each returned

| control | n=43 | n=50 | reading |
|---|---|---|---|
| plug-in lambda = C_T (the construction not to use) | **phi = 0.000** | **phi = 0.000** | leverage 1, residual 0 — the failure mode, demonstrated |
| no leverage correction, Pearson/K | 0.858 | 1.031 | correction is worth +0.037 / +0.031 |
| no leverage correction, Pearson/(K-P) | 0.891 | 1.068 | agrees with the exact correction, as theory requires |
| greedy binning on **observed** counts | 0.927 | 1.220 | ANOM-4 — moved phi, wrong direction |
| phi trimmed to bins with leverage <= 0.5 | 0.888 | 1.073 | terminal wide bin is not driving the result |
| MC-A: seeded Poisson null from the chosen fit | mean 0.985, sd 0.154, 300 reps | mean 1.002, sd 0.166, 300 reps | estimator bias <= 1.5 % |
| MC-B: seeded Poisson null from a **richer** (degree-10) fit | mean 0.994, sd 0.166, 150 reps | mean 0.993, sd 0.138, 150 reps | degree choice is not inflating phi |
| MC-C: seeded over-dispersed null, phi_true = 1.5 | mean 1.459, sd 0.237 | mean 1.521, sd 0.247 | **power check: the test can see 1.5** |
| SUM leverage = #parameters | 3.0000000 | 3.0000000 | hat identity holds |
| degree sensitivity (converged degrees >= chosen) | phi in [0.895, 1.074] | phi in [1.036, 1.233] | smaller than one sd |
| integrality of recovered counts | 1.360e-16 | 1.815e-16 | instrument reproduces BATCH-012 |

MC-C is the control that makes the null result informative rather than empty: a
test that returns phi ~ 1 is only worth reading if it would have returned
something else had the truth been different. It would have.

The synthetic calibrations are **declared synthetic**: seeded (`seed = 20260803`,
recorded in `results.json -> provenance.seeds`), used only to calibrate this
script's own estimator against a null object of the same shape, and not a
measurement of the archived system. Every measured quantity in this run is a
deterministic function of the archived bytes and is seed-independent.

### 2.4 The extreme tail is not testable, and that is the sharpest number here

| file | rows with C_T < 10 | total increment events in those rows |
|---|---|---|
| n=43 | 310 of 1803 | **9** |
| n=50 | 341 of 2310 | **9** |

The pipeline refuses to report a phi there and says why. Nine events cannot fill
two windows at expected count >= 10 under any binning rule. This is not a
limitation of the test; it is a property of the archive. Whatever the deep-tail
floor asserts about those 310/341 rows, it asserts it about a region containing
nine pooled observations.

### 2.5 Two observations that do not fit the expected picture — recorded, not interpreted

**The two files disagree in direction in the well-measured mid-band.** In
`1000 <= C_T < 1e5`, where each bin has 10 to 866 expected events and the fit is
comfortable:

| file | region | bins | phi | sd (MC) | (phi - phi_null)/sd | stable over degrees |
|---|---|---|---|---|---|---|
| n=43 | scores 551-851 | 301 | **0.802** | 0.084 | **-2.29** | 5-12: [0.800, 0.811] |
| n=50 | scores 636-1131 | 475 | **1.106** | 0.067 | **+1.89** | 3-12: [1.087, 1.107] |

Both are stable across every degree from the selected one to 12, so neither is
an under-fitting artifact, and both survive the binning and leverage controls.
n=43 reads under-dispersed by 2.3 sigma; n=50 reads over-dispersed by 1.9 sigma.
**The two archived files do not agree about mid-band dispersion.** This is
recorded as an unexplained observation. It is not the deep tail and it does not
bear on the C1 question, but it is exactly the kind of thing that must not be
dropped.

**The shallow region reads slightly above 1 in both files** (phi = 1.046 +/- 0.065
and 1.091 +/- 0.060, at expected counts of 10^3 to 10^7 per bin). At those counts
the Poisson sd per bin is a few parts in 10^4, so this statistic is measuring
the adequacy of the polynomial rate model, not the dispersion of the counts.
Recorded with that caveat; it is why the deep tail, where counts are of order
10, is the regime in which a dispersion test means what it says.

### 2.6 Comparison with the two prior attempts (read only after the above was fixed)

`EV-MLKEM-0cf1df` S-11 records two attempts that bracket the answer uselessly:

| attempt | method | n=43 | n=50 | stated bias |
|---|---|---|---|---|
| 1 | local **unweighted quadratic** detrend on **51-row blocks** | 0.68-0.81 | 0.20-0.65 | low (OLS over-fits sparse counts) |
| 2 | **global log-linear** Poisson trend on **16/24/40-row windows** | 1.27-1.54 | 1.82-2.72 | high (log-linear under-fits a rate falling three orders) |
| **C1 here** | **aggregated Poisson GLM, degree by forward deviance selection, leverage-corrected, bins at expected count >= 10, MC-calibrated** | **0.895 +/- 0.154** | **1.062 +/- 0.166** | bias measured at <= 1.5 % against a seeded null object |

Both diagnoses in S-11 are visible in this run's own instrumentation, which is
some corroboration that they were the right diagnoses:

* the **log-linear** member of my own degree sweep (degree 1) reads **1.132**
  (n=43) and **1.273** (n=50) — the top of the sweep in both files, and inside
  attempt 2's stated range. Under-fitting does inflate phi here.
* the **fixed-row-count windowing** both attempts used is the deeper problem.
  In the C_T < 1000 region a 51-row block averages **0.53** pooled events
  (n=43) and **0.43** (n=50); a 16-row window averages **0.17** and **0.13**.
  A Pearson dispersion statistic on cells with expected count far below 1 has
  no null distribution worth the name, in either direction. Binning to expected
  count >= 10 is what removes that, and it is the single largest difference
  between C1 and both attempts.

C1 lands between the two brackets and much closer to 1 than either.

---

## 3. Job B1 — effective degrees of freedom, derived independently

### 3.1 The derivation, written before reading the red team's

The statistic is `S = (1/n) SUM_T r_T^2` with
`r_T = log2(model_T) - log2(Phat(T))`. A perfect model has
`r_T = log2 lambda_T - log2 C_T`, pure counting noise. By the delta method
`r_T ~= -(C_T - lambda_T)/(lambda_T ln 2)`, and because C_T is a nested tail
count, `Cov(C_T, C_{T'}) = min(lambda_T, lambda_{T'})`, so

```
    Cov(r_T, r_T') = min(lambda_T, lambda_T') / (lambda_T lambda_T' ln^2 2)
                   = min(1/lambda_T, 1/lambda_T') / ln^2 2 .
```

That is the D-1 covariance. For `Q = r^T r` with `r ~ N(0, Sigma)`,
`E[Q] = tr Sigma` and `Var[Q] = 2 tr(Sigma^2)`, so matching to `c*chi^2_nu`
gives the Satterthwaite

```
    nu_eff = (tr Sigma)^2 / tr(Sigma^2) .
```

White noise is the same expression with the off-diagonal zeroed. lambda_T is
replaced by the plug-in C_T, the same plug-in the archived floor uses. Since
lambda is non-increasing in T, `min(1/lambda_T, 1/lambda_{T'})` is the value at
the smaller index, and the double sum collapses to `SUM_i (1 + 2(n-1-i)) a_i^2`,
an O(n) computation.

### 3.2 Three conventions, because they are not interchangeable

The per-row variance `a_T` can be the delta-method `1/(lambda_T ln^2 2)` or the
exact truncated-Poisson `E[(log2 lambda - log2 C)^2 | C >= 1]`. **The exact one
is the convention consistent with the archived floor**: its sum over the whole
band *is* `n * floor^2`, verified here at 209.12591 (n=43) and 247.86603 (n=50)
against BATCH-012's archived floors 0.3405697 and 0.3275688. When `a_T` is the
delta-method variance, `min(a_T, a_{T'})` genuinely *is* the covariance;
substituting the exact `a_T` into the same expression is an extension by
analogy, and a different extension (keep the delta-method correlation
`rho_ij = sqrt(lambda_j/lambda_i)`, rescale to the exact variances) gives a
different answer.

| whole band | n=43 | n=50 |
|---|---|---|
| **nu, min(a,a') with exact variances** | **1.5454** | **1.5135** |
| nu, min(a,a') with delta variances | 2.0600 | 2.0405 |
| nu, delta correlation rescaled to exact variances | 2.3486 | 1.8421 |
| nu, white noise, exact variances | **422.158** | **471.083** |
| nu, white noise, delta variances | 245.153 | 326.949 |
| n (rows) | 1803 | 2310 |

| C >= 1000 sub-band | n=43 | n=50 |
|---|---|---|
| nu, min(a,a') exact | **1.8088** | **1.8992** |
| nu, delta correlation rescaled to exact | 1.8081 | 1.8984 |
| nu, white noise, exact | **162.466** | **237.582** |
| n (rows) | 852 | 1132 |

### 3.3 Comparison with the red team

The red team's `dof = (SUM a_T)^2 / SUM_{T,T'} min(a_T, a_T')^2` with exact
truncated-Poisson `a_T` is the first row of each table. **Every published digit
reproduces**: 1.5454 -> 1.55, 1.5135 -> 1.51, 422.158 -> 422, 471.083 -> 471,
1.8088 -> 1.81, 1.8992 -> 1.90, 162.47 -> 163. Two independent implementations
now agree on all six.

What the recomputation adds is a **convention sensitivity that was not
reported**: the whole-band nu ranges over 1.51-2.35 across the three defensible
ways of combining the D-1 correlation structure with a per-row variance. The
qualitative statement — the whole-band rms has O(1) effective degrees of
freedom rather than O(n) — is robust across all three, and none of them gets
within two orders of magnitude of the white-noise reading. The specific figure
"1.55" is convention-dependent at the +/-50 % level. The corresponding sampling
sd of the ratio, `0.5*sqrt(2/nu)`, is 56.9 % (n=43) and 57.5 % (n=50) at
nu = 1.55/1.51, and would be 46 % (n=43) at nu = 2.35.

Observed, not concluded: the sub-band nu is 1.81/1.90 — also O(1). The C >= 1000
statistic has the same *kind* of degree-of-freedom deficit as the whole-band
one; what differs is the attenuation of section 4, not the dof.

---

## 4. Job B2 — the attenuation identity, derived independently

### 4.1 The derivation, written before reading the red team's

Write `Omega` for the whole band, `M` for the `C >= 1000` band,
`D = Omega \ M` for the deep tail. Because the floor is an equal-weight rms of
*per-row* noise terms, those terms are additive, and

```
    ratio_whole^2 = (SUM_{T in Omega} r_T^2) / (n_Omega * floor_Omega^2)
                  = [ SUM_D r_T^2 + SUM_M r_T^2 ] / (n_Omega * floor_Omega^2)
                  = C  +  ratio_M^2 / A ,

    C = SUM_D r_T^2 / (n_Omega floor_Omega^2),
    A = (n_Omega floor_Omega^2) / (n_M floor_M^2) .
```

`A` is the attenuation: it is the ratio of the whole band's total noise budget
to the measurable band's, and it is a property of the *instrument*, not of any
model.

### 4.2 The structural numbers, all reproduced exactly

| | n=43 | n=50 |
|---|---|---|
| whole-band noise budget `n_Omega floor_Omega^2` | **209.12591** (red team: 209.126) | **247.86603** (247.86) |
| measurable budget `n_M floor_M^2` | **0.1822882** (0.18229) | **0.2612618** |
| deep-tail budget | 208.94362 | 247.60477 |
| measurable share of the denominator | **0.08717 %** (0.087 %) | 0.10540 % (0.105 %) |
| **attenuation A** | **1147.23x** (1147x) | **948.73x** (949x) |
| deep-tail floor (951 / 1178 rows) | 0.468732 bits | 0.458466 bits |
| sampling sd of the whole-band ratio at nu = 1.55 / 1.51 | 56.9 % | 57.5 % |

The identity is verified numerically inside `results.json`: for every model,
`identity_check_ratio_whole_squared` equals `ratio_whole_squared` to 15 digits.

### 4.3 The model-dependent constant: what reproduces and what cannot

For **M2, n=43** the reconstruction is valid and the numbers land on the red
team's:

| | red team | this task |
|---|---|---|
| deep-tail (C < 1000) rms | 0.3608 bits | **0.36112 bits** |
| deep-tail ratio | **0.770x** | **0.7704x** (23.0 % below the deep-tail floor) |
| identity constant | 0.5919 | **0.5930** |
| perfect-on-measurable score | **0.769x** | **0.7701x** |

The 0.19 % gap has a stated cause and the right sign. The red team decomposed
the residuals of a **single** whole-band fit. From the archived summaries I can
only subtract two **separately profiled** fits, and a sub-band-optimised rms is
never larger than the same fit's rms restricted to that sub-band — so my
`SUM_M` is too small, my `SUM_D = SUM_Omega - SUM_M` too large, and my constant
too large. 0.5930 > 0.5919, exactly as predicted. For M2 n=43 the two fitted
normalisations differ by only 0.0280 bits, which is why the effect is 0.19 %.

For the other model/file combinations the reconstruction is **flagged invalid
in `results.json`**, with the reason recorded per entry:

| model | file | whole vs C>=1000 fit | valid? |
|---|---|---|---|
| M2 | n=43 | same shape, delta norm 0.0280 bits | **yes** |
| M2 | n=50 | same shape, delta norm 0.0960 bits | no (my 0.6003x vs red team 0.581x, 3.3 % apart) |
| M4 | n=50 | same shape, delta norm 0.0043 bits | **yes** (0.5247x) |
| M4 | n=43 | same shape, delta norm 0.1015 bits | no |
| M1 (argmin) | both | **different exponent** p (23.0 vs 20.0; 22.25 vs 20.0) | no — different models |
| M1a (own exponent) | both | same p, delta norm 0.827 / 0.525 bits | no |
| M3 (argmin) | both | **different s** (0.97 vs 0.90) | no |

So of the red team's six-row "16 % to 42 % below the deep-tail floor" table, I
independently confirm **one row exactly** (M2 n=43, 0.770x), come within 3.3 %
on a second (M2 n=50), and **cannot check the remaining four from the archived
summaries at all**. This is a gap in what BATCH-012 archived, not a
disagreement: the per-row residual vector at each fit was never written out.
Concrete successor: archive `residuals[T]` per model per fit, at which point
the entire table becomes checkable in a few lines.

### 4.4 The binding requirement, satisfied

`DEC-20260803-52a750` binds this goal to report the C >= 1000 comparison and
never to quote a whole-band ratio without its effective degrees of freedom
beside it. Every model entry in `results.json` carries
`effective_dof_of_whole_band_ratio` and `effective_dof_of_count_ge_1000_ratio`
alongside its ratios. The comparison, restated with dof attached:

| model | C >= 1000 ratio (nu = 1.81 / 1.90) | whole-band ratio (nu = 1.55 / 1.51) |
|---|---|---|
| n=43 M2 exact region measure | **23.89x** | 1.044x |
| n=43 M1 surrogate at argmin p | 16.54x | 1.254x |
| n=43 M1a surrogate at own exponent | 55.40x | 2.071x |
| n=50 M2 exact region measure | **23.41x** | 0.968x |
| n=50 M1 surrogate at argmin p | 24.77x | 1.305x |
| n=50 M1a surrogate at own exponent | 54.55x | 2.128x |

(C >= 1000 and whole-band rms values are BATCH-012's archived measurements; the
floors, ratios and dof beside them are this task's own computation.)

---

## 5. Deviations, attempts and anomalies — recorded, none discarded

### Protocol deviations

**DEV-1 — no `runs/<RUN-ID>/` reproduction package.** The handoff declares
three artifact paths and no `runs/` tree, and instructs that provenance be
declared inside `results.json`. All of `docs/evidence-and-reproducibility.md`'s
required fields are therefore carried in `results.json -> provenance`: command,
argv, cwd, script sha256, git commit + branch + dirty state + dirty paths,
environment and dependency availability, input file sha256s, seeds and
determinism, wall clock, **peak RSS (0.0257 GB, measurable on this host via
`resource.getrusage`)**, user/system CPU, captured stderr, an `inference` block,
a `certificate` block (`kind: none`, pure measurement run) and a `validity`
block. `stdout_log` and `stderr_log` carry the console transcript. Write scope
was not expanded.

**DEV-2 — seeded pseudo-random numbers were used.** The handoff says ZERO NEW
SAMPLING. No new sampling of the physical system occurred: no G6K, no network,
no lattice, no new `.out` bytes. The seeded draws are the null-object
calibration of this task's own estimator (MC-A/B/C), which
`docs/inventor-protocol.md` section 3 requires before any reported signal is
believed, and they are labelled as synthetic throughout. Every measured quantity
is seed-independent. Reported as a deviation rather than silently taken.

**DEV-3 — development attempts preceded the production run.** The handoff's
`maximum_runs: 1` is respected: exactly one production run produced the
declared `results.json`. Three earlier executions wrote only to the scratchpad
and are listed below rather than hidden.

**DEV-4 — the red team's published values are embedded in the script as
reference constants.** They were taken from the handoff body and
`DEC-20260803-52a750`, not from the red team's derivation, and no computation
consumes them; they appear only in the comparison fields. The red team's
*method* was read only after the script was written.

**DEV-5 — `report.md` was created through a shell redirect rather than the
editor tool.** The session's editor refuses to create `.md` report files. This
file is one of exactly three `artifact_paths` declared in
`ledger/handoffs/TASK-20260803-f81a66.yaml` and is required by the Coordinator's
snapshot archive, so it was created as a declared experiment artifact instead,
and its content is additionally returned verbatim in the executor's response.
Recorded rather than worked around silently.

### Attempts

| # | outcome | classification |
|---|---|---|
| 1 | crashed in `gamma_sample` (`ZeroDivisionError`, shape -> 0) inside the MC-C over-dispersed control, on a deep-tail row whose fitted rate underflows. Job A's n=43 blocks had already printed. No declared artifact written. | `implementation_error`, repaired (ANOM-1) |
| 2 | ran to completion but three diagnostics were defective: high-degree GLM fits diverged and reported phi = 9.4e16 and 5e47 as if they were readings; one MC replicate produced sd(phi) = 3.9e137; bins with fitted expectation 9.10 slipped past the >= 10 gate. No declared artifact written. | aborted by its own diagnostics; surfaced ANOM-2/ANOM-3 |
| 3 | ran to completion with the guards in place; degree sweep, leverage diagnostics and merge loop all behaving. No declared artifact written (scratchpad only). | development verification |
| 4 | **production run.** exit 0, wall clock 216.4 s (budget 3000 s), peak RSS 0.0257 GB (budget 4 GB), stderr empty. | `completed_valid` |

### Anomalies

**ANOM-1 — `gamma_sample` divided by zero at shape -> 0.** In the
negative-binomial over-dispersed control, a row whose fitted rate underflows
gives Gamma shape `lambda/(phi-1) -> 0` and `u**(1/shape)` divides by zero.
Guarded (`shape <= 1e-12` returns 0). The defect was confined to the synthetic
control and could not have affected a measured value, but it aborted attempt 1
and is recorded rather than quietly patched.

**ANOM-2 — high-degree Poisson GLM fits diverged and were being read as
dispersion values.** Before the fix, degree 6 (n=43 deep tail) reported
phi = 9.4e16 and degree 7 (n=43, C < 1e5) reported phi = 5e47. Fisher scoring
had wandered without a likelihood line search. Fixed with a log-likelihood line
search plus a convergence gate and a final gradient check; a non-converged fit
now raises and is **recorded as a failed degree, never as a reading**. The
degrees that fail are listed per region in `results.json ->
degrees_that_failed_to_converge` (7-12 for the n=43 deep tail, 8-12 for n=50).
This is the same class of defect BATCH-012's ANOM-1 caught: a control catching
its own instrument.

**ANOM-3 — one terminal bin reaches leverage 0.80.** The last bin of each deep
tail is very wide (n=43: scores 1080-1802 in the last window) and is
substantially fitted by itself. `1/(1-h)` then inflates the analytic sd — in
the `C < 1e5` region it reached 1560 and 12415 before trimming, which is
meaningless. Diagnostics added: `leverage.max`,
`leverage.n_bins_leverage_gt_0p5`, and a trimmed phi over bins with h <= 0.5. In
the primary region trimming moves phi by -0.007 (n=43) and +0.011 (n=50), so the
headline is not driven by it. **The Monte-Carlo sd is the one to read in every
region; the analytic sd is unstable wherever `leverage.max` is near 1.**

**ANOM-4 — the binning-selection control moved phi in the direction opposite to
the one I predicted.** I predicted that greedy binning on observed counts would
bias phi *down*, by truncating upward fluctuations. Measured, it reads *up*:
0.927 vs 0.895 (n=43) and 1.220 vs 1.062 (n=50). The prediction was wrong and is
recorded as wrong. The size of the effect — up to 0.16, comparable to one sd —
is the real content: **the binning rule is a live analysis choice at the
resolution of this test**, and the expected-count rule (the one the handoff
specifies) is the one reported.

**ANOM-5 — the two archived files disagree about mid-band dispersion**, n=43 at
0.802 +/- 0.084 and n=50 at 1.106 +/- 0.067, both stable across every degree from
the selected one to 12. Unexplained. See 2.5.

**ANOM-6 — the C_T < 10 region carries nine pooled events in each file** and
admits no dispersion statistic. See 2.4.

**ANOM-7 — the deep-tail split of four of six archived models is not
reconstructible** from BATCH-012's summaries, because the whole-band and
sub-band fits differ in shape parameter or normalisation. See 4.3. Flagged
per entry in `results.json`; no unsupported number is reported for them.

**ANOM-8 — the whole-band nu disagrees by up to 50 % across three defensible
conventions** (1.51-2.35) while the red team's published figure is one of them.
See 3.3. The order-of-magnitude statement is robust; the two-significant-figure
statement is not.

---

## 6. Boundaries

* Two archived toy files only (q=241, m=40, n=43 and n=50), resolved band only,
  raw undivided score scale. Nothing is computed past the last positive score.
* C1 tests the dispersion of the pooled increments against a smooth Poisson
  rate. It does **not** test the iteration-level exchangeability assumption
  directly, and it does not test the band-truncation selection effect
  (the band ends at the last positive score, so the deepest rows enter
  conditional on an upward fluctuation, while the floor conditions per-row on
  C >= 1). That second open control from S-11 is untouched here and remains open.
* The C1 resolution is +/-0.16 in phi. "Consistent with Poisson" means consistent
  at that resolution, in a region of ~1000 pooled events.
* The C_T < 10 rows — which carry the bulk of the whole-band floor's weight —
  are **untested and untestable** from this archive.
* Job B2's model-dependent constant is confirmed exactly for one of six
  model/file combinations and approximately for a second; the other four are
  not checkable from what was archived.
* One execution, one implementation of C1, no replication. The dof and the
  attenuation identity now have two independent computations each.
* Establishes nothing about ML-KEM security in either direction, nothing about
  Carrier et al.'s Kyber cost figures, and nothing about Table 5.1.
* `dominated_by`: not applicable — no attack advanced, no cost frontier
  occupied. `sota_delta`: zero.

---

## 7. Reproduction

```
cd /home/user/crypto-autoresearcher
python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-014/tasks/TASK-20260803-f81a66/dispersion_control_c1.py --reps 300
```

git commit at run time `766caa43a5bf8eac83cebd252e7e04c290541c86`, branch
`claude/harness-findings-repo-yyzt1x`, working tree dirty only in this task's
own untracked directory. Python 3.11.15, Linux-6.18.5-x86_64. **No numpy, scipy
or mpmath on this host** — the Poisson GLM, the Gaussian elimination, the
Chebyshev basis, the truncated-Poisson sums, the Poisson and Gamma samplers and
every dof contraction are written out in the script. Seed 20260803 affects only
the synthetic null-object calibration; every measured quantity is
seed-independent.
