---
id: KN-LIT-3988
type: literature
title: "Fully Homomorphic Encryption over the Integers"
authors:
  - "Marten van Dijk"
  - "Craig Gentry"
  - "Shai Halevi"
  - "Vinod Vaikuntanathan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a simple fully homomorphic encryption scheme, using only elementary modular arithmetic. We use Gentry’s technique to construct a fully homomorphic scheme from a “bootstrappable” somewhat homomorphic scheme.

## Key claims (as reported)
- However, instead of using ideal lattices over a polynomial ring, our bootstrappable encryption scheme merely uses addition and multiplication over the integers.
- The main appeal of our scheme is the conceptual simplicity.
- We reduce the security of our scheme to finding an approximate integer gcd – i.e., given a list of integers that are near-multiples of a hidden integer, output that hidden integer.
- We investigate the hardness of this task, building on earlier work of Howgrave-Graham.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320254 (1).pdf`
- `downloads/66320254 (2).pdf`
- `downloads/66320254 (3).pdf`
- `downloads/66320254.pdf`
