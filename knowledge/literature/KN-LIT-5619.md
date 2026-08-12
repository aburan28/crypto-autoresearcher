---
id: KN-LIT-5619
type: literature
title: "One-Hot Conversion: Towards Faster Table-based A2B Conversion"
authors:
  - "Jan-Pieter D’Anvers"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pairing, pqc, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Arithmetic to Boolean masking (A2B) conversion is a crucial technique in the masking of lattice-based post-quantum cryptography. It is also a crucial part of building a masked comparison which is one of the hardest to mask building blocks for active secure lattice-based encryption.

## Key claims (as reported)
- We first present a new method, called one-hot conversion, to efficiently convert from higher-order arithmetic masking to Boolean masking using a variant of the higher-order table-based conversion of Coron et al.
- Secondly, we specialize our method to perform arithmetic to 1-bit Boolean functions.
- Our one-hot function can be applied to masking lattice-based encryption building blocks such as masked comparison or to determine the most significant bit of an arithmetically masked variable.
- In our benchmarks on a Cortex M4 processor, a speedup of 15 times is achieved over state-of-the-art table-based A2B conversions, bringing table-based A2B conversions within the performance range of the Boolean circuit-based A2B conversions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004018 (1).pdf`
- `downloads/14004018.pdf`
