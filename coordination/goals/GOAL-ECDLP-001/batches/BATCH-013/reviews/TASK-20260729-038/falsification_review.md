# RT-20260729-031 — falsification review of the committed EXP-YIELD-003 package

**Task:** TASK-20260729-038 · **Goal/batch:** GOAL-ECDLP-001 / BATCH-013 ·
**Role:** red-team, independent session · **Archived by:** TASK-20260729-039

**Bound snapshot verified against Git in the assigned worktree** (HEAD
`2c6b11f3`, branch `claude/ecdlp-b011`, clean tree): run package at
`6921e716`, parent `572ce080`, eleven committed paths; frozen contract at
`de6fbb75`, not present in the run commit; approval receipt at `99dec70d`.
Every figure quoted below was read from a committed blob.

**Verdict: PASS WITH BLOCKING CONSTRAINTS ON THE DECISION.** The run package is
admissible and needs no repair. Four objections are blocking on
`DEC-20260729-003` and `EV-ECDLP-010`; none is blocking on the eleven artifacts,
and none of them may be edited.

---

## 1. The narrowest true statement the package licenses

Under the frozen `EXP-YIELD-003` contract at `de6fbb75`, on one macOS arm64
host, a curve-free balls-in-bins re-execution of the `EXP-YIELD-002`
repaired-null arm at the same 48 declared parameter tuples, under the fresh
disjoint master seed 130301 and the C-14 replicate schedule, produced a
48-tuple `z_sem` mean of 0.3336976784 with sample sd 0.8915705400 and standard
error 0.1286871228, with all 48 tuples measured, no invalidation rule fired,
the DEV-4 seed-string defect repaired and verified before any draw, and the
recorded computation reproducing bit-identically on re-execution and under two
further interpreter builds carrying numpy 2.4.0 and 2.4.4; the committed
`EXP-YIELD-002` arm under master seed 120201 produced 0.3610236850 with sd
0.9750016842; the two draws are independent in their Monte Carlo noise, share
every deterministic component by construction, and differ by 0.0273 against a
difference standard error of 0.1907. **That is all.** It licenses no statement
about decomposition yield, none about `P_pred`, none about the balls-in-bins
process, no locus for the shift, and no claim that any deterministic offset
exists.

**It is narrower than the batch's own framing in two places**, both outside the
run package: the commit subject line of `6921e716`, which asserts the shift
*replicates*; and the `-036` receipt key `PP_1_EXCLUDES_THE_BUILD_…` with its
`consequence` field.

---

## 2. The ruling: what the replicated shift is

### 2.1 The case for a real deterministic offset, at full strength

Two draws under disjoint master seeds both land about 2.2 design standard
errors above the expectation the committed package itself declares. The
BATCH-012 validator's 400-repetition Monte Carlo put the first at
P = 0.0100 ± 0.0050. The declared second-order biases account for at most
0.0895 SEM and realised 0.02638 SEM on average — an order of magnitude short.
PP-1 removes the interpreter build and the numpy version from the candidate
list. On those facts a fixed additive component is the natural reading, and if
it existed it would be a term nobody in this lineage has derived.

### 2.2 The case against, and it wins, on four independent grounds

**(a) The agreement argument is empty.** The `-036` receipt says *"A FIXED
OFFSET predicts the two agree within their combined error, which they do at
0.14 SE."* So does the chance hypothesis. Two draws of the same statistic agree
within their combined error with the *same* probability under both hypotheses.
The likelihood ratio contributed by the difference of the two means is ≈ 1.
**Agreement is not evidence here.** All the evidential content is in the
*level*, and the level is one fresh one-sided excursion at about p = 0.017.

**(b) The first observation is selected and cannot be compounded with the
second as if it were not.** The contract records in its own text that the
statistic was a *post-hoc tail-check observation* of `EXP-YIELD-002`, outside
all four of that contract's criteria. It was noticed because it was extreme,
from a menu that also held the `z_sd` mean, `n_neg`, three tail counts, the
maximum, the per-arity means and the `delta_z` vector. Multiplying 0.010 by
0.017 and reporting 1.7e-4 treats a selected statistic as if it had been named
in advance.

**(c) The mathematics cannot host a term of this size — and that is a
derivation, not an opinion.** For P-REPAIRED the exact mean

