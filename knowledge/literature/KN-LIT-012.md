---
id: KN-LIT-012
type: literature
title: Parallel Collision Search with Cryptanalytic Applications
authors: [van Oorschot Paul C., Wiener Michael J.]
year: 1999
venue: Journal of Cryptology, 12(1):1-28
identifiers:
  eprint: null
  doi: 10.1007/PL00003816
  url: https://link.springer.com/article/10.1007/PL00003816
tags: [pollard-rho, distinguished-points, parallel, collision-search, baseline, generic, discrete-logarithm, ecdlp]
confidence: established
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Makes the generic square-root attack *practical and parallel*: pseudo-random
walks are run on many processors, and collisions are detected cheaply using
*distinguished points* (points whose encoding satisfies an easy predicate,
e.g. leading zero bits). Only distinguished points are stored and compared,
giving an explicit memory/processor/time tradeoff. This is the actual form of
Pollard rho used in every serious ECDLP record computation.

## Key claims (as reported)
- On m processors searching a space of size n, achieves a near-linear speedup
  (heuristically ~m, assuming random-walk behavior): expected wall-clock
  ~sqrt(n)/m, with each processor storing little.
- Distinguished-point granularity trades storage against extra walk steps.
- Applies to parallel Pollard rho for discrete logs, hash collisions, and
  meet-in-the-middle attacks, with concrete cost estimates.

## Relevance to this program
This is the *real* rho baseline the program charges against, not just the 1978
serial method (KN-LIT-008): the baseline convention "0.886*sqrt(n) group
operations, van Oorschot-Wiener parallelization assumed" comes directly from
here. Any claimed prime-field advantage must beat this fully-charged parallel
baseline (memory traffic included), not an idealized serial count. The
walk-quality constant is further tightened by Teske, "On random walks for
Pollard's rho method," Math. Comp. 70(234):809-825, 2001
(doi:10.1090/S0025-5718-00-01213-8), which shows well-chosen r-adding walks
reach the ideal random-walk constant (~20% faster than Pollard's original
three-branch map).

## Not verified here
Full paper not re-read; the distinguished-point method is standard/textbook
(hence confidence: established), but the near-linear speedup rests on the usual
heuristic random-walk assumption. Bibliographic fields confirmed against the
publisher DOI record via search, not by fetching the primary page.
