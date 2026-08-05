---
id: KN-TECH-1a5b7e
type: technique
title: Null sufficiency - deriving a contrast's forced value before measuring it, the three ways a control passes without being able to fail, the fourth way a decision rule passes without being able to discriminate, and the two ways a correct derivation is scoped to a regime the headline is not in
tags: [methodology, controls, nulls, experiment-design, falsification, statistics, surrogate, ablation, pre-registration, decision-rules, comparator-replication]
complexity: "Not an algorithm. Cost is one derivation per contrast, one exhaustiveness argument per decision rule, and one replication of the comparator, all done before or beside compute: minutes of algebra plus a handful of kernel passes, against runs that have cost this program six batches. The sensitivity demonstration is usually one extra arm in an existing script."
applicability: "Any experiment whose headline is a CONTRAST between a real object and a surrogate, ablation, shuffle, permutation or synthetic control - i.e. most empirical claims about structure. Independent of cryptography; the worked failures happen to be lattice ones."
confidence: single_run_experiment
supersedes: KN-TECH-6c0e15
source_refs: [EV-MLKEM-b43de0, EV-MLKEM-ba6c25, EV-MLKEM-d777f0, DEC-20260803-81b778, DEC-20260803-264d6a, DEC-20260804-5c9fe1, DEC-20260804-485fa6, RT-20260803-d2e23e, RT-20260804-37a8f2, RT-20260804-0ff29a, VAL-20260803-3fc363, VAL-20260804-a84239, VAL-20260804-264ab9, KN-TECH-056]
added: 2026-08-05
superseded_by: null
---

## Status of this entry

**This supersedes `KN-TECH-6c0e15`, which remains immutable and in place.** It is a
creation authorised by `DEC-20260804-485fa6` NA-3, not a status change to the
superseded entry and not an edit of it. `KN-TECH-6c0e15` in turn supersedes
`KN-TECH-9d21c4`; both remain in place, unmodified, and both stay citable.

**AGENTS.md rule 12 is UNMET and UNWAIVED.** This entry changes the status of no
`EV-MLKEM-*` record and proposes none.

### What changed from `KN-TECH-6c0e15`, item by item

Two corrections are owed by `DEC-20260804-485fa6` (`corrections_owed`;
`EV-MLKEM-d777f0` INT-3), and both are made here. Both are in mode 4 case B.

1. **The cell count is wrong.** `KN-TECH-6c0e15` mode 4 case B says the rule
   "emitted the **same branch, `D2`, on all 18 family x group cells — including
   all six cells of its own null.**" The correct figure is **33 of 33**: 21 T1
   cells (3 families x 7 groups), **of which 7 are null cells**, plus all 12 T2
   cells. Eighteen is the number of cells *displayed in the log*, not the number
   *scored*. Source: `VAL-20260804-264ab9` DEF-3, which replayed the frozen rule
   on all 33 archived z-score sets with zero mismatches. The error understates
   the severity of the producer's own self-reported failure, so it was not
   self-serving; it was nonetheless propagated into a permanent knowledge entry,
   which is the hazard the superseded entry itself names in its
   "Priority, corrected" section.

2. **The causal attribution is scoped to a regime the headline is not in.**
   `KN-TECH-6c0e15` mode 4 case B gives the cause as a rank bound: the error
   vector is `m`-dimensional, "so ... the score covariance has rank at most `m`
   to first order, forcing the statistic below its null value **for any candidate
   count `K > m`**." The rank bound is correct and it is **VACUOUS at `K = 8` and
   `K = 25`, which is where every headline cell of that batch sits** (`8 <= 35`,
   `25 <= 35`). A reader with no campaign context takes away a rank condition
   that does not bind in the regime the case study is about. Sources:
   `VAL-20260804-264ab9` DEF-9, `RT-20260804-0ff29a` OBJ-9 and OBJ-10. The
   corrected mechanism is given in mode 4 case B below.

