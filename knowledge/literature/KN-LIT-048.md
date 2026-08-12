---
id: KN-LIT-048
type: literature
title: New directions in nearest neighbor searching with applications to lattice sieving (BDGL)
authors: [Becker Anja, Ducas Leo, Gama Nicolas, Laarhoven Thijs]
year: 2016
venue: SODA 2016, pp. 10-24
identifiers:
  eprint: iacr:2015/1128
  doi: 10.1137/1.9781611974331.ch2
  url: https://eprint.iacr.org/2015/1128
tags: [lattice-sieving, svp, nearest-neighbor, locality-sensitive-filtering, cost-model, security-estimate]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Develops locality-sensitive filtering for nearest-neighbor search and applies it
to heuristic lattice sieving for the shortest vector problem (SVP), achieving
heuristic time 2^{0.292n + o(n)} -- the leading asymptotic exponent for SVP
solvers.

## Key claims (as reported)
- 2^{0.292n} heuristic SVP-oracle time, establishing the near-linear-exponent
  sieving baseline used in modern lattice cost estimates.
- Heuristic (relies on sieving heuristics), not a proven worst-case bound.

## Relevance to this program
The 2^{0.292n} sieving exponent is the current best heuristic cost of the
SVP oracle that BKZ calls in each block (KN-LIT-047), so it sets the asymptotic
cost floor inside lattice-crypto security estimates (KN-TECH-020, KN-TECH-023).
Adjacent to this repo's ECDLP mission -- it prices attacks on lattice schemes, not
on the ECDLP -- but it is the quantitative backbone of "how hard is this lattice
instance."

## Not verified here
Full paper not read; the sieving exponent is relayed as the paper's stated
heuristic result (hence confidence: reported). Fields confirmed against the SIAM
proceedings DOI and IACR ePrint 2015/1128 via search, not by fetching the primary
pages.
