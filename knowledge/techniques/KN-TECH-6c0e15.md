---
id: KN-TECH-6c0e15
type: technique
title: Null sufficiency - deriving a contrast's forced value before measuring it, the three ways a control passes without being able to fail, and the fourth way a decision rule passes without being able to discriminate
tags: [methodology, controls, nulls, experiment-design, falsification, statistics, surrogate, ablation, pre-registration, decision-rules]
complexity: "Not an algorithm. Cost is one derivation per contrast and one exhaustiveness argument per decision rule, both done before compute: minutes of algebra against runs that have cost this program five batches. The sensitivity demonstration is usually one extra arm in an existing script."
applicability: "Any experiment whose headline is a CONTRAST between a real object and a surrogate, ablation, shuffle, permutation or synthetic control - i.e. most empirical claims about structure. Independent of cryptography; the worked failures happen to be lattice ones."
confidence: single_run_experiment
supersedes: KN-TECH-9d21c4
source_refs: [EV-MLKEM-b43de0, EV-MLKEM-ba6c25, DEC-20260803-81b778, DEC-20260803-264d6a, DEC-20260804-5c9fe1, RT-20260803-d2e23e, RT-20260804-37a8f2, VAL-20260803-3fc363, VAL-20260804-a84239, KN-TECH-056]
added: 2026-08-05
superseded_by: null
---

## Status of this entry

**This supersedes `KN-TECH-9d21c4`, which remains immutable and in place.** It is
a creation authorised by `DEC-20260804-5c9fe1` NA-3, not a status change to the
superseded entry. It carries the four corrections that decision recorded as owed,
and one further obligation the corrections implied.

**What changed from `KN-TECH-9d21c4`, item by item:**

1. A **fifth obligation, alternative exhaustiveness**, is added, and it is stated
   in the sharper form the evidence forced: exhaustiveness is relative to the
   alternatives a rule can *distinguish*, not to the values its statistic can
   *take*.
2. **Obligation 3 is now a criterion**, with a named comparator and a declared
   threshold. As advice it produced this program's own `DEF-7`.
3. The **false novelty claim is removed.** The iid shortfall was first reported by
   `RT-20260803-d2e23e` section 3 in batch 3, not by batch 4.
4. The **1.0-versus-`c4(8)` reference error is fixed**, `confidence:
   verified_by_execution` is dropped, and the self-citing `source_refs` entry is
   removed.

`confidence` is now `single_run_experiment`. The superseded entry claimed
`verified_by_execution`; it was written *about* four batches rather than verified
*by* one, and its single live application returned `C_NEITHER`. The present entry
has had one live prospective application (batch 5, `TASK-20260804-f58d34`), where
obligations 1-4 caught three defects before any measurement and obligation 5 was
violated by the same producer that wrote it. That is one run, and the field says
so.

---

## The rule

Before measuring a contrast between a real object and a null object, **derive
what that contrast must be under the null you are not testing.** If the sign is
forced by the construction, the measurement carries no information about the
question, and no amount of replication repairs that.

Stated as a five-part obligation, all five required, in this order:

1. **Object.** Name exactly what the null removes, and what it preserves.
2. **Statistic.** Name the statistic that will be computed on both arms.
3. **Sensitivity criterion.** *(Criterion, not advice — see below.)* Exhibit, for
   that *(object, statistic)* pair, a case where the statistic provably moves when
   the object is removed, **reported as a signed effect against a named comparator
   with a threshold declared before the run.**
4. **Forced value.** Derive the contrast's value under the *alternative* to the
   hypothesis before running. If the derivation returns the observed sign and
   magnitude for free, stop: the experiment as designed cannot answer the question.
5. **Alternative exhaustiveness.** Before freezing a decision rule, state the
   outcomes it can emit and **argue they exhaust the space of explanations, not
   merely the range of the statistic.** If you cannot, the rule must carry an
   explicit NEITHER branch and declare what you will do in it.

Steps 1-3 ask whether the instrument works. **Step 4 asks whether the measurement
is *about anything*** — a distinction the first three cannot make, because an
instrument that works perfectly can still be pointed at a quantity whose answer
was fixed before the data existed. **Step 5 asks whether the *verdict* is about
anything** — which steps 1-4 cannot make either, because a rule can be perfectly
calibrated and still emit the same label for a property of the object and for an
artifact of the apparatus.

## Obligation 3 as a criterion

