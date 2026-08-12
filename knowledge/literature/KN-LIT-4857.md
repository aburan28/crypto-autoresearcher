---
id: KN-LIT-4857
type: literature
title: "Masking at Gate Level in the Presence of Glitches"
authors:
  - "Wieland Fischer"
  - "Berndt M. Gammel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It has recently been shown that logic circuits in the implementation of cryptographic algorithms, although protected by “secure” random masking schemes, leak side-channel information, which can be exploited in differential power attacks [14]. The leak is due to the fact that the mathematical models describing the gates neglected multiple switching of the outputs of the gates in a single clock cycle.

## Key claims (as reported)
- This effect, however, is typical for CMOS circuits and known as glitching.
- Hence several currently known masking schemes are not secure in theory or practice.
- Solutions for DPA secure circuits based on logic styles which do not show glitches have several disadvantages in practice.
- In this paper, we refine the model for the power consumption of CMOS gates taking into account the side-channel of glitches.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/014 (1).pdf`
- `downloads/014 (2).pdf`
- `downloads/014 (3).pdf`
- `downloads/014.pdf`
