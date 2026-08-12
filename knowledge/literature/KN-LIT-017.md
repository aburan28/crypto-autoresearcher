---
id: KN-LIT-017
type: literature
title: Solving homogeneous linear equations over GF(2) via block Wiedemann algorithm
authors: [Coppersmith Don]
year: 1994
venue: Mathematics of Computation, 62(205):333-350
identifiers:
  eprint: null
  doi: 10.1090/S0025-5718-1994-1192970-7
  url: https://doi.org/10.1090/S0025-5718-1994-1192970-7
tags: [sparse-linear-algebra, block-wiedemann, coppersmith, finite-field, parallel, index-calculus, complexity]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
A *blocked* version of Wiedemann's algorithm (KN-LIT-016) for large sparse
homogeneous systems over GF(2). Operating on blocks of vectors (e.g. 32/64
packed into machine words) performs many matrix-vector products for essentially
the cost of one, exploiting word-level parallelism and handling multiple
right-hand sides; a block Berlekamp-Massey / matrix-generating-polynomial step
replaces scalar minimal-polynomial recovery.

## Key claims (as reported)
- Time-competitive with structured Gaussian elimination but far lower memory;
  aimed at the final linear-algebra stage of integer factorization and
  discrete-log index calculus.
- The blocking amortizes the many matrix-vector products that dominate that
  stage and parallelizes across the block.

## Relevance to this program
The practical form of the sparse solve for cryptographic-scale relation
matrices; combined with structured Gaussian elimination the standard recipe is
LaMacchia-Odlyzko, "Solving large sparse linear systems over finite fields,"
CRYPTO 1990, LNCS 537:109-133 (doi:10.1007/3-540-38424-3_8). Fixes the LA-stage
baseline (memory, parallelism, wall time) that structured-matrix proposals
(RQ-STR-001, KN-OPEN-006) are measured against under the program's fully-charged
cost model.

## Not verified here
Full paper not read; block-Wiedemann specifics relayed from the abstract and
standard references. The AMS Math. Comp. DOI is standard-format and
search-corroborated but was not opened directly (session egress blocks the
host); venue/volume/pages cross-checked across sources.
