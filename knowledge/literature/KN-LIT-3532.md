---
id: KN-LIT-3532
type: literature
title: "Efficient Boolean Search over Encrypted Data with Reduced Leakage"
authors:
  - "Sarvar Patel"
  - "Giuseppe Persiano"
  - "Joon Young Seo"
  - "Kevin Yeo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Encrypted multi-maps enable outsourcing the storage of a multi-map to an untrusted server while maintaining the ability to query privately. We focus on encrypted Boolean multi-maps that support arbitrary Boolean queries over the multi-map.

## Key claims (as reported)
- Kamara and Moataz [Eurocrypt’17] presented the first encrypted multi-map, BIEX, that supports CNF queries with optimal communication, worst-case sublinear search time and non-trivial leakage.
- We improve on previous work by presenting a new construction CNFFilter for CNF queries with significantly less leakage than BIEX, while maintaining both optimal communication and worst-case sublinear search time.
- As a direct consequence our construction shows additional resistance to leakage-abuse attacks in comparison to prior works.
- For most CNF queries, CNFFilter avoids leaking the result sets for any singleton queries for labels appearing in the CNF query.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900129 (1).pdf`
- `downloads/130900129.pdf`
