---
id: KN-LIT-1705
type: literature
title: "Jindo: Practical Lattice-Based Polynomial Commitments for Client-Side Proving"
authors:
  - "Intak Hwang"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/044"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/044"
tags: [dlp, elliptic-curve, finite-field, glv-gls, lattice, pairing, pqc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present Jindo, a new lattice-based polynomial commitment scheme (PCS) optimized for client-side proving, which requires fast prover performance while supporting evaluation hiding and flexible parameter regimes. To achieve this, we build Jindo on the previous lattice-based PCSs CELPC (CRYPTO’24) and Greyhound (CRYPTO’24), which exhibit fast proving performance but have several limitations for client-side proving.

## Key claims (as reported)
- We resolve these limitations by developing a new polynomial evaluation protocol that supports multilinear polynomials, diverse field choices, sublinear masking overhead for evaluation hiding, and cube-root verification and communication complexity.
- Our implementation shows that Jindo improves upon CELPC by about an order of magnitude across all metrics, including proof generation, verification, and proof size.
- Compared with the recent evaluation hiding code-based PCS PIP-FRI (USENIX’26), Jindo provides an order of magnitude faster proof generation while yielding similar verification and communication costs.
- Furthermore, when compiling the PIOP of Buckler (CCS’25) to prove the validity of an RLWE sample, Jindo outperforms CELPC by an order of magnitude across all metrics.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-044.pdf`
