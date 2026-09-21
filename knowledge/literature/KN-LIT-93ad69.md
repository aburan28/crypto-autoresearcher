---
id: KN-LIT-93ad69
type: literature
title: "Perturbation of Hankel moment singular values and supersingular endomorphism rings via CVP"
authors:
  - "Radmir Isyanov"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1586 (preprint)"
identifiers:
  eprint: iacr:2026/1586
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1586"
tags: [hankel, moments, supersingular, endomorphism-ring, cvp, p-adic, quantum-oracle]
confidence: unverified
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Presents two methodologically related results for post-quantum algebraic
computation. Part I (spectral): an explicit sufficient noise bound under which
the signal subspace of the Hankel matrix of power moments of supersingular
j-invariants stays strictly separated from the noise subspace, so roots of a
separable polynomial are recovered deterministically (propagation constant via
Vandermonde condition number; sharpened p-adically via the Teichmüller lift,
giving cond_p = 1 and an exact p-adic super-resolution law for precision loss).
Part II (arithmetic): reduction of computing a Z-basis of End(E) to a rank-4
closest-vector problem (CVP), with a Shor-based quantum oracle for Weil-pairing
discrete logarithms recovering the exact Gram matrix of the norm form in
O(poly log p) time, followed by LLL in fixed dimension.

## Key claims (as reported)
- Hankel-singular-value separation for supersingular j-invariant moments, plus
  p-adic strengthening.
- End(E) computation → rank-4 CVP; quantum ECDLP oracle (Weil pairing) helps
  recover the remaining Gram matrix information (authors claim LLL in fixed
  dimension finishes).

## Relevance
- On the ECDLP side, the supersingular endomorphism (End(E)) computation is
  adjacent to CSIDH/SIDH-style solving; the "quantum oracle reduces End(E) to
  CVP" claim is relevant as a quantum cost model, but the paper's correctness
  and completion claims could not be fully verified (single-author arXiv-style
  preprint on ePrint; "fully computed pipeline" claim unaccompanied by
  reproducible artifact in the first page text).

## Not verified here
- Full correctness of Part II (the reduction to CVP and use of Weil DL oracle)
  not verified. Recorded as unverified lead; the claims are per ePrint
  preprint, not peer review.