```
M = E[distinct] = N - (1 - s/N) [ (N-1)(1-2/N)^(C_red/2) + (1-1/N)^(C_red/2) ]
```

is a theorem, re-derived three times in this lineage and undisputed. Then

```
E[z_sem] = (M - P_pred) * E[1/sem_rep]  +  E[ (mu_rep - M) / sem_rep ]
```

The first term is bounded by the package's own declared envelope: at most
0.0801 in SEM units at any of the 48 tuples and 0.0262 on average, with the
Jensen factor `E[1/sem_rep] * sigma_sem` at most `1 + 3/(4 n_rep) ≤ 1.0083`
here. The second is the classical skewness bias of the one-sample *t*
statistic, `-gamma_1 / (2 sqrt(n_rep)) + O(1/n_rep)`; the distinct-bin count is
left-skewed at these parameters, so the term is **positive**, and it is at most
0.088 at the most extreme tuple (T-18-2-B34) and 0.012 averaged over the 48.
**Total expectation of order +0.04. There is no third analytic term available
to carry +0.30.** This reproduces, independently and at greater generality, the
finding `RT-20260729-021` recorded at RT21-6.

**(d) The only remaining locus — a shared code defect — is excluded by the
package's own high-precision block, freshly and at ten tuples.** A defect
producing a *fixed offset in bins* scales in SEM units as `sqrt(n_rep)/sd`, so
an offset large enough to give ≈ +0.31 SEM at the primary schedule must give
between **+2.5 and +5.6 SEM at 10,000 replicates** at the ten block tuples.
PDC-9 expressly preserves that quantity as recomputable from OM-8 and OM-9, and
it is **not** the prohibited repaired-minus-as-recorded difference column.
Recomputed from the committed HIGHPREC results, the repaired leg's deviation
from the exact analytic mean in SEM units is

```
0.501  -0.393  -0.686   1.305   1.224  -0.682  -0.723   0.781   0.096   1.829
```

mean 0.325, sd 0.941, ten values — none within reach of what a bins-level
offset requires. `RT-20260729-021` ran this control on the committed
`EXP-YIELD-002` block; **this batch reproduced it on a block that is no longer
a deliberately selected all-`m = 3` subset, with DEV-4 repaired and the legs
independently seeded, and nobody read it.**

### 2.3 The ruling

**It is not established as anything.** On the committed record it is a second
upper-tail draw of a statistic whose null the program has now calibrated twice,
and no locus for a deterministic component survives inspection. The correct
disposition is `inconclusive` on the mechanism and **closed** on the chase — and
the reason it is closed is *not* that the stopping rule says so, but that there
is nothing left to look for.

**Mathematics, code, or undetermined?** The two limbs are **not symmetric**, and
I decline the symmetric answer. The *mathematics* limb is **closed by
derivation**: the exact mean is known in closed form and the only other
`O(n^-1/2)` term is computable and bounded. The *code* limb is closed
**empirically** by the package's own ten-tuple, 10,000-replicate block for any
defect of the fixed-bins-offset kind — which is the only kind a defect shared by
two separately written drivers could plausibly be. What is **not** closed on the
committed record is a defect *proportional to* `sem_rep`, i.e. one producing the
same offset in SEM units at 100 and at 10,000 replicates. No such defect has
been named and I do not propose one; I record it because naming the residue is
the job.

**The single control that would separate them** is **RC-38-A**: K independent
master seeds through the same driver under the same seed-derivation rule,
reporting the empirical distribution of the 48-tuple `z_sem` mean. It cannot
come out ambiguous. Centre ≈ +0.03 with sd ≈ 0.147 → the two values are draws at
p ≈ 0.008 and p ≈ 0.017 and the residue closes. Centre ≳ +0.20 → the offset is
located in the driver-plus-seed-rule combination. It is curve-free; the
package's own timing (26.3 s for all three arms, 61 MB peak) puts K = 120 at a
few minutes.

---

## 3. The sentences that may and may not now be written

### May be written

- *"Under fresh disjoint master seed 130301 the 48-tuple `z_sem` mean was
  0.3336976784, sd 0.8915705400, standard error 0.1286871228, over the same 48
  declared tuples, with all 48 measured and no invalidation rule fired."*