**A third change, not a correction but an addition**, is a new failure mode
(**mode 5**) and one refinement to obligation 3. Both were paid for by the batch
that wrote this entry (`TASK-20260805-74a8e9`, `BATCH-4bc9bc`), and both are
labelled as executor observations that have not yet been through review.

**`confidence` stays `single_run_experiment`, deliberately.** The entry now has
two live prospective applications rather than one, but the second did not
replicate the first, it tested different obligations, and one of its own
controls failed in a way that is written up below as mode 5. Two single runs are
not a replication. Raising the field would be the exact behaviour this entry
exists to catch.

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

**Mode 5 below adds a sixth thing to check, and it is not a sixth obligation
because it is an instance of obligation 3 done properly**: when your comparator
is itself an ensemble, **replicate it before you read a residual against it.**

## Obligation 3 as a criterion

The superseded entry `KN-TECH-9d21c4` said "exhibit a case where the statistic
provably moves". A validator's finding against it was exact: *that names no
threshold — how much movement, against what spread, at what sample size, and
compared with which arm.* The program then scored a sensitivity demonstration
against the **most separating arm available** to claim a factor of ~50, where
against the arm the null was actually about the factor was **3.1**
(`VAL-20260804-a84239` DEF-7, `EV-MLKEM-ba6c25` INT-3). A red team added that the
"~50x dynamic range" divided by noise, its own replication giving -0.023.

**The criterion.** A sensitivity demonstration is admissible only if it states,
*before the run*:

- **the comparator, by name**, and it must be **the arm the null is about** — not
  whichever arm makes the demonstration look best;
- **the spread it is scored against**, and it must be the *same* surrogate spread
  used for the headline;
- **a numeric threshold** the demonstration must clear;
- **the dynamic range** of the statistic, with both ends exhibited;
- **and, new here: whether the statistic is MONOTONE between those two ends.**
  See the refinement below. Exhibiting two ends is not the same as exhibiting a
  direction.

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

### Refinement: exhibiting both ends does not exhibit a direction

*Worked case, and it is the entry's own most recent one.* A later batch built a
graded control for a *different* statistic — the standardised margin of a
designated "correct" column over the maximum of `K` competing columns — using the
same `sqrt(1-t) Z_k + sqrt(t) Z_0` idiom, and declared before the run that `t=0`
must return NULL and `t=0.75` must return one named direction. **Both declared
gates passed.** The grid in between did not: the emitted labels across
`t = 0, 0.10, 0.25, 0.50, 0.75` were NULL, HARDER, HARDER, HARDER, EASIER. The
statistic is **not monotone in `t`**, because raising the shared fraction
simultaneously shrinks the noise in the margin *and* raises the maximum over the
competing columns, and the two effects trade places as `t` grows.

The consequence is specific and it is not a technicality: **a verdict of HARDER
or EASIER from that rule cannot be read as "more dependence" or "less
dependence", because the map from dependence to the label is not monotone.** The
gate as declared was satisfied and the instrument was pronounced fit; the
instrument was fit to *detect* a departure and unfit to *sign* one. A two-point
gate cannot tell those apart.

**The rule.** If the sensitivity demonstration is graded, run at least three
interior points and **report whether the statistic is monotone across them.** If
it is not, say so where the verdict is reported, and do not attach a directional
reading to the label. This costs one extra row in a table that already exists.

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

**What replication DOES buy is in mode 5, and it is a different thing:**
replicating the *comparator* rather than the *effect*. That is not evidence about
the effect; it is the only way to know how wide the comparator is.

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

*Worked case C, and it is the cheapest killer that could not kill.* A campaign's
own named "cheapest possible" next test was to S-orthogonalise the phase columns
and re-measure. For the near-miss candidate group the phase columns **are** the
`Y` columns (`y_i . (s - c_k) = -Y[i,k]`), so orthogonalising them in the `S`
metric zeroes the off-diagonal of that part of the covariance **by algebra**, and
any diagonal covariance has correlation matrix exactly `I`. The test moved that
group from 0.7283 to 0.9740 and left the group that actually carried the headline
at 0.4275 against 0.4149 — it erased the group it could not fail on and did not
touch the group in question (`RT-20260804-0ff29a`, batch-6 recommendation). A
test named as decisive by the producer is not thereby a test.

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

