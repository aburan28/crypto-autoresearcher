---
id: KN-LIT-6534
type: literature
title: "Security-Preserving Distributed Samplers: How to Generate any CRS in One Round without Random Oracles"
authors:
  - "Damiano Abram"
  - "Brent Waters"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, pairing, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A distributed sampler is a way for several mutually distrusting parties to non-interactively generate a common reference string (CRS) that all parties trust. Previous work constructs distributed samplers in the random oracle model, or in the standard model with very limited security guarantees.

## Key claims (as reported)
- This is no accident, as standard model distributed samplers with full security were shown impossible.
- In this work, we provide new definitions for distributed samplers which we show achieve meaningful security guarantees in the standard model.
- In particular, our notion implies that the hardness of a wide range of security games is preserved when the CRS is replaced with a distributed sampler.
- We also show how to realize our notion of distributed samplers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850448 (1).pdf`
- `downloads/140850448.pdf`
