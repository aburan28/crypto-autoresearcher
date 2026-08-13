---
id: KN-FIND-7d098b
type: internal_finding
title: "Certified exactly non-constant on the fibre, even under exact arithmetic, carries no information about whether an object reads the instance"
tags: [dispersion-criterion, admissibility-gate, a-1, am-18, fibre-condition, precision-invariance, null-object, exact-arithmetic, p-gram, instrument-design, pre-registration, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_two_independently_built_objects_in_two_review_sessions_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-6b6e78, TASK-20260813-25cb95, TASK-20260813-2ce014, TASK-20260813-59c321, TASK-20260813-85e343]
internal_refs: [EV-MLKEM-4ba196, DEC-20260813-c60bba, DEC-20260812-781961]
sibling_findings_narrowed: [KN-FIND-9d44b4]
sibling_findings_note: "`internal_refs` carries LEDGER records only, matching the shape KN-FIND-9d44b4 itself uses. The sibling finding this entry narrows is named here and throughout the body; it is not edited and its `superseded_by` is not set."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-59c321/probes/probe_own_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-59c321/probes/probe_own_null_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_pgram_reach.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-59c321/validation_report.yaml
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-59c321/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/red_team_report.md
added: '2026-08-13'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured at
`q = 3329` on the frozen lattice/basis grid this campaign has used throughout, no
reduction above `d = 40`, `numpy 2.4.6` on one 4-core Linux host. No number here
transports to any deployment parameter set by extrapolation, analogy, or any other
route. There is no cryptographic baseline, so `dominated_by` and `sota_delta` are
**not applicable for that reason** and not by omission.

**THIS ENTRY MAKES NO ADMISSIBILITY CLAIM ABOUT ANY OBSERVABLE IN EITHER DIRECTION**
and asserts nothing about `BATCH-6b6e78`'s own headline count, which is separately
qualified (see "Scope and limits" §3 below — it does not bear on this finding).

The finding, in one sentence:

> "Certified exactly non-constant on the fibre" — even under **exact arithmetic**,
> even at a precision-invariance ratio far inside its declared tolerance window —
> **cannot separate an object that reads the instance from one that reads nothing of
> it at all**, because two structurally different information-free objects satisfy
> the certified class on exactly the same terms a real geometric observable would.

## 1. Why this entry exists, and what it narrows

`KN-FIND-9d44b4` §4 records that a fibre-constancy test **evaluated exactly requires
a scale**, and names "what remains open" as whether a scale exists that separates a
null object from a real one **without being calibrated on them** — closing with "the
measured separation is genuinely wide" and "nobody in this campaign has tried that."

`BATCH-6b6e78` tried it. `PREREG-2`'s `A-1.3` sub-clause is exactly that scale: a
precision-invariance ratio at exact arithmetic, declared **before** any measurement,
with a window `[1/2, 2]` that is not calibrated on any candidate scored against it.
This entry narrows `KN-FIND-9d44b4` in one place, **by reference**:

1. **The scale that was tried does not separate them either — for a different
   reason than the float case.** `KN-FIND-9d44b4` showed the float-evaluated test
   fails because machine epsilon makes every real object non-constant. This entry
   shows the **exact**-evaluated, precision-invariant test fails on the **same
   axis** — not because of rounding, but because the class of objects certified
   `A-1.3`-non-constant in this batch contained **no object that reads the
   instance**, and two objects that provably do not were admitted to it
   indistinguishably from one that would.

`KN-FIND-9d44b4` is immutable and is **not edited**; its `superseded_by` stays
`null`. This entry inherits its narrowing of `KN-FIND-4b8d73` and `KN-FIND-2a35aa`.
The adjudication is `DEC-20260813-c60bba`; the evidence is `EV-MLKEM-4ba196`.

## 2. What was measured

