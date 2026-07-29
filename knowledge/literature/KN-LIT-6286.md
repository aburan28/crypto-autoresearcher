---
id: KN-LIT-6286
type: literature
title: "Ring-based Identity Based Encryption"
authors:
  - "Asymptotically Shorter MPK"
  - "Tighter Security"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice, mov-fr, mpc, pairing, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work constructs an identity based encryption from the ring learning with errors assumption (RLWE), with shorter master public keys and tighter security analysis. To achieve this, we develop three new methods: (1) a new homomorphic equality test method using nice algebraic structures of the rings, (2) a new family of hash functions with natural homomorphic evaluation algorithms, and (3) a new insight for tighter reduction analyses.

## Key claims (as reported)
- These methods can be used to improve other important cryptographic tasks, and thus are of general interests.
- Particularly, our homomorphic equality test method can derive a new method for packing/unpacking GSW-style encodings, showing a new non-trivial advantage of RLWE over the plain LWE.
- Moreover, our new insight for tighter analyses can improve the analyses of all the currently known partition-based IBE designs, achieving the best of the both from prior analytical frameworks of Waters (Eurocrypt ’05) and Bellare and Ristenpart (Eurocrypt ’09).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420128 (1).pdf`
- `downloads/130420128.pdf`
