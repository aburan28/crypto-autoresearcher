---
id: KN-LIT-105
type: literature
title: 'Shortest Vector from Lattice Sieving: a Few Dimensions for Free'
authors: [Ducas Leo]
year: 2017
venue: EUROCRYPT 2018 (ePrint 2017/999)
identifiers:
  eprint: iacr:2017/999
  doi: null
  url: https://eprint.iacr.org/2017/999
tags: [sieving, dimensions-for-free, svp, lsh, tuple-sieve, enumeration-crossover, speedup, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Shows that solving SVP in dimension n does not require sieving in dimension n:
a few calls to a sieve in dimension `n - d`, with `d = Theta(n / log n)`,
suffice. The saving is only sub-exponential asymptotically but is large in the
dimensions that are actually computed, and it applies to essentially any sieve
variant. This is the trick that made sieving competitive with pruned
enumeration in practice.

## Key claims (as reported)
- `d = Theta(n / log n)` dimensions come "for free": SVP in dimension n is
  solved by a few sieve calls in dimension `n - d`.
- Implemented over a simple `(4/3)^(n+o(n))` sieve, it outperforms the best
  sieve algorithms in the literature by a factor of 10 in dimensions 70-80.
- In that range the improved sieve runs less than an order of magnitude slower
  than pruned enumeration, and the author predicts sieving will overtake pruned
  enumeration in practice in the near future -- a prediction subsequently borne
  out (KN-LIT-106 reports the crossover at dimension 70).
- The technique composes with LSH sieves and tuple sieves.

## Relevance to this program
A textbook case of a *sub-exponential* improvement changing a practical ranking.
The program's screening gates are usually framed around exponent-level
advantage over a baseline, and this paper is the standing counterexample to
treating that as the only thing worth measuring: the asymptotic exponent of
sieving did not move, yet the algorithm family went from losing to winning
against its competitor. Any program gate that would have rejected this
mechanism as "not an exponent improvement" is mis-specified for concrete
cryptanalysis, and the gate's scope should say so explicitly.

## Not verified here
The ePrint abstract was fetched and read. The `Theta(n / log n)` analysis was
not re-derived, and neither the factor-of-10 speedup nor the enumeration
comparison was reproduced.
