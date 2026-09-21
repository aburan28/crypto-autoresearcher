---
id: KN-TECH-008
type: technique
title: Sparse and structured linear algebra over finite fields
tags: [sparse-linear-algebra, wiedemann, block-wiedemann, structured-gaussian-elimination, displacement-rank, index-calculus, complexity]
confidence: established
complexity: Wiedemann ~O(n*w) field ops and O(n) memory for n x n with w nonzeros/row; displacement-rank solves ~O~(alpha*n) or O~(alpha^{omega-1}*n)
applicability: the linear-algebra stage of index calculus -- solving the large sparse relation system over Z/n
source_refs: [KN-LIT-016, KN-LIT-017]
added: 2026-07-21
superseded_by: null
---

## Method
After relation collection (KN-TECH-003), index calculus must solve a large
sparse linear system over Z/n (or GF(2)) for the factor-base logarithms. The
standard tools:
- **Wiedemann** (KN-LIT-016): Krylov / minimal-polynomial method via
  Berlekamp-Massey; ~O(n) matrix-vector products, O(n) memory, never densifies.
- **Block Wiedemann** (Coppersmith, KN-LIT-017): blocks of vectors packed into
  machine words -> word-level parallelism and multiple right-hand sides;
  time-competitive with structured Gaussian elimination at far lower memory.
- **Structured Gaussian elimination** (LaMacchia-Odlyzko): cheaply eliminate
  light rows/columns first, then run an iterative solver on the dense core.

## Structured / displacement-rank speedups
If the relation matrix is close to Toeplitz/Hankel (low *displacement rank*
alpha; Kailath-Kung-Morf 1979), superfast solvers apply: O~(alpha*n) classically,
and O~(alpha^{omega-1}*n) for larger alpha (Bostan-Jeannerod-Schost, ISSAC 2007 /
TCS 2008). This is the mechanism the program's structured-matrix candidate
targets: constrain relation supports (e.g. arithmetic progressions) so the
operator itself is structured (RQ-STR-001, KN-OPEN-006).

## Program usage
Fixes the LA-stage cost term in the program's fully-charged accounting -- half
the index-calculus algorithm, previously undocumented in the corpus. Any "cheaper
LA" proposal must beat the block-Wiedemann baseline on the same matrix; the
displacement-rank route must show alpha stays O(1) (not growing like sqrt(B))
AND that the support constraint's relation-probability penalty does not inflate
the matrix past the point where the LA saving is irrelevant.

## Applicability limits
Wiedemann's cost model assumes genuine sparsity (small w); dense or
badly-conditioned systems lose the advantage. Displacement-rank gains require the
matrix to be *provably* near-Toeplitz -- negation/twist symmetry can break the
translation invariance that structured harvesting relies on, so alpha must be
measured, not assumed.
