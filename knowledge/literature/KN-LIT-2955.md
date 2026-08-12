---
id: KN-LIT-2955
type: literature
title: "Collisions for Step-Reduced SHA-256"
authors:
  - "Ivica Nikolić"
  - "Alex Biryukov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article we find collisions for step-reduced SHA-256. We develop a differential that holds with high probability if the message satisfies certain conditions.

## Key claims (as reported)
- We solve the equations that arise from the conditions.
- Due to the carefully chosen differential and word differences, the message expansion of SHA-256 has little effect on spreading the differences in the words.
- This helps us to find full collision for 21-step reduced SHA-256, semi-free start collision, i.e. collision for a different initial value, for 23-step reduced SHA-256, and semi-free start near collision (with only 15 bit difference out of 256 bits) for 25-step reduced SHA-256.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860001 (1).pdf`
- `downloads/50860001 (2).pdf`
- `downloads/50860001 (3).pdf`
- `downloads/50860001.pdf`