The superseded entry said "exhibit a case where the statistic provably moves". A
validator's finding against it was exact: *that names no threshold — how much
movement, against what spread, at what sample size, and compared with which arm.*
The program then scored a sensitivity demonstration against the **most separating
arm available** to claim a factor of ~50, where against the arm the null was
actually about the factor was **3.1** (`VAL-20260804-a84239` DEF-7,
`EV-MLKEM-ba6c25` INT-3). A red team added that the "~50x dynamic range" divided
by noise, its own replication giving -0.023.

**The criterion.** A sensitivity demonstration is admissible only if it states,
*before the run*:

- **the comparator, by name**, and it must be **the arm the null is about** — not
  whichever arm makes the demonstration look best;
- **the spread it is scored against**, and it must be the *same* surrogate spread
  used for the headline;
- **a numeric threshold** the demonstration must clear;
- **the dynamic range** of the statistic, with both ends exhibited.

A demonstration that names no comparator is not weak evidence; it is not a
demonstration, because the analyst retains the choice of comparator after seeing
the numbers.

*Worked positive case.* A graded-coupling arm: synthetic matrices
`W = sqrt(1-t) Z_k + sqrt(t) Z_0` whose population off-diagonal correlation is
**exactly `t`**, at the same `(D, K)` as the real arms, with gates declared
before the run — recovered `t` to within 0.02 at every `t`, and the
effective-count statistic ran 24.21 → 3.70 monotonically as `t` went 0 → 0.75.
The comparator is named, the threshold is numeric, both ends of the range are
exhibited, and the whole thing costs no lattice and no sieve.

## Why replication does not substitute

A forced contrast replicates perfectly. That is what "forced" means. Replication
raises confidence that the number is real; it says nothing about what the number
is *of*. A statistic whose sign is guaranteed a priori is not evidence however
many independent instances reproduce it, and the tighter the error bars, the more
convincing the artifact looks.

The same applies to the *anti-artifact* signatures. A contrast that grows with
sample size, or decays when a nuisance parameter is increased, feels like a real
effect. Check the algebra first: if the real arm has any fixed non-decaying
component `b` and the surrogate arm is pure sampling noise `k/2N`, then the ratio
is `sqrt(1 + 2Nb^2/k)`, which is *necessarily* increasing in `N`. "Monotone
increasing over four sample sizes" is then one number, `b`, reported four times.

That algebra has since been confirmed empirically and independently: a red team
derived `excess = sqrt(1 + rho)` for a different observable of the same campaign,
measured `rho` **with no scoring at all**, found it linear in `N`, and predicted
subsampled values to 1.1% and 1.8% (`RT-20260804-37a8f2`).

## The failure modes, and how each is caught

Ordered by how hard they are to see. Each was paid for.

### Mode 1 - the null that cannot fail (caught by obligation 3)

The statistic is *provably invariant* under the removal. Power is not low; it is
exactly zero.

*Worked case A.* A campaign row-permuted a database and scored the correct
secret. But the correct candidate's phase offset is `y_i . (s - s) = 0` for every
row, whatever `y` sits in row `i`, so the correct-secret score is **bitwise**
unchanged by any row permutation. Measured max deviation: `0.0` on 9 of 9
instances, exactly. The control was run, reported, and passed, and it was
incapable of failing.

*Worked case B, and it is worth more than case A because it was caught
prospectively.* A later producer chose as its headline the mean off-diagonal of a
**centred** correlation matrix. Centring by `P = I - J/K` sends any exchangeable
covariance `(1-rho)I + rho 11^T` to `(1-rho)P`, so the centred correlation matrix
is the normalised projector and its mean off-diagonal is **exactly `-1/(K-1)` for
every `rho`**. More generally, whenever the marginal variances are equal the
centred correlation matrix has exactly zero row sums, and the statistic is
identically `-1/(K-1)`. A synthetic check before any measurement returned a
comparator spread of **0.0000**. The tell is mechanical and general: **if your
comparator's spread is zero, your statistic is a constant of the apparatus.**

*Catch.* Obligation 3. Try to construct a case where the statistic moves. If you
cannot, that is not a hard experiment — it is a proof that the pair is
inadmissible.

### Mode 2 - the null whose statistic never reads the object (caught by obligation 3)

Subtler and more common. The statistic *contains* the object, so mode 1's
invariance test passes, but it contains it in a form the *contrast* cannot see.

*Worked case.* A redesign removed `y_lat` from a pairing. Every candidate's score
did carry the residual phase `psi_i = 2 pi (y_lat,i . s_lat)/q`, and the correct
bin genuinely moved under the null (paired `|z|` medians 14.8-31.3). But `psi_i`
is **candidate-independent**: it multiplies every candidate's row-`i` term
identically, so it cannot generate *across-candidate* contrast at first order.
The group statistic was blind while the per-row statistic was not. The tell was
decisive and cheap: setting `psi := 0`, the *maximal* removal of the object,
landed **beyond** the random surrogate and on the **opposite side** from the real
data. Total removal should be at least as extreme as partial removal and on the
same side; when it is not, the statistic is not tracking the object.

