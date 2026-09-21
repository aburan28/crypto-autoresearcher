---
id: KN-LIT-6772
type: literature
title: "spongent: A Lightweight Hash Function"
authors:
  - "Kerem Varıcı"
  - "Ingrid Verbauwhede"
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
This paper proposes spongent – a family of lightweight hash functions with hash sizes of 88 (for preimage resistance only), 128, 160, 224, and 256 bits based on a sponge construction instantiated with a present-type permutation, following the hermetic sponge strategy. Its smallest implementations in ASIC require 738, 1060, 1329, 1728, and 1950 GE, respectively.

## Key claims (as reported)
- To our best knowledge, at all security levels attained, it is the hash function with the smallest footprint in hardware published so far, the parameter being highly technology dependent. spongent offers a lot of flexibility in terms of serialization degree and speed.
- We explore some of its numerous implementation trade-offs.
- We furthermore present a security analysis of spongent.
- Basing the design on a present-type primitive provides confidence in its security with respect to the most important attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170311 (1).pdf`
- `downloads/69170311 (2).pdf`
- `downloads/69170311 (3).pdf`
- `downloads/69170311.pdf`
