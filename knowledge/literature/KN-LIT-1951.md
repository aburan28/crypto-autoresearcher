---
id: KN-LIT-1951
type: literature
title: "Verifiable Bootstrapping from Lattice-based Folding"
authors:
  - "Amit Deo"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1127"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1127"
tags: [elliptic-curve, fhe, hash, lattice, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We explicitly construct and benchmark the first lattice-based IVC scheme from folding. The scheme supports customizable constraint systems over rings which we exploit to obtain proofs of correct execution of an FHE bootstrapping, a critical component of verifiable FHE.

## Key claims (as reported)
- Notably and of independent interest, we introduce a novel CCS relation capable of performing automorphism stability checks which yields better expressivity for CCS over rings.
- We use this new relation to arithmetize the folding scheme verifier as well as TFHE’s bootstrapping operation, and measure the performance of our folding scheme implementation on this arithmetization.
- Benchmarks indicate smaller proofs compared to the state of the art at the cost of a sharp increase in prover and verifier time.
- Lastly, we consider the security of folding-based IVC schemes with a super-constant number of recursive rounds and give an argument for the knowledge soundness of our construction in the ROM.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1127.pdf`
