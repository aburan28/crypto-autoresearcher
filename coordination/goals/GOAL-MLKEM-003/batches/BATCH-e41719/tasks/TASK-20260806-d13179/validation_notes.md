# Independent validation of the BATCH-e41719 joint-null package

Validator notes — `TASK-20260806-d13179`, `BATCH-e41719`, `GOAL-MLKEM-003`,
`EXP-MLKEM-011`. Package under review: snapshot commit
`acdd1398e90ef28c76455d98597a27c46bbb5329`, producer `TASK-20260806-518328`.

**Verdict: ADMISSIBLE_WITH_DEFECTS.** The receipt is admissible evidence. That
says nothing about ML-KEM, about Approximation 4.9, or about whether the
sub-Poisson deficit is real. AGENTS.md rule 12 stays UNMET and UNWAIVED;
`EV-MLKEM-011`, `EV-MLKEM-013`, `EV-MLKEM-017` keep their status; `KN-FIND-031`
stays withdrawn. Toy tier, raw undivided score scale, no ML-KEM security claim
in either direction.

## Inference provenance

```yaml
requested_policy: review-adversarial
reasoning_effort: xhigh
resolved_model_id: claude-opus-5
model_verified: false
fallback_used: true
fallback_reason: >-
  orchestration/model-policies.yaml names GPT-5.6 policy aliases this Claude
  Code harness cannot resolve.
independent_session: true
originated_the_claim_under_review: false
```

---

## 0. What I did that the producer did not

I did not re-run `joint_null.py` and I did not import the BATCH-015 module.
Everything below comes from my own code:

| step | producer's route | my route |
|---|---|---|
| read the `.out` bytes | `b015.ingest`, 80-digit `Decimal` recovery | own parser, `float(s)*M` + `round`, with a `"%.18e"` round-trip check |
| mid band | `b015.regions` | re-derived the region rule from the thresholds |
| GLM | Fisher scoring on a **Chebyshev** basis (b015) | own IRLS on a **monomial** basis in `u ∈ [-1,1]`, own Gauss-Jordan solver |
| null means | **Monte Carlo**, 800 replicates | **analytic**, the projection identity, no sampling at all |
| joint nulls | iteration-resampling (`JN-2` bisect-per-draw, `JN-3` systematic πps) | Multinomial by **sorted order statistics**; Gaussian-**copula** nulls with exact inverse-CDF marginals |
| model-free null mean | Monte Carlo | **closed form**: line lack-of-fit against the fitted rate profile |

The analytic route is the load-bearing one. For the log-link Poisson GLM,
`Y - μ̂ ≈ (I - A)(Y - μ)` with `A = W B (B'WB)^{-1} B'`, so for any second-moment
matrix `Σ`

```
E[ mean_A t ]  =  (1/|A|) Σ_{i∈A}  [(I-A) Σ (I-A)']_ii / ( μ_i (1 - h_i) )
```

which is exact to first order and needs no null sampler. It is what lets me
check the producer's **argument** rather than only the numbers illustrating it.

## 1. Receipt integrity

Commit `acdd1398e` is reachable from `HEAD`, its parent is
`7744cbe6972661494b7e1c834ba7b14793038a05` as the receipt declares, and it
changes exactly the seven declared paths (six artifacts plus the receipt).
All six artifact SHA-256s match the receipt and the committed blobs match the
working tree. `stderr.txt` is 0 bytes. The producer's recorded `git_commit`
`7744cbe69` is the parent of the snapshot, which is correct: the run predates
the commit that archives it. `git_tree_dirty: true` with one porcelain line is
consistent with the untracked task directory. Input `.out` hashes match the
producer's receipt and the files are unchanged since commit `7d639bb4f`.
Wall clock 720.6 s of 3600, peak RSS 28.2 MB of 4 GB.

Naming the command as standing binding (f) requires:
`find coordination/goals/GOAL-MLKEM-003/batches -name "__pycache__" -o -name "*.pyc"`
→ empty. BATCH-017 D-11 stays closed, before and after my own work.

## 2. Reproduction of the observed statistics

Through the entirely independent pipeline above, from the raw `.out` bytes:

| quantity | producer | mine | status |
|---|---|---|---|
| n43 mid band | (551, 851), 301 cells, total 98419 | identical | reproduced |
| n43 φ whole band | 0.802295 | 0.802295 | reproduced |
| low-occupancy subset | 164 cells, contiguous, [137,300] | identical | reproduced |
| **164-cell mean t** | **0.681097** | **0.68109701** | reproduced |
| model-free L=25/50/75/100/150 | 0.4531/0.5614/0.6882/0.6597/1.5513 | 0.45309/0.56141/0.68817/0.65974/1.55126 | reproduced |
| lag-1 acf of t, whole band | 0.014733 | 0.014733 | reproduced |
| lag-1 acf of t, subset | −0.0704 | −0.070380 | reproduced |
| n50 mid band, subset, mean t | 496 cells, 313, 1.034949 | identical, 1.03494948 | reproduced |
| n50 model-free 25/50/100 | 1.0421/0.9607/1.1919 | 1.04207/0.96070/1.19193 | reproduced |

The step I claim as independently checked here is **the recovery of the counts
from the file and the fit of the rate model**, by a different parser, a
different polynomial basis and a different linear solver. Agreement to eight
significant figures on `mean t` is not a shared-bug artifact.

The producer's stated convention for the model-free statistic — OLS line in the
within-window index, RSS/(L−2), divided by the window mean of the raw
increments — is confirmed: it is the only convention that reproduces all five
archived values, and I reached it independently.

## 3. Priority 1 — the identity argument

The producer's §3.5 says: `Var(D_T)` is a functional of the marginal law alone,
so coupling cannot lower it; the marginals therefore pin the null **mean**; the
whole room a budget-preserving joint null has to move a z lies in the null
**sd**, and it moves that sd **down**.

**The first clause is right. The inference from it is not.**

The statistic is not `(D-μ)²/μ` with known `μ`. It is `(D-μ̂)²/(μ̂(1-h))` after a
degree-5 refit, and the leverage factor `(1-h)` is precisely the first-order
correction to `E[(D-μ̂)²]` **derived under independence**. Off-diagonal terms of
`Σ` enter `E[t]` through `[(I-A)Σ(I-A)']_ii`. The marginals do not pin the null
mean; the marginals plus the assumption that `Σ` is diagonal do.

How much room is there? I held the marginals **exactly** at N2's and varied only
the coupling, using an AR(1) correlation `Σ_jk = r^{|j-k|} sqrt(v_j v_k)`:

| r | analytic null mean | shift |
|---|---|---|
| −0.60 | 1.004864 | +0.0128 |
| −0.20 | 0.997710 | +0.0057 |
| 0 | 0.992025 | — |
| +0.20 | 0.983563 | −0.0085 |
| +0.40 | 0.969629 | −0.0224 |
| +0.60 | 0.942378 | −0.0496 |
| +0.80 | 0.865356 | **−0.1267** |

The room the producer says is zero is worth up to −0.127 in the null mean —
larger than the entire sd move it allots to the joint family. Monte Carlo at
exact N2 marginals agrees and shows mean and sd moving together, which is not
what a pure-sd story predicts:

| null | null mean | null sd | z |
|---|---|---|---|
| JV-AR r=+0.20 | 0.9892 | 0.1125 | −2.74 |
| JV-AR r=+0.40 | 0.9722 | 0.1283 | −2.27 |
| JV-AR r=+0.60 | 0.9322 | 0.1558 | **−1.61** |
| JV-AR r=+0.75 | 0.9024 | 0.1751 | −1.26 |

**So yes: there is a joint construction the producer's framing excludes, and it
does rescue the rejection.** Short-range positive coupling at fixed marginals,
at `r ≈ 0.6`, brings the 164-cell reading inside 2 sd.

**And the data exclude it — decisively, on a statistic the producer already
computed.** The same nulls predict the lag-1 autocorrelation of the *Pearson
residuals*, whose observed value is +0.103955:

| r | null lag-1 acf of Pearson residuals | observed sits at |
|---|---|---|
| −0.30 | −0.3073 ± 0.0532 | +7.7 sd |
| +0.20 | +0.1754 ± 0.0569 | −1.25 sd (compatible) |
| +0.40 | +0.3676 ± 0.0582 | **−4.5 sd** |
| +0.60 | +0.5608 ± 0.0488 | **−9.4 sd** |
| +0.75 | +0.7074 ± 0.0408 | **−14.7 sd** |

