# The joint null, and how far occupancy can be separated from score position

Executor report — `TASK-20260806-518328`, `BATCH-e41719`, `GOAL-MLKEM-003`,
`EXP-MLKEM-011`. Authorised by `DEC-20260803-95176a`; goal state
`DEC-20260806-884ec2`.

**Scope.** Toy tier. Two archived files, q=241, m=40, n=43 and n=50, mid band
only, raw undivided score scale. **No ML-KEM or Kyber security claim in either
direction**, and nothing here about Approximation 4.9. **Zero new sampling of
the physical system**: no G6K, no network, no new `.out` bytes. Every random
number belongs to a seeded synthetic null object of this script's own; all 24
seeds are in `results.json -> seeds`.

**AGENTS.md rule 12 stays UNMET and UNWAIVED.** `EV-MLKEM-011`, `EV-MLKEM-013`
and `EV-MLKEM-017` keep their official status; `KN-FIND-031` stays withdrawn.

**OBSERVATIONS ONLY.** This report does not conclude that the deficit is or is
not real. It reports what each null gives and where each null is exposed. The
Coordinator adjudicates.

## Inference provenance

```yaml
requested_policy: executor-implementation
resolved_model_id: claude-opus-5
model_verified: false
fallback_used: true
fallback_reason: >-
  orchestration/model-policies.yaml names GPT-5.6 policy aliases this Claude
  Code harness cannot resolve.
```

---

## 0. The answer in four sentences

1. **The deficit SURVIVES every joint null in the iteration-budget family.**
   The 164-cell statistic reads z = **-2.84** against the band-total-preserving
   multinomial and **-2.82** against the joint minimum-variance object, against
   -2.79 / -2.82 / -2.69 for the three independence nulls. The model-free
   detrended var/mean behaves identically.
2. It survives for a reason that is an identity, not a coincidence: **cross-cell
   coupling cannot lower a marginal variance**, and a dispersion deficit is
   measured against the null *mean*, which is fixed by the marginals alone.
   Budget-preserving coupling moves only the null *sd*, and it moves it
   **down** — so a joint null of that family makes the deficit slightly *more*
   extreme, not less.
3. The one direction that could rescue the null is the opposite sign of
   dependence — **spatially correlated dispersion**, which widens the null. It
   is quantified here and it is **a live exposure**: a variance inflation of
   1.80x is required, and a latent log-dispersion field with sigma ~ 0.2-0.35 and
   correlation length ~ 25 cells supplies it while remaining compatible with the
   observed lag-1 autocorrelation of the terms. That family is *not* a
   dependence variant of the Poisson null; it is a non-Poisson process. Recorded
   as open, not adjudicated.
4. **Occupancy and score position cannot be separated by this design**, and the
   cross-file lever does not rescue it: the *sign* of the cross-file occupancy
   contrast at matched position flips with the choice of common position
   coordinate (n43/n50 occupancy ratio 1.87 under normalised band position, 2.60
   under log cumulative count, **0.22** under raw score), and there is no
   data-internal criterion for that choice. This is a clean negative.

---

## 1. What was imported, and what was disclosed rather than inherited

Everything from BATCH-015 is **imported by path**, not retyped:

```
coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/
    TASK-20260803-d9afbd/anom5_investigation.py
```

loaded with `importlib.util.spec_from_file_location` after
`sys.dont_write_bytecode = True`, and additionally run under
`PYTHONDONTWRITEBYTECODE=1`. Imported: `ingest`, `regions`, `increments`,
`glm`, `phi_of`, `pearson_residuals`, `floors`, `poisson_sample`,
`binomial_sample`, `gamma_sample`, `negbin_sample`, `solve`, `inverse`,
`mean_sd`, `quantile`, `FILES`, `DOF_BINDING`. **BATCH-017 D-11 check:**
`find coordination/goals/GOAL-MLKEM-003/batches -name "__pycache__" -o -name
"*.pyc"` returns nothing after the run.