*Catch.* Obligation 3 applied **per statistic, not per null**.
`statistic_reads_the_object` is a property of an *(object, statistic)* pair. A
null registry that records it once for a list of statistics will be
simultaneously true and false, and a reader who consults the registry will reach
the opposite conclusion from a reader who consults the analysis. That exact
contradiction sat archived in this program's own artifacts.

### Mode 3 - the forced contrast (caught only by obligation 4)

The statistic reads the object, the sensitivity demonstration succeeds, the null
is honestly constructed, the effect replicates - and the contrast's sign and
growth were still fixed by the definitions before any data were taken.

*Worked case.* The null preserved a property that the definition of the real
object guarantees. Scores were `(1/N) sum_i cos(2 pi (x_i.e + y_i.(s-c))/q)`, and
the objects were dual vectors, i.e. `y = A^T x mod q` *by definition*. So the
wrong-candidate score collapses to `F(e - a_k)`, one Fourier coefficient of the
`x`-database at a frequency where the database is coherent **because the vector is
short** — `a_k . x_i` is exactly the small quantity `Y[i,k]`. The real arm
therefore has a non-zero `N`-independent floor; the permuted arm is a product of
marginals with spread `~ N^{-1/2}`. Excess `> 1`, and increasing in `N`, before
any measurement. Three batches measured it, nine of nine instances agreed, the
decay control fired in the "right" direction, and none of it bore on the question.

A fourth batch then established that the same observable does not read what it
was believed to read at all: a family with **no lattice membership**, norms
matched row for row, and `y` a deterministic function of `x`, separated at
**12.15** — harder than any valid dual family measured. A fifth batch reproduced
that at **12.96** on an independently rebuilt instrument.

*Catch.* Obligation 4 only. Every obligation-1-to-3 requirement was met.

### Mode 4 - the decision rule that cannot discriminate (caught only by obligation 5)

**This is the mode the present entry adds.** Every arm is sound, every forced
value is derived, the rule is frozen in advance and emitted mechanically — and it
returns the *same label* for a property of the object and for an artifact of the
apparatus, because the alternatives it can separate do not include the one that
is operating.

*Worked case A - the two-outcome rule.* A batch froze a rule with exactly two
named outcomes: outcome A, the effect is lattice membership; outcome B, the effect
is sieving. It executed every other obligation impeccably — both forced values
derived and frozen before the run, a mechanical verdict, no re-scoring against a
different rule — and got `C_NEITHER`, because the operative alternative (the
coupling strength between `y` and `x`) was in neither branch. The producer
reported the third outcome honestly rather than choosing a nearest label, which is
the behaviour pre-registration exists to produce. **The defect was upstream, in
the design.** Worse, the archive already contained the refutation: a reviewer's
own report, cited by the decision that froze the dichotomy, recorded in the same
file a valid dual family separating at 5.4349, so on the day the rule was frozen
the archive already said the answer would be neither of its two branches.

*Worked case B - the exhaustive rule that still could not discriminate, and it is
the more instructive one.* A later batch, applying obligation 5 as first drafted,
froze a **five**-branch rule with an explicit NEITHER branch and a written proof
that the branches partition the outcome space by a two-bit case split. The proof
is correct. The rule then emitted the **same branch, `D2`, on all 18 family x
group cells — including all six cells of its own null.** The cause was a forced
value the producer had not derived: the error vector was `m`-dimensional, so every
candidate's score is a function of the same `m` variables and the score covariance
has rank at most `m` to first order, forcing the statistic below its null value
for any candidate count `K > m`. The null reproduced that to 0.8%. A rule that
fires on the null is not discriminating, whatever its branch count.

*Catch.* Obligation 5, in the sharper form that case B forces:

> **Exhaustiveness is relative to the alternatives the rule can DISTINGUISH, not
> to the values the statistic can TAKE.** Partitioning the real line into
> `(-inf,-3), [-3,3], (3,inf)` is a partition of a *statistic*, not of the *space
> of explanations*. Before freezing, list every mechanism that could move the
> statistic — including the apparatus, the sample size, the dimension of the noise,
> and the arithmetic of the estimator — and check that the rule assigns different
> outcomes to at least the object and the apparatus. **If a null arm exists, run
> the rule on the null arm first.** If it emits the same label there, the rule
> discriminates nothing and must be rewritten before the real arm is read.

