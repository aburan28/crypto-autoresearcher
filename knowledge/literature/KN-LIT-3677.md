---
id: KN-LIT-3677
type: literature
title: "Encryption and Applications"
authors:
  - "Structure Preserving"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present the first CCA-secure public key encryption scheme that is structure preserving, i.e., our encryption scheme uses only algebraic operations. In particular, it does not use hash-functions or interpret group elements as bit-strings.

## Key claims (as reported)
- This makes our scheme a perfect building block for cryptographic protocols where parties for instance want to prove properties about ciphertexts to each other or to jointly compute ciphertexts.
- Our scheme is very efficient and is secure against adaptive chosen ciphertext attacks.
- We also provide a few example protocols for which our scheme is useful.
- For instance, we present an efficient protocol for two parties, Alice and Bob, that allows them to jointly encrypt a given function of their respective secret inputs such that only Bob learns the resulting ciphertext, yet they are both ensured of the computation’s correctness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730088 (1).pdf`
- `downloads/70730088 (2).pdf`
- `downloads/70730088 (3).pdf`
- `downloads/70730088.pdf`
