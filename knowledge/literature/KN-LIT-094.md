---
id: KN-LIT-094
type: literature
title: The Full Cost of Cryptanalytic Attacks
authors: [Wiener Michael J.]
year: 2004
venue: Journal of Cryptology, 17(2):105-124
identifiers:
  eprint: null
  doi: 10.1007/s00145-003-0213-5
  url: https://link.springer.com/content/pdf/10.1007/s00145-003-0213-5.pdf
tags: [full-cost, cost-model, memory, communication, wiring, bsgs, pollard-rho, parallel-collision-search, baseline, asymptotics, ecdlp]
confidence: established
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Answers an open question about the asymptotic cost of wiring many processors
to a large memory in three dimensions, and then uses that answer to price
cryptanalytic attacks by *full cost* -- hardware multiplied by the time it is
occupied -- instead of by processor steps alone. The headline consequence for
discrete logarithms: Shanks's baby-step giant-step method takes n^{1/2+o(1)}
processor steps but has full cost n^{2/3+o(1)}, because the sqrt(n)-element
table cannot be reached in unit time.

## Key claims (as reported)
- BSGS in a cyclic group of prime order n: n^{1/2+o(1)} processor steps but
  full cost n^{2/3+o(1)} (the wiring bound is what raises the exponent).
- The paper states explicitly that counting only processor steps is a
  conservative choice for the cryptographer, but that this "should not be
  turned around to say that Shanks' method and the rho method have the same
  full cost, because they do not."
- Parallel collision search (KN-LIT-012) retains a significant asymptotic
  advantage over generic memory-heavy attacks once full cost is charged,
  because its per-processor storage is small.
- Other attacks analysed under the same model: number field sieve factoring,
  generic block-cipher attacks, double and triple encryption, hash collisions.

## Relevance to this program
This is the missing rigorous basis for the program's "fully charged" baseline
convention. Three specific uses. (1) It supplies the *reason* rho rather than
BSGS is the baseline: they differ in full cost, not just in convenience.
(2) It sets the correct penalty for any proposed mechanism whose relation
store, factor base, or linear-algebra matrix is large -- index-calculus-style
routes buy a smaller step count with memory, and memory is not free in this
model, so the comparison must be made at full cost or the advantage may be an
accounting artifact. (3) It gives the exponent to beat for memory-heavy
designs: n^{2/3} is what unrestricted-memory sqrt(n) methods actually cost, so
a mechanism claiming to beat sqrt(n) with sqrt(n) storage may not beat rho at
all. See KN-TECH-035.

## Not verified here
The publisher PDF was fetched and the abstract, the introduction's Shanks-vs-rho
passage (quoted above verbatim), and the statements of the full-cost results
were read directly. The three-dimensional wiring bound and the per-attack
derivations in Sections 3 onward were not re-derived, and the constants behind
the o(1) terms were not extracted. Author, title, venue (J. Cryptology
17(2):105-124, 2004) and DOI confirmed against the DBLP volume listing and the
publisher record.
