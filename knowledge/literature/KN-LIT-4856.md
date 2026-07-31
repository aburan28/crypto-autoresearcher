---
id: KN-LIT-4856
type: literature
title: "Masking and Dual-rail Logic Don’t Add Up"
authors:
  - "Patrick Schaumont"
  - "Kris Tiri"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masked logic styles use a random mask bit to de-correlate the power consumption of the circuit from the state of the algorithm. The effect of the random mask bit is that the circuit switches between two complementary states with a different power profile.

## Key claims (as reported)
- Earlier work has shown that the mask-bit value can be estimated from the power consumption profile, and that masked logic remains susceptible to classic power attacks after only a simple filtering operation.
- In this contribution we will show that this conclusion also holds for masked pre-charged logic styles and for all practical implementations of masked dual-rail logic styles.
- Up to now, it was believed that masking and dual-rail can be combined to provide a routing-insensitive logic style.
- We will show that this assumption is not correct.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270095 (1).pdf`
- `downloads/47270095 (2).pdf`
- `downloads/47270095 (3).pdf`
- `downloads/47270095.pdf`