- *"The two realised values differ by 0.0273 against a difference standard error
  of 0.1907; the difference statistic does not discriminate between a fixed
  offset and chance, and the discriminating quantity is the level."*
- *"The committed `z_sem` vector is bit-identical under CPython 3.13.1 with
  numpy 2.4.0, CPython 3.13.3 with numpy 2.4.4 and CPython 3.14.3 with numpy
  2.4.4, so no difference among those three build-and-library combinations
  contributes to the observed value."*
- *"The repaired null lands **at or slightly above** `P_pred`."*
- *"No locus for a deterministic component has been identified; none is
  asserted; the lineage is closed."*
- *"The DEV-4 seed-string defect is repaired in `EXP-YIELD-003` and verified
  before any draw at all ten block tuples; it is repaired in nothing else."*
- *"This contract is not threshold-free: it carries a real three-way disposition
  rule."*

### May **not** be written

- ✗ *"The shift is a property of the recorded driver, build and platform."*
  (RT31-1 — this is the queue's widened branch 2, and its `build` limb is
  contradicted inside this batch.)
- ✗ *"The z_sem shift replicates."* as a disposition. (RT31-2.)
- ✗ *"The interpreter build and the numpy version are excluded as sources of the
  shift."* (RT31-3 — invariance across three tested combinations is not
  exclusion of a property shared by all of them.)
- ✗ *"A fixed offset predicts exactly that agreement."* as support for a fixed
  offset. (RT31-4.)
- ✗ *"Eight deviations were declared."* (RT31-5 — five distinct identifiers
  across nine per-arm entries.)
- ✗ *"Better than 3.2e-5 at every one of the ten block tuples."* unaccompanied.
  (RT31-6 — the realised maximum is 3.230158e-05.)
- ✗ *"The repaired null lands **on** `P_pred`."* — the binding sentence stands.
- ✗ Any high-precision difference column quoted as a confirmation **or** a
  disconfirmation of `T`.
- ✗ *"A fresh-platform replication."*
- ✗ Anything about decomposition yield, any `E` or yield ratio, any re-disposal
  of INV-4, any determination of INV-5, any hypothesis movement, any cost-model
  consequence, any closure quorum.

---

## 4. The platform framing — attacked first and hardest

The platform **did not change**, and the package says so plainly in every
manifest, in `results.json`, at BND-3 and BND-4, and in both receipts. A run
that changed only the seed separates **chance** from a **seed-independent
deterministic property of the driver-build-platform combination**, and separates
none of those three from each other. The package states exactly that and does
not overstate it.

What the batch *did* obtain is more than the pre-run expectation: the primary
arms ran on 3.14.3/2.4.4 and PP-1 recovered both the exact committed reference
environment (3.13.1/2.4.0) and 3.13.3/2.4.4, **bit-identically**. That is a real
result about determinism of the recorded pipeline across builds. It is **not**
portability, **not** cross-version determinism as a general claim, and **not** a
separation of driver from build — PDC-8 says so and the package observes it.

**Where the batch overstates:** the `-036` receipt's `consequence` field and its
key name assert that the build and the numpy version are *excluded as sources of
the shift*. Invariance across the tested set excludes *variation among those
builds*. It does not exclude a property **shared** by all of them — a behaviour
of PCG64 or of `Generator.choice` common to numpy 2.4.0 and 2.4.4 — and a shared
property is precisely the shape a "numpy build" hypothesis must take to explain
an offset that reproduces under fresh seeds. The control for *that* is a
different **bit generator** (RC-38-B), not a different build. PP-1 is repeatedly
mistaken for it.

---

## 5. The resume condition — attacked

**Neither branch was re-read against the realised number, and the unassigned
interval was handled honestly.** The contract names the two unassigned regions
before data at
`resume_condition…the_unassigned_region_is_named_and_is_recorded_as_inconclusive`
and at BND-5, fixes their disposition as **inconclusive on the shift**, and
forbids assimilation to the nearer branch. The realised 0.3337 does not land
there, so the clause was not exercised — but it was correctly pre-committed, and
the honest handling is on the record before the number existed. Under PDC-14's
recorded unit convention the value is above +0.25 in `z_sem` units and selects
branch 2. **That is arithmetic.**