**The N1 generator disclosure (handoff constraint 9), and a correction to how
it was characterised.** BATCH-015's `poisson_sample` is `round(lambda +
sqrt(lambda)*Z)` with a non-negativity reject for lambda >= 30; 205 of 301 n=43
mid-band cells and **68 of the 164 subset cells** exceed lambda = 30 (subset max
lambda = 79.6). I did not silently inherit it. Null **N1x** re-runs N1 with
exact Knuth inversion for every lambda < 700, which covers every subset cell and
every model-free window:

| | null mean | null sd | z |
|---|---|---|---|
| N1 (BATCH-015 generator) | 0.9974 | 0.1135 | -2.79 |
| N1x (exact inversion) | 0.9975 | 0.1124 | -2.82 |

**It does not matter for either statistic here** — the difference is 0.01 % in
the mean and 1 % in the sd, inside Monte-Carlo error at 800 replicates. N2,
JN-2 and JN-3 never call `poisson_sample`.

Correction recorded under standing binding (j) — *grep the prior batch's own
report before calling a result new, and before calling a prior claim
undisclosed*: BATCH-017's D-8 states the approximation is "undisclosed in BOTH
BATCH-015 and BATCH-017". That is **not accurate for BATCH-015**, whose own
`report.md` (numbered list, item 4, "Sampler approximations, disclosed") says
"The Poisson sampler uses inversion below `lambda = 30` and a rounded normal
above, whose variance error is O(1/12) against `lambda >= 30`, i.e. below
0.3 %". Command: `grep -n "rounded normal\|inversion below"
coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/TASK-20260803-d9afbd/report.md`
-> line 375. The *substance* of D-8 (the generator is not Poisson) stands; its
attribution of non-disclosure to BATCH-015 does not.

## 2. Reproduction of the archived numbers this batch is built on

Recomputed from the archived bytes through my own pipeline before any null was
run (`results.json -> reproduction_of_archived_reference_values`):

| archived | value | recomputed |
|---|---|---|
| n43 low-occupancy subset, cells | 164 | **164** (contiguous, band indices 137-300) |
| n43 subset mean t | 0.6811 | **0.68109701** |
| model-free var/mean, L = 25/50/75/100/150 | 0.453 / 0.561 / 0.688 / 0.660 / 1.551 | **0.45309 / 0.56141 / 0.68817 / 0.65974 / 1.55126** |
| n50 model-free, L = 25/50/100 | 1.042 / 0.961 / 1.192 | **1.04207 / 0.96070 / 1.19193** |
| n43 lag-1 acf of Pearson residuals | 0.104 | **0.103955** |
| n43 lag-1 acf of t (whole band) | 0.0147 | **0.014733** |

The model-free statistic's convention was not archived as code (the BATCH-017
validator's package contains `validation_report.yaml` and
`validation_notes.md` only — `ls coordination/goals/GOAL-MLKEM-003/batches/
BATCH-017/tasks/TASK-20260803-001a04/`). It was **recovered by reproducing the
archived values**: OLS line in the within-window index, residual sum of squares
divided by **(L - 2)**, divided by the window mean of the raw increments. All
five values then match to four decimals. Note the small internal inconsistency
this exposes in the archived presentation: the divisor is (L - 2) while the
quoted sampling sd is sqrt(2/(L-1)). It is immaterial; every sd below is
measured, not assumed.

## 3. The joint null: construction and dependence structure

### 3.1 What the physical process actually couples

The `.out` file is a pooled survival curve `C_T` over `nb` iterations; the
per-cell counts are `D_T = C_T - C_{T+1}`. For n=43: `nb = 4000`, each iteration
deposits exactly `q^k_fft = 241^3 = 13 997 521` candidates over the full score
support, so the grand total is `M = nb*q^k_fft = 55 990 084 000`. The mid band
holds `S = 98 419` of them, i.e. `S/M = 1.76e-6`.

So the *actual* within-iteration coupling is a multinomial constraint on
1.4e7 candidates spread over the whole support, of which the mid band takes
one part in 570 000.

### 3.2 The five nulls, and the dependence each carries

| null | per-cell marginal | cross-cell structure | measured dependence ratio* |
|---|---|---|---|
| **N1** | Poisson(mu_T) — BATCH-015 generator | none | 0.982 |
| **N1x** | Poisson(mu_T) — exact inversion | none | 1.043 |
| **N2** | Binomial(nb, mu_T/nb) — the per-cell floor | none | 1.076 |
| **JN-P** | Binomial(M, mu_T/M) | multinomial over the **full support**, `Cov = -mu_T mu_T'/M` | analytic, see below |
| **JN-2** | Binomial(S, mu_T/S) | multinomial with the **band total fixed**, `Cov = -mu_T mu_T'/S` | **0.897** |
| **JN-3** | Bernoulli(pi_T) per iteration, pi_T = mu_T/nb -> exactly N2's marginals | **near-fixed per-iteration band budget**, cells compete within an iteration | **0.893** |
| **JN-4(sigma,ell)** | variance mu_T*psi_T, psi a smooth lognormal field | **positive** cross-cell dependence | (see section 5) |

