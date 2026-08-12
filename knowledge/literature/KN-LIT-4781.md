---
id: KN-LIT-4781
type: literature
title: "Lossiness and Entropic Hardness for Ring-LWE"
authors:
  - "Zvika Brakerski"
  - "Nico Döttling"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, number-theory, pairing, pqc, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hardness of the Ring Learning with Errors problem (RLWE) is a central building block for efficiency-oriented lattice-based cryptography. Many applications use an “entropic” variant of the problem where the so-called “secret” is not distributed uniformly as prescribed but instead comes from some distribution with sufficient minentropy.

## Key claims (as reported)
- However, the hardness of the entropic variant has not been substantiated thus far.
- For standard LWE (not over rings) entropic results are known, using a “lossiness approach” but it was not known how to adapt this approach to the ring setting.
- In this work we present the first such results, where entropic security is established either under RLWE or under the Decisional Small Polynomial Ratio (DSPR) assumption which is a mild variant of the NTRU assumption.
- In the context of general entropic distributions, our results in the ring setting essentially match the known lower bounds (Bolboceanu et al., Asiacrypt 2019; Brakerski and Döttling, Eurocrypt 2020).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550224 (1).pdf`
- `downloads/12550224.pdf`