*A second worked case, and it is the sharper one because the null removed the
wrong object rather than preserving the right one.* A batch measuring
across-candidate score dependence built its null by replacing `Y` with uniform
residues mod `q`. That edit removes **two** things at once: the `X`-`Y` dual
pairing, and the **shortness of the candidate phase offsets**. Offset shortness
is a property of the **candidate set**, not of the database — so the null deleted
the defining property of two of the three candidate groups being compared. When
the family was ablated at *fixed* candidate set instead (random-direction `X` at
matched row norms, iid `Y`), an object with no lattice, no sieve, no modulus and
no dual relation reproduced **66%, 71% and 92%** of the reported deficit, and the
reported "roughly a factor 2" became **1.10** (`VAL-20260804-264ab9` DEF-1 and
`forced_value_derivation`; `RT-20260804-0ff29a` OBJ-1 and OBJ-2, reaching the
same conclusion by a different construction). The generalisation at the end of
this entry — *ask which property causes the departure, then check whether your
null preserves it* — has a mirror image, and this is it: **a null that DELETES
the causal property is as inadmissible as one that preserves it.**

*Catch.* Obligation 4 only. Every obligation-1-to-3 requirement was met.

### Mode 4 - the decision rule that cannot discriminate (caught only by obligation 5)

Every arm is sound, every forced value is derived, the rule is frozen in advance
and emitted mechanically — and it returns the *same label* for a property of the
object and for an artifact of the apparatus, because the alternatives it can
separate do not include the one that is operating.

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
is correct. The rule then emitted the **same branch, `D2`, on 33 of 33 scored
cells — 21 T1 cells of which 7 were cells of its own null, plus all 12 T2
cells.**

> **CORRECTION 1, owed by `DEC-20260804-485fa6` and made here.**
> `KN-TECH-6c0e15` records this as "all 18 family x group cells — including all
> six cells of its own null". **The figure is 33 of 33: 21 T1 cells, of which 7
> are null cells, plus all 12 T2 cells.** Eighteen is the count *displayed* in
> the log (the display list had 6 entries), not the count *scored*. Source:
> `VAL-20260804-264ab9` DEF-3, which replayed the frozen rule on all 33 archived
> z-score sets with zero mismatches.

The cause was a forced value the producer had not derived. `KN-TECH-6c0e15`
states that cause as a rank bound — the error vector is `m`-dimensional, so the
score covariance has rank at most `m` to first order, "forcing the statistic
below its null value for any candidate count `K > m`".

> **CORRECTION 2, owed by `DEC-20260804-485fa6` and made here.** That
> attribution is **scoped to a regime the headline is not in**. The rank bound
> is correct and it is **vacuous at `K = 8` and `K = 25`**, which is where every
> headline cell of that batch sits, because `8 <= 35` and `25 <= 35`. A `25 x 25`
> correlation matrix is not constrained by `rank <= 35`.
>
> **What actually depresses the statistic at `K <= m`, from two independent
> reviews:**
>
> - **Channel composition.** With *short* candidate offsets, `cos(phi_ik) ~ 1`
>   for every candidate, so the cosine channel is a pure rank-one common mode
>   carrying no discriminating variance — measured variance share **0.9999 to
>   1.0000 in every short-offset arm, real or synthetic**. All discrimination is
>   therefore pushed into the sine channel, which lives in a space of dimension
>   at most `m` with a strongly anisotropic metric. The statistic is forced below
>   its null value **even for random offsets and even for `K < m`**
>   (`VAL-20260804-264ab9`, `forced_value_derivation`).
> - **Finite-`m` Gram geometry.** `K` near-random directions in `R^m` have Gram
>   off-diagonals of order `1/sqrt(m)`; at `m = 35` that is `0.169`, and the
>   measured values are `0.126` and `0.132` for two groups against `0.640` for a
>   group whose offsets share a common component (`RT-20260804-0ff29a` OBJ-10).
>   Matching `K` between arms equalises this floor **only when the Jacobian
>   directions are equally generic**, which is exactly what fails for a candidate
>   group built as `delta_k = s - c_k` with `c_k` iid — all such offsets share
>   `s`, at measured mean pairwise cosine `+0.5562` against the predicted
>   `||s||^2/(||s||^2 + E||c||^2) = 0.5643`.
> - **Finite-`D` estimator bias**, documented in "How to run obligation 4" below.
>
> So the same `m`-dimensional noise operates in **both** regimes, by **different
> mechanisms**: through *rank truncation* at `K > m`, and through *channel
> composition and Gram geometry* at `K <= m`. Stating only the first is what let
> that batch treat its matched-`K` comparisons as clean.

