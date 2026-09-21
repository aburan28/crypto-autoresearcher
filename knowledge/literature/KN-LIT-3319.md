---
id: KN-LIT-3319
type: literature
title: "Cryptography from Compression Functions: The UCE Bridge to the ROM"
authors:
  - "Mihir Bellare"
  - "Viet Tung Hoang"
  - "Sriram Keelveedhi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper suggests and explores the use of UCE security for the task of turning VIL-ROM schemes into FIL-ROM ones. The benefits we offer over indifferentiability, the current leading method for this task, are the ability to handle multi-stage games and greater efficiency.

## Key claims (as reported)
- The paradigm consists of (1) Showing that a VIL UCE function can instantiate the VIL RO in the scheme, and (2) Constructing the VIL UCE function given a FIL random oracle.
- The main technical contributions of the paper are domain extension transforms that implement the second step.
- Leveraging known results for the first step we automatically obtain FIL-ROM constructions for several primitives whose security notions are underlain by multi-stage games.Our first domain extender exploits indifferentiability, showing that although the latter does not work directly for multi-stage games it can be used indirectly, through UCE, as a tool for this end.
- Our second domain extender targets performance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160295 (1).pdf`
- `downloads/86160295 (2).pdf`
- `downloads/86160295 (3).pdf`
- `downloads/86160295 (4).pdf`
- `downloads/86160295 (5).pdf`
- `downloads/86160295.pdf`
