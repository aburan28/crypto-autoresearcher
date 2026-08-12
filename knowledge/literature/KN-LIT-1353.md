---
id: KN-LIT-1353
type: literature
title: "Circuit-Succinct Algebraic Batch Arguments from Projective Functional Commitments?"
authors:
  - "David Balbás"
  - "Dario Fiore"
  - "Russell W. F. Lai"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1943"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1943"
tags: [hash, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Batch arguments for NP (BARGs) are non-interactive proof systems that allow a prover to convince a verifier that k NP statements x1 , . . . , xk are valid relative to some circuit C, i.e. there exist witnesses wi such that (xi , wi ) satisfy C for all i, while the proof size remains sublinear in k. Most existing BARG constructions achieve a proof size of |π| = poly(λ, |C|, log k) for large or not explicitly specified poly acting on |C|, with two exceptions: 1.

## Key claims (as reported)
- Devadas et al. and Paneth and Pass’s “rate-1” constructions [FOCS’22] achieve |π| = |w| + O(|w|/λ) + poly(λ, log k) (with matching verification time for Paneth and Pass), but for not explicitly specified poly due to non-black-box use of cryptographic primitives.
- Waters and Wu’s algebraic (pairing-based) construction [Crypto’22] achieves |π| = O(λ · |C|).
- In this work, we give the first algebraic (pairing-based) construction of BARG that achieves proof size and online verifier runtime O(λ · |w|).
- We achieve our result by means of a compiler which builds a BARG generically from a projective chainable functional commitment (PCFC), which supports somewhere extraction, subvector projection, and functional openings.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1943.pdf`
