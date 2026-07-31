# RT-20260729-035 — falsification review of QUEUE-AMEND-20260729-005

Task: `TASK-20260729-047`, re-pointed by `QUEUE-AMEND-20260729-005`.
Role: red-team, independent session, non-originating.
Head reviewed: `b45edb5965ebec1da056a6df423b604558595562` on `claude/ecdlp-b011`.
Claim tier: **toy**. Nothing here is target-class under rule A1, no exponent
moves in either direction, and none of this is a cryptanalytic result.

Zero curve compute was performed. No harness function was imported or called.
No commit was made and nothing was staged. The machine-readable rulings are in
`red_team_report.yaml` beside this file; this document carries the argument.

---

## 0. What I was asked to break, and what I did

The ruling stands down `TASK-20260729-044`/`-045` — 7500 seconds and 28 run
identifiers released unspent, zero curve compute in the batch — on the ground
that **no amendment can make `EXP-STR-004` capable of supporting `H-STR-002`**.

My first obligation was to build the strongest honest case for executing
anyway. I built it, and I found four items the Coordinator did not record, two
of which are stronger than any of its own `F-1` … `F-7`. Then I tried to break
the ruling. **I could not break its conclusion. I broke three of its stated
grounds and I dissent from its central reason.**

---

## 1. The case for executing, at full strength

### F-8. The immediate predecessor of arm E-prime measured 29

This is the strongest item for running and the ruling does not record it.

Arm E-prime is not a new construction. `EXP-STR-003` arm E
(`experiments/EXP-STR-003/specification.yaml` lines 238-256) is the *identical*
random factor base, the *identical* base row list, and the *identical*
positional sigma-orbit closure — appended "if `sum(r_shift) > 0` AND `r_shift`
is not already in the list — mirroring, term for term, the filter and dedup at
`harness/endomorphism_la.py` lines 303-304."

That arm **measured `alpha = 11, 1, 0, 29`**
(`ledger/decisions/DEC-20260727-009.yaml`, `instrument_question_disposition`).

The ruling asserts that the same arm, with those two boolean conditions
deleted, is derivably `alpha <= 1` at every declared cell and every `B`. That is
a swing from a measured **29** to a derived **1**, attributed entirely to two
booleans, and it has never been checked on a machine. The derivation explains
the difference — a single suppressed emission shifts the phase of the whole
downstream stream, so triple boundaries stop coinciding with sigma-block
boundaries (`D-5`, and `EV-STR-003` observation `O-4`) — but *that explanation
is itself the unchecked step*. A measured `alpha(E-prime) >= 2` at any cell
would be a **counterexample certificate**, the strongest refutation-artifact
class, against the exact limb the ruling rests on.

### F-9. The arm E-prime limb is not unconditional

`A-2`, `R-7` and `L-5` say the E-prime limb is unconditional and that this is
why the ruling rests on it; `L-5` declares only the A-prime limb conditional (on
`D-3`). Two further conditions are undeclared:

1. **Supply.** The derivation is of the *square* branch of
   `_measure_displacement_rank` (lines 233-242), taken only when the emitted row
   count is at least `B`. The contract's own
   `matched_base_row_budget.why_this_value` states that a shortfall of **two**
   base rows loses it. In the rectangular branch (lines 226-232) the returned
   quantity is `rank(M Z - M)`, whose rows are `sigma . M[i] - M[i]` over the
   *whole* emitted list; for a sigma-closed list those are `sigma r - r`,
   `sigma^2 r - sigma r`, `r - sigma^2 r` per triple — two independent per base
   row — so the measured quantity generically becomes `Theta(B)` rather than
   `<= 1`. Nothing has measured arm E-prime's base-row supply at any cell.

2. **A driver that does not exist.** Arm E-prime's closure — "emit `r`,
   `sigma . r`, `sigma . (sigma . r)` unconditionally" — appears **nowhere** in
   `harness/endomorphism_la.py`. Arm A-prime's closure is the committed block
   *with two conditions deleted*, which is also not committed code. The
   derivation is an argument about a **program that has never been written**.
   `derivation_note.md` `D-8` item 4 already declares that limb conditional; the
   ruling drops the declaration at the exact point it leans on the limb, and
   `L-2` ("a derivation about committed Python functions") is inaccurate for it.

