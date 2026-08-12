---
id: KN-LIT-4768
type: literature
title: "Locality-Preserving Oblivious RAM Gilad Asharov1?"
authors:
  - "Rafael Pass"
  - "Ling Ren∗∗"
  - "Elaine Shi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAMs, introduced by Goldreich and Ostrovsky [JACM’96], compile any RAM program into one that is “memory oblivious”, i.e., the access pattern to the memory is independent of the input. All previous ORAM schemes, however, completely break the locality of data accesses (for instance, by shuffling the data to pseudorandom positions in memory).

## Key claims (as reported)
- In this work, we initiate the study of locality-preserving ORAMs — ORAMs that preserve locality of the accessed memory regions, while leaking only the lengths of contiguous memory regions accessed.
- Our main results demonstrate the existence of a locality-preserving ORAM with poly-logarithmic overhead both in terms of bandwidth and locality.
- We also study the tradeoff between locality, bandwidth and leakage, and show that any scheme that preserves locality and does not leak the lengths of the contiguous memory regions accessed, suffers from prohibitive bandwidth.
- To the best of our knowledge, before our work, the only works combining locality and obliviousness were for symmetric searchable encryption [e.g., Cash and Tessaro (EUROCRYPT’14), Asharov et al.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760301 (1).pdf`
- `downloads/114760301.pdf`
