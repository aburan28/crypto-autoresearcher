---
id: KN-LIT-1825
type: literature
title: "Pushing the boundaries of group-based aggregation with zero-evading generators of low additive complexity"
authors:
  - "Ariel Gabizon"
  - "Dmitry Krachun"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1148"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1148"
tags: [curve-arithmetic, elliptic-curve, finite-field, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A zero-evading generator with error parameter λ is a distribution Z on Fn such that for any non-zero vector x ∈ Fn the probability that ha, xi = 0 is at most 2−λ , when a is chosen according to Z. We investigate the number of additions required to compute ha, xi given x.

## Key claims (as reported)
- The traditional construction chooses a vector a with random λ-bit elements.
- Pippenger’s algorithm gives an additive complexity of at least Ω(λn/ log(n)) for this approach.
- We give a construction requiring only O(n + λ) additions.
- We highlight the impact of reducing the number of additions on aggregation of group-based commitments, such as KZG commitments [KZG10].

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1148.pdf`