\* `Var(sum_{i in A} D_i) / sum_{i in A} Var(D_i)` measured on the 164-cell
subset from the replicates; 1 = independent, < 1 = negative cross-cell
dependence, > 1 = positive. Monte-Carlo relative error at 800 replicates is
about 5 %, which is why the three independence nulls read 0.98-1.08 rather than
exactly 1. **The two joint nulls sit clearly below**, which is the direct
instrument check that they carry the coupling claimed for them. Second check:
JN-2's band total has measured sd **0.0** (fixed by construction) and JN-3's is
**30.1**, against 322.8 / 319.4 / 256.6 for N1 / N1x / N2.

**JN-2 is the handoff's named construction, made exact.** Each of the 4000
iterations deposits a deterministic budget `B_i` into the band with
`sum B_i = 98 419` exactly (2419 iterations of 25 and 1581 of 24), and each
candidate picks a cell with probability `p_T = mu_T/S`. That is *resampling
whole iterations preserving each iteration's total*, and it is equivalent to
`Multinomial(S, p)` — the **maximal** sum-preserving negative dependence
available in the exchangeable-allocation family.

**JN-3 is the joint minimum-variance object** — the thing BATCH-017's W-10 said
N2 is not. Systematic pi-ps sampling per iteration with inclusion probabilities
`pi_T = mu_T/nb` (feasible: max pi = 0.739 <= 1, sum pi = 24.60) and **a fresh
random cell order per iteration**, so that (i) each iteration contributes 0 or 1
to each cell, which is exactly what attains the per-cell floor, (ii) the
per-cell indicator is *exactly* Bernoulli(pi_T) so the marginals are identical
to N2, and (iii) the per-iteration band budget is 24 or 25, so cells genuinely
compete within an iteration. The per-iteration shuffle is there on purpose:
unshuffled systematic sampling would perfectly couple cells one unit apart on
the cumulative-pi axis, which is an artifact of the scheme and not of any
process.

### 3.3 Why this family is the right one for a cumulative counting process

A joint null here has to (a) keep the **iteration** as the unit of resampling,
because that is the unit the physical process repeats; (b) let cells inside one
iteration **compete for that iteration's budget**, because that is the only
within-iteration coupling the generator has; and (c) leave each per-cell
marginal at or above the per-cell floor, because a null may not assume away the
quantity under test. JN-P does all three faithfully. JN-2 and JN-3 do all three
with the budget constraint *tightened* — JN-2 fixes the band total that the
process does not fix, JN-3 additionally imposes 0/1 per cell — and are therefore
reported as **bounds**, deliberately over-constrained, exactly the direction the
validator's priority question warns about.

### 3.4 The physical joint null is numerically inert — and this is not new

`JN-P` is what you get if you implement the iteration budget faithfully. Its
effect on this band, analytically:

* marginal: `Var(D_T)/mu_T = 1 - mu_T/M` in [0.9999999986, 0.9999999998] on the
  subset;
* covariance: `|corr(D_T, D_T')| <= 1.41e-9` on the subset.

So **JN-P is independent Poisson to within one part in 10^7**, and no simulation
of it is worth spending replicates on. The **marginal** half of this is
BATCH-015's mechanism **M-a1**, already recorded there as *excluded*, with the
archived number `floor_multinomial_over_pooled_scores = 0.9999999941601551` for
the n43 mid band (`results.json -> files[0].job_A_regions[0].floors`). I claim
as new only the **covariance** half and the explicit statement that the full
*joint* law, not just its marginals, is Poisson to that precision.

### 3.5 The pinning identity — why a budget null was never going to kill this

`Var(D_T)` is a functional of the **marginal** law of `D_T` alone. No cross-cell
coupling can lower it. Consequently any joint null whose per-cell marginals are
the per-cell minimum-variance member has *exactly* N2's per-cell variances, and
therefore — up to the refit's response — the same `E[t_T]` and the same null
**mean** for any unweighted average of `t`. A dispersion deficit is a statement
about the distance from the observation to that mean. **The entire room a
budget-preserving joint null has to move a z lies in the null sd, and it moves
that sd down.** Measured, on the 164-cell subset: JN-2 sd 0.1129 and JN-3 sd
0.1115 against N2's 0.1125 — a -0.9 % move for JN-3, in the direction that makes
|z| larger.