**But one branch *was* widened, before the outcome, in the opening commit.**
`DEC-20260729-002` NA-1 reads: *"the driver, the numpy build and the platform
**become the objects of the next control**."* The BATCH-013 queue restates the
same branch as: *"**the terminal finding is that the shift is a property of** the
recorded driver, build and platform."* Those are different statements — one
names the objects of a future control, the other asserts a positive attribution
as a terminal finding.

The widening is now **unwritable**. Its `build` limb is contradicted by PP-1
inside this batch; its `driver` limb is unsupported and is in fact contradicted
by the high-precision block; its `platform` limb was never tested and BND-3
forbids claiming it. And its disjunction — chance or driver-build-platform —
**omits the option the evidence supports**: an upper-tail draw of a
correctly-calibrated null.

The queue's own feasibility table §4.1 puts P(branch 2) at ≈ 0.044 under a
centred replication (≈ 0.06 under the package's own declared centre of ≈ +0.03,
which §4.1 does not use). **A branch that fires about one time in twenty under
the null cannot carry a terminal positive attribution.** `DEC-20260729-003` must
record branch 2 in NA-1's own words and no stronger.

I note and endorse the design point: the contract has **no success and no
falsification criterion** by design, that is legitimate, it is a *calibration
protocol* — acceptance limits on the instrument, all seven IV rules shown able
to fire, none on the measurand — and **it is not threshold-free**. No record may
call it so.

---

## 6. The stopping rule — assessed, and accepted with one dissent

`RULE-BATCH013-SCOPE` closes this lineage to further replication or
control-on-a-control batches regardless of outcome, reserving exactly one item —
`DEFER-BATCH013-001`, RT21-3's structurally exact pre-marking arm — as able to
justify a batch, and only as its primary subject.

**My finding implies more instrument work, and I say so plainly: it does not
clear that bar.** RC-38-A and RC-38-B are controls-on-a-control. I name them,
cost them, give them resume conditions, and **do not request them as a batch**.

**I accept the foreclosure, and the acceptance is reasoned, not compliant.** I
would not accept it if the question were open. It is not open: the exact process
mean is a theorem, the residual expectation is bounded above by ≈ 0.04 by a
derivation any session can re-run, and the package's own ten-tuple
10,000-replicate block excludes a fixed bins-level offset by a factor of three
to seventeen. RC-38-A would convert a one-sided p ≈ 0.017 residue into a
measured exceedance probability — worth minutes of compute, **not** worth this
lineage's last batch. The alternative use of that batch,
`DEFER-BATCH009-001`'s `EXP-STR-004` replication, is the only carried obligation
that can move the goal's sole active hypothesis and is worth more by any ranking
this program has recorded.

**One dissent, from the rule's reasoning and not its conclusion:** the rule
justifies closure by *fiat*, and closure is in fact justified by *evidence*.
Those are different. A rule that would have closed the question equally firmly
had the evidence pointed the other way is not the reason the question is closed.

**If RC-38-A is ever run, it belongs as a subordinate calibration arm of the
`DEFER-BATCH013-001` batch — never as the primary subject of a batch of its
own.**

**No lane is declared dead.** Absence of a located mechanism is not
impossibility: RT31-3's residue (a property shared by every tested numpy
version) and the `sem_rep`-proportional residue are **unexcluded**, not
excluded.

---

## 7. What this licenses about O-4 component (d) — **orthogonal**

The substitution the repair makes — a uniformly random `s`-subset for the
structurally exact pre-marked set — has an **exactly computable** effect on the
process mean. Writing `A = (1-2/N)^(C_red/2)` and `C = (1-1/N)^(C_red/2)`:

- at `m = 2`, where the structurally exact set is `{bin 0}`, the structurally
  exact mean **exceeds** the uniform-subset mean by `((N-1)/N)(C - A)`;
- at `m = 3`, where it is `B/2` whole antipodal pairs, it **falls short** by
  `(B/N)(C - A)`.

Evaluated at the 48 declared tuples in SEM units: `m = 2` runs from **+0.00527
to +0.08605**, mean **+0.02974**; `m = 3` runs from **−0.000435 to
−0.00000073**, mean **−0.0000769**. The overall maximum is **0.08605** at
T-12-2-B46 — confirming the committed **0.0895 SEM** envelope as *correct and
tight* — and the overall mean is **+0.01794**.

