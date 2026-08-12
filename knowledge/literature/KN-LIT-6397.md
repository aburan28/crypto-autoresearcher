---
id: KN-LIT-6397
type: literature
title: "Secret Can Be Public: Low-Memory AEAD Mode for High-Order Masking"
authors:
  - "Yusuke Naito"
  - "Yu Sasaki"
  - "Takeshi Sugawara"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new AEAD mode of operation for an efficient countermeasure against side-channel attacks. Our mode achieves the smallest memory with high-order masking, by minimizing the states that are duplicated in masking.

## Key claims (as reported)
- An s-bit key-dependent state is necessary for achieving s-bit security, and the conventional schemes always protect the entire s bits with masking.
- We reduce the protected state size by introducing an unprotected state in the key-dependent state: we protect only a half and give another half to a side-channel adversary.
- Ensuring independence between the unprotected and protected states is the key technical challenge since mixing these states reveals the protected state to the adversary.
- We propose a new mode HOMA that achieves s-bit security using a tweakable block cipher with the s/2-bit block size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070065 (1).pdf`
- `downloads/135070065.pdf`