---

## 4. JOB A — the two statistics under the joint nulls

### 4.1 Statistic A: the 164-cell low-occupancy mean Pearson term

n=43 mid band, degree 5 (**inherited** from BATCH-014's forward deviance
selection, not chosen here), subset = fitted occupancy < 0.02 = 164 contiguous
cells. **Observed 0.681097.** 800 replicates per null; every replicate passes
through a full GLM refit, so the leverage geometry is carried.

| null | null mean | **null sd (measured)** | z | z, subset re-selected per replicate |
|---|---|---|---|---|
| N1 | 0.9974 | **0.1135** | **-2.79** | -2.79 |
| N1x | 0.9975 | **0.1124** | **-2.82** | -2.82 |
| N2 | 0.9832 | **0.1125** | **-2.69** | -2.68 |
| **JN-2 (joint, band total fixed)** | 1.0021 | **0.1129** | **-2.84** | -2.84 |
| **JN-3 (joint minimum-variance)** | 0.9957 | **0.1115** | **-2.82** | -2.82 |
| JN-P (joint, physical) | identical to N1 to 1 part in 10^7 (analytic, 3.4) | | | |

Archived reference for comparison: N1 0.9959 +/- 0.1084 (z = -2.91), N2
0.9995 +/- 0.1114 (z = -2.86).

**Statement required by the completion gate: the deficit SURVIVES the joint
null.** Against the two joint nulls it reads -2.84 and -2.82, which is not
weaker than the -2.69...-2.82 the independence nulls give. It does not die, and
it is not softened.

One reproduction discrepancy, recorded rather than reconciled: my N2 null
**mean** is 0.9832 where BATCH-017 archived 0.9995. The gap is 1.6 %, which is
4 Monte-Carlo standard errors of the mean at 800 replicates, so it is a
procedural difference between two implementations (different binomial sampler,
possibly a different subset convention), not noise. It moves z by +0.17 in the
conservative direction and changes no verdict. My N1 mean (0.9974) matches the
archived 0.9959 within error.

### 4.2 Statistic B: the model-free linearly-detrended var/mean

No rate model enters the **observed** value. The null needs a mean profile, for
which the fitted mu is used; the generated band is the same one Statistic A
uses, so both statistics come from the same replicates and the coupling is
band-wide.

n=43, observed vs measured null (mean +/- sd, z):

| L | observed | N1x | N2 | **JN-2** | **JN-3** |
|---|---|---|---|---|---|
| 25 | 0.4531 | 0.9903 +/- **0.2893** (-1.86) | 0.9979 +/- **0.2925** (-1.86) | 1.0009 +/- **0.2874** (**-1.91**) | 1.0119 +/- **0.2821** (**-1.98**) |
| 50 | 0.5614 | 1.0050 +/- **0.2005** (-2.21) | 0.9997 +/- **0.2078** (-2.11) | 1.0107 +/- **0.1995** (**-2.25**) | 1.0069 +/- **0.2130** (**-2.09**) |
| 75 | 0.6882 | 1.0459 +/- **0.1726** (-2.07) | 1.0378 +/- **0.1770** (-1.98) | 1.0438 +/- **0.1766** (**-2.01**) | 1.0482 +/- **0.1749** (**-2.06**) |
| 100 | 0.6597 | 1.1330 +/- **0.1626** (-2.91) | 1.1238 +/- **0.1679** (-2.76) | 1.1384 +/- **0.1746** (**-2.74**) | 1.1400 +/- **0.1691** (**-2.84**) |
| 150 | 1.5513 | 1.7358 +/- **0.2107** (-0.88) | 1.7282 +/- **0.2028** (-0.87) | 1.7478 +/- **0.2094** (**-0.94**) | 1.7557 +/- **0.2074** (**-0.99**) |

**The model-free deficit also survives**, and the joint nulls change it by at
most 0.13 in z at any window. Since this statistic needs no rate model, the
handoff's own criterion applies: the finding is not resting on the null family's
independence assumption.

Two things the *measured* null corrects in the archived presentation of this
statistic, both because a **linear** detrend under-fits the rate's curvature as
the window grows:

* the null **mean** is not 1 at large L. It is 1.13 at L = 100 and **1.73-1.76
  at L = 150**. So the archived L = 150 reading of 1.551, which against an
  assumed expectation of 1 looked like a *super*-Poisson excess, is in fact
  **0.9 sd BELOW its own null**. The window is not "where the statistic breaks";
  it is where the reference has to be measured rather than assumed, and once
  measured it points the same way as the others;
