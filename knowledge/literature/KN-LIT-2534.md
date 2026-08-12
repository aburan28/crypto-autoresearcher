---
id: KN-LIT-2534
type: literature
title: "Analyzing the complexity of reference post-quantum software"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, pairing, pqc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Constant-time C software for various post-quantum KEMs has been submitted by the KEM design teams to the SUPERCOP testing framework. The ref/*.c and ref/*.h files together occupy, e.g., 848 lines for ntruhps4096821, 928 lines for ntruhrss701, 1316 lines for sntrup1277, and 2613 lines for kyber1024.

## Key claims (as reported)
- It is easy to see that these numbers overestimate the inherent complexity of software for these KEMs.
- It is more difficult to systematically measure this inherent complexity.
- This paper takes these KEMs as case studies and applies consistent rules to streamline the ref software for the KEMs, while still passing SUPERCOP’s tests and preserving the decomposition of specified KEM operations into functions.
- The resulting software occupies 381 lines for ntruhps4096821, 385 lines for ntruhrss701, 472 lines for kyber1024, and 478 lines for sntrup1277.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/pqcomplexity-20231217.pdf`
- `downloads/pqcomplexity-20231221.pdf`
