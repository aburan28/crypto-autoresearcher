---
id: KN-LIT-104
type: literature
title: Faster exponential time algorithms for the shortest vector problem
authors: [Micciancio Daniele, Voulgaris Panagiotis]
year: 2010
venue: SODA 2010, SIAM, pages 1468-1480
identifiers:
  eprint: null
  doi: 10.1137/1.9781611973075.119
  url: https://cseweb.ucsd.edu/~daniele/papers/Sieve.pdf
tags: [sieving, gausssieve, listsieve, svp, exact-svp, kissing-number, memory, space-complexity, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Introduces List Sieve and Gauss Sieve. List Sieve is a provable improvement on
AKS; Gauss Sieve is the practical variant that became the workhorse
implementation of lattice sieving and the direct ancestor of every sieve in use
today. The paper is also the origin of the observation that sieve *space* is
governed by the kissing number, which is the sharpest available statement of
why sieving's memory cost is structural rather than incidental.

## Key claims (as reported)
- List Sieve provably finds the shortest vector in any n-dimensional lattice in
  time `2^(3.199n)` and space `2^(1.325n)`, or in space `2^(1.095n)` with
  `2^O(n)` time -- improving the AKS bounds of `2^(5.9n)` time and `2^(2.95n)`
  space as analysed by Nguyen-Vidick (KN-LIT-103). These are worst-case proven
  bounds.
- Gauss Sieve provably uses space proportional to `tau_n`, the kissing constant
  in dimension n. Using the known bounds `2^(0.2075+o(1))n < tau_n <
  2^(0.401+o(1))n`, its worst-case space is provably below `2^(0.402n)` and is
  expected near `2^(0.21n)` in practice.
- **No upper bound on Gauss Sieve's running time is known.** Its performance is
  experimental only: the paper reports roughly `2^(0.52n)` time and `2^(0.2n)`
  space observed, and outperforming the best previous practical sieve.

## Relevance to this program
The `2^(0.2075n)` kissing-number lower bound introduced here is the origin of
the "best plausible attack" floor later used as the paranoid bound in
post-quantum parameter selection (KN-LIT-107): no sieve of this shape can use
less memory than the number of near-neighbours it must store, whatever
algorithmic improvement arrives. That makes it one of the few genuinely
robust lower-bound-flavoured statements in concrete lattice cryptanalysis, and
the right anchor for any program claim about sieving limits. Note carefully
that the practical algorithm is the one *without* a proven time bound -- the
provable and the deployed algorithm are different objects, a distinction the
program's claim tiers require keeping explicit.

## Not verified here
The complete published abstract and the author-hosted PDF's results section were
read. The `2^(3.199n)` analysis was not re-derived, the kissing-constant bounds
were not checked against their source, and no implementation was run.
