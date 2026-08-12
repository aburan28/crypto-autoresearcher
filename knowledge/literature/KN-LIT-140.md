---
id: KN-LIT-140
type: literature
title: On the Complexity of Solving Quadratic Boolean Systems
authors: [Bardet Magali, Faugere Jean-Charles, Salvy Bruno, Spaenlehauer Pierre-Jean]
year: 2013
venue: 'Journal of Complexity, 29(1):53-75, Elsevier (arXiv:1112.6263)'
identifiers:
  eprint: null
  doi: null
  url: https://arxiv.org/abs/1112.6263
tags: [mq, multivariate-quadratic, booleansolve, boolean-solving, polynomial-system, exhaustive-search, sparse-linear-algebra, hybrid, complexity, las-vegas, solving, index-calculus]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Presents **BooleanSolve**, an algorithm for finding all common zeroes of `m`
quadratic polynomials in `n` unknowns over F_2, and proves complexity bounds
below exhaustive search. The method reduces the problem to a **combination of
exhaustive search and sparse linear algebra** — the same hybrid shape that the
crossbred algorithm (`KN-LIT-139`) later exploits — and the paper is the standard
reference for the proved asymptotics of this family.

## Key claims (as reported)
- The prior best complexity bound was exhaustive search at `4 log_2(n) * 2^n`
  operations.
- The **deterministic** variant of BooleanSolve is bounded by `O(2^{0.841 n})`
  when `m = n`.
- A **probabilistic Las Vegas** variant has expected complexity `O(2^{0.792 n})`.
- The cryptanalysis of several modern ciphers reduces to this problem.

## Relevance to this program
Supplies the proved complexity backdrop against which the program's measured
solver exponents should be read. `EXP-ICI-001` fits empirical cost exponents for
a crossbred solver path; this entry gives the analytically established exponents
for the closest well-analysed relative, so a measured cost that implies behaviour
better than `2^{0.792 n}` in the same regime is a signal to re-examine the
measurement rather than a discovery.

The structural lesson is the one the program keeps meeting from the other side:
the gain over exhaustive search comes from **trading linear algebra against
search**, and the achieved exponent depends on how that trade is parameterised.
That is the same trade `KN-TECH-050` describes for isogeny path-finding and
`KN-TECH-042` describes for lattice enumeration versus sieving — and in all three
cases the crossover, not the asymptotic, is what decides a matched baseline.

Note also the constant `4 log_2(n)` on the exhaustive-search baseline. The
program's full-cost discipline (`KN-TECH-035`) insists that such factors be
carried; an exponent comparison that drops them can invert a ranking at the sizes
actually tested.

## Not verified here
Verification was by web search surfacing primary-index listings (Journal of
Complexity 29(1):53-75, 2013, arXiv 1112.6263, Inria/HAL deposit `hal-00655745`,
NASA ADS record, Semantic Scholar, and an author-hosted PDF); direct fetches
returned HTTP 403 under this session's egress policy. **The Elsevier DOI was not
confirmed and is null.** The arXiv version is dated 2011 and the journal version
2013; 2013 is recorded.

NOT verified here: the algorithm's construction, the derivation of the 0.841 and
0.792 exponents, the conditions under which they hold (in particular the
`m = n` restriction and any genericity assumptions), and the constants hidden in
the `O(.)`. The exponents above are quoted from an abstract returned by search
and must be confirmed against the paper before use in any program cost model.
