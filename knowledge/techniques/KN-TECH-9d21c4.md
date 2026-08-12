---
id: KN-TECH-9d21c4
type: technique
title: Null sufficiency - deriving a contrast's forced value before measuring it, and the three ways a control passes without being able to fail
tags: [methodology, controls, nulls, experiment-design, falsification, statistics, surrogate, ablation, pre-registration]
complexity: "Not an algorithm. Cost is one derivation per contrast, done before compute: minutes of algebra against runs that have cost this program four batches. The sensitivity demonstration is usually one extra arm in an existing script."
applicability: "Any experiment whose headline is a CONTRAST between a real object and a surrogate, ablation, shuffle, permutation or synthetic control - i.e. most empirical claims about structure. Independent of cryptography; the worked failures happen to be lattice ones."
confidence: verified_by_execution
source_refs: [EV-MLKEM-b43de0, DEC-20260803-81b778, DEC-20260803-264d6a, RT-20260803-d2e23e, VAL-20260803-3fc363, TASK-20260804-7e6b54, KN-TECH-056]
added: 2026-08-05
superseded_by: null
---

## The rule

Before measuring a contrast between a real object and a null object, **derive
what that contrast must be under the null you are not testing.** If the sign is
forced by the construction, the measurement carries no information about the
question, and no amount of replication repairs that.

Stated as a four-part obligation, all four required, in this order:

1. **Object.** Name exactly what the null removes, and what it preserves.
2. **Statistic.** Name the statistic that will be computed on both arms.
3. **Sensitivity demonstration.** Exhibit, for that *(object, statistic)* pair,
   a case where the statistic provably moves when the object is removed. Naming
   the object is necessary and not sufficient.
4. **Forced value.** Derive the contrast's value under the *alternative* to the
   hypothesis before running. If the derivation returns the observed sign and
   magnitude for free, stop: the experiment as designed cannot answer the
   question.

Steps 1-3 are ordinary good practice and are widely followed. **Step 4 is the
one that is usually missing, and it is the one that catches the expensive
failures.** Steps 1-3 ask whether the instrument works. Step 4 asks whether the
measurement is *about anything* - a distinction the first three cannot make,
because an instrument that works perfectly can still be pointed at a quantity
whose answer was fixed before the data existed.

## Why replication does not substitute

A forced contrast replicates perfectly. That is what "forced" means. Replication
raises confidence that the number is real; it says nothing about what the number
is *of*. A statistic whose sign is guaranteed a priori is not evidence however
many independent instances reproduce it, and the tighter the error bars, the
more convincing the artifact looks. Replication and informativeness are
orthogonal axes, and experimental practice routinely treats the first as
evidence for the second.

The same applies to the *anti-artifact* signatures. A contrast that grows with
sample size, or decays when a nuisance parameter is increased, feels like a real
effect. Check the algebra first: if the real arm has any fixed non-decaying
component `b` and the surrogate arm is pure sampling noise `k/2N`, then the ratio
is `sqrt(1 + 2Nb^2/k)`, which is *necessarily* increasing in `N`. "Monotone
increasing over four sample sizes" is then one number, `b`, reported four times.

## The three failure modes, and how each is caught

These are the three distinct ways the check fails. They are ordered by how hard
they are to see, and each was paid for.

### Mode 1 - the null that cannot fail (caught by step 3)

The statistic is *provably invariant* under the removal. Power is not low; it is
exactly zero.

*Worked case.* A campaign row-permuted a database and scored the correct secret.
But the correct candidate's phase offset is `y_i . (s - s) = 0` for every row,
whatever `y` sits in row `i`, so the correct-secret score is **bitwise**
unchanged by any row permutation. Measured max deviation: `0.0` on 9 of 9
instances, exactly. The control was run, reported, and passed, and it was
incapable of failing.

*Catch.* Step 3. Try to construct a case where the statistic moves. If you
cannot, that is not a hard experiment - it is a proof that the pair is
inadmissible.

