---
id: KN-LIT-7139
type: literature
title: "Tight Time-Space Lower Bounds for Finding"
authors:
  - "Multiple Collision Pairs"
  - "Their Applications"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, pollard-rho, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a collision search problem (CSP), where given a parameter C, the goal is to find C collision pairs in a random function f : [N ] → [N ] (where [N ] = {0, 1, . . . , N − 1}) using S bits of memory. Algorithms for CSP have numerous cryptanalytic applications such as space-efficient attacks on double and triple encryption.

## Key claims (as reported)
- The best known algorithm for CSP is parallel collision search (PCS) published by van Oorschot and Wiener, which achieves the time-space tradeoff T 2 · S = Õ(C 2 · N ).
- In this paper, we prove that any algorithm for CSP satisfies T 2 · S = Ω̃(C 2 · N ), hence the best known time-space tradeoff is optimal (up to poly-logarithmic factors in N ).
- On the other hand, we give strong evidence that proving similar unconditional time-space tradeoff lower bounds on CSP applications (such as breaking double and triple encryption) may be very difficult, and would imply a breakthrough in complexity theory.
- Hence, we propose a new restricted model of computation and prove that under this model, the best known time-space tradeoff attack on double encryption is optimal.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105165 (1).pdf`
- `downloads/12105165.pdf`
