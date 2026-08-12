---
id: KN-LIT-074
type: literature
title: The supersingular isogeny path and endomorphism ring problems are equivalent
authors: [Wesolowski Benjamin]
year: 2021
venue: FOCS 2021, pp. 1100-1111
identifiers:
  eprint: iacr:2021/919
  doi: 10.1109/FOCS52979.2021.00109
  url: https://eprint.iacr.org/2021/919
tags: [endomorphism-ring, isogeny-path, equivalence, deuring, hardness-foundation, grh, isogeny, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Proves that the supersingular ENDOMORPHISM RING problem and the isogeny
PATH-FINDING problem are equivalent under polynomial-expected-time reductions,
assuming GRH. Unifies the hardness foundation of supersingular isogeny
cryptography (the presumed hardness of these problems underpins the whole family).

## Key claims (as reported)
- Equivalence is CONDITIONAL on the generalized Riemann hypothesis (not
  unconditional).
- A key tool is a rigorous algorithm for the quaternion analogue of path-finding,
  making the previously heuristic KLPT method (KN-LIT-073) rigorous.

## Relevance to this program
Ties path-finding hardness to endomorphism-ring structure, directly connecting to
the program's study of supersingular endomorphism structure and orientation
(RQ-ISO-001, ISO-AR). Establishes WHAT the surviving isogeny assumptions actually
rest on (endomorphism-ring computation) -- the open hardness question the corpus
records at KN-OPEN-013. Adjacent to the ECDLP mission.

## Not verified here
Full paper not read; the equivalence and its GRH conditionality relayed from the
abstract (hence confidence: reported). Fields confirmed against IACR ePrint
2021/919 and the IEEE FOCS DOI via search, not by fetching the primary pages.
