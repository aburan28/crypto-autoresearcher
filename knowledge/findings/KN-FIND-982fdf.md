---
id: KN-FIND-982fdf
type: internal_finding
title: C_t-minimality theorem — the threshold oracle is the minimal non-simulable order-based factor-base identifier
tags: [oracle-minimality, generic-group-model, threshold-oracle, semaev, index-calculus, proved]
confidence: proved
evidence_level: theorem
source_refs: [BATCH-122, BATCH-123, TASK-20260805-008, TASK-20260805-011]
internal_refs: [DEC-20260805-661790, DEC-20260805-48b52e, DEC-20260805-d4b182]
proof_status: derivation
proof_refs:
  - knowledge/findings/KN-FIND-982fdf.md
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-122/tasks/TASK-20260805-008/ct_minimality_lemma.md
review_refs:
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-123/tasks/TASK-20260805-011/review_ct_minimality.md
added: '2026-08-05'
superseded_by: null
---

## Theorem (C_t-minimality)

**C_t-minimality theorem.** Let E/F_p, N prime, G a generator, t in F_p with the
non-degeneracy condition ∅ != F_t != E(F_p) (F_t = {P : x(P) < t}). Then, for
the threshold-factor-base membership identification task (one bit per point):

(a) **Identification.** C_t(P) = [x(P) < t] identifies F_t with exactly one
query per point.

(b) **Non-simulability (Tier 3).** C_t is not GGM-simulable; it is
encoding-dependent and publicly computable. Non-simulability witness (same
curve, two secrets): if F_t is neither empty nor full there exist k1, k2 with
x([k1]G) < t <= x([k2]G); the instances (E,G,[k1]G) and (E,G,[k2]G) are
GGM-indistinguishable yet C_t agrees differently.

(c) **Query-cost minimality.** Any oracle identifying F_t transmits at least one
bit per point; C_t transmits exactly one.

(d) **Uniqueness in the order-based class.** Up to bit complement, C_t is the
unique order-based oracle identifying F_t.

(e) **No strictly weaker order-based identifier.** Under the pointwise
information order, the only strict predecessors of any non-constant 1-bit
oracle are the two constant oracles; no constant identifies a non-trivial F_t.
Thresholds at distinct effective cuts are incomparable (an antichain).

**Corollary.** C_t is the minimal non-simulable order-based oracle enabling
threshold factor-base membership identification: minimal in query cost (c),
unique up to complement in the order-based class (d), with no strictly weaker
order-based identifier (e).

## Proof, in brief

Lemma (a): from definitions; the membership test is the query itself.
Lemma (b): the random-label indistinguishability of the two same-curve
instances plus the non-degeneracy witnesses; public computability from the
concrete model (no k required). Boundary: if F_t ∈ {∅, E(F_p)} then C_t is
constant and simulable — the condition is exact.
Lemma (c): both F_t and its complement are non-empty, so constant oracles
fail and 1 bit is minimal.
Lemma (d): forcing {x : O(P)=1} ∩ X(E) = [0,t) ∩ X(E).
Lemma (e): h: {0,1}->{0,1} has four values, so predecessors of any
non-constant oracle are {0,1,O,¬O}; incomparability of distinct thresholds
via the (A,B,C) witness.

Unconditional: no H-PSEUDO / ECCG / heuristic dependence. Scope: the
identification task; the IC-complexity consequence is cited to Corrected
Claim A in the same lineage, not proved here; adaptive multi-query
information orders are out of scope.

## Review status

Independent adversarial review (TASK-20260805-011): ACCEPT WITH
QUALIFICATIONS. Clauses (a)-(e) and Lemmas 1-5 sound; corrections C1-C7 all
correct; qualifications Q1-Q3 are presentation-level (multi-query transcript
case asserted not written, "no randomized simulator" carried by the
distributional definition, corollary could be misread as global). See
review_refs.

## Significance

This is the first fully formalized non-simulable oracle characterization in
the program: the threshold oracle C_t is the precise minimal order-based
primitive that converts a GGM attack into concrete-model Semaev index
calculus. It joins KN-FIND-c7d31e and KN-FIND-9d2f56 as a structural
result at the oracle/combinatorics level, and it sharpens the GGM-oracle
roadmap from BATCH-060/IDEA-62ef74.