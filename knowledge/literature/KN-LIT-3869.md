---
id: KN-LIT-3869
type: literature
title: "FHE Over the Integers: Decomposed and Batched in the Post-Quantum Regime"
authors:
  - "Daniel Benarroch"
  - "Zvika Brakerski"
  - "Tancrède Lepoint"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fully homomorphic encryption over the integers (FHE-OI) is currently the only alternative to lattice-based FHE. FHE-OI includes a family of schemes whose security is based on the hardness of different variants of the approximate greatest common divisor (AGCD) problem.

## Key claims (as reported)
- A lot of effort was made to port techniques from second generation lattice-based FHE (using tensoring) to FHE-OI.
- Gentry, Sahai and Waters (Crypto 13) showed that third generation techniques (which were later formalized using the “gadget matrix”) can also be ported.
- However, the majority of these works was based on the noise-free variant of AGCD which is potentially weaker than the general one.
- In particular, the noise-free variant relies on the hardness of factoring and is thus vulnerable to quantum attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101750261 (1).pdf`
- `downloads/101750261 (2).pdf`
- `downloads/101750261 (3).pdf`
- `downloads/101750261 (4).pdf`
- `downloads/101750261.pdf`
