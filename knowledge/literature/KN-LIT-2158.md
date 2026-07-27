---
id: KN-LIT-2158
type: literature
title: "A New Related Message Attack on RSA"
authors:
  - "Oded Yacobi"
  - "Yacov Yacobi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Coppersmith, Franklin, Patarin, and Reiter show that given two RSA cryptograms xe mod N and (ax + b)e mod N for known constants a, b ∈ ZN , one can compute x in O(e log 2 e) ZN -operations with some positive error probability. We show that given e cryptograms ci ≡ (ai x + bi )e mod N, i = 0, 1, ...e − 1, for any known constants ai , bi ∈ ZN , one can deterministically compute x in O(e) ZN -operations that depend on the cryptograms, after a pre-processing that depends only on the constants.

## Key claims (as reported)
- The complexity of the pre-processing is O(e log 2 e) ZN operations, and can be amortized over many instances.
- We also consider a special case where the overall cost of the attack is O(e) ZN -operations.
- Our tools are borrowed from numerical-analysis and adapted to handle formal polynomials over finite-rings.
- To the best of our knowledge their use in cryptanalysis is novel.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860001 (1).pdf`
- `downloads/33860001 (2).pdf`
- `downloads/33860001 (3).pdf`
- `downloads/33860001.pdf`
