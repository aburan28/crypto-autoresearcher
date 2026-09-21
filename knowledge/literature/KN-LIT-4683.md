---
id: KN-LIT-4683
type: literature
title: "Leakage-Resilient Circuits without Computational Assumptions"
authors:
  - "Stefan Dziembowski⋆⋆"
  - "Sebastian Faust⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Physical cryptographic devices inadvertently leak information through numerous side-channels. Such leakage is exploited by socalled side-channel attacks, which often allow for a complete security breache.

## Key claims (as reported)
- A recent trend in cryptography is to propose formal models to incorporate leakage into the model and to construct schemes that are provably secure within them.
- We design a general compiler that transforms any cryptographic scheme, e.g., a block-cipher, into a functionally equivalent scheme which is resilient to any continual leakage provided that the following three requirements are satisfied: (i) in each observation the leakage is bounded, (ii) different parts of the computation leak independently, and (iii) the randomness that is used for certain operations comes from a simple (nonuniform) distribution.
- In contrast to earlier work on leakage resilient circuit compilers, which relied on computational assumptions, our results are purely information-theoretic.
- In particular, we do not make use of public key encryption, which was required in all previous works.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940195 (1).pdf`
- `downloads/71940195 (2).pdf`
- `downloads/71940195 (3).pdf`
- `downloads/71940195.pdf`