The null reproduced the `K = 512` uniform cell to **0.8%**. A rule that fires on
the null is not discriminating, whatever its branch count.

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

Two cheap sub-checks, both prospective, and **they are not interchangeable**:

1. **The archive check.** List every archived measurement of the same statistic
   and verify at least one named outcome is consistent with all of them. In case A
   the list was `17.078, 1.0371, 5.4349, 0.1058, 6.19e-15`; reading it would have
   shown both named outcomes were already excluded. Reading time, zero compute.
   **This check is unavailable when the statistic is new to the batch**, which was
   the case in case B — say so rather than claiming both.
2. **The null-first check.** Emit the frozen rule's verdict on the null arm before
   looking at the real arm. Case B would have been caught in one line.

*A note on what catching case B would and would not have bought.* It would have
caught the non-discriminating verdict, and cleanly. It would **not** have saved
that batch, because the defect that mattered was upstream — the null removed a
property of the candidate set rather than of the family (mode 3, second worked
case) — and that is an obligation-1 and obligation-4 failure that obligation 5
adds nothing to (`RT-20260804-0ff29a` OBJ-9). Two consecutive versions of this
entry have now fixed the previous batch's failure and missed the current one.
That pattern is itself worth recording, and this entry does not claim to have
broken it.

### Mode 5 - the comparator that is wider than the effect, read at n = 2 (caught by replicating the COMPARATOR)

**This is the mode the present entry adds.** Every arm is sound, obligations 1-5
are met, the null is admissible, the rule discriminates, the real arm sits below
the null arm — and the ensemble the null arm is drawn from has never been drawn
more than once or twice, so nobody knows how wide it is.

*Worked case.* Two independent reviewers of the same batch each constructed a
family-ablated null, each found the real family sitting a few percent below it,
and each recorded a residual: **4-9%** (`VAL-20260804-264ab9` DEF-1, from
`real / CTRL-BOTHRAND` = 0.956, 0.927, 0.912 on three groups) and **3-11%**
(`RT-20260804-0ff29a`). Both looked for a way to ablate the residual away and
neither found one, and the campaign's own decision record recorded it as the only
quantity in five batches to survive its own reviewers (`DEC-20260804-485fa6`,
`what_survives`). One reviewer then did the thing that matters and drew its
synthetic ensemble a **second** time: the two draws returned **0.4503 and 0.5039**
on the group carrying the headline, against a real value of **0.4149** — a
comparator spread *larger than the real-versus-synthetic gap in one of the two
draws*. At `n = 2` the residual was not resolved in either direction, and saying
so was the correct reading (`EV-MLKEM-d777f0`, `what_is_not_established`).

**The general shape.** A single draw of a stochastic comparator is a point
estimate with an unknown standard error. A residual read against it inherits that
unknown. This is *not* mode 1 (the comparator can fail), *not* mode 3 (the
contrast is not forced) and *not* mode 4 (the rule discriminates). It is a
sample-size failure in the **denominator arm**, and it is invisible because the
denominator arm looks like a fixed reference rather than a measurement.

