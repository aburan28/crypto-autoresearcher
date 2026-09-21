---
id: KN-LIT-5323
type: literature
title: "On Computational Shortcuts for Information-Theoretic PIR"
authors:
  - "Matthew M. Hong"
  - "Yuval Ishai"
  - "Victor I. Kolobov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Information-theoretic private information retrieval (PIR) schemes have attractive concrete efficiency features. However, in the standard PIR model, the computational complexity of the servers must scale linearly with the database size.

## Key claims (as reported)
- We study the possibility of bypassing this limitation in the case where the database is a truth table of a “simple” function, such as a union of (multidimensional) intervals or convex shapes, a decision tree, or a DNF formula.
- This question is motivated by the goal of obtaining lightweight homomorphic secret sharing (HSS) schemes and secure multiparty computation (MPC) protocols for the corresponding families.
- We obtain both positive and negative results.
- For “first-generation” PIR schemes based on Reed-Muller codes, we obtain computational shortcuts for the above function families, with the exception of DNF formulas for which we show a (conditional) hardness result.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550202 (1).pdf`
- `downloads/12550202.pdf`
