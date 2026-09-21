---
id: KN-LIT-117
type: literature
title: Efficient quantum algorithms for computing class groups and solving the principal ideal problem in arbitrary degree number fields
authors: [Biasse Jean-Francois, Song Fang]
year: 2016
venue: SODA 2016, SIAM, pages 893-902
identifiers:
  eprint: null
  doi: 10.1137/1.9781611974331.ch64
  url: https://doi.org/10.1137/1.9781611974331.ch64
tags: [quantum, principal-ideal-problem, class-group, s-units, hidden-subgroup, number-field, ideal-lattice, structure, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Gives quantum polynomial-time algorithms for computing the ideal class group
(under GRH) and solving the principal ideal problem in number fields of
*arbitrary* degree, generalising Hallgren's results which applied only to
constant degree. This is the quantum engine that the ideal-lattice attacks of
KN-LIT-115 and KN-LIT-116 plug into.

## Key claims (as reported)
- Class group computation is polynomial-time quantum under the Generalized
  Riemann Hypothesis; the principal ideal problem is solved in quantum
  polynomial time in arbitrary-degree fields. Previously only constant degree
  was known (Hallgren).
- Main technical contribution: both problems reduce naturally to computing
  S-unit groups, and there is an efficient quantum reduction from S-units to the
  continuous hidden subgroup problem of Eisentrager et al., whose correctness
  requires careful analysis of the metrical properties of lattices.
- The output is converted to an exact compact representation suitable for
  further algebraic manipulation.
- The authors state the methods are useful for ongoing cryptanalysis of schemes
  based on ideal lattices.

## Relevance to this program
Establishes where the quantum boundary actually sits for structured lattices,
and it is not where a casual reading of "quantum breaks structured lattices"
would put it. What is quantum-polynomial is class-group and principal-ideal
computation in number fields -- number-theoretic problems attached to the ring.
What that buys against a lattice assumption is only what KN-LIT-115 and
KN-LIT-116 derive from it: approximate Ideal-SVP at `exp(O~(sqrt(n)))`. The
program should keep the two layers distinct when reasoning about structured
lattices, in the same way it distinguishes the group-theoretic reduction
(Pohlig-Hellman, KN-TECH-030) from an attack on the residual prime-order
problem.

## Not verified here
The complete published abstract was read from the SIAM and ACM records. The
S-unit reduction, the GRH dependence, and the continuous hidden subgroup
machinery were not verified. No claim about concrete quantum resource
requirements is made by this entry -- the result is asymptotic, and nothing here
speaks to circuit sizes (contrast KN-LIT-099).