### F-10. The marginal cost of executing is zero and the option expires

7500 seconds and 28 run identifiers are already budgeted and have no alternative
use. `campaign_budget.maximum_batches = 14` is consumed at this close; a
fifteenth batch requires explicit user authorization and is not self-granted. So
the derivation the ruling rests on may go permanently unchecked, and the option
to check it expires here and cannot be repurchased from inside the program. The
information gained is not about `H-STR-002` — it is about **the ruling**.

### F-11. The ruling answers a different question from the one it decides

The amendment's title question, its single-sentence justification, and `A-3`
through `A-7` all answer *"can an amendment make `EXP-STR-004` capable of
supporting `H-STR-002`"*. The disposition answers *"should `EXP-STR-004` be
executed"*. These are different questions.

Route (a) — recording the three `discharge_condition_recordable_verbatim` texts
and approving — **requires no amendment**, edits no frozen file, consumes no
cycle, adds no arm and adds no statistic, so it passes
`QUEUE-AMEND-20260729-003`'s direction test trivially and `A-5`/`A-6` do not
reach it. Under route (a) nobody claims the run supports `H-STR-002`; its value
is checking the derivation and checking `D-3` at `B = 192` and `B = 193`. **The
amendment concedes exactly this at `R-7` and then does not weigh it against a
budget with no other use.**

### Where the recorded case FOR is itself overstated