**The rule.** If your comparator is generated — random directions, resampled
entries, a synthetic ensemble, a permutation family — then **it is a measurement
and it needs a sample size.** Draw it at least 8 times before reading any
residual against it, and report the **interval**, not the point. Where the
comparator is a closed-form or kernel evaluation this is usually the cheapest
line item in the batch: in the worked case, 16 draws cost about 4.5 minutes of
numpy with no scoring, no sieve, and no lattice library.

**And derive your own rule's false-positive rate before you run it.** If the rule
is "outside the ensemble's `[min, max]`", then applying it leave-one-out to the
ensemble's own `n` members must return OUTSIDE for **exactly 2 of `n`** —
**exactly one LOW and exactly one HIGH** — whenever the draws are pairwise
distinct, by the definition of a min/max interval. That number is derivable in
one line before the run, it is mechanically checkable after it, and it is the
honest per-group false-positive rate to quote beside any OUTSIDE verdict. In the
worked case it was derived in advance, observed as exactly `1 LOW / 14 INSIDE /
1 HIGH` on all five groups, and the corresponding rate — `2/16 = 12.5%` for
OUTSIDE in either direction, `1/16 = 6.25%` for OUTSIDE_LOW — was reported beside
the verdicts (`TASK-20260805-74a8e9`).

**Two cautions on that rate, both of which apply in the worked case.** First, an
`n`-draw min/max interval is a *tolerance* interval, not a confidence interval,
and its coverage is a property of `n` alone. Second, **groups measured against
the same ensemble draws are not independent**, so per-group rates must not be
multiplied into a joint p-value. Report the per-group rate and the pattern across
groups, and leave the inference to the reader.

*Catch.* Not obligations 1-5. Count the draws of the comparator.

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
   **Hold the candidate set, the sample size and the row norms FIXED while you do
   it** — that is the correction mode 3's second worked case forces, and it is
   what turned a reported factor of 2 into 1.10.
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

**A second caution, on the denominator, and it has now cost two Coordinator
commit messages.** A ratio is not restated without naming its denominator in the
same sentence. A campaign reported "0.44x against 0.22x" as a 2:1 spread between
two families; the numerators were `13.306` and `13.532` — the second family's raw
statistic is *higher*, i.e. marginally *less* departed — and the entire factor of
2 lived in a permutation comparator that returned `61.92` effective candidates out
of `25` on one arm and `29.98` on the other. Against nominal `K` the two families
are `0.532` and `0.541`: indistinguishable (`VAL-20260804-264ab9` DEF-2,
`RT-20260804-0ff29a` OBJ-5, `DEC-20260804-485fa6` CE-2). **A comparator that
reports more independent candidates than there are candidates is not calibrated on
that arm**; flag it mechanically when `comparator/K > 1.2`.

**A third caution, discovered while writing up mode 5's worked case and recorded
because it is one keystroke from a published error.** When the statistic can be
**negative**, a relative difference `real/comparator - 1` **inverts the direction
of the reading**: with `real = -0.2752` against `comparator = -0.2640`, that
expression returns `+4.24%` while the real value is *smaller* than the
comparator's. **Report the signed absolute difference for any statistic not
bounded away from zero**, and reserve ratios for statistics that are.

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
entry `KN-TECH-9d21c4` tabulated these as **7.13x** and **9.39x**, which are
`1/0.140324` and `1/0.106552` — i.e. computed against **1.0**, in the same passage
that argues 1.0 is the wrong reference and that using it is a 3.5% error. The
corrected factors are above. The direction is unchanged; the magnitude was
overstated.

**Priority, corrected.** `KN-TECH-9d21c4` stated this shortfall had never been
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
error standard deviation. This reproduces the measured surrogate value to **0.6%**
pooled over nine archived instances (max 1.1%), and to 1.2% and 3.5% on two
further vector families at 1.2x and 2.2x the norm scale — so it is a prediction,
not a fit. Two independent reviewers re-derived it before reading the producer's
version and obtained it term for term.

