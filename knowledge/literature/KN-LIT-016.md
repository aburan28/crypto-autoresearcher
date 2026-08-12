---
id: KN-LIT-016
type: literature
title: Solving sparse linear equations over finite fields
authors: [Wiedemann Douglas H.]
year: 1986
venue: IEEE Transactions on Information Theory, 32(1):54-62
identifiers:
  eprint: null
  doi: 10.1109/TIT.1986.1057137
  url: https://doi.org/10.1109/TIT.1986.1057137
tags: [sparse-linear-algebra, wiedemann, krylov, berlekamp-massey, finite-field, index-calculus, complexity]
confidence: established
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Introduces the "coordinate recurrence" (Krylov / minimal-polynomial) method for
solving sparse linear systems over a finite field. From the Krylov sequence of
matrix-vector products, Berlekamp-Massey recovers the minimal polynomial of the
matrix on a vector, which yields the solution -- the matrix is never densified.

## Key claims (as reported)
- For an n x n matrix with w nonzeros per row: roughly O(n) matrix-vector
  products, i.e. ~O(n*w) field operations, in O(n) extra storage.
- Also gives probabilistic algorithms for determinant, rank, and minimal
  polynomial.
- Kaltofen-Saunders (AAECC 1991, LNCS 539:29-38, doi:10.1007/3-540-54522-0_93)
  hardens the analysis (algebraic perturbation replacing random padding).

## Relevance to this program
The standard tool for the *linear-algebra stage* of index calculus -- the half
of the algorithm the corpus previously did not document at all. After relation
collection (KN-TECH-003) yields a large sparse relation matrix over Z/n, a
Wiedemann-type solve recovers the factor-base logs. Its cost model (matrix-vector
products, O(n) memory) is what any "cheaper LA stage" proposal (RQ-STR-001) must
beat, and defines the LA term in the program's fully-charged cost accounting.
Block/parallel refinement: Coppersmith (KN-LIT-017); structured speedups:
displacement rank (see KN-TECH-008).

## Not verified here
Full paper not read; the cost model is textbook-level in computer algebra (hence
confidence: established). Bibliographic fields confirmed against the IEEE DOI
record via search, not by fetching the primary page.
