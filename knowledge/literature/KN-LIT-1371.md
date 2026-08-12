---
id: KN-LIT-1371
type: literature
title: "Derivative-Free Richelot Isogenies via Subresultants:"
authors:
  - "Algebraic Equivalence"
  - "Certified Guarded Computation"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2145"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2145"
tags: [endomorphism, isogeny, jacobian, mov-fr, pairing, pqc, quantum, sidh-csidh, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a derivative-free Richelot (2,2)-isogeny formulation using first subresultants and a canonical quadratic lift. Over odd characteristic, we prove its algebraic equivalence in F p [x] to the classical Wronskian under natural normalization.

## Key claims (as reported)
- Leveraging this, we introduce the Guarded Subresultant Route (GSR): a deterministic evaluator with constant-size algebraic guards, lightweight post-check, and at most one affine retry.
- It returns a certified triple (U, V, W) or rejects non-admissible inputs, eliminating differentiation while enforcing admissibility and auditable control flow.
- Prototypes show the core 1.46–1.70× faster than Wronskian across varied primes, with GSR adding ≈ 5–10 μs constant overhead.
- The backend-agnostic design suits batched and hierarchical genus-2 isogeny pipelines for reproducible computation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2145.pdf`