### Mode 2 - the null whose statistic never reads the object (caught by step 3)

Subtler and more common. The statistic *contains* the object, so mode 1's
invariance test passes, but it contains it in a form the *contrast* cannot see.

*Worked case.* A redesign removed `y_lat` from a pairing. Every candidate's
score did carry the residual phase `psi_i = 2 pi (y_lat,i . s_lat)/q`, and the
correct bin genuinely moved under the null (paired `|z|` medians 14.8-31.3). But
`psi_i` is **candidate-independent**: it multiplies every candidate's row-`i`
term identically, so it cannot generate *across-candidate* contrast at first
order. The group statistic was blind while the per-row statistic was not. The
tell was decisive and cheap: setting `psi := 0`, the *maximal* removal of the
object, landed **beyond** the random surrogate and on the **opposite side** from
the real data. Total removal should be at least as extreme as partial removal
and on the same side; when it is not, the statistic is not tracking the object.

*Catch.* Step 3 applied **per statistic, not per null**. `statistic_reads_the_
object` is a property of an *(object, statistic)* pair. A null registry that
records it once for a list of statistics will be simultaneously true and false,
and a reader who consults the registry will reach the opposite conclusion from a
reader who consults the analysis. That exact contradiction sat archived in this
program's own artifacts.

### Mode 3 - the forced contrast (caught only by step 4)

The statistic reads the object, the sensitivity demonstration succeeds, the null
is honestly constructed, the effect replicates - and the contrast's sign and
growth were still fixed by the definitions before any data were taken.

*Worked case.* The null preserved a property that the definition of the real
object guarantees. Scores were `(1/N) sum_i cos(2 pi (x_i.e + y_i.(s-c))/q)`, and
the objects were dual vectors, i.e. `y = A^T x mod q` *by definition*. So the
wrong-candidate score collapses to `F(e - a_k)`, one Fourier coefficient of the
`x`-database at a frequency where the database is coherent **because the vector
is short** - `a_k . x_i` is exactly the small quantity `Y[i,k]`. The real arm
therefore has a non-zero `N`-independent floor; the permuted arm is a product of
marginals with spread `~ N^{-1/2}`. Excess `> 1`, and increasing in `N`, before
any measurement. Three batches measured it, nine of nine instances agreed, the
decay control fired in the "right" direction, and none of it bore on the
question.

*Catch.* Step 4 only. Every step-1-to-3 obligation was met.

## How to run step 4

Three moves, cheapest first. Any one of them is usually enough.

1. **Substitute the definition into the statistic and expand.** Most forced
   contrasts are visible in two lines once the defining relation of the object
   (here `y = A^T x mod q`) is substituted into the score. If a quantity the
   null preserves appears in the answer, the null preserves the cause.
2. **Build the null object with the mechanism deleted.** Strip everything you
   believe is doing the work and check the effect survives. In the worked case
   an ensemble of iid Gaussians with `y` a coordinate slice of `x` - no lattice,
   no sieve, no matrix, no modulus - reproduced the excess, the decay, and the
   graded contrast. That is a *constructive* refutation and it is far stronger
   than a statistical one. Pair it with the null-of-the-null: the same marginals
   with the dependence removed at the source, which must return nothing (it
   returned 1.04, flat), or you have only shown your instrument is broken.
3. **Ask what the null hypothesis predicts for your statistic, numerically.**
   Not "is the real arm different from the surrogate" but "what value does the
   assumption under test predict, and where do *both* arms sit relative to it".

Move 3 is the one that gets skipped, and it is nearly free.

## The diagnostic that move 3 buys: check both arms against the reference model

If the hypothesis is about a *model* - independence, randomness, a predicted
variance - then the model itself supplies a reference value, and both arms can be
scored against it directly with no surrogate at all.

