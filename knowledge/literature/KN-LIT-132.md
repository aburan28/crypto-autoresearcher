---
id: KN-LIT-132
type: literature
title: Improved algorithms for finding fixed-degree isogenies between supersingular elliptic curves
authors: [Bencina Benjamin, Kutas Peter, Merz Simon-Philipp, Petit Christophe, Stopar Miha, Weitkamper Charlotte]
year: 2024
venue: 'Advances in Cryptology - CRYPTO 2024, Springer'
identifiers:
  eprint: iacr:2023/1618
  doi: 10.1007/978-3-031-68388-6_8
  url: https://eprint.iacr.org/2023/1618
tags: [supersingular, isogeny, fixed-degree, endomorphism-ring, meet-in-the-middle, memory-free, low-memory, quantum, cost-model, path-finding, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Improved classical and quantum algorithms for computing an isogeny of a
**specific known degree** `d` between two supersingular elliptic curves, when
one exists. The paper distinguishes this from the general isogeny-finding
problem: finding some isogeny between supersingular curves is known to be
equivalent to computing the curves' endomorphism rings, but fixing the degree
appears to change the problem's nature, and its hardness is separately required
by isogeny-based cryptography. The reported algorithms are **essentially
memory-free** and beat meet-in-the-middle over a stated range of the degree
parameter.

## Key claims (as reported)
- Finding an isogeny between supersingular curves is equivalent to computing
  their endomorphism rings; requiring a **fixed known degree** `d` gives a
  problem "somewhat different in nature" whose hardness is also needed.
- The new algorithms are **essentially memory-free** and have better time
  complexity than meet-in-the-middle on a classical computer over a stated
  interval of the degree exponent.
- Time complexity is also improved on quantum computers over a stated interval.

## Relevance to this program
The single most directly useful entry for the `GOAL-SSI-001` BATCH-002 gate, and
a 2024 result the corpus was missing entirely. `DEC-20260725-002` frames
BATCH-002 as separating F_p^2 meet-in-the-middle from F_p Delfs-Galbraith and
defining or falsifying a low-memory alternative. This paper is a 2024 attack on
that exact axis: memory-free algorithms that beat MITM in a specified regime.

It also sharpens what BATCH-002 should conclude. `IDEA-20260725-001` proposes a
full-cost re-baselining, and the red team judged it cost-model hygiene rather
than a mechanism. This entry supports that judgement while raising the bar: the
honest matched baseline for fixed-degree supersingular isogeny finding is not
simply "MITM with memory charged" but a regime-dependent choice among MITM,
memory-free search, and Delfs-Galbraith, whose crossover depends on the degree
parameter. A recommendation that names one algorithm without naming the regime
is not a matched baseline.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2023/1618, Springer DOI 10.1007/978-3-031-68388-6_8, CRYPTO 2024, a University of
Birmingham research-portal record, Semantic Scholar); direct fetches returned
HTTP 403 under this session's egress policy. Title, author list, year and venue
are corroborated across independent results.

**The complexity ranges are deliberately not recorded numerically here.** A
search-returned abstract gave a classical range of `1/2 <= epsilon <= 3/4` and a
quantum range of `0 < epsilon < 5/2` for a degree exponent whose definition was
not visible; the quantum endpoint is not obviously consistent with the classical
one, so at least one figure may be garbled in transit. The parameterisation, the
exact intervals, the complexity expressions, and the memory model must be taken
from the paper before any BATCH-002 derivation quotes them.
