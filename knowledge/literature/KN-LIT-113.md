---
id: KN-LIT-113
type: literature
title: Revisiting Lattice Attacks on Overstretched NTRU Parameters
authors: [Kirchner Paul, Fouque Pierre-Alain]
year: 2017
venue: EUROCRYPT 2017 (Part I), Springer, pages 3-26
identifiers:
  eprint: null
  doi: 10.1007/978-3-319-56620-7_1
  url: https://doi.org/10.1007/978-3-319-56620-7_1
tags: [ntru, overstretched-ntru, dense-sublattice, bkz, subfield-attack, fatigue, structure, lattice]
confidence: reported
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
Shows that the algebraic subfield attack of KN-LIT-112 was unnecessary: plain
(dual-)BKZ already behaves far better on overstretched NTRU instances than the
standard estimates predict, achieving the same asymptotic improvements without
any subfield machinery. The explanation offered is geometric rather than
algebraic -- in the overstretched regime the NTRU lattice contains an
exceptionally dense sublattice, and lattice reduction detects it.

## Key claims (as reported)
- Standard lattice reduction on overstretched NTRU outperforms the 2016
  estimate, matching the subfield attack's asymptotic gains with minor
  performance tricks, demonstrated in practice.
- The mechanism is the dense sublattice of the NTRU lattice, not the presence of
  subfields; the security-relevant property is geometric.
- An asymptotic upper bound on the fatigue point -- the modulus at which the
  overstretched regime begins -- of `q <= n^(2.783+o(1))` for ternary NTRU, in
  the standard case where secret coefficients have standard deviation
  `sigma = Theta(1)`.
- The bound is obtained by an *impossibility argument*: beyond a certain point
  BKZ's predicted behaviour contradicts what a q-ary lattice can do, so it must
  have detected the dense sublattice. This yields an upper bound only, and does
  not explain how reduction recovers the secret.

## Relevance to this program
A direct methodological warning for the program's own negative and structural
arguments. The Kirchner-Fouque bound is derived from an impossibility argument,
and the follow-up (KN-LIT-114) shows what that costs: the argument gives a
correct-but-loose bound (`n^2.783` versus the true `n^2.484`) and no mechanism.
The program has itself produced an asymptotic negative gate by a saturation
argument; this is the reference case for how such an argument should be scoped
-- as a bound whose tightness is unknown until a mechanistic account replaces
it. It is also the cleanest example in the corpus of a *simpler* algorithm
matching a sophisticated one once the analysis is corrected.

## Not verified here
Author, title, venue, year, and page range were confirmed against IACR CryptoDB
and the Springer proceedings listing. The paper's own PDF was not fetched; the
claims above are read from the EUROCRYPT 2017 presentation slides and from the
detailed restatement of the Kirchner-Fouque estimate in KN-LIT-114, which is a
secondary account by other authors. The `n^(2.783+o(1))` figure and the
impossibility-argument characterisation should be re-checked against the paper
itself before any program claim depends on them.