* the null **sd** at L = 100 is 0.163-0.175, i.e. 15-23 % larger than the
  assumed sqrt(2/99) = 0.142. Using the measured mean and sd makes L = 100 the
  *strongest* window (z = -2.74 to -2.91) rather than the weakest.

### 4.3 The n=50 control

Observed subset (313 cells, occupancy < 0.02) mean t = 1.034949:

| null | null mean +/- sd | z |
|---|---|---|
| N1x | 0.9922 +/- 0.0729 | +0.59 |
| N2 | 0.9913 +/- 0.0817 | +0.53 |
| JN-2 | 0.9985 +/- 0.0861 | +0.42 |
| JN-3 | 0.9853 +/- 0.0807 | +0.62 |

No deficit under any null, joint or independent; the joint nulls do not create
one and do not remove one. Model-free at L = 25/50/100: z = +0.20 / -0.10 /
+1.38 under JN-3. This is consistent with EV-MLKEM-890e2a W-9 and adds nothing
new to it.

### 4.4 Whole-band ratios and their effective degrees of freedom

Standing binding (a)/(b). Where a whole-band ratio is quoted at all — n=43 mid
band phi = 0.802295, n=50 mid band phi = 1.108199 — it is carried with the
archived binding text, reproduced verbatim in `results.json -> dof_binding`: the
effective degrees of freedom of a whole-band ratio is **O(1)**; the published
defensible range across conventions is **1.51-2.35** and no single value is
quoted; and restricting to the **count >= 1000** sub-band does **not** buy
degrees of freedom — that ratio's effective dof is also O(1) and lies inside the
same 1.51-2.35 family, so a ratio at C >= 1000 is no better resolved than the
whole-band ratio and neither supports a several-percent comparison. No
conclusion in this report rests on a whole-band ratio; the two statistics under
test are a 164-cell subset mean and a 25-150 cell window statistic.

---

## 5. The direction that CAN weaken it, and how much is needed

Since a budget-preserving joint null can only narrow the null, the only
null-family objection left is one that **widens** it, which requires
**positive** cross-cell dependence. This is quantified rather than dismissed.

**How much widening is needed.** To bring the 164-cell z above -2 the null sd
must be **0.15106** against the measured 0.11251 — a **1.343x sd inflation**,
i.e. a **1.803x variance inflation**.

**Does the observed series show it?** The model-free effective-sample-size check
on the observed t series over the subset, Bartlett kernel: the inflation factor
is **0.930 / 0.889 / 0.849 / 0.901 / 0.853** at lag cut-offs 1 / 3 / 6 / 12 / 20,
with each individual autocorrelation carrying a sampling sd of 0.0781 at 164
cells. The observed lag-1 autocorrelation of t on the subset is **-0.0704**. So
the observed series shows, if anything, mild *anti*-correlation — the opposite
of what is needed — but the estimator is noisy and this is **not** a bound.

**JN-4: a null that supplies the widening by construction.** `psi_T =
exp(sigma*g_T - sigma^2/2)` with `g` an AR(1) of correlation length ell cells,
giving `Var(D_T) = mu_T*psi_T`, `E[psi] = 1`, and positive cross-cell
dependence. 300 replicates per grid point:

| sigma | ell | null mean +/- sd | z (stat A) | null lag-1 acf of t | observed -0.0704 sits at | z (model-free L=25) |
|---|---|---|---|---|---|---|
| 0.10 | 1 | 0.9885 +/- 0.1007 | -3.05 | -0.0013 +/- 0.0724 | -0.95 | -1.97 |
| 0.10 | 25 | 1.0007 +/- 0.1264 | -2.53 | -0.0080 +/- 0.0745 | -0.84 | -1.83 |
| 0.20 | 5 | 1.0039 +/- 0.1228 | -2.63 | +0.0002 +/- 0.0849 | -0.83 | -1.78 |
| **0.20** | **25** | 0.9847 +/- **0.1620** | **-1.87** | +0.0093 +/- 0.0803 | **-0.99** | -1.49 |
| 0.35 | 5 | 0.9942 +/- 0.1486 | -2.11 | +0.0374 +/- 0.0897 | -1.20 | -1.43 |
| **0.35** | **25** | 1.0061 +/- **0.2094** | **-1.55** | +0.0292 +/- 0.0859 | **-1.16** | -1.16 |
| 0.55 | 1 | 1.0116 +/- 0.1598 | -2.07 | +0.0289 +/- 0.0781 | -1.27 | -1.25 |
| 0.55 | 25 | 0.9988 +/- **0.3076** | **-1.03** | +0.0667 +/- 0.0951 | -1.44 | -0.84 |

