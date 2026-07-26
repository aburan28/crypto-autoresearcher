---
id: KN-LIT-2900
type: literature
title: "Ciminion: Symmetric Encryption Based on Toffoli-Gates over Large Finite Fields"
authors:
  - "Christoph Dobraunig"
  - "Lorenzo Grassi"
  - "Anna Guinet"
  - "Daniël Kuijsters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, cryptanalysis, fhe, finite-field, groebner, mpc, pairing, prime-field, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Motivated by new applications such as secure Multi-Party Computation (MPC), Fully Homomorphic Encryption (FHE), and ZeroKnowledge proofs (ZK), the need for symmetric encryption schemes that minimize the number of field multiplications in their natural algorithmic description is apparent. This development has brought forward many dedicated symmetric encryption schemes that minimize the number of multiplications in F2n or Fp , with p being prime.

## Key claims (as reported)
- These novel schemes have lead to new cryptanalytic insights that have broken many of said schemes.
- Interestingly, to the best of our knowledge, all of the newly proposed schemes that minimize the number of multiplications use those multiplications exclusively in S-boxes based on a power mapping that is typically x3 or x−1 .
- Furthermore, most of those schemes rely on complex and resource-intensive linear layers to achieve a low multiplication count.
- In this paper, we present Ciminion, an encryption scheme minimizing the number of field multiplications in large binary or prime fields, while using a very lightweight linear layer.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960187 (1).pdf`
- `downloads/126960187.pdf`
