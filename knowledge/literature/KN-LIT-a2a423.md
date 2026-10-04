---
id: KN-LIT-a2a423
type: literature
title: Rigorous Statements and Proofs of the Lemmas in Simon's Algorithm for the Dihedral Coset Problem and Their Underlying
  Hypothesis
authors:
- Yuchen Guo
- Shuo Yang
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1714
identifiers:
  eprint: iacr:2026/1714
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1714
source:
  citation: Yuchen Guo, Shuo Yang. Rigorous Statements and Proofs of the Lemmas in Simon's Algorithm for the Dihedral Coset
    Problem and Their Underlying Hypothesis. Cryptology ePrint Archive 2026/1714, 2026.
  url: https://eprint.iacr.org/2026/1714
tags:
- dcp
- lwe
- quantum
- proof-audit
- unverified-claim
- dihedral-coset
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The authors supply clarified statements and proofs for three sketched lemmas in Simon’s ePrint 2026/1591, repairing several counting details. Their analysis isolates an unproved condition: the two-side partition must be fixed independently of the measured string, whereas the algorithm’s choice rule does not supply that independence.

## Scope and evidence boundary

They explicitly say that proving these lemmas alone does not establish correctness of Simon’s DCP algorithm. This is an analysis of a disputed algorithm, not a quantum lattice break.

## Research follow-up

Read alongside the stronger no-go in ePrint 2026/1693 (KN-LIT-3b271a) and the original claim KN-LIT-e204ab; do not feed the unverified polynomial-time claim into current ML-KEM security estimates.

Source: [https://eprint.iacr.org/2026/1714](https://eprint.iacr.org/2026/1714); ePrint received 2026-08-17. Abstract and metadata read on 2026-09-26; result not reproduced.