Full 12-point grid in `results.json -> job_A_JN4`.

**Reported plainly: this is a live exposure and I do not close it.** A latent
smooth dispersion field with sigma ~ 0.2 and ell ~ 25 cells widens the null
enough to put the 164-cell reading inside 2 sd, and the observed lag-1
autocorrelation of t sits only 0.99 sd below that null's own lag-1 distribution
— the data do not exclude it on that statistic. Two qualifications belong beside
it, both recorded and neither adjudicated here:

* JN-4 is **not** a dependence variant of a Poisson process. It is a process
  whose per-cell dispersion is itself random and spatially smooth — i.e. it
  already concedes that the increments are not Poisson cell by cell. Whether
  that is a null or an alternative is a Coordinator question, not mine.
* the entries that supply the widening also change the mean of the model-free
  statistic and would leave their own signature at other windows; I have not
  searched for a JN-4 point that reproduces the whole L-profile.

Under standing binding (g) I note explicitly: none of these grid entries is a
minimum over a family being passed off as an expected value. Each row is the
measured mean and sd of the statistic under that specific null.

---

## 6. JOB B — how far occupancy and score position can be separated

### 6.1 Within a file: not at all

Confirming EV-MLKEM-890e2a W-8 on my own recomputation: occupancy has **3
non-monotone steps in 300** for n=43 and **0 in 495** for n=50, while spanning
**253x** and **199x** respectively. Occupancy is therefore a smooth monotone
function of the score index within each file. Any specification that permits an
arbitrary smooth position effect absorbs it exactly. Within a file the answer is
**not at all**, and no statistic here changes that.

### 6.2 Across files: the lever exists, and it does not have a well-defined sign

The two files map occupancy onto position differently, so cells matched on
position but differing in occupancy do exist. The question is what "the same
position" means across two files whose score scales differ. There are at least
three defensible common coordinates, and they **disagree about the sign of the
contrast**:

| common coordinate | bins with both files | n43/n50 occupancy ratio at matched position (geomean, [min, max] over 10 bins) |
|---|---|---|
| normalised band position `(T-lo)/(hi-lo)` | 10/10 | **1.87** [1.57, 2.97] |
| log10 cumulative count `C_T` (the band-defining variable) | 10/10 | **2.60** [1.97, 3.37] |
| raw undivided score `T` | **5/10** (ranges 551-851 vs 636-1131 only partly overlap) | **0.22** [0.17, 0.33] |

Under the first two, n=43 cells carry 1.9-2.6x the occupancy of n=50 cells at
matched position. Under the third — the *raw undivided score scale*, which is
this lane's declared measurement scale — they carry **0.22x**, i.e. the contrast
**reverses**. There is no data-internal criterion to choose among them: each is
a different assumption about what a "smooth score-position effect" is a smooth
function *of*. **The design does not determine even the sign of the occupancy
contrast it is supposed to exploit.**

### 6.3 The pooled regression, with its effective design size

Pooled over both files, 797 cells, `t ~ 1 + file + (position basis) + beta*occ`.
Standing binding (h) is respected: no coefficient is quoted without the
participation ratio `1/sum(w^2)` on the weights `w_i = c_i^2/sum(c^2)` of its
own linear functional. Null calibration by generating **both** bands, refitting
both GLMs and recomputing beta with the design held fixed — under N2 (400
replicates) and under the joint JN-3 (120 replicates).