Two cheap sub-checks, both prospective:

1. **The archive check.** List every archived measurement of the same statistic
   and verify at least one named outcome is consistent with all of them. In case A
   the list was `17.078, 1.0371, 5.4349, 0.1058, 6.19e-15`; reading it would have
   shown both named outcomes were already excluded. Reading time, zero compute.
2. **The null-first check.** Emit the frozen rule's verdict on the null arm before
   looking at the real arm. Case B would have been caught in one line.

## How to run obligation 4

Three moves, cheapest first. Any one of them is usually enough.

1. **Substitute the definition into the statistic and expand.** Most forced
   contrasts are visible in two lines once the defining relation of the object
   (here `y = A^T x mod q`) is substituted into the score. If a quantity the null
   preserves appears in the answer, the null preserves the cause.
2. **Build the null object with the mechanism deleted.** Strip everything you
   believe is doing the work and check the effect survives. In the worked case an
   ensemble of iid Gaussians with `y` a coordinate slice of `x` — no lattice, no
   sieve, no matrix, no modulus — reproduced the excess, the decay, and the graded
   contrast. That is a *constructive* refutation and it is far stronger than a
   statistical one. Pair it with the null-of-the-null: the same marginals with the
   dependence removed at the source, which must return nothing (it returned 1.04,
   flat), or you have only shown your instrument is broken.
3. **Ask what the null hypothesis predicts for your statistic, numerically.** Not
   "is the real arm different from the surrogate" but "what value does the
   assumption under test predict, and where do *both* arms sit relative to it".

Move 3 is the one that gets skipped, and it is nearly free.

**A caution on move 3 that cost a fifth batch a false 4-sigma.** The value the
assumption predicts is usually an **asymptotic** one, and your estimator is run at
finite sample size and often under a constraint your estimator itself imposes.
Two measured examples from one script: a participation-ratio statistic whose
asymptotic null is `K-1 = 7` has a finite-sample null at `6.989` for `D = 4000`,
and a centred maximum whose asymptotic null is `K = 8` has a null near `9.6`
because centring imposes `sum_k W_k = 0` and inflates the standardised maximum by
`~sqrt(K/(K-1))`. Scoring against `7` and `8` manufactured departures of about
four standard deviations **out of data generated as genuinely iid**. The fix is a
rule, not a correction: **the comparator supplies BOTH the reference and the
spread; the asymptotic value is reported beside it as the population target and is
never used as the test reference.** And note that a comparator conditional on the
observed marginals (a per-column permutation) is exactly invariant for any
statistic that depends on the marginals alone — so such statistics need a second,
unconditional comparator, or they are mode 1 again.

## The diagnostic that move 3 buys: check both arms against the reference model

If the hypothesis is about a *model* — independence, randomness, a predicted
variance — then the model itself supplies a reference value, and both arms can be
scored against it directly with no surrogate at all.

In the worked case the assumption was that wrong-candidate scores behave as
independent draws with variance `1/2N`. The statistic `sd / sqrt(1/2N)` was
already in the producer's code, and its predicted value is `c4(k)`, the
sample-standard-deviation bias factor — **`0.96503` for `k = 8`, not `1.0`**.
Measured:

| arm | `sd_ratio_to_iid` | vs `c4(8) = 0.96503` |
|---|---|---|
| real database | 0.140324 | **6.877x below** |
| row-permuted surrogate | 0.106552 | **9.057x below** |

**Correction carried from `DEC-20260804-5c9fe1` and `EV-MLKEM-ba6c25` INT-2.** The
superseded entry tabulated these as **7.13x** and **9.39x**, which are `1/0.140324`
and `1/0.106552` — i.e. computed against **1.0**, in the same passage that argues
1.0 is the wrong reference and that using it is a 3.5% error. The corrected
factors are above. The direction is unchanged; the magnitude was overstated.

**Priority, corrected.** The superseded entry stated this shortfall had never been
reported. That is **false**: `RT-20260803-d2e23e` section 3 reported it in batch 3,
in the archive the claim was citing. Batch 4 quantified it with a closed form and
identified its cause; it did not discover it. The false claim propagated from a
Coordinator decision into a snapshot commit message into a knowledge entry, which
is the general hazard: **an unchecked novelty claim is inherited by everything
downstream, and a knowledge entry is where it becomes permanent.**

Both arms fail the reference model by roughly an order of magnitude. The
campaign's headline was the **ratio between two objects that both fail the test**,
which is why it could be large, replicable, and uninformative at the same time.