**Two consequences.** First, **component (d) cannot explain the shift**: it
contributes at most 0.086 SEM at any single tuple and 0.018 SEM to the 48-tuple
mean, an order of magnitude short of +0.30, and at `m = 3` it has the **wrong
sign**. The two questions do not touch. Second, and more usefully, **the
mean-level content of `DEFER-BATCH013-001` is settled by the two expressions
above and by no experiment.** A 10⁴-replicate two-leg run over 48 tuples buys a
Monte Carlo estimate of a number already available in closed form.

**What this does not settle,** stated so the ruling is not overread: the
arithmetic settles the gap between *two specified pre-marking rules inside the
simulation*. It does **not** settle O-4 (d)'s **census-facing** claim — that the
correct null pre-marks the bins a cancelling multiset reaches deterministically
— which is a modelling claim about the census, remains untouched and unarchived
exactly as the queue records. Nor does it settle the **second moment**, on which
C-13 makes no claim; but that effect is of the same `O(s/N)` scale, with `s/N ≤
0.0055` across the declared set.

**Recommendation (RC-38-C):** if `DEFER-BATCH013-001` is dispatched, replace its
mean-level arm with a derivation note plus a two-tuple numerical confirmation,
and spend its compute on the second moment and the census-facing question.

---

## 8. AMB-2 — **right call, wrong authority. Ratify it.**

The contract *mandates*, in `tail_checks` and OM-6, the counts of `|z_sem|`
above 1, 2 and 3 and the count `n_neg`. Each is literally a threshold on a
quantity derived from OM-1 or OM-3, which IV-6 read literally forbids. PDC-1
scopes IV-6 away from IV-1/IV-3's tolerances but names only IV-1, KA-8, KA-3,
KA-4 and KA-6 — it does not reach these clauses. The Executor read the mandated
reporting thresholds as required execution and **flagged rather than applied
silently**.

**The reading is right, on three grounds.** (i) IV-6 read literally is
*self-invalidating*: it forbids the contract's own metrics section, since OM-6 is
*defined* as a count over a strict inequality — no execution could satisfy both,
and a rule no execution can satisfy is not the rule. (ii) PDC-1's *structure*
transfers a fortiori to a clause of identical shape. (iii) The contract states
of these counts that no test is performed, nothing fires and no p-value is
computed, so no criterion is created; and refusing to compute them would breach
`tail_checks` and OM-6 outright.

**The authority is wrong**, and the PDC binding statement says so in its own
words, citing D-2: *a condition recorded after the fact is not a condition*.
AMB-2 is an Executor-adopted extension of a pre-dispatch condition, recorded
after dispatch. Declaring it was exactly the ST-3 discipline that found DEV-4 —
but it carries no pre-dispatch authority and must be **ratified by the
Coordinator in `DEC-20260729-003`**, not left standing as an Executor reading.

**Blast radius confirmed.** OM-5 is a mean, an sd and a standard error and
applies no threshold. I independently recount from the committed sorted vector:
`|z_sem| > 1` is 12 (3 negative, 9 positive), `> 2` is 3, `> 3` is 0; `n_neg` is
16 with `n_pos` 32. Every figure reproduces, and every one is reported with its
member tuples named — PRED-ID EXTENDED correctly applied.

---

## 9. PDC-15 — **quoted-figure imprecision, not a violation**

Recomputed independently at 50-digit precision at all ten block tuples, the
exact expectation of the difference,
`(|S_(m-2)|/N)[(N-1)(1-2/N)^(C_red/2) + (1-1/N)^(C_red/2)]`, differs from the
quoted `T` by at most **3.230158e-05** at **T-12-2-B62**; the next largest is
7.358e-06 at T-14-2-B118 and the remaining eight are ≤ 1.939e-06. The Executor's
realised figure 3.2302e-05 is **correct**.

`"better than 3.2e-5"` is therefore **false as stated**. `"better than 3.24e-5"`
or `"better than 1e-4"` is true. **The run violated nothing**: it computed the
mandated quantity, reported it, carried the condition text verbatim beside the
per-tuple numbers, altered nothing, and handed the exceedance to the reviewers.
The defective object is the *condition*, whose numeral was hand-derived by the
pre-execution reviewer and truncated downward instead of rounded upward.
PDC-15's **substance is correct and unaffected**: the agreement is arithmetic,
not evidence, and the symmetric prohibition stands.