In the worked case the assumption was that wrong-candidate scores behave as
independent draws with variance `1/2N`. The statistic `sd / sqrt(1/2N)` was
already in the producer's code, its predicted value is `1` (strictly `c4(k)`, the
sample-standard-deviation bias factor - `0.9650` for `k = 8`, and using `1.0` is
a 3.5% error that is *not* negligible against effects of this size). Measured:

| arm | `sd_ratio_to_iid` | vs the model |
|---|---|---|
| real database | 0.1403 | **7.13x below** |
| row-permuted surrogate | 0.1066 | **9.39x below** |

Both arms fail the reference model by roughly an order of magnitude. The
campaign's headline was the **ratio between two objects that both fail the test**,
which is why it could be large, replicable, and uninformative at the same time.
The number cost zero compute, sat in the results file for three batches, and was
never reported, because the comparison had been chosen before anyone asked what
the null hypothesis predicted for it.

Worse - and this is the part that generalises - **the surrogate preserved the
cause of the failure.** The shortfall is driven by the offsets being small, i.e.
by `||y||` being short; a row permutation preserves the `||y||` multiset exactly.
So the surrogate arm was *forced* to fail the reference model too. In closed form:

```
sd_ratio_rowperm  ~=  c4(k) . rms(2 pi Y / q) . rms(sin u) / sqrt(1/2),
    rms(sin u)^2 = (1 - exp(-4 a_x))/2,     a_x = 2 pi^2 sigma^2 mean||x||^2 / q^2
```

which reproduces the measured surrogate value to **0.6%** pooled over nine
archived instances (max 1.1%), and to 1.2% and 3.5% on two further vector
families measured afterwards at 1.2x and 2.2x the norm scale - so it is a
prediction, not a fit. A control that provably lands where the real arm lands,
for a reason internal to the definitions, was never a control.

*Generalisation.* **Ask which property of the real object causes the departure
from your reference model, then check whether your null preserves that property.
If it does, the null is decorative.**

## What the technique does not claim

- It does not say a forced contrast is *false*. The measurements in the worked
  case are sound, reproduced independently, and stronger than originally
  claimed. They are simply not about the question.
- It does not license closing a lane. A null shown inadmissible removes one
  comparison, not the question behind it; per `docs/inventor-protocol.md`, a
  negative reading carries the same burden as a positive one. Premature closure
  is a failure mode symmetric with overclaiming.
- Step 4 is not a new claim tier and passing it asserts nothing. It is a
  falsification aid, and a failed step 4 is frequently the useful result.
- The derivations here are first order. They identify a dominant mechanism; they
  do not account for every residual, and the closed form above degrades as the
  expansion parameter grows (3.5% at 2.2x norm scale, from 0.6%).

## Cost of not doing it

Four batches of one campaign. Three of them measured a quantity whose sign and
growth were fixed a priori; the fourth was spent establishing that. Every
control that ran, passed. The failure was never a weak control - it was that
the comparison was chosen before anyone asked what the null hypothesis predicted
for it. The check that would have caught it costs one derivation, and it is
cheapest on the day the statistic is chosen.

## Checklist

Copy into any experiment contract that reports a contrast.

```yaml
null_sufficiency:
  object_removed:            # exactly what; and what is preserved
  object_preserved:          # the list that matters more than the removal list
  statistic:                 # one entry PER STATISTIC, never one per null
  statistic_reads_the_object: # per statistic. Prove it, do not assert it.
  sensitivity_demonstration: # a case where the statistic provably moves
  maximal_removal_control:   # total removal must be at least as extreme as
                             # partial, and on the same side. If not, mode 2.
  forced_value_derivation:   # what the contrast MUST be under the alternative
  forced_value_number:       # the actual number, before the run
  reference_model_value:     # what the assumption under test predicts
  both_arms_vs_reference:    # where BOTH arms sit against it
  can_this_null_fail:        # if no, it is not a null
```

The two lines that do the work are `object_preserved` and
`forced_value_derivation`. Everything else is bookkeeping around them.
