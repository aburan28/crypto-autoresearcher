---
id: KN-LIT-6396
type: literature
title: "Second-Order Differential Collisions for Reduced SHA-256"
authors:
  - "Alex Biryukov"
  - "Mario Lamberger"
  - "Florian Mendel"
  - "Ivica Nikolić"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we introduce a new non-random property for hash/compression functions using the theory of higher order differentials. Based on this, we show a second-order differential collision for the compression function of SHA-256 reduced to 47 out of 64 steps with practical complexity.

## Key claims (as reported)
- We have implemented the attack and provide an example.
- Our results suggest that the security margin of SHA-256 is much lower than the security margin of most of the SHA-3 finalists in this setting.
- The techniques employed in this attack are based on a rectangle/boomerang approach and cover advanced search algorithms for good characteristics and message modification techniques.
- Our analysis also exposes flaws in all of the previously published related-key rectangle attacks on the SHACAL-2 block cipher, which is based on SHA-256.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730269 (1).pdf`
- `downloads/70730269 (2).pdf`
- `downloads/70730269 (3).pdf`
- `downloads/70730269.pdf`
