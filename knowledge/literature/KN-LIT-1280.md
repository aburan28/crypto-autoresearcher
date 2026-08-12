---
id: KN-LIT-1280
type: literature
title: "On Wagner’s k-Tree Algorithm Over Integers"
authors:
  - "Haoxing Lin∗"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1612"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1612"
tags: [cryptanalysis, hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The k-Tree algorithm [Wag02] is a non-trivial algorithm for the average-case k-SUM problem that has found widespread use in cryptanalysis. Its input consists of k lists, each containing n integers from a range of size m.

## Key claims (as reported)
- Wagner’s original heuristic analysis [Wag02] suggested that this algorithm succeeds with constant probability if n ≈ m1/(log k+1) , and that in this case it runs in time O(kn).
- Subsequent rigorous analysis of the algorithm [Lyu05, Sha08, JKL24] has shown that it succeeds with high probability if the input list sizes are significantly larger than this.
- We present a broader rigorous analysis of the k-Tree algorithm, showing upper and lower bounds on its success probability and complexity for any size of the input lists.
- Our results confirm Wagner’s heuristic conclusions, and also give meaningful bounds for a wide range of list sizes that are not covered by existing analyses.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1612.pdf`
