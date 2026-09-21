---
id: KN-LIT-2980
type: literature
title: "Communication Lower Bounds for Statistically Secure MPC, with or without Preprocessing"
authors:
  - "Ivan Damgård"
  - "Kasper Green Larsen"
  - "Jesper Buus Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, finite-field, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We prove a lower bound on the communication complexity of unconditionally secure multiparty computation, both in the standard model with n = 2t + 1 parties of which t are corrupted, and in the preprocessing model with n = t + 1. In both cases, we show that for any g ∈ N there exists a Boolean circuit C with g gates, where any secure protocol implementing C must communicate Ω(ng) bits, even if only passive and statistical security is required.

## Key claims (as reported)
- The results easily extends to constructing similar circuits over any fixed finite field.
- This shows that for all sizes of circuits, the O(n) overhead of all known protocols when t is maximal is inherent.
- It also shows that security comes at a price: the circuit we consider could namely be computed among n parties with communication only O(g) bits if no security was required.
- Our results extend to the case where the threshold t is suboptimal.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940267 (1).pdf`
- `downloads/116940267.pdf`
