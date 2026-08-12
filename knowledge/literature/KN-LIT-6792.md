---
id: KN-LIT-6792
type: literature
title: "State Separation for Code-Based Game-Playing Proofs Chris Brzuska1 , Antoine Delignat-Lavaud2 , Cédric Fournet2"
authors:
  - "Konrad Kohbrok"
  - "Markulf Kohlweiss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
cryptography, process algebras, and type-based verification frameworks, we propose a method to simplify large reductions, avoid mistakes in carrying them out, and obtain concise security statements. Our method decomposes monolithic games into collections of stateful packages representing collections of oracles that call one another using well-defined interfaces.

## Key claims (as reported)
- Every component scheme yields a pair of a real and an ideal package.
- In security proofs, we then successively replace each real package with its ideal counterpart, treating the other packages as the reduction.
- We build this reduction by applying a number of algebraic operations on packages justified by their state separation.
- Our method handles reductions that emulate the game perfectly, and leaves more complex arguments to existing game-based proof techniques such as the code-based analysis suggested by Bellare and Rogaway.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272278 (1).pdf`
- `downloads/11272278.pdf`
