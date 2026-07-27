---
id: KN-LIT-2225
type: literature
title: "A Side-Channel Analysis Resistant Description of the AES S-box ?"
authors:
  - "Elisabeth Oswald"
  - "Stefan Mangard"
  - "Norbert Pramstaller"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, implementation, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
So far, efficient algorithmic countermeasures to secure the AES algorithm against (first-order) differential side-channel attacks have been very expensive to implement. In this article, we introduce a new masking countermeasure which is not only secure against first-order sidechannel attacks, but which also leads to relatively small implementations compared to other masking schemes implemented in dedicated hardware.

## Key claims (as reported)
- Our approach is based on shifting the computation of the finite field inversion in the AES S-box down to GF (4).
- In this field, the inversion is a linear operation and therefore it is easy to mask.
- Summarizing, the new masking scheme combines the concepts of multiplicative and additive masking in such a way that security against firstorder side-channel attacks is maintained, and that small implementations in dedicated hardware can be achieved.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/35570401 (1).pdf`
- `downloads/35570401 (2).pdf`
- `downloads/35570401 (3).pdf`
- `downloads/35570401.pdf`
