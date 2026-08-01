---
id: KN-LIT-7589
type: literature
title: Lower bounds on the strength of the determinant
authors:
  - "Qiyuan Chen"
  - "Yuhao Zhao"
year: 2026
venue: 'arXiv preprint arXiv:2607.21015 [math.AC]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.21015'
  url: https://arxiv.org/abs/2607.21015
tags: [algebraic-complexity, strength, partition-rank, birch-rank, determinant, lower-bound, chow-ring, intersection-theory, polynomial-system, proof-technique]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Establishes new lower bounds for the **strength** and **partition rank** of the
determinant, and introduces an intersection-theoretic method for lower-bounding strength.

## Key claims (as reported)
- Exact identity for every prime `p`: `str(det_p) = p`.
- A weak monotonicity argument plus a prime-gap bound gives
  `str(det_n) >= (1 - o(1)) n^{0.475}` for sufficiently large `n`.
- Since the **Birch rank** of `det_n` is always 4, this is the first explicit family
  showing that the dependence on degree in bounds for strength in terms of Birch rank is
  **unavoidable**.
- Viewing `det_n` as an `n`-linear form in its columns, its partition rank is at least the
  largest prime `<= n`; hence `n - n^{0.525} <= prk(det_n) <= n`, so `prk(det_n) = n - o(n)`.
- Method: a short strength decomposition would produce a nowhere-vanishing section of a
  split vector bundle on the complement of the determinantal hypersurface, while a nonzero
  top Chern class in the Chow ring of `PGL_n` obstructs such a section.

## Relevance to this program
Pure algebraic geometry / commutative algebra with no cryptographic content. Recorded for
one reason: the **proof technique**, and its bearing on how the program measures the
difficulty of the polynomial systems it actually solves.

"Strength" (Ananyan–Hochster) measures how far a form is from decomposing as a short sum
of products of lower-degree forms — a structural complexity measure on polynomials, and
the kind of quantity that governs whether a system decomposes into easier pieces. The
program's central computational object is a family of structured polynomial systems: the
Semaev summation-polynomial systems (`KN-TECH-002`) whose Gröbner solving degree is the
program's principal difficulty indicator (`KN-TECH-004`, `KN-TECH-011`, `KN-OPEN-002`).
Solving degree is an *empirical* indicator — measured by running a solver and watching the
degree fall out — and the program has repeatedly wanted a structural quantity that could
be **lower-bounded a priori** rather than observed.

This paper is a worked example of proving such a lower bound for a specific structured
determinantal form, and the machinery is the interesting part: obstruct a hypothetical
short decomposition by exhibiting a nonvanishing characteristic class. That is a route to
a genuine lower bound on decomposability rather than a measurement of one solver's
behaviour, which is what a barrier claim would need in order to be more than
solver-relative.

Two honest caveats, both of which should prevent this entry from being over-read:

1. Nothing here concerns summation polynomials, elliptic curves, or Gröbner bases. The
   determinant is not the program's object, and no transfer has been attempted or checked.
2. Strength and partition rank are not the same as solving degree, and no result is known
   here relating them. Treating a strength bound as a Gröbner-complexity bound would be
   exactly the indicator-substitution error catalogued in `KN-LIT-7587`.

Recorded as a speculative technique pointer at low priority, not as evidence. No entry
status changes.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-27 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-23, primary category math.AC (cross-listed math.AG, math.CO), 16 pages per the
author comment. Preprint — not peer-reviewed, no DOI or venue as of this entry.

NOT verified here: the identity `str(det_p) = p`; the `n^{0.475}` and `n^{0.525}` exponents
and the prime-gap input they depend on; the claim that Birch rank of `det_n` is always 4;
the intersection-theoretic obstruction argument and the Chow-ring computation; the
partition-rank bounds; and the priority claim ("first explicit family"). **No connection
between strength/partition rank and Gröbner solving degree has been established, here or
in the paper** — the relevance argument above is a speculative reading by this program and
must not be cited as a result.