The amount of short-range coupling the data actually support (`r ≈ 0.1–0.2`)
leaves the statistic at z = −2.74. The amount needed to rescue it is excluded at
9 sd.

**Why the producer's conclusion is nonetheless right for its own nulls**, for a
reason it does not give: JN-2 and JN-3 both carry **rank-one** coupling
(`Σ = diag(v) − c w w'`), and a rank-one perturbation along a smooth direction is
almost annihilated by the residual projection `(I-A)`, which is a high-pass
filter after a degree-5 fit. Analytically the coupling moves the null mean by

* JN-2 (multinomial, band total fixed): **−3.2 × 10⁻⁴** (1.000000 → 0.999676)
* JN-3 (fixed-size 0/1 per iteration): **< 10⁻⁶** (0.992025 → 0.992025)
* JN-P (the faithful physical null): **0** to six decimals; null mean 1.000000,
  identical to independent Poisson.

That is a far sharper statement than the producer's ±1% Monte-Carlo one, and it
settles the dispatching hypothesis: **the hypothesis was misconceived in
direction, but not for the reason given.** It is not that coupling cannot move
the mean. It is that (a) the *physical* coupling is O(μ/M) ≈ 10⁻⁷ and therefore
inert, and (b) any *budget-type* coupling is rank-one along a smooth direction
and is filtered out by the statistic itself. The class of coupling that would
matter is short-range, and the observed residual autocorrelation excludes it.

**Consequence for the priority attack, both directions.** A null that is too
tightly constrained would manufacture the deficit's survival. JN-2 and JN-3 *are*
over-constrained and the producer says so — but I can now bound what that
over-constraint buys: it narrows the null sd by 0.9% (producer) and moves the
null mean by ≤3×10⁻⁴ (my analytic value). Neither manufactures anything. The
faithful joint null JN-P is analytically indistinguishable from independent
Poisson, so the honest reference for this band **is** the independence family,
and the deficit is measured against it. Symmetrically, the independence
assumption did not manufacture the deficit's presence either.

## 4. Priority 2 — is JN-3 the joint minimum-variance object?

Three separate questions; the answers differ.

**(a) Are JN-3's marginals exactly N2's? YES, verified analytically.** With
`max π = 0.7392 < 1`, each cell spans an interval of length `π < 1` on the
cumulative axis and therefore crosses at most one integer threshold, so the
`if` (rather than `while`) in the producer's selection loop is correct and each
iteration contributes 0 or 1 per cell. Systematic πps with a uniform random
start gives inclusion probability exactly `π_T` for any fixed order, and
averaging over a random order preserves that. Across `nb` independent
iterations, `D_T ~ Binomial(nb, π_T)` exactly — N2's law. Confirmed empirically:
my copula null JV-C3, which imposes exactly those marginals by inverse CDF,
reproduces the producer's JN-3 null mean to 0.0001 (0.9958 vs 0.9957).

**(b) Does it attain the per-cell floor? YES**, trivially, because it has N2's
marginals — `Var(D_T) = μ_T(1 − occ_T)`, the Cauchy-Schwarz floor over
independent iterations. But that is exactly what N2 already does. JN-3 adds
nothing to the marginals.

**(c) Is it "the JOINT minimum-variance object"? NO — this claim is
unsupported.** The report offers no variational statement: minimum of what, over
what class. The only aggregate that could be meant is `Var(Σ_A D)` on the
subset. On my own numbers:

| object | `Var(Σ_A D)` | dependence ratio |
|---|---|---|
| independent, N2 marginals | 5058.5 | 1.0000 |
| JN-2 (band total fixed) | 4847.5 | 0.9485 |
| **JN-3 (fixed-size, 0/1 per cell)** | **4659.4** | **0.9211** |
| a fixed-size design constraining the **subset** count per iteration | 803.3 | **0.1588** |
| any joint law with these marginals, best case | ≈0.2 | ≈0 |