*Generalisation, in both directions.* **Ask which property of the real object
causes the departure from your reference model, then check whether your null
preserves that property. If it does, the null is decorative — and if it DELETES
that property, the null is decorative in the mirror-image way and the contrast is
about the deletion.**

## What the technique does not claim

- It does not say a forced contrast is *false*. The measurements in the worked
  cases are sound, reproduced independently, and in several cases stronger than
  originally claimed. They are simply not about the question.
- It does not license closing a lane. A null shown inadmissible removes one
  comparison, not the question behind it; per `docs/inventor-protocol.md`, a
  negative reading carries the same burden as a positive one. Premature closure is
  a failure mode symmetric with overclaiming.
- Obligations 4 and 5, and mode 5's comparator replication, are not new claim
  tiers and passing them asserts nothing. They are falsification aids, and a
  failed obligation is frequently the useful result.
- The derivations quoted here are first order unless stated otherwise. They
  identify a dominant mechanism; they do not account for every residual, and the
  closed form above degrades as the expansion parameter grows (3.5% at 2.2x norm
  scale, from 0.6%).
- **This entry does not claim the check would have saved any batch.** The
  supportable statement is narrower and is the only one made here: **the check is
  cheap, it is cheapest on the day the statistic is chosen, and it has caught
  defects prospectively** — three of them in one batch, before any measurement
  run, in the producer's own design.
- **Mode 5's worked case is an executor observation that has not been through
  review.** The 16-draw replication described there was run by
  `TASK-20260805-74a8e9` and its outcome is recorded in that task's artifacts. It
  is cited here only for the *method* — replicate the comparator, derive the
  rule's false-positive rate — and this entry asserts nothing about whether any
  residual in that campaign is real. That judgement belongs to a Reviewer and to
  the Coordinator, and AGENTS.md rule 12 is UNMET.
- **No ML-KEM claim of any kind.** No break, no security proof, no FIPS 203
  parameter set affected or cleared, no speedup, no cost claim, no exponent
  moved. Every worked case above is toy scale.

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
  sensitivity_monotone:      # >=3 interior points. Two ends do not give a SIGN.
  comparator_spread_nonzero: # if zero, the statistic is a constant. Mode 1.
  comparator_n_draws:        # >= 8 if the comparator is GENERATED. Mode 5.
  comparator_interval:       # report the interval, never a single draw
  comparator_over_K:         # flag if comparator/K > 1.2: not calibrated on that arm
  maximal_removal_control:   # total removal must be at least as extreme as
                             # partial, and on the same side. If not, mode 2.
  forced_value_derivation:   # what the contrast MUST be under the alternative
  forced_value_number:       # the actual number, before the run
  forced_value_regime:       # WHERE the derivation binds. A bound that holds only
                             # for K > m says nothing about a headline at K <= m.
  null_deletes_causal_property: # mirror of the decorative null. Mode 3, case 2.
  reference_model_value:     # what the assumption under test predicts
  reference_is_finite_sample: # asymptotic value != estimator's null at finite D
  both_arms_vs_reference:    # where BOTH arms sit against it
  ratio_denominator_named:   # in the same sentence. Signed diff if the statistic
                             # can be negative: real/comp - 1 INVERTS then.
  can_this_null_fail:        # if no, it is not a null
decision_rule:
  outcomes:                  # every label the rule can emit
  exhaustive_over_statistic: # the case split, written out
  exhaustive_over_MECHANISMS: # object vs apparatus vs sample size vs noise dim
  verdict_on_the_null_arm:   # RUN IT FIRST. Same label as the real arm => mode 4
  rule_false_positive_rate:  # DERIVE it before the run; check it after. Mode 5.
  groups_are_not_independent: # do not multiply per-group rates into a p-value
  neither_branch:            # required if exhaustiveness cannot be argued
  action_in_neither_branch:  # declared before the run
```

The lines that do the work are `object_preserved`, `forced_value_derivation`,
`forced_value_regime`, `comparator_spread_nonzero`, `comparator_n_draws` and
`verdict_on_the_null_arm`. Everything else is bookkeeping around them.
