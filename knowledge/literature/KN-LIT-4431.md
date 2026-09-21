---
id: KN-LIT-4431
type: literature
title: "Improved Security Analysis for Nonce-based Enhanced Hash-then-Mask MACs"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we prove that the nonce-based enhanced hash3n then-mask MAC (nEHtM) is secure up to 2 4 MAC queries and 2n verification queries (ignoring logarithmic factors) as long as the number of 3n faulty queries μ is below 2 8 , significantly improving the previous bound 3n by Dutta et al. Even when μ goes beyond 2 8 , nEHtM enjoys graceful degradation of security.

## Key claims (as reported)
- The second result is to prove the security of PRF-based nEHtM; when nEHtM is based on an n-to-s bit random function for a fixed size s such that 1 ≤ s ≤ n, it is proved to be secure up to any number of MAC n queries and 2s verification queries, if (1) s = n and μ < 2 2 or (2) n2 < n s n−s n−s n }, or (3) s ≤ 2 and μ < 2 2 .
- This s < 2 and μ < max{2 2 , 2 result leads to the security proof of truncated nEHtM that returns only s bits of the original tag since a truncated permutation can be seen as a pseudorandom function.
- In particular, when s ≤ 2n , the truncated 3 s nEHtM is secure up to 2n− 2 MAC queries and 2s verification queries n as long as μ < min{2 2 , 2n−s }.
- For example, when s = n2 (resp. s = 3n 7n n ), the truncated nEHtM is secure up to 2 4 (resp.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491198 (1).pdf`
- `downloads/12491198.pdf`