| specification | beta-hat | null (N2) | z | eff. design size / 797 | VIF |
|---|---|---|---|---|---|
| pos_norm, deg 1, common position | -0.318 | -0.968 +/- 0.429 | +1.51 | 38.7 | 1.8 |
| pos_norm, deg 3, common | -0.742 | -0.993 +/- 0.632 | +0.40 | 44.7 | 3.9 |
| logC, deg 1, common | -0.427 | -0.968 +/- 0.469 | +1.16 | 40.0 | 2.1 |
| logC, deg 5, common | -0.446 | -0.983 +/- 0.644 | +0.83 | 67.4 | 3.8 |
| T_raw, deg 1, common | -0.104 | -0.974 +/- 0.384 | +2.27 | 36.9 | 1.5 |
| T_raw, deg 5, common | -1.122 | -0.935 +/- 1.605 | -0.12 | 134.1 | 14.3 |
| pos_norm / T_raw, deg 1, **file-specific** | -0.519 | -0.952 +/- 0.535 | +0.81 | 49.8 | 2.2 |
| pos_norm / T_raw, deg 3, **file-specific** | -1.584 | -0.980 +/- 1.829 | -0.33 | 63.8 | 23.0 |
| logC, deg 3, **file-specific** | -3.098 | -1.303 +/- 6.497 | -0.28 | 114.8 | 244.5 |
| pos_norm / T_raw, deg 5, **file-specific** | **+14.566** | -1.131 +/- 12.154 | +1.29 | 92.2 | 824.0 |
| logC, deg 5, **file-specific** | **-330.36** | -20.12 +/- 210.73 | -1.47 | 83.5 | **258 301** |

Full 24-specification table, and the JN-3 calibration (which agrees to within
its own Monte-Carlo error), in `results.json -> job_B`.

Reading, stated as observation only:

* **No specification produces an occupancy coefficient distinguishable from its
  null.** |z| <= 2.27 across all 24, and the largest, T_raw deg 1 common, is the
  most heavily functional-form-constrained one in the table.
* **beta-hat is not stable under specification**: -0.10, -0.32, -0.43, -0.74,
  -1.12, -1.58, -3.10, +14.57, -330.4. It moves by three orders of magnitude and
  changes sign. That is the diagnostic of an unidentified coefficient, and the
  VIF column says why: allowing the position effect to be smooth **and**
  file-specific — the minimal honest specification when two files have different
  score scales — drives the collinearity of occupancy on the rest of the design
  to R^2 = 0.999996.
* Effective design size is **37 to 134 of 797 pooled cells**, never more than
  17 %. The pooled design does not deliver 797 independent lever arms for
  occupancy, in the same way BATCH-017 W-6 found 33 of 301 for the within-file
  slope.
* A structural note: `pos_norm` and `T_raw` give **identical** beta-hat in every
  file-specific specification, because within a file the raw score is an affine
  function of normalised position, so file-specific polynomial designs in the
  two coordinates span the same column space. Only `logC` is a genuinely
  different coordinate — and it is the one that explodes.

### 6.4 The part that cannot be broken at all, and why

Even granting a coordinate choice, the identification rests on an assumption the
data cannot test. With **two** files, "the file main effect" and "the difference
between the two files' occupancy-position maps" are **the same single
contrast**. The two files differ in n (43 vs 50), beta0/beta1, nlat, and nb
(4000 vs 6000), and they differ in dispersion in *opposite directions*
(phi = 0.802 vs 1.108). Any cross-file occupancy effect estimated at matched
position is therefore numerically indistinguishable from a file main effect
unless one assumes there is none — and EV-MLKEM-890e2a W-9 already records that
there is one.

**Answer required by the completion gate.** Within a file: occupancy and score
position cannot be separated **at all**. Across the two files: a nominal lever
exists — occupancy differs by a factor of 1.9-2.6 at matched position under two
of three common coordinates — but it does not identify an occupancy effect,
because (i) the sign of the contrast is coordinate-dependent and the raw-score
coordinate reverses it, (ii) every estimate is inside its own null, (iii) the
estimate is unstable across specifications by three orders of magnitude with VIF
up to 2.6e5, and (iv) with two files the occupancy contrast and the file main
effect are one contrast, not two. **Separating them would need a third file, or
a file whose occupancy-position map is non-monotone.** This is a clean negative
and is not dressed up as anything else.

---

## 7. Defects and surprises in this package

* **D-1 (mine, recorded).** The seed scheme `seed(name) = 518328 +
  sum_i (i+1)*ord(c_i)` is a weak additive hash and produced **one collision**:
  `n43|JN2` and `n50|JN3` both received seed **520379**. Those two replicate
  sets therefore draw from the same underlying uniform stream and are not
  independent of each other. No statistic in this report compares them: every
  headline comparison is within a file across nulls with distinct seeds.
  Recorded, not repaired, since repair would require a second run.
* **D-2 (mine, recorded).** The measured cross-cell dependence ratio for the
  three *independence* nulls reads 0.982 / 1.043 / 1.076 rather than exactly 1.
  This is Monte-Carlo error on a 164-cell aggregate variance at 800 replicates
  (relative sd about 5 %), not a defect in the generators, but it means the
  instrument resolves the joint nulls' 0.89 only at roughly 2 sd. A tighter
  reading needs more replicates.
