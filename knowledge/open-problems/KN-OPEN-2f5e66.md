---
id: KN-OPEN-2f5e66
type: open_problem
title: H-CREP-001's z_R construction-cost ceiling broadens to the recursive meet-in-the-middle method class; Wagner-style generalized-birthday closed as a named sub-avenue; still over cap
tags: [ecdlp, h-crep-001, exp-crep-001, resultant, semaev, meet-in-the-middle, wagner-k-tree, construction-cost, obj-5]
confidence: unverified
status: open
source_refs: [KN-OPEN-f008ae, DEC-20260831-054c31]
added: 2026-08-31
superseded_by: null
---

## Statement

`TASK-20260831-cdecb2` (idea-generator), independently reviewed by
`TASK-20260831-0cbeca` (coordinator), investigated `KN-OPEN-f008ae`'s
residual question directly: does ANY construction for `z_R = gcd(g_I, r_R)`
-- distinct from the flat two-list meet-in-the-middle method already
ceiling-derived in `TASK-20260830-53a818` -- reach `H-CREP-001`'s declared
exponent caps? Two results, both genuinely derived and independently
verified, neither closing the top-level question:

1. **Recursive meet-in-the-middle method-class ceiling.** Six decompositions
   (flat two-list, sequential tree, direct-S5, a three-hop partial
   elimination, and two four-hop full-elimination variants) were derived by
   hand. All either exactly reproduce `Theta(B^3)` (two-pairs) / `Theta(B^2)`
   (one-pair) or land strictly worse (one four-hop GCD variant, after a
   disclosed and corrected mid-derivation arithmetic error, costs
   `Theta(B^4)`). This broadens the prior round's single-method ceiling into
   a ceiling for the **method class** of fixed-degree-relation,
   point-test-via-analytic-inversion constructions -- scoped explicitly to
   GENERIC decks (`H-CREP-001`'s own cost-model assumption) and to the
   enumerated family, not to every conceivable recursive decomposition.

2. **Wagner-style generalized-birthday: closed as a named sub-avenue.** No
   construction of Wagner's k-list-tree shape (exact coordinate-quotient
   split, or the known `Z_p`/interval-based near-collision generalization)
   can accelerate the z_R support-finding computation, via two independent,
   stacked legs: (i) Semaev's `S_3`/`S_5` relation is provably not
   additively separable (a direct degree argument: additive separability
   would force degree <= 1 in each variable given the others fixed, but
   `S_3`/`S_5` have degree exactly 2 / 2^(n-2) >= 2, confirmed against
   `KN-TECH-002.md`); (ii) the exact-quotient-homomorphism special case is
   independently blocked because both `F_p`'s additive group and the
   curve's order-`N` subgroup are of PRIME order, hence simple, hence admit
   no nontrivial surjective homomorphism onto any smaller group -- the same
   mechanism `KN-FIND-ffe1df`'s Theorem C establishes for `E(F_p)`
   (independently Validator-confirmed, `VAL-20260803-3b7c1a`), and the same
   mechanism (reason (i) only, not reasons (ii)/(iii)) that the round-10
   P1553 mixed-radix closure established for `N` specifically as a group.
   This is a narrow, named-sub-avenue closure per the inventor protocol's
   closure standard, **not** a claim that no construction of any shape can
   reach cap.

**Both bounds still exceed `H-CREP-001`'s declared
`fresh_target_online_exponent_cap_in_B: 1.25`.** No impossibility is
claimed for the z_R construction-cost question in general; disposition is
`no_construction_found_inconclusive`.

## What is now foreclosed, precisely

- Re-attempting the flat OR any of the six enumerated recursive
  meet-in-the-middle decompositions against the current `S_3`/`S_5`-based
  formulation, absent a genuinely new structural ingredient. Their combined
  ceiling is derived in `TASK-20260830-53a818`'s and `TASK-20260831-cdecb2`'s
  `proof-search-map.yaml` files.
- Re-attempting a Wagner-style generalized-birthday construction (exact or
  interval-based coordinate-splitting filter) against the joint relation as
  currently formulated in `H-CREP-001`'s mechanism and the
  `rcrep-candidate-definition.yaml` construction, absent a reformulation
  that removes leg (i) above.

## What remains open, precisely

- Any construction outside both families examined (recursive
  fixed-degree-relation meet-in-the-middle, and Wagner-style
  coordinate-splitting) is untouched by this round's findings.
- A future reformulation of the joint pair-pair relation into an additively
  separable form would remove the Wagner closure's leg (i) and reopen that
  sub-avenue. Not proven impossible here; the relation encodes genuine
  elliptic-curve chord-tangent addition, which is the source of the
  non-additivity, so this is judged unlikely but not foreclosed.
- A non-generic deck configuration (the flagged, unexploited `PRE-3-new`
  possibility named in `TASK-20260831-cdecb2`'s `derivation-report.yaml`
  `honest_limitations` item 6) that provably shrinks a pair-deck's degree
  below `Theta(B^2)` would fall outside the recursive-MITM class-ceiling's
  genericity assumption and would need separate analysis.

## What would resolve this

A genuinely new structural idea outside both examined families (e.g. an
additively-separable reformulation of the joint relation, or a non-generic
deck family with a smaller pair-deck), or a genuine derived lower-bound
argument covering constructions beyond these two families, with its own
correctly-executed proves-too-much control.

## Citation-precision notes (do not repeat uncritically)

- The round-10 mixed-radix closure transfers to this leg only via its
  reason (i) (prime order forecloses a CRT decomposition); reasons (ii) and
  (iii) concerned a different object (the scalar exponent's mixed-radix
  digit recurrence) and do not transfer. Citing "round 10 already closed
  Wagner-style attacks on `N`" without this reason-by-reason scoping
  overstates what round 10 found.
- `KN-FIND-ffe1df.md` is internally in tension about its own review status:
  one section names a specific Validator verdict for Theorem C
  (`VAL-20260803-3b7c1a`); a later section states no Validator or Red Team
  pass exists on any of its documents. The second statement concerns the
  four-gate asymptotic-complexity promotion process, not the Theorem C
  verdict specifically -- but a future citer should read both sections
  before repeating "Theorem C, independently Validator-confirmed" as if the
  whole entry were reviewed.

## Provenance

- `knowledge/open-problems/KN-OPEN-f008ae.md` (kb — the superseded, narrower framing before this round)
- `ledger/decisions/DEC-20260831-054c31.yaml` (kb — this round's independent verification and closeout)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-ZR-NEW-CONSTRUCTION-20260831-cdecb2/tasks/TASK-20260831-cdecb2/derivation-report.yaml`, `outcome-card.yaml`, `proof-search-map.yaml` (kb — the six recursive-MITM variants, the Wagner closure, and their audits)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-ZR-NEW-CONSTRUCTION-20260831-cdecb2/tasks/TASK-20260831-0cbeca/coordinator-review.yaml` (kb — independent verification of every load-bearing claim)
- `knowledge/findings/KN-FIND-ffe1df.md` (internal — Theorem C, the prime-order-quotient obstruction for `E(F_p)`)
- `knowledge/techniques/KN-TECH-002.md` (kb — Semaev `S_3`'s fixed degree-2 fact and general `S_n` degree formula)
- `ledger/hypotheses/H-CREP-001.yaml`, `experiments/EXP-CREP-001/specification.yaml` (retrieved — the frozen cap language, unchanged)
