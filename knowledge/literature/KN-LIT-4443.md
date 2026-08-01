---
id: KN-LIT-4443
type: literature
title: "Improved Slide Attacks"
authors:
  - "Eli Biham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The slide attack is applicable to ciphers that can be represented as an iterative application of the same keyed permutation. The slide attack leverages simple attacks on the keyed permutation to more complicated (and time consuming) attacks on the entire cipher.

## Key claims (as reported)
- In this paper we extend the slide attack by examining the cycle structures of the entire cipher and of the underlying keyed permutation.
- Our method allows to find slid pairs much faster than was previously known, and hence reduces the time complexity of the entire slide attack significantly.
- In addition, since our attack finds as many slid pairs as the attacker requires, it allows to leverage all types of attacks on the underlying permutation (and not only simple attacks) to an attack on the entire cipher.
- We demonstrate the strength of our technique by presenting an attack on 24-round reduced GOST whose S-boxes are unknown.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930152 (1).pdf`
- `downloads/45930152 (2).pdf`
- `downloads/45930152 (3).pdf`
- `downloads/45930152.pdf`
