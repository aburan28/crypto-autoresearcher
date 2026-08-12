---
id: KN-LIT-073
type: literature
title: On the quaternion ell-isogeny path problem (KLPT)
authors: [Kohel David, Lauter Kristin E., Petit Christophe, Tignol Jean-Pierre]
year: 2014
venue: LMS Journal of Computation and Mathematics, 17(A):418-432
identifiers:
  eprint: iacr:2014/505
  doi: 10.1112/S1461157014000151
  url: https://eprint.iacr.org/2014/505
tags: [klpt, quaternion, maximal-order, deuring, endomorphism-ring, isogeny-path, sqisign, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The KLPT algorithm: given a left O-ideal (O a maximal order in a definite
quaternion algebra over Q of prime discriminant p), computes a representative in
its left ideal class of ell-power norm. This is the algebraic (quaternion) side of
the Deuring correspondence (KN-LIT-075) and is foundational for SQIsign
(KN-LIT-072) and endomorphism-ring computations.

## Key claims (as reported)
- Runs in expected polynomial time IN PRACTICE, subject to heuristics on prime
  distributions (heuristic, not unconditional; later made rigorous under GRH by
  Wesolowski, KN-LIT-074).
- Also breaks a quaternion analogue of the CGL hash (KN-LIT-063), with security
  implications for the original supersingular-isogeny hash.

## Relevance to this program
KLPT operates on quaternion maximal orders -- the Deuring-corresponding algebraic
image of supersingular endomorphism rings -- placing it at the algebraic heart of
the endomorphism-structure questions the program investigates (RQ-ISO-001,
ISO-AR). Adjacent to the ECDLP mission. Example of solving the "algebraic side"
of a correspondence to attack/construct the "geometric side."

## Not verified here
Full paper not read; the algorithm and its heuristic status relayed from the
abstract (hence confidence: reported). Fields confirmed against IACR ePrint
2014/505 and the LMS/Cambridge DOI via search, not by fetching the primary pages.