`PREREG-2`'s `A-1` names five falsifiers, independently sufficient. `A-1.2`
(consistency) fired on the **certified-CONSTANT** class, at 153 cells, on real
candidates from this goal's own list (`X_null`, `rdet`, `X_parfree`) — that half of
`A-1` is falsified on real objects and is not this entry's subject.

`A-1.3` (invariance) fired at 868 (`FC-3a`) and 354 (`FC-3b`) cells — **exclusively**
on the null object `X_hash`, which `PREREG-2` §2.8 itself declares carries "no
lattice information whatever." `X_gso_k`, the **only** in-scope candidate that reads
the instance, was **UNCERTIFIED**: `P-GRAM` failed because the two committed
float64 routes it must reconcile disagree by up to `3.0e-9` at five of ten lattices
— more than the triangle inequality allows any real number to satisfy the frozen
`1e-10` tolerance, not merely more than any exact route can reach. That removal is
what emptied `A-1.3`'s certified class of the one real candidate that could have
given it empirical content on an object that matters.

| what | measured |
|---|---|
| `A-1.3` firings (`FC-3a` + `FC-3b`) | 1,222, **all** on the null object `X_hash` |
| the one in-scope real-reading candidate (`X_gso_k`) | UNCERTIFIED — removed by `P-GRAM`'s unreachable tolerance, not by any property of `A-1.3` |
| consequence | `A-1.3` was tested this batch **without a single certified real object to test it against** |

## 3. The two independently built counterexamples

Both reviews, without visibility into each other's write scope, **built** an object
certified `A-1.3`-non-constant that reads no lattice content — not proposed,
executed and recorded:

- **The Validator's `X_indexnoise`** — a fixed pseudorandom function of the **basis
  index alone**. It reads no entry of any basis, not even a hash of one. Certified
  non-constant by the exact route; scores **identically**, cell for cell, to
  `X_rowsum`, a blind null that *does* read `A` (Validator CC-2, CC-3): 114 `FC-3a`
  firings, 92 `VAR-F` verdict changes, on both.
- **The Red Team's `X_lin` and `X_par`** — a linear functional (`mean(A)/q`) and a
  counting functional (fraction of even entries of `A`), neither a hash. Both
  **certified exactly non-constant at 30 of 30 fibres**; precision-invariance ratio
  `[0.999997517, 1.000003717]` and `[0.999998595, 1.000000653]` respectively — **0 of
  30 cells** outside the frozen `[1/2, 2]` window, so neither `FC-3a` nor `FC-3b`
  would fire on either object. **Provably not lattice invariants**: an integral
  unimodular row operation that leaves the generated lattice identical moves both by
  a fixed, measured amount, and each carries a median Pearson correlation to the one
  in-scope geometric observable `X_gso_k` of `-0.0045` (`X_lin`) and `-0.0178`
  (`X_par`) — against a must-pass control (two float routes for the same geometric
  quantity) of exactly `+1.0000`.

Two structurally different constructions — one reading nothing, two reading `A` but
proven uncorrelated with the lattice geometry — land in the same certified class a
real observable would, on exactly the same terms.

## 4. What this compounds with, and what it does not

**It compounds with `OBJ-1`** (`EV-MLKEM-4ba196.obj_1_ruling`): the tolerance defect
that made `X_gso_k` uncertified is a `PREREG-2 2.9` specification gap, not evidence
against its derivation, which both reviews independently verified correct over exact
rational arithmetic. A successor that repairs the tolerance would recover the one
candidate that could give `A-1.3` empirical content on a real object — **that,
rather than a new dispersion statistic, is what the numbers point at.**

**It does not say `A-1` is false in general.** `A-1.2` is falsified on real
candidates independently of this finding. It says specifically that `A-1.3`'s
sub-clause was never tested this batch where it would matter — on an object that
both reads the instance **and** is certified.

