---
id: KN-LIT-3800
type: literature
title: "Fast Evaluation of Polynomials over Binary"
authors:
  - "Finite Fields"
  - "Application to Side-channel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, finite-field, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a new technique for evaluating polynomials over binary finite fields. This is useful in the context of anti-DPA countermeasures when an S-box is expressed as a polynomial over a binary finite field.

## Key claims (as reported)
- For n-bit S-boxes our new technique has heuristic complexity √ O(2n/2 / n) instead of O(2n/2 ) proven complexity for the Parity-Split √ method.
- We also prove a lower bound of Ω(2n/2 / n) on the complexity of any method to evaluate n-bit S-boxes; this shows that our method is asymptotically optimal.
- Here, complexity refers to the number of nonlinear multiplications required to evaluate the polynomial corresponding to an S-box.
- In practice we can evaluate any 8-bit S-box in 10 non-linear multiplications instead of 16 in the Roy-Vivek paper from CHES 2013, and the DES S-boxes in 4 non-linear multiplications instead of 7.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310143 (1).pdf`
- `downloads/87310143 (2).pdf`
- `downloads/87310143 (3).pdf`
- `downloads/87310143.pdf`
