---
id: KN-LIT-3210
type: literature
title: "Cryptanalyses of Candidate Branching Program Obfuscators"
authors:
  - "Yilei Chen"
  - "Craig Gentry"
  - "Shai Halevi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, number-theory, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe new cryptanalytic attacks on the candidate branching program obfuscator proposed by Garg, Gentry, Halevi, Raykova, Sahai and Waters (GGHRSW) using the GGH13 graded encoding, and its variant using the GGH15 graded encoding as specified by Gentry, Gorbunov and Halevi. All our attacks require very specific structure of the branching programs being obfuscated, which in particular must have some input-partitioning property.

## Key claims (as reported)
- Common to all our attacks are techniques to extract information about the “multiplicative bundling” scalars that are used in the GGHRSW construction.
- For GGHRSW over GGH13, we show how to recover the ideal generating the plaintext space when the branching program has input partitioning.
- Combined with the information that we extract about the “multiplicative bundling” scalars, we get a distinguishing attack by an extension of the annihilation attack of Miles, Sahai and Zhandry.
- Alternatively, once we have the ideal we can solve the principle-ideal problem (PIP) in classical subexponential time or quantum polynomial time, hence obtaining a total break.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210257 (1).pdf`
- `downloads/10210257.pdf`
