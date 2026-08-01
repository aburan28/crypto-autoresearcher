---
id: KN-LIT-2566
type: literature
title: "APE: Authenticated Permutation-Based"
authors:
  - "Bart Mennink"
  - "Nicky Mouha"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The domain of lightweight cryptography focuses on cryptographic algorithms for extremely constrained devices. It is very costly to avoid nonce reuse in such environments, because this requires either a hardware source of randomness, or non-volatile memory to store a counter.

## Key claims (as reported)
- At the same time, a lot of cryptographic schemes actually require the nonce assumption for their security.
- In this paper, we propose APE as the first permutation-based authenticated encryption scheme that is resistant against nonce misuse.
- We formally prove that APE is secure, based on the security of the underlying permutation.
- To decrypt, APE processes the ciphertext blocks in reverse order, and uses inverse permutation calls.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400171 (1).pdf`
- `downloads/85400171 (2).pdf`
- `downloads/85400171 (3).pdf`
- `downloads/85400171.pdf`
