---
id: KN-LIT-3821
type: literature
title: "Faster Algorithms for Approximate Common Divisors: Breaking Fully-Homomorphic-Encryption Challenges over the Integers"
authors:
  - "Yuanmi Chen"
  - "Phong Q. Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At EUROCRYPT ’10, van Dijk et al. presented simple fully-homomorphic encryption (FHE) schemes based on the hardness of approximate integer common divisors problems, which were introduced in 2001 by Howgrave-Graham. There are two versions for these problems: the partial version (PACD) and the general version (GACD).

## Key claims (as reported)
- The seemingly easier problem PACD was recently used by Coron et al. at CRYPTO ’11 to build a more efficient variant of the FHE scheme by van Dijk et al..
- We present a new PACD algorithm whose running time is essentially the “square root” of that of exhaustive search, which was the best attack in practice.
- This allows us to experimentally break the FHE challenges proposed by Coron et al.
- Our PACD algorithm directly gives rise to a new GACD algorithm, which is exponentially faster than exhaustive search.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370497 (1).pdf`
- `downloads/72370497 (2).pdf`
- `downloads/72370497 (3).pdf`
- `downloads/72370497.pdf`
