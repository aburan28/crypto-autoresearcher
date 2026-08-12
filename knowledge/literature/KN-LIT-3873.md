---
id: KN-LIT-3873
type: literature
title: "Fiat-Shamir Security of FRI and Related SNARKs"
authors:
  - "Alexander R. Block"
  - "Albert Garreta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We establish new results on the Fiat-Shamir (FS) security of several protocols that are widely used in practice, and we provide general tools for establishing similar results for others. More precisely, we: (1) prove the FS security of the FRI and batched FRI protocols; (2) analyze a general class of protocols, which we call δ-correlated, that use low-degree proximity testing as a subroutine (this includes many “Plonk-like” protocols (e.g., Plonky2 and Redshift), ethSTARK, RISC Zero, etc.); and (3) prove FS security of the aforementioned “Plonk-like” protocols, and sketch how to prove the same for the others.

## Key claims (as reported)
- We obtain our first result by analyzing the round-by-round (RBR) soundness and RBR knowledge soundness of FRI.
- For the second result, we prove that if a δ-correlated protocol is RBR (knowledge) sound under the assumption that adversaries always send low-degree polynomials, then it is RBR (knowledge) sound in general.
- Equipped with this tool, we prove our third result by formally showing that “Plonk-like” protocols are RBR (knowledge) sound under the assumption that adversaries always send low-degree polynomials.
- We then outline analogous arguments for the remainder of the aforementioned protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438135 (1).pdf`
- `downloads/14438135.pdf`