**It does not bear on `BATCH-6b6e78`'s headline count.** The 1,416-cell precision
count is separately qualified as not-yet-admissible (`EV-MLKEM-4ba196` finding F-1);
this finding is invariant under both readings of that ambiguity and does not depend
on it.

## 5. What a successor must do, and what it must not

1. **Repair `P-GRAM`'s tolerance before any successor certifies `X_gso_k`.** The
   defect is in the frozen `1e-10` bound, not in the derivation it tests; a
   superseding pre-registration states the bound in a form the two committed float64
   routes can jointly satisfy, or states explicitly why none is chosen.
2. **A certified-non-constant class needs a positive test, not only a negative
   one.** Nothing in `A-1.3` as frozen requires a candidate admitted to the
   non-constant class to demonstrate correlation with the underlying lattice
   geometry; `X_indexnoise`, `X_lin` and `X_par` show the class as specified
   contains no such requirement, exact arithmetic or not.
3. **This is a specification requirement, not a lane closure.** It retires nothing
   and forbids no direction of inquiry; it is the same discipline `AM-18`'s first
   clause already established for the float case, extended to the exact case.

## 6. Scope and limits — read before citing

1. **THE FINDING IS REACHED BY TWO INDEPENDENTLY BUILT OBJECTS, NOT ONE.**
   `X_indexnoise` and (`X_lin`, `X_par`) were constructed by different sessions
   without visibility into each other's write scope, using structurally different
   constructions (index-only functional vs. non-digest linear/counting functionals),
   and reach the same conclusion. Each is otherwise `n = 1` and must be cited as
   such.
2. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL
   EITHER.** AGENTS.md rule 12 is **UNMET AND UNWAIVED**. Both reviews ran on the
   SAME model and the SAME host as the producer, confirmed by the Validator itself.
   **Nothing in this entry may be cited as model-level or environmental
   corroboration.**
3. **THIS DOES NOT BEAR ON `BATCH-6b6e78`'s OWN VALIDATOR VERDICT.** That verdict is
   `incomplete`, not `passed` (`EV-MLKEM-4ba196`); the two open corrections (RC-1,
   RC-2) are about the headline precision count and a narrative disclosure, both
   unrelated fields — this finding is invariant under either resolution.
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** §5 names what a successor must add;
   it does not claim no scale can ever separate the classes, only that none in force
   this batch did.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** That an integral unimodular row
   operation moves a non-lattice-invariant functional by a measured, nonzero amount
   is elementary; the rest are built counterexamples, each reported with its exact
   count.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** `BATCH-6b6e78` adjudicates no
   proposition about a lattice, revalidates no prior batch, retires no prior
   amendment, and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-7d098b` was drawn **without scanning state** (AGENTS.md rule 14) and then
confirmed in **two scopes** by the dispatching session at the Coordinator's request:
worktree `tools/allocate_id.py --check` (well-formed, 0 occurrences across 6,498
identifier-bearing paths) **and** a cross-ref sweep of the 25 most-recently-updated
remote branches (0 hits), plus confirmation that it is not tracked under
`knowledge/findings/` on `origin/main`. Recorded as two-scope confirmed and **never**
as `--check` alone — `--check` answers from the working tree only, which is how the
same tool once reported two identifiers "free" while both were already bound on a
pushed branch. **A passing `--check` is necessary and not sufficient.** The
Coordinator that specified this entry's content held no shell and claimed neither
check as its own; both were performed by the dispatching harness session.

## Superseding relationship

This entry **narrows** `knowledge/findings/KN-FIND-9d44b4.md` in the one place
listed in §1 and inherits its narrowing of `KN-FIND-4b8d73.md` and
`KN-FIND-2a35aa.md`. **No prior entry is edited and no `superseded_by` is set**:
each remains correct on what it measured, and each is extended rather than
corrected. A reader arriving at any prior entry first is not pointed forward to
this one; that is an accepted consequence of immutability, and the links exist here
and in `DEC-20260813-c60bba.knowledge_promotion`.