* **D-3 (prior package, recorded).** BATCH-017 D-8's attribution — the Poisson
  approximation "undisclosed in BOTH BATCH-015 and BATCH-017" — is not accurate
  for BATCH-015; see section 1.
* **Surprise 1.** The model-free statistic's null mean is **1.73-1.76 at
  L = 150**, not 1. The archived L = 150 reading of 1.551 therefore sits *below*
  its own null rather than above it, inverting the natural reading of that row.
  Nothing in this lane rests on L = 150, but the archived table invites the
  wrong inference.
* **Surprise 2.** JN-3, the doubly over-constrained joint minimum-variance
  object, gives a null sd only **0.9 % below** N2's. The intuition that the
  joint minimum-variance object would be a much tighter null is wrong at this
  occupancy: with sum pi = 24.6 candidates per iteration spread over 301 cells,
  the competition each cell feels is tiny.
* **No infrastructure failure, no protocol deviation, no discarded replicate.**
  `replicates_discarded = 0` for every null. `stderr.txt` is 0 bytes.

## 8. Provenance and budget

| | |
|---|---|
| git commit | `7744cbe6972661494b7e1c834ba7b14793038a05` |
| tree dirty at run time | yes — 1 porcelain line, the untracked task directory itself |
| command | `PYTHONDONTWRITEBYTECODE=1 python3 joint_null.py > stdout.txt 2> stderr.txt` |
| runs | **1** (the declared run). Development smoke tests were run on a **copy** of the script in the session scratchpad with replicate counts reduced to 3-12; they produced no archived artifact and no number in this report. |
| wall clock | **720.6 s** of a 3600 s budget |
| peak RSS | **28.19 MB** (29 560 832 bytes) of a 4 GB budget |
| CPU | 720.28 s user, 0.08 s system |
| python / platform | 3.11.15 / Linux-6.18.5-fc-v18-x86_64-with-glibc2.39 |
| input sha256 (n43) | `50bd293cadf952516b092524c25f4404a1e4ca40983d1751286f96269dbf90bb` |
| input sha256 (n50) | `ce23181dca95a1c6a72463c2c39f14f645500a068b3af46c71d5b45af69ab459` |
| seeds | 24 streams, all listed in `results.json -> seeds`; scheme in `results.json -> seed_scheme` |
| replicates | n43 nulls 800 each; n50 400 (JN-3 200); JN-4 grid 300 x 12; Job B 400 (N2) and 120 (JN-3) |
| `__pycache__` written into any archived directory | **none** — verified after the run by `find coordination/goals/GOAL-MLKEM-003/batches -name "__pycache__" -o -name "*.pyc"` |
| git state touched | none: nothing added, nothing staged, nothing committed |

Standing bindings honoured, itemised: (a)/(b) section 4.4; (c) the imported
BATCH-015 routines `ingest`, `regions`, `increments`, `glm`, `phi_of`, `floors`,
`poisson_sample`, `binomial_sample`, `negbin_sample` were read in source before
being summarised, which is how section 1's disclosure and D-3 were found; (d)
the step I claim as independently checked is the **null object's dependence
structure**, by a route BATCH-015 and BATCH-017 do not contain — I did not
re-derive the GLM or the leverage correction and do not claim them as
independently checked here; (e) no rms-ratio fit-dependence inference is made;
(f) the two absences asserted (no code archived for the model-free statistic; no
per-iteration data) were established by `ls` on the BATCH-017 validator
directory and by BATCH-015's own M-a4 record, both named at the point of use;
(g) section 5; (h) section 6.3; (i) section 6.3 reports marginal coefficients as
marginal coefficients and tests no joint prediction with them; (j) sections 1,
3.4 and 4.3 credit BATCH-015 M-a1, BATCH-015's sampler disclosure and
EV-MLKEM-890e2a W-9 rather than claiming them.

## 9. What this report does not say

It does not say the deficit is real. It does not say Approximation 4.9 is
validated or refuted. It does not promote anything, retire anything, or change
any record's status. It establishes nothing about ML-KEM security in either
direction and nothing about Carrier et al.'s Kyber cost figures. Every number is
scoped to two archived toy-dimension files, their mid bands, the raw undivided
score scale, the inherited degrees, and the seven null objects named above.