Per iteration the subset expects `Σ_A π = 1.2783` candidates, fractional part
0.2783, so a design that fixes the subset count per iteration has aggregate
variance `nb·0.2783·0.7217 = 803`. **JN-3 leaves a factor 5.8 of the available
aggregate variance unclaimed** and is nowhere near a minimiser. What JN-3
actually is: the natural iteration-level fixed-size design that attains the
per-cell floor and carries an unstructured negative coupling. That is a
legitimate and useful null object; it is not "the" joint minimum. The
over-claim is in the wrong direction for the producer's own argument — a
genuinely tighter joint null would make |z| *larger*, not smaller — so no
number changes, but BATCH-017's W-10 gap is not closed by this construction.

**The shuffle.** It is a legitimate fix for a real artifact: unshuffled
systematic sampling perfectly couples cells 1.0 apart on the cumulative-π axis,
which at subset occupancies of ~0.005 means cells ~200 apart — a pure artifact
of the scheme. But the shuffle introduces its own: it makes the coupling
**exchangeable and spatially unstructured**, i.e. mean-field. For a
score-indexed counting process that is a strong and unmotivated modelling
choice, and it is precisely the coupling direction the statistic is blind to.
So the shuffle guarantees in advance that JN-3 cannot move the statistic. That —
not the low occupancy — is the sharp reason for the producer's own Surprise 2
(JN-3's sd only 0.9% below N2's). The producer's explanation ("with `Σπ = 24.6`
candidates per iteration spread over 301 cells, the competition each cell feels
is tiny") is a correct statement of the coupling's magnitude; the projection
argument explains why even a much larger coupling of that shape would not move
the statistic.

**Instrument check.** The producer reads the coupling off a measured dependence
ratio. Exact values exist: 0.9480 (JN-2) and 0.9211 (JN-3, conditional-Poisson
second moments). The producer measured 0.8968 and 0.8931; my own independent
nulls measured 0.8706 (exact multinomial) and 0.8827 (copula). All four
measurements sit 3–8% below the exact values, i.e. the instrument is
noise-limited at about its own claimed 5%, and the reported magnitudes overstate
the coupling. The *analytic* values confirm the sign and the fact that both
joint nulls carry the coupling claimed for them, which is the substantive point.
Similarly, JN-3's band-total sd is exactly
`sqrt(nb·frac(Σπ)·(1−frac(Σπ))) = 30.9`; the producer measured 30.1.

## 5. My own joint nulls, and whether they agree

Five independent constructions, seeds in `resource_receipt.json`, 800
replicates each, statistic recomputed through my own GLM refit:

| my null | construction | null mean | null sd | **z** |
|---|---|---|---|---|
| JV-C0p | exact Poisson marginals, copula machinery, no coupling | 1.0040 | 0.1152 | −2.80 |
| JV-C0 | exact Binomial(nb,π) marginals, no coupling | 0.9885 | 0.1071 | −2.87 |
| **JV-M** | **exact Multinomial(S,p) by sorted order statistics** | **1.0011** | **0.1075** | **−2.98** |
| **JV-C2** | copula, Poisson marginals + JN-2's rank-one coupling | **0.9937** | **0.1087** | **−2.88** |
| **JV-C3** | copula, exact N2 marginals + conditional-Poisson coupling | **0.9958** | **0.1085** | **−2.90** |

against the producer's JN-2 (−2.84) and JN-3 (−2.82) and the analytic null
means 0.999676 and 0.992025.

**They agree.** JV-M's null mean matches the producer's JN-2 to 0.001 (0.25
Monte-Carlo standard errors) with a band total fixed at sd 0.0 exactly, as the
construction requires. JV-C3's null mean matches JN-3 to 0.0001 — from a
completely different generative mechanism (inverse-CDF copula, no iterations at
all). Every one of my joint nulls gives a z at least as extreme as the
producer's: −2.87 to −2.98 against the producer's −2.82 to −2.84.

**The deficit survives every joint null I built.** The model-free statistic
behaves the same way under my nulls (z = −2.74 to −2.84 at L=100).

One measured discrepancy I record rather than reconcile: my independent
N2-equivalent gives null mean 0.9885 where the producer's N2 gives 0.9832; the
analytic value is 0.992025. The producer's N2 mean is 2.4 Monte-Carlo standard
errors low; mine is 0.9 low. This is the same "reproduction discrepancy" the
producer records against BATCH-017's archived 0.9995 (which is 1.9 SE *high*).
All three are Monte-Carlo scatter around 0.9920; the analytic value should be
the reference. It moves z from the producer's −2.69 to −2.76 for N2 —
conservative in the same direction as everything else.