- `F-2` ("the one measured hazard is cleared", "the infrastructure is specified
  and paid for"). The `TASK-20260729-043` receipt's
  `O_2_VERIFIED_BY_THE_DISPATCHING_SESSION` block measures the **distinct-target**
  limb only: `target_period` 183 for CURVE-J12S1 against a maximum `R_base` of
  66, and 3468 for CURVE-J16S3 against `R_base(97) = 34`. **Base rows are hits,
  not distinct targets.** No archived hit rate exists for a phi-invariant factor
  base at any declared `B`; the contract's own `collection_quota` clause picks
  `Q = 60` expressly because "at the smallest rungs the committed quota leaves
  too few candidate targets to make `R_base(B)` base rows probable" — and picks
  it *without measuring*. The receipt's own `the_hazard_is_still_real` concedes
  the point. The hazard is half cleared.

- `F-4`'s live content — that `D-3` is unverified at `B = 192` and `B = 193`,
  where the builder returns a **short** list if it cannot find enough whole
  orbits inside `j < 50*B + 1000` (line 95) — is true and is the one genuinely
  unchecked fact about *committed* code in the design. It does not require the
  ladder, a driver, a closure, a relation or an alpha. See §6.

---

## 2. My own derivation, from primary source

I read `harness/endomorphism_la.py` lines 85-114, 122-244 and 247-353
**directly**, not as quoted in the derivation note or the review. This matters:
the amendment's own `how_many_independent_derivations_exist` records that its
third derivation worked "by hand from the source text **quoted in those
artifacts**", so a mis-transcription in derivation #1 would propagate silently
into #3. It does not.

`Z[i][j] = 1` exactly when `j = sigma(i)`; `(Z M)[i][j] = M[sigma(i)][j]`;
`Z_inv[k][j] = 1` exactly when `k = sigma(j)`, so `(A Z_inv)[i][j] =
A[i][sigma(j)]`. Hence

```
D[i][j] = M[i][j] - M[sigma(i)][sigma(j)]   (mod n)
```

At a cell with `B = 3q + 1`, writing `c_j = r_j[3q]`, with
`S_1 r_j = sigma . r_j` zeroed at coordinate `3q`,
`S_2 r_j = sigma^2 . r_j` zeroed at coordinate `3q`, and `sigma(3q) = 3q` so
`sigma . e_{3q} = e_{3q}`:

```
D[3j]   =  c_j e_{3q}
D[3j+1] =  0
D[3j+2] = -c_j e_{3q}
D[3q]   =  r_q - sigma^{-1} . r_q ,  whose 3q coordinate is r_q[3q] - r_q[3q] = 0
```

Every tail-induced row lies in the one-dimensional span of `e_{3q}`; the
remaining row is orthogonal to that coordinate and independent of it when
nonzero. Therefore

```
alpha(A-prime) = [exists j < q with r_j[3q] = 1] + [sigma . r_q != r_q]  <= 2
alpha(E-prime) = [sigma . r'_q != r'_q]                                  <= 1
alpha = 0 exactly, both arms, at every residue-zero cell
```

**I reproduce the row forms and both bounds.** I checked it twice, once in the
note's convention and once in the equivalent convention
`sigma . D[i] = sigma . M[i] - M[sigma(i)]`, which has the same rank because it
is right-multiplication of the whole matrix by one permutation. This is a fifth
derivation and it **agrees** — subject to the conditionalities of `F-9`.

---

## 3. Is there a fifth discriminating statistic? No.

I concur with `C-1` … `C-4` on their stated grounds and add four more, all of
which fail.

- **C-5, displacement rank under the multiplicative phi-image map as the
  shift.** Collapses into `C-2`. That map is a permutation of factor-base
  indices *if and only if* the base is closed under multiplication by `zeta3` —
  the definition of the builder's output. The statistic returns "the
  phi-invariant factor base is phi-invariant".
- **C-6, per-eigenspace block ranks.** Both arms are sigma-equivariant by
  construction after the closure, both consume `R_base(B)` base rows of support
  size `m`, and a decomposition has no reason to prefer summands inside one
  orbit. A refinement of `C-3`, inheriting its blindness to genuineness and its
  archived adverse prior (rank deficiency 4, 6, 30, 67 against 0, 0, 0, 1).
- **C-7, truncation-loss rate of the phi-image map.** Supported on the single
  index `3q` at residue one, identically zero at residue zero, and fully
  derivable before any alpha. Measures the builder's truncation.
- **C-8, row-weight distribution of the closed matrix.** The same tail artifact
  under another name; identically equal in the two arms at every residue-zero
  cell.

### What I found instead: the verdict is set by a free choice of null

Arm E-prime's closure is **positional**; arm A-prime's is the committed
**multiplicative** map. The spec declares the mismatch itself. Now take the
other candidate null, which the spec names and discards: the committed
multiplicative closure with the filter off, applied to a *random* factor base.
The spec asserts that "a random factor base is almost never closed under
multiplication by `zeta3` and the closure would emit empty rows at every cell".
Take that assertion and run the same row computation on the stream
`[r'_0, 0, 0, r'_1, 0, 0, ...]`:

```
D[3j]   =  r'_j
D[3j+1] =  0
D[3j+2] = -sigma^{-1} . r'_j
D[3q]   =  r'_q - sigma^{-1} . r'_q
```

Rank generically `2q = 2(B-1)/3` — **`Theta(B)`, not `O(1)`**.

So three defensible-looking null conventions give three answers on the same
instance: no closure gives `alpha` of order `B` (the `EV-STR-001` baseline the
prediction actually cites); the committed multiplicative closure with the filter
off gives about `2B/3`; the positional sigma closure gives `<= 1`. **Under two
of the three, `H-STR-002`'s first prediction reads as confirmed with a large
separation.** Nothing in the mathematics of the curve selects among them.

This does not rescue the experiment — it buries it. The instrument is not merely
vacuous against one null; **its verdict is chosen by the experimenter's
convention, in both directions.** That cannot be repaired by an amendment and
cannot be rescued by running it. It is also emphatically *not* a reason to run
the multiplicative null: that arm appends literal all-zero rows, its `Theta(B)`
is an artifact of counting zero rows as rows, and it would be a forbidden third
arm.

---

## 4. Ruling: the stand-down stands, on a narrowed ground

**The ground that survives adversarial pressure is not "no amendment can create
support".** It is this:

> The only discriminating power execution would have over the derivation is the
> power to detect a **driver bug**. Arm E-prime's bound follows from the
> *contract's own definition* of arm E-prime's closure together with
> `sigma^3 = id`; arm A-prime's follows from the same plus `D-3` and `D-4(b)`. A
> driver that implements the specification reproduces both bounds by
> construction. Twenty-eight curve runs at the last authorized batch is an
> expensive software test — and the two *committed-code* facts it would settle
> are reachable for seconds without it.

I record what would have made me rule the other way, so the ruling is
falsifiable: if arm E-prime's bound had depended on any property of the curve,
the factor base or the collector rather than on the contract's own closure
definition, execution would have had real discriminating power and I would have
recommended running.

### The ruling this card exists for

**If `alpha <= 3` holds at every named ladder cell for arm A-prime and arm
E-prime matches it, that is a property of the closure convention and not support
for `H-STR-002`.** I rule it in terms, from a derivation I performed myself from
primary source. And the converse holds too: an *unfavourable* ladder would not
be evidence against `H-STR-002` either, because under the derivation
`alpha > 2` means the driver, the builder or the collector failed. Both
directions are instrument findings. That symmetry *is* the definition of a
non-diagnostic instrument, and it is the honest content of this batch.

### Defects that must be repaired in `DEC-20260729-004`

| id | defect | severity |
|----|--------|----------|
| RT35-D1 | The E-prime limb is called unconditional and rests on undeclared supply and driver-fidelity conditions (`F-9`). | blocking for wording |
| RT35-D2 | `R-2` compares derived **upper bounds** as if they were realised values. `alpha(A-prime) = 0` with `alpha(E-prime) = 1` occurs whenever no A-prime base row touches the tail, `sigma . r_q = r_q`, and `sigma . r'_q != r'_q`. | major |
| RT35-D3 | The reserved `KN-FIND-010` boundary sentence is **false as written**. | blocking for wording |
| RT35-D4 | `F-2` clears one of the two limbs of `O-2`. | major |
| RT35-D5 | The `RT-20260729-036` defect is a **dangling reference**, not a duplication. | minor |

**RT35-D3 is the most important, and it is archived-number checkable.** The
sentence reserved verbatim for promotion reads: *"closing a relation row list
under a shift operator makes the displacement rank with respect to that operator
`O(1)` **by construction**, independently of the factor base, so a displacement
rank measured on a shift-closed row list cannot be evidence of endomorphism
structure."* The qualifier **unconditionally** is missing — and without it the
sentence is falsified by this program's own archived numbers: `EXP-STR-003` arm
E closed its row list under exactly this shift operator with the line-303/304
filter and dedup **enabled**, and measured `alpha = 11, 1, 0, 29`. A
shift-closed row list measured 29. Carry the sentence only with the
unconditionality qualifier and with the arm-E counter-numbers beside it, and do
not promote `KN-FIND-010` in the present wording under any amendment.

On **RT35-D5**: from a read-only scan of the whole worktree, `RT-20260729-034`
occurs in the `TASK-20260729-042` card, the queue, both `-042` review artifacts
and `ledger/goals/GOAL-ECDLP-001.yaml`; `RT-20260729-035` occurs only in this
card, the queue and the goal record (reserved and free for this report);
`RT-20260729-036` occurs in exactly two places — the receipt that cites it and
the queue block recording the defect — **and nowhere else**. It is a *phantom*
identifier naming no report, which is a different and milder class than a
duplication. This is a grep, not `tools/allocate_id.py`; the allocator check is
`TASK-20260729-046`'s `D5`.

---

## 5. The five rulings asked for

**Premature closure.** *Not premature, and the derived null is sounder in kind
and weaker in warrant.* The closure standard of `docs/inventor-protocol.md` §4 —
named obstruction, argument, forward guidance — is met, and the ruling expressly
claims no closure of the lane. The controls-before-belief obligation of §3 is an
obligation on **believing a signal**, not on **producing one**; no signal exists
and none is believed, so standing down satisfies it. Reading it as compelling
execution inverts it. A derived null is *stronger* than a measured one on the
failure the protocol exists to prevent — it is universal over cells, seeds and
`B` and cannot be confounded by a nuisance variable, which is exactly what
`O-4` found in the measured null of arm E. It is *weaker* in that an error in
the argument is invisible, and this lineage has already shipped two wrong
arguments that passed review (`DEC-20260727-009`'s next-action phrasing; the
feasibility table's "F-5 CAN FIRE"). Resolution: **a derived null is an
admissible basis for not running if and only if every hypothesis it rests on is
checked, or declared conditional and cheaply checkable.** The amendment does
that for A-prime and not for E-prime; the repair is a declaration plus the probe
in §6, not 28 runs.

*Correlation.* Real and now smaller. Derivations #1, #2 and #3 share a
transcription channel; this report closes it for the row computation by deriving
from the primary file. What remains correlated is irreducible: **all five
derivations share the same reading of what a driver that does not exist will
do.** A sixth derivation will not reduce that, and neither will
`TASK-20260729-046`'s fourth. Only execution or an honest conditionality
declaration will.

**`reject_scoped`.** *Not available on `H-STR-002`*, on three grounds: §9 defines
it as valid evidence contradicting the exact tested prediction and there is no
evidence at all; `DEC-20260727-009` already forbade it on a strictly stronger
record; and, most importantly, the derivation **does not contradict the
prediction** — `alpha <= 2` *satisfies* the bound limb. What fails is the
comparative limb, against a null the derivation itself constructs.
Not-discriminating is not contradicted. *Not available on the narrow
diagnosticity proposition either*: the §9 labels attach to a hypothesis or
experiment, and there is no ledger object for it to attach to; and the strongest
archived artifact is a **derivation** (rank 2), never a counterexample
certificate. What *is* available is a **scoped narrowing recorded in the
decision**, with `proof_status: derivation`, both artifacts cited by path, both
limbs' conditionalities declared, and never `proved`.

**`DEC-20260727-009`'s prohibition.** *The ruling does not cross it; the
reserved `KN-FIND-010` sentence does.* `phi_alpha` names the quantity from the
as-committed pipeline, whose append block skips an emission when the shifted row
is all-zero or already present — and a skip desynchronises triple boundaries
from sigma-block boundaries, so `D-6`'s entire argument fails and the row
computation is simply unavailable. This is not a formal dodge: the filtered
version of arm E-prime **measured 29** where the unfiltered version is derived
`<= 1`. The two instruments demonstrably differ. The crossing occurs only in the
unqualified boundary sentence, which applied to `EV-STR-002`/`EV-STR-003` asserts
precisely the prohibited proposition — crossed by an omitted adverb.

**AGENTS.md rule 12.** *Does not fire on the `refine` decision*: redesigning an
experiment because a pre-data derivation shows the instrument cannot bear on the
claim is neither a breakthrough, a closure result, nor a contradiction of
established evidence. *It does fire* on (i) a `reject_scoped` on the narrow
diagnosticity proposition, which would settle in one direction a question
`DEC-20260727-009` committed as **open**, and (ii) promotion of the reserved
boundary sentence in its present general wording. `review-breakthrough` at `max`
is unavailable on this branch and may not be degraded, **so neither claim is
made** — not by this report, and it should not be by `DEC-20260729-004`.
`SUP-BATCH014-A` does not fire rule 12: correcting a phrasing in a decision's
next-action field, changing no measured number and no disposition, recorded as a
supersession and never an edit, is a correction.

**`O-1`'s scoping.** *Right in direction; over-reaching in one phrase and
under-reaching in one place.* It reaches `H-STR-002`'s first prediction and does
not reach the mechanism — both correct. **Over-reach:** "the asserted separation
does not exist" is a claim about the world; the derived claim is that the
separation is not exhibited by this instrument and its *sign* is set by a free
choice of null (§3). The comparison has no canonical referent — a stronger and
more accurate criticism than the ruling makes. **Under-reach:** it bears on the
cost claim's *input*. `H-STR-002`'s third prediction is
`alpha^2 * B * ceil(log2 B)`, and the committed harness computes exactly that,
plus a `cost_ratio` against `2*B^2`, at `endomorphism_la.py` lines 472-475. A
closure-determined alpha flowing into that formula manufactures a cost number.
`DEC-20260729-004` should say in terms: **no cost quantity is measured or
derived by this batch, and no alpha measured on a shift-closed row list may ever
be substituted into `H-STR-002`'s cost model.** Note also that the derivation
predicts `alpha = 0` at **seven of fourteen** cells, and `RT-CM-2` records that
the model returns cost **zero** at `alpha = 0`, masked by a `-1` sentinel at
line 472. Half the ladder sits in the model's degenerate region.

---

## 6. The successor experiment — right in shape, incomplete in three places

`S-1` (assemble a real system with right-hand sides; the unrepaired
`DEC-20260727-009` `R3`), `S-2` (use the `C_3` block decomposition directly
rather than measuring a rank), `S-4` (density honestly, quoting the whole
`EV-STR-001` range **17.5x to 4128.6x**, which grows with size and superlinearly
in `m`, and never 17.5x alone) and `S-5` (pre-register the ceiling at `r = 3`;
a constant is not target-class under rule A1) are all correct. `S-5` is the
single most important line in the amendment.

Three gaps:

1. **The baseline named in `S-3` is the wrong one.** Plain Pollard rho is not
   the closest specialized baseline for a curve with an order-3 automorphism.
   The published specialized baselines are rho **with** the automorphism
   (Wiener–Zuccherato; Duursma–Gaudry–Morain; Gallant–Lambert–Vanstone), taking
   `sqrt(3)` on the rho side, and the automorphism-quotient factor base taking
   `r = 3` on the index-calculus side. `S-5` names those authors for the LA
   ceiling and `S-3` fails to carry them into the baseline. A successor
   baselining against plain rho will credit `C_3` with a saving the specialized
   baseline already has. **Require a matched rho-with-automorphism baseline.**

2. **Memory is absent** from `S-1`…`S-5`. `RT-CM-4` is open: Wiedemann's whole
   point is `O(B)` memory at `O(B^2)` operations; the structured side needs a
   generator representation plus a transform; neither is costed. Add `S-6`:
   memory beside time on both sides, with a time–memory interpolation so a
   memory-constrained baseline can be checked for dominance.

3. **Total expected cost is not per-attempt cost.** Add `S-7`.
   `DEC-20260727-009` `R3` archives the phi arm's rank deficiency as 4, 6, 30,
   67 against the control's 0, 0, 0, 1. A rank-deficient block system needs more
   relations, so the success probability of one assembled system is below 1 and
   the honest quantity is per-attempt cost × inverse success probability.
   **Pre-register that the deficiency `d(B)` must be `o(B/3)` for the factor-3
   saving to survive at all, and measure `d(B)` along the ladder.**

**Is "no exhibited mechanism for the super-constant limb" fair?** Yes, and if
anything understated. The super-constant limb is a saving of
`B/(alpha^2 log B)`; exact `C_3` equivariance delivers three blocks of size
`B/3`, a factor of 3. `RT-CM-1` — open since BATCH-007 — names why nothing
connects them: `alpha^2 * B * log B` is the superfast-solver cost for a
**Toeplitz-like** matrix, whose displacement operator is the **nilpotent** lower
shift; here `Z` is a permutation of **order 3**, so small
`rank(M - Z M Z^{-1})` means near-`C_3`-equivariance, a different structure with
no superfast solver attached. That is also the real reason `S-2` is right: the
rank has no solver attached to it. And `RT-CM-3`, also open, measures relation
collection at **7.0x, 6.1x, 20.6x, 78.7x** the entire modelled linear algebra at
`B = 27, 55, 204, 397`, growing in `B` — so even a perfect factor-3 LA saving is
invisible at every size this lineage has reached. That stronger statement, not
the LA-only one, should be the successor's pre-registered ceiling.

One wording caution: "**has no exhibited mechanism**" is inside the ceiling
because it describes the record, but it is one word from crossing it. Write "no
mechanism for the super-constant limb has been exhibited in this lineage;
whether one exists is open and is asserted in neither direction."

---

## 7. Ceiling sweep

**Excesses found** (file and location):

- `dispatch_queue.json`, `QUEUE-AMEND-20260729-005` →
  `THE_RULING.what_experiment_COULD_actually_move_H_STR_002.S_5`: *"EXACT C_3
  EQUIVARIANCE BUYS AT MOST A FACTOR r = 3 — three blocks of size B/3 against
  Wiedemann's 2B squared"* is a cost statement and a Wiedemann comparison, both
  forbidden by `claim_ceiling` and `N-4`. **Admissible only as an attributed
  verbatim carry-forward of `DEC-20260727-009`'s third limitation and `R5`**,
  never as this batch's own arithmetic. (Note `RT-CM-1` states the ceiling
  against a *dense* baseline, `3*(B/3)^2 = B^2/3`, while `S_5` states it against
  Wiedemann's `2B^2`; both give factor 3 against their own baseline, and the
  successor must name which it means.)
- Same amendment → `knowledge_promotion.not_warranted`, the reserved boundary
  sentence: an unqualified general instrument claim which, applied to the
  as-committed pipeline, asserts the exact proposition `DEC-20260727-009`
  committed as open. See RT35-D3.
- Same amendment → `the_direction_level_consequence_stated_plainly_and_not_buried`:
  **not** an excess as written, flagged for wording only (§6).

**Clean:**

- **No quotation of 17.5x without its range exists anywhere in BATCH-014 or in
  `experiments/EXP-STR-004`.** Every occurrence carries the full range 17.5x to
  4128.6x with the growth qualifier — `contract_review.yaml` 771-772,
  `specification.yaml` 867-868, the queue's
  `EV-STR-001_yield_penalty_must_be_quoted_as_a_RANGE`, `C-4`, `S_4`, and both
  task cards. This report quotes only the range.
- No statement anywhere in BATCH-014 asserts that the ledger validates;
  `INT-BATCH012-F` is carried and `L-6` restates it. I ran no validator and
  assert nothing about validation.
- No statement about `B > 193` or `field_bits > 16` was found. The derivation's
  "at every `B` with `B mod 3` in {0, 1}" is an algebraic identity on a row list,
  not a measurement claim — but it deserves a qualifier in `DEC-20260729-004`,
  since a reader scanning for "every B" will not distinguish the two.
- No mechanism claim, no asymptotic or scaling claim, no cost-ratio,
  structured-cost, crossover or density-penalty claim in either committed
  receipt. No `C-20` power sentence anywhere.

**Cardinality-not-identity hunt** (including the Coordinator's own receipts and
commit messages, per RT31-5):

- `RT35-CNI-1` — `R-2`/`A-2`: a **bound-for-value substitution**, the nearest
  neighbour of the failure class.
- `RT35-CNI-2` — `SUP-BATCH014-C`: a count whose members are of **unlike kind**
  (a dangling reference grouped with two duplications).
- `RT35-CNI-3` — `F-2`: a two-limbed hazard read as one object and cleared on
  the limb that was measured.
- **None found** in the two committed snapshot receipts or the two commit
  subjects, which I swept specifically. Both subjects state counts matching
  their diffstats — three files at `7c9aa579`, two at `0cea73f9` — verified with
  `git show --stat`.

Counts re-checked against their stated terms: `16200` (nine named terms; and
`23700 - 7500 = 16200` with `7500 = 7200 + 300`) ✔; the seven-path declared set
✔; three named derivations ✔ *as a count*, with unequal independence; four
candidate statistics ✔ (I add four more); seven items in the case FOR ✔ (I add
four more); nine cards, seven performed, two stood down ✔.

---

## 8. Dissent, recorded plainly and unsoftened

**I dissent from the ruling's central reason while concurring in its
conclusion.** The reason given is that the arm with zero endomorphism content
satisfies the bound *more strongly*, so a criterion a null object satisfies
identically carries no information. At that generality it is wrong: it holds for
the positional-sigma null the contract chose and fails for the equally
constructible multiplicative null, under which the same arm has `alpha` about
`2B/3` and `H-STR-002`'s first prediction reads as **confirmed** with a large
separation. The correct reason is stronger and different: **alpha on a
closure-generated row list is a function of the closure convention in both arms,
the convention is a free parameter of the experiment, and it determines the sign
of the reported separation.** The conclusion survives the loss of its stated
reason.

**Second dissent:** the arm E-prime limb is not unconditional. It rests on a
base-row supply nothing has measured and on a driver nobody has written. `R-7`'s
concession is larger than `R-7` admits.

**Third dissent, recorded against myself:** if the probe in §9 finds that
`_build_phi_invariant_factor_base` returns a short list at `B = 192` or
`B = 193`, or a base-row shortfall of two or more at any cell, then the
derivation's hypotheses fail on committed code, the ruling's basis is defective
in substance and not only in wording, and executing becomes the right call. I am
recommending against 28 runs on the strength of an argument — the same species
of act I am reviewing.

---

## 9. Recommended transition and the single next action

**Pre-stated before the ruling sections were written, together with the checks
that neither `EV-STR-004` nor `DEC-20260729-004` existed at the head reviewed
(both absent at HEAD and in the working tree; `experiments/EXP-STR-004` contains
only `derivation_note.md` and `specification.yaml`; no `driver/`, `runs/` or
`results/`).** I also verified that `7c9aa579` and `0cea73f9` are commit objects
and ancestors of HEAD, with diffstats of three and two files respectively, and
that the derivation-note and contract-review blobs are **byte-identical** at
those commits and at HEAD (`c71ba196…`, `1b20ce00…`).

> **Recommended transition: `refine`. Exactly one label.**

Carried by a **derivation**, not a counterexample certificate:
`experiments/EXP-STR-004/derivation_note.md` at `7c9aa579`, together with §6.2
of `derivation_check.md` and objection `O-1` of `contract_review.yaml` under
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/reviews/TASK-20260729-042/`
at `0cea73f9`. Since `refine` is not stronger than `weaken`, the binding
constraint on `reject_scoped` is not engaged. Rejected alternatives: `support`
(nothing supports anything), `weaken` (no evidence exists; `H-STR-002` is
already `weakened`), `reject_scoped` (unavailable, three grounds),
`inconclusive` (understates — `R1`, `R2`, `R3` stand unretracted), `pause`
(misdescribes which design is exhausted), `replicate`/`expand` (no result to
replicate, no range to expand).

### Single next concrete action

**Dispatch `RT35-CTRL-1` and `RT35-CTRL-2` as one bounded supply-and-structure
probe:** build the phi-invariant factor base at `B = 192` and `B = 193` on
CURVE-J12S1 and assert `CTRL-4`'s two conditions (`len(F) == B` and
`F[3j+k] == pow(zeta3, k, p) * F[3j] % p` on every complete block); and collect
base rows at every declared cell in both arms, reporting only `len(relations)`
against `R_base(B)`. **No closure, no alpha, no driver, no ladder.** Seconds to
minutes of toy-scale curve compute — a rounding error against the 7500 released
seconds.

It resolves every fact about **committed** code that the ruling's derivation
assumes, leaving only driver fidelity, which is a software-test question and not
a research question. It is the only cheap artifact that could contradict the
ruling. And it converts the price the amendment concedes at `R-7` into a
discharged obligation.

It is a **successor-batch** action and is **not self-granted here**:
`campaign_budget.maximum_batches = 14` is consumed at this close and a fifteenth
batch requires explicit user authorization.

---

## 10. Not reached inside the cap

- `TASK-20260729-046`'s validation report and recount note — they did not exist
  at the head reviewed and nothing here depends on them. **If its fourth
  derivation disagrees with mine, that disagreement governs and this report
  should be re-read against it.**
- I ran no `tools/allocate_id.py`, `tools/validate_ledger.py`,
  `tools/research_dispatch.py` or `tools/check_merge_hygiene.py`, and assert
  nothing about their output.
- I did not re-derive any recorded path SHA-256 from Git blobs and did not audit
  either receipt's declared-versus-committed set arithmetic beyond the two
  diffstats above. That is `TASK-20260729-046`'s `D3` and is **not** reported
  here as passed.
- I did not read `EV-STR-001`, `EV-STR-002` or `EV-STR-003` in full; every
  number attributed to them comes from `ledger/decisions/DEC-20260727-009.yaml`
  or the BATCH-007 red-team report and is attributed there.
- I did not audit BATCH-013 or `RT-20260729-031` directly, so the "fifth" and
  "sixth" cardinality-instance counts are carried from other records and are not
  independently confirmed by me.

*Model independence is unavailable and is not claimed (`INT-BATCH014-D`);
session independence is asserted. This report is not durable until
`TASK-20260729-048` commits it and the post-commit verifier accepts the commit.
This session made no commit and staged nothing.*
