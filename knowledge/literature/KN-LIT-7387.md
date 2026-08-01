---
id: KN-LIT-7387
type: literature
title: "Universal One-Way"
authors:
  - "Salil Vadhan"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper revisits the construction of Universal One-Way Hash Functions (UOWHFs) from any one-way function due to Rompel (STOC 1990). We give a simpler construction of UOWHFs, which also obtains better efficiency and security.

## Key claims (as reported)
- The construction exploits a strong connection to the recently introduced notion of inaccessible entropy (Haitner et al.
- With this perspective, we observe that a small tweak of any one-way function f is already a weak form of a UOWHF: Consider F (x, i) that outputs the i-bit long prefix of f (x).
- If F were a UOWHF then given a random x and i it would be hard to come up with x0 6= x such that F (x, i) = F (x0 , i).
- While this may not be the case, we show (rather easily) that it is hard to sample x0 with almost full entropy among all the possible such values of x0 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320273 (1).pdf`
- `downloads/66320273 (2).pdf`
- `downloads/66320273 (3).pdf`
- `downloads/66320273.pdf`
