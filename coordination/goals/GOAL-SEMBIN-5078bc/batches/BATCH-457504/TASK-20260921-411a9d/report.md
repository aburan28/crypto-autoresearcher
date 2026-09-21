# Red Team report — J-2 and the proves-too-much control

- **task**: `TASK-20260921-411a9d`
- **review round**: `REVIEW-SEMBIN-20260921-457504`
- **joint owned**: J-2 only, plus the round's `proves_too_much` control
- **run under review**: `RUN-SEMBIN-b6eb9f` (`EXP-SEMBIN-c2c312`, `H-SEMBIN-112e2e`)
- **runs launched**: 0. Every number below is an exact finite recomputation from
  committed records in the run package.
- **verdict on J-2**: **BREAKS.**

I am blind to `TASK-20260921-f2d82f` (J-1) and `TASK-20260921-f1e5bd` (J-3) and to
the plan's `coordinator_prior`. I read the review plan through a filter that
replaced `coordinator_prior` with a placeholder before anything was printed; see
`attestation.yaml`.

---

## 0. Answer first

The contract's declared primary metric `D_macaulay_rank_statistic` was **never
computed**. `experiments/EXP-SEMBIN-c2c312/code/run_cells.py:148` binds that
contract metric name to the value `closure_D`:

```python
recB = dict(base, instrument="closure_certificate", input_sha256=sha, closure_D=closure_D,
            max_generator_degree=max_gen_deg, per_D=per_D,
            D_macaulay_rank_statistic=closure_D,
```

`closure_D` is a third quantity, and by the run's own code documentation it is an
**F4-side** quantity, not a Macaulay-side one. The instrument the same file calls
"the DREG statistic" (`macaulay_single_level`) emits a rank, rows, columns and a
deficit at an input degree; it emits **no degree at all**. So the headline
`closure_D − d_F4 = 0` is an agreement between two F4-side quantities, and the
load-bearing conclusion — that the DREG statistic is a different kind of thing —
rests on a third instrument that produced no number to compare and was never
calibrated against any archived GOAL-DREG-001 rank.

The substitution is disclosed **nowhere** as a deviation. `manifest.yaml` records
`protocol_deviations: []`. The seven deviations in `task-report.md` and
`NOTES-deviations-and-limitations.md` are all about cost, cells and caps; none of
them says that the contract's primary metric was replaced. The run's own summary
sentence — "all for cost, none for content" — is therefore **false as to the
metric**, and false as to at least one other item (deviation 2, below).

**Unit-ideal count among the 9 map-supporting instances: 5 of 9.**

**The falsification criterion is unsound as written.** Under the `D` actually
measured it cannot fire at all, and even under the `D` the contract intended the
inference to `EV-DREG-008` does not go through, because it conflates a degree at
which a Macaulay matrix was *built* with a degree a system *attains*.

**On the completion criterion, directly, as the card invites:** this run does
**not** earn `GOAL-SEMBIN-5078bc` completion criterion 1. That criterion asks for
the map between `d_F4` and *GOAL-DREG-001's Macaulay-rank `d_reg`/`D`*,
**instrumented on identical instances**. The map that was instrumented on
identical instances is `d_F4` ↔ `closure_D`, which is not that map. A Coordinator
decision could still state an explicit map and satisfy the criterion's letter —
but it would be resting on a definitional argument plus `EV-DREG-008`'s own
committed text, not on this run's instrumentation, and it should say so.

---

## 1. (a) The metric

### 1.1 What the contract asked for

`specification.yaml` `metrics.primary`:

```
- d_F4_semaev_definition
- D_macaulay_rank_statistic
- separation_D_minus_d_F4
- per_degree_pair_count_profile
- per_degree_rank_increment_profile
```

The contract never gives `D_macaulay_rank_statistic` a formula. The nearest
binding definitions are in the records the contract is built on:

- `preregistered_prediction.formula`: "the excluded tail, i.e. **degrees at which
  the Macaulay block still gains rank** are degrees at which F4 reports 'No pairs
  to reduce'".
- `H-SEMBIN-112e2e.mechanism`: "The Macaulay-rank statistic is a property of a
  FIXED-DEGREE LINEAR ALGEBRA PROBLEM: for each degree d, build the Macaulay
  matrix … and compute its rank, or its rank deficiency … It **reports a degree as
  active whenever the degree-d block contributes rank the degree-(d−1) block did
  not**."

Both readings make `D` the **largest active degree** — a degree read *off* a rank
sweep. The hypothesis then flags, in its own words, that this is ambiguous:
"GOAL-DREG-001 may report a solving degree, a degree of regularity in the
semi-regular sense, or a first-degree-of-rank-deficiency; these coincide for
semi-regular systems and diverge for the chained system." Resolving that ambiguity
is squarely inside this experiment's objective. **It was not resolved. It was
sidestepped.**

That under-specification is a **defect of the CONTRACT** and I record it as one
(OBJ-3). A contract that names a primary metric and never defines it invites
exactly the substitution that happened.

### 1.2 What `closure_D` is

From `code/closure_cert.py`, the instrument's own docstring:

