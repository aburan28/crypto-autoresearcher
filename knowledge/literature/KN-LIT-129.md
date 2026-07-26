---
id: KN-LIT-129
type: literature
title: 'The SQALE of CSIDH: Sublinear Velu Quantum-resistant isogeny Action with Low Exponents'
authors: [Chavez-Saab Jorge, Chi-Dominguez Jesus-Javier, Jaques Samuel, Rodriguez-Henriquez Francisco]
year: 2022
venue: 'Journal of Cryptographic Engineering (ePrint 2020/1520)'
identifiers:
  eprint: iacr:2020/1520
  doi: null
  url: https://eprint.iacr.org/2020/1520
tags: [csidh, class-group-action, quantum, collimation-sieve, parameter-selection, security-estimate, implementation, constant-time, velu, resource-constrained, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
The constructive response to the CSIDH quantum-security reassessment of
`KN-LIT-127` and `KN-LIT-128`. It refines the estimates of a
**resource-constrained** quantum collimation-sieve attack in order to assign
CSIDH a precise quantum security level, then optimises large CSIDH parameters to
meet NIST security levels 1, 2 and 3 and supplies a constant-time C
implementation using square-root-complexity Velu formulas. Reported as the first
CSIDH implementation at these higher security levels, with primes ranging from
about 2000 to 9000 bits.

## Key claims (as reported)
- The Bonnetain-Schrottenloher and Peikert EUROCRYPT 2020 analyses
  "significantly reduced the estimated quantum security" of CSIDH; this work
  responds to that.
- Estimates of a **resource-constrained** collimation-sieve attack are refined to
  give CSIDH a precise quantum security level — the qualifier matters, and is the
  whole argument.
- Parameters meeting NIST levels 1, 2 and 3 are derived and implemented in
  constant time using square-root-complexity (sublinear) Velu formulas.
- Primes range from roughly 2000 up to 9000 bits — i.e. the response to the
  attack is a large parameter increase, not a refutation.

## Relevance to this program
The third leg of the CSIDH quantum-cost dispute and the most instructive one for
this program's methodology. The disagreement between `KN-LIT-127`/`KN-LIT-128`
and this paper is substantially about **what resources the adversary is allowed**
— an unbounded-quantum-memory model versus a resource-constrained one — rather
than about the algorithm. That is precisely the pattern `KN-TECH-040` records for
lattices (core-SVP charging one SVP oracle call and no memory) and
`KN-TECH-044`/`KN-OPEN-017` record for sieving memory.

So the corpus now holds the same lesson in three independent domains: lattice
cost-model conventions, ECDLP full-cost accounting, and CSIDH quantum security.
`GOAL-SSI-001`'s requirement that memory, preprocessing, oracle and
quantum-query costs all be charged is not local hygiene; it is the axis on which
this entire subfield's numbers move.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2020/1520, a Tampere University research-portal record, a Semantic Scholar
record, and the authors' GitHub implementation); direct fetches returned HTTP
403 under this session's egress policy.

Two bibliographic cautions. **The title varies between versions**: the ePrint
listing gives "Sublinear Velu" (recorded here) while other indexes give
"Square-root velu"; the same work is meant. **The year is uncertain** — the
ePrint is 2020 and the journal publication is reported as Journal of
Cryptographic Engineering 2022; 2022 is recorded with the ePrint number given,
and the DOI was not confirmed so it is null.

NOT verified here: the refined attack estimates, the resulting security levels,
the exact prime sizes per NIST level, and the benchmark figures.
