---
id: KN-LIT-2434
type: literature
title: "Alzette: a 64-bit ARX-box"
authors:
  - "Christof Beierle"
  - "Alex Biryukov"
  - "Luan Cardoso dos Santos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
S-boxes are the only source of non-linearity in many symmetric primitives. While they are often defined as being functions operating on a small space, some recent designs propose the use of much larger ones (e.g., 32 bits).

## Key claims (as reported)
- In this context, an S-box is then defined as a subfunction whose cryptographic properties can be estimated precisely.
- We present a 64-bit ARX-based S-box called Alzette, which can be evaluated in constant time using only 12 instructions on modern CPUs.
- Its parallel application can also leverage vector (SIMD) instructions.
- One iteration of Alzette has differential and linear properties comparable to those of the AES S-box, and two are at least as secure as the AES super S-box.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171388 (1).pdf`
- `downloads/12171388.pdf`
