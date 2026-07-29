---
id: KN-LIT-100
type: literature
title: Lattice Reduction by Random Sampling and Birthday Methods
authors: [Schnorr Claus Peter]
year: 2003
venue: STACS 2003, LNCS 2607, Springer
identifiers:
  eprint: null
  doi: 10.1007/3-540-36494-3_14
  url: https://link.springer.com/chapter/10.1007/3-540-36494-3_14
tags: [gsa, geometric-series-assumption, random-sampling, birthday, lattice-reduction, bkz, basis-profile, heuristic, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Introduces a random-sampling reduction algorithm that finds short lattice
vectors by sampling in high-dimensional sublattices rather than by
enumeration, sped up further by a birthday variant. Its lasting importance to
cryptanalysis is incidental to the algorithm: this is the paper that states
the **Geometric Series Assumption (GSA)**, the heuristic that underpins almost
every concrete lattice security estimate written since.

## Key claims (as reported)
- The GSA, stated verbatim as: let `||b*_i||^2 / ||b_1||^2 = q^(i-1)` for
  i = 1..n be a geometric series with quotient q, `3/4 <= q < 1`. The paper is
  explicit that "we merely use the GSA to simplify the analysis" -- it is an
  analytical convenience, not a theorem.
- The paper immediately qualifies it: in practice the quotients only
  *approximate* `q^(i-1)` without equality, LLL-type reduced bases usually have
  bad GSA behaviour, and it is BKZ-reduced bases whose log Gram-Schmidt norms
  "closely approximate a line."
- The sampling algorithm finds a vector shorter than b_1 in `O(n^2 (k/6)^(k/4))`
  average time provided b_1 is `(k/6)^(n/(2k))` times longer than the shortest
  nonzero vector, assuming the input basis has an orthogonal basis typical of
  worst-case lattices (heuristic, not proven for arbitrary input).
- The birthday variant reduces the number of sampled vectors to roughly its
  square root and is superior for large k.

## Relevance to this program
The GSA is the lattice analogue of a modelling assumption this program is
obliged to treat with suspicion. Every primal/dual attack cost estimate
(KN-TECH-038, KN-TECH-039) predicts a required BKZ block size by assuming the
basis profile is a straight line; the paper that introduced the line says it is
an approximation that fails at the head and tail. Any internal claim about
lattice attack cost that inherits a GSA-based block-size prediction inherits an
unproven heuristic, and must be labelled as such rather than reported as a
complexity. This is directly parallel to the program's treatment of the
first-fall-degree and degree-of-regularity heuristics on the ECDLP side.

## Not verified here
The paper text hosted at d-nb.info was fetched and the abstract and the GSA
statement, its stated justification, and the practical caveats were read
directly. Theorems 1 and 2 and the sampling analysis were not re-derived, and
the exact page range in the STACS 2003 proceedings was not confirmed.