## 6. Priority 3 — Surprise 1, and the number it corrects

**Reproduced, by a route with no Monte Carlo at all.** The model-free statistic
is `RSS/(L−2)` divided by the window mean, after fitting a *straight line*. Its
null expectation is

```
E[stat] = [ Σ_i v_i (1 - p_ii)  +  ||(I-P)μ||² ] / ( (L-2) · μ̄ )
```

and the second term is the straight line's **lack of fit to the curved rate
profile** — deterministic, not noise. Computed directly from the fitted μ:

| L | noise term | lack-of-fit ‖(I−P)μ‖² | **analytic null mean** (v=μ) | producer's measured range | observed |
|---|---|---|---|---|---|
| 25 | 276.1 | 0.3 | **1.0007** | 0.9903–1.0119 | 0.4531 |
| 50 | 633.5 | 7.2 | **1.0109** | 0.9997–1.0107 | 0.5614 |
| 75 | 1111.5 | 53.5 | **1.0474** | 1.0378–1.0482 | 0.6882 |
| 100 | 1777.2 | 243.1 | **1.1359** | 1.1238–1.1400 | 0.6597 |
| 150 | 4047.7 | 3037.3 | **1.7486** | 1.7282–1.7557 | 1.5513 |

The producer is right and the mechanism is now explicit. At L=150 the
deterministic curvature term is 43% of the total, which is why the null mean is
1.75 rather than 1.

`EV-MLKEM-890e2a` W-1 lines 56–57 and `DEC-20260803-95176a` line 59 quote
"0.453, 0.561 and 0.660 … against an expectation of 1 with sampling sd 0.29,
0.20 and 0.14". **The corrected reference values are:**

| L | expectation (was 1) | sampling sd (was) | implied z (was) | **corrected z** |
|---|---|---|---|---|
| 25 | **1.001** | **0.28–0.30** (0.289) | −1.89 | **−1.86 to −1.98** |
| 50 | **1.011** | **0.20–0.21** (0.202) | −2.17 | **−2.09 to −2.25** |
| 100 | **1.136** | **0.16–0.18** (0.142) | −2.40 | **−2.74 to −2.91** |

**The correction makes the finding STRONGER, not weaker.** At L=25 and L=50 it
is immaterial. At L=100 the archived reference understated the deficit by about
0.4 in z. And it removes an apparent internal inconsistency: the archived L=150
reading of 1.551, which against an assumed expectation of 1 looked like a
*super*-Poisson excess pointing the other way, is in fact 0.9 sd **below** its
own null and points the same way as every other window. A correction record
against `EV-MLKEM-890e2a` W-1 is warranted; it is the Coordinator's to make, not
mine.

Note in passing the internal inconsistency the producer flags and I confirm: the
statistic divides RSS by (L−2) while the archived sampling sd assumed
`sqrt(2/(L−1))`. Immaterial, since every sd here is measured or derived.

## 7. Priority 4 — JN-4 and the live exposure

**The inflation arithmetic reproduces.** `|0.983223 − 0.681097| / 2 = 0.151063`
against a measured N2 sd of 0.112512 gives 1.3426× sd and 1.8027× variance,
exactly as recorded. Two qualifications:

* it is computed off **n43_N2, the lowest null mean of the five**. Off N1x, JN-2
  and JN-3 the requirement is 1.408×, 1.421× and 1.410× sd (1.98×, 2.02×, 1.99×
  variance). Off the analytic null mean 0.99203 it is 1.38× (1.91×).
* a single "sd inflation factor" presumes the null mean is fixed, which §3 above
  shows is false for exactly the kind of dependence that widens a null. My JV-AR
  rows rescue by moving mean **and** sd together.

