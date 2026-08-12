---
id: KN-LIT-7012
type: literature
title: "The Locality of Searchable Symmetric Encryption"
authors:
  - "David Cash"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proves a lower bound on the trade-off between server storage size and the locality of memory accesses in searchable symmetric encryption (SSE). Namely, when encrypting an index of N identifier/keyword pairs, the encrypted index must have size ω(N ) or the scheme must perform searching with ω(1) non-contiguous reads to memory or the scheme must read many more bits than is necessary to compute the results.

## Key claims (as reported)
- Recent implementations have shown that nonlocality of server memory accesses create a throughput-bottleneck on very large databases.
- Our lower bound shows that this is due to the security notion and not a defect of the constructions.
- An upper bound is also given in the form of a new SSE construction with an O(N log N ) size encrypted index that performs O(log N ) reads during a search.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410155 (1).pdf`
- `downloads/84410155 (2).pdf`
- `downloads/84410155 (3).pdf`
- `downloads/84410155.pdf`
