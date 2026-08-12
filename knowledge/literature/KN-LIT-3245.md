---
id: KN-LIT-3245
type: literature
title: "Cryptanalysis of Masked Ciphers: A not so Random Idea"
authors:
  - "Tim Beyne"
  - "Siemen Dhooghe"
  - "Zhenda Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A new approach to the security analysis of hardware-oriented masked ciphers against second-order side-channel attacks is developed. By relying on techniques from symmetric-key cryptanalysis, concrete security bounds are obtained in a variant of the probing model that allows the adversary to make only a bounded, but possibly very large, number of measurements.

## Key claims (as reported)
- Specifically, it is formally shown how a boundedquery variant of robust probing security can be reduced to the linear cryptanalysis of masked ciphers.
- As a result, the compositional issues of higher-order threshold implementations can be overcome without relying on fresh randomness.
- From a practical point of view, the aforementioned approach makes it possible to transfer many of the desirable properties of first-order threshold implementations, such as their low randomness usage, to the second-order setting.
- For example, a straightforward application to the block cipher LED results in a masking using less than 700 random bits including the initial sharing.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491290 (1).pdf`
- `downloads/12491290.pdf`