> For a cap D ≥ max generator degree, `W_D` is the smallest subspace of the
> Boolean ring truncated at degree D that contains the generators and is closed
> under multiplication by monomials … Its reduced echelon basis `G_D` has the same
> leading-monomial ideal as the basis an F4 with pair selection by degree holds
> after processing every pair of degree ≤ D (truncated Buchberger criterion), so:
> **`G_D` is a Groebner basis of the ideal ⟺ F4 completes with step degree ≤ D**.
> … `closure_D` = the smallest D with verdict SUFFICIENT.

So `closure_D = min{ D : a degree-selecting F4 completes at step degree ≤ D }`.
That is a **solving degree of a truncated F4** — an output of a terminating
procedure, on the F4 side of the ledger, and defined by reference to F4. It is
iterated: `_run(..., max_iter=64)` re-multiplies the accumulating basis until the
degree-D span stabilises.

The DREG-side instrument is a *different function in the same file*:

```python
def macaulay_single_level(N, equations, D, mem_cap_gb):
    res = _run(N, D, equations, max_iter=1, mem_cap_gb=mem_cap_gb)
```

`max_iter=1` — rows are `μ·g` for the **original** generators only, no
re-multiplication, exactly as the docstring says ("The DREG statistic is the
single-level Macaulay matrix at degree D"). It returns `{D, status, rows, cols,
rank, sr_pred_rank, deficit_vs_semiregular}`. **No degree is returned.** `D` is a
call argument.

### 1.3 Is `closure_D` the contract's `D`? No — and the run knows it

Three independent reasons:

1. **Different objects.** `closure_D` is iterated closure; the DREG statistic is
   single-level. The run's own code separates them into two functions with two
   instrument labels (`closure_certificate` vs `macaulay_single_level_DREG`) and
   emits two separate record types per instance.
2. **Different sides of the comparison.** `closure_D` is *defined by* F4
   termination. The contract's `D` was to be defined by Macaulay rank growth. A
   statistic defined by F4 termination cannot be the independent second
   instrument in a map from F4 to Macaulay.
3. **Different direction of the argument.** The report's own central claim is that
   the DREG statistic's degree is an *input* while `d_F4` and `closure_D` are
   *outputs*. That sentence concedes that `closure_D` is on the `d_F4` side of the
   very distinction the report draws.

**Grep result:** the strings `D_macaulay_rank_statistic` and
`separation_D_minus_d_F4` appear in exactly three places in the experiment tree —
the specification (where they are declared), `run_cells.py:148` (where the first is
bound to `closure_D`), and the raw `results.jsonl` records (where the closure
record carries `"D_macaulay_rank_statistic": 4` alongside `"closure_D": 4`). The
string `separation_D_minus_d_F4` never appears outside the specification at all;
the computed field is `separation_closure_minus_dF4`.

So the substitution happens in the raw record writer, **under the contract's own
metric name**, and is then renamed to `closure_D` in `results-table.json`,
`summary.json` and the report. The report's naming is the more honest of the two;
the raw record is the one that asserts the contract metric was measured.

### 1.4 Testing "all for cost, none for content"

| # | Deviation | Cost or content? |
|---|---|---|
| 1 | 5 draws instead of 20 | cost, but see #2 |
| 2 | **closure on draw 0 only** | **CONTENT** |
| 3 | field-equation convention confounded with instrument | disclosed, content, and the run says so |
| 4 | memory-capped F4 traces | cost (infrastructure) |
| 5 | closure D=5 never attempted | cost |
| 6 | single-level D=4 skipped at (12,6,6,2) | cost, but see §1.5 |
| 7 | instrument-identity control scope | cost |
| — | **primary metric substituted** | **CONTENT, and undeclared** |

Deviation 2 has a content consequence the run does not state. All 9
map-supporting instances are at **seed 20260913001, draw 0** — verified by
recomputation. `HEUR-001` is the contract's `heuristic_under_test`, and its
declared `falsification_condition` is "`D − d_F4` varies across the 20 random R
draws within a single cell **or** varies between B = 1 and random B." With the
closure run on one draw, the R-draw arm of that condition is **structurally
untestable**, and so is the contract's `separation_invariance` prediction. Half of
the falsification route for the run's own declared heuristic was removed by a
deviation labelled "for cost."

The B arm survives: (15,5,3,3) carries all four subspace×B variants and (17,3,3,6)
carries both B modes, and the separation is 0 in every one. That is real and I
credit it.

### 1.5 The metric the run could have computed and did not

This is the part that makes the substitution avoidable rather than merely
regrettable, and it is the cheapest route forward.

The single-level DREG-style instrument **did run**, on every instance, at D = 3 and
D = 4. Recomputed from `results-table.json`:

- D = 3: 126 completed measurements, `deficit_vs_semiregular` ∈ {0, 1} (1 on every
  structured instance, 0 on the planted-point control).
- D = 4: 111 completed measurements, deficit ranging 0 … 71 (46 … 71 on structured
  cells).

A first-degree-of-rank-deficiency reading — one of the three readings
`H-SEMBIN-112e2e` explicitly names — is computable from those two columns without
running anything. **31 instances** carry a completed single-level measurement at
both degrees *and* a `d_F4` value. That is 3.4× the 9 instances the closure-based
headline rests on. The contract's actual primary pairing had more raw material in
the package than the substitute did, and none of it was formed into the metric.

I am not asserting which of the three readings is the right one — naming it is a
Coordinator act. I am asserting that the run held the data to state one, state
which one, and compute `D − d_F4` on 31 instances, and instead reported a
different separation on 9.

---

## 2. (b) The prosecution: the run did not settle the map

The central move, quoted from `task-report.md`:

> This is a rank statistic of a fixed-degree linear algebra problem; it has no
> notion of termination and is not the quantity Assumption 1 bounds. Its degree
> parameter D is an input to the instrument, whereas `d_F4` and `closure_D` are
> outputs.

**P1 — The distinction is a property of the instrument the run built, not a
measured property of GOAL-DREG-001's instrument.** `macaulay_single_level(N,
equations, D, mem_cap_gb)` takes `D` as a positional argument. That `D` is an input
to *this function* is a fact about the function signature, available before the
function is called, on zero instances. No byte-identical system, no F4 trace and no
closure was required to observe it.

**P2 — GOAL-DREG-001's instrument was never run, and the re-implementation was
never calibrated.** `H-SEMBIN-112e2e.assumptions` item 3 is "GOAL-DREG-001's
instrument can be run on instances chosen here." It was not. What was copied
verbatim is the *semi-regular prediction formula*
(`h012_peel_rank.py::semireg_rank_pred`), not the rank instrument or its
degree-reporting logic. The run's own limitation is explicit:

> the archived n = 12 fixture hash was not reproducible by the fixture builder on
> this host … so **no numeric calibration against an archived DREG rank was
> possible**.

So the one instrument whose commensurability is the entire question is the one
instrument with **no** baseline control. The contract's baseline control ("both
instruments must return 4") was discharged by `closure_D` and `d_F4` — the two
instruments whose commensurability was never in doubt.

**P3 — The conclusion was already in the committed ledger.** `EV-DREG-008`'s own
`boundaries` block reads: "Structural `deficit_genuine` ≠ theoretical `d_reg`." Its
cell is "n=12, t=3, ti=0, seed=2026, **D=6**" and its reported quantity is
`deficit_genuine = 17947`, a rank difference. That record, committed in July 2026,
already says that its `D` is a frozen input and its output is a rank, not a degree.
The run's conclusion is a restatement of it. Restating a committed boundary is
useful; it is not settling an open question by measurement.

**P4 — The headline number's expected value is 0 by the run's own equivalence
argument.** `closure_cert.py` asserts `G_D` is a GB ⟺ F4 completes at step degree
≤ D. Under that assertion, `min{D : G_D is a GB}` and "the maximal F4 step degree
before termination" are the same number. Measuring a difference of 0 between two
quantities you have argued are equal is a consistency check on the argument. It is
a real check (see §3), but it is not a map to a third quantity.

**P5 — The measured set is degenerate for the purpose.** All recomputed:

| property of the 9 map-supporting instances | value |
|---|---|
| unsatisfiable (unit ideal, quotient dimension 0) | **5 of 9** |
| distinct seeds | 1 (`20260913001`) |
| distinct draws | 1 (`d0`) |
| instances exercising Semaev's empty-tail exclusion (`d_F4_naive ≠ d_F4_semaev`) | **0 of 9** |
| instances at n = 12, the only n with a committed GOAL-DREG-001 measurement | **0 of 9** |

Two of those deserve a sentence each.

*The definitional feature under test is inert on the whole set.* Across all 45
completed F4 traces exactly **one** instance has `d_F4_naive ≠ d_F4_semaev`
(`sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3`: naive 5, Semaev 4, empty steps at
[4, 5]). That instance has **no closure value** and is not among the 9. Semaev's
`d_F4` differs from "max step degree" precisely by the exclusion of empty tail
steps; the run asserts the map exactly where that exclusion never bites.

*There is no shared cell with the campaign the map is for.* GOAL-DREG-001's
committed cell is n = 12, t = 3 (m = 3). The SEMBIN cell set contains no
(12, 3, 3, ·). Its only n = 12 cell is (12, 6, 6, 2), and closure coverage there is
**0 of 15 instances** — recomputed. `H-SEMBIN-112e2e.predictions` asked for
strictness "on the instances closest in shape to those GOAL-DREG-001 measured at
Macaulay degrees 5 and 6." No such instance was measured with both instruments.

**P6 — One conjunct of the `success_criterion` was not evaluated, and the report
does not say so.** The criterion has four conjuncts; the third is "the matched-null
separation differs from the structured separation." The null's F4 hit the wall cap
after 3 rounds, so the null has **no** `d_F4` and therefore **no separation**
(`manifest.yaml` records `null_f4_d_F4: null`, `null_closure_D: null`). The
contract's third invalidation rule — the run is invalid if the two separations are
equal — was likewise not evaluable. Neither non-evaluation is a defect: it is an
infrastructure fact under AGENTS.md rule 5 and nothing follows from it. **Failing
to report it as a non-evaluation is the defect**, and the report instead writes
"This is the control the contract asks for" about a different comparison. See §5,
object 3.

**P7 — The two halves of the report never meet.** The "0" comes from
closure vs F4. The "not the same quantity" comes from single-level vs *nothing*.
There is no instance in this package on which the DREG-side statistic and `d_F4`
were both reduced to comparable numbers and differenced. The map named by
completion criterion 1 has **no measured value anywhere in the run package**.

---

## 3. (c) The defence: what byte-identical measurement adds

I built this case as hard as the prosecution, and part of it holds.

**D1 — It converts an argued equivalence into a tested one, and the test could
have failed.** `closure_cert.py`'s equivalence is an *argument* (a truncated
Buchberger criterion for a pair-selection-by-degree F4), and the run says so:
"the closure certificate's equivalence … is argued in `closure_cert.py`; the run
measures both and reports their agreement per instance rather than relying on the
argument." msolve is an independently written F4 with a **different
field-equation convention** — explicit `x² + x` generators, against the closure's
Boolean ring where `x² = x` is implicit. `H-SEMBIN-112e2e.mechanism` names that
convention as one of two effects that "can shift a reported degree by one." It did
not shift it on any of the 9. Nor is the agreement forced by pair-selection order:
msolve uses its own strategy and could in principle have done productive work at
degree 4 where a degree-truncated closure completes at 3. This is a genuine,
falsifiable, passed cross-engine test, and it is the one result the run has
honestly earned.

**D2 — It calibrates the degree scale against the paper.** Both instruments return
4 at both reproduction cells, matching KN-LIT-fa346d Table 1. Without that, any
later degree disagreement is equally explicable as an engine artifact, and
`EXP-SEMBIN-7e1371` is blocked on exactly this. That is a real prerequisite
discharged. (Whether it is discharged *validly* — instance counts, byte identity,
duplicate records — is J-1's, and I express no view.)

**D3 — It produced a reusable DREG-side datum on shared bytes.** The single-level
deficit against the archived semi-regular prediction is exactly 1 at D = 3 on every
structured instance and 46 … 71 at D = 4. That is a concrete, per-instance
measurement of where the chained system departs from semi-regularity, on systems
whose bytes are also the F4 instrument's bytes. It is the raw material a `d_reg`
reading needs, and it did not exist before this run.

**D4 — Writing a definitional remark down against data makes it auditable.** The
input/output distinction may be available a priori, but no SEMBIN record stated it,
and stating it beside per-degree profiles on shared bytes makes it checkable rather
than assertible. A remark nobody had written down is a contribution when it is
written down with the data that lets a reader test it.

### Which case is stronger, and why

**The prosecution, decisively — but not on the ground the attack plan leads with.**

The attack plan's (b) asks whether the input/output remark needed an experiment.
Taken alone, the defence answers that well enough: D1 is a real test of a real
argument, and D4 is a fair point about auditability. If the only charge were
"you proved something definitional", I would return `inconclusive`.

The charge that carries is **P1 + P7 together**: the run measured the map between
`d_F4` and a quantity *defined by F4 termination*, then drew its conclusion about
GOAL-DREG-001 from a *third* instrument that emitted no comparable number and was
never calibrated. The headline and the conclusion are about different objects and
are joined by no measurement. The defence's best items (D1, D2) are about the
first object; they say nothing about the second, which is the one the completion
criterion names.

P5 then bounds even D1. The cross-engine agreement is verified on 9 instances at
one seed and one draw, 5 of them unit-ideal — where the closure decides by the much
coarser `1 ∈ W_D` test rather than by counting standard monomials — and 0 of them
exercising the empty-tail exclusion that distinguishes Semaev's `d_F4` from the
naive maximum. The conventions had the least room to differ exactly where they were
compared. D1 survives as a narrow, honest result; it does not survive as a map.

**Narrowest statement the run supports:** *on 9 chained-S₃ Boolean instances at
seed 20260913001 draw 0, across 5 cells with n ≤ 19 and N ≤ 42, msolve's F4 maximal
productive step degree under Semaev's reading and the minimal sufficient
degree-capped Boolean-ring closure cap agree at 4, with 4 confirmed at both
reproduction cells against the paper's published value; 5 of those 9 instances are
unit-ideal, where the closure decides by `1 ∈ W_4`.* Nothing about the DREG
statistic is measured by that sentence.

---

## 4. (d) The falsification criterion

The contract:

> `D − d_F4 = 0` on every measured instance including the off-diagonal cells refutes
> the hypothesis in the direction that matters most: the two statistics would then
> be the same quantity here, and GOAL-DREG-001's degree-5/6 measurements **WOULD be
> in tension with Assumption 1**.

The run observed `closure_D − d_F4 = 0` on all 9. **The criterion does not fire, and
it is unsound as written.** Three separate failures, in increasing order of
seriousness:

**(i) Antecedent not satisfied — wrong `D`.** The criterion is about
`D_macaulay_rank_statistic`. What was observed is `closure_D − d_F4 = 0`. Since
`closure_D` is defined by F4 termination, that observation is uninformative about
`D_DREG − d_F4`. The criterion cannot be triggered by this run in either direction.
This is a **RUN** defect (the substitution), not a defect of the criterion.

**(ii) Antecedent not satisfied — "every measured instance including the
off-diagonal cells."** Only 1 of the 2 off-diagonal cells produced a separation
value at all: (17,3,3,7) on one instance; (17,3,3,8) produced no F4 trace and no
closure decision. "Every measured instance" is 9 of 126 recorded instances. Even
under the right `D`, the universal the criterion quantifies over was not covered.
Again a matter of coverage, largely infrastructure-driven and therefore not a
defect in itself — but it means the criterion's antecedent is unmet regardless.

**(iii) The consequent is invalid even with a perfect antecedent — and this is the
real fault.** Suppose it were established that `D_DREG = d_F4` on these systems.
The criterion concludes that GOAL-DREG-001's "degree-5/6 measurements" would be in
tension with Assumption 1. That step **conflates the degree at which a Macaulay
matrix was built with a degree the system attains.** `EV-DREG-008` is a rank
measurement at a *frozen input* `D = 6`; its reported output is
`deficit_genuine = 17947`, and the record's own boundary says "Structural
`deficit_genuine` ≠ theoretical `d_reg`." Building a Macaulay matrix at degree 6 and
measuring its rank asserts nothing about the solving degree being 6. Assumption 1
bounds `d_F4 ≤ 4`; a rank computed at input degree 6 is not a claim that any degree
statistic equals 6, so no equality `D_DREG = d_F4` could put it in tension with
anything.

So the criterion is unsound at its consequent, independently of what was measured.
**That is a defect of the CONTRACT, not of the run** — and it is the more important
of the two classifications, because it means the experiment could not have
delivered the inference the criterion promised even if it had been executed
perfectly.

**This cuts both ways, and here is the direction the card asked me to check.** If
the criterion were sound, the run would have a live tension with `EV-DREG-008` that
must be recorded rather than dissolved. It is not sound *for `EV-DREG-008`*. But a
live tension does exist elsewhere and this run neither creates nor resolves it:
GOAL-DREG-001's campaign-level quantity is **not only** a rank at a fixed degree.
Its objective asks "does `d_reg(n)` track the semi-regular null, or depart
non-generically … bounded `d_reg`, or a deficit/`gap(n) = d_reg − d_ff` that grows
with n". Its completion criterion asks for "`d_reg` OR `gap(n) = d_reg − d_ff`
measurements … evaluated at D up to and including `d_reg` where reachable" — `D`
swept, `d_reg` read off as an **output**. Its BATCH-001 and BATCH-002 checkpoints
report degree outputs: "analytic linear `d_reg` law (c* = 0.23748, Θ(n))",
"`d_reg(sem) ≥ d_reg(null) = 7`", "sem `d_ff` = 2–3".

For **those** quantities the input/output escape does not apply, and the
commensurability question is fully open. This run does not touch them: it computed
no `d_reg`, no `d_ff`, no gap, and measured no instance at GOAL-DREG-001's cell.
**That residual must be recorded, not dissolved** (OBJ-2).

---

## 5. (e) The proves-too-much control

Argument under test, verbatim from the plan: *"both instruments returned the same
number on identical bytes, therefore the two statistics are the same quantity
here."* Run unchanged against four objects whose conclusion is known false.

### Object 1 — the known-false planted-dependency control

**Declared signature:** must NOT conclude commensurability from this instance.

**Outcome: PASSES.** The report's treatment is one line — "Known-false (planted
degree-2 point). `d_F4` = 2, `closure_D` = 2; the contract requires 2 from both" —
and it draws no map conclusion. I verified by recomputation that the control is
**excluded from the 9**: 11 rows in `results-table.json` carry a non-null
`separation_closure_minus_dF4`; removing `ctrl_known_false_N35` and
`sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0_repeat` leaves exactly 9. The argument
correctly declines to run here.

**Residual, minor:** the raw record for this degenerate control carries
`"D_macaulay_rank_statistic": 2`. The contract's primary metric name is populated
on a planted-dependency control. That is the §1.3 labelling defect showing up
where it is most visible, not a conclusion defect.

### Object 2 — the unsatisfiable instances

**Declared signature:** must report how many of the 9 are unsatisfiable, and must
not rest the identity claim on them. *"THE REVIEWER MUST COMPUTE THIS NUMBER."*

**The number: 5 of 9.** Computed from `results-table.json` as
`quotient_dimension == 0` over the 9:

| instance | cell | quotient dim | unit ideal | closure `D=4` verdict basis |
|---|---|---|---|---|
| `sem_n13_m4_t4_k4_low_B_equ_…_d0` | (13,4,4,4) | 36 | no | standard monomials = \|V(I)\| = 36 |
| `sem_n15_m5_t3_k3_low_B_equ_…_d0` | (15,5,3,3) | 0 | **yes** | **1 in W_D** |
| `sem_n15_m5_t3_k3_low_B_ran_…_d0` | (15,5,3,3) | 0 | **yes** | **1 in W_D** |
| `sem_n15_m5_t3_k3_ran_B_equ_…_d0` | (15,5,3,3) | 0 | **yes** | **1 in W_D** |
| `sem_n15_m5_t3_k3_ran_B_ran_…_d0` | (15,5,3,3) | 0 | **yes** | **1 in W_D** |
| `sem_n17_m3_t3_k6_low_B_equ_…_d0` | (17,3,3,6) | 6 | no | standard monomials = \|V(I)\| = 6 |
| `sem_n17_m3_t3_k6_low_B_ran_…_d0` | (17,3,3,6) | 0 | **yes** | **1 in W_D** |
| `sem_n17_m3_t3_k7_low_B_equ_…_d0` | (17,3,3,7) | 18 | no | standard monomials = \|V(I)\| = 18 |
| `sem_n19_m3_t3_k7_low_B_equ_…_d0` | (19,3,3,7) | 6 | no | standard monomials = \|V(I)\| = 6 |

**Outcome: FAILS the reporting half of the signature; partially fails the resting
half.**

*Reporting.* The report gives "Of the 43 completed traces, 35 are on unsatisfiable
instances" — a statistic over F4 traces, not over the 9. The 9 are **never** broken
down by satisfiability anywhere in the package. The signature requires that
breakdown and it is absent.

*Resting.* The table above shows the identity is not one fact repeated nine times:
on the 5 unit-ideal instances `closure_D = 4` means "`1 ∈ W_4`", and on the 4
satisfiable ones it means "the standard-monomial count equals `|V(I)|`". Those are
structurally different certificates — the first is a single containment test, the
second a quotient-dimension match — and the report presents their agreement as a
single uniform finding. Semaev's §4.5.1 distinguishes the same two cases in the
same way ("If the ideal generated by the polynomials is unit, then 'step degree'
was always bounded by 4. If not, that is there is a solution, then 'step degree' was
bounded by 4 for all the steps before the basis is computed").

*Calibration — what I am not saying.* 5 of 9 is a majority, not "most or all." Four
genuinely satisfiable instances remain, including a reproduction cell at
(13,4,4,4) with quotient dimension 36, a reproduction cell at (17,3,3,6) with 6, the
off-diagonal (17,3,3,7) with 18, and (19,3,3,7) with 6. The identity is **not**
asserted only where agreement is forced. The plan flagged this as potentially the
most damaging finding in the round; on the numbers it is **material, not fatal**,
and I decline to inflate it. The finding is that the run did not do the split, not
that the split destroys the result.

### Object 3 — the matched-null random dense system

**Declared signature:** must treat the null's wall-cap outcome as an INFRASTRUCTURE
fact yielding no separation (AGENTS.md rule 5), and must not convert "the null did
not produce a sufficient verdict" into "the null confirms the structured result."

**Outcome: PARTIAL FAIL. The argument survives where its conclusion is false, and
the location is identifiable to a single sentence.**

What the run gets right: `manifest.yaml` records `null_f4_status:
unreached_wall_cap`, `null_f4_d_F4: null`, `null_closure_D: null`. The report's own
phrasing, "the verdict does not come out sufficient", is exact — the recorded
verdict is `undetermined`, not `insufficient`, and the report does not upgrade it.

Where it converts, exactly:

> **This is the control the contract asks for**: it shows that a SUFFICIENT verdict
> at degree 4 is not an artifact of the Macaulay construction's shape …

The control the contract asks for is a **separation** comparison: "If the separation
`D − d_F4` is the SAME on the structured and the null system, the separation is a
property of the two conventions." The null produced no `d_F4` and hence no
separation. The declared control was **not evaluated**, and the run substitutes a
different comparison (closure sufficiency: rank 59530/59536 structured against
11186/59536 null) and labels the substitute as the contract's control. That is the
conversion this object was built to catch, and the phrase "This is the control the
contract asks for" is where it happens.

Partial rather than full, in fairness: the substituted comparison is itself
supported by a **completed** rank measurement on both sides, so it is not an
infrastructure artifact, and it does license the narrower claim the report makes
about closure sufficiency. What it does not license is the claim to *be* the
contract's control, or the third conjunct of the `success_criterion`.

Validity consequences of a non-evaluated control belong to J-1 and I express no
view on them.

### Object 4 — GOAL-DREG-001's reported degree-5/6 Macaulay work (`EV-DREG-008`)

**Declared signature:** must block the inference explicitly; the only clean block is
the input-versus-output distinction; if the distinction is sound the inference is
blocked, if merely asserted the run has an unresolved tension that must be recorded
rather than dissolved.

**Outcome: PASSES for `EV-DREG-008` as named. FAILS as a general block, and the
residual tension is real and unrecorded.**

*Blocked, and soundly, for `EV-DREG-008`.* The run does state the block explicitly.
I verified it independently against the record rather than against the run: the cell
is "n=12, t=3, ti=0, seed=2026, **D=6**" — `D` frozen as a parameter — the reported
quantity is `rank_null_restricted = 156520`, `deficit_genuine = 17947`, and the
record's own `boundaries` say "Structural `deficit_genuine` ≠ theoretical `d_reg`."
No degree statistic of 5 or 6 is asserted there. The inference is blocked. **But it
is blocked by `EV-DREG-008`'s own committed text, which predates this run by seven
weeks.** The run confirms a block that was already in the ledger; it does not
establish one.

*Not blocked for the campaign.* GOAL-DREG-001's objective, completion criterion and
BATCH-001/002 checkpoints report `d_reg` and `d_ff` as **outputs** (§4). For those
the input/output distinction is simply false, and the run neither measured them nor
mentions them. A decision citing this run to say "GOAL-DREG-001's measurements do
not bear on Assumption 1" would be true of `EV-DREG-008` and unsupported for
`d_reg(n)`.

*And there is no shared instance.* GOAL-DREG-001's cell is n = 12, t = 3; this run
measured no (12, 3, 3, ·) instance, and its only n = 12 cell, (12, 6, 6, 2), has
closure coverage 0 of 15. Completion criterion 1's phrase "instrumented on identical
instances" is not satisfiable across the two campaigns from this package.

**Control summary:** 1 pass, 1 fail (reporting), 1 partial fail, 1 pass-with-fatal-
gap. The argument does not survive on the objects where its conclusion is false in
one clean piece; it survives in two specific places — the "This is the control the
contract asks for" sentence (object 3) and the unqualified generalisation from
`EV-DREG-008` to GOAL-DREG-001 (object 4).

---

## 6. (f) Leakage against `interpretation_limits`

`specification.yaml` forbids this run bearing on Assumption 1 in either direction.
I checked both.

**Toward supporting Assumption 1: no leakage found.** The report opens with
"Commensurability only: nothing here supports or refutes Assumption 1", repeats it
in the limitations, and never states that Assumption 1 held. Unreached cells are
labelled "not evidence" and their impediments recorded. The sentence "a value below
4 on an unsatisfiable instance is the expected behaviour and not a disagreement with
the reported tables" is about reproduction of Semaev's tables (criterion 2's
territory), not about Assumption 1's truth, and is defensible.

**Toward undermining Assumption 1: no leakage found.** One near-miss, which I
record because it is the kind of thing that should be visible. `manifest.yaml`
reports `d_F4_naive_values_over_completed: [3, 4, 5]`. Under the naive reading a 5
would look like a counterexample to `d_F4 ≤ 4`. The run correctly applies Semaev's
reading, under which the degree-5 step was empty and is excluded — I verified the
single instance concerned (`sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3`, empty steps
[4, 5], Semaev reading 4). `task-report.md` discusses only instances *below* 4 and
never mentions the naive 5. The omission cuts *away* from a false alarm, not toward
one, so it is not overclaiming in either direction; it is a minor disclosure gap
(OBJ-7).

**The sentence "is not the quantity Assumption 1 bounds" is in scope.** It is a
commensurability statement, which is this experiment's deliverable, not a validity
statement. My objection to it is that it outruns the measurement (§2), not that it
breaches the limits.

**Verdict on (f): the interpretation limits are respected in both directions.** The
run deserves this and I state it plainly.

---

## 7. Forward guidance — what would earn the criterion, cheaply

Under `docs/inventor-protocol.md` §4 a negative finding owes a redirection, and a
red team that only prosecutes is not measuring the claim. Three concrete acts, in
increasing cost. None requires a run.

1. **Zero-run recomputation, highest value.** The contract's actual primary metric
   is derivable from committed records. Name which of the three readings in
   `H-SEMBIN-112e2e.mechanism` is GOAL-DREG-001's (a Coordinator act), compute
   `D_DREG` from the `single_level` rank/deficit columns already in
   `results-table.json`, and form `D_DREG − d_F4` on the **31** instances that carry
   both. That is the contract's `separation_D_minus_d_F4`, on 3.4× the instances the
   substitute rests on, at the cost of a script. It may well come out 0 as well —
   the D = 3 deficit is 1 everywhere and the D = 4 deficit is 46–71 everywhere, so a
   first-fall reading is plainly 4 — and 0 there would be a *real* trigger of the
   falsification criterion's antecedent, requiring the analysis in §4(iii) before
   any conclusion is drawn.
2. **Split the 9 and re-report.** State the 5/4 unit-ideal split, state that the
   `1 ∈ W_D` and standard-monomial certificates are different, and restate the map
   over the 4 satisfiable instances alone. If it still holds there — and on the
   numbers it does, at 4 on all four — the claim is weaker in scope and much
   stronger in kind.
3. **Successor experiment for the shared cell.** The map GOAL-SEMBIN-5078bc
   criterion 1 names needs an instance at GOAL-DREG-001's own cell (n = 12, t = 3).
   `EXP-SEMBIN-c2c312`'s stopping rules forbid adding cells to this contract, so
   this is a new contract, not an amendment.

---

## 8. Required role output

```yaml
red_team_report:
  id: RT-20260921-411a9d
  task_id: TASK-20260921-411a9d
  claim_under_review: >-
    RUN-SEMBIN-b6eb9f states the map between Semaev's d_F4 and GOAL-DREG-001's
    Macaulay-rank statistic: identity on 9 byte-identical instances, and the DREG
    statistic is a different kind of quantity because its degree is an input while
    d_F4 is an output. Claimed to discharge GOAL-SEMBIN-5078bc completion
    criterion 1.
  joint_verdict:
    joint: J-2
    verdict: breaks
  objections: see objections.json (8 entries; 1 fatal, 4 material, 3 minor)
  required_controls:
    - Split the 9 map-supporting instances by satisfiability and report the map
      over the 4 satisfiable instances alone (5 of 9 are unit-ideal; on those the
      closure decides by `1 in W_D`, a different certificate).
    - Compute the contract's D_macaulay_rank_statistic from the single-level rank
      and deficit columns already in results-table.json and form
      separation_D_minus_d_F4 over the 31 instances that carry both it and d_F4.
    - Record that the matched-null separation comparison and the third invalidation
      rule were NOT EVALUABLE (the null has no d_F4), rather than reporting a
      different comparison as the contract's control.
    - Before any successor uses closure_D as a second instrument, calibrate the
      single-level instrument against an archived GOAL-DREG-001 rank; the run
      records that no such calibration was possible on its host.
  counterexample_or_mutation: >-
    The cheapest discriminating mutation is already available at zero run cost:
    recompute the map from the single-level columns instead of the closure columns.
    If D_DREG - d_F4 is also 0 on 31 instances, the run's conclusion survives on
    the right metric and on 3.4x the data; if it is nonzero, the headline was an
    artifact of the substitution. Either outcome is more informative than the
    present report, and neither needs a measurement.
  baseline_comparison: >-
    Not applicable in the Pollard-rho / BSGS sense: no attack, no cost claim, no
    discrete logarithm and no relation is asserted by this run (manifest
    certificate.kind = none, verifier = no-claim). The relevant baseline is the
    prior state of the record, and it is unfavourable: EV-DREG-008's committed
    boundaries already state "Structural deficit_genuine != theoretical d_reg",
    which is the run's load-bearing conclusion. dominated_by for the input/output
    finding: EV-DREG-008 (2026-07-31). sota_delta: none for that finding; for the
    cross-engine closure/F4 agreement the delta is 9 instances of previously
    unmeasured cross-convention consistency, at n <= 19, N <= 42, one seed, one
    draw.
  heuristic_challenges:
    - HEUR-001 is the contract's declared heuristic_under_test and its
      falsification condition has two arms, R-draw variation and B variation. The
      R-draw arm is structurally untestable in this run because the closure
      instrument ran on draw 0 only; all 9 map-supporting instances are seed
      20260913001 draw 0. The B arm is exercised at two cells and shows no
      variation. Half the declared falsification route was removed by a deviation
      labelled "for cost".
    - HEUR-001's random-model justification ("degree-d Macaulay blocks behave like
      random matrices of their size subject to the structural rank defect") is not
      tested by this run at all, and the one instrument that could have tested it
      (single-level rank against the semi-regular prediction) was measured but
      never compared across draws.
  cost_model_challenges:
    - >-
      Non-applicable, recorded rather than omitted. No asymptotic or concrete cost
      claim is made; the contract declares tier toy and the run respects it.
  reduction_and_scope_challenges:
    - >-
      The reduction from "closure_D = d_F4 on 9 instances" to "GOAL-DREG-001's
      measurements do not bear on Assumption 1" passes through a third instrument
      that produced no comparable number and was never calibrated. The hypotheses
      of the step are not checked.
    - >-
      Scope inflation. The input/output block is sound for EV-DREG-008 (D=6 frozen
      as an input, output a rank deficit, boundary says deficit_genuine != d_reg)
      and unsound for GOAL-DREG-001's d_reg outputs (d_reg(null) = 7 at n = 12,
      d_reg(sem) >= d_reg(null), "analytic linear d_reg law c* = 0.23748,
      Theta(n)", d_ff = 2-3). Generalising from the first to the second is the
      scope error.
  proof_architecture_challenges:
    - >-
      Observation-fiber attack. The observable is the scalar degree. The run's own
      contract identified the maxima as "the lossy projection whose fibres created
      the ambiguity" and required per-degree profiles for that reason. The 9
      agreements sit in two distinct fibres (1-in-W_D on 5 instances,
      standard-monomial match on 4) and are reported as one.
    - >-
      Nearby-object attack. The closest object where the conclusion is false is a
      satisfiable instance at GOAL-DREG-001's own cell (n = 12, t = 3). The method
      cannot distinguish it because no such instance was measured; the only n = 12
      cell present, (12,6,6,2), has closure coverage 0 of 15.
    - >-
      Method-ceiling attack. The strongest claim the closure instrument can certify
      is a statement about F4 termination degree, because its own equivalence is
      stated in terms of F4 termination. It cannot in principle certify anything
      about a single-level Macaulay rank statistic. The headline metric was
      therefore outside the instrument's ceiling before the run began.
  narrowest_supported_statement: >-
    On 9 chained-S_3 Boolean instances at seed 20260913001 draw 0, across 5 cells
    with n <= 19 and N <= 42, msolve's F4 maximal productive step degree under
    Semaev's reading and the minimal sufficient degree-capped Boolean-ring closure
    cap both equal 4, including at both reproduction cells where KN-LIT-fa346d
    reports 4. Five of those 9 instances are unit-ideal, where the closure decides
    by 1 in W_4. This is a cross-engine, cross-field-equation-convention
    consistency check on the closure certificate's own truncated-Buchberger
    equivalence argument. It is not a map to GOAL-DREG-001's statistic, which
    produced no degree in this run.
  next_concrete_action: >-
    Before any Coordinator decision cites this run for completion criterion 1:
    compute D_macaulay_rank_statistic from the single_level rank and deficit
    columns already committed in results-table.json, under a named choice among the
    three readings in H-SEMBIN-112e2e.mechanism, and form separation_D_minus_d_F4
    over the 31 instances that carry both it and a d_F4 value. Zero runs, exact
    finite recomputation, and it produces the metric the contract actually declared.
  artifact_paths:
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-411a9d/report.md
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-411a9d/objections.json
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-411a9d/attestation.yaml
```

---

## 9. What I did not review

Owned elsewhere in this round, and I express no view: run validity as the contract
defines it, byte-identity verification, the duplicate `(instance, instrument)`
records from pids 9160/9336 and whether any pair is discordant, the 314/126/44
arithmetic, instance counts per cell, and re-derivation of the `d_F4`, `closure_D`
and separation values from the raw traces. Where a J-2 finding touches those —
object 3's control non-evaluation, and the `protocol_deviations: []` field — I state
the fact and defer the validity consequence.

I also did not verify that the recorded numbers are correct. I read
`results-table.json` as given and recomputed *derived* quantities from it
(satisfiability split, seed/draw coverage, naive-vs-Semaev divergence, single-level
coverage, cell coverage). If the underlying records are wrong, my counts inherit
that error; J-3 owns that question.
