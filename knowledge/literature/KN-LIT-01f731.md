---
id: KN-LIT-01f731
type: literature
title: "A new sieving-style information-set decoding algorithm"
authors:
  - "Qian Guo"
  - "Thomas Johansson"
  - "Vu Nguyen"
year: 2023
venue: null
identifiers:
  eprint: "iacr:2023/247"
  doi: "10.1109/tit.2024.3457150"
  arxiv: null
  url: "https://eprint.iacr.org/2023/247"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, sieving, nearest-neighbor]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Introduces the **sieving-style** information-set decoding algorithm: rather than
the meet-in-the-middle list construction of the MMT/BJMM family, the inner
search is run as a sieve, repeatedly combining a list of vectors to produce
shorter ones. This is the paper the later sieving-style ISD line
([[KN-LIT-47b29b]], and asymptotically [[KN-LIT-182bfb]]) builds on.

## Key claims (as reported)
- A new ISD algorithm using a sieving inner loop.
- Positioned as a new *style* of ISD rather than a parameter refinement of the existing family.

## Relevance to this program
Held as the origin point of the sieving-style branch. Its value to this program
is as a worked example of the highest-value move in
`docs/inventor-protocol.md`: **replacing a subroutine's data structure changed
the algorithm family**, rather than tuning constants within it. Proposals in
this program are asked to identify that kind of substitution explicitly.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/247 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1109/tit.2024.3457150).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The claimed exponent, and how it compares to BJMM at Classic McEliece
parameters, are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
