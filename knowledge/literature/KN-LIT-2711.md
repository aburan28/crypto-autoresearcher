---
id: KN-LIT-2711
type: literature
title: "Bipartite Modular Multiplication"
authors:
  - "Marcelo E. Kaihara"
  - "Naofumi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, implementation, protocol, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes a new fast method for calculating modular multiplication. The calculation is performed using a new representation of residue classes modulo M that enables the splitting of the multiplier into two parts.

## Key claims (as reported)
- These two parts are then processed separately, in parallel, potentially doubling the calculation speed.
- The upper part and the lower part of the multiplier are processed using the interleaved modular multiplication algorithm and the Montgomery algorithm respectively.
- Conversions back and forth between the original integer set and the new residue system can be performed at speeds up to twice that of the Montgomery method without the need for precomputed constants.
- This new method is suitable for both hardware implementation; and software implementation in a multiprocessor environment.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/015 (1).pdf`
- `downloads/015 (2).pdf`
- `downloads/015 (3).pdf`
- `downloads/015.pdf`
