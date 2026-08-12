---
id: KN-LIT-115
type: literature
title: Recovering Short Generators of Principal Ideals in Cyclotomic Rings
authors: [Cramer Ronald, Ducas Leo, Peikert Chris, Regev Oded]
year: 2016
venue: EUROCRYPT 2016 (ePrint 2015/313)
identifiers:
  eprint: iacr:2015/313
  doi: null
  url: https://eprint.iacr.org/2015/313
tags: [ideal-lattice, principal-ideal, short-generator, log-unit-lattice, cyclotomic, ideal-svp, approximation-factor, quantum, structure, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Proves rigorously that the log-unit lattice of a prime-power cyclotomic field is
efficiently decodable, which was the unsubstantiated step in the
Campbell-Groves-Shepherd sketch of an attack on the short-generator problem.
Combined with the quantum principal-ideal algorithm of Biasse-Song
(KN-LIT-117), this confirms a quantum polynomial-time attack on the
short-generator problem and, as a second contribution, gives a
`2^(O~(sqrt(n)))`-approximate SVP algorithm on principal ideal lattices.

## Key claims (as reported)
- Rigorous proof that the log-unit lattice is efficiently decodable for any
  cyclotomic of prime-power index -- where the standard approach on general
  lattices takes exponential time. Two technical ingredients: a geometric
  analysis of the standard cyclotomic units using analytic number theory, and a
  proof that standard lattice decoding recovers the short generator for a wide
  class of typical short-generator distributions.
- Combined with Biasse-Song, this confirms the main claim of Campbell et al.
- Extending the geometric analysis gives an efficient algorithm finding a
  `2^(O~(sqrt(n)))`-approximate shortest vector in a principal ideal; with
  Biasse-Song this is quantum polynomial time for
  `2^(O~(sqrt(n)))`-approximate SVP on principal ideal lattices.

## Relevance to this program
The precise statement of how much structure buys, which is exactly the shape of
question KN-OPEN-012 asks. The gain is real and provable, but it is confined to
(i) principal ideals, (ii) prime-power cyclotomics, (iii) *typical* short
generators, and (iv) an approximation factor of `2^(O~(sqrt(n)))` -- which is
superpolynomial, and far larger than the small polynomial factors that
Ring-LWE-based schemes actually rely on. The program should hold onto both
halves of that: structure demonstrably changed the complexity, and it did so at
an approximation factor that does not touch deployed parameters. Stating only
one half misrepresents the result in either direction.

## Not verified here
The ePrint abstract was fetched and read. The decoding proof, the geometric
analysis of cyclotomic units, and the approximation-factor derivation were not
re-derived. The characterisation of which short-generator distributions count as
"typical" was not extracted from the full text.
