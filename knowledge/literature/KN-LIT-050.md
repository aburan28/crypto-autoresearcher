---
id: KN-LIT-050
type: literature
title: On Lattices, Learning with Errors, Random Linear Codes, and Cryptography (the LWE problem)
authors: [Regev Oded]
year: 2009
venue: Journal of the ACM 56(6):Art.34 (STOC 2005, pp. 84-93)
identifiers:
  eprint: null
  doi: 10.1145/1568318.1568324
  url: https://doi.org/10.1145/1568318.1568324
tags: [lwe, learning-with-errors, worst-case-average-case, quantum-reduction, lattice, post-quantum, foundational, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Defines the Learning With Errors (LWE) problem -- recover a secret from noisy
random linear equations mod q -- and gives a QUANTUM reduction from worst-case
lattice problems (GapSVP, SIVP to within Otilde(n) factors) to average-case LWE.
Also builds a public-key cryptosystem whose security rests on LWE.

## Key claims (as reported)
- Worst-case lattice hardness => average-case LWE hardness, via a QUANTUM
  reduction (the paper explicitly leaves a classical reduction open; partial
  classical reductions came later, e.g. Peikert; Brakerski et al.).
- LWE is the workhorse assumption of modern lattice cryptography.
- Journal of the ACM 56(6), 2009 is the full version of STOC 2005.

## Relevance to this program
POST-QUANTUM foundation, ADJACENT to (not part of) the ECDLP mission. Recorded as
context: LWE underlies most deployed lattice schemes (Kyber/Dilithium via
Module-LWE, KN-TECH-022) that are meant to replace ECDLP-based crypto because
LWE's worst-case lattice hardness is conjectured quantum-resistant while ECDLP is
not. No known reduction links LWE and ECDLP.

## Not verified here
Full paper not read; LWE and the quantum reduction are textbook-level in lattice
cryptography (hence confidence: established); the quantum-vs-classical hedge is
the paper's own. Fields for both JACM 2009 and STOC 2005 versions confirmed
against ACM DL DOI records via search, not by fetching the primary pages.
