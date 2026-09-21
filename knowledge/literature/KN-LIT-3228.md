---
id: KN-LIT-3228
type: literature
title: "Cryptanalysis of ESSENCE"
authors:
  - "Gaëtan Leurent"
  - "Willi Meier"
  - "Thomas Peyrin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ESSENCE is a hash function submitted to the NIST Hash Competition that stands out as a hardware-friendly and highly parallelizable design. Previous analysis showed some non-randomness in the compression function which could not be extended to an attack on the hash function and ESSENCE remained unbroken.

## Key claims (as reported)
- Preliminary analysis in its documentation argues that it resists standard differential cryptanalysis.
- This paper disproves this claim, showing that advanced techniques can be used to significantly reduce the cost of such attacks: using a manually found differential characteristic and an advanced search algorithm, we obtain collision attacks on the full ESSENCE-256 and ESSENCE512, with respective complexities 267.4 and 2134.7 .
- In addition, we show how to use these attacks to forge valid (message, MAC) pairs for HMACESSENCE-256 and HMAC-ESSENCE-512, essentially at the same cost as a collision.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470137 (1).pdf`
- `downloads/61470137 (2).pdf`
- `downloads/61470137 (3).pdf`
- `downloads/61470137.pdf`
