# Red Team review — EXP-FROB-91ee9c, round 2 (TASK-20260921-aac8e7, joint J-REDTEAM)

Claim under review: DEC-20260921-d5e997.yaml / EV-FROB-576872.yaml's J3
(clause (6)/(c)) and J4 (collision-count / PTM-2) findings on H-FROB-d93575,
decision `weaken`, strength `preliminary`. This is an interpretive audit, not
a re-verification of the arithmetic (owned independently by J-VALIDATOR in
the same task). Working blind from the validator's report per
TASK-20260921-aac8e7's blindness constraint: I have not read, and did not
request, any validator output.

Sources read: TASK-20260921-aac8e7.yaml (this handoff, in full);
agents/red-team.md; H-FROB-d93575.yaml (statement, mechanism, proof_search_map,
predictions, falsification_conditions); EXP-FROB-91ee9c/specification.yaml (in
full, in particular `metrics.primary`, `controls.C1-C8` verbatim,
`success_criterion`, `falsification_criterion`, `named_parameter_sets`);
EXP-FROB-91ee9c/analysis.md (both rounds, in full); EV-FROB-576872.yaml;
DEC-20260921-d5e997.yaml; DEC-20260914-d04668.yaml (original design/approval);
TASK-20260921-1dba2a.yaml (round 2's review_plan and coordinator_prior);
DEC-20260921-e81e25.yaml (the v2 amendment); EV-FROB-2fe225.yaml and
DEC-20260921-3678fc.yaml (round 1); and, beyond the handoff's reading list,
`experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/report.md` and
`.../implementation.py` (both explicitly named as available primary raw
evidence in the parent audit's inputs list) — read to check item 4's "hidden
assumption" question directly against the actual C2 construction, which
produced the round's most consequential new finding (Section 3 below).

---

## 1. Was clause (6) ever testable on a 2-achievable-partition cell — and is this a round-2 finding or a design-time scope gap?

**The m=1-forced-tie fact is real and its consequence is exactly as stated:**
`p_1 = |B_1|/(N-1)` for a single slot is a pure function of cardinality
(`metrics.primary`, verbatim), so C3 (cardinality EXACTLY matched by
`controls.C3`'s own design text) ties the object's m=1 ratio identically by
construction, and C4 ties it up to a constant scalar `(N'-1)/(N-1)` that
cancels in any max/min ratio — *provided* the finer partition's
`distinct_targets` also matches. On a cell with exactly two achievable
partitions, that leaves exactly one place C3/C4 could ever show a strictly
smaller spread: the single finer partition's collision count. This is not a
round-2 argument I have to take on faith — it follows deductively from
`metrics.primary`'s and `controls.C3`'s own frozen text, and I worked it the
same way independently before checking it against the round's own framing.

**But the two tested cells are sparse for two structurally different
reasons, and the record does not say so — this is itself worth flagging.**
`report.md` (`runs/TASK-20260921-51bc02/report.md`, §1) and
`EV-FROB-576872.yaml`'s own `boundaries` field both state: *"Only 2 of 15
achievable set-partitions are `ok` ... for either tested curve, in either
cell."* This is only true of FROB-SPLIT-q11n5. FROB-SPLIT-q11n5 has s=4
non-trivial atomic factors, so its abstract lattice really does have
Bell(4)=15 set-partitions (5 distinct dimension-multisets), of which this
specific curve instance realizes only 2 as non-empty — a fact about *this
curve's* generator, not about the cell. FROB-EQDEG-q19n5 has s=2 non-trivial
atomic factors (`specification.yaml`'s own
`named_parameter_sets.FROB-EQDEG-q19n5`: "Achievable multisets: (2,2) and
(4); m sweeps 1..2"), so its abstract lattice has Bell(2)=**2** set-partitions
total, full stop — there is no "15" to be a fraction of, and there is no
curve, generator, or seed choice that could ever raise it, because s=2 is
fixed by q mod n for this (q,n). Restating "2 of 15" for EQDEG is a factual
error carried from `report.md` into the evidence record's `boundaries` text,
and it matters beyond precision: it hides that EQDEG's two-partition ceiling
is a **permanent, cell-design fact**, while SPLIT's is a **contingent,
per-curve-instance fact** that a different curve or generator search inside
the same cell might not share.

**Answer to the question as posed:** clause (6), as originally specified,
was capable in principle of being tested on a richer cell (SPLIT's abstract
lattice has 5 distinct dimension-multisets and could in principle show more
than 2 `ok` configurations on a different curve instance), but **it was never
capable of carrying more than one bit of information on FROB-EQDEG-q19n5, on
any curve, by the cell's own definition, from the moment
DEC-20260914-d04668 selected it.** DEC-20260914-d04668's own
`cell_selection_rationale` picked q=19 specifically because "two EQUAL-DEGREE
factors ... the required several-equal-degree-factors cell, where the
partition lattice cannot be an artefact of degree-1 factors" — a good reason
for *that* diagnostic purpose — without ever connecting it to clause (6)'s
own requirement (ALL of C2, C3, C4 strictly smaller, in *every* completed
cell, including this one). s=2 is the smallest s that admits any non-trivial
partition at all (s=1 is the FROB-NOLATTICE-q13n5 null cell by design); the
approval checklist, the proof_search_map, and the optimistic-assumptions list
all discuss OA-1 through OA-6 and the algebraic-cost omission at length, but
none of them asks "how many bits of information can clause (6) actually
carry on this cell." **This is a scope critique of the original experiment
design (DEC-20260914-d04668, 2026-09-14), not of round 2's execution or
interpretation** — round 2 (via EV-FROB-576872's own `resource_check`) is in
fact the first place in this experiment's history that the limitation is
named at all, and I am sharpening, not originating, that reading: it should
distinguish the two cells' different reasons for sparsity rather than
reporting one shared "2 of 15" figure for both.

## 2. Is `weaken` the decision this data licenses, or does the mixed PTM-2 result argue for something else?

**(a) FROB-SPLIT-q11n5 alone already carries real weight, independent of what
happens on EQDEG.** On SPLIT, PTM-2(ii) does *not* fire (the smaller
construction, C2, collides *more* than the larger, zero-collision
object/C3/C4 construction — the opposite of a scale-artifact signature), and
C2 genuinely diverges from the object (smaller, not tied). C3 and C4 tie the
object exactly, on real non-degenerate data (spread ≈4.56, not round 1's
vacuous 1). Nothing in my review changes this cell's bottom line: clause (6)
fails there and falsification clause (c) fires there, on grounds that survive
scrutiny (subject to the scale/underpower point in §3 below, which weakens
*how much* the tie can prove, not *whether* it occurred).

**(b) FROB-EQDEG-q19n5's PTM-2(ii)-fired reading does not pull the overall
verdict back to `inconclusive`, because the two cells' findings are not one
pooled measurement — they are two independent tests of the same clause, each
individually sufficient to trigger falsification clause (c) on its own cell.**
`inconclusive` is reserved, by this experiment's own
`decision_branches.inconclusive` text, for "the exact eligibility, matching,
validity or infrastructure impediment" — none of which describes either
cell here: both completed, both are hash-bound, both were independently
recomputed and matched exactly (per J1/J2 in EV-FROB-576872). Calling this
`inconclusive` a second time, as the frozen decision text itself argues,
would mischaracterize what was actually measured. I agree with that
reasoning. Where I would correct the record's own narrative is that it treats
the two cells as contributing *symmetrically* to one blended "weaken,
preliminary" call ("a partial, cell-dependent proves-too-much complication
that prevents treating the trigger as cleanly, uniformly attributable to
Frobenius structure on both cells" — DEC-20260921-d5e997 rationale). The
honest asymmetry is: SPLIT's C3/C4 tie is the *solid* leg (PTM-2 clears it,
and — see §3 — its own underlying collision statistic is close to what a
uniform-random null model would already predict, which bounds its strength
without undermining its direction); EQDEG's contribution is the *heavily
qualified* leg, qualified by PTM-2(ii) firing on the C2 reading **and**, more
consequentially, by the C2-construction defect in §3 below, which removes
C2's contribution to EQDEG's falsification trigger almost entirely. This
asymmetry is exactly what `strength: preliminary` should be read as encoding,
and I would not read it as license to soften the decision itself.

**I therefore agree that `weaken` — not `inconclusive`, not `support`, not
`reject_scoped` — is the ceiling the combined evidence licenses**, for the
reasons the decision already gives (AGENTS.md's bar against `reject_scoped`
on a single unreplicated `empirical_only` run) plus the asymmetry above,
which if anything makes SPLIT's contribution to `weaken` *more* solid than
the record's own symmetric framing suggests, while EQDEG's contribution
should be read as thinner than the record credits it (see §3).

## 3. The cheapest additional check for FROB-EQDEG-q19n5's ambiguity — and it has already resolved part of it

Two checks, both analytic, both performable from already-committed artifacts
with no new run:

**(i) A null-model (birthday-collision) comparison — the control-before-belief
check this claim needs and does not have.** For a set of `k` ordered
tuple-sums landing uniformly at random among `M = N-1` targets, the expected
number of colliding pairs is approximately `k²/(2M)`. Applying this to the
*already-published* block products:

| cell | arm (finer partition) | product `k` | `M=N-1` | `k²/(2M)` (expected collisions under a uniform-random null) | observed |
|---|---|---|---|---|---|
| SPLIT | object/C3/C4 `[10,10]` | 100 | 10,060 | ≈0.50 | 0 |
| SPLIT | C2 `[6,6]` | 36 | 10,060 | ≈0.06 | 18 (of 36) |
| EQDEG | object/C3/C4 `[10,30]` | 300 | 117,990 | ≈0.38 | 0 |
| EQDEG | C2 `[24,24]` | 576 | 117,990 | ≈1.41 | 288 (of 576) |

The object/C3/C4 rows show **zero collisions is exactly what a
uniform-random object of the same cardinality would be expected to show** at
this scale (expected count already comfortably below 1 in both cells). This
is the null-object control my role's mandate asks for: the observed tie is
not merely *permitted* by the m=1-forced-tie algebra, it is *predicted* by
chance alone, which means the finer-partition comparison at these specific
block sizes has essentially no statistical power to distinguish "Frobenius
structure suppresses collisions" from "nothing distinguishes anything at this
product size" — a second, independent, and more general reason (beyond the
m=1-forced-tie argument) that clause (6) could not have given a strong signal
here, in either cell, regardless of which way the truth runs. This is cheap,
requires no tool access beyond arithmetic on numbers already in
`metrics.json`, and directly quantifies what EV-FROB-576872's own
`resource_check` gestures at without quantifying.

**(ii) Reading `implementation.py` directly resolves, right now, why C2
collides on both cells — and it is neither Frobenius structure nor scale.**
`specification.yaml`'s `controls.C2` design text says: "For each object slot
of dimension `d_j`, construct an F_q-subspace W ... Take the
lexicographically first such subspace." Read literally (a single,
dimension-only-dependent, deterministic selection rule with no per-slot
index), this licenses exactly what `runs/TASK-20260921-51bc02/implementation.py`
does: `non_stable_subspace_of_dim(d, ...)` is called **once per distinct
dimension appearing anywhere in the achievable partitions**
(`dims_present = sorted(set(d for r in obj_partitions ... for d in
r["slot_dims"]))`, lines 430-435), cached in `c2_by_dim`, and then re-used —
literally the same Python list object — for **every slot of that dimension**
in a partition (lines 459-466: `for d in r["slot_dims"]: block_ksets.append(
c2_by_dim[str(d)]["_ks"])`). The only non-trivial partition tested in either
cell is `[2,2]` — two slots of the *same* dimension — so C2's "two-slot"
factor base in both SPLIT and EQDEG is, in both cases, **the same size-`|B_W|`
set summed with itself**, not two independently chosen non-stable subspaces.
This is confirmed a second, independent way directly in the already-reported
numbers: `U_neg` for C2's `[2,2]` partition is `6/2=3` (SPLIT) and `24/2=12`
(EQDEG) — i.e. `B_union` equals the *single* block's own size (6, 24), not
the sum of two blocks' sizes as it is for the object (`U_neg=20/2=10` on
SPLIT's `[2,2]`, from two disjoint size-10 blocks) — which is only possible
if both "slots" are literally the same set. Summing a negation-closed set
with itself is subject to the swap symmetry `Q1+Q2 = Q2+Q1`, which forces
`distinct_targets ≤ (k²-k)/2 + k` where `k=|B_W|` — for SPLIT that bound is
`(36-6)/2+6 = 21` against an observed `18`; for EQDEG it is `(576-24)/2+24 =
300` against an observed `288` — in both cases the observed count sits close
to, and well under, the symmetry-forced ceiling, and nowhere near what the
null-model column above would predict for two *independently drawn*
same-size sets (0.06 and 1.41 expected pairs respectively, not a ~50% fold).
**This settles, cheaply and from artifacts already on disk, that C2's
collision pattern in both cells is an artifact of the control's own
literal-lexicographic-first construction colliding a slot dimension with
itself whenever a tested partition repeats a dimension — not a genuine
"dimension without stability" measurement, and not a scale effect either.**

This has a direct, load-bearing consequence for J3/J4 as recorded: round 2's
PTM-2(i) concludes "C2 diverges genuinely on both cells ... the instrument
still has discriminating power at this scale in general," and
DEC-20260921-d5e997 lists falsification clause (c) as triggered on
FROB-EQDEG-q19n5 "via the C3/C4 ties ... and additionally via C2." Both
statements treat C2's divergence as informative about the object under test.
Given the mechanism just identified, **C2's divergence in both cells is
better explained by its own construction defect than by anything about
Frobenius structure, cardinality, or scale**, which removes C2 as reliable
support for "the instrument retains general discriminating power" and
weakens (does not eliminate — C3/C4 independently and correctly trigger
clause (c) with no dependency on C2) the "additionally via C2" component of
EQDEG's falsification-trigger attribution. C4 is not affected: it is built
from `controls.C4`'s "matched to the object's `|B_j|` by the C3 construction"
text, and `random_matched_subset` draws independently per slot (fresh
`rng.sample` call per iteration) — confirmed both by reading the function and
by the reported numbers (`U_neg=20/2=10` on C4's SPLIT `[2,2]`, from two
distinct size-10 blocks, not one size-10 block reused).

**The cheapest concrete fix, if this control is used again:** require C2's
subspace search to select a distinct witness per slot whenever a partition
repeats a dimension (e.g., "the `i`-th lexicographically-first non-stable
subspace of dimension `d`, for the `i`-th slot of that dimension in the
partition, distinct from every subspace already assigned in the same
partition") — an additive, narrowly-scoped protocol amendment, not a new
experiment.

## 4. Hidden assumptions in the C2/C3/C4 designs themselves (not merely this round's application)

- **C2 (addressed fully in §3):** the design text's singular "Take the
  lexicographically first such subspace" is the root cause, not merely an
  implementation choice — a construction keyed only on dimension silently
  assumes no partition will ever repeat a dimension. Every partition either
  cell can test beyond m=1 is exactly `[2,2]` (a repeated dimension), so this
  assumption fails on the *only* data clause (6) had to work with.
- **C4's `(N'-1)/(N-1)` cancellation is a second, previously undisclosed
  instance of the same limitation already named for C3.** `controls.C4`'s
  `claim_limit` (frozen at design time, DEC-20260914-d04668) discusses only
  *causal attribution* of a difference ("a difference is attributable to
  'not a subfield curve' ... No single control here isolates Frobenius
  causality"). It does not disclose — and, as far as this experiment's
  history shows, no round noticed until round 2's Section 0 — that the
  `spread` *ratio* itself is mathematically incapable of differing from the
  object's at all whenever `distinct_targets` matches on both endpoints,
  regardless of `N'` versus `N`, because the `(N'-1)/(N-1)` factor cancels
  exactly in a max/min ratio. This is a property of the metric and the C4
  construction as jointly specified, not of round 2's data, and it belongs
  in `controls.C4`'s own `claim_limit` text going forward.
- **C3 has no comparable hidden defect beyond the already-disclosed,
  by-design cardinality match.** Its `random_matched_subset` draws
  independently per slot (verified directly against `implementation.py`),
  so its tie is a genuine (if statistically underpowered, per §3(i))
  measurement, not a construction artifact.

## Objections, controls, and scope (summary)

- **Objection 1 (scope, not execution):** clause (6) could never carry more
  than one bit of information on FROB-EQDEG-q19n5, for any curve, because
  s=2 caps its abstract partition lattice at Bell(2)=2 — a fact fixed by
  DEC-20260914-d04668's cell selection, not discovered by round 2's
  execution.
- **Objection 2 (record accuracy):** "2 of 15 ... for either tested curve, in
  either cell" (`report.md`, `EV-FROB-576872.yaml` boundaries) misdescribes
  FROB-EQDEG-q19n5, which has no 15-element lattice to be a fraction of.
- **Objection 3 (interpretive defect, load-bearing):** PTM-2(i)'s "C2
  diverges genuinely ... the instrument retains general discriminating
  power" and DEC-20260921-d5e997's "additionally via C2" attribution of
  EQDEG's falsification trigger both rest on treating C2's divergence as
  informative; it is explainable, from `implementation.py` alone, as an
  artifact of reusing one non-stable subspace across same-dimension slots.
- **Required control (already run, above):** the birthday/null-model
  comparison in §3(i) is the null-object control this clause never had; it
  shows the observed zero-collision ties are what chance alone predicts at
  these block-product sizes.
- **Counterexample/mutation proposed:** a corrected C2 with per-slot-distinct
  subspace selection (§3, "cheapest concrete fix") would let a future run
  distinguish a genuine dimension-only effect from this artifact cheaply,
  without a new experiment.
- **Baseline comparison:** not applicable beyond what specification.yaml
  already scopes — this experiment prices the combinatorial half only, no
  Pollard-rho/BSGS/specialized-baseline comparison is claimed or owed here,
  and nothing in this review changes that scope.
- **Narrowest supported statement:** on the two tested (cell, curve) pairs,
  success_criterion clause (6) is not met and falsification_criterion clause
  (c) is triggered via the C3/C4 ties in both cells (robust, unaffected by
  anything in this review) and, on FROB-EQDEG-q19n5, was also reported as
  triggered via C2 (not robust — better explained by a C2 construction
  artifact than by the object). The `weaken`/`preliminary` decision correctly
  reflects an aggregate of one solid finding (SPLIT) and one more heavily
  qualified finding (EQDEG), though the record states this less precisely
  than the underlying evidence supports.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260921-aac8e7
  joints_owned: [J-REDTEAM]
  role: red-team
  paths_read:
    - ledger/handoffs/TASK-20260921-aac8e7.yaml
    - agents/red-team.md
    - ledger/hypotheses/H-FROB-d93575.yaml
    - experiments/EXP-FROB-91ee9c/specification.yaml
    - experiments/EXP-FROB-91ee9c/analysis.md
    - ledger/evidence/EV-FROB-576872.yaml
    - ledger/decisions/DEC-20260921-d5e997.yaml
    - ledger/decisions/DEC-20260914-d04668.yaml
    - ledger/handoffs/TASK-20260921-1dba2a.yaml
    - experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml
    - ledger/evidence/EV-FROB-2fe225.yaml
    - ledger/decisions/DEC-20260921-3678fc.yaml
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/report.md
    - experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/implementation.py
  read_sibling_reports: false
  blindness_honoured: true
  did_not_edit:
    - specification.yaml
    - any file under runs/TASK-20260914-7119f2/ or runs/TASK-20260921-51bc02/
    - EV-FROB-576872.yaml
    - DEC-20260921-d5e997.yaml
    - H-FROB-d93575.yaml
  verdict: FINDS_A_DEFECT_NO_DECISION_CHANGE
```

## Verdict

**FINDS A DEFECT.** Two concrete defects, neither of which changes
DEC-20260921-d5e997's `weaken` decision or its `preliminary` strength (both
remain correct, and if anything are better-supported by the asymmetric
SPLIT/EQDEG reading in §2 than by the record's own symmetric framing):

1. A factual imprecision in `report.md` and `EV-FROB-576872.yaml`'s
   `boundaries` field ("2 of 15 ... for either tested curve, in either
   cell"), which does not describe FROB-EQDEG-q19n5 (whose abstract lattice
   has exactly 2 set-partitions total, not 15) and which obscures that
   EQDEG's sparsity is a permanent, cell-design fact while SPLIT's is a
   contingent, per-curve fact — a distinction that matters for any follow-up
   (a curve/generator search can plausibly enrich SPLIT's lattice; it cannot
   touch EQDEG's).
2. A construction defect in control C2 (traced to `specification.yaml`'s own
   singular "Take the lexicographically first such subspace" text, and
   confirmed directly in `implementation.py`'s per-dimension, not per-slot,
   subspace cache), which causes C2 to sum one non-stable subspace with
   itself on the only partition either cell could test, producing a
   swap-symmetry collision unrelated to Frobenius structure, cardinality, or
   scale. This specifically undermines round 2's PTM-2(i) conclusion ("the
   instrument retains general discriminating power" via C2) and
   DEC-20260921-d5e997's "additionally via C2" attribution of
   FROB-EQDEG-q19n5's falsification trigger — that attribution should be
   corrected or dropped, leaving the C3/C4 ties (robust, unaffected by this
   finding) as the sole basis for the trigger in both cells.

Beyond these, I confirm — independently, via the null-model comparison in
§3(i), which the record does not perform — that the observed C3/C4
zero-collision ties are exactly what a uniform-random object of the same
cardinality would be expected to show at these block-product sizes. This
sharpens, without contradicting, EV-FROB-576872's own `resource_check`
reading: clause (6) was statistically underpowered on both tested cells by
construction, independent of whichever way the underlying Frobenius-vs-
cardinality question actually resolves. Concrete next action: a corrected C2
(per-slot-distinct subspace selection, §3) is the cheapest way to make C2's
contribution trustworthy again; separately, and only for
FROB-EQDEG-q19n5's structural ceiling specifically, no curve search inside
that cell can ever exceed 2 achievable partitions — completing the
already-designed, already-probed FROB-EXT-q13n7 extension cell (s=3,
Bell(3)=5, currently `not_run_resource` under SR-4) is the cheapest route to
a genuinely richer lattice for the "several equal-degree factors" diagnostic
this hypothesis wants; EV-FROB-576872's own resource_check option
(a redesigned statistic) remains open and is not addressed by either of
these.
