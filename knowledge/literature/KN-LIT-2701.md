---
id: KN-LIT-2701
type: literature
title: "Biclique Cryptanalysis of the Full AES"
authors:
  - "Andrey Bogdanov⋆⋆"
  - "Dmitry Khovratovich"
  - "Christian Rechberger⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since Rijndael was chosen as the Advanced Encryption Standard (AES), improving upon 7-round attacks on the 128-bit key variant (out of 10 rounds) or upon 8-round attacks on the 192/256-bit key variants (out of 12/14 rounds) has been one of the most difficult challenges in the cryptanalysis of block ciphers for more than a decade. In this paper, we present the novel technique of block cipher cryptanalysis with bicliques, which leads to the following results: – The first key recovery method for the full AES-128 with computational complexity 2126.1 . – The first key recovery method for the full AES-192 with computational complexity 2189.7 . – The first key recovery method for the full AES-256 with computational complexity 2254.4 . – Key recovery methods with lower complexity for the reduced-round versions of AES not considered before, including cryptanalysis of 8-round AES-128 with complexity 2124.9 . – Preimage search for compression functions based on the full AES versions faster than brute force.

## Key claims (as reported)
- In contrast to most shortcut attacks on AES variants, we do not need to assume related-keys.
- Most of our techniques only need a very small part of the codebook and have low memory requirements, and are practically verified to a large extent.
- As our cryptanalysis is of high computational complexity, it does not threaten the practical use of AES in any way.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730339 (1).pdf`
- `downloads/70730339 (2).pdf`
- `downloads/70730339 (3).pdf`
- `downloads/70730339.pdf`
