# EXP-SEMAEV-002 — Composition analysis (owed disposition)

Record: composed 2026-09-08 under BATCH-d5f70a, TASK-20260908-854393,
REVIEW-PLAN-BATCH-d5f70a. This file does NOT overwrite the producer's
`analysis.md`; it is the Coordinator composition of the owed disposition
that BATCH-1f4d53 left explicitly open ("substantive review gaps remain
explicit"). Zero scientific runs were executed in this batch.

## 1. Why a disposition was owed

- Runs RUN-SEMAEV-002-{a,b,c,d} are `completed_valid` (snapshot 54aa83b92c).
- Inherited red team RT-20260907-823b5e: verdict HOLDS, with OBJ-5
  (tautological as-implemented primary metric) and OBJ-2/3/4
  (information content, scope, no-runtime-closure boundaries).
- Inherited validator VAL-20260907-b16812: verdict `incomplete`, resting
  SOLELY on two receipt-admissibility defects; the mathematics was not
  falsified.
- CORR-20260907-e65243 adjudicated both defects: the corrected
  `nonexceptional_full_box_fraction` is genuinely 1.0 (independently
  re-derived from committed raw bytes; the implementation bug fixed;
  mutation-tested), and `code.dirty` was clarified to the canonical
  tracked-file definition.
- No EV or DEC existed for the experiment; H-SEMAEV-002 sat at `approved`.

## 2. New evidence in this batch: blind re-derivation J4

TASK-20260908-0b434a derived the corrected fraction table, identity-hull
facts, and predicted-set cardinalities for all 8 cells from the committed
raw bytes and the frozen contract's metric language ALONE — CORR's report,
the producer's code and notes were on the blind_from list and were not
read (attested in the frozen report; freeze commit b4def82098; schema
addenda 0bb51610, abbffc0b, content unchanged).

Result: **agreement at all 8 cells.**

| cell | identity_hull | |predicted| | corrected fraction |
|---|---|---|---|
| m=3, p=101 | true | 2 | 99/99 |
| m=3, p=103 | true | 2 | 101/101 |
| m=3, p=107 | true | 2 | 105/105 |
| m=3, p=211 | true | 2 | 209/209 |
| m=4, p=101 | true | 3 | 98/98 |
| m=4, p=103 | true | 3 | 100/100 |
| m=4, p=107 | true | 3 | 104/104 |
| m=4, p=211 | true | 3 | 208/208 |

m=3 calibration identities: true in all 4 cells. Mutation control
(independently constructed by J4): corrected formula decays to 98/99 =
0.98989... on a synthetic misclassified cell; the original as-implemented
formula returns 1.0 — matching CORR's and VAL's independently constructed
mutation tests exactly.

## 3. Declared comparison act (Coordinator, post-freeze)

The J4 table matches CORR-20260907-e65243's table cell-for-cell. The
Coordinator prior (committed in the review plan BEFORE the J4 report
returned) clause (1) is satisfied; composition proceeds under clause (3):
support, strength replicated, claim_tier toy, H-SEMAEV-002 → supported,
knowledge promotion required.

## 4. Inference

The exceptional-target classification and the full-box-outside-exceptions
claim are computationally verified, exhaustively, at every tested cell
(m ∈ {3,4}; p ∈ {101,103,107,211}), and the load-bearing corrected metric
is now triangulated by FOUR independent derivations: producer, VAL's
from-scratch reproduction, CORR's post-fix re-derivation, and J4's blind
re-derivation. This replicates the base cases of the IDEA-20260723-006
corner induction and strengthens the scoped negative Newton/BKK gate of
EV-CRYPTO-009 toward replicated toy tier — exactly the outcome the frozen
contract's interpretation_limits pre-declared for a positive result.

## 5. Boundaries adopted (RT OBJ-2/3/4 + contract limits)

- OBJ-2 information content: the 8-cell headline collapses to fewer
  distinct curve shapes, and the m=4 corner targets are constant per cell;
  the count of cells overstates independent information. The EV records
  this explicitly.
- OBJ-3 scope: original target-sectioned canonical Semaev formulation
  only; unsectioned, coefficient-dependent lifted, Groebner, and
  non-Semaev routes are unaffected (rule 6).
- OBJ-4: no exceptional-system runtime is closed; exception-only
  uniform-mask bridges receive no sub-rho credit; this is a negative-gate
  control, not an algorithm.
- Toy tier: m ∈ {3,4} and small primes only; nothing about m >= 5 or
  cryptographic scale (rule 7). All-m remains a theorem-shaped open
  question; this is a computational base-case check, not a proof.
- No contradiction with EV-CRYPTO-009 or EV-BKK-001 arose; the rule-12
  escalation path in the contract was not triggered.

## 6. Disposition

- EV-CRYPTO-3374a2: supports, strength replicated, claim_tier toy.
- DEC-20260908-f39f65: support; H-SEMAEV-002 approved → supported;
  EXP-SEMAEV-002 approved → analyzed (lifecycle gate field, disclosed).
- KN-FIND-ba1cc6 promoted.
- Open follow-ups recorded in the DEC: owed red-team review of
  RUN-HZM-001-c-primary-gate-only (DEC-20260907-5b500d); any m >= 5 or
  larger-prime extension is NEW experimental work under its own frozen
  contract.

## 7. Citations

Runs: RUN-SEMAEV-002-{a,b,c,d} (experiments/EXP-SEMAEV-002/runs/).
Reviews: RT-20260907-823b5e, VAL-20260907-b16812
(experiments/EXP-SEMAEV-002/reviews/), J4 blind report
(coordination/goals/GOAL-CRYPTO-001/batches/BATCH-d5f70a/reviews/TASK-20260908-0b434a/blind-rederivation.yaml),
composition attestation (…/reviews/TASK-20260908-854393/composition-attestation.yaml).
Correction: CORR-20260907-e65243. Prior gate: EV-CRYPTO-009,
DEC-20260724-001. Contract: experiments/EXP-SEMAEV-002/specification.yaml
(snapshot 54aa83b92c).