**The lag-1 non-exclusion reproduces arithmetically but the test has almost no
power.** Every one of the producer's twelve recorded lag-1 z values recomputes
from `results.json` to within 0.005. But the quantity being tested separates the
hypotheses by almost nothing: the null mean lag-1 acf of `t` is −0.0014 under
independence, +0.0093 under JN-4(0.20, 25) and +0.0292 under JN-4(0.35, 25),
against a sampling sd of 0.080–0.086. The rescuing JN-4 points are 0.1–0.4 sd
from independence on this statistic. "The data do not exclude it" is therefore a
statement about the instrument, not about the data. The producer says the
estimator is noisy and that this is "not a bound"; that is correct, and it
understates how uninformative the test is.

I looked for a statistic with power and **did not find one**. The spread of the
model-free statistic across 12 disjoint L=25 windows, which a smooth dispersion
field with correlation length 25 ought to inflate, gives: observed 0.6418; null
0.5303 ± 0.1251 (Poisson), 0.5565 ± 0.1485 (JN-4 σ=0.20), 0.5963 ± 0.1730
(JN-4 σ=0.35). All three are compatible with the observation. Recorded as an
honest negative: **I could not close the exposure by finding a discriminating
statistic.**

**But I did narrow it, and one headline row does not reproduce.** At 2000
replicates and two independent seeds, with my own samplers:

| σ | ℓ | reps | null mean | null sd | z | **empirical one-sided tail** |
|---|---|---|---|---|---|---|
| 0.20 | 25 | 2000 | 0.9953 | 0.1496 | **−2.10** | **12/2000 = 0.0060** |
| 0.20 | 25 | 2000 | 0.9996 | 0.1481 | **−2.15** | **14/2000 = 0.0070** |
| 0.35 | 25 | 2000 | 0.9989 | 0.2241 | −1.42 | 94/2000 = 0.047 |
| 0.35 | 25 | 2000 | 1.0019 | 0.2133 | −1.50 | 70/2000 = 0.035 |
| 0.55 | 25 | 2000 | 0.9911 | 0.3088 | −1.00 | 282/2000 = 0.141 |

The producer's σ=0.20, ℓ=25 row (z = −1.87 at 300 replicates) **does not
reproduce**: I get −2.10 and −2.15, and the empirical tail is 0.6–0.7%. The
σ=0.35 row does reproduce (−1.55 vs my −1.42/−1.50), but its empirical tail is
3.5–4.7%, still nominally significant one-sided at 5%. The Gaussian z
systematically **overstates** the rescue because the JN-4 null is right-skewed.
So the corrected statement is: **JN-4(ℓ=25) needs σ ≳ 0.35–0.4 to make the
164-cell reading non-significant, not σ ~ 0.2**, and the producer's
"σ ~ 0.2–0.35 supplies it" is too generous at its lower end. The exposure is
real but narrower than reported.

### Is a process whose per-cell dispersion is itself random and spatially smooth a NULL or an ALTERNATIVE?

**It is an ALTERNATIVE.** The producer declined to rule; here is the argument.

1. **It contradicts the hypothesis under test rather than calibrating it.** The
   quantity under test in this lane is whether `Var(D_T) = μ_T`. JN-4 asserts
   `Var(D_T) = μ_T ψ_T` with `ψ_T` random and pointwise ≠ 1. That is a competing
   model of the same quantity, not a reference distribution for it. A null
   object under `docs/inventor-protocol.md` §3 is "an object of the same shape"
   that lacks the property being claimed; JN-4 is a mixed-Poisson object of a
   *different* shape whose per-cell dispersion is itself the free parameter.
2. **It carries a free nuisance parameter that is being chosen, not estimated.**
   σ is selected so that z crosses −2. A reference distribution selected to
   maximise its own p-value is a minimum over a family, which is exactly what
   standing binding (g) forbids being read as an expected value. The producer
   correctly flags (g) for each individual grid row — each row *is* the measured
   mean and sd of that specific null — but §0 sentence 3 and §5 then select the
   friendliest rows and report them as "the" exposure. My replication shows how
   much that selection costs: at the lower selected σ the rescue disappears.
3. **It does not explain the observation, it only widens the reference.** JN-4
   has `E[ψ] = 1`, so its own model-free null mean stays near 1 while the
   observation is 0.45–0.66. It makes the deficit non-significant without
   predicting it. An alternative that widens the error bar without accounting
   for the effect is a weak alternative, and treating it as a null converts
   "we cannot measure this precisely" into "there is nothing here".
