---
id: KN-LIT-5168
type: literature
title: "Non-cryptographic Primitive for Pseudorandom Permutation"
authors:
  - "Tetsu Iwata"
  - "Tomonobu Yoshino"
  - "Kaoru Kurosawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Four round Feistel permutation (like DES) is super-pseudorandom if each round function is random or a secret universal hash function. A similar result is known for five round MISTY type permutation.

## Key claims (as reported)
- It seems that each round function must be at least either random or secret in both cases.
- In this paper, however, we show that the second round permutation g in five round MISTY type permutation need not be cryptographic at all, i.e., no randomness nor secrecy is required. g has only to satisfy that g(x) ⊕ x 6= g(x0 ) ⊕ x0 for any x 6= x0 .
- This is the first example such that a non-cryptographic primitive is substituted to construct the minimum round super-pseudorandom permutation.
- Further we show efficient constructions of super-pseudorandom permutations by using above mentioned g.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/23650151 (1).pdf`
- `downloads/23650151 (2).pdf`
- `downloads/23650151.pdf`
