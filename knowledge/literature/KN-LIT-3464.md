---
id: KN-LIT-3464
type: literature
title: "Domain Extension for MACs Beyond the Birthday Barrier"
authors:
  - "Yevgeniy Dodis"
  - "John Steinberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, implementation, quantum, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given an n-bit to n-bit MAC (e.g., a fixed key blockcipher) with MAC security ε against q queries, we design a variable-length MAC achieving MAC security O(εq poly(n)) against queries of total length qn. In particular, our construction is the first to break the “birthday barrier” for MAC domain extension from noncompressing primitives, since our security bound is meaningful even for q = 2n /poly(n) (assuming ε is the best possible O(1/2n )).

## Key claims (as reported)
- In contrast, the previous best construction for MAC domain extension for n-bit to n-bit primitives, due to Dodis and Steinberger [11], achieved MAC security of O(εq 2 (log q)2 ), which means that q cannot cross the “birthday bound” of 2n/2 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320328 (1).pdf`
- `downloads/66320328 (2).pdf`
- `downloads/66320328 (3).pdf`
- `downloads/66320328.pdf`