4. **The legitimate version has not been done.** A *fitted* JN-4 — (σ, ℓ)
   estimated from the data and then tested for goodness of fit across all
   windows and the whole L-profile — would be a legitimate composite null, at
   the price of paying for the estimated parameters. The producer explicitly
   declines this ("I have not searched for a JN-4 point that reproduces the
   whole L-profile"), and I did not do it either. **That is the concrete open
   item this batch leaves.**

The producer was right to record it as open rather than adjudicate it, and right
to say it is not a dependence variant of a Poisson process. Its status is
`alternative, unfitted, not excluded by any statistic tried in this lane`.

## 8. Priority 5 — the seed collision

I re-derived the scheme `seed(name) = 518328 + Σ_i (i+1)·ord(name_i)`
independently and enumerated the full stream set. Every recorded seed matches
the stated rule. **There is exactly one collision over all 25 streams**:
`n43|JN2` and `n50|JN3` both receive 520379. 24 distinct values for 25 streams.
No other collision exists — I checked all of them, which the producer's D-1 does
not claim to have done.

**Is any number in `results.json` affected? No, quantitatively.** The two
streams are `random.Random(520379)` instances consumed through different
transforms at different rates — 98419 `random()` calls per replicate for
`n43|JN2`, versus per-iteration `shuffle()` (which draws through
`getrandbits`) plus one `random()` for `n50|JN3`. The induced dependence is not
zero but is not expressible in any reported statistic.

**The producer's justification is nonetheless stronger than the facts.** D-1
says "No statistic in this report compares them: every headline comparison is
within a file across nulls with distinct seeds." But §0 sentence 1 quotes the
n43 JN-2 z (−2.84) and §0 sentence 4 / §4.3 quote the n50 control (+0.42 to
+0.62, the JN-3 row being +0.62) as the two sides of one control argument — that
*is* a comparison, and it crosses the collision. The correct justification is
the one about consumption paths, plus the fact that the contrast is qualitative
(sign of z) and not a differenced statistic carrying an error bar. Affected
records: `job_A.n43_JN2.*` and `job_A.n50_JN3.*`. Nothing needs recomputing;
the justification needs restating.

## 9. Lower-priority items

**D-3 (BATCH-015 disclosure).** Confirmed by opening the file:
`grep -n "rounded normal\|inversion below" .../BATCH-015/tasks/TASK-20260803-d9afbd/report.md`
→ line 375, "Poisson sampler uses inversion below `lambda = 30` and a rounded
normal". BATCH-017 D-8's attribution — "neither BATCH-015 nor BATCH-017 records
that N1 is a rounded Gaussian" — is **inaccurate for BATCH-015**. The producer's
D-3 is upheld.

**The substance of D-8 stands.** `b015.poisson_sample` returns
`round(λ + √λ·Z)` with a non-negativity reject for λ ≥ 30, which is not a
Poisson sampler, and 205 of 301 n43 mid-band cells and 68 of the 164 subset
cells exceed λ = 30. It matters only at the 0.5% level, and this package does
not lean on it: N1x re-runs with exact inversion (0.9975 vs 0.9974; z −2.82 vs
−2.79), and N2, JN-2, JN-3 never call it. My own Poisson nulls use my own exact
inversion and land at 1.0040 ± 0.1152 (copula) and 1.0064 ± 0.1088 (direct),
consistent with N1x. **It does not matter for either statistic here.** I note
that `b015.binomial_sample`, which N2 *does* use, is exact (recursive
Beta/BINV) — I read it before saying so, per standing binding (c).

**Job B, recomputed from my own ingest.** Every claim reproduces:

| claim | producer | mine |
|---|---|---|
| non-monotone occupancy steps | 3 in 300 (n43), 0 in 495 (n50) | 3 of 300, 0 of 495 |
| occupancy span | 253×, 199× | 253.2×, 198.6× |
| pooled cells | 797 | 797 |
| geomean n43/n50 occupancy ratio, `pos_norm` | 1.87 [1.57, 2.97] | **1.873** [1.574, 2.971] |
| geomean, `logC` | 2.60 [1.97, 3.37] | **2.598** [1.966, 3.366] |
| geomean, **raw score** | **0.22** [0.17, 0.33] | **0.219** [0.174, 0.327] |
| bins with both files | 10 / 10 / 5 of 10 | 10 / 10 / 5 |
| effective design size | 37–134 of 797 | 36.9–134.1 (4.6%–16.8%) |
| max VIF | 258 301 | 258 301.3, at `logC|deg5|file_specific` |
| max |z| over 24 specs | 2.27 | 2.27, at `T_raw|deg1|common` |
| β̂ range | −330.4 … +14.57 | −330.364 … +14.566 |
| `pos_norm` ≡ `T_raw` file-specific | asserted structurally | verified: identical to 1e-6 relative in every file-specific spec |

**The confound conclusion is sound.** The sign of the cross-file occupancy
contrast reverses with the choice of common coordinate — and it reverses on
*this lane's declared measurement scale*, the raw undivided score. With two
files, the occupancy contrast and the file main effect are one contrast, not
two. No specification produces a coefficient distinguishable from its null, and
β̂ moves three orders of magnitude and changes sign across specifications. This
is a clean negative and the producer does not dress it up. Standing bindings
(h) and (i) are honoured: every coefficient carries its participation ratio, and
the marginal coefficients are reported as marginal coefficients.

**Standing binding (a)/(b).** The report quotes whole-band φ (0.802295,
1.108199) only alongside the archived binding text; effective dof is stated as
O(1) with the range 1.51–2.35 and no single value, and the C ≥ 1000 comparison
is carried. Neither statistic under test is a whole-band ratio. I have quoted no
specific dof value either.

**Standing binding (j).** The producer credits BATCH-015 M-a1 for the marginal
half of JN-P's inertness and claims only the covariance half as new; I checked
`results.json -> files[0].job_A_regions[0].floors` in the BATCH-015 archive and
the value 0.9999999941601551 is there. The credit is correct.

## 10. Does the deficit survive a joint null?

**Yes.** Stated as plainly as the completion gate asks:

* against the producer's two joint nulls, z = −2.84 (JN-2) and −2.82 (JN-3);
* against my three independent joint nulls, z = −2.98 (exact multinomial by
  sorted order statistics), −2.88 and −2.90 (copula constructions);
* against the faithful *physical* joint null JN-P, which is analytically
  identical to independent Poisson to one part in 10⁷;
* the model-free statistic, which needs no rate model, moves by at most 0.13 in
  z under any of these;
* the n=50 control shows no deficit under any null, joint or independent.

The deficit is not an artifact of the independence assumption in the nulls. It
is *not* thereby shown to be real: it survives everything in the
budget-preserving family and everything in the fixed-marginal short-range family
that the data admit, and it remains exposed to an unfitted mixed-Poisson
alternative (JN-4) at σ ≳ 0.35, whose status as null or alternative I rule on in
§7 and which nobody has fitted.

## 11. Scope and limitations

Toy tier: two archived files, q=241, m=40, n=43 and n=50, mid band only, raw
undivided score scale, inherited degrees 5 and 3, occupancy threshold 0.02.
**Nothing here supports or refutes any ML-KEM or Kyber security claim**, and
nothing here bears on Approximation 4.9. Zero new sampling of the physical
system; every random number in this validation belongs to a seeded synthetic
null object of my own, all seeds disclosed.

My analytic route is first-order: `Y − μ̂ ≈ (I − A)(Y − μ)` neglects the
curvature of the log link, which is why the exact analytic null mean under
independent Poisson is exactly 1.000000 while Monte Carlo gives 0.9975–1.0064.
That second-order term is ~0.3% and is smaller than every effect I use it to
adjudicate, but it is an approximation and I record it as one.

My Gaussian-copula nulls impose the target second-moment structure through a
Gaussian dependence and exact discrete marginals; the induced count correlation
equals the Gaussian one only approximately. For the rank-one nulls the pairwise
correlations are ~10⁻³ and the approximation is excellent; for the AR(1) family
at r = 0.6–0.8 it is coarser, and those rows should be read as showing the
*direction and order of magnitude* of the excluded class, not exact values.

I did not re-derive the GLM's leverage correction, the degree selection
(inherited from BATCH-014), or the occupancy-threshold rule. I did not fit JN-4.
I did not find a statistic with power against JN-4 and say so.
