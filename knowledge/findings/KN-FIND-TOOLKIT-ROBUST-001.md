---
id: KN-FIND-TOOLKIT-ROBUST-001
type: internal_finding
title: The prime-field m=3 decomposition barrier is robust to the full standard algorithmic toolkit
tags: [prime-field, index-calculus, 3sum, oracle, fft, multipoint-evaluation, no-speedup, barrier, m3]
confidence: reported
internal_refs: [research/PLAN-prime-field-ecdlp-program-20260722.md, research/THM-collection-lower-bound-20260722.md, KN-FIND-S4-ORACLE-001, KN-FIND-3SUM-NOGO-001]
added: 2026-07-22
superseded_by: null
---

## Result (analysis + toy verification)
Every standard technique for the m=3 decomposition oracle over a prime-field
elliptic curve hits the same wall:
- meet-in-the-middle pairwise table: Theta(B^2) (verified);
- algebraic root-finding on S_4 (solve the summation curve): Theta(B^2) (verified);
- fast multipoint evaluation of S_4 on the V x V grid: detecting a zero entry of
  the evaluation matrix has no sublinear method for unstructured V -> Theta(B^2);
- group-FFT / convolution (1_V * 1_V * 1_V over the group) -- the technique that
  makes INTEGER 3SUM subquadratic: FFT is over a universe of size N -> O~(N); the
  sparse-convolution variant has output support <= B^2 -> O~(B^2). Either way
  >= min(N, B^2).
Optimizing the resulting total (setup + collection) over B gives >= N^{2/3} in all
cases -- strictly worse than Pollard rho (sqrt N).

## Consequence
The prime-field m=3 index-calculus barrier is ROBUST to the full standard
algorithmic toolkit (MITM, algebraic elimination, multipoint evaluation,
FFT/convolution). This substantially strengthens the reduction to 3SUM-Indexing:
not only is the problem 3SUM-Indexing in form, but every known 3SUM technique
fails to beat sqrt N here. A sub-rho algorithm therefore requires a genuinely
new idea that beats 3SUM-Indexing by exploiting non-obvious curve structure --
the open crux (SP4 / IDEA-20260722-002).

## Boundaries (honest)
- These are the standard techniques; the result does not prove NO technique works
  (that is the open crux, equivalent to a 3SUM-Indexing breakthrough).
- The group-FFT and multipoint-evaluation cost statements are standard-complexity
  analysis; MITM and root-finding were verified computationally at toy scale.
- A negative/robustness result that maps the barrier's extent -- not a breakthrough.
