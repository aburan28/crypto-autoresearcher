---
id: KN-FIND-ba1cc6
type: internal_finding
title: Semaev exceptional-target classification is exact and full-box saturation holds exhaustively at m=3,4 (replicated toy tier)
tags: [semaev, newton-polytope, exceptional-set, corner-coefficients, index-calculus, negative-gate, ecdlp, toy-scale]
confidence: replicated_empirical
evidence_level: toy_demonstration
source_refs: [BATCH-d5f70a, EV-CRYPTO-3374a2, DEC-20260908-f39f65]
internal_refs: [EV-CRYPTO-3374a2, DEC-20260908-f39f65, EV-CRYPTO-009, RUN-SEMAEV-002-a, RUN-SEMAEV-002-b, RUN-SEMAEV-002-c, RUN-SEMAEV-002-d]
review_chain_note: >-
  The adjudication and review records backing this finding are cited by
  path in the body (validator record index does not cover them):
  ledger/corrections/CORR-20260907-e65243.yaml,
  experiments/EXP-SEMAEV-002/reviews/RT-20260907-823b5e.yaml,
  experiments/EXP-SEMAEV-002/reviews/VAL-20260907-b16812.yaml, and the
  blind re-derivation at
  coordination/goals/GOAL-CRYPTO-001/batches/BATCH-d5f70a/reviews/TASK-20260908-0b434a/blind-rederivation.yaml.
proof_status: empirical_only
proof_refs: []
added: '2026-09-08'
superseded_by: null
---

## Finding

For the original target-sectioned Semaev polynomials f_{m,t} over F_p
(nonsingular short-Weierstrass curves under the frozen selection rule),
at every tested cell — m in {3,4}, p in {101,103,107,211} — exhaustive
computation confirms:

- Newt(f_{m,t}) = the full box [0, 2^(m-2)]^(m-1) for EVERY target t
  outside the exceptional set (corrected
  nonexceptional_full_box_fraction = 1.0 with exact counts 99/99,
  101/101, 105/105, 209/209 for m=3 and 98/98, 100/100, 104/104, 208/208
  for m=4).
- The observed exceptional set EQUALS the group-arithmetic prediction
  Exc_m(E) = {x([r]P_0) : 1 <= r <= m-1} exactly (|Exc| = m-1), and every
  exceptional target loses at least one box-corner coefficient.
- m=3 calibration identities hold in all four m=3 cells.

The load-bearing corrected metric is triangulated by four independent
derivations: the producer's runs, VAL's from-scratch reproduction, CORR's
post-fix re-derivation from committed raw bytes, and a blind
re-derivation (J4, TASK-20260908-0b434a) that read neither CORR nor the
producer's artifacts and matched cell-for-cell. Three independently
constructed mutation controls agree: the corrected formula decays to
98/99 on a synthetic misclassified cell; the ORIGINAL as-implemented
formula returns 1.0 there (a tautology defect — OBJ-5 — caught and
voided; never cite the original metric as confirmation).

## Significance

- Replicates the base cases of the IDEA-20260723-006 corner-coefficient
  induction and strengthens the scoped negative Newton/BKK gate of
  EV-CRYPTO-009 toward replicated toy tier: support-aware Semaev routes
  through the original sectioned formulation gain no polytope slack
  outside an exactly-classified O(m) exceptional set.
- Exception-only uniform-mask bridges receive no sub-rho credit
  (consistent with EV-CRYPTO-009). This is a negative-gate control, not
  an algorithm; no runtime is closed.

## Boundaries

- Toy tier only: m in {3,4}, small primes; nothing about m >= 5 or
  cryptographic scale. All-m remains open; the locked derivation behind
  EV-CRYPTO-009 is the only all-m argument (preliminary strength).
- Original target-sectioned canonical Semaev formulation only;
  unsectioned, coefficient-dependent lifted, Groebner, and non-Semaev
  routes are unaffected.
- Information content: the 8 cells collapse to fewer distinct curve
  shapes with constant m=4 corner targets; the replication strength rests
  on the four independent derivations, not on cell diversity.
