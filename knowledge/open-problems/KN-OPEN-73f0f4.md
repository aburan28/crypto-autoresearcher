---
id: KN-OPEN-73f0f4
type: open_problem
title: Does H-CREP-001's target quantity r_R have real degree Theta(B^2) from genuine multi-way elimination, or from non-deduplicated pair-product accounting?
tags: [ecdlp, h-crep-001, exp-crep-001, p1553, resultant, degree, bezout, elimination, deduplication]
confidence: unverified
status: open
source_refs: [KN-OPEN-7f424d, DEC-20260830-680f6d, DEC-20260830-6f28e0]
added: 2026-08-30
superseded_by: KN-OPEN-de67f0
---

## Statement

`KN-OPEN-7f424d` asked whether a decomposed, `g_I`-reduced combination rule
exists for a second deck pair (decks 2-3) in `H-CREP-001`'s complete-chart
intersection system, analogous to the existing decks-0/1 pair-product
generator. `TASK-20260830-789280` answered the toy-level part of that
question: **yes, a genuine construction exists** (`G01_local`, `G23_local`,
`Adm4`), independently hand-verified field-for-field against the actual
generated instances in `experiments/EXP-CREP-001/instances/generate_instances.py`.

But the construction cannot be routed through the frozen `EXP-CREP-001`
engine for two reasons, one certain and one now identified as the real
open bottleneck:

1. **Certain, engine-level (not the open question here):** `check_representation.py`'s
   `execute_package` hard-wires `load_pair_product_generators` to decks
   0/1 only, and every "online algebra kind" computes the identical global
   `support_of_target()` regardless of which kind is named — no node in
   this engine ever computes a decomposed intermediate. This blocks the
   frozen route set specifically and would recur for any deck pair; it is
   not itself in question.

2. **The genuinely open question, promoted here:** the local construction's
   correctness mechanism implies a natural degree scale of `O(B)`, while
   `r_R` is declared (at every layer of this corpus — package docstrings,
   route notes, `specification.yaml`'s forbidden-payload text, and the
   original 2026-07-22 problem statement itself,
   `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-101/candidate_report.yaml`)
   to have degree `Theta(B^2)`. Tracing this figure found it **stated
   identically at every layer and derived or computed nowhere** — it is a
   modeling declaration, not a result. The toy engine's own execution of
   the corresponding node produces a `Theta(B)` object, decoupled from the
   declared certificate by the module's own docstring.

## The open question, precisely

Does `r_R`'s real, non-toy `Theta(B^2)` degree reflect:

- **(A) Genuine multi-way Bezout-type elimination** between two
  independently-varying degree-`B` algebraic structures (in which case the
  `B^2` scale is real information content, and the local `O(B)`
  construction genuinely cannot reach it — supporting the obstruction), or
- **(B) Non-deduplicated accounting** over the `B^2` pair-product
  generators (in which case the *true* information content might be
  `O(B)` after all, and a decomposed construction achieving that scale is
  not ruled out by anything found so far)?

**Critically, the observed `Theta(B^2)` figure cannot discriminate between
(A) and (B) even in principle** — both predict the identical headline
number. Resolving this requires new mathematical derivation on the real
(non-toy) construction, not further reading of this corpus: is there an
independent way to check whether the `B^2`-sized object genuinely carries
`B^2` bits of non-redundant information, or whether it is expressible more
compactly?

## Why it matters

- **If (A):** the decks-0/1-and-2/3 obstruction genuinely extends toward a
  real structural claim about the complete-chart intersection system,
  strengthening (though still not completing) the case opened by
  `DEC-20260830-6f28e0`.
- **If (B):** the apparent obstruction is an artifact of how the frozen
  routes count information, not a real barrier — and a decomposed
  construction reaching the true `O(B)` content might exist after all,
  reopening the search for a genuine trigger.

## What would resolve this

A bounded, low-compute **mathematical derivation** task (not corpus
reading, not another toy-construction attempt) examining the real
elliptic-curve elimination underlying `r_R`'s construction directly: does
computing it via genuine resultant elimination between the relevant
degree-`B` polynomials/divisors actually require `B^2` independent
coefficients, or can the same information be extracted from `O(B)` of
them via a redundancy the frozen accounting doesn't currently exploit?
This is the concrete next action recorded in
`ledger/goals/GOAL-ECDLP-001/goal.yaml`'s `next_action` as of 2026-08-30.

## Provenance

- `coordination/goals/GOAL-ECDLP-001/proposals/B71-DECKS23-INTERLEAVED-COMBINATION-20260830-789280/tasks/TASK-20260830-789280/derivation-report.yaml` (kb — originating construction and disclosed degree-mismatch observation)
- `ledger/decisions/DEC-20260830-680f6d.yaml` (kb — independent verification, evidentiary correction, and this promotion)
- `ledger/decisions/DEC-20260830-6f28e0.yaml` (kb — the prior accepted finding this question extends)
- `knowledge/open-problems/KN-OPEN-7f424d.md` (kb — the original, now-superseded open question)
- `experiments/EXP-CREP-001/instances/generate_instances.py`, `experiments/EXP-CREP-001/verifier/check_representation.py`, `experiments/EXP-CREP-001/packages/build_packages.py`, `experiments/EXP-CREP-001/specification.yaml` (retrieved — directly opened and read by the archiving Coordinator)
- `coordination/goals/GOAL-CRYPTO-001/batches/BATCH-001/tasks/TASK-20260722-101/candidate_report.yaml` (retrieved — the original 2026-07-22 problem statement tracing the degree declaration to its source)
