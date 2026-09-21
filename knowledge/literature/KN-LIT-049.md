---
id: KN-LIT-049
type: literature
title: Generating Hard Instances of Lattice Problems (the SIS problem)
authors: [Ajtai Miklos]
year: 1996
venue: STOC 1996, pp. 99-108
identifiers:
  eprint: null
  doi: 10.1145/237814.237838
  url: https://doi.org/10.1145/237814.237838
tags: [sis, short-integer-solution, worst-case-average-case, lattice, post-quantum, foundational, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces the Short Integer Solution (SIS) problem -- given random vectors in
Z_q^n, find a short nonzero integer combination summing to 0 mod q -- and proves
a *worst-case-to-average-case* reduction: solving random SIS instances is at least
as hard as approximating worst-case lattice problems (approximate SVP, SIVP)
within polynomial factors.

## Key claims (as reported)
- The first result establishing hardness on RANDOM instances of a lattice
  problem, enabling provably secure lattice cryptography.
- Extended abstract; approximation factors later tightened (Micciancio-Regev,
  "Worst-Case to Average-Case Reductions Based on Gaussian Measures," SIAM J.
  Comput. 37(1):267-302, 2007, doi:10.1137/S0097539705447360, introducing the
  smoothing parameter).

## Relevance to this program
POST-QUANTUM foundation -- a DIFFERENT hardness domain from this repo's ECDLP
mission. Recorded as context: SIS/lattice hardness is conjectured quantum-
resistant, whereas ECDLP falls to Shor's algorithm, which is precisely why
lattice schemes (KN-TECH-022) are the intended replacements for ECDLP-based
crypto. There is no known reduction between SIS and ECDLP in either direction.

## Not verified here
Full paper not read; the SIS problem and worst-case/average-case reduction are
textbook-level in lattice cryptography (hence confidence: established). Fields
(incl. Micciancio-Regev) confirmed against ACM DL / SIAM DOI records via search,
not by fetching the primary pages.
