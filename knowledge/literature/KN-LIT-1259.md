---
id: KN-LIT-1259
type: literature
title: "LeOPaRd: Towards Practical Post-Quantum Oblivious PRFs via 2HashDH Paradigm"
authors:
  - "Muhammed F. Esgin"
  - "Ron Steinfeld"
  - "Erkan Tairi⋆"
  - "Jie Xu"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1615"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1615"
tags: [fhe, lattice, mpc, pairing, pqc, protocol, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we introduce a more efficient post-quantum oblivious PRF (OPRF) design, called LeOPaRd. Our proposal is round-optimal and supports verifiability and partial obliviousness, all of which are important for practical applications.

## Key claims (as reported)
- The main technical novelty of our work is a new method for computing samples of MLWE (Module Learning With Errors) in a two-party setting.
- To do this, we introduce a new family of (interactive) lattice problems, called MLWE-PRF with re-use (MLWE-PRF-RU).
- Here, the adversary is given a mix of MLWE and PRF samples where each PRF error is dependent on an adversarially-chosen matrix and the MLWE error.
- We rigorously study the hardness of MLWE-PRF-RU and provide a reduction from the standard MLWE to MLWE-PRF-RU, establishing a strong security foundation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1615.pdf`
