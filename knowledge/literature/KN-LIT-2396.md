---
id: KN-LIT-2396
type: literature
title: "Algebraic Cryptanalysis of STARK-Friendly Designs: Application to MARVELlous and MiMC"
authors:
  - "Martin R. Albrecht"
  - "Carlos Cid"
  - "Lorenzo Grassi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, cryptanalysis, groebner, hash, lattice, pairing, pqc, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The block cipher Jarvis and the hash function Friday, both members of the MARVELlous family of cryptographic primitives, are among the first proposed solutions to the problem of designing symmetric-key algorithms suitable for transparent, post-quantum secure zero-knowledge proof systems such as ZK-STARKs. In this paper we describe an algebraic cryptanalysis of Jarvis and Friday and show that the proposed number of rounds is not sufficient to provide adequate security.

## Key claims (as reported)
- In Jarvis, the round function is obtained by combining a finite field inversion, a full-degree affine permutation polynomial and a key addition.
- Yet we show that even though the high degree of the affine polynomial may prevent some algebraic attacks (as claimed by the designers), the particular algebraic properties of the round function make both Jarvis and Friday vulnerable to Gröbner basis attacks.
- We also consider MiMC, a block cipher similar in structure to Jarvis.
- However, this cipher proves to be resistant against our proposed attack strategy.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210231 (1).pdf`
- `downloads/119210231.pdf`