Worse — and this is the part that generalises — **the surrogate preserved the
cause of the failure.** The shortfall is driven by the offsets being small, i.e.
by `||y||` being short; a row permutation preserves the `||y||` multiset exactly.
So the surrogate arm was *forced* to fail the reference model too. In closed form:

```
sd_ratio_rowperm  ~=  c4(k) . rms(2 pi Y / q) . rms(sin u) / sqrt(1/2)
    rms(sin u)^2 = (1 - exp(-4 a_x))/2,     a_x = 2 pi^2 sigma^2 mean||x||^2 / q^2
```

where `Y[i,k] = y_i . (s - c_k)` is the phase offset of candidate `k` at vector
`i`, `q` is the modulus, `k` the number of candidates in the group, `u_i =
2 pi x_i . e / q` the error phase, `N` the number of vectors, and `sigma` the
error standard deviation. (The superseded entry left `Y`, `q`, `k`, `u` and `N`
undefined, and a validator had to read the producer's code to recover `rms(Y)`.)
This reproduces the measured surrogate value to **0.6%** pooled over nine
archived instances (max 1.1%), and to 1.2% and 3.5% on two further vector
families at 1.2x and 2.2x the norm scale — so it is a prediction, not a fit. Two
independent reviewers re-derived it before reading the producer's version and
obtained it term for term.

*Generalisation.* **Ask which property of the real object causes the departure
from your reference model, then check whether your null preserves that property.
If it does, the null is decorative.**

## What the technique does not claim

- It does not say a forced contrast is *false*. The measurements in the worked
  cases are sound, reproduced independently, and in several cases stronger than
  originally claimed. They are simply not about the question.
- It does not license closing a lane. A null shown inadmissible removes one
  comparison, not the question behind it; per `docs/inventor-protocol.md`, a
  negative reading carries the same burden as a positive one. Premature closure is
  a failure mode symmetric with overclaiming.
- Obligations 4 and 5 are not new claim tiers and passing them asserts nothing.
  They are falsification aids, and a failed obligation 4 or 5 is frequently the
  useful result.
- The derivations quoted here are first order unless stated otherwise. They
  identify a dominant mechanism; they do not account for every residual, and the
  closed form above degrades as the expansion parameter grows (3.5% at 2.2x norm
  scale, from 0.6%).
- **This entry does not claim the check would have saved any batch.** The
  superseded entry's "cost of not doing it: four batches of one campaign" asserted
  that, and it is unsupported: the batch that *did* run obligations 1-4 still did
  not answer its question. The supportable statement is narrower and is the only
  one made here: **the check is cheap, it is cheapest on the day the statistic is
  chosen, and it has caught defects prospectively** — three of them in one batch,
  before any measurement run, in the producer's own design.

## Checklist

Copy into any experiment contract that reports a contrast.

```yaml
null_sufficiency:
  object_removed:            # exactly what; and what is preserved
  object_preserved:          # the list that matters more than the removal list
  statistic:                 # one entry PER STATISTIC, never one per null
  statistic_reads_the_object: # per statistic. Prove it, do not assert it.
  sensitivity_demonstration: # a case where the statistic provably moves
  sensitivity_comparator:    # NAMED, and it must be the arm the null is about
  sensitivity_threshold:     # numeric, declared BEFORE the run
  sensitivity_dynamic_range: # both ends exhibited
  comparator_spread_nonzero: # if zero, the statistic is a constant. Mode 1.
  maximal_removal_control:   # total removal must be at least as extreme as
                             # partial, and on the same side. If not, mode 2.
  forced_value_derivation:   # what the contrast MUST be under the alternative
  forced_value_number:       # the actual number, before the run
  reference_model_value:     # what the assumption under test predicts
  reference_is_finite_sample: # asymptotic value != estimator's null at finite D
  both_arms_vs_reference:    # where BOTH arms sit against it
  can_this_null_fail:        # if no, it is not a null
decision_rule:
  outcomes:                  # every label the rule can emit
  exhaustive_over_statistic: # the case split, written out
  exhaustive_over_MECHANISMS: # object vs apparatus vs sample size vs noise dim
  verdict_on_the_null_arm:   # RUN IT FIRST. Same label as the real arm => mode 4
  neither_branch:            # required if exhaustiveness cannot be argued
  action_in_neither_branch:  # declared before the run
```

The lines that do the work are `object_preserved`, `forced_value_derivation`,
`comparator_spread_nonzero` and `verdict_on_the_null_arm`. Everything else is
bookkeeping around them.