**But it is the RT21-1 genus again** — a hand-derived numeral, frozen into an
immutable governing text, surviving an independent review, and false. That is
the third distinct occurrence of that pattern after C-20 and after the
feasibility table's rank-4 sentence. Supersede it explicitly; never quote it
unaccompanied.

---

## 10. The fifth cardinality-not-identity instance

**Found, and it is in the bound snapshot receipt and in an immutable commit
message.**

The `-036` receipt states `"deviations": {"count": 8, …}` and the commit message
states *"Eight deviations declared with effect sizes."* Neither names a member.
The committed package carries **five** distinct declared deviation identifiers —
`DEV-1, DEV-5, DEV-6, DEV-7, DEV-8` — across **nine** per-arm entries
(REPLICATE-REPAIRED 5, KNOWNANSWER 2, HIGHPREC 2). A repository-wide enumeration
over `experiments/EXP-YIELD-003` returns `DEV-1, DEV-4, DEV-5, DEV-6, DEV-7,
DEV-8`, and **DEV-4 is the carried-and-repaired `EXP-YIELD-002` contract defect,
not a deviation of this run**. `DEV-2` and `DEV-3` appear nowhere. So **8 matches
neither 5, nor 9, nor 6.** The likeliest origin is 5 deviations plus the 3
declared ambiguities AMB-1/2/3 — two different sets pooled into one numeral,
which is exactly the D-2 shape.

PRED-ID EXTENDED was written into this contract *specifically* to stop this, and
it binds "every record derived from it". The count survived the Executor, the
archiving session and the commit message, and is now immutable in two places.
**The recurrence, not the magnitude, is the finding.**

A second candidate of the same family, recorded but ranked below it: RT31-4's
*"a fixed offset predicts exactly that agreement"* is a match cited as
confirmation when the match is equally probable under the alternative — the
continuous-variable form of PC-2's *"eleven predicted, eleven occurred, only
five the same cells."*

---

## 11. Scope — the A1 admission holds

Curve-free simulation of an occupancy null; claim tier **toy**; four toy prime
fields with group orders 4001, 16619, 65633, 261707; one prime-order curve per
size in the source package; a **single unreplicated source run set** that is a
size series and not a replication. **Not a fresh-platform replication**, and
every artifact says so. Nothing quotable as target-class, as an exponent result,
as an attack or attack improvement, as a cryptanalytic result, as a closure or
as an impossibility claim. **No cost model touched** — every occurrence of
`efficiency E`, `yield ratio`, `0.85`, `INV-4` and `INV-5` in the package sits
inside a prohibition or a statement of non-action. **INV-4 not un-fired and not
re-disposed; INV-5 declared neither way.** No hypothesis moves. No completion
criterion met or approached; no closure quorum claimed or claimable
(INT-BATCH013-D).

**Standing prohibitions verified clean in the package:** no record says the
repaired null lands *on* `P_pred` (every occurrence of the phrase is inside the
prohibition); the C-20 power sentence is not reproduced anywhere in the package
or the receipts, its only occurrence in the batch being inside the RT21-1
carried-defect block which carries the correction; the `EXP-YIELD-002`
high-precision difference column is nowhere quoted as a confirmation of `T`.

**The two ceiling exceptions are RT31-2 and RT31-3 — both in the commit message
and the receipt, neither in the run package.**

---

## 12. Refutation-artifact ordering

1. **Counterexample certificate — NOT APPLICABLE**, and recorded as not
   applicable rather than as satisfied. There is no universally quantified
   proposition to exhibit a witness against; a replication is a measurement.
2. **Derivation note — AVAILABLE, and this is what the ordering rule exists to
   surface.** Against the proposition *"a third analytic term of size +0.30 SEM
   exists"*, a derivation note is available and is **strictly stronger** than the
   empirical basis the batch declares. Its content is §2.2(c). It is not a
   product of this run and is not archived; it is derivable from the committed
   package plus standard results, in one session, with no compute.
3. **Declared `empirical_only` — CORRECT for what the run itself adds**, and
   `EV-ECDLP-010` should declare it so, as BND-6 and INT-BATCH013-I anticipate.

