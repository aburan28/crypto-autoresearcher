---
id: KN-LIT-7002
type: literature
title: "The Iterated Random Function Problem"
authors:
  - "Ritam Bhaumik"
  - "Nilanjan Datta"
  - "Avijit Dutta"
  - "Nicky Mouha"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pollard-rho, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2015, Minaud and Seurin introduced and studied the iterated random permutation problem, which is to distinguish the r-th iterate of a random permutation from a random permutation. In this paper, we study the closely related iterated random function problem, and prove the first almost-tight bound in the adaptive setting.

## Key claims (as reported)
- More specifically, we prove that the advantage to distinguish the r-th iterate of a random function from a random function using q queries is bounded by O(q 2 r(log r)3 /N ), where N is the size of the domain.
- In previous work, the best known bound was O(q 2 r 2 /N ), obtained as a direct result of interpreting the iterated random function problem as a special case of CBC-MAC based on a random function.
- For the iterated random function problem, the best known attack has an advantage of Ω(q 2 r/N ), showing that our security bound is tight up to a factor of (log r)3 .

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240329 (1).pdf`
- `downloads/106240329.pdf`