**The undeclared basis would be the failure.** If `DEC-20260729-003` rests on
"no third analytic term exists", its basis is a **derivation note**, must be
declared as one, and must be archived before the decision that relies on it.
Resting that on `empirical_only` when a derivation is available is the
undeclared-basis failure. The absence of a proof is not the failure; the
misdeclaration is.

---

## 13. Cheapest discriminating control, and the mutation already inside the snapshot

**The mutation is free and it is already committed.** The high-precision block's
**repaired leg measured against the exact analytic mean in standard-error
units** — the quantity PDC-9 expressly preserves, and *not* the prohibited
difference column — is decisive against the bins-level-offset reading (§2.2(d)),
at ten tuples including six `m = 2` tuples, with independent legs. Nobody read
it against this question.

**The cheapest control not yet on the record is RC-38-A** (K master seeds, same
driver, same seed rule; curve-free; minutes). It is foreclosed by
`RULE-BATCH013-SCOPE` and I accept the foreclosure (§6).

---

## 14. Unarchived probes — **NOT EVIDENCE**

Run outside the repository; no conclusion here rests on them; every conclusion
is *also* supported by the derivation note and by the committed high-precision
block, both available without running anything.

- Exact 50-digit recomputation of `M` and `(M − P_pred)/sem_rep` at all 48
  tuples from the committed `results.json`, and of the occupancy skewness from
  exact factorial moments.
- An independent from-scratch re-implementation of P-REPAIRED written from the
  frozen contract's prose, run at all 48 tuples over 120 fresh master seeds
  under the contract's own SHA-256 seed rule.
- The same re-implementation seeded with master 130301, which reproduced the
  committed 48-tuple `z_sem` vector and its mean **bit-identically at all 48
  tuples** — an independent verification of the committed driver that nobody
  asked for, recorded as a probe and not as a result.
- Exact evaluation of §7's two closed forms and of PDC-15's exact difference
  expectation at the ten block tuples.

They are named rather than omitted because they shaped the ruling and a reader
is entitled to know it, and because **RC-38-A exists precisely so the
load-bearing one can be put on the record properly** if the program ever decides
it is worth the minutes.

**Zero curve compute was performed by this session, inside the repository or
outside it. No commit was made. Nothing outside the declared write scope was
written. The frozen specification was read and not edited.**

---

## 15. Not reached inside the cap

- `EV-ECDLP-009` and `DEC-20260729-002` were read at the cited fields (O-6, the
  NA-1 resume condition verbatim, the unexplained-and-unreplicated statement) and
  **not in full**. Nothing here turns on an unread field of either.
- The BATCH-012 reviews were read at NARROW-1..7 as carried in the queue and at
  RT21-6 in full; the remaining RT21 objections and the recount note were not
  read in full.
- The KNOWNANSWER arm's eight cases were verified as reported-and-not-fired from
  the committed artifacts; their per-case arithmetic was not individually
  re-derived (KA-3's target is the same closed form re-derived here at the 48
  tuples, so the family is not unchecked).
- RC-38-A was executed only as an unarchived probe at K = 120 outside the
  repository, and is named as a required control **precisely because it is not on
  the record**.

---

## 16. Next concrete action

Draft `DEC-20260729-003` as **`inconclusive`** on the shift's mechanism and
**closed** on the chase, carrying RC-38-D's four supersessions verbatim, and in
the same decision replace the queue's branch-2 terminal-finding sentence with
NA-1's own words. In one line, write:

> The replicated 48-tuple `z_sem` mean of 0.3336976784 is an upper-tail draw of
> a statistic whose expectation under the specified process is bounded above by
> about 0.04 by derivation and whose fixed-bins-offset alternative is excluded by
> this batch's own high-precision block; no locus for a deterministic component
> has been identified, none is asserted, and this lineage is closed.

— and write no sentence attributing the shift to the driver, the build or the
platform.

---

**Independence:** fresh session, no conversation lineage shared with
TASK-20260729-031, -033, -035 or -037; inputs are committed blobs and the task
card. Reading a committed artifact is not shared lineage.
**Model independence: not available and not claimed** (INT-BATCH013-D); this
session is not offered toward any `completion_quorum` attestation.
**Requested policy:** `review-adversarial`. **Resolved model:** `claude-opus-5`,
self-reported, `model_verified: false`, `fallback_used: false`. The adapter was
not invoked.
